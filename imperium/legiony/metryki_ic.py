"""
W-369..371: Information Coefficient, breadth i IR (Grinold & Kahn Fundamental Law).

IC_t(h) = Spearman_rank_corr(sygnał_neuronu_t, zwrot_{t+h})
IR = IC_śr / σ_IC * √breadth (Full Fundamental Law)
Breadth = liczba niezależnych klastrów ONC

Implementacja pure-numpy (scipy/sklearn niedostępne).
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Pomocnicze: Spearman
# ---------------------------------------------------------------------------

def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (pure numpy)."""
    def _rank(a: np.ndarray) -> np.ndarray:
        order = np.argsort(a)
        r = np.empty_like(a, dtype=float)
        r[order] = np.arange(1, len(a) + 1, dtype=float)
        # ties: average ranks
        # proste podejście — sortujemy i uśredniamy grupy
        sorted_a = a[order]
        i = 0
        while i < len(sorted_a):
            j = i + 1
            while j < len(sorted_a) and sorted_a[j] == sorted_a[i]:
                j += 1
            avg = (i + 1 + j) / 2.0
            r[order[i:j]] = avg
            i = j
        return r

    rx, ry = _rank(x), _rank(y)
    d = rx - ry
    n = len(d)
    return float(1 - 6 * np.sum(d ** 2) / (n * (n ** 2 - 1)))


# ---------------------------------------------------------------------------
# KolektorIC: zbiera sygnały i zwroty, liczy IC
# ---------------------------------------------------------------------------

class KolektorIC:
    """
    Na każdym kroku:
      - `rejestruj_sygnal(neuron_id, wartosc)` — wartość sygnału ∈ [-1..1]
      - `rejestruj_zwrot(zwrot_t)` — zrealizowany forward return (cena_{t+h}/cena_t - 1)

    Historię sygnałów buforuje z opóźnieniem h kroków, żeby skojarzyć
    sygnał_t z realizowanym_zwrotem_{t+h}.
    """

    def __init__(
        self,
        okno: int = 120,
        horyzonty: Tuple[int, ...] = (1, 5, 21),
        min_probek: int = 20,
    ) -> None:
        self.okno = okno
        self.horyzonty = tuple(sorted(horyzonty))
        self.min_probek = min_probek
        self._max_h = max(self.horyzonty)

        # bufor sygnałów: deque[(krok, {neuron_id: wartosc})]
        self._bufor_sygnalow: deque = deque(maxlen=okno + self._max_h + 1)
        # bufor zwrotów na dany krok: deque[(krok, zwrot)]
        self._bufor_zwrotow: deque = deque(maxlen=okno + self._max_h + 1)
        self._krok = 0

    # ------------------------------------------------------------------
    def rejestruj_sygnal(self, sygnaly: Dict[str, float]) -> None:
        """Rejestruj mapę neuron_id→wartość sygnału dla bieżącego kroku."""
        self._bufor_sygnalow.append((self._krok, dict(sygnaly)))

    def rejestruj_zwrot(self, zwrot: float) -> None:
        """Rejestruj forward return dla bieżącego kroku."""
        self._bufor_zwrotow.append((self._krok, float(zwrot)))
        self._krok += 1

    # ------------------------------------------------------------------
    def _para_sygnal_zwrot(self, h: int,
                           tylko_glosy: bool = False) -> Dict[str, Tuple[List[float], List[float]]]:
        """
        Dla horyzontu h: łącz sygnał na kroku t z zwrotem na kroku t+h.
        Zwraca {neuron_id: ([sygnały_t], [zwroty_{t+h}])}.

        tylko_glosy=True → pomija bary gdzie sygnał==0 (neuron abstynował). To liczy
        IC WARUNKOWY: „gdy neuron GŁOSUJE, czy trafia?" — usuwa inflację Spearmana od
        tysięcy zerowych remisów (Prawo XVI, poprawka pomiaru 2026-07-01).
        """
        zwroty = {k: v for k, v in self._bufor_zwrotow}
        wynik: Dict[str, Tuple[List[float], List[float]]] = {}
        for krok, mapa in self._bufor_sygnalow:
            krok_h = krok + h
            if krok_h not in zwroty:
                continue
            r = zwroty[krok_h]
            for nid, s in mapa.items():
                if tylko_glosy and abs(s) < 1e-12:
                    continue   # neuron nie głosował na tym barze — pomiń
                if nid not in wynik:
                    wynik[nid] = ([], [])
                wynik[nid][0].append(s)
                wynik[nid][1].append(r)
        return wynik

    # ------------------------------------------------------------------
    def ic(self, h: Optional[int] = None, tylko_glosy: bool = False) -> Dict[str, Dict[int, float]]:
        """
        Oblicz IC per neuron, per horyzont.

        Zwraca: {neuron_id: {h: IC_value}} lub {neuron_id: {h: None}} gdy brak danych.
        Gdy h podane — tylko dla tego horyzontu.
        tylko_glosy=True → IC warunkowy (tylko bary z niezerowym głosem) — wiarygodniejszy
        dla rzadko głosujących neuronów (bez inflacji od remisów zer).
        """
        horyzonty = (h,) if h is not None else self.horyzonty
        neurony: Dict[str, Dict[int, float]] = {}

        for hz in horyzonty:
            pary = self._para_sygnal_zwrot(hz, tylko_glosy=tylko_glosy)
            for nid, (sigs, rets) in pary.items():
                if nid not in neurony:
                    neurony[nid] = {}
                if len(sigs) < self.min_probek:
                    neurony[nid][hz] = float("nan")
                    continue
                x = np.array(sigs, dtype=float)
                y = np.array(rets, dtype=float)
                # pomiń stałe série (zerowa wariancja)
                if np.std(x) < 1e-10 or np.std(y) < 1e-10:
                    neurony[nid][hz] = float("nan")
                    continue
                neurony[nid][hz] = round(_spearman(x, y), 4)

        return neurony

    # ------------------------------------------------------------------
    def ic_srednie(self, tylko_glosy: bool = False) -> Dict[str, float]:
        """IC uśrednione po horyzontach (ignoruje NaN). tylko_glosy → IC warunkowy."""
        wyniki = {}
        for nid, hz_dict in self.ic(tylko_glosy=tylko_glosy).items():
            wartosci = [v for v in hz_dict.values() if not np.isnan(v)]
            wyniki[nid] = round(float(np.mean(wartosci)), 4) if wartosci else float("nan")
        return wyniki


# ---------------------------------------------------------------------------
# prawo_fundamentalne: IR = IC·√breadth
# ---------------------------------------------------------------------------

def prawo_fundamentalne(
    ic_srednie: Dict[str, float],
    breadth: Optional[int] = None,
    korelacje_denoised: Optional[Dict[Tuple[str, str], float]] = None,
) -> Dict:
    """
    Fundamental Law of Active Management (Grinold & Kahn).

    IR = IC_śr · √breadth

    breadth: liczba niezależnych zakładów — albo podana wprost,
             albo wyliczona z ONC na macierzy korelacji.

    Jeśli breadth=None i brak korelacje_denoised → breadth = len(neurony) (pesymistyczne).

    Zwraca raport: IC_zbiorowy, breadth, IR, diagnoza.
    """
    neurony_valid = {k: v for k, v in ic_srednie.items() if not np.isnan(v)}

    if not neurony_valid:
        return {
            "ic_zbiorowy": float("nan"),
            "breadth": 0,
            "ir": float("nan"),
            "diagnoza": "BRAK_IC — za mało danych do obliczenia IC",
            "neurony": {},
        }

    ic_zbiorowy = float(np.mean(list(neurony_valid.values())))

    # --- wyznacz breadth ---
    if breadth is None:
        if korelacje_denoised:
            try:
                from imperium.legiony.denoising_macierzy import klastruj_onc
                klucze = list(neurony_valid.keys())
                n = len(klucze)
                # Zbuduj macierz korelacji z dostępnych par
                corr = np.eye(n)
                idx = {k: i for i, k in enumerate(klucze)}
                for (a, b), v in korelacje_denoised.items():
                    if a in idx and b in idx:
                        corr[idx[a], idx[b]] = v
                        corr[idx[b], idx[a]] = v
                res = klastruj_onc(corr, klucze)
                breadth = len(res["klastry"])
            except Exception:
                breadth = len(neurony_valid)
        else:
            breadth = len(neurony_valid)

    ir = round(ic_zbiorowy * (breadth ** 0.5), 4)

    # diagnoza
    if abs(ic_zbiorowy) < 0.02:
        diagnoza = "IC_NISKI — rój ma słabą przewagę informacyjną (IC < 0.02)"
    elif breadth < 4:
        diagnoza = "BREADTH_NISKI — za mało niezależnych sygnałów (breadth < 4)"
    elif abs(ir) >= 0.5:
        diagnoza = "IR_DOBRY — silna, zdywersyfikowana przewaga (|IR| ≥ 0.5)"
    elif abs(ir) >= 0.2:
        diagnoza = "IR_SREDNI — umiarkowana przewaga (0.2 ≤ |IR| < 0.5)"
    else:
        diagnoza = "IR_SLABY — słaba przewaga łączna (|IR| < 0.2)"

    return {
        "ic_zbiorowy": round(ic_zbiorowy, 4),
        "breadth": breadth,
        "ir": ir,
        "diagnoza": diagnoza,
        "neurony": {
            k: round(v, 4) for k, v in sorted(
                neurony_valid.items(), key=lambda x: abs(x[1]), reverse=True
            )
        },
    }
