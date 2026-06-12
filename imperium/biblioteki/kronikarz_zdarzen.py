"""
📜💎 KRONIKARZ ZDARZEŃ (Augur Imperium) — unikat W-289 (v2 rozbudowany 2026-06-10).

WIZJA CEZARA: system zna zdarzenia fundamentalne (FED, halvingi, krachy, ETF...),
automatycznie dopasowuje historyczne analogie do sytuacji live, podaje PROCENTOWE
prawdopodobieństwa jako głos w roju — z dokładnym czasem/dniem i znajomością PRZYSZŁOŚCI.
(Realizuje ROADMAP Faza 3 "Macierz zdarzeń historycznych" + W-039 Kroniki Bitew.)

TRZY WYMIARY (v2):
  1. PER-PARA — zdarzenie może dotyczyć konkretnych par (ETH ETF → tylko ETH) albo
     być makro/BTC-dominacyjne (None = wszystkie). `kontekst(ts, symbol)` filtruje.
  2. KALENDARZ FOMC — ~8 posiedzeń/rok na ZNANYCH datach (też przyszłych 2026):
     • event-study post-FOMC (wysokie n → statystyka mocna),
     • BLACKOUT pre-FOMC — system WIE, że FED jutro → sygnał ostrożności PRZED.
  3. DECAY + SPÓJNOŚĆ — siła głosu maleje z dni_po (waga_zaniku) i rośnie ze
     ZGODNOŚCIĄ historycznych epizodów (wszystkie +→ mocno; rozsypane → słabo).

ŹRÓDŁA (ZPO):
  • FOMC → BTC dryf po posiedzeniu, silniejszy w hossie:
    https://www.sciencedirect.com/science/article/abs/pii/S027553192200099X
  • Halving 2024 +24.55% (synthetic control): https://arxiv.org/pdf/2511.05512
  • Spot ETF dodatni zwrot + spadek vol: https://www.sciencedirect.com/science/article/pii/S106297692500047X

ORYGINALNOŚĆ: literatura = jedna liczba z jednego badania. Nasz augur SAMOKALIBRUJE
się z własnych barów, przyczynowo (zero look-ahead — test wymusza), i mądrzeje z
każdą parą/historią bez zmiany kodu.
"""

import bisect
import logging
from datetime import datetime, timezone
from typing import List, Optional, Set

logger = logging.getLogger("Kronikarz")

_D = 86_400_000  # ms w dobie


def _ts(rok, mies, dzien) -> int:
    return int(datetime(rok, mies, dzien, tzinfo=timezone.utc).timestamp() * 1000)


# ── KATALOG ZDARZEŃ JEDNORAZOWYCH (daty powszechnie znane, UTC) ───────────────
# "pary": None = makro/BTC-dominacja (dotyczy wszystkich); zbiór = tylko te pary.
KATALOG_ZDARZEN: List[dict] = [
    {"typ": "HALVING", "ts": _ts(2016, 7, 9),  "opis": "Halving #2 (12.5 BTC)", "pary": None},
    {"typ": "HALVING", "ts": _ts(2020, 5, 11), "opis": "Halving #3 (6.25 BTC)", "pary": None},
    {"typ": "HALVING", "ts": _ts(2024, 4, 20), "opis": "Halving #4 (3.125 BTC)", "pary": None},
    {"typ": "KRACH",   "ts": _ts(2020, 3, 12), "opis": "COVID Black Thursday (−40%)", "pary": None},
    {"typ": "KRACH",   "ts": _ts(2022, 5, 9),  "opis": "Upadek LUNA/UST", "pary": None},
    {"typ": "KRACH",   "ts": _ts(2022, 11, 8), "opis": "Upadek FTX", "pary": None},
    {"typ": "REGULACJA", "ts": _ts(2021, 5, 19), "opis": "Chiny: zakaz kopania/handlu", "pary": None},
    {"typ": "REGULACJA", "ts": _ts(2021, 9, 24), "opis": "Chiny: pełny ban transakcji", "pary": None},
    {"typ": "ETF",     "ts": _ts(2021, 10, 19), "opis": "BITO — futures ETF (USA)", "pary": {"BTCUSDT"}},
    {"typ": "ETF",     "ts": _ts(2024, 1, 10),  "opis": "Spot BTC ETF approval", "pary": {"BTCUSDT"}},
    {"typ": "ETF",     "ts": _ts(2024, 5, 23),  "opis": "Spot ETH ETF approval", "pary": {"ETHUSDT"}},
    {"typ": "MAKRO",   "ts": _ts(2024, 11, 5),  "opis": "Wybory USA 2024", "pary": None},
]

# ── KALENDARZ FOMC (daty ogłoszenia decyzji, ~19:00 UTC — publicznie znane) ────
# Przeszłe → event-study (wysokie n); 2026 → znane PRZYSZŁE okna (blackout).
_FOMC_DATY = [
    (2020, 1, 29), (2020, 4, 29), (2020, 6, 10), (2020, 7, 29), (2020, 9, 16),
    (2020, 11, 5), (2020, 12, 16),
    (2021, 1, 27), (2021, 3, 17), (2021, 4, 28), (2021, 6, 16), (2021, 7, 28),
    (2021, 9, 22), (2021, 11, 3), (2021, 12, 15),
    (2022, 1, 26), (2022, 3, 16), (2022, 5, 4), (2022, 6, 15), (2022, 7, 27),
    (2022, 9, 21), (2022, 11, 2), (2022, 12, 14),
    (2023, 2, 1), (2023, 3, 22), (2023, 5, 3), (2023, 6, 14), (2023, 7, 26),
    (2023, 9, 20), (2023, 11, 1), (2023, 12, 13),
    (2024, 1, 31), (2024, 3, 20), (2024, 5, 1), (2024, 6, 12), (2024, 7, 31),
    (2024, 9, 18), (2024, 11, 7), (2024, 12, 18),
    (2025, 1, 29), (2025, 3, 19), (2025, 5, 7), (2025, 6, 18), (2025, 7, 30),
    (2025, 9, 17), (2025, 10, 29), (2025, 12, 10),
    (2026, 1, 28), (2026, 3, 18), (2026, 4, 29), (2026, 6, 17), (2026, 7, 29),
    (2026, 9, 16), (2026, 11, 4), (2026, 12, 16),  # PRZYSZŁE — znane okna
]
KALENDARZ_FOMC: List[dict] = [
    {"typ": "FOMC", "ts": _ts(r, m, d) + 19 * 3_600_000,
     "opis": f"FOMC {r}-{m:02d}-{d:02d}", "pary": None}
    for (r, m, d) in _FOMC_DATY
]

# Wszystkie zdarzenia jednorazowe + FOMC (do event-study i live-matchingu)
_WSZYSTKIE = KATALOG_ZDARZEN + KALENDARZ_FOMC


def _dotyczy(z: dict, symbol: str) -> bool:
    """Czy zdarzenie dotyczy danej pary (None=wszystkie; pusty symbol=tak)."""
    pary: Optional[Set[str]] = z.get("pary")
    if pary is None or not symbol:
        return True
    return symbol.upper() in pary


class KronikarzZdarzen:
    """
    Użycie:
        kr = KronikarzZdarzen(bary_dzienne)
        st  = kr.studium("FOMC", ts_teraz)            # statystyki przyczynowe
        ctx = kr.kontekst(ts_teraz, symbol="ETHUSDT") # okno wpływu + blackout
    """

    def __init__(self, bary: List[dict], okno_wplywu_dni: int = 30,
                 horyzont_dni: int = 30, blackout_dni: int = 2):
        """
        bary: pełna historia barów DZIENNYCH (dict z 'timestamp' ms i 'close').
        okno_wplywu_dni: ile dni PO zdarzeniu to "okno wpływu" (live-match).
        horyzont_dni: horyzont forward-zwrotu w studium.
        blackout_dni: ile dni PRZED zdarzeniem zaplanowanym (FOMC) = ostrzeżenie.
        """
        if okno_wplywu_dni < 1 or horyzont_dni < 1 or blackout_dni < 1:
            raise ValueError("okna muszą być ≥ 1 dnia")
        self.okno_wplywu_dni = okno_wplywu_dni
        self.horyzont_dni = horyzont_dni
        self.blackout_dni = blackout_dni
        self._bary = sorted((b for b in bary if b.get("timestamp") is not None),
                            key=lambda b: b["timestamp"])
        self._ts_list = [int(b["timestamp"]) for b in self._bary]

    # ── rdzeń: event-study przyczynowe ───────────────────────────────────────

    def _indeks_baru(self, ts: int, tolerancja_dni: int = 3) -> Optional[int]:
        """
        Indeks pierwszego baru ≥ ts, ale TYLKO jeśli ≤ tolerancja_dni od ts.
        Bez tolerancji zdarzenie spoza pokrycia danych dopasowałoby się do
        pierwszego baru → absurdalny zwrot (Prawo I: brak danych ≠ wymyślone).
        """
        i = bisect.bisect_left(self._ts_list, ts)
        if i >= len(self._ts_list):
            return None
        if self._ts_list[i] - ts > tolerancja_dni * _D:
            return None
        return i

    def studium(self, typ: str, ts_teraz: int, symbol: str = "") -> dict:
        """
        Statystyki forward-zwrotów po zdarzeniach danego typu — PRZYCZYNOWO
        (tylko epizody o horyzoncie domkniętym przed ts_teraz) i per-para.

        Zwraca: n, prob_wzrostu, mediana_pct, srednia_pct, rozrzut_pct,
                zgodne_kierunkowo (bool), horyzont_dni.
        """
        zwroty = []
        granica = ts_teraz - self.horyzont_dni * _D
        for z in _WSZYSTKIE:
            if z["typ"] != typ or z["ts"] > granica or not _dotyczy(z, symbol):
                continue
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
            return {"typ": typ, "n": 0, "prob_wzrostu": None, "mediana_pct": None,
                    "srednia_pct": None, "rozrzut_pct": None,
                    "zgodne_kierunkowo": False, "horyzont_dni": self.horyzont_dni}
        zw = sorted(zwroty)
        n = len(zw)
        mediana = zw[n // 2] if n % 2 else (zw[n // 2 - 1] + zw[n // 2]) / 2
        srednia = sum(zw) / n
        rozrzut = (sum((x - srednia) ** 2 for x in zw) / n) ** 0.5
        dodatnie = sum(1 for x in zw if x > 0)
        return {"typ": typ, "n": n,
                "prob_wzrostu": round(100.0 * dodatnie / n, 1),
                "mediana_pct": round(100.0 * mediana, 2),
                "srednia_pct": round(100.0 * srednia, 2),
                "rozrzut_pct": round(100.0 * rozrzut, 2),
                "zgodne_kierunkowo": dodatnie == n or dodatnie == 0,
                "horyzont_dni": self.horyzont_dni}

    # ── live-matching: okno wpływu (po) + blackout (przed zaplanowanym) ───────

    def kontekst(self, ts_teraz: int, symbol: str = "") -> Optional[dict]:
        """
        Zwraca najistotniejszy kontekst zdarzeniowy na moment ts dla pary symbol:
          • BLACKOUT — zaplanowane FOMC w ciągu ≤ blackout_dni PRZED nami
            (system wie, że FED idzie — ostrzeżenie). Ma PIERWSZEŃSTWO.
          • OKNO WPŁYWU — najświeższe zdarzenie ≤ okno_wplywu_dni PO nas.
        Dorzuca waga_zaniku (1.0 w dniu zdarzenia → 0.0 na krawędzi okna).
        None = cisza augura (Prawo XV — neuron abstynuje).
        """
        # 1. BLACKOUT przed zaplanowanym FOMC
        for z in KALENDARZ_FOMC:
            dni_do = (z["ts"] - ts_teraz) / _D
            if 0 < dni_do <= self.blackout_dni and _dotyczy(z, symbol):
                return {"typ": z["typ"], "opis": z["opis"], "blackout": True,
                        "dni_po": round(-dni_do, 1), "dni_do": round(dni_do, 1),
                        "waga_zaniku": 1.0,
                        "studium": self.studium(z["typ"], ts_teraz, symbol)}
        # 2. OKNO WPŁYWU po zdarzeniu
        kandydat = None
        for z in _WSZYSTKIE:
            dni_po = (ts_teraz - z["ts"]) / _D
            if 0 <= dni_po <= self.okno_wplywu_dni and _dotyczy(z, symbol):
                if kandydat is None or z["ts"] > kandydat["ts"]:
                    kandydat = z
        if kandydat is None:
            return None
        dni_po = (ts_teraz - kandydat["ts"]) / _D
        waga = max(0.0, 1.0 - dni_po / self.okno_wplywu_dni)
        return {"typ": kandydat["typ"], "opis": kandydat["opis"], "blackout": False,
                "dni_po": round(dni_po, 1), "waga_zaniku": round(waga, 3),
                "studium": self.studium(kandydat["typ"], ts_teraz, symbol)}

    def raport_pelny(self, ts_teraz: int, symbol: str = "") -> List[dict]:
        """Studium wszystkich typów na moment ts (tabela dowodowa)."""
        typy = sorted({z["typ"] for z in _WSZYSTKIE})
        return [self.studium(t, ts_teraz, symbol) for t in typy]


class AdapterKronikarz:
    """
    Adapter (mechanizm Dyrygenta) — wstrzykuje kontekst Augura do wskaźników:
      EVENT_TYP, EVENT_DNI_PO, EVENT_N, EVENT_PROB_WZROSTU, EVENT_MEDIANA_PCT,
      EVENT_WAGA (decay), EVENT_ZGODNE (spójność), EVENT_BLACKOUT (przed FOMC).
    Brak kontekstu → klucze nie dodawane (AUG-01 abstynuje, Prawo XV).
    """

    NAZWA = "AdapterKronikarz"

    def __init__(self, bary_dzienne: List[dict], **kw):
        self.kronikarz = KronikarzZdarzen(bary_dzienne, **kw)

    def wzbogac(self, wskazniki: dict, symbol: str = "") -> None:
        ts = wskazniki.get("TIMESTAMP")
        if ts is None:
            return
        ctx = self.kronikarz.kontekst(int(ts), symbol)
        if ctx is None:
            return
        st = ctx["studium"]
        wskazniki["EVENT_TYP"] = ctx["typ"]
        wskazniki["EVENT_DNI_PO"] = ctx["dni_po"]
        wskazniki["EVENT_N"] = st["n"]
        wskazniki["EVENT_PROB_WZROSTU"] = st["prob_wzrostu"]
        wskazniki["EVENT_MEDIANA_PCT"] = st["mediana_pct"]
        wskazniki["EVENT_WAGA"] = ctx["waga_zaniku"]
        wskazniki["EVENT_ZGODNE"] = st["zgodne_kierunkowo"]
        wskazniki["EVENT_BLACKOUT"] = ctx["blackout"]
        if ctx["blackout"]:
            wskazniki["EVENT_DNI_DO"] = ctx["dni_do"]
