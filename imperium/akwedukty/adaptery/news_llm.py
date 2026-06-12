"""
📰 AdapterNewsLLM — most do NEWS-01 (sentyment nagłówków rynkowych).

Dostarcza NEWS_SENTYMENT (-1..+1), NEWS_PEWNOSC (0..1), NEWS_N (liczba nagłówków)
budząc NeuronSentymentNews.

DWA TRYBY KLASYFIKACJI (offline-first, Prawo XIX: kod+testy zanim coś „istnieje"):
  1. LLM (DeepSeek) — gdy DEEPSEEK_API_KEY ustawiony i `uzyj_llm=True`.
     GlosImperium klasyfikuje wydźwięk listy nagłówków → JSON {sentyment, pewnosc}.
     LLM NIE liczy matematyki (Prawo I) — tylko KLASYFIKUJE język. Mapowanie na
     liczbę robi adapter.
  2. FALLBACK SŁOWNIKOWY — gdy brak klucza/LLM padł/uzyj_llm=False.
     Deterministyczny licznik słów-kluczy (byczych/niedźwiedzich) → sentyment.
     Działa OFFLINE, w pełni testowalny, bez sieci i bez kosztu. Zero zależności.

WSTRZYKIWANY FETCHER (jak AdapterFearGreed):
  `pobierz()` deleguje pobranie nagłówków do `self._fetcher(symbol) -> List[str]`.
  - produkcja: podłącz fetcher uderzający w RSS/API newsów (CryptoPanic, RSS).
  - testy: wstrzykujemy fetcher zwracający listę nagłówków → pełny test OFFLINE.

BEZPIECZEŃSTWO: klucz LLM WYŁĄCZNIE z os.getenv (przez GlosImperium). Fallback
  słownikowy nie potrzebuje żadnych kluczy ani sieci.

PRAWO XV: budzi NEWS-01 tylko gdy adapter podpięty i dostarcza NEWS_SENTYMENT.
"""

import json
import logging
import re
from typing import Callable, List, Optional

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.sentyment import NeuronSentymentNews

logger = logging.getLogger("Adapter")


def _slowo_wystepuje(slowo: str, tekst: str) -> bool:
    """
    True gdy `slowo` występuje w `tekst` jako PEŁNE słowo (granice \\b\\b),
    nie podciąg. Chroni przed fałszywym trafieniem "sec" w "second" itp.
    Obsługuje frazy wielowyrazowe (np. "all-time high") — granica wokół całości.
    """
    return re.search(r"\b" + re.escape(slowo) + r"\b", tekst) is not None


# Leksykon sentymentu krypto (fallback bez LLM). Wagi: 1.0 standard, 1.5 mocne.
# UWAGA: klucze dopasowywane do PEŁNYCH słów (granice \b\b), nie podciągów —
# inaczej "sec" trafiałby "second", "ban" w "urban", "bull" w "bulletin" (fałszywy
# wydźwięk neutralnego nagłówka). Dlatego rdzenie podajemy w pełnych formach;
# warianty fleksyjne wymieniamy jawnie zamiast polegać na prefiksie.
SLOWA_BYCZE = {
    "partnership": 1.0, "partnerstwo": 1.0, "adoption": 1.2, "adopcja": 1.2,
    "etf": 1.3, "approval": 1.3, "approved": 1.3, "zatwierdzenie": 1.3,
    "rally": 1.2, "wzrost": 1.0, "wzrosty": 1.0,
    "surge": 1.3, "bull": 1.2, "bullish": 1.2, "byczy": 1.2, "bycze": 1.2,
    "breakout": 1.1, "record": 1.2, "rekord": 1.2, "upgrade": 1.0,
    "integration": 1.0, "integracja": 1.0, "buy": 0.8,
    "akumulacja": 1.1, "accumulation": 1.1, "halving": 1.1,
    "institutional": 1.2, "instytucjonalny": 1.2, "soar": 1.3, "soars": 1.3,
    "all-time high": 1.5,
}
SLOWA_NIEDZWIEDZIE = {
    "hack": 1.5, "wlamanie": 1.5, "exploit": 1.4, "scam": 1.4, "oszustwo": 1.4,
    "ban": 1.3, "banned": 1.3, "zakaz": 1.3, "crash": 1.5, "krach": 1.5,
    "dump": 1.3, "lawsuit": 1.2, "pozew": 1.2, "regulation": 1.0, "regulacja": 1.0,
    "sec": 1.0, "fraud": 1.4, "bear": 1.2, "bearish": 1.2,
    "niedźwiedzi": 1.2, "selloff": 1.3, "wyprzedaż": 1.3,
    "bankruptcy": 1.5, "bankructwo": 1.5, "liquidation": 1.3, "likwidacja": 1.3,
    "plunge": 1.4, "collapse": 1.5, "upadek": 1.4, "delisting": 1.3,
    "halt": 1.2, "halts": 1.2, "wstrzymanie": 1.1,
}

# System prompt dla DeepSeek — klasyfikacja, nie matematyka (Prawo I).
_SYSTEM_PROMPT = (
    "Jesteś analitykiem sentymentu rynku krypto. Otrzymasz listę nagłówków "
    "newsów. Oceń ZBIORCZY wydźwięk dla ceny aktywa. Odpowiedz WYŁĄCZNIE czystym "
    'JSON-em: {"sentyment": float od -1.0 do 1.0, "pewnosc": float od 0.0 do 1.0}. '
    "sentyment: -1 skrajnie negatywny, 0 neutralny/mieszany, +1 skrajnie pozytywny. "
    "pewnosc: jak jednoznaczny jest wydźwięk. Bez komentarza, tylko JSON."
)


class AdapterNewsLLM(AdapterDanych):
    """
    Most do NEWS-01 NeuronSentymentNews. Dostarcza NEWS_SENTYMENT/PEWNOSC/N.

    Sentyment newsów jest (domyślnie) globalny dla rynku krypto — `symbol`
    przekazywany do fetchera, który może filtrować nagłówki per aktywo.
    """
    NAZWA = "NewsLLM(DeepSeek+fallback)"
    KLUCZE = ["NEWS_SENTYMENT", "NEWS_PEWNOSC", "NEWS_N"]
    _NEURONY = (NeuronSentymentNews,)
    _POWOD_USPIENIA = "Wymaga feedu newsów (AdapterNewsLLM — RSS/API + LLM/fallback)."

    def __init__(
        self,
        fetcher: Optional[Callable[[str], List[str]]] = None,
        uzyj_llm: bool = True,
        glos=None,
    ):
        """
        fetcher: callable(symbol) -> List[str] nagłówków. Domyślnie pusty feed
                 (neuron śpi — produkcja podłącza RSS/API).
        uzyj_llm: True → próbuj DeepSeek (gdy klucz); False → tylko fallback słownikowy.
        glos:     wstrzykiwany GlosImperium (test/produkcja); None → lazy-init z klucza.
        """
        self._fetcher = fetcher or (lambda symbol: [])
        self.uzyj_llm = uzyj_llm
        self._glos = glos

    # ── Klasyfikacja słownikowa (offline, deterministyczna) ───────────────────

    @staticmethod
    def _sentyment_slownikowy(naglowki: List[str]) -> dict:
        """
        Liczy sentyment z leksykonu: (bycze - niedźwiedzie) / (bycze + niedźwiedzie).
        Pewność rośnie z liczbą trafień (saturacja). Zero trafień → 0.0 neutralny.
        """
        score_byk = 0.0
        score_niedz = 0.0
        trafienia = 0
        for naglowek in naglowki:
            tekst = naglowek.lower()
            for slowo, waga in SLOWA_BYCZE.items():
                if _slowo_wystepuje(slowo, tekst):
                    score_byk += waga
                    trafienia += 1
            for slowo, waga in SLOWA_NIEDZWIEDZIE.items():
                if _slowo_wystepuje(slowo, tekst):
                    score_niedz += waga
                    trafienia += 1
        suma = score_byk + score_niedz
        if suma == 0:
            return {"sentyment": 0.0, "pewnosc": 0.2}
        sentyment = (score_byk - score_niedz) / suma
        # pewność: saturuje przy ~6 trafieniach
        pewnosc = min(1.0, 0.3 + trafienia / 10.0)
        return {"sentyment": round(sentyment, 4), "pewnosc": round(pewnosc, 4)}

    # ── Klasyfikacja LLM (DeepSeek) ────────────────────────────────────────────

    def _sentyment_llm(self, naglowki: List[str]) -> Optional[dict]:
        """
        Klasyfikuje przez DeepSeek. Zwraca {sentyment, pewnosc} lub None gdy
        brak klucza / LLM padł / odpowiedź nieparsowalna (→ wywołujący użyje fallbacku).
        """
        glos = self._glos
        if glos is None:
            try:
                from imperium.cesarz.deepseek_glos import GlosImperium
                glos = GlosImperium()
            except Exception as e:
                logger.info(f"[Adapter:NewsLLM] LLM niedostępny ({e}) — fallback słownikowy")
                return None
        tresc = "Nagłówki:\n" + "\n".join(f"- {h}" for h in naglowki)
        try:
            odp = glos.zapytaj(_SYSTEM_PROMPT, tresc, temperatura=0.1)
            return self._parsuj_json_llm(odp)
        except Exception as e:
            logger.warning(f"[Adapter:NewsLLM] LLM padł ({e}) — fallback słownikowy")
            return None

    @staticmethod
    def _parsuj_json_llm(odp: str) -> Optional[dict]:
        """Wyłuskuje {sentyment, pewnosc} z odpowiedzi LLM (toleruje otoczkę tekstu)."""
        if not odp:
            return None
        m = re.search(r"\{.*\}", odp, re.DOTALL)
        if not m:
            return None
        try:
            d = json.loads(m.group(0))
        except (ValueError, TypeError):
            return None
        if "sentyment" not in d:
            return None
        try:
            sent = max(-1.0, min(1.0, float(d["sentyment"])))
            pew = max(0.0, min(1.0, float(d.get("pewnosc", 0.5))))
        except (ValueError, TypeError):
            return None
        return {"sentyment": round(sent, 4), "pewnosc": round(pew, 4)}

    # ── Dostarczanie danych ────────────────────────────────────────────────────

    def pobierz(self, symbol: str = "") -> dict:
        """
        Zwraca {"NEWS_SENTYMENT": float|None, "NEWS_PEWNOSC": float, "NEWS_N": int}.
        Brak nagłówków → NEWS_SENTYMENT None (wzbogac() pominie → neuron śpi).
        """
        try:
            naglowki = list(self._fetcher(symbol) or [])
        except Exception as e:
            logger.warning(f"[Adapter:NewsLLM] fetcher padł dla {symbol}: {e}")
            return {"NEWS_SENTYMENT": None, "NEWS_PEWNOSC": None, "NEWS_N": 0}

        if not naglowki:
            return {"NEWS_SENTYMENT": None, "NEWS_PEWNOSC": None, "NEWS_N": 0}

        wynik = None
        if self.uzyj_llm:
            wynik = self._sentyment_llm(naglowki)
        if wynik is None:
            wynik = self._sentyment_slownikowy(naglowki)

        return {
            "NEWS_SENTYMENT": wynik["sentyment"],
            "NEWS_PEWNOSC": wynik["pewnosc"],
            "NEWS_N": len(naglowki),
        }
