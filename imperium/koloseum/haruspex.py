"""
🔮 HARUSPEX — Predykcyjny Namiestnik (kandydat #20, żniwo wrzutni 2026-07-12).

╔═══════════════════════════════════════════════════════════════════════════════╗
║ ⚠️  WERDYKT POMIARU (2026-07-15, Prawo I): FALSYFIKOWANY — NIE WPINAĆ.          ║
║ Markow 1. rzędu NIE bije persystencji na realnych danych (BTC/ETH 4H):         ║
║   • trafność argmax == baseline persystencji (97.5%=97.5% BTC, 92.5% ETH) → +0%║
║   • sygnał ZMIANY: recall 0% (0 ostrzeżeń na 7 realnych zmian, także przy 0.10)║
║ Przyczyna strukturalna: reżimy o wysokim P(zmiany) (NORMAL 33%, VOLATILE) są   ║
║ RZADKIE → nigdy nie zbierają min_obserwacji → milczą; częste (TREND/RANGING)   ║
║ są 97-98% lepkie → zmiana nieprognozowana. To NIE kwestia progu — to natura    ║
║ rozkładu. Moduł ZOSTAJE jako infrastruktura pomiaru + udokumentowany negatyw   ║
║ (antykruchość: nie budować tego naiwnie ponownie). Ewentualna wartość dopiero  ║
║ z modelem WARUNKOWYM na cechy (nie goły Markow) — osobny kandydat, po pomiarze.║
╚═══════════════════════════════════════════════════════════════════════════════╝


Nazwa (ZASADA NOMENKLATURY IMPERIALNEJ): HARUSPEX — rzymski/etruski kapłan-wróżbita,
który PRZEWIDYWAŁ przyszłość czytając znaki (haruspicium). Dobrana do funkcji: organ
przewiduje NADCHODZĄCY reżim, zanim się objawi — w odróżnieniu od reaktywnego Namiestnika.

DLA NOWICJUSZA — czym różni się od tego, co już mamy:
  • NAMIESTNIK (koloseum/namiestnik.py) jest REAKTYWNY — dostaje GOTOWY reżim i decyduje
    o bramkowaniu DOPIERO gdy reżim już nastał.
  • DRIFT ADAPTER (koloseum/drift_adapter.py) mierzy TERAŹNIEJSZY dryf (entropia/momentum
    okna) — „jak bardzo reżim jest teraz niestabilny", ale NIE mówi KTÓRY reżim nadejdzie.
  • HARUSPEX PRZEWIDUJE — buduje macierz przejść Markowa P(następny reżim | obecny) z
    obserwowanej sekwencji reżimów i wskazuje NAJBARDZIEJ PRAWDOPODOBNY następny stan
    + prawdopodobieństwo zmiany. To predykcja, nie pomiar turbulencji.

POMIAR NAJPIERW (ZASADA WPIĘCIA W ŚCIEŻKĘ DECYZYJNĄ — opt-in OFF):
  Haruspex NIE jest wpięty w żadną decyzję. To standalone predyktor + własny pomiar
  trafności (`oszacuj_trafnosc`, bez look-ahead). Dopiero gdy arena/A-B pokaże, że
  prognoza ma wartość (trafność > bazy losowej / częstości), Cezar zdecyduje o wpięciu
  sygnału „przygotuj się na zmianę" do Namiestnika (osobny krok, osobna flaga).

Prawo I (bez zmyślania): przy zbyt małej liczbie obserwacji przejść z danego reżimu
Haruspex MILCZY (czy_milczy=True) — nie zgaduje prognozy z 1-2 próbek (wzorzec Pythii).

Model: łańcuch Markowa 1. rzędu (pierwsze przybliżenie — najtańszy splot istniejącego
strumienia reżimów). Wyższe rzędy / bayesowskie wygładzanie = przyszłe rozszerzenia,
gdy pomiar uzasadni koszt (Prawo XVI).
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ─── Progi (Reguła Test-Granic: każdy ma test wartości granicznej) ──────────────
MIN_OBSERWACJI = 5      # min. liczba przejść Z danego reżimu, by ufać prognozie (inaczej MILCZENIE)
PROG_ZMIANY = 0.5       # P(następny ≠ obecny) > tego → czy_zmiana_prawdopodobna=True


@dataclass
class Prognoza:
    """Prognoza następnego reżimu z macierzy przejść."""
    docelowy_rezim: Optional[str]        # najbardziej prawdopodobny NASTĘPNY reżim (None gdy MILCZENIE)
    prawdopodobienstwo: float            # P(docelowy | obecny) ∈ [0, 1]
    czy_zmiana_prawdopodobna: bool       # P(następny ≠ obecny) > PROG_ZMIANY
    czy_milczy: bool                     # True gdy za mało obserwacji (nie zgadujemy — Prawo I)
    n_obserwacji: int                    # ile przejść zaobserwowano z obecnego reżimu (support)
    rozklad: Dict[str, float] = field(default_factory=dict)  # pełny rozkład P(następny | obecny)


@dataclass
class RaportTrafnosci:
    """Wynik pomiaru trafności prognoz na sekwencji (bez look-ahead)."""
    n_prognoz: int           # ile prognoz nie-milczących postawiono
    trafienia: int           # ile trafiło w faktyczny następny reżim (argmax)
    trafnosc: float          # trafienia / n_prognoz ∈ [0, 1]
    brier: float             # średni Brier na faktycznym następnym reżimie (0=idealny, im mniej tym lepiej)
    baza_czestosci: float    # trafność naiwnego predyktora „najczęstszy reżim ogółem" (słaby baseline)
    baza_persystencji: float # trafność predyktora „następny = obecny" (MOCNY baseline — reżimy są lepkie)
    n_milczen: int           # ile kroków Haruspex zmilczał (za mało danych)
    # Sygnał ZMIANY (czy_zmiana_prawdopodobna) — właściwa wartość organu „przygotuj się":
    n_zmian_faktycznych: int = 0   # ile realnych przejść (obecny ≠ następny) na krokach nie-milczących
    zmiany_zlapane: int = 0        # ile z nich Haruspex ostrzegł (czy_zmiana_prawdopodobna=True) — recall
    zmiany_falszywe: int = 0       # ile ostrzeżeń zmiany BEZ realnej zmiany (fałszywe alarmy) — do precyzji
    # UWAGA (Prawo I): reżimy są persystentne, więc baza_persystencji jest wysoka.
    # argmax ≈ persystencja; realna wartość = recall/precyzja sygnału ZMIANY (rzadkie zdarzenia).


class Haruspex:
    """
    Predyktor następnego reżimu (łańcuch Markowa 1. rzędu).

    Użycie (pomiar):
        h = Haruspex()
        for rezim in sekwencja_rezimow:   # co bar, po klasyfikuj_rezim()
            h.dodaj_rezim(rezim)
        prog = h.przewiduj()              # prognoza z ostatniego reżimu

    Użycie (walidacja bez look-ahead):
        raport = Haruspex().oszacuj_trafnosc(sekwencja_rezimow)
    """

    def __init__(self, min_obserwacji: int = MIN_OBSERWACJI,
                 prog_zmiany: float = PROG_ZMIANY) -> None:
        if min_obserwacji < 1:
            raise ValueError("min_obserwacji musi być ≥ 1")
        if not 0.0 <= prog_zmiany <= 1.0:
            raise ValueError("prog_zmiany musi być w [0, 1]")
        self.min_obserwacji = min_obserwacji
        self.prog_zmiany = prog_zmiany
        # przejscia[z_rezimu][do_rezimu] = licznik
        self._przejscia: Dict[str, Counter] = defaultdict(Counter)
        self._poprzedni: Optional[str] = None
        self._wszystkie: Counter = Counter()   # globalna częstość reżimów (do baseline)

    def dodaj_rezim(self, rezim: str) -> None:
        """Rejestruje obserwację reżimu. Wywołuj co bar. Buduje przejście poprzedni→obecny."""
        if not rezim:
            return   # pusty reżim ignorowany (brak danych ≠ przejście)
        if self._poprzedni is not None:
            self._przejscia[self._poprzedni][rezim] += 1
        self._wszystkie[rezim] += 1
        self._poprzedni = rezim

    def przewiduj(self, obecny_rezim: Optional[str] = None) -> Prognoza:
        """
        Prognoza następnego reżimu z macierzy przejść.

        obecny_rezim=None → użyj ostatniego zaobserwowanego (self._poprzedni).
        Za mało obserwacji przejść z tego reżimu → MILCZENIE (Prawo I, nie zgadujemy).
        """
        rezim = obecny_rezim if obecny_rezim is not None else self._poprzedni
        if rezim is None:
            return Prognoza(None, 0.0, False, True, 0, {})

        licznik = self._przejscia.get(rezim, Counter())
        total = sum(licznik.values())
        if total < self.min_obserwacji:
            return Prognoza(None, 0.0, False, True, total, {})

        rozklad = {do: c / total for do, c in licznik.items()}
        docelowy, p_docelowy = max(rozklad.items(), key=lambda kv: kv[1])
        # P(zmiana) = 1 − P(pozostania w tym samym reżimie)
        p_pozostania = rozklad.get(rezim, 0.0)
        p_zmiany = 1.0 - p_pozostania
        return Prognoza(
            docelowy_rezim=docelowy,
            prawdopodobienstwo=round(p_docelowy, 6),
            czy_zmiana_prawdopodobna=p_zmiany > self.prog_zmiany,
            czy_milczy=False,
            n_obserwacji=total,
            rozklad={k: round(v, 6) for k, v in rozklad.items()},
        )

    def oszacuj_trafnosc(self, sekwencja: List[str]) -> RaportTrafnosci:
        """
        Mierzy trafność prognoz na sekwencji reżimów BEZ look-ahead:
        dla każdego kroku prognozuje z macierzy zbudowanej TYLKO z wcześniejszych
        przejść, potem porównuje z faktycznym następnym reżimem i dopiero AKTUALIZUJE
        macierz. Zwraca trafność (argmax) + Brier + baseline (najczęstszy reżim).
        """
        proba = Haruspex(self.min_obserwacji, self.prog_zmiany)
        n_prognoz = trafienia = n_milczen = 0
        traf_persyst = 0   # trafienia baseline „następny = obecny" na TYCH SAMYCH krokach
        n_zmian_faktycznych = zmiany_zlapane = zmiany_falszywe = 0
        brier_suma = 0.0
        czyste = [r for r in sekwencja if r]

        for i in range(len(czyste) - 1):
            obecny, faktyczny = czyste[i], czyste[i + 1]
            proba.dodaj_rezim(obecny)          # macierz zna tylko przejścia < i
            prog = proba.przewiduj(obecny)
            if prog.czy_milczy:
                n_milczen += 1
                continue
            n_prognoz += 1
            if prog.docelowy_rezim == faktyczny:
                trafienia += 1
            if obecny == faktyczny:            # baseline persystencji na tym samym kroku
                traf_persyst += 1
            # Sygnał ZMIANY: precyzja/recall ostrzeżeń „przygotuj się na zmianę"
            realna_zmiana = obecny != faktyczny
            if realna_zmiana:
                n_zmian_faktycznych += 1
                if prog.czy_zmiana_prawdopodobna:
                    zmiany_zlapane += 1
            elif prog.czy_zmiana_prawdopodobna:
                zmiany_falszywe += 1
            # Brier na faktycznym następnym reżimie: Σ_k (p_k − 1[k=faktyczny])²
            brier_suma += sum(
                (p - (1.0 if k == faktyczny else 0.0)) ** 2
                for k, p in prog.rozklad.items()
            ) + (0.0 if faktyczny in prog.rozklad else 1.0)  # kara gdy faktyczny spoza rozkładu
        if czyste:
            proba.dodaj_rezim(czyste[-1])

        # Baseline: naiwny predyktor „zawsze najczęstszy reżim ogółem"
        globalny = Counter(czyste)
        if globalny:
            _, c = globalny.most_common(1)[0]
            baza = c / len(czyste)
        else:
            baza = 0.0

        return RaportTrafnosci(
            n_prognoz=n_prognoz,
            trafienia=trafienia,
            trafnosc=round(trafienia / n_prognoz, 6) if n_prognoz else 0.0,
            brier=round(brier_suma / n_prognoz, 6) if n_prognoz else 0.0,
            baza_czestosci=round(baza, 6),
            baza_persystencji=round(traf_persyst / n_prognoz, 6) if n_prognoz else 0.0,
            n_milczen=n_milczen,
            n_zmian_faktycznych=n_zmian_faktycznych,
            zmiany_zlapane=zmiany_zlapane,
            zmiany_falszywe=zmiany_falszywe,
        )

    def macierz(self) -> Dict[str, Dict[str, float]]:
        """Zwraca macierz przejść jako prawdopodobieństwa (diagnostyka/raport)."""
        wynik: Dict[str, Dict[str, float]] = {}
        for z_rezimu, licznik in self._przejscia.items():
            total = sum(licznik.values())
            if total:
                wynik[z_rezimu] = {do: round(c / total, 6) for do, c in licznik.items()}
        return wynik
