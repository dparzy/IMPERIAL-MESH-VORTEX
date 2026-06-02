"""
🧪 Testy frameworku adapterów danych (most API → rój).

Weryfikują model Cezara "wersja testowa teraz → łatwe auto-wybudzenie później":
  1. adapter dolewa klucze API do dict (wzbogac)
  2. adapter budzi neurony swojej domeny (aktywuj → DOSTEPNY=True)
  3. obudzony neuron interpretuje świeże dane (kierunek zgodny ze scenariuszem)
  4. usypiaj() przywraca stan (DOSTEPNY=False) — by NIE zafałszować audytu

KRYTYCZNE: każdy test budzący neurony przywraca stan w `finally`.
Inaczej statyczny audyt (test_spojnosc) policzyłby inną liczbę wyciszonych.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.akwedukty.adaptery import (
    AdapterDanych, AdapterTestowyOnChain, AdapterTestowyFutures, AdapterTestowyCVD,
)


# ── Framework: wzbogacanie dict ───────────────────────────────────────────────

def test_adapter_wzbogac_dodaje_klucze():
    """wzbogac() dolewa klucze API do dict (jak EXP-05.wstrzyknij)."""
    ad = AdapterTestowyOnChain("kapitulacja")
    w = {"CLOSE": 100.0}
    ad.wzbogac(w, "BTCUSDT")
    assert w["CLOSE"] == 100.0           # nie nadpisuje istniejących
    assert "MVRV_Z_SCORE" in w
    assert w["MVRV_Z_SCORE"] == -0.8


def test_adapter_wzbogac_pomija_none():
    """Wartości None nie trafiają do dict (nie psują istniejących danych)."""
    class PustyAdapter(AdapterDanych):
        NAZWA = "pusty"
        def pobierz(self, symbol):
            return {"A": None, "B": 5}
    w = {}
    PustyAdapter().wzbogac(w, "X")
    assert "A" not in w
    assert w["B"] == 5


def test_adapter_baza_pobierz_wymaga_implementacji():
    """Bazowy pobierz() rzuca NotImplementedError (kontrakt podklas)."""
    try:
        AdapterDanych().pobierz("X")
        assert False, "Powinien rzucić NotImplementedError"
    except NotImplementedError:
        pass


# ── On-Chain (OC-01..04) ──────────────────────────────────────────────────────

def test_onchain_aktywuj_i_usypiaj():
    """aktywuj() budzi OC, usypiaj() przywraca — stan czysty po teście."""
    from imperium.legiony.neurony.onchain import NeuronMVRV
    ad = AdapterTestowyOnChain("kapitulacja")
    assert NeuronMVRV.DOSTEPNY is False          # stan wyjściowy
    try:
        obudzone = ad.aktywuj()
        assert set(obudzone) == {"OC-01", "OC-02", "OC-03", "OC-04"}
        assert NeuronMVRV.DOSTEPNY is True
        assert NeuronMVRV.POWOD_NIEDOSTEPNOSCI == ""
    finally:
        uspione = ad.usypiaj()
        assert set(uspione) == {"OC-01", "OC-02", "OC-03", "OC-04"}
        assert NeuronMVRV.DOSTEPNY is False
        assert NeuronMVRV.POWOD_NIEDOSTEPNOSCI != ""


def test_onchain_kapitulacja_long():
    """Scenariusz kapitulacji → wszystkie 4 OC głosują LONG (dno cyklu)."""
    from imperium.legiony.neurony.onchain import (
        NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
    )
    ad = AdapterTestowyOnChain("kapitulacja")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    for klasa in (NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow):
        s = klasa().interpretuj(w)
        assert s.kierunek == "LONG", f"{klasa.KLUCZ} powinien LONG w kapitulacji, jest {s.kierunek}"


def test_onchain_euforia_short():
    """Scenariusz euforii → wszystkie 4 OC głosują SHORT (szczyt bańki)."""
    from imperium.legiony.neurony.onchain import (
        NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
    )
    ad = AdapterTestowyOnChain("euforia")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    for klasa in (NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow):
        s = klasa().interpretuj(w)
        assert s.kierunek == "SHORT", f"{klasa.KLUCZ} powinien SHORT w euforii, jest {s.kierunek}"


# ── Futures / sentyment (PSY-01..04) ──────────────────────────────────────────

def test_futures_aktywuj_i_usypiaj():
    """aktywuj()/usypiaj() dla domeny PSY — stan czysty po teście."""
    from imperium.legiony.neurony.psychologia import NeuronFearGreed
    ad = AdapterTestowyFutures("panika")
    assert NeuronFearGreed.DOSTEPNY is False
    try:
        obudzone = ad.aktywuj()
        assert set(obudzone) == {"PSY-01", "PSY-02", "PSY-03", "PSY-04"}
        assert NeuronFearGreed.DOSTEPNY is True
    finally:
        ad.usypiaj()
        assert NeuronFearGreed.DOSTEPNY is False


def test_futures_panika_long():
    """Panika (strach, crowded short) → Funding/Panika/FearGreed kontrariańsko LONG."""
    from imperium.legiony.neurony.psychologia import (
        NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed,
    )
    ad = AdapterTestowyFutures("panika")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    for klasa in (NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed):
        s = klasa().interpretuj(w)
        assert s.kierunek == "LONG", f"{klasa.KLUCZ} powinien LONG w panice, jest {s.kierunek}"


def test_futures_chciwosc_short():
    """Chciwość (euforia, crowded long) → Funding/Panika/FearGreed kontrariańsko SHORT."""
    from imperium.legiony.neurony.psychologia import (
        NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed,
    )
    ad = AdapterTestowyFutures("chciwosc")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    for klasa in (NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed):
        s = klasa().interpretuj(w)
        assert s.kierunek == "SHORT", f"{klasa.KLUCZ} powinien SHORT w chciwości, jest {s.kierunek}"


# ── CVD (V-03) ────────────────────────────────────────────────────────────────

def test_cvd_aktywuj_i_usypiaj():
    """aktywuj()/usypiaj() dla V-03 CVD — stan czysty po teście."""
    from imperium.legiony.neurony.wolumen import NeuronCVD
    ad = AdapterTestowyCVD("akumulacja")
    assert NeuronCVD.DOSTEPNY is False
    try:
        assert ad.aktywuj() == ["V-03"]
        assert NeuronCVD.DOSTEPNY is True
    finally:
        ad.usypiaj()
        assert NeuronCVD.DOSTEPNY is False


def test_cvd_akumulacja_long():
    """CVD dodatni (kupujący agresorzy) → LONG."""
    from imperium.legiony.neurony.wolumen import NeuronCVD
    ad = AdapterTestowyCVD("akumulacja")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    assert NeuronCVD().interpretuj(w).kierunek == "LONG"


def test_cvd_dystrybucja_short():
    """CVD ujemny (sprzedający agresorzy) → SHORT."""
    from imperium.legiony.neurony.wolumen import NeuronCVD
    ad = AdapterTestowyCVD("dystrybucja")
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    assert NeuronCVD().interpretuj(w).kierunek == "SHORT"


# ── Gwarancja czystego stanu globalnego ───────────────────────────────────────

def test_stan_globalny_przywrocony():
    """Po wszystkich testach 9 neuronów API musi być z powrotem wyciszonych."""
    from imperium.legiony.neurony.onchain import (
        NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
    )
    from imperium.legiony.neurony.psychologia import (
        NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv,
    )
    from imperium.legiony.neurony.wolumen import NeuronCVD
    api_neurony = [NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
                   NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv,
                   NeuronCVD]
    for klasa in api_neurony:
        assert klasa.DOSTEPNY is False, f"{klasa.KLUCZ} pozostał obudzony — zafałszuje audyt!"
