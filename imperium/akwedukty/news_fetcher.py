"""
📡 FetcherNewsRSS — pobieracz nagłówków rynkowych dla NEWS-01 (UNLOCK adaptera).

PROBLEM (audyt 2026-06-30): NEWS-01 + AdapterNewsLLM były gotowe (klasyfikator LLM +
fallback słownikowy), ale adapter dostawał PUSTY fetcher → neuron zawsze milczał, nawet
z DeepSeek. Brakującym ogniwem był FEED nagłówków, nie API. Ten moduł to ogniwo.

ŹRÓDŁA (darmowe RSS, bez klucza — research 2026: CoinDesk/CoinTelegraph/Decrypt to czołówka
publisherów indeksowanych przez płatne API jak CoinGecko News/Crypto News API):
  • https://www.coindesk.com/arc/outboundfeeds/rss/
  • https://cointelegraph.com/rss
  • https://decrypt.co/feed
Parsowanie RSS wyłącznie stdlib (xml.etree) — ZERO nowych zależności (Prawo I).

DWA TRYBY (offline-first, jak cała Brama):
  1. LIVE — urllib pobiera RSS z sieci (lokal/serwer; w chmurze proxy może blokować).
  2. TEST/OFFLINE — wstrzykiwany `_pobieracz(url)->str` zwraca surowy XML → pełny test bez sieci.

FILTROWANIE PER-AKTYWO: `pobierz(symbol)` zwraca nagłówki; gdy symbol podany (np. "BTCUSDT"),
filtruje po nazwie bazowej (BTC/Bitcoin) — reszta to szum globalny. Bez symbolu → wszystko.

DEDUPLIKACJA: ta sama historia u wielu wydawców liczona raz (normalizacja tytułu) —
zgodne z research 2026 (embedding-based event linking; tu deterministyczny odpowiednik).

Wpięcie: `AdapterNewsLLM(fetcher=FetcherNewsRSS())` w petla_live/dyrygent (opt-in).
Bez sieci / błąd → [] (Prawo XV: NEWS-01 abstynuje, nie martwy ciężar).
"""

from __future__ import annotations

import logging
import re
import urllib.request
from typing import Callable, Dict, List, Optional
from xml.etree import ElementTree

logger = logging.getLogger("Fetcher")

# Darmowe feedy RSS (czołowi wydawcy krypto — research 2026).
ZRODLA_DOMYSLNE = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

# NEWS-05: wiarygodność wydawcy (source credibility weighting — research 2026).
# Skala 0..1: ile waży nagłówek z danego źródła w ważonym sentymencie. Uzasadnienie:
# CoinDesk/CoinTelegraph = redakcje z fact-checkiem; nieznane źródło = ostrożnie (0.5).
WIARYGODNOSC_ZRODEL = {
    "coindesk.com": 1.0,
    "cointelegraph.com": 0.9,
    "decrypt.co": 0.85,
    "theblock.co": 0.9,
    "reuters.com": 1.0,
    "bloomberg.com": 1.0,
}
WAGA_NIEZNANE = 0.5   # nieznana domena → połowa wagi (nie zero — może być wartościowa)


def _domena(url: str) -> str:
    """'https://www.coindesk.com/arc/...' → 'coindesk.com'."""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1).lower() if m else url


# Mapowanie symbol→aliasy do filtrowania per-aktywo (nazwa bazowa + pełna).
_ALIASY = {
    "BTC": ["btc", "bitcoin"], "ETH": ["eth", "ethereum", "ether"],
    "SOL": ["sol", "solana"], "BNB": ["bnb", "binance coin"],
    "DOGE": ["doge", "dogecoin"], "XRP": ["xrp", "ripple"],
    "ADA": ["ada", "cardano"], "AVAX": ["avax", "avalanche"],
}


def _baza_z_symbolu(symbol: str) -> str:
    """'BTCUSDT' → 'BTC'; 'ETH/USDT' → 'ETH'; '' → ''."""
    s = re.sub(r"[^A-Za-z]", "", symbol).upper()
    # BUSD/USDT/USDC PRZED USD — inaczej "BTCBUSD" ucięłoby tylko "USD" → "BTCB" (zły alias).
    for koncowka in ("USDT", "USDC", "BUSD", "USD", "PERP"):
        if s.endswith(koncowka) and len(s) > len(koncowka):
            return s[: -len(koncowka)]
    return s


def _parsuj_date_pub(s: "Optional[str]") -> "Optional[float]":
    """
    Data publikacji → epoch (float) lub None. RSS: RFC822 ('Wed, 02 Jul 2026 14:30:00 +0000'),
    Atom: ISO ('2026-07-02T14:30:00Z'). Stdlib, tolerancyjne. NEWS-08 half-life.
    """
    if not s or not s.strip():
        return None
    s = s.strip()
    try:
        from email.utils import parsedate_to_datetime
        from datetime import timezone
        dt = parsedate_to_datetime(s)
        if dt is not None:
            # feed bez strefy → traktuj jako UTC (inaczej timestamp() użyłby strefy hosta
            # i przesunął wiek → skrzywił half-life NEWS-08).
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
    except (TypeError, ValueError, IndexError):
        pass
    try:
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


def _pozycje_z_rss(xml_tekst: str) -> "List[Dict[str, object]]":
    """
    Wyłuskuje POZYCJE (item/entry) z RSS/Atom: [{"tytul": str, "data_pub": epoch|None}].
    Tytuł kanału pominięty. data_pub z <pubDate> (RSS) lub <published>/<updated> (Atom).
    """
    if not xml_tekst:
        return []
    poz: "List[Dict[str, object]]" = []
    try:
        root = ElementTree.fromstring(xml_tekst)
    except ElementTree.ParseError:
        # fallback regexowy: tytuł + data z bloków item/entry
        for blok in re.findall(r"<(?:item|entry)[^>]*>(.*?)</(?:item|entry)>",
                               xml_tekst, re.DOTALL | re.I):
            mt = re.search(r"<title[^>]*>(.*?)</title>", blok, re.DOTALL | re.I)
            md = re.search(r"<(?:pubDate|published|updated)[^>]*>(.*?)</", blok, re.DOTALL | re.I)
            if mt:
                poz.append({"tytul": re.sub(r"<.*?>", "", mt.group(1)).strip(),
                            "data_pub": _parsuj_date_pub(md.group(1) if md else None)})
        return poz
    for el in root.iter():
        if el.tag.split("}")[-1].lower() not in ("item", "entry"):
            continue
        tytul, data = None, None
        for dziecko in el:
            tag = dziecko.tag.split("}")[-1].lower()
            if tag == "title" and dziecko.text and dziecko.text.strip() and tytul is None:
                tytul = dziecko.text.strip()
            elif tag in ("pubdate", "published", "updated") and dziecko.text and data is None:
                data = _parsuj_date_pub(dziecko.text)
        if tytul:
            poz.append({"tytul": tytul, "data_pub": data})
    return poz


def _tytuly_z_rss(xml_tekst: str) -> List[str]:
    """Same tytuły POZYCJI (item/entry) — wstecznie kompatybilne opakowanie na _pozycje_z_rss."""
    return [str(p["tytul"]) for p in _pozycje_z_rss(xml_tekst)]


def _normalizuj(tytul: str) -> str:
    """Klucz dedup: małe litery, bez interpunkcji/whitespace (ta sama historia = 1)."""
    return re.sub(r"[^a-z0-9]", "", tytul.lower())


class FetcherNewsRSS:
    """
    Pobieracz nagłówków RSS dla AdapterNewsLLM. Callable: `fetcher(symbol) -> List[str]`.
    """

    def __init__(
        self,
        zrodla: Optional[List[str]] = None,
        pobieracz: Optional[Callable[[str], str]] = None,
        timeout: int = 8,
        limit: int = 40,
    ):
        """
        zrodla:    lista URL-i RSS (domyślnie czołowi wydawcy krypto).
        pobieracz: callable(url)->str surowy XML (wstrzykiwany w testach; None → urllib).
        limit:     max nagłówków łącznie (po dedup).
        """
        self.zrodla = zrodla if zrodla is not None else list(ZRODLA_DOMYSLNE)
        self._pobieracz = pobieracz or self._pobierz_http
        self.timeout = timeout
        self.limit = limit

    def _pobierz_http(self, url: str) -> str:
        """Domyślne pobranie surowego RSS (urllib, stdlib). Błąd → '' (graceful)."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ImperiumBot/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.read().decode("utf-8", errors="ignore")
        except Exception as e:  # noqa: BLE001 — sieć zawodna, abstynencja zamiast crash
            logger.info(f"[Fetcher] RSS {url} niedostępny: {e}")
            return ""

    def __call__(self, symbol: str = "") -> List[str]:
        return self.pobierz(symbol)

    def pobierz(self, symbol: str = "") -> List[str]:
        """Zwraca zdeduplikowane nagłówki (opcjonalnie filtrowane per-aktywo)."""
        return [m["tytul"] for m in self.pobierz_z_metadanymi(symbol)]

    def pobierz_z_metadanymi(self, symbol: str = "") -> List[Dict[str, object]]:
        """
        NEWS-05 (source credibility, research 2026): nagłówki Z WAGĄ ŹRÓDŁA.
        Zwraca [{"tytul": str, "zrodlo": domena, "waga": float}] — CoinDesk waży
        więcej niż nieznany blog. Adapter używa wag do ważonego sentymentu.
        """
        baza = _baza_z_symbolu(symbol)
        aliasy = _ALIASY.get(baza, [baza.lower()] if baza else [])
        widziane = set()
        wynik: List[Dict[str, object]] = []
        for url in self.zrodla:
            try:
                surowe = self._pobieracz(url)
            except Exception as e:  # noqa: BLE001 — źródło zawodne → pomiń, nie crash
                logger.info(f"[Fetcher] źródło {url} padło: {e}")
                continue
            domena = _domena(url)
            waga = WIARYGODNOSC_ZRODEL.get(domena, WAGA_NIEZNANE)
            for poz in _pozycje_z_rss(surowe):
                tytul = str(poz["tytul"])
                klucz = _normalizuj(tytul)
                if not klucz or klucz in widziane:
                    continue
                # filtr per-aktywo: alias jako PEŁNE słowo (granice \b), nie podciąg —
                # inaczej "eth" trafiałby "ethics", "sol" → "solid" (zaśmiecanie NEWS-01).
                low = tytul.lower()
                if aliasy and not any(
                        re.search(r"\b" + re.escape(a) + r"\b", low) for a in aliasy):
                    continue
                widziane.add(klucz)
                wynik.append({"tytul": tytul, "zrodlo": domena, "waga": waga,
                              "data_pub": poz.get("data_pub")})
                if len(wynik) >= self.limit:
                    return wynik
        return wynik


def diagnostyka() -> Dict[str, int]:
    """Szybki test żywego feedu (lokal): ile nagłówków łapie każde źródło."""
    f = FetcherNewsRSS()
    return {url: len(_tytuly_z_rss(f._pobierz_http(url))) for url in f.zrodla}


if __name__ == "__main__":
    print("📡 Diagnostyka feedów RSS (wymaga sieci):")
    for url, n in diagnostyka().items():
        print(f"  {n:3d} nagłówków ← {url}")
    print("\nPrzykład (BTC):")
    for h in FetcherNewsRSS().pobierz("BTCUSDT")[:8]:
        print(f"  • {h}")
