"""Testy klasyfikatora zdarzeń + NEWS-02 (taksonomia, kierunek per typ)."""

from imperium.akwedukty.klasyfikator_zdarzen import klasyfikuj
from imperium.legiony.neurony.zdarzenia import NeuronTaksonomiaZdarzen


def test_hack_ujemny():
    r = klasyfikuj(["Major exchange hack drains millions"])
    assert r["typ"] == "HACK"
    assert r["kierunek"] < 0


def test_etf_dodatni():
    r = klasyfikuj(["Bitcoin ETF approval granted by regulator"])
    assert r["typ"] == "ETF_APPROVAL"
    assert r["kierunek"] > 0


def test_rumor_kontrariański_ujemny():
    """KLUCZOWE (arXiv:2508.07408): rumor/spekulacja = kierunek UJEMNY (fade hype)."""
    r = klasyfikuj(["Solana could reportedly launch new product, speculation grows"])
    assert r["typ"] == "RUMOR"
    assert r["kierunek"] < 0          # mimo 'pozytywnego' brzmienia — kontrariański


def test_upadek_silnie_ujemny():
    r = klasyfikuj(["Crypto lender files for bankruptcy, faces liquidation"])
    assert r["typ"] == "UPADEK"
    assert r["kierunek"] <= -0.7


def test_brak_zdarzenia():
    r = klasyfikuj(["Price moved slightly today"])
    assert r["typ"] == "BRAK"
    assert r["kierunek"] == 0.0 and r["pewnosc"] == 0.0


def test_pelne_slowo_nie_podciag():
    """'sec' nie trafia w 'second'; 'ban' nie w 'urban'."""
    r = klasyfikuj(["The second urban project launched"])
    assert "REGULACJA_NEG" not in r["rozklad"]


def test_neuron_long_na_silny_dodatni():
    s = NeuronTaksonomiaZdarzen().interpretuj(
        {"NEWS_EVENT_KIERUNEK": 0.8, "NEWS_EVENT_TYP": "ETF_APPROVAL", "NEWS_EVENT_PEWNOSC": 0.9})
    assert s.kierunek == "LONG"
    assert s.pewnosc > 0


def test_neuron_short_na_silny_ujemny():
    s = NeuronTaksonomiaZdarzen().interpretuj(
        {"NEWS_EVENT_KIERUNEK": -0.9, "NEWS_EVENT_TYP": "HACK", "NEWS_EVENT_PEWNOSC": 1.0})
    assert s.kierunek == "SHORT"


def test_neuron_rumor_kontrarianski_short():
    """Rumor z ujemnym kierunkiem → SHORT z adnotacją kontrariańską."""
    s = NeuronTaksonomiaZdarzen().interpretuj(
        {"NEWS_EVENT_KIERUNEK": -0.4, "NEWS_EVENT_TYP": "RUMOR", "NEWS_EVENT_PEWNOSC": 0.6})
    assert s.kierunek == "SHORT"
    assert any("KONTRARIAŃSKI" in p for p in s.powody)


def test_neuron_abstynuje_bez_danych():
    s = NeuronTaksonomiaZdarzen().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0


def test_neuron_neutral_w_strefie_szumu():
    s = NeuronTaksonomiaZdarzen().interpretuj(
        {"NEWS_EVENT_KIERUNEK": 0.1, "NEWS_EVENT_TYP": "TECHNICZNY", "NEWS_EVENT_PEWNOSC": 0.5})
    assert s.kierunek == "NEUTRAL"
