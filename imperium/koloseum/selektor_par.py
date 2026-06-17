"""
🎯 SELEKTOR PAR (W-330) — automatyczny dobór par do handlu LIVE na MEXC.

Luka audytu (przed LIVE): petla_live miała SZTYWNĄ listę par. System nie umiał sam
wykryć, co jest dostępne i płynne na giełdzie. Ten moduł to naprawia — łączy trzy
warstwy w jeden ranking ALFY (Prawo I — dane, nie opinia):

  1. DISTRIBUTION  — lista_par_rynku() z CCXT (wszystkie aktywne USDT-perp na MEXC)
  2. PŁYNNOŚĆ      — filtruj_plynne() (min. obrót 24h — chroni przed poślizgiem)
  3. DEKORELACJA   — score alfy = obrót_znorm × (1 − |korelacja z BTC|)

DLACZEGO DEKORELACJA (Prawo XVI): koszyk 5 par silnie skorelowanych z BTC to de facto
JEDNA pozycja ×5 — zero dywersyfikacji, kaskada w bessie. Premiujemy pary, które niosą
WŁASNĄ informację (niska |korelacja|), nie kopię ruchu BTC. To filar siły, nie redundancja.

WSTRZYKIWANY LOADER: SelektorPar(loader) — produkcja: DataLoader (CCXT, sieć), testy:
mock loader (deterministyczne serie) → pełny test OFFLINE bez sieci.

BEZPIECZEŃSTWO: endpointy publiczne CCXT (load_markets/fetch_ticker/fetch_ohlcv) — bez
klucza. Klucze handlowe (MEXC_API_KEY/SECRET) tylko w realnym routerze zleceń, z os.getenv.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

logger = logging.getLogger("SelektorPar")


@dataclass
class KandydatPary:
    """Jedna para z metrykami doboru."""
    symbol: str                     # format giełdy, np. 'ETH/USDT:USDT'
    obrot_usd: float                # obrót 24h (płynność)
    korelacja_btc: Optional[float]  # |korelacja| zwrotów z BTC ∈ [0,1] lub None
    score: float = 0.0              # finalny ranking alfy
    powody: List[str] = field(default_factory=list)


def _zwroty(close: Sequence[float]) -> List[float]:
    """Proste zwroty serii (pomija zerowe mianowniki)."""
    c = [float(x) for x in close if x is not None]
    return [(c[i] - c[i - 1]) / c[i - 1] for i in range(1, len(c)) if c[i - 1] > 0]


def _korelacja(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    """Pearson dwóch serii równej długości. None gdy zerowa wariancja/za krótkie."""
    n = min(len(a), len(b))
    if n < 5:
        return None
    a, b = list(a[-n:]), list(b[-n:])
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return None
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return max(-1.0, min(1.0, cov / (va ** 0.5 * vb ** 0.5)))


class SelektorPar:
    """
    Dobiera TOP-N par do handlu LIVE wg alfy (płynność × dekorelacja od BTC).

    Użycie produkcyjne:
        from imperium.akwedukty.kwatermistrz_danych import DataLoader
        sel = SelektorPar(DataLoader())
        pary = sel.wybierz(top_n=5, min_obrot_usd=5_000_000)
        # → ['BTC/USDT:USDT', 'XRP/USDT:USDT', ...] (symbole giełdy)
    """

    def __init__(self, loader, btc_symbol: str = "BTC/USDT:USDT", okno_korelacji: int = 200):
        self.loader = loader
        self.btc_symbol = btc_symbol
        self.okno_korelacji = okno_korelacji

    def _serie_close(self, symbol: str, timeframe: str) -> List[float]:
        """Pobiera zamknięcia (lista float). Pusta przy błędzie."""
        try:
            df = self.loader.fetch(symbol, timeframe=timeframe, limit=self.okno_korelacji)
            return [float(x) for x in df["close"].tolist()]
        except Exception as e:
            logger.warning(f"[SelektorPar] fetch {symbol} padł: {e}")
            return []

    def ranking(self, top_n: int = 5, min_obrot_usd: float = 5_000_000.0,
                quote: str = "USDT", typ: str = "swap",
                timeframe: str = "4h", max_kandydatow: int = 40) -> List[KandydatPary]:
        """
        Pełny pipeline: lista → płynność (TOP max_kandydatow) → dekorelacja → score.
        Zwraca posortowaną listę KandydatPary (najlepsze pierwsze). BTC zawsze w puli
        (kotwica koszyka), reszta wg alfy.
        """
        pary = self.loader.lista_par_rynku(quote=quote, typ=typ)
        if not pary:
            logger.warning("[SelektorPar] Brak par z rynku (sieć?) — pusty ranking.")
            return []

        plynne = self.loader.filtruj_plynne(pary, min_obrot_usd=min_obrot_usd,
                                             limit=max_kandydatow)
        if not plynne:
            return []

        # Normalizacja obrotu do [0,1] (max-min wśród płynnych)
        obroty = [p["obrot_usd"] for p in plynne]
        o_max, o_min = max(obroty), min(obroty)
        rozpietosc = (o_max - o_min) or 1.0

        # Seria BTC raz (kotwica korelacji)
        zr_btc = _zwroty(self._serie_close(self.btc_symbol, timeframe))

        kandydaci: List[KandydatPary] = []
        for p in plynne:
            sym = p["symbol"]
            obrot_norm = (p["obrot_usd"] - o_min) / rozpietosc
            if sym == self.btc_symbol or not zr_btc:
                kor = None
                dekor = 1.0  # BTC vs sam siebie — nie karzemy kotwicy
            else:
                zr = _zwroty(self._serie_close(sym, timeframe))
                k = _korelacja(zr_btc, zr)
                kor = abs(k) if k is not None else None
                dekor = (1.0 - kor) if kor is not None else 0.7  # brak danych: neutralnie
            # Score: 60% płynność + 40% dekorelacja (płynność warunek konieczny LIVE)
            score = 0.60 * obrot_norm + 0.40 * dekor
            powody = [f"obrót ${p['obrot_usd']/1e6:.1f}M (norm {obrot_norm:.2f})"]
            if kor is not None:
                powody.append(f"|korelacja BTC|={kor:.2f} → dekor {dekor:.2f}")
            kandydaci.append(KandydatPary(symbol=sym, obrot_usd=p["obrot_usd"],
                                          korelacja_btc=kor, score=round(score, 4),
                                          powody=powody))

        kandydaci.sort(key=lambda k: k.score, reverse=True)
        return kandydaci[:top_n]

    def wybierz(self, top_n: int = 5, **kw) -> List[str]:
        """Skrót: zwraca same symbole TOP-N (gotowe do KonfigPetliLive.symbole)."""
        return [k.symbol for k in self.ranking(top_n=top_n, **kw)]
