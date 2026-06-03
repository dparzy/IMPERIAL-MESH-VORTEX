"""
⚔️ IMV-INS | Neurony Dźwigni i Zmienności — kategorie L i V.

Kategoria L (Leverage/Dźwignia): modulacja pozycji względem ryzyka ATR.
Kategoria V (Zmienność): pomiar realized volatility dla oceny reżimu.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronATRLev(MikroNeuron):
    """
    VI-13 | ATR-Leverage Score — ocena bezpiecznej dźwigni na bazie ATR.

    Dla nowicjusza: ATR (Average True Range) mierzy, jak bardzo cena "skacze"
    w ciągu dnia. Im większe skoki, tym mniejsza dźwignia jest bezpieczna.
    Ten neuron daje sygnał: gdy ATR jest mały (spokojny rynek) → LONG bias
    (bezpiecznie wejść z dźwignią), gdy ATR wielki (turbulencja) → SHORT bias
    (poczekaj / redukuj ryzyko).

    Logika:
      ATR_rel = ATR_14 / CLOSE (relatywny ATR)
      < 0.5%  → bardzo spokojny → LONG (safe leverage zone)
      0.5–2%  → normalny → NEUTRAL
      > 2%    → turbulencja → SHORT (reduce leverage)
      > 4%    → ekstremalne → SHORT silny (stój z boku)

    Źródło: systematyczny trend-following (arXiv:2602.11708) — position sizing
    przez ATR jest branżowym standardem.
    """
    KLUCZ = "VI-13"
    LEGION = "WSPOLNY"
    WSKAZNIK = "ATR_14"
    KATEGORIA = "L"
    WAGA = 8
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_SPOKOJNY = 0.005   # ATR/CLOSE < 0.5% → bardzo spokojny
    _PROG_NORMALNY = 0.020   # ATR/CLOSE < 2.0% → normalny
    _PROG_EKSTREMALNY = 0.040  # ATR/CLOSE > 4.0% → ekstremalne

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        atr = wskazniki.get("ATR_14")
        close = wskazniki.get("CLOSE")

        if atr is None or close is None or close <= 0:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak ATR_14"])

        atr_rel = atr / close

        if atr_rel < self._PROG_SPOKOJNY:
            sila = 0.65
            return self._bazowy_sygnal(atr_rel, "LONG", sila,
                [f"ATR rel={atr_rel:.3%} — bardzo spokojny rynek, bezpieczna dźwignia"])

        if atr_rel <= self._PROG_NORMALNY:
            return self._bazowy_sygnal(atr_rel, "NEUTRAL", 0.40,
                [f"ATR rel={atr_rel:.3%} — normalna zmienność"])

        if atr_rel <= self._PROG_EKSTREMALNY:
            sila = 0.60 + (atr_rel - self._PROG_NORMALNY) / (self._PROG_EKSTREMALNY - self._PROG_NORMALNY) * 0.15
            return self._bazowy_sygnal(atr_rel, "SHORT", sila,
                [f"ATR rel={atr_rel:.3%} — turbulencja, redukuj dźwignię"])

        return self._bazowy_sygnal(atr_rel, "SHORT", 0.80,
            [f"ATR rel={atr_rel:.3%} — ekstremalny ruch, NIE handluj z dźwignią"])


class NeuronRealizedVol(MikroNeuron):
    """
    V-13 | Realized Volatility Regime — klasyfikacja zmienności rynku.

    Dla nowicjusza: Historyczna zmienność (HV) mierzy, jak bardzo cena wahała
    się przez ostatnie 20 dni. Annualizowana: 30% = typowy spokojny BTC,
    60%+ = wysoka zmienność, 100%+ = chaos/mania.

    Estymator (Prawo XV — pełne wykorzystanie OHLC, wizja W-055):
      PODSTAWA: YANG_ZHANG_20 — annualizowana vol z pełnego OHLC (open/high/low/
        close). ~14× efektywniejszy statystycznie niż close-only, odporny na luki
        overnight i drift (Yang & Zhang, 2000).
      FALLBACK: HIST_VOL_20 — gdy brak pełnego OHLC (np. seria tylko-close),
        neuron nie milknie, tylko schodzi na estymator close-only.
    Obie liczby są w TEJ SAMEJ skali (annualizowana vol × √252), więc progi
    reżimu pozostają ważne niezależnie od użytego estymatora.

    Logika progów (annualized realized vol):
      < 0.30  → niska zmienność → LONG (wchodzimy, środowisko sprzyjające)
      0.30–0.60 → normalna → NEUTRAL
      0.60–0.90 → wysoka → SHORT (ostrożnie, reżim VOLATILE)
      > 0.90  → ekstremalna → SHORT silny (obrona kapitału)

    Kategoria V (Zmienność) informuje Namiestnika i Legatusa o reżimie.
    Dekoreluje z kategorią T (Trend) — trend może być silny przy niskiej vol.
    """
    KLUCZ = "V-13"
    LEGION = "WSPOLNY"
    WSKAZNIK = "YANG_ZHANG_20"
    KATEGORIA = "V"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_NISKA = 0.30
    _PROG_NORMALNA = 0.60
    _PROG_WYSOKA = 0.90

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        hv = wskazniki.get("YANG_ZHANG_20")
        zrodlo = "YZ"
        if hv is None:
            hv = wskazniki.get("HIST_VOL_20")   # fallback close-only (Prawo XV: bez martwego głosu)
            zrodlo = "HV"

        if hv is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak YANG_ZHANG_20/HIST_VOL_20"])

        if hv < self._PROG_NISKA:
            return self._bazowy_sygnal(hv, "LONG", 0.65,
                [f"{zrodlo}={hv:.1%} — niska zmienność, sprzyjające środowisko"])

        if hv < self._PROG_NORMALNA:
            return self._bazowy_sygnal(hv, "NEUTRAL", 0.40,
                [f"{zrodlo}={hv:.1%} — normalna zmienność BTC"])

        if hv < self._PROG_WYSOKA:
            return self._bazowy_sygnal(hv, "SHORT", 0.60,
                [f"{zrodlo}={hv:.1%} — wysoka zmienność, ostrożnie"])

        return self._bazowy_sygnal(hv, "SHORT", 0.78,
            [f"{zrodlo}={hv:.1%} — ekstremalna zmienność, obrona kapitału"])


class NeuronChoppiness(MikroNeuron):
    """
    V-14 | Choppiness Index — trend kontra konsolidacja (kategoria V).

    Dla nowicjusza: Choppiness Index (CHOP) mówi, czy rynek IDZIE w jedną stronę
    (trend), czy "miele w miejscu" (konsolidacja/piła). Skala 0–100:
      > 61.8 → konsolidacja (piła) → SHORT bias (nie goń wybić, fałszywe ruchy)
      38.2–61.8 → strefa przejściowa → NEUTRAL
      < 38.2 → silny trend → LONG bias (ruch jest efektywny, podążaj)

    Dlaczego osobny neuron od V-13 (Realized Volatility): HV mierzy MAGNITUDĘ
    wahań (jak mocno), CHOP mierzy EFEKTYWNOŚĆ ruchu (czy dokądś zmierza).
    Rynek może mieć wysoką HV i niski CHOP (silny zmienny trend) — to różna
    informacja, więc dekoreluje (Prawo XVI).

    Źródło: E.W. Dreiss, Choppiness Index (commodity trading, lata 90.) —
    branżowy wskaźnik reżimu trend/range.
    """
    KLUCZ = "V-14"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CHOPPINESS_14"
    KATEGORIA = "V"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_TREND = 38.2      # < 38.2 → silny trend
    _PROG_KONSOLIDACJA = 61.8  # > 61.8 → konsolidacja (piła)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        chop = wskazniki.get("CHOPPINESS_14")

        if chop is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CHOPPINESS_14"])

        if chop < self._PROG_TREND:
            return self._bazowy_sygnal(chop, "LONG", 0.62,
                [f"CHOP={chop:.1f} — silny trend, ruch efektywny (podążaj)"])

        if chop <= self._PROG_KONSOLIDACJA:
            return self._bazowy_sygnal(chop, "NEUTRAL", 0.40,
                [f"CHOP={chop:.1f} — strefa przejściowa"])

        return self._bazowy_sygnal(chop, "SHORT", 0.60,
            [f"CHOP={chop:.1f} — konsolidacja/piła, unikaj fałszywych wybić"])


class NeuronUlcer(MikroNeuron):
    """
    L-14 | Ulcer Index — ryzyko spadkowe modulujące dźwignię (kategoria L).

    Dla nowicjusza: Ulcer Index (UI) mierzy "ból posiadania" — jak głębokie i
    jak długie były obsunięcia (drawdowny) w ostatnim oknie. W odróżnieniu od
    ATR (który liczy zwykły zakres, symetrycznie góra/dół), UI karze TYLKO ruch
    w dół. Im wyższy UI, tym mocniejsze osuwanie się ceny → mniejsza bezpieczna
    dźwignia.

    Logika:
      < 1%   → płytkie obsunięcia → LONG (bezpieczna dźwignia)
      1–4%   → umiarkowane → NEUTRAL
      > 4%   → bolesne obsunięcia → SHORT (redukuj dźwignię/ryzyko)
      > 8%   → ekstremalne → SHORT silny

    Dlaczego osobny neuron od VI-13 (ATR-Leverage): ATR jest symetryczny i mierzy
    POZIOM zmienności; UI mierzy ASYMETRIĘ spadkową (downside) — różna informacja,
    dekoreluje (Prawo XVI).

    Źródło: Peter Martin, "The Investor's Guide to Fidelity Funds" (1989) —
    Ulcer Index jako miara ryzyka downside.
    """
    KLUCZ = "L-14"
    LEGION = "WSPOLNY"
    WSKAZNIK = "ULCER_14"
    KATEGORIA = "L"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_PLYTKI = 1.0     # UI < 1% → płytkie obsunięcia
    _PROG_UMIARKOWANY = 4.0  # UI < 4% → umiarkowane
    _PROG_EKSTREMALNY = 8.0  # UI > 8% → ekstremalne

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ui = wskazniki.get("ULCER_14")

        if ui is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak ULCER_14"])

        if ui < self._PROG_PLYTKI:
            return self._bazowy_sygnal(ui, "LONG", 0.62,
                [f"UI={ui:.2f}% — płytkie obsunięcia, bezpieczna dźwignia"])

        if ui <= self._PROG_UMIARKOWANY:
            return self._bazowy_sygnal(ui, "NEUTRAL", 0.40,
                [f"UI={ui:.2f}% — umiarkowane ryzyko spadkowe"])

        if ui <= self._PROG_EKSTREMALNY:
            sila = 0.60 + (ui - self._PROG_UMIARKOWANY) / (self._PROG_EKSTREMALNY - self._PROG_UMIARKOWANY) * 0.15
            return self._bazowy_sygnal(ui, "SHORT", sila,
                [f"UI={ui:.2f}% — bolesne obsunięcia, redukuj dźwignię"])

        return self._bazowy_sygnal(ui, "SHORT", 0.80,
            [f"UI={ui:.2f}% — ekstremalne ryzyko spadkowe, obrona kapitału"])
