"""Testy PSY-05 DVOL — neuron (granice kontrariańskie) + AdapterDVOL (offline).
Prawo XXI + Reguła Test-Granic: progi 80/60/45/30, None, kierunek kontrariański."""
from imperium.legiony.neurony.psychologia import NeuronDVOL
from imperium.akwedukty.adaptery.dvol import AdapterDVOL


# ── Neuron: granice progów (kontrariański — wysoki strach → LONG) ──────────────
def test_dvol_brak_danych_neutral():
    s = NeuronDVOL().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0


def test_dvol_ekstremalny_strach_long():
    s = NeuronDVOL().interpretuj({"DVOL_INDEX": 90})
    assert s.kierunek == "LONG" and s.pewnosc == 0.85


def test_dvol_prog_80_dokladnie_long():
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 80}).kierunek == "LONG"
    # tuż poniżej 80 → słabszy LONG (60-79), nie ekstremalny
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 79}).pewnosc == 0.60


def test_dvol_prog_45_granica():
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 45}).kierunek == "LONG"   # ==45 → LONG
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 44}).kierunek == "NEUTRAL"  # 31-44 neutral


def test_dvol_samozadowolenie_short():
    # niski DVOL (<=30) → słaby SHORT (kontrariański: brak strachu = ryzyko)
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 30}).kierunek == "SHORT"
    assert NeuronDVOL().interpretuj({"DVOL_INDEX": 31}).kierunek == "NEUTRAL"  # tuż powyżej


def test_dvol_kategoria_i_klucz():
    n = NeuronDVOL()
    assert n.KLUCZ == "PSY-05" and n.KATEGORIA == "R" and n.WSKAZNIK == "DVOL"


# ── Adapter: offline (wstrzyknięty fetcher — bez sieci) ────────────────────────
_PROBKA = ('{"result":{"data":[[1700000000000,40.0,41.0,39.0,42.5],'
           '[1700003600000,42.0,43.0,41.5,43.1]]}}')


def test_adapter_parsuje_ostatni_close():
    a = AdapterDVOL(fetcher=lambda waluta: _PROBKA)
    assert a.pobierz("BTCUSDT") == {"DVOL_INDEX": 43.1}   # ostatni close


def test_adapter_pusta_odpowiedz_none():
    a = AdapterDVOL(fetcher=lambda waluta: '{"result":{"data":[]}}')
    assert a.pobierz("BTCUSDT") == {"DVOL_INDEX": None}


def test_adapter_uszkodzone_none():
    a = AdapterDVOL(fetcher=lambda waluta: "nie-json")
    assert a.pobierz("BTCUSDT") == {"DVOL_INDEX": None}


def test_adapter_waluta_z_symbolu():
    a = AdapterDVOL()
    assert a._waluta("ETHUSDT") == "ETH" and a._waluta("BTCUSDT") == "BTC"
