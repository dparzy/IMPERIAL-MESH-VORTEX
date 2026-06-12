"""
🌊 DRIFT ADAPTER — antycypacyjna adaptacja do zmiany reżimu (W-296).

Inspiracja: DDG-DA (Microsoft Qlib, NeurIPS 2021, Liu et al.),
github.com/microsoft/qlib/tree/main/examples/benchmarks_dynamic/DDG-DA.

DLA NOWICJUSZA: WAGI_REZIMU w Legatus są REAKTYWNE — gdy reżim już się zmienił,
dopiero wtedy wagi się dostosowują. Drift Adapter jest ANTYCYPACYJNY:
monitoruje STABILNOŚĆ REŻIMU (jak często zmienia się klasyfikacja w ostatnich
barach?) i gdy wykryje narastającą niestabilność (sygnał nadchodzącej zmiany),
PRE-PRZESUWUJE wagi kategorii neuronów zanim pełna zmiana nastąpi.
Efekt: mniej strat na przejściach reżimowych.

Dwa sygnały dryfu:
1. ENTROPIA REŻIMU: H = -Σ p_i·log₂(p_i) w oknie n barów.
   Wysoka entropia = reżim niestabilny. → defensywna korekta wag.
2. MOMENTUM REŻIMU: porównaj rozkład 1. vs 2. połowy okna.
   Czy rynek ZMIERZA ku trendowi czy ku range? → korekta kierunkowa.

Integracja z backtest.py:
    adapter = DriftAdapter(okno=20)
    adapter.dodaj_rezim(aktualny_rezim)      # co bar, po klasyfikuj_rezim()
    sygnal = adapter.skanuj()
    if sygnal.czy_drift:
        wagi_adj = adapter.koryguj_wagi(WAGI_REZIMU, aktualny_rezim, sygnal)
        legatus.ustaw_wagi_rezimu(wagi_adj)
"""

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional


# Progi
PROG_DRYFU = 0.55       # entropia_norm > tego → sygnał dryfu (aktywuj korektę)
PROG_MOMENTUM = 0.15    # delta frakcji reżimu między połówkami > tego → kierunkowy drift
OKNO_DRYFU = 20         # domyślne okno historii reżimów
MAX_SILA_KOREKTY = 0.30  # max ±30% korekty wag (agresja ograniczona)


@dataclass
class SygnalDryfu:
    """Aktualny sygnał dryfu reżimu."""
    entropia: float             # H ∈ [0, log₂(N)]
    entropia_norm: float        # ∈ [0, 1]
    momentum_rezim: str         # "TRENDING" | "RANGING" | "NEUTRAL"
    wspolczynnik_dryfu: float   # ∈ [0, 1] — kombinacja entropii i tempa zmian
    czy_drift: bool             # True gdy entropia_norm > PROG_DRYFU
    zalecane_korekty: Dict[str, float]  # mnożniki dla kategorii neuronów


class DriftAdapter:
    """
    Adapter dryfu reżimu — antycypacyjna korekta wag WAGI_REZIMU.

    Nie modyfikuje WAGI_REZIMU w miejscu — zwraca nową strukturę wag
    z zastosowanymi mnożnikami kategorii. Legatus dostaje poprawione wagi
    przez ustaw_wagi_rezimu() lub bezpośrednio.
    """

    def __init__(self, okno: int = OKNO_DRYFU):
        if okno < 3:
            raise ValueError("okno musi być ≥ 3")
        self.okno = okno
        self._historia: List[str] = []

    def dodaj_rezim(self, rezim: str) -> None:
        """Rejestruje aktualną klasyfikację reżimu. Wywołaj co bar."""
        self._historia.append(rezim)
        if len(self._historia) > self.okno:
            self._historia.pop(0)

    def skanuj(self) -> SygnalDryfu:
        """
        Oblicza aktualny sygnał dryfu z historii reżimów.
        Wywołaj po dodaj_rezim() na każdym barze.
        """
        h = self._historia
        if len(h) < 3:
            return SygnalDryfu(
                entropia=0.0, entropia_norm=0.0,
                momentum_rezim="NEUTRAL", wspolczynnik_dryfu=0.0,
                czy_drift=False, zalecane_korekty={},
            )

        # 1. Entropia Shannona rozkładu reżimów w oknie
        licznik = Counter(h)
        n = len(h)
        entropia = -sum((c / n) * math.log2(c / n) for c in licznik.values() if c > 0)
        n_uniq = len(licznik)
        max_ent = math.log2(n_uniq) if n_uniq > 1 else 1.0
        entropia_norm = entropia / max_ent if max_ent > 0 else 0.0

        # 2. Momentum: rozkład 1. vs 2. połowy okna
        pol = len(h) // 2
        stara = Counter(h[:pol])
        nowa = Counter(h[pol:])
        momentum = _oblicz_momentum(stara, nowa, pol)

        # 3. Współczynnik dryfu (50% entropia + 50% tempo przejść)
        n_przejsc = sum(1 for i in range(1, len(h)) if h[i] != h[i - 1])
        tempo = n_przejsc / max(len(h) - 1, 1)
        wspolczynnik = round(entropia_norm * 0.5 + tempo * 0.5, 4)

        czy_drift = entropia_norm > PROG_DRYFU
        korekty = _korekty_wag(czy_drift, momentum, wspolczynnik) if czy_drift else {}

        return SygnalDryfu(
            entropia=round(entropia, 4),
            entropia_norm=round(entropia_norm, 4),
            momentum_rezim=momentum,
            wspolczynnik_dryfu=wspolczynnik,
            czy_drift=czy_drift,
            zalecane_korekty=korekty,
        )

    def koryguj_wagi(
        self,
        wagi_rezimu: Dict[str, Dict[str, float]],
        aktualny_rezim: str,
        sygnal: Optional[SygnalDryfu] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Zwraca SKORYGOWANĄ kopię WAGI_REZIMU z uwzględnieniem dryfu.
        NIE modyfikuje oryginału — zawsze zwraca nową strukturę.

        Korekty dotyczą wyłącznie aktywnego reżimu + sąsiednich wag
        (nie cały słownik — reszta reżimów bez zmian).
        """
        if sygnal is None:
            sygnal = self.skanuj()
        if not sygnal.czy_drift or not sygnal.zalecane_korekty:
            return wagi_rezimu  # brak dryfu → bez korekty, bez kopii

        wynik: Dict[str, Dict[str, float]] = {}
        for rezim_klucz, mapa in wagi_rezimu.items():
            nowa_mapa: Dict[str, float] = {}
            for kat, waga in mapa.items():
                if kat == "_default":
                    nowa_mapa[kat] = waga
                    continue
                mnoz = sygnal.zalecane_korekty.get(kat, 1.0)
                nowa_mapa[kat] = round(waga * mnoz, 6)
            wynik[rezim_klucz] = nowa_mapa
        return wynik


# ─── helpers ──────────────────────────────────────────────────────────────────

def _oblicz_momentum(stara: Counter, nowa: Counter, pol: int) -> str:
    """Wykrywa czy rynek zmierza ku trendowi, range, czy jest neutralny."""
    trend_kluczy = {"TRENDING_UP", "TRENDING_DOWN", "TREND_STRONG", "TREND_WEAK"}
    trend_stara = sum(stara.get(k, 0) for k in trend_kluczy)
    trend_nowa = sum(nowa.get(k, 0) for k in trend_kluczy)
    range_stara = stara.get("RANGING", 0)
    range_nowa = nowa.get("RANGING", 0)

    pol_max = max(pol, 1)
    delta_trend = (trend_nowa - trend_stara) / pol_max
    delta_range = (range_nowa - range_stara) / pol_max

    if delta_trend > PROG_MOMENTUM:
        return "TRENDING"
    if delta_range > PROG_MOMENTUM:
        return "RANGING"
    return "NEUTRAL"


def _korekty_wag(
    czy_drift: bool,
    momentum: str,
    wspolczynnik: float,
) -> Dict[str, float]:
    """
    Mnożniki kategorii neuronów na czas dryfu.
    Im wyższy współczynnik dryfu, tym silniejsza korekta (max MAX_SILA_KOREKTY).
    """
    if not czy_drift:
        return {}

    sila = min(wspolczynnik, MAX_SILA_KOREKTY)

    if momentum == "RANGING":
        # Rynek zmierza ku range → trendy tracą, structure/value zyska
        return {
            "M": round(1.0 - sila, 6),      # Momentum w dół
            "T": round(1.0 - sila, 6),      # Trend w dół
            "V": round(1.0 + sila * 0.5, 6),  # Volatility (range) w górę
            "S": round(1.0 + sila, 6),      # Structure (SMC) w górę
            "R": round(1.0 + sila * 0.5, 6),  # Regime w górę
        }
    if momentum == "TRENDING":
        # Rynek zmierza ku trendowi → range/structure tracą, trend zyska
        return {
            "M": round(1.0 + sila, 6),
            "T": round(1.0 + sila, 6),
            "V": round(1.0 - sila * 0.5, 6),
            "S": round(1.0 - sila * 0.3, 6),
            "R": round(1.0 + sila * 0.5, 6),
        }
    # NEUTRAL drift: ogólna defensywa — minimalna korekta
    return {
        "M": round(1.0 - sila * 0.4, 6),
        "T": round(1.0 - sila * 0.4, 6),
        "R": round(1.0 + sila * 0.3, 6),
    }
