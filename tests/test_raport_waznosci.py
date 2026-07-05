"""Testy raportu ważności (narzedzia/raport_waznosci.py) + kolektor sygnałów backtestu."""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest


def _bary(n: int = 320, symbol: str = "BTCUSDT") -> list:
    bary = []
    cena = 100.0
    for i in range(n):
        cena *= 1.002 if (i // 7) % 2 == 0 else 0.999
        o = cena
        c = cena * (1.001 if i % 2 == 0 else 0.9995)
        bary.append({
            "timestamp": 1_600_000_000_000 + i * 3_600_000,
            "open": o, "high": max(o, c) * 1.002, "low": min(o, c) * 0.998,
            "close": c, "volume": 1000.0 + i, "volume_quote": 0.0,
            "symbol": symbol, "interwal": "1H", "tradecount": 100,
        })
    return bary


def test_zbieraj_sygnaly_wyrownane_dlugosci():
    eng = backtest("X", "1H", okno=250, bary=_bary(), zbieraj_sygnaly=True)
    syg = getattr(eng, "historia_sygnalow", None)
    wyn = getattr(eng, "historia_wynikow", None)
    assert syg is not None and wyn is not None
    assert len(syg) == len(wyn)                  # etykieta forward sparowana z sygnałem
    assert all(v in (1, -1) for v in wyn)        # znak zwrotu następnego baru


def test_zbieraj_sygnaly_domyslnie_off():
    eng = backtest("X", "1H", okno=250, bary=_bary())
    assert not hasattr(eng, "historia_sygnalow")   # opt-in: bez flagi brak kolekcji


def test_raport_za_malo_obserwacji():
    from narzedzia.raport_waznosci import raport
    # pusty glob → 0 par → komunikat o zbyt małej próbie (nie wybuch)
    out = raport([], "4h")
    assert "za mało" in out.lower() or "RAPORT WAŻNOŚCI" in out


def test_do_areny_zapisuje_mda(tmp_path, monkeypatch):
    """--do-areny zapisuje MDA per neuron do bazy (na sztucznym raporcie)."""
    import narzedzia.raport_waznosci as rw
    from imperium.legiony.feature_importance import RaportWaznosci, WaznoscNeuronu

    fake = RaportWaznosci(
        n_obserwacji=100, base_accuracy=0.5,
        rankowanie=[WaznoscNeuronu("A-01", mda=0.05, sfi_long=0.55, sfi_short=0.57,
                                   sfi_overall=0.6, n_long=30, n_short=20, n_neutral=5),
                    WaznoscNeuronu("B-02", mda=-0.01, sfi_long=0.45, sfi_short=0.42,
                                   sfi_overall=0.4, n_long=10, n_short=12, n_neutral=3,
                                   pominiety=True)],
        martwe_glosy=[], redundantne=[], podsumowanie="x")
    monkeypatch.setattr(rw, "zbierz_sygnaly", lambda *a, **k: ([{}] * 100, [1] * 100, 3))
    from imperium.legiony import feature_importance as fi
    monkeypatch.setattr(fi, "raport_waznosci", lambda *a, **k: fake)

    zapisane = {}
    from imperium.biblioteki import arena_baza
    def _spy(wiersze, *a, **k):
        zapisane["w"] = list(wiersze)
        return len(zapisane["w"])
    monkeypatch.setattr(arena_baza, "zapisz_pomiary", _spy)

    out = rw.raport(["x"], "4h", do_areny=True)
    # pominięty B-02 nie trafia; A-01 tak; rodzaj WAZNOSC
    assert [w[1] for w in zapisane["w"]] == ["A-01"]
    assert zapisane["w"][0][0] == "WAZNOSC" and "Zapisano" in out
