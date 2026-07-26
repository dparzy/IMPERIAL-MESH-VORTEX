"""🔏 SIGILLARIUM — Skarbiec Pieczęci Imperium (SIGLA IMPERII).

Rzymskie *sigillum* to pieczęć: jeden znak, który uruchamia całą procedurę bez
recytowania jej za każdym razem. SIGLA IMPERII to hasła-skróty Cezara — `/apertio`,
`/clausura`, `/limes` — które rozwijają się w PEŁNE, ŻYWE checklisty.

ROZKAZ ŹRÓDŁOWY: Cezar Pixel, 2026-07-19 (domknięcie wachty doks20) — „ustalić SIGLA
IMPERII: skróty użytkowe uruchamiające pełne procedury; NIE dublować runbooków W11 —
skróty mają być ich WYZWALACZAMI (Prawo XVI)". Forma wybrana przez Cezara 2026-07-20:
skille harnessa `/nazwa` + polskie aliasy słowne.

═══════════════════════════════════════════════════════════════════════════════
DLACZEGO KROKI SĄ GENEROWANE, A NIE WPISANE (rdzeń tego organu)
═══════════════════════════════════════════════════════════════════════════════
Lekcja zmierzona 2026-07-20: runbook W11 „Bezpieczny commit" kazał Claude wykonać
`git push -u origin <branch>` — mimo że od 2026-07-11 obowiązuje rozkaz **Claude
NIGDY nie pushuje**. Treść runbooka była wpisana RĘCZNIE, więc zgniła w ciszy;
`dodaj()` dedupuje po nazwie, więc nie dawało się jej nawet nadpisać.

To ta sama klasa, którą Imperium nazwało dzień wcześniej (CENSUS ORGANORUM, W17):
**lekarstwem na gnicie jest ODEBRANIE DOKUMENTOWI PRAWA DO WŁASNEJ TREŚCI.**
Dlatego SIGILLARIUM niczego nie przechowuje — czyta kroki z KONSTYTUCJI (`CLAUDE.md`)
w chwili wywołania. Zmiana checklisty w CLAUDE.md natychmiast zmienia to, co robi
sigillum. Rozjazd jest strukturalnie niemożliwy, nie „pilnowany".

GRANICA WOBEC ISTNIEJĄCYCH ORGANÓW (Prawo XVI — nie duplikujemy):
  • `pamiec_proceduralna` (W11) = MAGAZYN runbooków (know-how skrystalizowane, np.
    „jak dodać neuron"). SIGILLARIUM go nie zastępuje — KARMI go żywą treścią
    (`synchronizuj_w11()`) i daje mu wyzwalacze.
  • `CLAUDE.md` = ŹRÓDŁO PRAWDY procedur. SIGILLARIUM tylko je czyta i podaje.
  • `.claude/skills/*/SKILL.md` = UJŚCIE w harnessie (`/apertio`). Skill jest cienki:
    mówi „uruchom to sigillum i wykonaj wydrukowane kroki" — nie powtarza kroków.

ZERO ZALEŻNOŚCI: czysty stdlib (jak cały Imperium).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

KORZEN = Path(__file__).resolve().parents[2]
KONSTYTUCJA = KORZEN / "CLAUDE.md"

# Znacznik końca checklisty w sekcji konstytucji — po nim idzie klauzula karna,
# która NIE jest krokiem do wykonania.
_STOP = "**Złamanie:**"


@dataclass(frozen=True)
class Sigillum:
    """Jedna pieczęć: hasło → procedura.

    `sekcja`   — nagłówek w CLAUDE.md, z którego czytamy kroki (źródło prawdy).
    `komendy`  — alternatywa dla sekcji: twarda lista komend (gdy procedura JEST
                 sekwencją poleceń, a nie prozą — np. bramka LIMES).
    """

    nazwa: str
    tytul: str
    opis: str
    wyzwalacze: List[str]
    sekcja: str = ""
    komendy: List[str] = field(default_factory=list)
    zrodlo: str = ""


# ── REJESTR SIGLI (rdzeń zatwierdzony przez Cezara 2026-07-20) ────────────────
SIGLA: Dict[str, Sigillum] = {
    "APERTIO": Sigillum(
        nazwa="APERTIO",
        tytul="APERTIO — otwarcie wachty",
        opis="Pełna checklista otwarcia sesji: czytanie wydruku hooka, rozstrzygnięcie "
             "alarmów, weryfikacja „czy już istnieje”, rozpoznanie terenu, plan.",
        wyzwalacze=["apertio", "otwarcie", "otwarcie sesji", "start sesji",
                    "zaczynamy", "otwieramy", "nowa sesja"],
        sekcja="## 🌅 OTWARCIE SESJI",
        zrodlo="CLAUDE.md § OTWARCIE SESJI (Cezar 2026-07-19)",
    ),
    "CLAUSURA": Sigillum(
        nazwa="CLAUSURA",
        tytul="CLAUSURA — domknięcie wachty",
        opis="Pełna checklista końca sesji: bramka, CODEX, recenzja adversarialna, "
             "symbioza dokumentów, Prawo XV, dług honorowy, Dziennik, commit, alarmy.",
        wyzwalacze=["clausura", "zamknięcie", "zamkniecie", "zamykamy", "koniec sesji",
                    "domykamy", "kończymy", "konczymy"],
        sekcja="## 🏁 KONIEC SESJI",
        zrodlo="CLAUDE.md § KONIEC SESJI (Cezar 2026-07-19)",
    ),
    "LIMES": Sigillum(
        nazwa="LIMES",
        tytul="LIMES — bramka Prawa XXI (wał graniczny)",
        opis="Twarda bramka przed każdym commitem: testy, pełny audyt (z ruff W13), "
             "łowca powtórek Księgi Wad, spis obalonych twierdzeń, dług honorowy.",
        wyzwalacze=["limes", "bramka", "zrób bramkę", "zrob bramke", "przed commitem",
                    "przed pushem", "sprawdź wszystko", "sprawdz wszystko"],
        komendy=[
            "python tests/run_tests.py",
            "python narzedzia/audyt_spojnosci.py",
            "python narzedzia/skan_wad_kodu.py",
            "python narzedzia/skan_wad_kodu.py --falsa",
            "python -m imperium.biblioteki.codex_notarum bilans",
        ],
        zrodlo="CLAUDE.md § TRYB AUTONOMICZNY + § KONIEC SESJI kroki 1/3/5b",
    ),
}


# ── PARSER KONSTYTUCJI ────────────────────────────────────────────────────────

def _tresc_sekcji(sekcja: str, tekst: Optional[str] = None) -> str:
    """Zwraca treść sekcji CLAUDE.md (od jej nagłówka do następnego `## `).

    Dopasowanie po PREFIKSIE nagłówka, bo nagłówki niosą ogon „(ROZKAZ STAŁY —
    Cezar zatwierdził ...)", który bywa aktualizowany. Pusty string = brak sekcji.
    """
    if tekst is None:
        if not KONSTYTUCJA.exists():
            return ""
        tekst = KONSTYTUCJA.read_text(encoding="utf-8", errors="ignore")
    linie = tekst.splitlines()
    start = -1
    for i, ln in enumerate(linie):
        if ln.startswith(sekcja):
            start = i
            break
    if start < 0:
        return ""
    koniec = len(linie)
    for j in range(start + 1, len(linie)):
        if linie[j].startswith("## "):
            koniec = j
            break
    return "\n".join(linie[start + 1:koniec])


def _splasz(tekst: str) -> str:
    """Skleja krok rozbity na wiele linii w jedno czytelne zdanie."""
    return re.sub(r"\s+", " ", tekst).strip()


def kroki_z_konstytucji(sekcja: str, tekst: Optional[str] = None) -> List[str]:
    """Wyciąga numerowaną checklistę z sekcji CLAUDE.md.

    Rozpoznaje numerację `1.` oraz sufiksowaną `5b.` (kroki dopisane później).
    Kontynuacje (linie wcięte) doklejane są do bieżącego kroku. Zatrzymuje się na
    klauzuli `**Złamanie:**` — to opis kary, nie krok do wykonania.
    """
    tresc = _tresc_sekcji(sekcja, tekst)
    if not tresc:
        return []
    kroki: List[str] = []
    biezacy: List[str] = []
    for ln in tresc.splitlines():
        if ln.lstrip().startswith(_STOP):
            break
        m = re.match(r"^(\d+[a-z]?)\.\s+(.*)$", ln)
        if m:
            if biezacy:
                kroki.append(_splasz(" ".join(biezacy)))
            biezacy = [f"{m.group(1)}. {m.group(2)}"]
        elif biezacy:
            if not ln.strip():
                # pusta linia domyka bieżący krok
                kroki.append(_splasz(" ".join(biezacy)))
                biezacy = []
            else:
                # KAŻDA niepusta linia w środku kroku (wcięta LUB nie) = zawinięta
                # kontynuacja — doklejamy ją. Wcześniej niewcięta linia była CICHO
                # gubiona jako „proza po liście", co ucinało treść kroku, zostawiając
                # numerację ciągłą (zmierzone 2026-07-20). Zgubienie fragmentu
                # checklisty jest groźniejsze niż doklejenie ogona (Prawo I): stop daje
                # `**Złamanie:**` albo następny nagłówek `## ` (obsłużony w _tresc_sekcji).
                biezacy.append(ln.strip())
    if biezacy:
        kroki.append(_splasz(" ".join(biezacy)))
    return kroki


# ── API SIGLI ─────────────────────────────────────────────────────────────────

def sigillum(nazwa: str) -> Optional[Sigillum]:
    """Pieczęć po nazwie albo po dowolnym z jej wyzwalaczy (case-insensitive)."""
    klucz = (nazwa or "").strip().lower()
    if not klucz:
        return None
    for s in SIGLA.values():
        if s.nazwa.lower() == klucz or klucz in s.wyzwalacze:
            return s
    return None


def kroki(nazwa: str, tekst: Optional[str] = None) -> List[str]:
    """Żywe kroki pieczęci — z konstytucji albo z listy komend."""
    s = sigillum(nazwa)
    if s is None:
        return []
    if s.komendy:
        return list(s.komendy)
    return kroki_z_konstytucji(s.sekcja, tekst)


def _cel_komendy_istnieje(kom: str) -> Optional[bool]:
    """Czy plik/moduł, na który wskazuje komenda, istnieje?

    Zwraca True/False dla komend wskazujących cel, albo None gdy komenda nie
    odwołuje się do żadnego pliku ani modułu (nic do sprawdzenia). Rozpoznaje
    DWA warianty, bo LIMES używa obu:
      • ścieżka `narzedzia/x.py`             → sprawdzenie pliku,
      • `python -m imperium.biblioteki.x`    → mapowanie kropek na ścieżkę .py.
    Wariant `-m` był wcześniej ślepą plamą (regex `\\S+\\.py` go nie łapał), więc
    martwa komenda LEX TALIONIS przeszłaby cicho (zmierzone 2026-07-20).
    """
    m_mod = re.search(r"-m\s+([\w.]+)", kom)
    if m_mod:
        rel = Path(m_mod.group(1).replace(".", "/") + ".py")
        # moduł-plik `a/b/c.py` albo pakiet `a/b/c/__init__.py`
        return (KORZEN / rel).exists() or (KORZEN / rel.with_suffix("") / "__init__.py").exists()
    m_py = re.search(r"(\S+\.py)", kom)
    if m_py:
        return (KORZEN / m_py.group(1)).exists()
    return None


def brakujace_komendy(nazwa: str) -> List[str]:
    """Komendy sigla wskazujące na NIEISTNIEJĄCY plik/moduł (łowca API-widm, Warstwa 16).

    Pieczęć wołająca skrypt, którego nie ma, to procedura udająca sprawną —
    dokładnie klasa „mechanizm, który przy awarii wygląda na sprawny".
    """
    s = sigillum(nazwa)
    if s is None:
        return []
    return [kom for kom in s.komendy if _cel_komendy_istnieje(kom) is False]


def raport(nazwa: str) -> str:
    """Wydruk pieczęci gotowy do wykonania (to widzi Architekt po `/apertio`)."""
    s = sigillum(nazwa)
    if s is None:
        znane = ", ".join(sorted(SIGLA))
        return f"❌ Nie znam sigillum „{nazwa}”. Znane pieczęcie: {znane}"
    lst = kroki(nazwa)
    naglowek = f"🔏 {s.tytul}\n   źródło: {s.zrodlo}\n   wyzwalacze: {', '.join(s.wyzwalacze)}"
    if not lst:
        return (f"{naglowek}\n\n🚨 PIECZĘĆ PUSTA — sekcja „{s.sekcja}” nie istnieje "
                f"w CLAUDE.md albo zmieniła format. To alarm, nie brak zadań.")
    ciało = "\n".join(f"   {k}" for k in lst)
    stopka = ""
    braki = brakujace_komendy(nazwa)
    if braki:
        stopka = "\n\n🚨 MARTWE KOMENDY (plik nie istnieje):\n" + "\n".join(f"   • {b}" for b in braki)
    return f"{naglowek}\n\n{ciało}{stopka}"


def wszystkie() -> List[Sigillum]:
    return [SIGLA[k] for k in sorted(SIGLA)]


def raport_startowy() -> str:
    """Jedna linia do hooka/Centrum Pamięci — Cezar widzi, że sigla żyją."""
    czesci = []
    for s in wszystkie():
        n = len(kroki(s.nazwa))
        czesci.append(f"/{s.nazwa.lower()} ({n})")
    return "🔏 SIGLA IMPERII: " + " | ".join(czesci) + " — kroki żywe z CLAUDE.md"


def synchronizuj_w11(plik: Optional[Path] = None) -> Dict[str, str]:
    """Przepisuje ŻYWE kroki sigli do pamięci proceduralnej (W11).

    Dzięki temu runbooki W11 przestają być ręcznym tekstem, który gnije — a
    wyszukiwanie po słowach (`pamiec_proceduralna.szukaj`) trafia w sigla nawet
    wtedy, gdy Cezar pisze zwykłym zdaniem, bez ukośnika.
    Zwraca mapę nazwa → 'dodano' | 'zaktualizowano' | 'bez zmian'.
    """
    from imperium.biblioteki import pamiec_proceduralna as w11

    wynik: Dict[str, str] = {}
    for s in wszystkie():
        lst = kroki(s.nazwa)
        if not lst:
            wynik[s.nazwa] = "pominięto (pieczęć pusta)"
            continue
        wynik[s.nazwa] = w11.zapisz(
            nazwa=s.tytul,
            kroki=lst,
            wyzwalacz=", ".join(s.wyzwalacze),
            zrodlo=s.zrodlo,
            plik=plik,
        )
    return wynik


def _main(argv: List[str]) -> int:
    arg = (argv[1] if len(argv) > 1 else "lista").strip().lower()
    if arg in ("lista", "--lista", "-l"):
        print("🔏 SIGLA IMPERII — pieczęcie uruchamiające pełne procedury:\n")
        for s in wszystkie():
            print(f"  /{s.nazwa.lower():<9} {s.opis}")
            print(f"  {'':<10} wyzwalacze: {', '.join(s.wyzwalacze)}")
            print(f"  {'':<10} kroków: {len(kroki(s.nazwa))} (żywe, z {s.zrodlo})\n")
        return 0
    if arg in ("sync-w11", "--sync-w11"):
        for nazwa, stan in synchronizuj_w11().items():
            print(f"  {nazwa}: {stan}")
        return 0
    print(raport(arg))
    return 0 if sigillum(arg) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main(sys.argv))
