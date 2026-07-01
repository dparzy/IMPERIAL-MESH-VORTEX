"""Testy FetcherNewsRSS (unlock NEWS-01) — offline, wstrzyknięty RSS."""

from imperium.akwedukty.news_fetcher import (
    FetcherNewsRSS, _tytuly_z_rss, _baza_z_symbolu, _normalizuj)

RSS = """<?xml version="1.0"?><rss><channel>
<title>CoinDesk</title>
<item><title>Bitcoin ETF approval sparks record rally</title></item>
<item><title>Exchange hack drains Ethereum funds</title></item>
<item><title>Solana institutional partnership announced</title></item>
</channel></rss>"""


def test_parsuje_tytuly():
    t = _tytuly_z_rss(RSS)
    assert "Bitcoin ETF approval sparks record rally" in t
    assert any("hack" in x.lower() for x in t)


def test_parsuje_uszkodzony_xml_fallback_regex():
    zly = "<rss><item><title>Bitcoin surges</title></item>"  # niezamknięte
    t = _tytuly_z_rss(zly)
    assert any("Bitcoin surges" in x for x in t)


def test_pusty_xml():
    assert _tytuly_z_rss("") == []


def test_baza_z_symbolu():
    assert _baza_z_symbolu("BTCUSDT") == "BTC"
    assert _baza_z_symbolu("ETH/USDT") == "ETH"
    assert _baza_z_symbolu("DOGEUSDC") == "DOGE"
    assert _baza_z_symbolu("") == ""


def test_filtr_per_aktywo():
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=lambda url: RSS)
    btc = f.pobierz("BTCUSDT")
    assert btc == ["Bitcoin ETF approval sparks record rally"]
    eth = f.pobierz("ETHUSDT")
    assert len(eth) == 1 and "Ethereum" in eth[0]


def test_bez_symbolu_wszystko():
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=lambda url: RSS)
    assert len(f.pobierz()) == 3   # 3 pozycje item (tytuł kanału pominięty)


def test_deduplikacja_miedzy_zrodlami():
    f = FetcherNewsRSS(zrodla=["a", "b"], pobieracz=lambda url: RSS)  # ten sam feed 2×
    wynik = f.pobierz()
    klucze = [_normalizuj(t) for t in wynik]
    assert len(klucze) == len(set(klucze))   # zero duplikatów


def test_siec_padla_graceful():
    def wybuch(url):
        raise OSError("brak sieci")
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=wybuch)
    assert f.pobierz("BTCUSDT") == []        # abstynencja, nie crash


def test_callable_interfejs():
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=lambda url: RSS)
    assert f("BTCUSDT") == f.pobierz("BTCUSDT")   # __call__ == pobierz


def test_limit():
    duzo = "<rss><channel>" + "".join(
        f"<item><title>News {i} bitcoin</title></item>" for i in range(100)) + "</channel></rss>"
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=lambda url: duzo, limit=10)
    assert len(f.pobierz()) == 10
