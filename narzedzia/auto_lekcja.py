"""
🤖 Auto-Lekcja (Opcja C — W-360 v4) — DeepSeek ekstrahuje lekcje i wizje z sesji.

PROBLEM: lekcje są dodawane ręcznie → w praktyce większość sesji ich nie ma.
100 sesji dialogu, ale wyciągnięte wnioski z < 10%.

ROZWIĄZANIE: po każdej sesji (przez SessionStart hook → przyrostowo) DeepSeek
czyta ostatnią kronikę i wyciąga strukturalnie:
  • LEKCJA   — co się nauczyliśmy ("bug Force Index przy fi2==0")
  • WIZJA    — długoterminowy kierunek ("portfel multiasset")
  • DECYZJA  — zamknięta sprawa ("NIE robimy Y bo Z")
  • POMYSŁ   — open backlog ("RAG z wektorami — czeka na sieć")
  • ZMIANA   — co wdrożono ("dodano neuron X-28")

Wyniki zapisywane do:
  - bibliotheca_ulpia/dane/lekcje via pamiec_sesji.dopisz_lekcje()
  - bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl via rejestr_wizji.dodaj()

TRYB: przyrostowy — śledzi przetworzone sesje w .auto_lekcja_przetworzone.txt
(nie przetwarza dwa razy tej samej sesji).

BEZPIECZEŃSTWO: wymaga DEEPSEEK_API_KEY. Bez klucza → nic nie robi, exit 0 (silent).

Użycie:
  python narzedzia/auto_lekcja.py                # przetwarza nowe sesje
  python narzedzia/auto_lekcja.py --sesja <id>   # wymusza jedną sesję
  python narzedzia/auto_lekcja.py --podglad      # pokazuje co by wyekstrahował (dry-run)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KRONIKA_DIR = ROOT / "bibliotheca_ulpia" / "dane" / "kronika"
WIZJE_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "wizje_i_decyzje.jsonl"

# Marker przetworzonych kronik — WERSJONOWANY (był w .gitignore i per-maszyna, przez co ta
# sama kronika była ekstrahowana ponownie na każdym komputerze: tu 14 z 102 sesji oznaczonych,
# na laptopie 0 → DeepSeek generował kolejną parafrazę tej samej lekcji. Źródło duplikatów,
# recenzja cubic PR #118). Klucz = HASZ TREŚCI kroniki, nie ID sesji: kronika dopisana po
# przetworzeniu zmienia hasz i zostanie doczytana, a niezmieniona nigdy nie kosztuje tokenów.
PRZETWORZONE_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "auto_lekcja_przetworzone.txt"
# Stary marker (per-maszyna, ID sesji) — czytany dla zgodności wstecz, nigdy nie zapisywany.
STARY_MARKER = ROOT / "bibliotheca_ulpia" / "dane" / ".auto_lekcja_przetworzone.txt"

_SYSTEM_PROMPT = """Jesteś analitykiem pamięci dla systemu tradingowego IMPERIAL-MESH-VORTEX.
Twoje zadanie: przeanalizuj poniższą kronikę sesji (dialog Cezara z Claude)
i wyciągnij KLUCZOWE elementy do strukturalnej pamięci.

Odpowiedz WYŁĄCZNIE w formacie JSON — lista obiektów, każdy z polami:
  typ: "LEKCJA" | "WIZJA" | "DECYZJA" | "POMYSŁ" | "ZMIANA"
  tytul: krótki tytuł (max 80 znaków), po polsku
  tresc: rozwinięcie (max 300 znaków), po polsku
  status: "WDROŻONA" (dla ZMIANA/LEKCJA) | "POMYSŁ" (dla POMYSŁ) | "ZAMKNIĘTA" (dla DECYZJA) | "PLANOWANE" (dla WIZJA)
  rezim: "" lub kanoniczny reżim jeśli dotyczy konkretnego reżimu rynku (BULL/BEAR/TREND_STRONG/VOLATILE/RANGING/NORMAL)

Zasady ekstrakcji:
- LEKCJA: konkretny fakt techniczny/błąd/odkrycie ("bug X przy warunku Y", "neuron Z zwraca NEUTRAL gdy brak danych")
- WIZJA: długoterminowy kierunek strategiczny ("chcemy portfel 20 par", "live trading przez MEXC")
- DECYZJA: zamknięta sprawa, którą NIE ma sensu ponownie otwierać ("odrzucono X bo Y", "mnemosyne wycofany")
- POMYSŁ: backlog — coś co chcemy zrobić, ale jeszcze nie ("RAG z wektorami", "auto-lekcja")
- ZMIANA: co faktycznie zostało wdrożone w tej sesji ("dodano moduł X", "naprawiono Y")

Ekstrakcja musi być PRECYZYJNA i OSZCZĘDNA: 3-10 elementów per sesja (nie lej wody).
Każdy element musi mieć REALNĄ wartość informacyjną dla systemu tradingowego.
Pomiń small-talk, pytania bez odpowiedzi, powtarzające się informacje.

NIE zwracaj żadnego tekstu poza JSON. Odpowiedź = czysty JSON array."""

_MAX_KRONIKA_ZNAKOW = 8000   # ucinamy długie kroniki by nie przepalać tokenów


def _klucz_kroniki(plik: Path) -> str:
    """Hasz treści kroniki (12 znaków sha1) — stabilny między maszynami i klonami repo."""
    return hashlib.sha1(plik.read_bytes()).hexdigest()[:12]


def _wczytaj_przetworzone() -> tuple[set, set]:
    """
    Zwraca (hasze_tresci, stare_id_sesji) — DWA ROZŁĄCZNE zbiory (recenzja cubic PR #118).

    Wrzucenie obu do jednego worka niweczyło sens haszowania: kronika dopisana po
    przetworzeniu dostawała nowy hasz, ale jej `sesja_id` (kolumna informacyjna nowego
    markera) wciąż był w zbiorze → kronika pomijana mimo zmienionej treści.
    Dziś ID rozstrzyga WYŁĄCZNIE gdy pochodzi ze starego markera (zgodność wstecz),
    a nowy marker jest kluczowany samym haszem.
    """
    hasze: set = set()
    zmigrowane: set = set()
    stare_id: set = set()

    if PRZETWORZONE_PLIK.exists():
        for linia in PRZETWORZONE_PLIK.read_text(encoding="utf-8").splitlines():
            linia = linia.strip()
            if not linia or linia.startswith("#"):
                continue
            czesci = linia.split()
            hasze.add(czesci[0])                      # kolumna 1 = hasz (rozstrzyga)
            if len(czesci) > 1:
                zmigrowane.add(czesci[1])             # kolumna 2 = sesja_id (informacyjna)

    if STARY_MARKER.exists():
        for linia in STARY_MARKER.read_text(encoding="utf-8").splitlines():
            linia = linia.strip()
            if linia and not linia.startswith("#"):
                stare_id.add(linia.split()[0])

    # Sesje już zmigrowane do markera haszowego wypadają ze starego zbioru — inaczej ich
    # ID wiecznie blokowałoby ponowne przetworzenie ZMIENIONEJ kroniki (hasz by się zmienił,
    # ale ID pozostaje). Stary marker rozstrzyga wyłącznie o sesjach, których nie zmigrowano.
    return hasze, stare_id - zmigrowane


def _zapisz_przetworzona(sesja_id: str, hasz: str) -> None:
    PRZETWORZONE_PLIK.parent.mkdir(parents=True, exist_ok=True)
    if not PRZETWORZONE_PLIK.exists():
        PRZETWORZONE_PLIK.write_text(
            "# Kroniki przetworzone przez auto_lekcja (hasz treści + ID sesji).\n"
            "# Wersjonowany świadomie: bez tego ta sama kronika jest ekstrahowana\n"
            "# na każdej maszynie od nowa, produkując parafrazy tych samych lekcji.\n",
            encoding="utf-8",
        )
    with PRZETWORZONE_PLIK.open("a", encoding="utf-8") as f:
        f.write(f"{hasz}  {sesja_id}\n")


def _czytaj_kronika(plik: Path) -> str:
    tekst = plik.read_text(encoding="utf-8", errors="ignore")
    if len(tekst) > _MAX_KRONIKA_ZNAKOW:
        tekst = tekst[:_MAX_KRONIKA_ZNAKOW] + "\n\n[...ucięto dla oszczędności tokenów...]"
    return tekst


def _wywolaj_deepseek(tekst_sesji: str) -> List[Dict[str, Any]]:
    """Wywołuje DeepSeek API i zwraca sparsowane wyniki. [] przy błędzie."""
    try:
        from imperium.cesarz.deepseek_glos import GlosImperium
        glos = GlosImperium()   # domyślny = deepseek-v4-flash (migracja V4, legacy retire 2026-07-24)
        odp = glos.zapytaj(_SYSTEM_PROMPT, tekst_sesji, temperatura=0.3)
        # parsuj JSON z odpowiedzi
        odp = odp.strip()
        if odp.startswith("```"):
            odp = "\n".join(odp.splitlines()[1:])
        if odp.endswith("```"):
            odp = "\n".join(odp.splitlines()[:-1])
        return json.loads(odp)
    except Exception as e:
        print(f"  [auto_lekcja] Błąd DeepSeek: {e}", file=sys.stderr)
        return []


def _zapisz_wyniki(wyniki: List[Dict[str, Any]], data_sesji: str) -> int:
    """Zapisuje wyniki do W3 (lekcje) i W4 (wizje). Zwraca liczbę zapisanych."""
    from imperium.biblioteki import pamiec_sesji as _ps
    from imperium.biblioteki import rejestr_wizji as _rw

    zapisane = 0
    for w in wyniki:
        typ = w.get("typ", "").upper()
        tytul = w.get("tytul", "").strip()
        tresc = w.get("tresc", "").strip()
        status = w.get("status", "POMYSŁ").upper()
        rezim = w.get("rezim", "").upper()

        if not tytul or not tresc:
            continue

        if typ == "LEKCJA":
            # Dedup SEMANTYCZNY: DeepSeek parafrazuje tytuł przy każdym przebiegu, więc
            # porównanie napisów przepuszczało 4 kopie tej samej lekcji (recenzja cubic
            # PR #118). Porównujemy sygnatury techniczne — patrz pamiec_sesji.duplikat_lekcji.
            istniejaca = _ps.duplikat_lekcji(tytul, tresc)
            if istniejaca is not None:
                # Pominięcie MUSI być widoczne: sygnatura nie odróżnia „za niski" od „za
                # wysoki", więc lekcja obalająca poprzednią też trafi tutaj. Cichy `continue`
                # kasowałby ją bez śladu (Prawo XV — utrata potencjału).
                print(f"  [auto_lekcja] ⏭️  duplikat: {tytul!r} ≈ {istniejaca['tytul']!r}",
                      file=sys.stderr)
                continue
            _ps.dopisz_lekcje(tytul, tresc, data=data_sesji)
        elif typ in ("WIZJA", "DECYZJA", "POMYSŁ", "ZMIANA"):
            # rejestr_wizji.dodaj ma wbudowany dedup (typ+tytuł) → zwraca False gdy duplikat
            try:
                dopisano = _rw.dodaj(typ, tytul, tresc, status=status, rezim=rezim, data=data_sesji)
            except ValueError:
                dopisano = _rw.dodaj(typ, tytul, tresc, status="POMYSŁ", data=data_sesji)
            if not dopisano:
                continue
        else:
            continue
        zapisane += 1
    return zapisane


def przetworz_sesje(sesja_id: str, podglad: bool = False) -> int:
    """Przetwarza jedną sesję. Zwraca liczbę nowych wpisów (0 = nic nowego)."""
    plik = KRONIKA_DIR / f"sesja_{sesja_id}.md"
    if not plik.exists():
        print(f"  [auto_lekcja] Nie znaleziono kroniki: {plik.name}")
        return 0

    tekst = _czytaj_kronika(plik)
    data_sesji = plik.stat().st_mtime
    from datetime import datetime
    data_str = datetime.utcfromtimestamp(data_sesji).strftime("%Y-%m-%d")

    print(f"  [auto_lekcja] Analizuję sesję {sesja_id[:12]}... ({len(tekst)} znaków)")
    wyniki = _wywolaj_deepseek(tekst)

    if not wyniki:
        print("  [auto_lekcja] Brak wyników (lub błąd DeepSeek)")
        return 0

    if podglad:
        print(f"  [auto_lekcja] Podgląd ({len(wyniki)} elementów):")
        for w in wyniki:
            print(f"    [{w.get('typ','?')}] {w.get('tytul','')}")
        return len(wyniki)

    zapisane = _zapisz_wyniki(wyniki, data_str)
    _zapisz_przetworzona(sesja_id, _klucz_kroniki(plik))
    pominiete = len(wyniki) - zapisane
    ogon = f" (pominięto {pominiete} duplikatów)" if pominiete else ""
    print(f"  [auto_lekcja] ✅ Zapisano {zapisane} elementów z sesji {sesja_id[:12]}{ogon}")
    return zapisane


def przetworz_nowe(maks_sesji: int = 3, podglad: bool = False) -> Dict[str, int]:
    """
    Przetwarza do `maks_sesji` nowych (nieprzetworzonnych) sesji z kroniki.
    Zwraca {"przetworzone": N, "lacznie_wpisow": M}.
    Ograniczenie do 3 sesji per uruchomienie = kontrola kosztów tokenów.
    """
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("  [auto_lekcja] Brak DEEPSEEK_API_KEY — pomijam (Prawo Bezpieczeństwa).")
        return {"przetworzone": 0, "lacznie_wpisow": 0}

    hasze_juz, stare_id_juz = _wczytaj_przetworzone()
    sesje = sorted(KRONIKA_DIR.glob("sesja_*.md"), reverse=True)  # najnowsze pierwsze

    wynik = {"przetworzone": 0, "lacznie_wpisow": 0}
    for plik in sesje:
        sesja_id = plik.stem.replace("sesja_", "")
        # Hasz łapie kronikę przetworzoną na INNEJ maszynie i UNIEWAŻNIA SIĘ przy dopisaniu.
        # Stare ID rozstrzyga tylko dla kronik sprzed migracji markera.
        if _klucz_kroniki(plik) in hasze_juz or sesja_id in stare_id_juz:
            continue
        n = przetworz_sesje(sesja_id, podglad=podglad)
        wynik["lacznie_wpisow"] += n
        wynik["przetworzone"] += 1
        if wynik["przetworzone"] >= maks_sesji:
            break

    return wynik


def powod_odlozenia(wymuszona_sesja: str = "", takze_w_szczycie: bool = False,
                    kiedy=None) -> str:
    """Czy odłożyć analizę na później — zwraca POWÓD (pusty string = działaj).

    TARYFA SZCZYTOWA (zmierzone 2026-07-21): DeepSeek liczy 2× w oknach 01:00–04:00
    i 06:00–10:00 UTC, a 06–10 UTC to 08:00–12:00 czasu Cezara — czyli TYPOWY poranny
    start sesji trafia prosto w szczyt. Rachunek za 2026-07-21 pokazał 22 takie wywołania
    i WSZYSTKIE pochodziły z tego hooka.

    Odłożenie nie kosztuje NIC, bo auto-lekcja analizuje sesje JUŻ ZAKOŃCZONE: nie ma czego
    stracić przez zwłokę, a nieprzetworzona sesja zostaje w kolejce i zostanie domknięta
    przy najbliższym starcie poza szczytem (`przetworz_nowe` bierze zaległe).

    Wyjątki są świadome: `--sesja` (wymuszenie konkretnej) i `--takze-w-szczycie` —
    kto MUSI mieć lekcję teraz, płaci podwójnie i wie za co.

    Wydzielone z `__main__` UMYŚLNIE: bramka schowana w bloku uruchomieniowym jest
    nietestowalna, a bramka bez testu prędzej czy później przestaje gryźć niezauważona.
    """
    if wymuszona_sesja or takze_w_szczycie:
        return ""
    from imperium.cesarz.dispensator import czy_szczyt
    if czy_szczyt(kiedy):
        return ("okno podwójnej stawki DeepSeeka — odkładam analizę (sesje czekają, "
                "nic nie ginie). Wymuszenie: --takze-w-szczycie")
    return ""


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Auto-Lekcja W-360 v4 — DeepSeek ekstrahuje lekcje z sesji")
    p.add_argument("--sesja", default="", help="ID sesji do wymuszenia przetworzenia")
    p.add_argument("--podglad", action="store_true", help="Dry-run — pokaż bez zapisywania")
    p.add_argument("--maks", type=int, default=3, help="Maks sesji do przetworzenia (default 3)")
    p.add_argument("--takze-w-szczycie", action="store_true",
                   help="przetwarzaj nawet w oknie podwójnej stawki DeepSeeka "
                        "(domyślnie odkładamy — patrz niżej)")
    args = p.parse_args()

    powod = powod_odlozenia(wymuszona_sesja=args.sesja,
                            takze_w_szczycie=args.takze_w_szczycie)
    if powod:
        print(f"  [auto_lekcja] ⏸️ {powod}")
        raise SystemExit(0)

    if args.sesja:
        przetworz_sesje(args.sesja, podglad=args.podglad)
    else:
        r = przetworz_nowe(maks_sesji=args.maks, podglad=args.podglad)
        print(f"  [auto_lekcja] Podsumowanie: {r['przetworzone']} sesji, {r['lacznie_wpisow']} wpisów")
