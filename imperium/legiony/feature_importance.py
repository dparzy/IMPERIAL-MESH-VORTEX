"""
W-355 | Feature Importance: MDA + SFI (López de Prado, AFML Ch. 8).

DLA NOWICJUSZA: Przy 78 neuronach NIE WIEMY które faktycznie przewidują zysk,
a które są martwymi głosami. Intuicja "ten wskaźnik jest dobry" to opinia — nie pomiar.
LdP: "Backtesting is not a research tool. Feature importance is."

Dwie metody bezszkieletowe (zero scikit-learn):

MDA — Mean Decrease Accuracy (permutacyjna ważność cech):
  1. Oblicz bazową accuracy modelu (Legatus + historia wyników)
  2. Dla każdego neuronu i: potasuj jego sygnały w czasie
  3. Importance(i) = (base_accuracy − shuffled_accuracy)
  • Duży spadek → neuron jest niezbędny (usuń go → system głupieje)
  • Brak spadku → neuron redundantny lub martwy

SFI — Single Feature Importance (izolowana ważność):
  Dla każdego neuronu: jaka jest jego WŁASNA kierunkowa accuracy, gdy działa SAM?
  Odporna na substitution effects (MDI/MDA mogą rozdzielić ważność między
  skorelowane neurony — SFI nie).

Użycie (po sesji backtestowej lub live z historią):
    from imperium.legiony.feature_importance import raport_waznosci

    raport = raport_waznosci(historia_sygnalow, historia_wynikow)
    for w in raport.rankowanie:
        print(w)

Gdzie:
  historia_sygnalow: List[Dict[str, str]]  — [{klucz_neuronu: "LONG"/"SHORT"/"NEUTRAL"}, ...]
  historia_wynikow:  List[int]             — [+1, -1, +1, ...] (1=cena w górę, -1=w dół)

Prawo XVI: redundancja mierzona (MDA), nie zgadywana.
Prawo XV: martwy głos = neuron z zerową ważnością MDA i zerową SFI.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("FeatureImportance")

# Minimalna liczba obserwacji (bez tego wyniki są szumem)
MIN_OBS = 20


# ─── Typy danych ──────────────────────────────────────────────────────────────

@dataclass
class WaznoscNeuronu:
    """Ważność jednego neuronu z obu metod."""
    klucz: str
    mda: float           # Mean Decrease Accuracy ∈ (-∞, 1] — im wyżej tym ważniejszy
    sfi_long: float      # % poprawnych sygnałów LONG (cena wzrosła po LONG)
    sfi_short: float     # % poprawnych sygnałów SHORT (cena spadła po SHORT)
    sfi_overall: float   # harmoniczy balans: HM(sfi_long, sfi_short)
    n_long: int          # liczba sygnałów LONG w historii
    n_short: int         # liczba sygnałów SHORT w historii
    n_neutral: int       # liczba sygnałów NEUTRAL
    pominiety: bool = False   # True = za mało sygnałów do oceny


@dataclass
class RaportWaznosci:
    """Pełny raport ważności neuronów (wynik raport_waznosci())."""
    n_obserwacji: int
    base_accuracy: float
    rankowanie: List[WaznoscNeuronu]   # posortowane wg MDA malejąco
    martwe_glosy: List[str]            # klucze neuronów z MDA ≤ 0 i SFI ≤ 0.50
    redundantne: List[str]             # klucze neuronów z MDA < threshold i SFI < threshold
    podsumowanie: str

    def __str__(self) -> str:
        linie = [
            "=== RAPORT WAŻNOŚCI NEURONÓW (W-355) ===",
            f"Obserwacji: {self.n_obserwacji} | Base accuracy: {self.base_accuracy:.1%}",
            f"Martwe głosy: {self.martwe_glosy}",
            f"Redundantne: {self.redundantne}",
            "",
            f"{'Klucz':<14} {'MDA':>7} {'SFI':>7} {'L-acc':>7} {'S-acc':>7} {'#L':>5} {'#S':>5}",
            "-" * 60,
        ]
        for w in self.rankowanie:
            flag = " ⚠" if w.klucz in self.martwe_glosy else ""
            linie.append(
                f"{w.klucz:<14} {w.mda:>7.3f} {w.sfi_overall:>7.1%} "
                f"{w.sfi_long:>7.1%} {w.sfi_short:>7.1%} "
                f"{w.n_long:>5} {w.n_short:>5}{flag}"
            )
        return "\n".join(linie)


# ─── SFI — Single Feature Importance ─────────────────────────────────────────

def _sfi_neuronu(
    sygnaly: List[str],
    wyniki: List[int],
) -> Tuple[float, float, int, int, int]:
    """
    Liczy kierunkową accuracy neuronu działającego SAMODZIELNIE.

    sygnaly: ["LONG","NEUTRAL","SHORT", ...] dla jednego neuronu
    wyniki:  [+1,-1,+1,...] — +1=cena wzrosła, -1=cena spadła (w tym samym czasie)

    Zwraca: (sfi_long, sfi_short, n_long, n_short, n_neutral)
    sfi_long  = P(wynik==+1 | sygnal==LONG)
    sfi_short = P(wynik==-1 | sygnal==SHORT)
    """
    tp_long = tp_short = n_long = n_short = n_neutral = 0
    for sig, wynik in zip(sygnaly, wyniki):
        sig_up = sig.upper() if sig else "NEUTRAL"
        if sig_up == "LONG":
            n_long += 1
            if wynik == 1:
                tp_long += 1
        elif sig_up == "SHORT":
            n_short += 1
            if wynik == -1:
                tp_short += 1
        else:
            n_neutral += 1

    sfi_long = tp_long / n_long if n_long > 0 else 0.5
    sfi_short = tp_short / n_short if n_short > 0 else 0.5
    return sfi_long, sfi_short, n_long, n_short, n_neutral


def _harmonic_mean(a: float, b: float) -> float:
    """Średnia harmoniczna dwóch wartości (jak F1 dla precision/recall)."""
    if a + b <= 0:
        return 0.0
    return 2 * a * b / (a + b)


# ─── Głosowanie zagregowane (proxy Legatusa) ─────────────────────────────────

def _accuracy_zagregowana(
    historia_sygnalow: List[Dict[str, str]],
    wyniki: List[int],
    wyklucz_klucz: Optional[str] = None,
    seed: Optional[int] = None,
    potasuj_klucz: Optional[str] = None,
) -> float:
    """
    Liczy accuracy prostego głosowania większościowego po neuronach.

    wyklucz_klucz: pomiń ten neuron (do SFI)
    potasuj_klucz: potasuj sygnały tego neuronu (do MDA)
    """
    if not historia_sygnalow:
        return 0.5

    # Opcjonalne tasowanie (MDA)
    shuffled_vals: Optional[List[str]] = None
    if potasuj_klucz is not None:
        rng = random.Random(seed)
        shuffled_vals = [h.get(potasuj_klucz, "NEUTRAL") for h in historia_sygnalow]
        rng.shuffle(shuffled_vals)

    trafne = 0
    lacznie = 0
    for i, (snap, wynik) in enumerate(zip(historia_sygnalow, wyniki)):
        glosy_long = glosy_short = 0
        for klucz, sig in snap.items():
            if klucz == wyklucz_klucz:
                continue
            if potasuj_klucz and klucz == potasuj_klucz:
                sig = shuffled_vals[i] if shuffled_vals else "NEUTRAL"
            sig_up = (sig or "").upper()
            if sig_up == "LONG":
                glosy_long += 1
            elif sig_up == "SHORT":
                glosy_short += 1

        if glosy_long > glosy_short:
            pred = 1
        elif glosy_short > glosy_long:
            pred = -1
        else:
            continue  # remis = brak decyzji, pomijamy

        lacznie += 1
        if pred == wynik:
            trafne += 1

    return trafne / lacznie if lacznie > 0 else 0.5


# ─── MDA — Mean Decrease Accuracy ────────────────────────────────────────────

def _mda_neuronu(
    klucz: str,
    historia_sygnalow: List[Dict[str, str]],
    wyniki: List[int],
    base_accuracy: float,
    n_permutacji: int = 10,
) -> float:
    """
    MDA dla jednego neuronu: tyle razy tasuj jego sygnały i uśredniaj spadek accuracy.
    Zwraca: base_accuracy − mean(shuffled_accuracy) — im wyżej, tym ważniejszy neuron.
    """
    shuffled_accs = []
    for seed in range(n_permutacji):
        acc = _accuracy_zagregowana(
            historia_sygnalow, wyniki,
            potasuj_klucz=klucz, seed=seed,
        )
        shuffled_accs.append(acc)
    avg_shuffled = sum(shuffled_accs) / len(shuffled_accs)
    return base_accuracy - avg_shuffled


# ─── Główna funkcja ───────────────────────────────────────────────────────────

def raport_waznosci(
    historia_sygnalow: List[Dict[str, str]],
    historia_wynikow: List[int],
    prog_martwy: float = 0.0,
    prog_redundantny: float = 0.01,
    n_permutacji: int = 20,
    min_sygnalow: int = 10,
) -> RaportWaznosci:
    """
    Produkuje pełny raport ważności neuronów (MDA + SFI).

    Argumenty:
      historia_sygnalow  — List[Dict[klucz_neuronu → "LONG"/"SHORT"/"NEUTRAL"]]
                           Jeden dict na bar/zdarzenie.
      historia_wynikow   — List[int] (+1=cena wzrosła, -1=cena spadła) — ten sam indeks.
      prog_martwy        — neuron z MDA ≤ prog_martwy i SFI_overall ≤ 0.51 → "martwy głos"
      prog_redundantny   — neuron z MDA < prog_redundantny → "redundantny"
      n_permutacji       — ile losowań do MDA (więcej = stabilniej, wolniej)
      min_sygnalow       — minimum aktywnych sygnałów neuronu do oceny

    Zwraca RaportWaznosci z rankingiem, martwymi głosami, redundantnymi.
    """
    # Niezgodne długości = rozjechana etykieta forward (look-ahead / ucięte bary).
    # `min()` cicho ucinał do krótszej serii — a przy przesunięciu w ŚRODKU serii
    # snap[i] i wyk[i] przestają opisywać ten sam bar → skażone MDA/SFI, czyli fałszywy
    # osąd „martwy głos"/„redundantny" (Prawo XVI/XX). Bliźniaczy `legatus.oblicz_wagi_ic`
    # odrzuca to twardo (cubic P2) — przenosimy ten sam strażnik tu, zamiast ucinać w ciszy.
    if len(historia_sygnalow) != len(historia_wynikow):
        raise ValueError(
            f"raport_waznosci: historia_sygnalow ({len(historia_sygnalow)}) i "
            f"historia_wynikow ({len(historia_wynikow)}) muszą mieć tę samą długość "
            "(etykieta forward równolegle do sygnału na tym samym barze)")
    n = len(historia_sygnalow)
    if n < MIN_OBS:
        logger.warning(
            "[FeatureImportance] Za mało obserwacji (%d < %d) — raport pustynny.", n, MIN_OBS
        )
        return RaportWaznosci(
            n_obserwacji=n,
            base_accuracy=0.5,
            rankowanie=[],
            martwe_glosy=[],
            redundantne=[],
            podsumowanie=f"Za mało danych ({n} < {MIN_OBS}). Zbierz więcej historii.",
        )

    snap = historia_sygnalow[:n]
    wyk = historia_wynikow[:n]

    # Zbiór wszystkich kluczy neuronów
    wszystkie_klucze: set = set()
    for h in snap:
        wszystkie_klucze.update(h.keys())
    klucze = sorted(wszystkie_klucze)

    # Base accuracy (bez tasowania)
    base_acc = _accuracy_zagregowana(snap, wyk)
    logger.info("[FeatureImportance] Base accuracy: %.1f%% | Neurony: %d | Obs: %d",
                base_acc * 100, len(klucze), n)

    # Oblicz SFI i MDA dla każdego neuronu
    wyniki_neuronow: List[WaznoscNeuronu] = []
    for klucz in klucze:
        sygnaly_k = [h.get(klucz, "NEUTRAL") for h in snap]
        sl, ss, nl, ns, nn = _sfi_neuronu(sygnaly_k, wyk)
        sfi_hm = _harmonic_mean(sl, ss)

        pominiety = (nl + ns) < min_sygnalow

        if pominiety:
            mda = 0.0
        else:
            mda = _mda_neuronu(klucz, snap, wyk, base_acc, n_permutacji)

        wyniki_neuronow.append(WaznoscNeuronu(
            klucz=klucz,
            mda=round(mda, 5),
            sfi_long=round(sl, 4),
            sfi_short=round(ss, 4),
            sfi_overall=round(sfi_hm, 4),
            n_long=nl,
            n_short=ns,
            n_neutral=nn,
            pominiety=pominiety,
        ))

    # Sortowanie wg MDA malejąco
    wyniki_neuronow.sort(key=lambda w: w.mda, reverse=True)

    martwe = [
        w.klucz for w in wyniki_neuronow
        if w.mda <= prog_martwy and w.sfi_overall <= 0.51 and not w.pominiety
    ]
    redundantne = [
        w.klucz for w in wyniki_neuronow
        if w.mda < prog_redundantny and not w.pominiety and w.klucz not in martwe
    ]

    pdsm = (
        f"Base accuracy: {base_acc:.1%} | "
        f"Neuronów: {len(klucze)} | "
        f"Martwych: {len(martwe)} | "
        f"Redundantnych: {len(redundantne)}"
    )

    return RaportWaznosci(
        n_obserwacji=n,
        base_accuracy=round(base_acc, 4),
        rankowanie=wyniki_neuronow,
        martwe_glosy=martwe,
        redundantne=redundantne,
        podsumowanie=pdsm,
    )


# ─── Adapter z historii Igrzysk ───────────────────────────────────────────────

def raport_z_igrzysk(igrzyska, bary: List[Dict], sygnaly_hist: List[Dict]) -> RaportWaznosci:
    """
    Pomocnicza: buduje historie wynikow z Igrzysk (StatystykaNeuronu.tp/fp)
    i sygnałów (z historii raportów neuronów w backteście).

    igrzyska: instancja Igrzyska z wypełnionymi statystykami per neuron
    bary: lista barów OHLCV (do wyznaczenia kierunku ceny: close[t+1] > close[t])
    sygnaly_hist: Lista snapów [{klucz: "LONG"/"SHORT"/"NEUTRAL"}, ...] — jeden per bar

    Wyniki: +1 gdy close[t+1] > close[t], -1 gdy < close[t].
    """
    wyniki: List[int] = []
    for i in range(len(bary) - 1):
        c_now = bary[i].get("close", 0.0)
        c_next = bary[i + 1].get("close", 0.0)
        if c_next > c_now:
            wyniki.append(1)
        elif c_next < c_now:
            wyniki.append(-1)
        else:
            wyniki.append(0)

    # Odetnij ostatni bar (brak następnego)
    snap_h = sygnaly_hist[: len(wyniki)]
    wyk_h = [w for w in wyniki if w != 0]
    snap_h_nonzero = [s for s, w in zip(snap_h, wyniki) if w != 0]

    return raport_waznosci(snap_h_nonzero, wyk_h)
