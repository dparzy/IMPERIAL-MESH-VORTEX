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
from imperium.akwedukty.klasyfikator_zdarzen import klasyfikuj as _klasyfikuj_zdarzenia
from imperium.legiony.neurony.sentyment import NeuronSentymentNews
from imperium.legiony.neurony.zdarzenia import NeuronTaksonomiaZdarzen
from imperium.legiony.neurony.news_dynamika import NeuronDeltaeSentymentu, NeuronSpikeUwagi

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
    KLUCZE = ["NEWS_SENTYMENT", "NEWS_PEWNOSC", "NEWS_N",
              "NEWS_EVENT_KIERUNEK", "NEWS_EVENT_TYP", "NEWS_EVENT_PEWNOSC",
              "NEWS_SENTYMENT_DELTA", "NEWS_ATTENTION_SPIKE", "NEWS_WIARYGODNOSC", "NEWS_NOVELTY"]
    _NEURONY = (NeuronSentymentNews, NeuronTaksonomiaZdarzen,
                NeuronDeltaeSentymentu, NeuronSpikeUwagi)
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
        # Stan kroczący per symbol (do NEWS-03 spike uwagi + NEWS-04 Δ sentymentu).
        # Adapter żyje przez całą pętlę (live/backtest) → pamięta poprzednie wartości.
        from collections import deque, defaultdict
        self._hist_sent = defaultdict(lambda: deque(maxlen=10))   # poprzednie sentymenty
        self._hist_n = defaultdict(lambda: deque(maxlen=20))      # poprzednia liczba nagłówków
        # NEWS-06 novelty: znormalizowane nagłówki widziane w POPRZEDNICH pobraniach —
        # powtórzony news jest już wyceniony (original-vs-amplified, research 2026).
        self._widziane = defaultdict(lambda: deque(maxlen=300))   # klucze nagłówków per symbol

    # ── Klasyfikacja słownikowa (offline, deterministyczna) ───────────────────

    @staticmethod
    def _sentyment_slownikowy(naglowki: List[str],
                              wagi_zrodel: "Optional[List[float]]" = None) -> dict:
        """
        Liczy sentyment z leksykonu: (bycze - niedźwiedzie) / (bycze + niedźwiedzie).
        Pewność rośnie z liczbą trafień (saturacja). Zero trafień → 0.0 neutralny.

        wagi_zrodel (NEWS-05, source credibility): waga wiarygodności per nagłówek —
        trafienie z CoinDesk (1.0) liczy się mocniej niż z nieznanego bloga (0.5).
        None → wszystkie 1.0 (wstecznie kompatybilne).
        """
        score_byk = 0.0
        score_niedz = 0.0
        trafienia = 0
        for i, naglowek in enumerate(naglowki):
            w_zrodla = wagi_zrodel[i] if wagi_zrodel and i < len(wagi_zrodel) else 1.0
            tekst = naglowek.lower()
            for slowo, waga in SLOWA_BYCZE.items():
                if _slowo_wystepuje(slowo, tekst):
                    score_byk += waga * w_zrodla
                    trafienia += 1
            for slowo, waga in SLOWA_NIEDZWIEDZIE.items():
                if _slowo_wystepuje(slowo, tekst):
                    score_niedz += waga * w_zrodla
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
            # NEWS-05 (source credibility): jeśli fetcher zna źródła — bierz z wagami.
            if hasattr(self._fetcher, "pobierz_z_metadanymi"):
                meta = list(self._fetcher.pobierz_z_metadanymi(symbol) or [])
                naglowki = [m["tytul"] for m in meta]
                wagi_zrodel = [float(m.get("waga", 1.0)) for m in meta]
            else:
                naglowki = list(self._fetcher(symbol) or [])
                wagi_zrodel = [1.0] * len(naglowki)
        except Exception as e:
            logger.warning(f"[Adapter:NewsLLM] fetcher padł dla {symbol}: {e}")
            return {"NEWS_SENTYMENT": None, "NEWS_PEWNOSC": None, "NEWS_N": 0}

        if not naglowki:
            return {"NEWS_SENTYMENT": None, "NEWS_PEWNOSC": None, "NEWS_N": 0}

        wiarygodnosc = round(sum(wagi_zrodel) / len(wagi_zrodel), 4)

        # NEWS-06 novelty (liczone WZGLĘDEM przeszłości, przed dopisaniem bieżących):
        # frakcja nagłówków NIEwidzianych wcześniej. 1.0 = wszystko świeże;
        # 0.0 = wszystko przeżute (już wycenione przez rynek) → tłumimy pewność.
        from imperium.akwedukty.news_fetcher import _normalizuj
        widziane = self._widziane[symbol]
        klucze = [_normalizuj(t) for t in naglowki]
        nowe = sum(1 for k in klucze if k and k not in widziane)
        novelty = round(nowe / len(klucze), 4) if klucze else 1.0
        for k in klucze:
            if k:
                widziane.append(k)

        wynik = None
        if self.uzyj_llm:
            wynik = self._sentyment_llm(naglowki)
        if wynik is None:
            wynik = self._sentyment_slownikowy(naglowki, wagi_zrodel=wagi_zrodel)
        # NEWS-05: pewność × średnia wiarygodność źródeł (blogi ważą mniej).
        # NEWS-06: pewność × (0.5 + 0.5·novelty) — całkiem przeżuty feed waży o połowę
        # mniej (stary news już w cenie), całkiem świeży bez kary.
        wynik = dict(wynik)
        wynik["pewnosc"] = round(wynik["pewnosc"] * wiarygodnosc * (0.5 + 0.5 * novelty), 4)

        # NEWS-02: taksonomia zdarzeń (kierunek per typ — deterministyczna, zawsze liczona)
        zdarz = _klasyfikuj_zdarzenia(naglowki)
        kier = zdarz["kierunek"] if zdarz["typ"] != "BRAK" else None

        sent = wynik["sentyment"]
        n = len(naglowki)

        # NEWS-04: Δ sentymentu = bieżący − średnia z historii (momentum informacyjny).
        # Liczone WZGLĘDEM przeszłości (przed dopisaniem bieżącego). Brak historii → None.
        hist_s = self._hist_sent[symbol]
        delta = round(sent - (sum(hist_s) / len(hist_s)), 4) if hist_s else None

        # NEWS-03: spike uwagi = bieżąca liczba nagłówków / średnia historyczna (≥1 = normalnie).
        hist_n = self._hist_n[symbol]
        srednia_n = (sum(hist_n) / len(hist_n)) if hist_n else 0.0
        spike = round(n / srednia_n, 4) if srednia_n > 0 else None

        # dopisz bieżące do historii (po obliczeniu Δ/spike względem przeszłości)
        hist_s.append(sent)
        hist_n.append(n)

        return {
            "NEWS_SENTYMENT": sent,
            "NEWS_PEWNOSC": wynik["pewnosc"],
            "NEWS_N": n,
            "NEWS_EVENT_KIERUNEK": kier,
            "NEWS_EVENT_TYP": zdarz["typ"] if kier is not None else None,
            "NEWS_EVENT_PEWNOSC": zdarz["pewnosc"] if kier is not None else None,
            "NEWS_SENTYMENT_DELTA": delta,
            "NEWS_ATTENTION_SPIKE": spike,
            "NEWS_WIARYGODNOSC": wiarygodnosc,
            "NEWS_NOVELTY": novelty,
        }
