"""Testy walidatora zmysłów (narzedzia/waliduj_zmysly.py) — Prawo XV.

Offline i deterministycznie: tryb --bez-sieci nie dotyka API, a logikę różnicy
BAZA↔ZMYSŁY sprawdzamy wstrzykniętym sztucznym adapterem (bez sieci w CI).
"""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia import waliduj_zmysly as wz


class _FakeAdapterFunding:
    """Sztuczny adapter — wstrzykuje ekstremalny funding (odblokowuje PSY-01 SHORT)."""
    NAZWA = "FakeFunding"

    def wzbogac(self, wskazniki: dict, symbol: str = "") -> dict:
        wskazniki["FUNDING_RATE"] = 0.0015   # ≥0.001 → PSY-01 SHORT (próg zmierzony)
        return wskazniki


def test_bez_sieci_nie_dodaje_adapterow():
    """--bez-sieci: zero adapterów, ZMYSŁY == BAZA (nic nie dolane)."""
    r = wz.waliduj(bez_sieci=True)
    assert r["zywe_adaptery"] == []
    assert r["martwe_adaptery"] == []
    assert r["aktywne_zmysly"] == r["aktywne_baza"]   # brak zmysłów = brak odblokowań
    assert r["odblokowane"] == []


def test_onchain_zawsze_w_detalach():
    """On-chain (realny timestamp) raportowany nawet bez sieci — nie znika."""
    r = wz.waliduj(bez_sieci=True)
    klucze = {d[0] for d in r["detale"]}
    assert {"OC-06", "OC-07", "OC-08"} <= klucze
    # KAŻDY neuron sensoryczny musi się pojawić w raporcie (głos, cisza albo pominięty)
    assert wz.KLUCZE_SENSORYCZNE <= klucze


def test_onchain_glosuje_na_realnej_dacie():
    """OC-06 (S2F po halvingu) daje realny głos na dzisiejszej dacie — nie martwy."""
    r = wz.waliduj(bez_sieci=True)
    oc06 = next(d for d in r["detale"] if d[0] == "OC-06")
    # kierunek (indeks 2) i powód (indeks 4) — S2F liczony z realnego block height
    assert oc06[2] in ("LONG", "SHORT", "NEUTRAL")
    assert oc06[4]                                    # niepusty powód (neuron przemówił)


def test_wstrzykniety_adapter_odblokowuje_neuron(monkeypatch):
    """Sztuczny adapter z ekstremalnym fundingiem → PSY-01 w 'odblokowane' (logika różnicy)."""
    monkeypatch.setattr(wz, "_zbuduj_adaptery", lambda bez_sieci: [_FakeAdapterFunding()])
    r = wz.waliduj(bez_sieci=False)
    assert ("FakeFunding", ["FUNDING_RATE"]) in r["zywe_adaptery"]
    assert "PSY-01" in r["odblokowane"]               # był NEUTRAL w bazie, głosuje ze zmysłem
    assert r["aktywne_zmysly"] > r["aktywne_baza"]


def test_padniety_adapter_nie_wywala(monkeypatch):
    """Adapter, który rzuca wyjątek, ląduje w martwych — walidacja nie pada (offline-safe)."""
    class _Pada:
        NAZWA = "Pada"
        def wzbogac(self, wskazniki, symbol=""):
            raise RuntimeError("brak sieci")

    monkeypatch.setattr(wz, "_zbuduj_adaptery", lambda bez_sieci: [_Pada()])
    r = wz.waliduj(bez_sieci=False)
    assert any(n == "Pada" for n, _ in r["martwe_adaptery"])
    assert r["odblokowane"] == []                      # padnięty adapter nic nie odblokował


def test_main_zwraca_zero():
    """CLI --bez-sieci: raport diagnostyczny zawsze exit 0, drukuje sekcje."""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = wz.main(["--bez-sieci"])
    assert rc == 0
    out = buf.getvalue()
    assert "WALIDACJA ZMYSŁÓW" in out
    assert "Neurony sensoryczne" in out
