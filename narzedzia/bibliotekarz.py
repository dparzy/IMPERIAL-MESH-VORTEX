"""
📚 HYGINUS — BIBLIOTEKARZ-ZWIADOWCA Imperium. DeepSeek skanuje bibliotekę i proponuje KANDYDATÓW
(pod nadzorem Vitruviusza/Opusa).

Imię (Cezar Pixel, 2026-07-13): GAIUS JULIUS HYGINUS — wyzwoleniec Augusta, pierwszy prefekt
Biblioteki Palatyńskiej (pierwszej cesarskiej biblioteki), uczony-polihistor i zarządca zbiorów.
Symetria epoki: Vitruviusz (Architekt) + Hyginus (Bibliotekarz) — obaj ze złotego wieku Augusta.

Operacjonalizacja ZASADY ZWIADOWCY WIEDZY (CLAUDE.md): DWA modele o różnych rolach.
  • DeepSeek (deepseek-v4-flash, tani ~$0.14/1M) = HYGINUS, ZWIADOWCA/proponent — czyta fragmenty
    RAG biblioteki i wyciąga KANDYDATÓW na neurony/strategie/koncepcje.
  • Opus/Vitruviusz = SĘDZIA/krytyk kompletności — czyta kolejkę kandydatów, weryfikuje, odrzuca
    halucynacje, decyduje co idzie do areny.

ŻELAZNE ZASADY (Prawo I + ZASADA WPIĘCIA):
  • Każdy wynik DeepSeeka = ⚠️ HIPOTEZA/KANDYDAT, NIGDY fakt. Trafia do kolejki, NIE do kodu.
  • Rozstrzyga wyłącznie POMIAR areny (IC/WFO/P&L). Wpięcie w ścieżkę = opt-in OFF + A/B.
  • DeepSeek proponuje TYLKO z podanych fragmentów, cytuje źródło (BIB-xxx). Zero wymyślania.

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): temat → RAG → DeepSeek → ZAPIS do kolejki JSONL
ZANIM ruszy następny temat (wznawialność, nic nie ginie). Pasek postępu na stderr (Prawo XXIV).

Użycie:
  python narzedzia/bibliotekarz.py --temat "momentum mean-reversion regime"     # jeden temat
  python narzedzia/bibliotekarz.py                                              # domyślne tematy
  python narzedzia/bibliotekarz.py --dry-run                                    # tylko RAG, bez DeepSeek (bez kosztu)
"""

from __future__ import annotations

import argparse
import functools
import json
import logging
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))

KOLEJKA = ROOT / "docs" / "KOLEJKA_HIPOTEZ_BIBLIOTEKARZ.jsonl"

# Domyślne tematy zwiadu — luki/obszary rozwoju roju (można nadpisać --temat).
TEMATY_DOMYSLNE = [
    "momentum trend-following breakout entry rules",
    "mean reversion overextension bands entry",
    "market regime detection volatility filter",
    "order flow volume delta absorption",
    "risk position sizing stop placement expectancy",
]

_SYSTEM = (
    "Jesteś HYGINUSEM — Bibliotekarzem-Zwiadowcą Imperium tradingowego. Dostajesz FRAGMENTY z książek "
    "(z oznaczeniem źródła BIB-xxx). Twoje zadanie: zaproponuj 1-4 KANDYDATÓW na nowy neuron/"
    "strategię/koncepcję, WYŁĄCZNIE na podstawie podanych fragmentów. ŻELAZNE ZASADY:\n"
    "1. Każdy kandydat to HIPOTEZA, nie fakt — nie twierdź, że coś działa.\n"
    "2. Cytuj źródło (BIB-xxx) dla każdego kandydata. Nie wymyślaj źródeł ani nazw.\n"
    "3. Dla każdego podaj: nazwa, typ (neuron/strategia/koncepcja), zwięzły opis mechanizmu, "
    "oraz JAK to ZMIERZYĆ w backteście (co byłoby dowodem przewagi).\n"
    "4. Jeśli fragmenty nie niosą nic wartościowego — powiedz to wprost, nie konfabuluj.\n"
    "Odpowiedz ZWIĘZŁO, po polsku, w punktach. Bez wstępów."
)


def _fragmenty_tekst(wyniki) -> str:
    """Składa fragmenty RAG w blok dla DeepSeeka (źródło + tekst, przycięte)."""
    czesci = []
    for w in wyniki:
        tekst = (w.tekst or "")[:900]
        czesci.append(f"[{w.zrodlo} — {w.tytul}, chunk {w.nr_chunk}]\n{tekst}")
    return "\n\n---\n\n".join(czesci)


_RE_SLOWO = re.compile(r"[A-Za-z0-9]+")


def _fts_bezpieczne(q: str) -> str:
    """U2: sanityzacja do bezpiecznej składni FTS5 — tylko słowa złączone OR.

    Bez tego myślniki/słowa-klucze FTS wywalają MATCH (realny bug: temat
    'momentum trend-following breakout entry rules' → OperationalError
    'no such column: following' → temat cicho ginął). OR poszerza recall
    (trafienie na dowolny termin), a BM25 i tak rankuje najlepsze na górę."""
    slowa = _RE_SLOWO.findall(q or "")
    return " OR ".join(slowa) if slowa else q


_SYSTEM_ROZWIN = (
    "Jesteś asystentem wyszukiwania pełnotekstowego w anglojęzycznej bibliotece tradingowej. "
    "Rozwiń podany TEMAT w bogate zapytanie: dodaj synonimy, terminy techniczne i pokrewne "
    "pojęcia (trading, finance, statistics). Zwróć WYŁĄCZNIE słowa kluczowe po angielsku, "
    "oddzielone spacjami — bez zdań, bez wyjaśnień, bez interpunkcji. Maksymalnie 30 słów."
)


def rozwin_zapytanie(glos, temat: str) -> str:
    """U2: DeepSeek rozszerza temat w zapytanie bogate w synonimy → lepszy recall FTS.

    Retrieval-only: NIE generuje kandydatów, więc ryzyko halucynacji ograniczone do trafień
    RAG, które i tak filtruje sędzia (Opus) + arena. Fallback na oryginalny temat przy pustej/
    błędnej odpowiedzi — zwiad nigdy nie ginie przez błąd rozszerzenia (Prawo XV)."""
    try:
        odp = glos.zapytaj(_SYSTEM_ROZWIN, f"TEMAT: {temat}", temperatura=0.3)
    except Exception:  # noqa: BLE001 — błąd API nie może zabić zwiadu; wracamy do surowego tematu
        return temat
    slowa = _RE_SLOWO.findall(odp or "")
    return " ".join(slowa[:40]) or temat


# U3: sufiks szukania DOWODÓW PRZECIW — poszerza retrieval o kontrargumenty (ryzyka, założenia,
# ograniczenia, sprzeczne wyniki), których „happy-path" zwiad by nie pobrał.
_KONTRA_SUFIKS = "risk failure limitation assumption drawback criticism overfitting"

_SYSTEM_KRYTYKA = (
    "Jesteś SĘDZIĄ-SCEPTYKIEM Imperium (ZASADA ZWIADOWCY WIEDZY: kandydat≠prawda). Dostajesz "
    "KANDYDATÓW (hipotezy Bibliotekarza) oraz FRAGMENTY z biblioteki. Dla KAŻDEGO kandydata wskaż "
    "DOWODY PRZECIW: co w tych fragmentach go podważa, ogranicza lub mu zaprzecza (ukryte założenia, "
    "warunki ważności, znane pułapki, sprzeczne wyniki, ryzyko overfittingu). Oceń wsparcie dowodowe "
    "każdego: MOCNE / SŁABE / SPRZECZNE. Jeśli NIE znajdujesz dowodów przeciw — powiedz to wprost "
    "(to sygnał możliwej stronniczości potwierdzenia, nie dowód słuszności). Surowo, zwięźle, po polsku."
)


def krytyka_kandydatow(glos, kandydaci: str, wyniki_kontra) -> str:
    """U3 (self-critique): drugie przejście — sędzia-sceptyk szuka DOWODÓW PRZECIW kandydatom.

    Wzorzec agentic-RAG: po hipotezie szukamy dowodów DISCONFIRMING, by ograniczyć confirmation
    bias. Wynik ląduje w polu 'krytyka' cząstki — Opus-sędzia i arena widzą od razu słabe hipotezy.
    Błąd API nie może zabić zwiadu (Prawo XV): zwracamy komunikat, kandydaci już są zapisani."""
    tresc = (f"KANDYDACI:\n{kandydaci}\n\n"
             f"FRAGMENTY (możliwe kontrargumenty):\n{_fragmenty_tekst(wyniki_kontra)}")
    try:
        return glos.zapytaj(_SYSTEM_KRYTYKA, tresc, temperatura=0.3).strip()
    except Exception:  # noqa: BLE001 — krytyka to dodatek; jej brak nie przekreśla cząstki
        return "(krytyka niedostępna — błąd API)"


@functools.lru_cache(maxsize=1)
def _kontekst_systemu() -> str:
    """U4 (świadomość systemu): zwięzły blok o LUKACH (Prawo XV) i ISTNIEJĄCYCH modułach
    (anty-redundancja, Prawo XVI), wstrzykiwany DeepSeekowi przy generacji kandydatów.

    Dzięki temu Hyginus proponuje pod REALNE braki roju i wie, co już istnieje — odtwarza
    główną siłę ręcznego web-DeepSeeka (kontekst systemu), ale ze źródeł biblioteki. Cache 1×
    (rejestr nie zmienia się w trakcie biegu). Brak rejestru → '' (zwiad działa dalej, Prawo XV)."""
    try:
        from imperium.legiony.rejestr import wszystkie_neurony
        from narzedzia.audyt_spojnosci import NEURONY_ZALEZNE_OD_ADAPTEROW as LUKI
    except Exception:  # noqa: BLE001 — brak rejestru/audytu nie może zabić zwiadu
        return ""
    neurony = wszystkie_neurony()
    istniejace = ", ".join(sorted({n.KLUCZ for n in neurony}))
    kategorie = ", ".join(sorted({n.KATEGORIA for n in neurony}))
    luki = "; ".join(f"{k} ({opis})" for k, opis in sorted(LUKI.items()))
    return (
        "\n\nKONTEKST IMPERIUM (świadomość systemu — steruj doborem kandydatów):\n"
        f"• ISTNIEJĄCE moduły — NIE proponuj duplikatów (Prawo XVI): {istniejace}\n"
        f"• Kategorie w użyciu: {kategorie}\n"
        f"• LUKI — moduły milczące, czekają na dane/adapter; PREFERUJ kandydatów, którzy je "
        f"zasilają lub wnoszą NOWĄ informację: {luki}\n"
        "Dla KAŻDEGO kandydata dopisz: (a) którą LUKĘ zasila LUB jaką NOWĄ informację wnosi, "
        "(b) czy NIE dubluje istniejącego modułu."
    )


def scout_temat(glos, temat: str, topk: int = 6, tryb: str = "hybrid",
                korpus: str | None = "biblioteka", rozwin: bool = False,
                krytyka: bool = False, swiadomosc: bool = False,
                probator: bool = True) -> dict:
    """Jeden temat: RAG → DeepSeek proponuje kandydatów. Zwraca dict cząstki (do kolejki).

    Zakłada, że indeks RAG ISTNIEJE (bramkuje raport() — Cubic P2). Status cząstki:
    'ok' = kandydaci od DeepSeeka, 'dry' = podgląd RAG bez API, 'pusto' = brak trafień.

    U1 (anty-echo, Prawo XVI): domyślnie czytamy TYLKO korpus 'biblioteka' (książki BIB-xxx),
    nie 'docs'/'dane' — inaczej Hyginus wyciąga NASZE własne notatki i podaje je jako
    „odkrycie" (echo własnego głosu = redundancja). korpus=None świadomie omija filtr.

    U2 (recall): tryb domyślnie 'hybrid' (auto-fallback na FTS gdy brak wektorów). Gdy rozwin=True
    DeepSeek rozszerza temat w synonimy PRZED RAG. Zapytanie ZAWSZE sanityzowane do bezpiecznej
    składni FTS5 (_fts_bezpieczne) — inaczej myślniki/słowa-klucze wywalają MATCH."""
    from szukaj import szukaj  # type: ignore[import]
    zapytanie = rozwin_zapytanie(glos, temat) if (rozwin and glos is not None) else temat
    wyniki = szukaj(_fts_bezpieczne(zapytanie), topk=topk, tryb=tryb, cichy=True, korpus=korpus)
    zrodla = sorted({w.zrodlo for w in wyniki})
    baza = {"temat": temat, "zapytanie": zapytanie, "ts": time.time()}
    if not wyniki:                          # indeks jest (bramka w raport), więc to REALNY brak trafień
        return {**baza, "zrodla": [], "kandydaci": "(brak fragmentów RAG)", "status": "pusto"}
    if glos is None:                       # dry-run: bez DeepSeeka, tylko podgląd RAG
        return {**baza, "zrodla": zrodla,
                "kandydaci": "(dry-run — DeepSeek pominięty)", "status": "dry"}
    tresc = f"TEMAT: {temat}\n\nFRAGMENTY:\n{_fragmenty_tekst(wyniki)}"
    if swiadomosc:  # U4: dołącz świadomość systemu (luki + istniejące moduły) do generacji kandydatów
        tresc += _kontekst_systemu()
    odp = glos.zapytaj(_SYSTEM, tresc, temperatura=0.4)
    rec = {**baza, "zrodla": zrodla, "kandydaci": odp.strip(), "status": "ok"}
    if probator:  # WARSTWA 1 anty-halucynacyjna: cytat spoza podanych fragmentów (0 tokenów)
        from imperium.pretorianie.probator import do_slownika, sprawdz
        rec["probator"] = do_slownika(sprawdz(rec["kandydaci"], wyniki))
    if krytyka:  # U3: drugie przejście — dowody PRZECIW (osobne retrieval na kontrargumenty)
        kontra = szukaj(_fts_bezpieczne(f"{zapytanie} {_KONTRA_SUFIKS}"),
                        topk=topk, tryb=tryb, cichy=True, korpus=korpus)
        rec["krytyka"] = krytyka_kandydatow(glos, rec["kandydaci"], kontra)
        if probator:  # krytyka to też plon modelu — bada się ją wobec WŁASNYCH fragmentów
            from imperium.pretorianie.probator import do_slownika, sprawdz
            rec["probator_krytyka"] = do_slownika(sprawdz(rec["krytyka"], kontra))
    return rec


def _tematy_ukonczone() -> set:
    """Tematy już zeskanowane realnie (status ≠ 'dry') w kolejce — by NIE płacić DeepSeekowi
    ponownie ani nie dublować kandydatów (Cubic P2). Stare rekordy bez pola status = ukończone."""
    if not KOLEJKA.exists():
        return set()
    done = set()
    with open(KOLEJKA, encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                continue
            try:
                rec = json.loads(linia)
            except json.JSONDecodeError:
                continue
            if rec.get("temat") and rec.get("status") != "dry":
                done.add(rec["temat"])
    return done


def zapisz_czastke(czastka: dict) -> None:
    """Dopisz kandydatów tematu do kolejki JSONL (ZASADA ANALIZY CZĄSTKOWEJ — natychmiast)."""
    KOLEJKA.parent.mkdir(parents=True, exist_ok=True)
    with open(KOLEJKA, "a", encoding="utf-8") as f:
        f.write(json.dumps(czastka, ensure_ascii=False) + "\n")


def raport(tematy, topk=6, tryb="hybrid", dry_run=False, force=False, korpus="biblioteka",
           rozwin=False, krytyka=False, swiadomosc=False, probator=True) -> str:
    # Cubic P2: bramka indeksu RAG — brak bazy to AWARIA INFRY, nie „pusty wynik". Nie skanujemy
    # i NIC nie zapisujemy do kolejki (inaczej awaria udawałaby ukończony, pusty zwiad).
    from szukaj import DEFAULT_BAZA  # type: ignore[import]
    if not DEFAULT_BAZA.exists():
        return (f"🚨 BIBLIOTEKARZ — brak indeksu RAG ({DEFAULT_BAZA}). "
                "Uruchom: python narzedzia/rag/indeksuj.py. Nic nie zeskanowano ani nie zapisano.")

    glos = None
    if not dry_run:
        from imperium.cesarz.deepseek_glos import GlosImperium
        glos = GlosImperium()   # domyślny = deepseek-v4-flash (tani zwiadowca; Prawo XVI: rola proponenta)

    # Cubic P2: pomiń tematy już zeskanowane realnie (chyba że --force) — zero podwójnego kosztu API.
    zrobione = set() if force else _tematy_ukonczone()

    N = len(tematy)
    podejrzane: list[str] = []      # tematy, w których PROBATOR złapał cytat spoza fragmentów
    linie = [f"📚 HYGINUS (Bibliotekarz-Zwiadowca) — {N} tematów, {'DRY-RUN' if dry_run else 'DeepSeek'} "
             f"(⚠️ KANDYDACI — prawdą po arenie)"]
    for i, temat in enumerate(tematy, 1):
        if temat in zrobione:
            print(f"[{i}/{N}] ⏭️ „{temat}” — już w kolejce (pomijam; --force by przeliczyć)",
                  file=sys.stderr, flush=True)
            linie.append(f"\n── [{i}/{N}] {temat} — pominięty (już zeskanowany; --force by powtórzyć) ──")
            continue
        print(f"[{i}/{N}] zwiad: „{temat}” — RAG + {'(dry)' if dry_run else 'DeepSeek'}…",
              file=sys.stderr, flush=True)
        try:
            czastka = scout_temat(glos, temat, topk=topk, tryb=tryb, korpus=korpus,
                                  rozwin=rozwin, krytyka=krytyka, swiadomosc=swiadomosc,
                                  probator=probator)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ „{temat}”: {e}", file=sys.stderr, flush=True)
            continue
        zapisz_czastke(czastka)
        zr = ", ".join(czastka["zrodla"][:5]) or "—"
        print(f"[{i}/{N}] ✅ „{temat}” → źródła: {zr} | 💾 kolejka", file=sys.stderr, flush=True)
        # PROBATOR mówi tylko wtedy, gdy ma co zarzucić — cisza znaczy „cytaty się zgadzają".
        pro = czastka.get("probator") or {}
        if pro and not pro.get("czysty", True):
            print(f"[{i}/{N}] {pro['opis']}", file=sys.stderr, flush=True)
            podejrzane.append(f"{temat} → {pro['opis']}")
        linie.append(f"\n── [{i}/{N}] {temat} (źródła: {zr}) ──\n{czastka['kandydaci']}")
        if pro:
            linie.append(pro["opis"])

    if podejrzane:
        linie.append(f"\n🚨 PROBATOR — {len(podejrzane)}/{N} tematów z cytatem spoza podanych "
                     f"fragmentów (halucynacja citation; sędzia niech czyta je najostrożniej):")
        linie.extend(f"   • {x}" for x in podejrzane)
    linie.append(f"\n💾 Kolejka: {KOLEJKA.relative_to(ROOT)} — do PRZEGLĄDU Opusa (sędzia). "
                 f"Nic nie wchodzi do kodu bez weryfikacji + areny (Prawo I, ZASADA WPIĘCIA).")
    return "\n".join(linie)


_TOPK_MAX = 20


def _topk_arg(tekst: str) -> int:
    """Cubic P2: ogranicz --topk do małego dodatniego zakresu — bez tego wielki/ujemny topk
    ściąga nieograniczony korpus i wysyła go do PŁATNEGO API."""
    v = int(tekst)
    if not (1 <= v <= _TOPK_MAX):
        raise argparse.ArgumentTypeError(f"--topk musi być w [1, {_TOPK_MAX}], podano: {tekst}")
    return v


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="HYGINUS — Bibliotekarz-Zwiadowca, DeepSeek skanuje bibliotekę (W-363)")
    p.add_argument("--temat", action="append", help="temat zwiadu (można wiele razy). Brak → domyślne.")
    p.add_argument("--topk", type=_topk_arg, default=6, help=f"ile fragmentów RAG na temat [1, {_TOPK_MAX}]")
    p.add_argument("--tryb", default="hybrid", choices=["fts", "hybrid", "wektor"],
                   help="U2: domyślnie 'hybrid' (semantyka+FTS; auto-fallback na FTS gdy brak wektorów)")
    p.add_argument("--korpus", default="biblioteka", choices=["biblioteka", "dane", "docs", "wszystko"],
                   help="korpus RAG do zwiadu (U1: domyślnie 'biblioteka' — tylko książki, anty-echo docs)")
    p.add_argument("--rozwin", action="store_true",
                   help="U2: rozszerz temat przez DeepSeek w synonimy przed RAG (lepszy recall; +1 tani call/temat)")
    p.add_argument("--krytyka", action="store_true",
                   help="U3: self-critique — drugie przejście szuka DOWODÓW PRZECIW kandydatom (+1 RAG +1 call/temat)")
    p.add_argument("--swiadomosc", action="store_true",
                   help="U4: wstrzyknij świadomość systemu (luki Prawa XV + istniejące klucze) — kandydaci pod realne braki")
    p.add_argument("--pelny", action="store_true",
                   help="komplet U2+U3+U4: --rozwin --krytyka --swiadomosc naraz (najlepszy zwiad)")
    p.add_argument("--bez-probatora", action="store_true",
                   help="wyłącz PROBATORA (strażnik cytatów, 0 tokenów) — domyślnie WŁĄCZONY")
    p.add_argument("--dry-run", action="store_true", help="tylko RAG, bez DeepSeek (bez kosztu API)")
    p.add_argument("--force", action="store_true", help="przeskanuj też tematy już w kolejce")
    args = p.parse_args()

    tematy = args.temat or TEMATY_DOMYSLNE
    korpus = None if args.korpus == "wszystko" else args.korpus  # 'wszystko' → bez filtra (dawne zachowanie)
    rozwin = args.rozwin or args.pelny
    krytyka = args.krytyka or args.pelny
    swiadomosc = args.swiadomosc or args.pelny
    print(raport(tematy, topk=args.topk, tryb=args.tryb, dry_run=args.dry_run,
                 force=args.force, korpus=korpus, rozwin=rozwin, krytyka=krytyka,
                 swiadomosc=swiadomosc, probator=not args.bez_probatora))
