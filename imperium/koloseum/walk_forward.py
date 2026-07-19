"""
🔄 WALK-FORWARD — kroczące okna In-Sample/Out-of-Sample (W-345).

Luka #2 ze skanu konkurencji (Freqtrade/Jesse mają WFO od lat). Mamy hyperopt
(`optymalizator.py`, DSR-guided) i walidację (`walidacja.py`, PBO/DSR), ale BRAK
orkiestracji walk-forward — jedynej uczciwej obrony przed przeuczeniem przy
76 neuronach × wagi reżimowe (ogromna przestrzeń parametrów do przeuczenia).

DLA NOWICJUSZA: optymalizacja parametrów na CAŁEJ historii zawsze znajdzie
„zwycięzcę", który pasuje do przeszłości — ale przyszłość to inny rynek.
Walk-forward dzieli historię na kroczące pary okien:
  • IS (In-Sample) — tu OPTYMALIZUJEMY parametry (uczymy się).
  • OOS (Out-of-Sample) — tu TESTUJEMY te parametry na danych, których model
    nie widział (egzamin). Potem przesuwamy okno i powtarzamy.
Liczy się TYLKO wynik OOS — zagregowany przez wszystkie okna. To jedyna
prawdziwa miara (Prawo I: nie falsyfikujemy — egzamin na nieznanym).

WFE (Walk-Forward Efficiency) = wydajność_OOS / wydajność_IS:
  • WFE ≈ 1.0 → parametry działają tak samo poza próbą (zdrowe, robust)
  • WFE bliskie 0 lub ujemne → IS świetny, OOS słaby = KLASYCZNE PRZEUCZENIE
  • Próg robustności domyślnie 0.5 (literatura Pardo: WFE > 0.5 = system zdrowy)

Tryby okien:
  • kroczący (rolling, domyślny) — IS okno o stałym rozmiarze przesuwa się
    (zapomina starą historię — adaptacja do zmiany rynku).
  • zakotwiczony (anchored) — IS rośnie od startu (więcej danych, wolniejsza adaptacja).

Użycie:
    from imperium.koloseum.walk_forward import walk_forward
    from imperium.koloseum.optymalizator import PrzestrzeńParam

    def ewaluator(bary, params):
        eng = backtest(bary, min_pewnosc=params['min_pewnosc'], ...)
        zwroty = list(np.diff(eng.krzywa_equity) / eng.krzywa_equity[:-1])
        return eng.kapital_calkowity, zwroty

    raport = walk_forward(
        bary, ewaluator,
        przestrzenie=[PrzestrzeńParam('min_pewnosc', 0.45, 0.75)],
        rozmiar_is=500, rozmiar_oos=100, n_iteracji=50,
    )
    print(raport.werdykt, raport.wfe_srednia, raport.oos_sharpe_zagregowany)

Zasady:
  • Prawo I — wynik OOS to egzamin na nieznanym; zero look-ahead (okna rozłączne,
    OOS zawsze PO IS w czasie).
  • Prawo XVI — wykorzystuje istniejący `optymalizuj` (DSR-guided), nie dubluje.
  • Prawo XXI — granice testowane: za mało barów, jedno okno, stałe parametry,
    OOS gorszy/lepszy niż IS, dzielenie przez ~0.
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from imperium.koloseum.optymalizator import optymalizuj, PrzestrzeńParam

# Typ ewaluatora: (bary_okna, parametry) -> (skalar_wyniku, lista_zwrotow_per_bar)
Ewaluator = Callable[[list, Dict[str, float]], Tuple[float, List[float]]]


@dataclass
class OknoWF:
    """Para indeksów IS/OOS w serii barów (półotwarte [start, end))."""
    idx: int
    is_start: int
    is_end: int
    oos_start: int
    oos_end: int


@dataclass
class WynikOkna:
    """Wynik jednego okna walk-forward."""
    okno: OknoWF
    parametry: Dict[str, float]
    sharpe_is: float
    sharpe_oos: float
    wynik_is: float          # skalar zwrócony przez ewaluator na IS (np. kapitał)
    wynik_oos: float         # skalar na OOS
    efektywnosc: float       # WFE = sharpe_oos / sharpe_is (klamrowane do [-1, 2])


@dataclass
class RaportWalkForward:
    """Pełny raport walk-forward — werdykt oparty na OOS (Prawo I)."""
    okna: List[WynikOkna] = field(default_factory=list)
    wfe_srednia: float = 0.0
    oos_sharpe_zagregowany: float = 0.0
    stabilnosc_parametrow: Dict[str, float] = field(default_factory=dict)  # CV per param
    werdykt: str = "BRAK_DANYCH"   # ROBUST / PRZEUCZONY / SLABY / BRAK_DANYCH
    powod: str = ""
    n_okien: int = 0


def _sharpe(zwroty: List[float]) -> float:
    """Roczny-niezależny Sharpe (per-bar) — średnia/odchylenie. 0 gdy brak wariancji."""
    n = len(zwroty)
    if n < 2:
        return 0.0
    srednia = sum(zwroty) / n
    war = sum((z - srednia) ** 2 for z in zwroty) / (n - 1)
    if war <= 1e-18:
        return 0.0
    return srednia / math.sqrt(war)


def generuj_okna(n_barow: int, rozmiar_is: int, rozmiar_oos: int,
                 krok: Optional[int] = None, zakotwiczony: bool = False) -> List[OknoWF]:
    """
    Generuje kroczące okna IS/OOS. OOS zawsze następuje PO IS (zero look-ahead).

    krok: o ile przesuwać okno (domyślnie = rozmiar_oos → okna OOS rozłączne,
          pełne pokrycie bez nakładania — kanon walk-forward).
    zakotwiczony: IS rośnie od bara 0 (anchored); inaczej IS o stałym rozmiarze sunie.
    """
    if rozmiar_is < 2 or rozmiar_oos < 1:
        raise ValueError("rozmiar_is >= 2 i rozmiar_oos >= 1 wymagane")
    krok = krok or rozmiar_oos
    if krok < 1:
        raise ValueError("krok >= 1 wymagany")

    okna: List[OknoWF] = []
    is_start = 0
    idx = 0
    while True:
        is_end = is_start + rozmiar_is if not zakotwiczony else (0 + rozmiar_is + idx * krok)
        oos_start = is_end
        oos_end = oos_start + rozmiar_oos
        if oos_end > n_barow:
            break
        okna.append(OknoWF(idx=idx, is_start=(0 if zakotwiczony else is_start),
                           is_end=is_end, oos_start=oos_start, oos_end=oos_end))
        idx += 1
        is_start += krok
    return okna


def ewaluuj_okno(bary: list, okno: OknoWF, ewaluator: Ewaluator,
                 przestrzenie: List[PrzestrzeńParam],
                 n_iteracji: int = 50, seed: Optional[int] = 42
                 ) -> Tuple[WynikOkna, List[float]]:
    """
    Liczy JEDNO okno walk-forward (najmniejsza wznawialna jednostka — ZASADA ANALIZY
    CZĄSTKOWEJ). Optymalizuje na IS, egzaminuje na OOS, zwraca (WynikOkna, zwroty_oos).

    Deterministyczne przy stałym seed (optymalizuj → np.random.default_rng(seed)) — więc
    okno policzone na dwóch biegach daje IDENTYCZNY wynik → checkpoint/wznawianie bezpieczne.
    Wynik OOS to egzamin na nieznanym (Prawo I: OOS zawsze PO IS, zero look-ahead).
    """
    bary_is = bary[okno.is_start:okno.is_end]
    bary_oos = bary[okno.oos_start:okno.oos_end]

    # 1. Optymalizuj na IS (wykorzystuje DSR-guided optymalizuj — Prawo XVI)
    cel_is = lambda p, _b=bary_is: ewaluator(_b, p)  # noqa: E731
    raport_opt = optymalizuj(cel_is, przestrzenie, n_iteracji=n_iteracji, seed=seed)
    best = raport_opt.najlepsze_parametry

    # 2. Egzamin: te same parametry na IS i OOS — porównywalny Sharpe
    wynik_is, zwroty_is = ewaluator(bary_is, best)
    wynik_oos, zwroty_oos = ewaluator(bary_oos, best)
    sh_is = _sharpe(zwroty_is)
    sh_oos = _sharpe(zwroty_oos)

    # WFE: OOS/IS. Gdy IS ≤ 0 (nie nauczył się przewagi) → WFE = 0 (nie dziel/0).
    if sh_is > 1e-9:
        wfe = max(-1.0, min(2.0, sh_oos / sh_is))
    else:
        wfe = 0.0

    wynik = WynikOkna(
        okno=okno, parametry=best, sharpe_is=round(sh_is, 4),
        sharpe_oos=round(sh_oos, 4), wynik_is=round(float(wynik_is), 4),
        wynik_oos=round(float(wynik_oos), 4), efektywnosc=round(wfe, 4))
    return wynik, list(zwroty_oos)


def agreguj(pary: List[Tuple[WynikOkna, List[float]]],
            przestrzenie: List[PrzestrzeńParam],
            prog_wfe: float = 0.5) -> RaportWalkForward:
    """
    Agreguje wyniki okien w RaportWalkForward — wszystko z OOS (Prawo I). Czysta,
    deterministyczna funkcja z zapisanych cząstek: te same okna (z pętli albo z
    checkpointu) → ten sam raport. `pary`: [(WynikOkna, zwroty_oos), ...] w kolejności okien.
    """
    wyniki = [w for w, _ in pary]
    if not wyniki:
        return RaportWalkForward(werdykt="BRAK_DANYCH", n_okien=0, powod="brak okien")

    oos_zwroty_zagreg: List[float] = []
    for _, zwroty_oos in pary:
        oos_zwroty_zagreg.extend(zwroty_oos)
    parametry_per_okno: Dict[str, List[float]] = {p.nazwa: [] for p in przestrzenie}
    for w in wyniki:
        for nazwa in parametry_per_okno:
            if nazwa in w.parametry:
                parametry_per_okno[nazwa].append(w.parametry[nazwa])

    wfe_sr = sum(w.efektywnosc for w in wyniki) / len(wyniki)
    oos_sharpe = _sharpe(oos_zwroty_zagreg)
    stabilnosc = {nazwa: _wsp_zmiennosci(wart) for nazwa, wart in parametry_per_okno.items()}
    werdykt, powod = _werdykt(wfe_sr, oos_sharpe, prog_wfe, wyniki)

    return RaportWalkForward(
        okna=wyniki, wfe_srednia=round(wfe_sr, 4),
        oos_sharpe_zagregowany=round(oos_sharpe, 4),
        stabilnosc_parametrow=stabilnosc, werdykt=werdykt, powod=powod,
        n_okien=len(wyniki))


def walk_forward(bary: list, ewaluator: Ewaluator,
                 przestrzenie: List[PrzestrzeńParam],
                 rozmiar_is: int, rozmiar_oos: int,
                 n_iteracji: int = 50, krok: Optional[int] = None,
                 zakotwiczony: bool = False, seed: Optional[int] = 42,
                 prog_wfe: float = 0.5,
                 checkpoint_cb: "Optional[Callable[[WynikOkna, List[float]], None]]" = None,
                 postep_cb: "Optional[Callable[[int, int, WynikOkna], None]]" = None,
                 wznow: "Optional[Dict[int, Tuple[WynikOkna, List[float]]]]" = None,
                 ) -> RaportWalkForward:
    """
    Walk-forward optimization: optymalizuj na IS, egzaminuj na OOS, przesuń, powtórz.

    ewaluator(bary_okna, parametry) -> (skalar, lista_zwrotow):
        backtest na PODANYM wycinku barów z PODANYMI parametrami.
    przestrzenie: zakresy parametrów (jak w optymalizator.optymalizuj).
    rozmiar_is/oos: długości okien (w barach).
    n_iteracji: prób hyperopt per okno IS.
    prog_wfe: próg robustności WFE (Pardo: 0.5). Powyżej → ROBUST.

    Wznawialność (opt-in, ZASADA ANALIZY CZĄSTKOWEJ — domyślnie None = zachowanie bez zmian):
      checkpoint_cb(wynik, zwroty_oos)  — wołany po KAŻDYM świeżo policzonym oknie (zapis cząstki).
      postep_cb(i, n, wynik)            — pasek postępu (Prawo XXIV) po każdym oknie.
      wznow {idx: (WynikOkna, zwroty_oos)} — okna JUŻ policzone: pomiń, użyj zapisanego.

    Zwraca RaportWalkForward. Werdykt liczony WYŁĄCZNIE z OOS (Prawo I).
    """
    okna = generuj_okna(len(bary), rozmiar_is, rozmiar_oos, krok, zakotwiczony)
    if not okna:
        return RaportWalkForward(
            werdykt="BRAK_DANYCH", n_okien=0,
            powod=f"za mało barów ({len(bary)}) na okno IS={rozmiar_is}+OOS={rozmiar_oos}")

    wznow = wznow or {}
    pary: List[Tuple[WynikOkna, List[float]]] = []
    for i, okno in enumerate(okna):
        zapis = wznow.get(okno.idx)
        # Ufaj checkpointowi TYLKO gdy granice okna dokładnie się zgadzają — inaczej przelicz
        # (obrona przed cichym zmieszaniem wyników z innego podziału danych; Prawo I).
        if zapis is not None and zapis[0].okno == okno:
            wynik, zwroty_oos = zapis                  # wznowione z checkpointu — nie licz
        else:
            wynik, zwroty_oos = ewaluuj_okno(
                bary, okno, ewaluator, przestrzenie, n_iteracji=n_iteracji, seed=seed)
            if checkpoint_cb is not None:
                checkpoint_cb(wynik, zwroty_oos)       # zapis cząstki ZANIM następne okno
        pary.append((wynik, zwroty_oos))
        if postep_cb is not None:
            postep_cb(i + 1, len(okna), wynik)

    return agreguj(pary, przestrzenie, prog_wfe)


def _wsp_zmiennosci(wartosci: List[float]) -> float:
    """Współczynnik zmienności (CV = std/|mean|) — stabilność parametru między oknami.
    Niski CV = parametr stabilny (zaufanie); wysoki = parametr skacze (ostrożność)."""
    if len(wartosci) < 2:
        return 0.0
    srednia = sum(wartosci) / len(wartosci)
    if abs(srednia) < 1e-12:
        return 0.0
    war = sum((w - srednia) ** 2 for w in wartosci) / (len(wartosci) - 1)
    return round(math.sqrt(war) / abs(srednia), 4)


def _werdykt(wfe_sr: float, oos_sharpe: float, prog_wfe: float,
             wyniki: List[WynikOkna]) -> Tuple[str, str]:
    """
    Werdykt oparty na OOS (Prawo I):
      • SLABY        — OOS Sharpe ≤ 0 (system nie zarabia poza próbą, niezależnie od WFE)
      • PRZEUCZONY   — IS zarabiał (był dodatni Sharpe), ale WFE < prog (OOS degraduje)
      • ROBUST       — WFE ≥ prog i OOS Sharpe > 0 (zdrowy poza próbą)
    """
    if oos_sharpe <= 0.0:
        return "SLABY", f"OOS Sharpe {oos_sharpe:.3f} ≤ 0 — brak przewagi poza próbą"
    if wfe_sr < prog_wfe:
        ile_is_dodatnich = sum(1 for w in wyniki if w.sharpe_is > 0)
        if ile_is_dodatnich > 0:
            return "PRZEUCZONY", (f"WFE {wfe_sr:.2f} < próg {prog_wfe} — IS uczył się "
                                  f"przewagi, OOS ją tracił (degradacja poza próbą)")
        return "SLABY", f"WFE {wfe_sr:.2f} < próg i IS bez przewagi"
    return "ROBUST", (f"WFE {wfe_sr:.2f} ≥ {prog_wfe} i OOS Sharpe {oos_sharpe:.3f} > 0 "
                      f"— parametry trzymają poza próbą")
