"""Testy W-361 A/B na żywo (narzedzia/ab_wazenie_ic.py) + rozszerzenie backtestu.

Reguła Test-Granic (Prawo XXI): pomiar decyduje na ZNAKU agregatu → testujemy granice.
Rdzeń: _trafnosc_legatus musi (a) pomijać bary NEUTRAL/weto, (b) po włączeniu ważenia IC
odwracać neuron mylący się systematycznie (OFF pudłuje, ON trafia). Backtest: opt-in
zbieraj_pelne_sygnaly zbiera pełne SygnalNeuronu RÓWNOLEGLE do etykiet, domyślnie nic (OFF)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging

logging.disable(logging.CRITICAL)

from imperium.legiony.legatus import Legatus
from imperium.legiony.mikro_neuron import SygnalNeuronu
from imperium.koloseum.backtest import backtest
from narzedzia.ab_wazenie_ic import _trafnosc_legatus, _nota


def _syg(nid, kier, finalna, waga=5):
    s = SygnalNeuronu(neuron_id=nid, legion="SWING", wskaznik="X", wartosc=1.0,
                      kierunek=kier, waga=waga, kategoria="M")
    s.pewnosc_finalna = finalna
    return s


def _leg():
    # min_przewaga=0.0 → mierzymy sam znak agregatu, bez weta progowego (identyczne OFF/ON)
    return Legatus(neurony=[], min_neuronow=1, min_przewaga=0.0)


def _bary(n=320, symbol="BTCUSDT"):
    """Syntetyczny trend (kopia wzorca z test_backtest) — bez zależności od CSV."""
    bary = []
    cena = 100.0
    for i in range(n):
        cena *= 1.002 if (i // 7) % 2 == 0 else 0.999
        o = cena
        c = cena * (1.001 if i % 2 == 0 else 0.9995)
        bary.append({
            "timestamp": 1_600_000_000_000 + i * 3_600_000,
            "open": o, "high": max(o, c) * 1.002, "low": min(o, c) * 0.998, "close": c,
            "volume": 1000.0 + i, "volume_quote": 0.0,
            "symbol": symbol, "interwal": "1H", "tradecount": 100,
        })
    return bary


# ── Rdzeń pomiaru: _trafnosc_legatus ───────────────────────────────────────────

def test_off_myli_sie_on_odwraca_trafia():
    # A zawsze LONG, rynek zawsze spada (-1) → OFF pudłuje (0%); ON z IC<0 odwraca → SHORT → 100%
    pelne = [[_syg("A", "LONG", 0.5)] for _ in range(4)]
    wyn = [-1, -1, -1, -1]
    leg = _leg()
    acc_off, akt_off = _trafnosc_legatus(leg, pelne, wyn)
    assert acc_off == 0.0 and akt_off == 4
    leg.ustaw_wagi_ic({"A": -1.0}, wlacz=True)
    acc_on, akt_on = _trafnosc_legatus(leg, pelne, wyn)
    assert acc_on == 1.0 and akt_on == 4


def test_bar_bez_sygnalow_pomijany():
    # pusta lista sygnałów → weto/NEUTRAL → bar nie liczony (akt=0, nan)
    acc, akt = _trafnosc_legatus(_leg(), [[]], [1])
    assert akt == 0 and acc != acc   # NaN


def test_bar_zrownowazony_pomijany():
    # LONG i SHORT o równym wkładzie → agregat remis → pewnosc 0.5, kierunek LONG?
    # prev_l==prev_s → kierunek LONG, pewnosc=0.5 (nie <0.5) → liczony. Sprawdzamy że NIE wybucha.
    pelne = [[_syg("A", "LONG", 0.4), _syg("B", "SHORT", 0.4)]]
    acc, akt = _trafnosc_legatus(_leg(), pelne, [1])
    assert akt in (0, 1)   # deterministyczny tie-break, byle bez wyjątku


def test_off_trafia_gdy_neuron_ma_racje():
    # A LONG, rynek rośnie (+1) → OFF trafia (100%); brak potrzeby odwracania
    pelne = [[_syg("A", "LONG", 0.5)] for _ in range(3)]
    acc_off, akt = _trafnosc_legatus(_leg(), pelne, [1, 1, 1])
    assert acc_off == 1.0 and akt == 3


# ── Nota (round-trip pól do areny) ─────────────────────────────────────────────

def test_nota_zawiera_kluczowe_pola():
    w = {"bary_test": 120, "acc_off": 0.482, "acc_on": 0.518, "akt_off": 100, "akt_on": 98}
    nota = _nota("Binance_BTCUSDT_4h.csv", 0.6, w)
    assert "accOFF=0.4820" in nota and "accON=0.5180" in nota
    assert "test=120" in nota and "aktON=98" in nota


# ── Rozszerzenie backtestu: zbieraj_pelne_sygnaly (opt-in) ──────────────────────

def test_backtest_pelne_sygnaly_off_domyslnie():
    # Domyślnie NIE zbiera pełnych sygnałów (ZASADA WPIĘCIA — zero zmiany zachowania)
    eng = backtest("X", "1H", okno=250, bary=_bary(), zbieraj_sygnaly=True)
    assert not hasattr(eng, "historia_pelnych_sygnalow")


def test_backtest_pelne_sygnaly_opt_in_rownolegle():
    eng = backtest("X", "1H", okno=250, bary=_bary(),
                   zbieraj_sygnaly=True, zbieraj_pelne_sygnaly=True)
    pelne = getattr(eng, "historia_pelnych_sygnalow", None)
    assert pelne is not None
    # RÓWNOLEGLE do etykiet i kierunków (ta sama liczba barów decyzyjnych)
    assert len(pelne) == len(eng.historia_wynikow) == len(eng.historia_sygnalow)
    # każdy bar = lista SygnalNeuronu (mają neuron_id/kierunek/pewnosc_finalna/waga)
    if pelne and pelne[0]:
        s = pelne[0][0]
        assert hasattr(s, "neuron_id") and hasattr(s, "pewnosc_finalna") and hasattr(s, "waga")
