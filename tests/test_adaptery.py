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
    AdapterFearGreed, AdapterFutures,
)


def _fetcher_futures(funding="0.00010000", long_acc="0.50", oi="1500000.0"):
    """Buduje wstrzykiwany fetcher(url)->JSON dla AdapterFutures (offline)."""
    def fetch(url: str) -> str:
        if "premiumIndex" in url:
            return '{"symbol":"BTCUSDT","lastFundingRate":"%s","markPrice":"40000"}' % funding
        if "globalLongShortAccountRatio" in url:
            return '[{"symbol":"BTCUSDT","longAccount":"%s","shortAccount":"0.50","longShortRatio":"1.0"}]' % long_acc
        if "openInterest" in url:
            return '{"symbol":"BTCUSDT","openInterest":"%s","time":1718000000}' % oi
        return "{}"
    return fetch

# Próbka prawdziwej odpowiedzi alternative.me (format zweryfikowany z dokumentacji API)
_FNG_JSON = (
    '{"name":"Fear and Greed Index",'
    '"data":[{"value":"%s","value_classification":"%s",'
    '"timestamp":"1718000000","time_until_update":"3600"}],'
    '"metadata":{"error":null}}'
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

def test_futures_psy_aktywne_faza_b():
    """Faza B: PSY-01/02/04 aktywne domyślnie (realny AdapterFutures publiczny)."""
    from imperium.legiony.neurony.psychologia import (
        NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv,
    )
    # PSY obudzone w Fazie B — kategoria R głosuje (nie martwy głos)
    assert NeuronFundingExtreme.DOSTEPNY is True
    assert NeuronPanikaDetal.DOSTEPNY is True
    assert NeuronOIDiv.DOSTEPNY is True
    # Mock futures wciąż dostarcza dane przez wzbogac()
    ad = AdapterTestowyFutures("panika")
    assert set(ad.neurony_obslugiwane()) >= {"PSY-01", "PSY-02", "PSY-04"}


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


# ── AdapterFutures REALNY (Binance public, fetcher wstrzyknięty — offline) ────

def test_futures_real_dolewa_klucze():
    """AdapterFutures.wzbogac dolewa FUNDING_RATE/LONG_SHORT_RATIO/OPEN_INTEREST."""
    ad = AdapterFutures(fetcher=_fetcher_futures(funding="0.00250000", long_acc="0.82", oi="1600000"))
    w = {"CLOSE": 40000.0}
    ad.wzbogac(w, "BTCUSDT")
    assert abs(w["FUNDING_RATE"] - 0.0025) < 1e-9
    assert abs(w["LONG_SHORT_RATIO"] - 0.82) < 1e-9
    assert w["OPEN_INTEREST"] == 1600000.0


def test_futures_real_funding_extreme_short():
    """Wysoki funding (crowded long) → PSY-01 kontrariański SHORT."""
    from imperium.legiony.neurony.psychologia import NeuronFundingExtreme
    ad = AdapterFutures(fetcher=_fetcher_futures(funding="0.00250000"))
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    assert NeuronFundingExtreme().interpretuj(w).kierunek == "SHORT"


def test_futures_real_oi_prev_pamiec():
    """OPEN_INTEREST_PREV: pierwszy odczyt = OI (brak dywergencji), drugi pamięta poprzedni."""
    ad = AdapterFutures(fetcher=_fetcher_futures(oi="1500000"))
    w1 = {}
    ad.wzbogac(w1, "BTCUSDT")
    assert w1["OPEN_INTEREST"] == w1["OPEN_INTEREST_PREV"]  # pierwszy = brak dywergencji
    ad._fetcher = _fetcher_futures(oi="1600000")
    w2 = {}
    ad.wzbogac(w2, "BTCUSDT")
    assert w2["OPEN_INTEREST"] == 1600000.0
    assert w2["OPEN_INTEREST_PREV"] == 1500000.0  # pamięta poprzedni odczyt


def test_futures_real_padniety_fetcher_bezpieczny():
    """Fetcher rzucający wyjątek → dict bez zmian (Prawo XV: neuron abstynuje)."""
    def zly(url):
        raise RuntimeError("brak sieci")
    ad = AdapterFutures(fetcher=zly)
    w = {"CLOSE": 100.0}
    ad.wzbogac(w, "BTCUSDT")
    assert w.get("FUNDING_RATE") is None
    assert "CLOSE" in w  # nietknięte


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


# ── AdapterFearGreed (PSY-03) — pierwszy prawdziwy adapter API ────────────────

def test_feargreed_parsuje_realny_json():
    """Parsuje prawdziwy format alternative.me → FEAR_GREED_INDEX jako float."""
    ad = AdapterFearGreed(fetcher=lambda: _FNG_JSON % ("40", "Fear"))
    dane = ad.pobierz("BTCUSDT")
    assert dane["FEAR_GREED_INDEX"] == 40.0


def test_feargreed_pusta_data_zwraca_none():
    """Pusta sekcja 'data' → None (graceful, neuron śpi dalej, nie martwy głos)."""
    ad = AdapterFearGreed(fetcher=lambda: '{"name":"x","data":[],"metadata":{}}')
    assert ad.pobierz("X")["FEAR_GREED_INDEX"] is None


def test_feargreed_uszkodzony_json_nie_psuje_dict():
    """Uszkodzony JSON → wzbogac() łapie błąd, dict bez zmian (Prawo XV)."""
    def zly_fetcher():
        return "to nie jest json {{{"
    ad = AdapterFearGreed(fetcher=zly_fetcher)
    w = {"CLOSE": 100.0}
    ad.wzbogac(w, "X")                 # nie rzuca — baza łapie wyjątek
    assert w == {"CLOSE": 100.0}       # dict nietknięty
    assert "FEAR_GREED_INDEX" not in w


def test_feargreed_psy03_aktywny():
    """Faza B: PSY-03 aktywny domyślnie (AdapterFearGreed alternative.me, bez klucza)."""
    from imperium.legiony.neurony.psychologia import NeuronFearGreed
    assert NeuronFearGreed.DOSTEPNY is True
    ad = AdapterFearGreed(fetcher=lambda: _FNG_JSON % ("40", "Fear"))
    assert ad.neurony_obslugiwane() == ["PSY-03"]
    # aktywuj() idempotentne — stan pozostaje aktywny
    assert ad.aktywuj() == ["PSY-03"]
    assert NeuronFearGreed.DOSTEPNY is True


def test_feargreed_strach_long():
    """Ekstremalny strach (12) → wzbogac + PSY-03 → kontrariański LONG."""
    from imperium.legiony.neurony.psychologia import NeuronFearGreed
    ad = AdapterFearGreed(fetcher=lambda: _FNG_JSON % ("12", "Extreme Fear"))
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    assert w["FEAR_GREED_INDEX"] == 12.0
    assert NeuronFearGreed().interpretuj(w).kierunek == "LONG"


def test_feargreed_chciwosc_short():
    """Ekstremalna chciwość (88) → kontrariański SHORT."""
    from imperium.legiony.neurony.psychologia import NeuronFearGreed
    ad = AdapterFearGreed(fetcher=lambda: _FNG_JSON % ("88", "Extreme Greed"))
    w = {}
    ad.wzbogac(w, "BTCUSDT")
    assert NeuronFearGreed().interpretuj(w).kierunek == "SHORT"


# ── Gwarancja czystego stanu globalnego ───────────────────────────────────────

def test_stan_globalny_przywrocony():
    """Po testach: OC (4) + CVD (1) wyciszone; PSY (4) aktywne (Faza B)."""
    from imperium.legiony.neurony.onchain import (
        NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
    )
    from imperium.legiony.neurony.psychologia import (
        NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv,
    )
    from imperium.legiony.neurony.wolumen import NeuronCVD
    wyciszone = [NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
                 NeuronCVD]
    for klasa in wyciszone:
        assert klasa.DOSTEPNY is False, f"{klasa.KLUCZ} pozostał obudzony — zafałszuje audyt!"
    aktywne_psy = [NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv]
    for klasa in aktywne_psy:
        assert klasa.DOSTEPNY is True, f"{klasa.KLUCZ} powinien być aktywny (Faza B)"
