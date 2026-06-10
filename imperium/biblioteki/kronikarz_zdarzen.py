"""
📜💎 KRONIKARZ ZDARZEŃ (Augur Imperium) — unikat W-289.

WIZJA CEZARA (2026-06-10): system ma znać zdarzenia fundamentalne (FED, halvingi,
krachy, ETF...), automatycznie dopasowywać historyczne analogie do sytuacji live
i podawać PROCENTOWE prawdopodobieństwa — jako głos w roju.
(Realizuje ROADMAP Faza 3 "Macierz zdarzeń historycznych" + W-039 Kroniki Bitew.)

ŹRÓDŁA NAUKOWE (ZPO):
  • FOMC → BTC: dryf cenowy przez kilka dni PO posiedzeniu, silniejszy w hossie
    (https://www.sciencedirect.com/science/article/abs/pii/S027553192200099X)
  • Halving 2024: +24.55% vs syntetyczny BTC po 3 mies. (synthetic control,
    https://arxiv.org/pdf/2511.05512)
  • Spot ETF: dodatni wpływ na zwroty, spadek zmienności
    (https://www.sciencedirect.com/science/article/pii/S106297692500047X)

ORYGINALNOŚĆ (nasz twist — "samokalibrujący się augur"):
  Literatura podaje JEDNĄ liczbę z jednego badania. Kronikarz liczy statystyki
  KAŻDEGO TYPU zdarzenia Z NASZYCH WŁASNYCH BARÓW (event-study: zwroty forward
  po zdarzeniu) — i robi to PRZYCZYNOWO: pytany o moment t, używa WYŁĄCZNIE
  zdarzeń zakończonych przed t (zero look-ahead; test to wymusza). Im więcej
  danych dostarczy Cezar, tym mądrzejszy augur — bez zmiany kodu.

KATALOG: powszechnie znane, weryfikowalne daty (UTC). Rozszerzanie = dopisanie
wiersza. Typy: HALVING, ETF, KRACH, REGULACJA, MAKRO.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

logger = logging.getLogger("Kronikarz")

_D = 86_400_000  # ms w dobie


def _ts(rok, mies, dzien) -> int:
    return int(datetime(rok, mies, dzien, tzinfo=timezone.utc).timestamp() * 1000)


# ── KATALOG ZDARZEŃ FUNDAMENTALNYCH (daty powszechnie znane, UTC) ─────────────
KATALOG_ZDARZEN: List[dict] = [
    {"typ": "HALVING", "ts": _ts(2016, 7, 9),  "opis": "Halving #2 (12.5 BTC)"},
    {"typ": "HALVING", "ts": _ts(2020, 5, 11), "opis": "Halving #3 (6.25 BTC)"},
    {"typ": "HALVING", "ts": _ts(2024, 4, 20), "opis": "Halving #4 (3.125 BTC)"},
    {"typ": "KRACH",   "ts": _ts(2020, 3, 12), "opis": "COVID Black Thursday (−40%)"},
    {"typ": "KRACH",   "ts": _ts(2022, 5, 9),  "opis": "Upadek LUNA/UST"},
    {"typ": "KRACH",   "ts": _ts(2022, 11, 8), "opis": "Upadek FTX"},
    {"typ": "REGULACJA", "ts": _ts(2021, 5, 19), "opis": "Chiny: zakaz kopania/handlu"},
    {"typ": "REGULACJA", "ts": _ts(2021, 9, 24), "opis": "Chiny: pełny ban transakcji"},
    {"typ": "ETF",     "ts": _ts(2021, 10, 19), "opis": "BITO — pierwszy futures ETF (USA)"},
    {"typ": "ETF",     "ts": _ts(2024, 1, 10),  "opis": "Spot BTC ETF approval (SEC)"},
    {"typ": "ETF",     "ts": _ts(2024, 5, 23),  "opis": "Spot ETH ETF approval (SEC)"},
    {"typ": "MAKRO",   "ts": _ts(2024, 11, 5),  "opis": "Wybory USA 2024"},
]


class KronikarzZdarzen:
    """
    Użycie:
        kr = KronikarzZdarzen(bary_dzienne)         # pełna historia 1D
        st = kr.studium("HALVING", ts_teraz)        # statystyki TYLKO sprzed ts
        ctx = kr.kontekst(ts_teraz)                 # czy jesteśmy w oknie wpływu?
    """

    def __init__(self, bary: List[dict], okno_wplywu_dni: int = 30,
                 horyzont_dni: int = 30):
        """
        bary: pełna historia barów DZIENNYCH (dict z 'timestamp' ms i 'close').
        okno_wplywu_dni: ile dni PO zdarzeniu uznajemy za "okno wpływu" (live-match).
        horyzont_dni: horyzont forward-zwrotu w studium (close[t+h]/close[t]−1).
        """
        if okno_wplywu_dni < 1 or horyzont_dni < 1:
            raise ValueError("okna muszą być ≥ 1 dnia")
        self.okno_wplywu_dni = okno_wplywu_dni
        self.horyzont_dni = horyzont_dni
        self._bary = sorted((b for b in bary if b.get("timestamp") is not None),
                            key=lambda b: b["timestamp"])
        self._ts_list = [int(b["timestamp"]) for b in self._bary]

    # ── rdzeń: event-study przyczynowe ───────────────────────────────────────

    def _indeks_baru(self, ts: int, tolerancja_dni: int = 3) -> Optional[int]:
        """
        Indeks pierwszego baru o timestamp ≥ ts — ale TYLKO jeśli bar leży
        ≤ tolerancja_dni od ts. Bez tolerancji zdarzenie SPOZA pokrycia danych
        (np. halving 2016 przy barach od 2024) dopasowałoby się do pierwszego
        dostępnego baru i policzyło absurdalny zwrot (bug złapany testem
        2026-06-10 — Prawo I: brak danych ≠ wymyślone dane).
        """
        import bisect
        i = bisect.bisect_left(self._ts_list, ts)
        if i >= len(self._ts_list):
            return None
        if self._ts_list[i] - ts > tolerancja_dni * _D:
            return None
        return i

    def studium(self, typ: str, ts_teraz: int) -> dict:
        """
        Statystyki forward-zwrotów po zdarzeniach danego typu — PRZYCZYNOWO:
        tylko zdarzenia, których pełny horyzont zakończył się PRZED ts_teraz.

        Zwraca: n, prob_wzrostu (0–100%), mediana_pct, srednia_pct, horyzont_dni.
        Prawo I: liczone z barów; n małe → raportujemy n, nie udajemy pewności.
        """
        zwroty = []
        granica = ts_teraz - self.horyzont_dni * _D
        for z in KATALOG_ZDARZEN:
            if z["typ"] != typ or z["ts"] > granica:
                continue  # przyszłe lub niedomknięte horyzontem — wykluczone
            i0 = self._indeks_baru(z["ts"])
            if i0 is None:
                continue
            ih = self._indeks_baru(z["ts"] + self.horyzont_dni * _D)
            if ih is None or ih >= len(self._bary):
                continue
            c0 = float(self._bary[i0]["close"])
            ch = float(self._bary[ih]["close"])
            if c0 > 0:
                zwroty.append((ch - c0) / c0)
        if not zwroty:
            return {"typ": typ, "n": 0, "prob_wzrostu": None,
                    "mediana_pct": None, "srednia_pct": None,
                    "horyzont_dni": self.horyzont_dni}
        zw = sorted(zwroty)
        n = len(zw)
        mediana = zw[n // 2] if n % 2 else (zw[n // 2 - 1] + zw[n // 2]) / 2
        return {"typ": typ, "n": n,
                "prob_wzrostu": round(100.0 * sum(1 for x in zw if x > 0) / n, 1),
                "mediana_pct": round(100.0 * mediana, 2),
                "srednia_pct": round(100.0 * sum(zw) / n, 2),
                "horyzont_dni": self.horyzont_dni}

    # ── live-matching: czy TERAZ jesteśmy w oknie wpływu? ────────────────────

    def kontekst(self, ts_teraz: int) -> Optional[dict]:
        """
        Najświeższe zdarzenie z katalogu, od którego minęło ≤ okno_wplywu_dni.
        Zwraca dict {typ, opis, dni_po, studium:{...}} lub None (cisza augura).
        Studium liczone przyczynowo względem ts_teraz (bieżące zdarzenie NIE
        zasila własnych statystyk — patrzy tylko na wcześniejsze epizody typu).
        """
        kandydat = None
        for z in KATALOG_ZDARZEN:
            dni_po = (ts_teraz - z["ts"]) / _D
            if 0 <= dni_po <= self.okno_wplywu_dni:
                if kandydat is None or z["ts"] > kandydat["ts"]:
                    kandydat = z
        if kandydat is None:
            return None
        return {"typ": kandydat["typ"], "opis": kandydat["opis"],
                "dni_po": round((ts_teraz - kandydat["ts"]) / _D, 1),
                "studium": self.studium(kandydat["typ"], ts_teraz)}

    def raport_pelny(self, ts_teraz: int) -> List[dict]:
        """Studium wszystkich typów na moment ts (tabela dowodowa dla Cezara)."""
        typy = sorted({z["typ"] for z in KATALOG_ZDARZEN})
        return [self.studium(t, ts_teraz) for t in typy]


class AdapterKronikarz:
    """
    Adapter (mechanizm Dyrygenta) — wstrzykuje kontekst Augura do wskaźników:
      EVENT_TYP, EVENT_DNI_PO, EVENT_N, EVENT_PROB_WZROSTU, EVENT_MEDIANA_PCT.
    Brak okna wpływu → klucze nie są dodawane (neuron AUG-01 abstynuje, Prawo XV).
    """

    def __init__(self, bary_dzienne: List[dict], **kw):
        self.kronikarz = KronikarzZdarzen(bary_dzienne, **kw)

    NAZWA = "AdapterKronikarz"

    def wzbogac(self, wskazniki: dict, symbol: str = "") -> None:
        ts = wskazniki.get("TIMESTAMP")
        if ts is None:
            return
        ctx = self.kronikarz.kontekst(int(ts))
        if ctx is None:
            return
        st = ctx["studium"]
        wskazniki["EVENT_TYP"] = ctx["typ"]
        wskazniki["EVENT_DNI_PO"] = ctx["dni_po"]
        wskazniki["EVENT_N"] = st["n"]
        wskazniki["EVENT_PROB_WZROSTU"] = st["prob_wzrostu"]
        wskazniki["EVENT_MEDIANA_PCT"] = st["mediana_pct"]
