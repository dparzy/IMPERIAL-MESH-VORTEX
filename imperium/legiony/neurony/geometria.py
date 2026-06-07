"""
⚔️ IMV-INS | Neurony Geometrii Ścieżki — kategoria D (Dynamika ścieżkowa).

Kategoria D mierzy GEOMETRIĘ trajektorii ceny w przestrzeni wielowymiarowej,
nie pojedyncze wartości wskaźników. Metoda Rough Path Theory (Chen's Iterated
Integrals) wychwytuje strukturę SEKWENCYJNĄ sygnału — kolejność zdarzeń ma
znaczenie (nieprzemienność), co jest niewidoczne dla korelacji liniowej czy
Fouriera. Lévy Area (iterated integral rzędu 2 między Close a Volume) mierzy
"obszar zamknięty" ścieżki w przestrzeni (Close, Volume) — dodatni obszar
oznacza, że wzrostom ceny towarzyszyły wzrosty wolumenu ZANIM cena wzrosła
(przyczynowość: akumulacja poprzedza ruch). Ujemny obszar: odwrotna kolejność
(dystrybucja). Zerowy obszar: brak synchronizacji (chaos).

Ortogonalność (Prawo XVI): Signature nie mierzy poziomu (RSI), siły kierunku
(T), entropii wzorców (N), ani zmienności (V). Mierzy TOPOLOGIĘ ścieżki —
nieprzemienność kolejności zdarzeń. Zmierz `diagnostyka_korelacji` po
zebraniu danych paper-tradingu.

Źródła:
  Chen (1958), Ann. Math. 65:163 — iterated integrals
  Lyons et al. (2007), Lecture Notes in Mathematics 1908, Springer
  arXiv:1307.7244 — Path Signature Features, Gyurkó et al.
  arXiv:2503.02680 — Market microstructure signatures
  arXiv:2505.05332 — Lévy area in financial time series
"""

import math
from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


def _levy_area(x: list, y: list) -> float | None:
    """
    Lévy Area między dwoma sygnałami x i y (iterated integral rzędu 2).

    LA(x,y) = ∫∫_{s<t} (dx_s · dy_t − dy_s · dx_t) / 2
             ≈ Σ_{i<j} (Δx_i · Δy_j − Δy_i · Δx_j) / 2

    Efektywna implementacja: LA = (Σ_i x_i * Δy_i - Σ_i y_i * Δx_i) / 2
    gdzie suma to całkowanie Stratonovicza (środkowe) — równoważne definicji.

    Zwraca wartość znormalizowaną przez długość ścieżki (scale-invariant),
    lub None gdy brak danych / zerowa długość.
    """
    n = len(x)
    if n != len(y) or n < 3:
        return None

    # Przyrosty
    dx = [x[i] - x[i - 1] for i in range(1, n)]
    dy = [y[i] - y[i - 1] for i in range(1, n)]

    # Lévy Area: LA = 0.5 * (Σ x_{i} * dy_{i} - Σ y_{i} * dx_{i})
    # (indeksowane od 1, używamy lewego punktu każdego kroku)
    la_raw = 0.0
    for i in range(len(dx)):
        la_raw += x[i] * dy[i] - y[i] * dx[i]
    la_raw *= 0.5

    # Normalizacja: długość ścieżki w przestrzeni (Close, Volume)
    path_len = sum(math.sqrt(dx[i] ** 2 + dy[i] ** 2) for i in range(len(dx)))
    if path_len < 1e-12:
        return None

    return la_raw / (path_len ** 2 + 1e-12)


class NeuronPathSignature(MikroNeuron):
    """
    D-01 | Path Signature — Lévy Area Close×Volume.

    Dla nowicjusza: wyobraź sobie, że cena i wolumen razem rysują ścieżkę na
    papierze (oś X = cena, oś Y = wolumen). Lévy Area to POLE powierzchni
    zakreślonej przez tę ścieżkę. Gdy byki najpierw kupują (wolumen rośnie),
    a potem cena rośnie — ścieżka "zakręca w prawo" → pole dodatnie → LONG.
    Gdy cena rośnie bez wolumenu (słaba podstawa) lub z opóźnionym wolumenem —
    ścieżka "zakręca w lewo" → pole ujemne → SHORT.

    Obliczenie: iterated integral rzędu 2 z Rough Path Theory, czyste NumPy
    (bez zewnętrznych bibliotek). Okno: 20 barów (W-079 rekomendacja).

    Wskaźniki wymagane (z Bramy):
      CLOSE_SERIES_20  — lista 20 zamknięć (najnowsze ostatnie)
      VOLUME_SERIES_20 — lista 20 wolumenów (najnowsze ostatnie)

    Kryterium elitarności E1 (Exploratores, Prawo XX):
      Signature jest jedyną w Imperium miarą nieprzemiennej geometrii ścieżki.
      Zero modułów konkurencyjnych (|r| ≈ 0.00 z T/M/V/N na podstawie teorii).
    """
    KLUCZ = "D-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CLOSE_SERIES_20"
    KATEGORIA = "D"
    WAGA = 7
    ELITARNY = True
    POWOD_ELITARNOSCI = (
        "E1: jedyna miara nieprzemiennej geometrii ścieżki (Lévy Area) w Imperium; "
        "zero overlap z T/M/V/N — inna oś informacji (Prawo XX, kryterium E1)"
    )

    _LA_STRONG = 0.20    # |LA| > 0.20 → silny sygnał geometryczny (pewnosc 0.75)
    _LA_WEAK = 0.07      # |LA| > 0.07 → słaby sygnał (pewnosc 0.55)
    _WINDOW = 20

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        closes = wskazniki.get("CLOSE_SERIES_20")
        volumes = wskazniki.get("VOLUME_SERIES_20")

        if not closes or not volumes:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CLOSE_SERIES_20 / VOLUME_SERIES_20"])

        if len(closes) < 3 or len(volumes) < 3:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Za krótka seria (min 3 bary)"])

        # Normalizuj serie do [0,1] (scale-invariant — Prawo XVI)
        c_min, c_max = min(closes), max(closes)
        v_min, v_max = min(volumes), max(volumes)

        c_range = c_max - c_min
        v_range = v_max - v_min

        if c_range < 1e-12:
            # Płaska cena — brak geometrii
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Płaska cena — brak geometrii ścieżki"])

        c_norm = [(c - c_min) / c_range for c in closes]
        v_norm = [(v - v_min) / v_range for v in volumes] if v_range > 1e-12 else [0.5] * len(volumes)

        la = _levy_area(c_norm, v_norm)
        if la is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Błąd obliczenia Lévy Area"])

        abs_la = abs(la)

        if abs_la < self._LA_WEAK:
            return self._bazowy_sygnal(
                la, "NEUTRAL", 0.0,
                [f"Lévy Area {la:.4f} — brak geometrycznej struktury"]
            )

        kierunek = "LONG" if la > 0 else "SHORT"

        if abs_la >= self._LA_STRONG:
            pewnosc = 0.55 + 0.30 * min((abs_la - self._LA_STRONG) / 0.30, 1.0)
        else:
            pewnosc = 0.55

        pewnosc = round(min(pewnosc, 0.85), 4)

        return self._bazowy_sygnal(
            la, kierunek, pewnosc,
            [f"Lévy Area {la:.4f} → {kierunek} (pewnosc {pewnosc:.2f})"]
        )
