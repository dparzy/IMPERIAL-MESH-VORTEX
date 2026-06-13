"""Testy NEWS-01 NeuronSentymentNews + AdapterNewsLLM (W-297).

Reguła Test-Granic (Prawo XXI): testujemy progi, znaki, zero/None, granice.
"""

from imperium.legiony.neurony.sentyment import NeuronSentymentNews
from imperium.akwedukty.adaptery.news_llm import AdapterNewsLLM


# ════════════════════════════════════════════════════════════════════════════
#  NEURON NEWS-01
# ════════════════════════════════════════════════════════════════════════════

def _neuron():
    return NeuronSentymentNews()


# ── abstynencja / brak danych (Prawo XV) ──────────────────────────────────────

def test_brak_feedu_abstynuje():
    s = _neuron().interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_sentyment_none_abstynuje():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": None})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


# ── za mało nagłówków (granica MIN_NAGLOWKOW) ────────────────────────────────

def test_za_malo_naglowkow_neutral():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.9, "NEWS_N": 1})
    assert s.kierunek == "NEUTRAL"


def test_dokladnie_min_naglowkow_glosuje():
    # N == MIN_NAGLOWKOW (2) → już głosuje
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.9, "NEWS_N": 2})
    assert s.kierunek == "LONG"


# ── kierunek wg znaku sentymentu ─────────────────────────────────────────────

def test_pozytywny_long():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.7, "NEWS_N": 5})
    assert s.kierunek == "LONG"


def test_negatywny_short():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": -0.7, "NEWS_N": 5})
    assert s.kierunek == "SHORT"


# ── granica PROG_SZUMU (0.30) ─────────────────────────────────────────────────

def test_dokladnie_prog_szumu_long():
    # sentyment == +PROG_SZUMU → LONG (>=)
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.30, "NEWS_N": 5})
    assert s.kierunek == "LONG"


def test_dokladnie_minus_prog_szumu_short():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": -0.30, "NEWS_N": 5})
    assert s.kierunek == "SHORT"


def test_ponizej_progu_neutral():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.29, "NEWS_N": 5})
    assert s.kierunek == "NEUTRAL"


def test_zero_sentyment_neutral():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.0, "NEWS_N": 5})
    assert s.kierunek == "NEUTRAL"


# ── modulacja pewności przez NEWS_PEWNOSC ────────────────────────────────────

def test_pewnosc_modulowana_przez_llm():
    wysoka = _neuron().interpretuj({"NEWS_SENTYMENT": 0.8, "NEWS_N": 5, "NEWS_PEWNOSC": 1.0})
    niska = _neuron().interpretuj({"NEWS_SENTYMENT": 0.8, "NEWS_N": 5, "NEWS_PEWNOSC": 0.3})
    assert wysoka.pewnosc > niska.pewnosc


def test_brak_pewnosci_llm_traktowane_jak_jeden():
    # NEWS_PEWNOSC None → traktowane jak 1.0
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 0.8, "NEWS_N": 5})
    assert s.pewnosc > 0.0


def test_pewnosc_nie_przekracza_maksa():
    s = _neuron().interpretuj({"NEWS_SENTYMENT": 1.0, "NEWS_N": 9, "NEWS_PEWNOSC": 1.0})
    assert s.pewnosc <= NeuronSentymentNews.PEWNOSC_MAX


# ── metadane neuronu ──────────────────────────────────────────────────────────

def test_kategoria_R():
    assert _neuron().KATEGORIA == "R"


def test_klucz_news01():
    assert _neuron().KLUCZ == "NEWS-01"


def test_dostepny():
    assert _neuron().DOSTEPNY is True


# ════════════════════════════════════════════════════════════════════════════
#  ADAPTER NewsLLM — fallback słownikowy (offline)
# ════════════════════════════════════════════════════════════════════════════

def _adapter_offline(naglowki):
    # uzyj_llm=False → zawsze fallback słownikowy, bez sieci
    return AdapterNewsLLM(fetcher=lambda s: naglowki, uzyj_llm=False)


def test_pusty_feed_zwraca_none():
    a = _adapter_offline([])
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] is None
    assert wynik["NEWS_N"] == 0


def test_bycze_naglowki_dodatni_sentyment():
    a = _adapter_offline([
        "Bitcoin ETF approval sparks record rally",
        "Major institutional adoption surge",
        "Ethereum upgrade integration partnership",
    ])
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] > 0
    assert wynik["NEWS_N"] == 3


def test_niedzwiedzie_naglowki_ujemny_sentyment():
    a = _adapter_offline([
        "Exchange hack drains millions in exploit",
        "SEC lawsuit triggers selloff and crash",
        "Major bankruptcy causes liquidation cascade",
    ])
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] < 0


def test_neutralne_naglowki_zero_sentyment():
    a = _adapter_offline([
        "Bitcoin price stays flat today",
        "Analysts discuss market structure",
    ])
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] == 0.0


def test_podciag_nie_falszywie_trafia():
    # "second"⊃"sec", "urban"⊃"ban", "bulletin"⊃"bull" — NIE mogą liczyć się
    # jako sygnał (granice słów). Neutralny nagłówek = sentyment 0.
    a = _adapter_offline([
        "Bitcoin holds for a second consecutive week",
        "Urban adoption bulletin published",
    ])
    wynik = a.pobierz("BTCUSDT")
    # "adoption" to jedyne prawdziwe trafienie (bycze) — "ban"/"bull"/"sec" pominięte
    assert wynik["NEWS_SENTYMENT"] > 0


def test_sec_jako_pelne_slowo_trafia():
    # "SEC" (regulator) jako pełne słowo MUSI się liczyć (niedźwiedzie)
    a = _adapter_offline(["SEC lawsuit against major exchange"])
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] < 0


def test_mieszane_naglowki_w_zakresie():
    a = _adapter_offline([
        "ETF approval rally",  # bycze
        "Exchange hack crash",  # niedźwiedzie
    ])
    wynik = a.pobierz("BTCUSDT")
    assert -1.0 <= wynik["NEWS_SENTYMENT"] <= 1.0


def test_pewnosc_rosnie_z_trafieniami():
    a_malo = _adapter_offline(["Bitcoin rally"])
    a_duzo = _adapter_offline([
        "rally surge record bull breakout",
        "adoption etf approval institutional",
    ])
    w_malo = a_malo.pobierz("X")
    w_duzo = a_duzo.pobierz("X")
    assert w_duzo["NEWS_PEWNOSC"] >= w_malo["NEWS_PEWNOSC"]


def test_fetcher_padniety_bezpieczny():
    def zly_fetcher(symbol):
        raise RuntimeError("brak sieci")
    a = AdapterNewsLLM(fetcher=zly_fetcher, uzyj_llm=False)
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] is None
    assert wynik["NEWS_N"] == 0


# ── parsowanie JSON z LLM ────────────────────────────────────────────────────

def test_parsuj_json_czysty():
    d = AdapterNewsLLM._parsuj_json_llm('{"sentyment": 0.6, "pewnosc": 0.8}')
    assert d["sentyment"] == 0.6
    assert d["pewnosc"] == 0.8


def test_parsuj_json_z_otoczka():
    d = AdapterNewsLLM._parsuj_json_llm('Oto wynik: {"sentyment": -0.4, "pewnosc": 0.7} koniec')
    assert d["sentyment"] == -0.4


def test_parsuj_json_clamp_zakres():
    # LLM zwrócił poza zakresem → przycięte do [-1, 1]
    d = AdapterNewsLLM._parsuj_json_llm('{"sentyment": 5.0, "pewnosc": 2.0}')
    assert d["sentyment"] == 1.0
    assert d["pewnosc"] == 1.0


def test_parsuj_json_smieci_none():
    assert AdapterNewsLLM._parsuj_json_llm("zupełnie nie json") is None
    assert AdapterNewsLLM._parsuj_json_llm("") is None
    assert AdapterNewsLLM._parsuj_json_llm('{"inne": 1}') is None


# ── LLM z wstrzykniętym głosem (mock, bez sieci) ──────────────────────────────

class _FakeGlos:
    def __init__(self, odp):
        self._odp = odp
    def zapytaj(self, system_prompt, tresc, temperatura=0.1):
        return self._odp


def test_llm_uzywany_gdy_dostepny():
    glos = _FakeGlos('{"sentyment": 0.9, "pewnosc": 0.95}')
    a = AdapterNewsLLM(fetcher=lambda s: ["jakikolwiek nagłówek"], uzyj_llm=True, glos=glos)
    wynik = a.pobierz("BTCUSDT")
    assert wynik["NEWS_SENTYMENT"] == 0.9
    assert wynik["NEWS_PEWNOSC"] == 0.95


def test_llm_padniety_fallback_slownikowy():
    glos = _FakeGlos("zepsuta odpowiedź bez json")
    a = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin ETF approval rally"],
                       uzyj_llm=True, glos=glos)
    wynik = a.pobierz("BTCUSDT")
    # LLM nieparsowalny → fallback słownikowy zadziałał (bycze → dodatni)
    assert wynik["NEWS_SENTYMENT"] > 0


# ── integracja adapter → neuron ───────────────────────────────────────────────

def test_adapter_budzi_neuron_long():
    a = _adapter_offline([
        "ETF approval record rally surge",
        "Institutional adoption breakout all-time high",
    ])
    wskazniki = {}
    wskazniki.update(a.pobierz("BTCUSDT"))
    s = NeuronSentymentNews().interpretuj(wskazniki)
    assert s.kierunek == "LONG"
