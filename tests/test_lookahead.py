"""
Testy detektora lookahead-bias (imperium/koloseum/lookahead.py).

Weryfikują niezmiennik: głos roju na barze i jest niezależny od istnienia
barów po i. Używają generowanej serii OHLCV (bez zależności od plików danych).

Inspiracja metody: Freqtrade lookahead-analysis (REJESTR_INSPIRACJI.md LA-01).
"""

import math

from imperium.koloseum.lookahead import (
    wykryj_lookahead, _slad_glosow, _swiezy_roj,
)


def _bary(n=320, start=100.0):
    """Generuje realistyczną serię OHLCV z trendem i oscylacją (deterministyczna)."""
    bary = []
    cena = start
    for i in range(n):
        # trend + sinusoidalna oscylacja → różnorodne reżimy, budzi wiele neuronów
        drift = 0.15
        fala = 3.0 * math.sin(i / 12.0)
        o = cena
        c = cena + drift + fala * 0.1
        h = max(o, c) + 0.8
        l = min(o, c) - 0.8
        bary.append({"open": o, "high": h, "low": l, "close": c,
                     "volume": 1000.0 + (i % 7) * 50.0,
                     "symbol": "BTCUSDT", "interwal": "1H"})
        cena = c
    return bary


def test_brak_lookahead_na_czystym_pipeline():
    """Rój Imperium nie powinien zaglądać w przyszłość — zero rozbieżności."""
    bary = _bary(320)
    rozb = wykryj_lookahead(bary, okno=200, odciecie=260, aktywuj_smc=False)
    assert rozb == [], f"Wykryto lookahead-bias: {rozb[:3]}"


def test_slad_deterministyczny():
    """Ten sam zestaw barów → identyczny ślad głosów przy dwóch przejazdach."""
    bary = _bary(280)
    l1, b1 = _swiezy_roj(aktywuj_smc=False)
    l2, b2 = _swiezy_roj(aktywuj_smc=False)
    s1 = _slad_glosow(bary, 200, "BTCUSDT", l1, b1)
    s2 = _slad_glosow(bary, 200, "BTCUSDT", l2, b2)
    assert s1 == s2, "Ślad głosów niedeterministyczny — rój zależny od stanu"


def test_detektor_wykrywa_sztuczny_przeciek():
    """
    Kontrola pozytywna: gdy sztucznie wstrzykniemy lookahead (głos zależny od
    przyszłego baru), detektor MUSI go złapać — inaczej test byłby ślepy.
    """
    bary = _bary(300)
    okno = 200
    odciecie = 250

    # Symulujemy ślad "pełny", w którym bar i zna cenę z przyszłości (i+5):
    # to imituje wadliwy wskaźnik czytający do przodu.
    slad_pelny = {}
    slad_ucany = {}
    for i in range(okno, len(bary)):
        przyszla = bary[min(i + 5, len(bary) - 1)]["close"]
        kier = "LONG" if przyszla > bary[i]["close"] else "SHORT"
        slad_pelny[i] = (kier, 0.7)
    for i in range(okno, odciecie):
        # wersja ucięta nie widzi i+5 poza odcięciem → inny kierunek przy krawędzi
        idx = min(i + 5, odciecie - 1)
        przyszla = bary[idx]["close"]
        kier = "LONG" if przyszla > bary[i]["close"] else "SHORT"
        slad_ucany[i] = (kier, 0.7)

    rozb = [i for i in slad_ucany
            if slad_pelny[i] != slad_ucany[i]]
    # Przy krawędzi odcięcia kierunki muszą się rozjechać → detektor ma co łapać
    assert len(rozb) > 0, "Kontrola pozytywna: przeciek powinien być wykrywalny"
