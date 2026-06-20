"""
W-357 | Triple-Barrier Method + CUSUM Filter (AFML Ch. 3, §3.4 + Ch. 17, §17.2).

DLA NOWICJUSZA: Standardowe etykietowanie "cena wzrosła w następnej świecy = LONG"
ignoruje ścieżkę między barami i bieżącą zmienność. Problem: dla spokojnego rynku
+0.5% to dużo, dla krypto w kryzysie to szum.

Triple-Barrier Method rozwiązuje to przez dynamiczne progi oparte na zmienności:
  ━━━━━━━━ górna bariera: wejście + k·zmienność  (take-profit)
  ─────── lewa bariera: max_hold barów od wejścia (time-out)
  ━━━━━━━━ dolna bariera: wejście − k·zmienność  (stop-loss)

Etykieta = która bariera dotknięta PIERWSZA:
  +1  → górna (dobry trade)
  -1  → dolna (zły trade)
   0  → pionowa, cena wróciła (niejednoznaczny, często filtrowany)

CUSUM Filter (§17.2): sampler zdarzeń — emituj nową obserwację TYLKO gdy
skumulowany odchył ceny przekroczy próg h. Redukuje redundancję próbkowania
(100 barów bocznego rynku → 0-2 zdarzeń CUSUM zamiast 100 szumowych).

Użycie:
    from imperium.legiony.triple_barrier import (
        filtr_cusum, triple_barrier, etykiety_z_barier
    )

    # 1. CUSUM filter → indeksy barów do etykietowania
    zdarzenia_idx = filtr_cusum(close, h=0.01)  # h=1% odchylenie

    # 2. Triple-barrier labeling
    bariery = triple_barrier(
        close, zdarzenia_idx,
        k_tp=2.0, k_sl=1.0,     # take-profit 2σ, stop-loss 1σ
        max_hold=20,              # max 20 barów
        zmiennosc_okno=20,        # zmienność z 20-dniowego okna zwrotów
    )

    # 3. Etykiety gotowe do treningu B-01 / MetaLabeling
    etykiety = etykiety_z_barier(bariery)   # {idx: +1/-1/0}

Źródło: López de Prado, AFML (2018), Ch. 3 §3.4, Ch. 17 §17.2.
  https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


# ─── Zmienność ────────────────────────────────────────────────────────────────

def _zmiennosc_codzienna(close: Sequence[float], okno: int = 20) -> List[float]:
    """
    Codzienna zmienność = std(zwrotów log) z okna `okno` barów.
    Zwraca listę tej samej długości co `close` (pierwsze `okno` barów = NaN → 0.0).
    """
    c = list(close)
    n = len(c)
    out = [0.0] * n
    for i in range(okno, n):
        zwroty = [math.log(c[j] / c[j - 1]) for j in range(i - okno + 1, i + 1) if c[j - 1] > 0]
        if not zwroty:
            continue
        mu = sum(zwroty) / len(zwroty)
        var = sum((r - mu) ** 2 for r in zwroty) / len(zwroty)
        out[i] = math.sqrt(var)
    return out


# ─── CUSUM Filter ─────────────────────────────────────────────────────────────

def filtr_cusum(
    close: Sequence[float],
    h: float = 0.01,
    typ: str = "symetryczny",
) -> List[int]:
    """
    CUSUM Filter (AFML §17.2, Snippet 17.1): sygnalizuje zdarzenie gdy
    skumulowany odchył przekroczy próg h.

    Parametry:
      close — seria cen zamknięcia
      h     — próg w jednostkach ceny (absolutny) lub zwrot (gdy <1 = traktuj jako
              ułamek; automatycznie przeliczany na absolutny względem pierwszej ceny)
      typ   — "symetryczny" (górny + dolny CUSUM), "gorny" (tylko wzrosty), "dolny"

    Zwraca: lista indeksów barów, dla których zdarzenie zostało wyemitowane.
    Użyj ich jako tEvents w triple_barrier().
    """
    c = list(close)
    if not c:
        return []

    # Jeśli h < 1 — traktuj jako zwrot procentowy
    h_abs = h * c[0] if h < 1.0 else h

    zdarzenia: List[int] = []
    s_pos = s_neg = 0.0

    for i in range(1, len(c)):
        if c[i - 1] <= 0:
            continue
        delta = math.log(c[i] / c[i - 1])   # zwrot logarytmiczny
        s_pos = max(0.0, s_pos + delta)
        s_neg = min(0.0, s_neg + delta)

        if typ in ("symetryczny", "gorny") and s_pos >= math.log(1 + h_abs / c[i]):
            zdarzenia.append(i)
            s_pos = 0.0
        elif typ in ("symetryczny", "dolny") and s_neg <= -math.log(1 + h_abs / c[i]):
            zdarzenia.append(i)
            s_neg = 0.0

    return zdarzenia


# ─── Triple-Barrier Method ────────────────────────────────────────────────────

@dataclass
class Bariera:
    """Wynik jednej obserwacji triple-barrier."""
    idx_wejscia: int        # indeks baru wejścia
    cena_wejscia: float
    idx_dotknięcia: Optional[int]   # który bar dotknął barierę (None = na końcu danych)
    etykieta: int           # +1 (TP), -1 (SL), 0 (time-out / niejednoznaczny)
    bariera_gorna: float    # poziom take-profit
    bariera_dolna: float    # poziom stop-loss
    bariera_pionowa: int    # indeks time-out baru
    zysk_pct: float         # procentowy zysk/strata przy dotknięciu


def triple_barrier(
    close: Sequence[float],
    zdarzenia: List[int],
    k_tp: float = 2.0,
    k_sl: float = 1.0,
    max_hold: int = 20,
    zmiennosc_okno: int = 20,
    strona: Optional[int] = None,
) -> List[Bariera]:
    """
    Triple-Barrier Method (AFML Ch. 3, Snippet 3.2).

    Parametry:
      close          — ceny zamknięcia (cały okres)
      zdarzenia      — indeksy barów do etykietowania (np. z filtr_cusum())
      k_tp           — wielokrotność σ dla take-profit (górna bariera)
      k_sl           — wielokrotność σ dla stop-loss (dolna bariera)
      max_hold       — maks. barów do trzymania (pionowa bariera)
      zmiennosc_okno — okno do szacowania σ
      strona         — None (unknown side) lub +1 (LONG only) / -1 (SHORT only)
                       gdy podane: tylko jedna z barier poziomych jest aktywna

    Zwraca listę Bariera — jedna na każde zdarzenie wejścia.
    """
    c = list(close)
    n = len(c)
    zmiennosc = _zmiennosc_codzienna(c, zmiennosc_okno)
    wynik: List[Bariera] = []

    for idx in zdarzenia:
        if idx >= n:
            continue
        p0 = c[idx]
        sigma = zmiennosc[idx] if zmiennosc[idx] > 0 else 0.01  # fallback 1%

        tp = p0 * (1 + k_tp * sigma)   # górna bariera
        sl = p0 * (1 - k_sl * sigma)   # dolna bariera
        t1 = min(idx + max_hold, n - 1)  # pionowa bariera

        # Jeśli znamy stronę — jedna bariera nieaktywna
        tp_aktywne = (strona is None or strona == 1)
        sl_aktywne = (strona is None or strona == -1)

        etykieta = 0
        idx_dot: Optional[int] = None
        zysk = 0.0

        for j in range(idx + 1, t1 + 1):
            cj = c[j]
            if tp_aktywne and cj >= tp:
                etykieta = 1
                idx_dot = j
                zysk = (cj - p0) / p0
                break
            if sl_aktywne and cj <= sl:
                etykieta = -1
                idx_dot = j
                zysk = (cj - p0) / p0
                break
        else:
            # Pionowa bariera (time-out)
            etykieta = 0
            idx_dot = t1
            zysk = (c[t1] - p0) / p0 if p0 > 0 else 0.0

        wynik.append(Bariera(
            idx_wejscia=idx,
            cena_wejscia=round(p0, 6),
            idx_dotknięcia=idx_dot,
            etykieta=etykieta,
            bariera_gorna=round(tp, 6),
            bariera_dolna=round(sl, 6),
            bariera_pionowa=t1,
            zysk_pct=round(zysk * 100, 4),
        ))

    return wynik


def etykiety_z_barier(bariery: List[Bariera]) -> Dict[int, int]:
    """Konwertuje listę Bariera na dict {idx_wejscia: etykieta}."""
    return {b.idx_wejscia: b.etykieta for b in bariery}


# ─── Statystyki triple-barrier ────────────────────────────────────────────────

def statystyki_barier(bariery: List[Bariera]) -> Dict[str, float]:
    """Rozkład etykiet i zyski dla zestawu barier."""
    if not bariery:
        return {}
    tp_n = sum(1 for b in bariery if b.etykieta == 1)
    sl_n = sum(1 for b in bariery if b.etykieta == -1)
    to_n = sum(1 for b in bariery if b.etykieta == 0)
    n = len(bariery)
    zyski = [b.zysk_pct for b in bariery]
    avg_zysk = sum(zyski) / len(zyski) if zyski else 0.0
    return {
        "n": n,
        "tp_pct": round(tp_n / n * 100, 1),
        "sl_pct": round(sl_n / n * 100, 1),
        "timeout_pct": round(to_n / n * 100, 1),
        "avg_zysk_pct": round(avg_zysk, 3),
    }


# ─── Sample Uniqueness (AFML Ch. 4, §4.2) ────────────────────────────────────

def sample_uniqueness(
    bariery: List[Bariera],
    n_close: int,
) -> List[float]:
    """
    Oblicza average uniqueness każdej etykiety (AFML §4.2, Snippet 4.1).

    Obserwacje z nakładającymi się okienkami etykiet NIE są IID.
    Uniqueness(t) = 1 / (liczba innych etykiet aktywnych w tym samym czasie).
    Waga próbki = jej average uniqueness w oknie etykiety.

    Użycie: wagi do trenowania MetaLabelingScorer / ML modelu.

    Zwraca: List[float] tej samej długości co bariery — wagi [0,1].
    """
    if not bariery:
        return []

    # Współbieżność: ile etykiet jest aktywnych w barze t
    concurrency = [0.0] * n_close
    for b in bariery:
        t0 = b.idx_wejscia
        t1 = b.idx_dotknięcia if b.idx_dotknięcia is not None else b.bariera_pionowa
        for t in range(t0, min(t1 + 1, n_close)):
            concurrency[t] += 1.0

    # Uniqueness per próbka = średnia 1/concurrency w jej oknie
    wagi: List[float] = []
    for b in bariery:
        t0 = b.idx_wejscia
        t1 = b.idx_dotknięcia if b.idx_dotknięcia is not None else b.bariera_pionowa
        uniq_vals = [
            1.0 / concurrency[t]
            for t in range(t0, min(t1 + 1, n_close))
            if concurrency[t] > 0
        ]
        avg_uniq = sum(uniq_vals) / len(uniq_vals) if uniq_vals else 1.0
        wagi.append(round(avg_uniq, 4))

    return wagi
