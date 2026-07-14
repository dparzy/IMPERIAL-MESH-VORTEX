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
import json
import logging
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


def scout_temat(glos, temat: str, topk: int = 6, tryb: str = "fts",
                korpus: str | None = "biblioteka") -> dict:
    """Jeden temat: RAG → DeepSeek proponuje kandydatów. Zwraca dict cząstki (do kolejki).

    Zakłada, że indeks RAG ISTNIEJE (bramkuje raport() — Cubic P2). Status cząstki:
    'ok' = kandydaci od DeepSeeka, 'dry' = podgląd RAG bez API, 'pusto' = brak trafień.

    U1 (anty-echo, Prawo XVI): domyślnie czytamy TYLKO korpus 'biblioteka' (książki BIB-xxx),
    nie 'docs'/'dane' — inaczej Hyginus wyciąga NASZE własne notatki i podaje je jako
    „odkrycie" (echo własnego głosu = redundancja). korpus=None świadomie omija filtr."""
    from szukaj import szukaj  # type: ignore[import]
    wyniki = szukaj(temat, topk=topk, tryb=tryb, cichy=True, korpus=korpus)
    zrodla = sorted({w.zrodlo for w in wyniki})
    if not wyniki:                          # indeks jest (bramka w raport), więc to REALNY brak trafień
        return {"temat": temat, "zrodla": [], "kandydaci": "(brak fragmentów RAG)",
                "status": "pusto", "ts": time.time()}
    if glos is None:                       # dry-run: bez DeepSeeka, tylko podgląd RAG
        return {"temat": temat, "zrodla": zrodla,
                "kandydaci": "(dry-run — DeepSeek pominięty)", "status": "dry", "ts": time.time()}
    tresc = f"TEMAT: {temat}\n\nFRAGMENTY:\n{_fragmenty_tekst(wyniki)}"
    odp = glos.zapytaj(_SYSTEM, tresc, temperatura=0.4)
    return {"temat": temat, "zrodla": zrodla, "kandydaci": odp.strip(),
            "status": "ok", "ts": time.time()}


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


def raport(tematy, topk=6, tryb="fts", dry_run=False, force=False, korpus="biblioteka") -> str:
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
            czastka = scout_temat(glos, temat, topk=topk, tryb=tryb, korpus=korpus)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ „{temat}”: {e}", file=sys.stderr, flush=True)
            continue
        zapisz_czastke(czastka)
        zr = ", ".join(czastka["zrodla"][:5]) or "—"
        print(f"[{i}/{N}] ✅ „{temat}” → źródła: {zr} | 💾 kolejka", file=sys.stderr, flush=True)
        linie.append(f"\n── [{i}/{N}] {temat} (źródła: {zr}) ──\n{czastka['kandydaci']}")

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
    p.add_argument("--tryb", default="fts", choices=["fts", "hybrid", "wektor"])
    p.add_argument("--korpus", default="biblioteka", choices=["biblioteka", "dane", "docs", "wszystko"],
                   help="korpus RAG do zwiadu (U1: domyślnie 'biblioteka' — tylko książki, anty-echo docs)")
    p.add_argument("--dry-run", action="store_true", help="tylko RAG, bez DeepSeek (bez kosztu API)")
    p.add_argument("--force", action="store_true", help="przeskanuj też tematy już w kolejce")
    args = p.parse_args()

    tematy = args.temat or TEMATY_DOMYSLNE
    korpus = None if args.korpus == "wszystko" else args.korpus  # 'wszystko' → bez filtra (dawne zachowanie)
    print(raport(tematy, topk=args.topk, tryb=args.tryb, dry_run=args.dry_run,
                 force=args.force, korpus=korpus))
