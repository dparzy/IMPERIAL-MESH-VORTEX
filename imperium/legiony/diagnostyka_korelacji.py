"""
📊 IMV-DIAG | Diagnostyka Dekorelacji — macierz korelacji sygnałów modułów

ROLA (Prawo XV — mierzyć, nie zgadywać):
  Zasada „brak redundancji" była dotąd stosowana po PODOBIEŃSTWIE (ten sam
  wskaźnik = odrzuć). To błąd: redundancja szkodzi tylko gdy sygnały są
  SKORELOWANE (te same błędy w tych samych momentach). Dwa podobne moduły
  liczone inaczej mogą DEKORELOWAĆ błędy = wartość, nie szum.

  Ten moduł zamienia dogmat w liczbę: na serii barów zbiera wektory sygnałów
  każdego zwiadowcy, liczy macierz korelacji Pearsona i raportuje:
    - pary NADMIAROWO skorelowane (>prog) → kandydaci do scalenia / wagi w dół
    - pary DYWERSYFIKUJĄCE (niska/ujemna korelacja) → filar siły Imperium

  Dzięki temu decyzja „redundancja czy postęp" jest jawna dla Cezara.

Uwaga: działa na zwiadowcach EXP (pure Python, bez TA-Lib) — czyli dokładnie tam,
gdzie pojawiło się pytanie o redundancję elitarnych. Neurony wymagają Bramy
(TA-Lib), więc nie są tu zbierane (mogą być dodane gdy Brama dostępna).
"""

import logging
import math
from collections import deque
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("DiagKorelacji")


def sygnal_na_liczbe(kierunek: str, pewnosc: float) -> float:
    """
    Mapuje sygnał na liczbę dla korelacji:
      LONG  → +pewnosc
      SHORT → -pewnosc
      NEUTRAL → 0.0
    Pewność jako amplituda — mocniejszy sygnał waży więcej.
    """
    if kierunek == "LONG":
        return abs(pewnosc)
    if kierunek == "SHORT":
        return -abs(pewnosc)
    return 0.0


def korelacja_pearson(x: List[float], y: List[float]) -> Optional[float]:
    """
    Współczynnik korelacji Pearsona — pure Python.
    Zwraca None gdy któryś wektor ma zerową wariancję (stały sygnał) lub za mało
    danych — wtedy korelacja jest nieokreślona (nie udawaj 0).
    """
    n = len(x)
    if n < 2 or n != len(y):
        return None
    sx = sum(x)
    sy = sum(y)
    mx = sx / n
    my = sy / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    vx = sum((xi - mx) ** 2 for xi in x)
    vy = sum((yi - my) ** 2 for yi in y)
    if vx <= 0 or vy <= 0:
        return None  # stały wektor — korelacja nieokreślona
    return cov / math.sqrt(vx * vy)


def _dyskretyzuj(x: List[float], biny: int = 5) -> Optional[List[int]]:
    """
    Mapuje serię ciągłą na indeksy binów [0..biny-1] (równe szerokości).
    Zwraca None gdy seria stała (max<=min) — entropia/MI nieokreślone.
    """
    if not x:
        return None
    lo, hi = min(x), max(x)
    if hi <= lo:
        return None  # stała seria — brak informacji
    szer = (hi - lo) / biny
    return [min(biny - 1, int((xi - lo) / szer)) for xi in x]


def _entropia_shannon(etykiety: List[int]) -> float:
    """Entropia Shannona (naturalna, nat) rozkładu etykiet dyskretnych."""
    n = len(etykiety)
    if n == 0:
        return 0.0
    from collections import Counter
    c = Counter(etykiety)
    return -sum((v / n) * math.log(v / n) for v in c.values())


def informacja_wzajemna(x: List[float], y: List[float], biny: int = 5) -> Optional[float]:
    """
    Informacja wzajemna I(X;Y) (nat) przez histogram. Pure Python.
    None gdy któraś seria stała (brak informacji) lub za mało danych.

    MI = H(X) + H(Y) - H(X,Y). Łapie zależności NIELINIOWE, których Pearson nie widzi.
    """
    n = len(x)
    if n < 2 or n != len(y):
        return None
    dx = _dyskretyzuj(x, biny)
    dy = _dyskretyzuj(y, biny)
    if dx is None or dy is None:
        return None
    hx = _entropia_shannon(dx)
    hy = _entropia_shannon(dy)
    hxy = _entropia_shannon([a * biny + b for a, b in zip(dx, dy)])  # łączny
    mi = hx + hy - hxy
    return max(0.0, mi)  # numeryczny floor (MI ≥ 0)


def nmi(x: List[float], y: List[float], biny: int = 5) -> Optional[float]:
    """
    Znormalizowana informacja wzajemna ∈ [0,1]: NMI = I(X;Y)/sqrt(H(X)·H(Y)).
    1 = pełna redundancja (ten sam rozkład informacji), 0 = niezależne.
    None gdy seria stała. Wykrywa redundancję NIELINIOWĄ (Pearson ~0 a NMI wysokie).
    """
    n = len(x)
    if n < 2 or n != len(y):
        return None
    dx = _dyskretyzuj(x, biny)
    dy = _dyskretyzuj(y, biny)
    if dx is None or dy is None:
        return None
    hx = _entropia_shannon(dx)
    hy = _entropia_shannon(dy)
    if hx <= 0 or hy <= 0:
        return None
    mi = max(0.0, hx + hy - _entropia_shannon([a * biny + b for a, b in zip(dx, dy)]))
    return min(1.0, mi / math.sqrt(hx * hy))


def variation_of_information(x: List[float], y: List[float], biny: int = 5) -> Optional[float]:
    """
    Znormalizowana Variation of Information ∈ [0,1] (López de Prado, MLAM).
    VI_norm = (H(X,Y) - I(X;Y)) / H(X,Y).  0 = identyczna informacja, 1 = niezależne.
    Metryka odległości (spełnia nierówność trójkąta) — lepsza do klastrowania niż |ρ|.
    """
    n = len(x)
    if n < 2 or n != len(y):
        return None
    dx = _dyskretyzuj(x, biny)
    dy = _dyskretyzuj(y, biny)
    if dx is None or dy is None:
        return None
    hx = _entropia_shannon(dx)
    hy = _entropia_shannon(dy)
    hxy = _entropia_shannon([a * biny + b for a, b in zip(dx, dy)])
    if hxy <= 0:
        return None
    mi = max(0.0, hx + hy - hxy)
    return min(1.0, max(0.0, (hxy - mi) / hxy))


def raport_informacji_wzajemnej(
    serie: Dict[str, List[float]],
    prog_nmi: float = 0.50,
    prog_pearson_liniowy: float = 0.50,
    biny: int = 5,
) -> Dict[str, Any]:
    """
    📊 META-01 (research W-335) | Redundancja NIELINIOWA — czego Pearson nie widzi.

    DLA NOWICJUSZA: dwa neurony mogą mieć korelację Pearsona ~0 (pozornie niezależne),
    a jednocześnie nieść tę samą informację w sposób nieliniowy (np. jeden reaguje na
    |ruch|, drugi na ruch — korelacja liniowa znika, ale wiedza ta sama). Pearson tego
    NIE złapie. Informacja wzajemna i Variation-of-Information łapią.

    Flaguje pary „ukrycie redundantne": wysokie NMI (≥prog_nmi) PRZY niskim |Pearson|
    (<prog_pearson_liniowy) — to redundancja, którą reguła |ρ|>0.80 przegapiła.

    Zwraca dict z listami par + metrykami (NMI, VI, Pearson) — uzupełnia Prawo XVI.
    """
    klucze = sorted(serie.keys())
    ukryte_redundantne = []
    wszystkie = []
    for i in range(len(klucze)):
        for j in range(i + 1, len(klucze)):
            a, b = klucze[i], klucze[j]
            xa, xb = serie[a], serie[b]
            n_ab = min(len(xa), len(xb))
            if n_ab < 2:
                continue
            xa2, xb2 = xa[-n_ab:], xb[-n_ab:]
            wzajemna = nmi(xa2, xb2, biny)
            vi = variation_of_information(xa2, xb2, biny)
            pear = korelacja_pearson(xa2, xb2)
            if wzajemna is None:
                continue
            wpis = {
                "para": f"{a}~{b}",
                "nmi": round(wzajemna, 3),
                "vi": round(vi, 3) if vi is not None else None,
                "pearson": round(pear, 3) if pear is not None else None,
            }
            wszystkie.append(wpis)
            # Ukryta redundancja: silna informacyjnie, słaba liniowo
            if wzajemna >= prog_nmi and (pear is None or abs(pear) < prog_pearson_liniowy):
                ukryte_redundantne.append(wpis)

    ukryte_redundantne.sort(key=lambda w: -w["nmi"])
    return {
        "liczba_modulow": len(serie),
        "pary_ukryte_redundantne": ukryte_redundantne,
        "wszystkie_pary": wszystkie,
        "prog_nmi": prog_nmi,
        "prog_pearson_liniowy": prog_pearson_liniowy,
    }


def zbierz_sygnaly_zwiadowcow(
    bary: List[Dict[str, Any]],
    zwiadowcy: list,
    okno: int = 60,
    krok: int = 1,
) -> Dict[str, List[float]]:
    """
    Przesuwa okno po serii barów i zbiera sygnał każdego zwiadowcy w każdym kroku.

    bary:   pełna seria OHLCV (im dłuższa, tym wiarygodniejsza korelacja).
    okno:   ile barów widzi zwiadowca w danym kroku (jego kontekst).
    krok:   co ile barów przesuwamy okno (1 = każdy bar).

    Zwraca {KLUCZ: [wartości sygnału w kolejnych krokach]}.
    Pomija zwiadowców wyciszonych (DOSTEPNY=False) — nie mają danych.
    """
    aktywni = [z for z in zwiadowcy if getattr(z, "DOSTEPNY", True)]
    serie: Dict[str, List[float]] = {z.KLUCZ: [] for z in aktywni}

    if len(bary) < okno:
        return serie

    for koniec in range(okno, len(bary) + 1, krok):
        wycinek = bary[koniec - okno:koniec]
        for z in aktywni:
            try:
                raport = z.analizuj(wycinek)
                wartosc = sygnal_na_liczbe(raport.kierunek, raport.pewnosc)
            except Exception as e:
                logger.error(f"[DiagKorelacji] {z.KLUCZ} analizuj() padł: {e}")
                wartosc = 0.0
            serie[z.KLUCZ].append(wartosc)
    return serie


def macierz_korelacji(serie: Dict[str, List[float]]) -> Dict[Tuple[str, str], Optional[float]]:
    """
    Liczy korelację Pearsona dla każdej pary modułów.
    Zwraca {(klucz_a, klucz_b): korelacja} dla a < b (bez duplikatów i przekątnej).
    """
    klucze = sorted(serie.keys())
    wynik: Dict[Tuple[str, str], Optional[float]] = {}
    for i in range(len(klucze)):
        for j in range(i + 1, len(klucze)):
            a, b = klucze[i], klucze[j]
            wynik[(a, b)] = korelacja_pearson(serie[a], serie[b])
    return wynik


def raport_dekorelacji(
    bary: List[Dict[str, Any]],
    zwiadowcy: list,
    okno: int = 60,
    krok: int = 1,
    prog_redundancji: float = 0.80,
    prog_dywersyfikacji: float = 0.20,
) -> Dict[str, Any]:
    """
    Pełny raport dekorelacji dla Cezara (Prawo XV).

    prog_redundancji:    |korelacja| > prog → para nadmiarowa (kandydat do scalenia)
    prog_dywersyfikacji: |korelacja| < prog → para dywersyfikująca (filar siły)

    Zwraca dict z listami par i surową macierzą — gotowy do logu/dashboardu.
    """
    serie = zbierz_sygnaly_zwiadowcow(bary, zwiadowcy, okno=okno, krok=krok)
    macierz = macierz_korelacji(serie)

    redundantne = []
    dywersyfikujace = []
    martwe = []          # None Z POWODU stałego sygnału (zerowa wariancja) = martwy głos
    niedostateczne = []  # None z powodu za małej liczby próbek (NIE martwy moduł)

    # Moduły zawsze NEUTRAL w całym oknie (zerowa wariancja) = martwy głos.
    # Wymaga ≥2 próbek — przy 1 próbce seria trywialnie ma len(set)==1, co NIE
    # dowodzi martwoty, tylko braku danych (Prawo I: nie udawaj wiedzy z 1 punktu).
    stale = {k for k, v in serie.items() if len(v) >= 2 and len(set(v)) == 1}

    for (a, b), kor in macierz.items():
        if kor is None:
            # None oznacza: (1) stały sygnał (martwy) LUB (2) za mało próbek.
            # Tylko (1) to realna utrata potencjału — (2) to po prostu krótka seria.
            if a in stale or b in stale:
                martwe.append((a, b))
            else:
                niedostateczne.append((a, b))
            continue
        if abs(kor) > prog_redundancji:
            redundantne.append((a, b, round(kor, 3)))
        elif abs(kor) < prog_dywersyfikacji:
            dywersyfikujace.append((a, b, round(kor, 3)))

    stale = sorted(stale)

    redundantne.sort(key=lambda t: -abs(t[2]))
    dywersyfikujace.sort(key=lambda t: abs(t[2]))

    return {
        "liczba_modulow": len(serie),
        "liczba_krokow": len(next(iter(serie.values()))) if serie else 0,
        "pary_redundantne": redundantne,
        "pary_dywersyfikujace": dywersyfikujace,
        "pary_nieokreslone": martwe,
        "pary_niedostateczne_dane": niedostateczne,
        "moduly_stale": stale,
        "prog_redundancji": prog_redundancji,
        "prog_dywersyfikacji": prog_dywersyfikacji,
        "macierz": {f"{a}~{b}": (round(k, 3) if k is not None else None)
                    for (a, b), k in macierz.items()},
    }


class KolektorKorelacjiNeuronow:
    """
    📡 W-305 | Online kolektor korelacji NEURONÓW (nie zwiadowców).

    DLA NOWICJUSZA: SynapsyRezimowe (W-299) wzmacniają duety neuronów TYM bardziej,
    im są od siebie NIEZALEŻNE (dekorelacja = Prawo XVI). Ale by wiedzieć, kto jest
    niezależny, trzeba mierzyć korelację par neuronów na żywo. `diagnostyka_korelacji`
    robiła to dotąd TYLKO dla zwiadowców EXP (pure Python). Neurony głosują przez Bramę
    i pojawiają się dopiero w `raport.sygnaly` Legatusa. Ten kolektor zbiera te właśnie
    głosy strumieniowo (okno przesuwne) i liczy macierz korelacji par neuronów —
    domykając pętlę: kara_korelacji/dekorelacja w SynapsyRezimowych przestaje być martwa.

    Brak lookahead (Prawo I): macierz zwracana w kroku t opiera się WYŁĄCZNIE na głosach
    z kroków ≤ t. Dyrygent najpierw odczytuje korelacje (z przeszłości), potem rejestruje
    bieżący głos — nigdy odwrotnie.

    Wyrównanie czasowe: każdy znany neuron dostaje wartość w KAŻDYM kroku (nieobecny =
    0.0 = NEUTRAL), więc wszystkie serie mają tę samą oś czasu; `[-n:]` obu wektorów
    odnosi się do tych samych n ostatnich kroków.
    """

    def __init__(self, okno: int = 120, min_probek: int = 20):
        """
        okno:      ile ostatnich kroków trzymamy (przesuwne, bounded — O(N·okno) pamięci).
        min_probek: minimalna liczba wspólnych próbek, by w ogóle liczyć korelację
                   (mniej = None, czyli traktowane jak para niezależna — Prawo I).
        """
        self.okno = okno
        self.min_probek = min_probek
        self._serie: Dict[str, deque] = {}

    def zarejestruj(self, sygnaly: list) -> None:
        """Dokłada jeden krok: wektor głosów {neuron_id: ±pewnosc/0}. Nieobecni → 0.0."""
        biezace = {s.neuron_id: sygnal_na_liczbe(s.kierunek, s.pewnosc) for s in sygnaly}
        klucze = set(self._serie) | set(biezace)
        for k in klucze:
            d = self._serie.get(k)
            if d is None:
                d = deque(maxlen=self.okno)
                self._serie[k] = d
            d.append(biezace.get(k, 0.0))

    def korelacje(self) -> Dict[Tuple[str, str], float]:
        """
        Macierz {(a, b): corr} dla par z ≥min_probek wspólnych próbek i określoną korelacją.
        Pary o nieokreślonej korelacji (stały sygnał / za mało danych) są POMIJANE —
        SynapsyRezimowe potraktują je wtedy jako niezależne (corr=0), co jest bezpiecznym
        domyślnym (Prawo I: nie udawaj wiedzy, której nie masz).
        """
        klucze = sorted(self._serie)
        wynik: Dict[Tuple[str, str], float] = {}
        for i in range(len(klucze)):
            for j in range(i + 1, len(klucze)):
                a, b = klucze[i], klucze[j]
                xa = list(self._serie[a])
                xb = list(self._serie[b])
                n = min(len(xa), len(xb))
                if n < self.min_probek:
                    continue
                kor = korelacja_pearson(xa[-n:], xb[-n:])
                if kor is not None:
                    wynik[(a, b)] = round(kor, 4)
        return wynik

    def korelacje_denoised(self, bwidth: float = 0.25) -> Dict[Tuple[str, str], float]:
        """
        🧬 W-365 | Macierz korelacji par neuronów PO denoisingu Marchenko-Pastur.

        Buduje pełną macierz korelacji z zebranych serii, odszumia ją (constant residual
        eigenvalue — `denoising_macierzy.denoise_macierz`) i zwraca pary w formacie
        zgodnym z `korelacje()`. Dzięki temu SynapsyRezimowe karzą/wzmacniają na podstawie
        SYGNAŁU (struktura), nie szumu — podnosi jakość Prawa XVI tam, gdzie jest konsumowana.

        BEZPIECZNY FALLBACK (Prawo I — nie udawaj wiedzy): zwraca surową `korelacje()` gdy:
        - <2 neuronów, lub
        - za mało wspólnych próbek (t < min_probek), lub
        - q = T/N ≤ 1 (za mało obserwacji na zmienną — MP niezdefiniowane), lub
        - którakolwiek seria stała (NaN w corrcoef).
        Denoising aktywuje się dopiero gdy danych jest dość, by był wiarygodny.
        """
        klucze = sorted(self._serie)
        n = len(klucze)
        if n < 2:
            return {}
        t = min(len(self._serie[k]) for k in klucze)
        if t < self.min_probek:
            return self.korelacje()
        q = t / n
        if q <= 1:
            return self.korelacje()  # za mało obserwacji na zmienną — MP niezdefiniowane

        import numpy as np
        M = np.array([list(self._serie[k])[-t:] for k in klucze], dtype=float)
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = np.corrcoef(M)
        if not np.all(np.isfinite(corr)):
            return self.korelacje()  # stała seria → NaN → fallback do surowej

        from imperium.legiony.denoising_macierzy import denoise_macierz
        try:
            cd = denoise_macierz(corr, q=q, bwidth=bwidth)["corr_denoised"]
        except Exception as e:
            logger.error(f"[Kolektor] denoising padł, fallback do surowej: {e}")
            return self.korelacje()

        wynik: Dict[Tuple[str, str], float] = {}
        for i in range(n):
            for j in range(i + 1, n):
                wynik[(klucze[i], klucze[j])] = round(float(cd[i, j]), 4)
        return wynik

    def liczba_krokow(self) -> int:
        """Ile kroków zebrano dla najdłuższej serii (diagnostyka)."""
        return max((len(d) for d in self._serie.values()), default=0)

    def klucze(self) -> List[str]:
        """Lista neuronów, których głosy zebrano (diagnostyka)."""
        return sorted(self._serie)


def raport_z_kolektora(
    kolektor: "KolektorKorelacjiNeuronow",
    prog_redundancji: float = 0.80,
    prog_dywersyfikacji: float = 0.20,
) -> Dict[str, Any]:
    """
    📊 W-306 | Raport dekorelacji NEURONÓW (Prawo XVI) z populowanego kolektora.

    Bliźniak `raport_dekorelacji` (zwiadowcy), ale dla pełnego roju neuronów —
    korzysta z macierzy korelacji zebranej online w `KolektorKorelacjiNeuronow`
    (W-305) podczas backtestu/live. Dzięki temu „redundancja mierzona, nie zgadywana"
    działa nie tylko dla 11 zwiadowców EXP, ale dla wszystkich aktywnych neuronów.

    prog_redundancji:    |corr| > prog → para nadmiarowa (kandydat do wagi w dół / scalenia)
    prog_dywersyfikacji: |corr| < prog → para dywersyfikująca (filar siły Imperium)

    Zwraca strukturę zgodną kształtem z `raport_dekorelacji` (do wspólnego formatera).
    """
    macierz = kolektor.korelacje()
    redundantne = []
    dywersyfikujace = []
    for (a, b), kor in macierz.items():
        if abs(kor) > prog_redundancji:
            redundantne.append((a, b, round(kor, 3)))
        elif abs(kor) < prog_dywersyfikacji:
            dywersyfikujace.append((a, b, round(kor, 3)))
    redundantne.sort(key=lambda t: -abs(t[2]))
    dywersyfikujace.sort(key=lambda t: abs(t[2]))
    return {
        "liczba_modulow": len(kolektor.klucze()),
        "liczba_krokow": kolektor.liczba_krokow(),
        "pary_redundantne": redundantne,
        "pary_dywersyfikujace": dywersyfikujace,
        "pary_nieokreslone": [],          # kolektor pomija nieokreślone u źródła
        "pary_niedostateczne_dane": [],
        "moduly_stale": [],               # stałe serie nie wchodzą do macierzy (None)
        "prog_redundancji": prog_redundancji,
        "prog_dywersyfikacji": prog_dywersyfikacji,
        "macierz": {f"{a}~{b}": k for (a, b), k in macierz.items()},
    }


def sformatuj_raport(rap: Dict[str, Any]) -> str:
    """Czytelny tekst raportu dekorelacji — do konsoli/logu."""
    linie = []
    linie.append("📊 RAPORT DEKORELACJI ZWIADOWCÓW (Prawo XV)")
    linie.append(f"  Modułów: {rap['liczba_modulow']}, kroków: {rap['liczba_krokow']}")

    if rap["moduly_stale"]:
        linie.append(f"\n🚨 MARTWE GŁOSY (zawsze NEUTRAL w oknie): {rap['moduly_stale']}")
        linie.append("   → UTRATA POTENCJAŁU: moduł nic nie wnosi na tych danych.")

    linie.append(f"\n🔴 PARY NADMIAROWE (|kor| > {rap['prog_redundancji']}):")
    if rap["pary_redundantne"]:
        for a, b, k in rap["pary_redundantne"]:
            linie.append(f"   {a} ~ {b}: {k:+.3f}  → kandydat do scalenia / wagi w dół")
    else:
        linie.append("   (brak — dobrze, mało nadmiarowości)")

    linie.append(f"\n🟢 PARY DYWERSYFIKUJĄCE (|kor| < {rap['prog_dywersyfikacji']}):")
    if rap["pary_dywersyfikujace"]:
        for a, b, k in rap["pary_dywersyfikujace"]:
            linie.append(f"   {a} ~ {b}: {k:+.3f}  → filar siły (niezależna informacja)")
    else:
        linie.append("   (brak — sygnały podobne, rozważ większą różnorodność)")

    return "\n".join(linie)
