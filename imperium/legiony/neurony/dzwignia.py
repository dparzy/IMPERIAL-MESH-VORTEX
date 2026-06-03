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

    Logika:
      HIST_VOL_20 (annualized std log returns × √252):
      < 0.30  → niska zmienność → LONG (wchodzimy, środowisko sprzyjające)
      0.30–0.60 → normalna → NEUTRAL
      0.60–0.90 → wysoka → SHORT (ostrożnie, reżim VOLATILE)
      > 0.90  → ekstremalna → SHORT silny (obrona kapitału)

    Kategoria V (Zmienność) informuje Namiestnika i Legatusa o reżimie.
    Dekoreluje z kategorią T (Trend) — trend może być silny przy niskiej vol.
    """
    KLUCZ = "V-13"
    LEGION = "WSPOLNY"
    WSKAZNIK = "HIST_VOL_20"
    KATEGORIA = "V"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_NISKA = 0.30
    _PROG_NORMALNA = 0.60
    _PROG_WYSOKA = 0.90

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        hv = wskazniki.get("HIST_VOL_20")

        if hv is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak HIST_VOL_20"])

        if hv < self._PROG_NISKA:
            return self._bazowy_sygnal(hv, "LONG", 0.65,
                [f"HV={hv:.1%} — niska zmienność, sprzyjające środowisko"])

        if hv < self._PROG_NORMALNA:
            return self._bazowy_sygnal(hv, "NEUTRAL", 0.40,
                [f"HV={hv:.1%} — normalna zmienność BTC"])

        if hv < self._PROG_WYSOKA:
            return self._bazowy_sygnal(hv, "SHORT", 0.60,
                [f"HV={hv:.1%} — wysoka zmienność, ostrożnie"])

        return self._bazowy_sygnal(hv, "SHORT", 0.78,
            [f"HV={hv:.1%} — ekstremalna zmienność, obrona kapitału"])
