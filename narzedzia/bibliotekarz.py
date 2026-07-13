"""
📚 BIBLIOTEKARZ-ZWIADOWCA — DeepSeek skanuje bibliotekę i proponuje KANDYDATÓW (pod nadzorem Opusa).

Operacjonalizacja ZASADY ZWIADOWCY WIEDZY (CLAUDE.md): DWA modele o różnych rolach.
  • DeepSeek (deepseek-v4-flash, tani ~$0.14/1M) = ZWIADOWCA/proponent — czyta fragmenty RAG
    biblioteki i wyciąga KANDYDATÓW na neurony/strategie/koncepcje.
  • Opus/Claude = SĘDZIA/krytyk kompletności — czyta kolejkę kandydatów, weryfikuje, odrzuca
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
    "Jesteś Bibliotekarzem-Zwiadowcą Imperium tradingowego. Dostajesz FRAGMENTY z książek "
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


def scout_temat(glos, temat: str, topk: int = 6, tryb: str = "fts") -> dict:
    """Jeden temat: RAG → DeepSeek proponuje kandydatów. Zwraca dict cząstki (do kolejki)."""
    from szukaj import szukaj  # type: ignore[import]
    wyniki = szukaj(temat, topk=topk, tryb=tryb, cichy=True)
    zrodla = sorted({w.zrodlo for w in wyniki})
    if not wyniki:
        return {"temat": temat, "zrodla": [], "kandydaci": "(brak fragmentów RAG)", "ts": time.time()}
    if glos is None:                       # dry-run: bez DeepSeeka, tylko podgląd RAG
        return {"temat": temat, "zrodla": zrodla,
                "kandydaci": "(dry-run — DeepSeek pominięty)", "ts": time.time()}
    tresc = f"TEMAT: {temat}\n\nFRAGMENTY:\n{_fragmenty_tekst(wyniki)}"
    odp = glos.zapytaj(_SYSTEM, tresc, temperatura=0.4)
    return {"temat": temat, "zrodla": zrodla, "kandydaci": odp.strip(), "ts": time.time()}


def zapisz_czastke(czastka: dict) -> None:
    """Dopisz kandydatów tematu do kolejki JSONL (ZASADA ANALIZY CZĄSTKOWEJ — natychmiast)."""
    KOLEJKA.parent.mkdir(parents=True, exist_ok=True)
    with open(KOLEJKA, "a", encoding="utf-8") as f:
        f.write(json.dumps(czastka, ensure_ascii=False) + "\n")


def raport(tematy, topk=6, tryb="fts", dry_run=False) -> str:
    glos = None
    if not dry_run:
        from imperium.cesarz.deepseek_glos import GlosImperium
        glos = GlosImperium()   # domyślny = deepseek-v4-flash (tani zwiadowca; Prawo XVI: rola proponenta)

    N = len(tematy)
    linie = [f"📚 BIBLIOTEKARZ-ZWIADOWCA — {N} tematów, {'DRY-RUN' if dry_run else 'DeepSeek'} "
             f"(⚠️ KANDYDACI — prawdą po arenie)"]
    for i, temat in enumerate(tematy, 1):
        print(f"[{i}/{N}] zwiad: „{temat}” — RAG + {'(dry)' if dry_run else 'DeepSeek'}…",
              file=sys.stderr, flush=True)
        try:
            czastka = scout_temat(glos, temat, topk=topk, tryb=tryb)
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


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Bibliotekarz-Zwiadowca — DeepSeek skanuje bibliotekę (W-363)")
    p.add_argument("--temat", action="append", help="temat zwiadu (można wiele razy). Brak → domyślne.")
    p.add_argument("--topk", type=int, default=6, help="ile fragmentów RAG na temat")
    p.add_argument("--tryb", default="fts", choices=["fts", "hybrid", "wektor"])
    p.add_argument("--dry-run", action="store_true", help="tylko RAG, bez DeepSeek (bez kosztu API)")
    args = p.parse_args()

    tematy = args.temat or TEMATY_DOMYSLNE
    print(raport(tematy, topk=args.topk, tryb=args.tryb, dry_run=args.dry_run))
