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


def _tytuly_z_rss(xml_tekst: str) -> List[str]:
    """Wyłuskuje <title> z surowego RSS/Atom (stdlib, odporne na drobne błędy)."""
    if not xml_tekst:
        return []
    tytuly: List[str] = []
    try:
        root = ElementTree.fromstring(xml_tekst)
    except ElementTree.ParseError:
        # fallback regexowy gdy XML lekko uszkodzony: bierz tytuły z <item>/<entry>,
        # pomijając <title> kanału (metadane feedu, nie nagłówek).
        pozycje = re.findall(r"<(?:item|entry)[^>]*>(.*?)</(?:item|entry)>",
                             xml_tekst, re.DOTALL | re.I)
        for poz in pozycje:
            m = re.search(r"<title[^>]*>(.*?)</title>", poz, re.DOTALL | re.I)
            if m:
                tytuly.append(re.sub(r"<.*?>", "", m.group(1)).strip())
        return tytuly
    # Tylko tytuły POZYCJI (item/entry) — <title> kanału/feedu to metadane, nie nagłówek.
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()   # bez namespace
        if tag not in ("item", "entry"):
            continue
        for dziecko in el:
            if dziecko.tag.split("}")[-1].lower() == "title" and dziecko.text and dziecko.text.strip():
                tytuly.append(dziecko.text.strip())
                break
    return tytuly


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
        baza = _baza_z_symbolu(symbol)
        aliasy = _ALIASY.get(baza, [baza.lower()] if baza else [])
        widziane = set()
        wynik: List[str] = []
        for url in self.zrodla:
            try:
                surowe = self._pobieracz(url)
            except Exception as e:  # noqa: BLE001 — źródło zawodne → pomiń, nie crash
                logger.info(f"[Fetcher] źródło {url} padło: {e}")
                continue
            for tytul in _tytuly_z_rss(surowe):
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
                wynik.append(tytul)
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
