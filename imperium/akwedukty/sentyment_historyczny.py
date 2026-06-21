"""
📡 Sentyment historyczny — most między historią futures (funding/OI/LS) a osią barów.

CEL (Prawo XVI — mierz, nie zgaduj):
  PSY-01/02/04 (funding, long/short, open interest) żyją tylko w trybie LIVE,
  bo backtest_portfel nie miał historycznych danych sentymentu. Bez pomiaru nie
  wiemy, czy te neurony dodają przewagę. Ten moduł wnosi historię do backtestu:
  surowe punkty (różne osie czasu) → forward-fill kauzalny do osi barów.

KAUZALNOŚĆ (Prawo I — zero look-ahead):
  Każdy bar o timestamp T dostaje OSTATNI znany punkt sentymentu o ts ≤ T.
  Funding publikowany co 8h, OI/LS wg period (np. 1h) — forward-fill bez zaglądania
  w przyszłość. Bar przed pierwszym punktem sentymentu → klucze None (neuron śpi).

OPEN_INTEREST_PREV (Prawo I):
  Liczone z forward-fillowanej serii OI — poprzednia RÓŻNA wartość OI dla dywergencji
  PSY-04. Pierwszy bar z OI → PREV = OI (brak dywergencji).
"""

from __future__ import annotations

import bisect
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


_POLA = ("FUNDING_RATE", "OPEN_INTEREST", "LONG_SHORT_RATIO")


def forward_fill_na_bary(
    bary: List[Dict[str, Any]],
    historia: List[Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    Mapuje historię sentymentu na timestampy barów (forward-fill kauzalny).

    bary:     lista barów z polem 'timestamp' (ms).
    historia: lista rekordów {timestamp, FUNDING_RATE, OPEN_INTEREST, LONG_SHORT_RATIO}
              posortowana rosnąco po timestamp (jak zwraca AdapterFutures.pobierz_historie).

    Zwraca {timestamp_baru: {FUNDING_RATE, OPEN_INTEREST, OPEN_INTEREST_PREV,
            LONG_SHORT_RATIO}} — tylko klucze z dostępną wartością (None pominięte).
    """
    if not historia:
        return {}

    # Osobny forward-fill per pole (różne osie czasu — funding 8h, OI 1h).
    # Prekompute: dla każdego pola lista (ts, wartość) niepustych punktów.
    serie: Dict[str, List[tuple]] = {p: [] for p in _POLA}
    for r in historia:
        ts = int(r["timestamp"])
        for p in _POLA:
            v = r.get(p)
            if v is not None:
                serie[p].append((ts, v))
    serie_ts: Dict[str, List[int]] = {p: [t for t, _ in serie[p]] for p in _POLA}

    wynik: Dict[int, Dict[str, Any]] = {}
    oi_prev_val: Optional[float] = None
    oi_last_val: Optional[float] = None

    for bar in bary:
        ts_bar = bar.get("timestamp")
        if ts_bar is None:
            continue
        ts_bar = int(ts_bar)
        rekord: Dict[str, Any] = {}
        for p in _POLA:
            tsy = serie_ts[p]
            if not tsy:
                continue
            # ostatni punkt o ts <= ts_bar (forward-fill kauzalny)
            idx = bisect.bisect_right(tsy, ts_bar) - 1
            if idx >= 0:
                rekord[p] = serie[p][idx][1]
        # OPEN_INTEREST_PREV — poprzednia RÓŻNA wartość OI (dla dywergencji PSY-04)
        oi = rekord.get("OPEN_INTEREST")
        if oi is not None:
            if oi_last_val is None:
                rekord["OPEN_INTEREST_PREV"] = oi   # pierwszy odczyt: brak dywergencji
            elif oi != oi_last_val:
                # OI się zmienił → poprzednia wartość to ostatnia inna (oi_last_val)
                oi_prev_val = oi_last_val
                rekord["OPEN_INTEREST_PREV"] = oi_prev_val
            else:
                # OI bez zmian (forward-fill tego samego punktu) → PREV = ostatnia różna
                rekord["OPEN_INTEREST_PREV"] = oi_prev_val if oi_prev_val is not None else oi
            oi_last_val = oi
        if rekord:
            wynik[ts_bar] = rekord

    # uzupełnij OPEN_INTEREST_PREV gdy zostało None (pierwszy raz)
    for ts_bar, rek in wynik.items():
        if "OPEN_INTEREST" in rek and rek.get("OPEN_INTEREST_PREV") is None:
            rek["OPEN_INTEREST_PREV"] = rek["OPEN_INTEREST"]

    return wynik


def zapisz_csv(historia: List[Dict[str, Any]], sciezka: str | Path) -> int:
    """Zapisuje historię sentymentu do CSV (cache lokalny). Zwraca liczbę wierszy."""
    sciezka = Path(sciezka)
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    pola = ["timestamp", *_POLA]
    with sciezka.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=pola)
        w.writeheader()
        for r in historia:
            w.writerow({k: r.get(k) for k in pola})
    return len(historia)


def wczytaj_csv(sciezka: str | Path) -> List[Dict[str, Any]]:
    """Wczytuje historię sentymentu z CSV (cache). Puste komórki → None."""
    sciezka = Path(sciezka)
    if not sciezka.exists():
        return []
    out: List[Dict[str, Any]] = []
    with sciezka.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rek: Dict[str, Any] = {"timestamp": int(row["timestamp"])}
            for p in _POLA:
                v = row.get(p)
                rek[p] = float(v) if v not in (None, "", "None") else None
            out.append(rek)
    out.sort(key=lambda r: r["timestamp"])
    return out
