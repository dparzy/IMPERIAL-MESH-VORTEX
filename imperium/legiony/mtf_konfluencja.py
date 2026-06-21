"""
🕐 IMV-MTF | Konfluencja Multi-Timeframe na poziomie ROJU (W-384).

PROBLEM (zgłoszony przez Cezara 2026-06-21): Imperium podejmuje decyzję o orderze
na JEDNYM interwale. Jedyna nadbudowa MTF (X-28) używa tylko RSI+EMA i karmi 1 neuron —
pozostałe 80 widzą jeden TF. Prawdziwy trader sprawdza pełny stos czasowy przed wejściem.

ROZWIĄZANIE: brama konfluencji na poziomie roju (jak Senat — warstwa NAD Legatusem).
Po decyzji kierunkowej roju sprawdzamy, czy WYŻSZE interwały ją potwierdzają:
  • wejście ZGODNE z wyższym TF → wzmocnienie (mnoznik > 1)
  • wejście PRZECIW wyższym TF → tłumienie (mnoznik < 1) lub weto (opt-in)

Trend wyższego TF liczony robustnie (EMA50 vs EMA200 + nachylenie + MACD znak),
nie jednym oscylatorem. Agregacja w GÓRĘ z barów bieżącego TF (bez dodatkowych danych).

ZALEŻNOŚCI: tylko numpy. Bez lookahead (agreguje domknięte bary historyczne).
"""

from __future__ import annotations

from typing import Dict, List, Any

import numpy as np

# Które wyższe TF sprawdzać dla danego interwału bazowego (mnożnik agregacji).
# Spójne z budowniczy_wskaznikow._MTF_INTERWAL_MNOZNIKI, rozszerzone w dół stosu.
_STOS_TF: Dict[str, Dict[str, int]] = {
    "1m":  {"15m": 15, "1h": 60},
    "5m":  {"15m": 3, "1h": 12, "4h": 48},
    "15m": {"1h": 4, "4h": 16},
    "1h":  {"4h": 4, "1d": 24},
    "1H":  {"4h": 4, "1d": 24},
    "4h":  {"1d": 6, "1w": 42},
    "4H":  {"1d": 6, "1w": 42},
    "1d":  {"1w": 7},
}

_MIN_BAROW_TF = 60   # min barów wyższego TF do oceny trendu (EMA200 potrzebuje historii)


def _ema(wartosci: np.ndarray, okres: int) -> float:
    """Wykładnicza średnia krocząca — ostatnia wartość."""
    if len(wartosci) == 0:
        return float("nan")
    k = 2.0 / (okres + 1)
    ema = float(wartosci[0])
    for v in wartosci[1:]:
        ema = float(v) * k + ema * (1 - k)
    return ema


def _agreguj(bary: List[Dict[str, Any]], n: int) -> List[Dict[str, float]]:
    """Agreguje bary do wyższego TF grupując po N (OHLCV poprawnie, bez ostatniej niepełnej)."""
    wynik = []
    pelne = (len(bary) // n) * n
    for i in range(0, pelne, n):
        okno = bary[i:i + n]
        wynik.append({
            "open": float(okno[0].get("open", 0)),
            "high": max(float(b.get("high", 0)) for b in okno),
            "low": min(float(b.get("low", 0)) for b in okno),
            "close": float(okno[-1].get("close", 0)),
            "volume": sum(float(b.get("volume", 0)) for b in okno),
        })
    return wynik


def _kierunek_trendu(bary_tf: List[Dict[str, float]]) -> str:
    """
    Robustny kierunek trendu wyższego TF:
      EMA50 vs EMA200 (struktura) + cena vs EMA50 + MACD znak (momentum).
      LONG gdy ≥2/3 sygnałów bull, SHORT gdy ≥2/3 bear, inaczej NEUTRAL.
    """
    if len(bary_tf) < _MIN_BAROW_TF:
        return "NEUTRAL"
    close = np.array([b["close"] for b in bary_tf], dtype=float)
    ema50 = _ema(close[-200:] if len(close) >= 200 else close, 50)
    ema200 = _ema(close, 200) if len(close) >= 200 else _ema(close, len(close))
    macd = _ema(close, 12) - _ema(close, 26)
    cena = float(close[-1])

    bull = sum([ema50 > ema200, cena > ema50, macd > 0])
    bear = sum([ema50 < ema200, cena < ema50, macd < 0])
    if bull >= 2 and bull > bear:
        return "LONG"
    if bear >= 2 and bear > bull:
        return "SHORT"
    return "NEUTRAL"


def ocena_konfluencji_tf(
    bary: List[Dict[str, Any]],
    interwal: str,
    kierunek_glowny: str,
    prog_weta: float = -1.0,
) -> Dict[str, Any]:
    """
    🕐 W-384 | Ocena konfluencji wyższych TF względem decyzji roju.

    bary:            bary bieżącego (bazowego) interwału
    interwal:        etykieta TF bazowego ("1h", "4h", "1d"...)
    kierunek_glowny: decyzja roju ("LONG"/"SHORT")
    prog_weta:       wyrownanie ≤ prog_weta → weto (domyślnie -1.0 = tylko pełna opozycja)

    Zwraca:
      wyrownanie:  -1..+1 (średnia zgodności wyższych TF z kierunkiem roju)
      tf_kierunki: {tf: "LONG"/"SHORT"/"NEUTRAL"}
      mnoznik:     0.5..1.2 — skala pewności/rozmiaru (zgodność→>1, opozycja→<1)
      weto:        bool — czy wyższe TF na tyle przeciwne, że blokują wejście
      werdykt:     opis tekstowy
    """
    if kierunek_glowny not in ("LONG", "SHORT") or not bary:
        return {"wyrownanie": 0.0, "tf_kierunki": {}, "mnoznik": 1.0,
                "weto": False, "werdykt": "brak kierunku/barów — neutralnie"}

    stos = _STOS_TF.get(interwal, {})
    if not stos:
        return {"wyrownanie": 0.0, "tf_kierunki": {}, "mnoznik": 1.0,
                "weto": False, "werdykt": f"brak stosu TF dla '{interwal}'"}

    tf_kierunki: Dict[str, str] = {}
    zgodne = przeciwne = ocenione = 0
    for tf, n in stos.items():
        bary_tf = _agreguj(bary, n)
        kier = _kierunek_trendu(bary_tf)
        tf_kierunki[tf] = kier
        if kier == "NEUTRAL":
            continue
        ocenione += 1
        if kier == kierunek_glowny:
            zgodne += 1
        else:
            przeciwne += 1

    if ocenione == 0:
        return {"wyrownanie": 0.0, "tf_kierunki": tf_kierunki, "mnoznik": 1.0,
                "weto": False, "werdykt": "wyższe TF neutralne — brak konfluencji"}

    wyrownanie = (zgodne - przeciwne) / ocenione  # -1..+1

    # mnoznik: liniowo od 0.5 (pełna opozycja) do 1.2 (pełna zgodność)
    mnoznik = 1.0 + 0.2 * wyrownanie if wyrownanie >= 0 else 1.0 + 0.5 * wyrownanie
    mnoznik = max(0.5, min(1.2, mnoznik))

    weto = wyrownanie <= prog_weta

    if wyrownanie >= 0.5:
        werdykt = f"KONFLUENCJA ↑ wyższe TF potwierdzają {kierunek_glowny} ({zgodne}/{ocenione})"
    elif wyrownanie <= -0.5:
        werdykt = f"KONFLIKT ↓ wyższe TF przeciw {kierunek_glowny} ({przeciwne}/{ocenione})"
    else:
        werdykt = f"mieszane TF: zgodne={zgodne} przeciwne={przeciwne} z {ocenione}"

    return {
        "wyrownanie": round(wyrownanie, 3),
        "tf_kierunki": tf_kierunki,
        "mnoznik": round(mnoznik, 3),
        "weto": weto,
        "werdykt": werdykt,
    }
