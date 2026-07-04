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


# ── NEWS-05: wiarygodność źródła (source credibility) ────────────────────────

def test_metadane_zawieraja_zrodlo_i_wage():
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS
    f = FetcherNewsRSS(zrodla=["https://www.coindesk.com/rss"], pobieracz=lambda u: RSS)
    m = f.pobierz_z_metadanymi()
    assert m and m[0]["zrodlo"] == "coindesk.com" and m[0]["waga"] == 1.0


def test_nieznane_zrodlo_polowa_wagi():
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS, WAGA_NIEZNANE
    f = FetcherNewsRSS(zrodla=["https://nieznany-blog.xyz/feed"], pobieracz=lambda u: RSS)
    m = f.pobierz_z_metadanymi()
    assert m and m[0]["waga"] == WAGA_NIEZNANE == 0.5


def test_domena_z_url():
    from imperium.akwedukty.news_fetcher import _domena
    assert _domena("https://www.coindesk.com/arc/rss/") == "coindesk.com"
    assert _domena("http://decrypt.co/feed") == "decrypt.co"


def test_pobierz_wstecznie_kompatybilne():
    """pobierz() nadal zwraca List[str] (stare API nietknięte)."""
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS
    f = FetcherNewsRSS(zrodla=["x"], pobieracz=lambda u: RSS)
    w = f.pobierz()
    assert w and all(isinstance(t, str) for t in w)


# ── NEWS-08: data publikacji z RSS (half-life) ────────────────────────────────

def test_parsuj_date_rss_rfc822():
    from imperium.akwedukty.news_fetcher import _parsuj_date_pub
    assert _parsuj_date_pub("Wed, 02 Jul 2026 14:30:00 +0000") is not None


def test_parsuj_date_atom_iso():
    from imperium.akwedukty.news_fetcher import _parsuj_date_pub
    assert _parsuj_date_pub("2026-07-02T14:30:00Z") is not None


def test_parsuj_date_pusta_none():
    from imperium.akwedukty.news_fetcher import _parsuj_date_pub
    assert _parsuj_date_pub("") is None and _parsuj_date_pub("bzdura") is None


def test_pozycje_z_data_pub():
    from imperium.akwedukty.news_fetcher import _pozycje_z_rss
    xml = ("<rss><channel><title>CD</title><item><title>BTC rally</title>"
           "<pubDate>Wed, 02 Jul 2026 14:30:00 +0000</pubDate></item></channel></rss>")
    poz = _pozycje_z_rss(xml)
    assert poz[0]["tytul"] == "BTC rally" and poz[0]["data_pub"] is not None


def test_metadane_zawieraja_date_pub():
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS
    xml = ("<rss><channel><title>X</title><item><title>BTC surge</title>"
           "<pubDate>Wed, 02 Jul 2026 14:30:00 +0000</pubDate></item></channel></rss>")
    f = FetcherNewsRSS(zrodla=["https://www.coindesk.com/rss"], pobieracz=lambda u: xml)
    m = f.pobierz_z_metadanymi()
    assert "data_pub" in m[0]
