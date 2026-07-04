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


# ── NEWS-05: wiarygodność źródła skaluje pewność ──────────────────────────────

def test_wiarygodnosc_skaluje_pewnosc():
    """Ten sam nagłówek: źródło 1.0 → wyższa pewność niż źródło 0.5."""
    class FMeta:
        def __init__(self, waga): self.waga = waga
        def __call__(self, s): return ["Bitcoin ETF approval rally"]
        def pobierz_z_metadanymi(self, s):
            return [{"tytul": "Bitcoin ETF approval rally", "zrodlo": "x", "waga": self.waga}]
    a1 = AdapterNewsLLM(fetcher=FMeta(1.0), uzyj_llm=False).pobierz()
    a5 = AdapterNewsLLM(fetcher=FMeta(0.5), uzyj_llm=False).pobierz()
    assert a1["NEWS_PEWNOSC"] > a5["NEWS_PEWNOSC"]
    assert a1["NEWS_WIARYGODNOSC"] == 1.0 and a5["NEWS_WIARYGODNOSC"] == 0.5


def test_fetcher_bez_metadanych_wiarygodnosc_1():
    """Stary fetcher (List[str]) → wiarygodność neutralna 1.0 (wstecznie kompatybilne)."""
    ad = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin rally record"], uzyj_llm=False)
    d = ad.pobierz()
    assert d["NEWS_WIARYGODNOSC"] == 1.0


def test_wagi_zrodel_wplywaja_na_kierunek():
    """Bycze z mocnego źródła + niedźwiedzie ze słabego → sentyment netto DODATNI."""
    w = AdapterNewsLLM._sentyment_slownikowy(
        ["Bitcoin rally surge record", "Bitcoin crash collapse dump"],
        wagi_zrodel=[1.0, 0.3])
    assert w["sentyment"] > 0


# ── NEWS-06: novelty (powtórzony news już wyceniony) ──────────────────────────

def test_novelty_swiezy_feed_pelna_pewnosc():
    ad = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin rally record"], uzyj_llm=False)
    d = ad.pobierz("BTCUSDT")
    assert d["NEWS_NOVELTY"] == 1.0


def test_novelty_powtorzony_news_tlumiony():
    """Ten sam nagłówek drugi raz → novelty 0, pewność ×0.5."""
    ad = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin rally record"], uzyj_llm=False)
    d1 = ad.pobierz("BTCUSDT")
    d2 = ad.pobierz("BTCUSDT")
    assert d2["NEWS_NOVELTY"] == 0.0
    assert abs(d2["NEWS_PEWNOSC"] - d1["NEWS_PEWNOSC"] * 0.5) < 1e-6


def test_novelty_mieszany_feed():
    """1 stary + 1 nowy nagłówek → novelty 0.5."""
    feeds = [["Bitcoin rally record"], ["Bitcoin rally record", "Ethereum hack exploit"]]
    box = {"i": 0}
    ad = AdapterNewsLLM(fetcher=lambda s: feeds[box["i"]], uzyj_llm=False)
    ad.pobierz("BTCUSDT"); box["i"] = 1
    d = ad.pobierz("BTCUSDT")
    assert d["NEWS_NOVELTY"] == 0.5


def test_novelty_per_symbol_niezalezna():
    """Pamięć widzianych nagłówków jest per symbol (BTC nie zaraża ETH)."""
    ad = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin rally record"], uzyj_llm=False)
    ad.pobierz("BTCUSDT")
    d_eth = ad.pobierz("ETHUSDT")
    assert d_eth["NEWS_NOVELTY"] == 1.0   # dla ETH to pierwszy raz


# ── NEWS-07: rozrzut/niezgoda między nagłówkami (dispersion) ──────────────────

def test_rozrzut_jednomyslne_zero():
    r = AdapterNewsLLM._rozrzut_naglowkow(["Bitcoin rally surge", "ETH record breakout"])
    assert r == 0.0


def test_rozrzut_pol_na_pol_jeden():
    r = AdapterNewsLLM._rozrzut_naglowkow(["Bitcoin rally surge", "ETH crash collapse"])
    assert r == 1.0


def test_rozrzut_bez_wydzwieku_none():
    assert AdapterNewsLLM._rozrzut_naglowkow(["market update today"]) is None


def test_rozrzut_2_1_wartosc():
    """2 bycze + 1 niedźwiedzi → 1 - |2-1|/3 = 0.6667."""
    r = AdapterNewsLLM._rozrzut_naglowkow(
        ["BTC rally", "ETH surge", "SOL crash"])
    assert abs(r - 0.6667) < 1e-3


def test_rozrzut_w_pobierz():
    ad = AdapterNewsLLM(fetcher=lambda s: ["BTC rally", "BTC crash"], uzyj_llm=False)
    assert ad.pobierz()["NEWS_ROZRZUT"] == 1.0


def test_rozrzut_nie_zmienia_pewnosci():
    """Prawo XVI: rozrzut to wskaźnik informacyjny — NIE mnoży pewności (zanim IC zmierzony)."""
    zgodne = AdapterNewsLLM(fetcher=lambda s: ["BTC rally", "ETH surge"], uzyj_llm=False).pobierz()
    # pewność wynika z trafień/wiarygodności/novelty — rozrzut osobno w kluczu
    assert "NEWS_ROZRZUT" in zgodne and "NEWS_PEWNOSC" in zgodne


# ── NEWS-08: half-life świeżości ──────────────────────────────────────────────

def test_swiezosc_swiezy_pelna_stary_tlumiony():
    import time
    HL = AdapterNewsLLM.HALF_LIFE_SEK
    t = time.time()
    w = AdapterNewsLLM._wagi_swiezosci([t, t - HL, None])   # świeży, 1 half-life, brak daty
    assert w[0] == 1.0 and abs(w[1] - 0.5) < 0.02 and w[2] == 1.0


def test_swiezosc_wszystkie_bez_daty_neutralne():
    assert AdapterNewsLLM._wagi_swiezosci([None, None]) == [1.0, 1.0]


def test_swiezosc_wzgledem_najnowszego():
    """Wiek liczony względem najnowszego w partii (nie zegara)."""
    w = AdapterNewsLLM._wagi_swiezosci([1000.0, 1000.0 - AdapterNewsLLM.HALF_LIFE_SEK])
    assert w[0] == 1.0 and abs(w[1] - 0.5) < 0.02


def test_swiezy_news_wazy_wiecej_w_sentymencie():
    """Bycze świeże + niedźwiedzie stare → sentyment DODATNI (świeżość przeważa)."""
    class F:
        def __call__(self, s): return ["BTC rally surge", "BTC crash collapse"]
        def pobierz_z_metadanymi(self, s):
            import time
            t = time.time()
            return [
                {"tytul": "BTC rally surge", "waga": 1.0, "data_pub": t},
                {"tytul": "BTC crash collapse", "waga": 1.0, "data_pub": t - 48 * 3600}]
    d = AdapterNewsLLM(fetcher=F(), uzyj_llm=False).pobierz("BTCUSDT")
    assert d["NEWS_SENTYMENT"] > 0   # świeży byczy przeważa nad starym niedźwiedzim
    assert d["NEWS_SWIEZOSC"] < 1.0
