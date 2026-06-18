"""
⚔️ IMV-INS | Neurony Zmiany Reżimu — kategoria R (Regime).

CP-01 wykrywa PRZEŁOM strukturalny (CUSUM change-point), nie siłę trwającego ruchu.
BOCPD-01 daje Bayesowskie P(zmiana reżimu w tym barze) — ciągłe, nie binarne.
Oba ortogonalne do momentum/trendu (Prawo XVI): sygnał wczesny o ZMIANIE, nie podążający.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu
from imperium.legiony.zmiana_rezimu import cusum_break
from imperium.legiony.bocpd import bocpd_changepoint_prob


class NeuronChangePoint(MikroNeuron):
    """
    CP-01 | CUSUM Change-Point — przełom reżimu z filtra CUSUM (AFML Ch17, Page 1954).

    Czyta CLOSE_SERIES_60 (Budowniczy). Świeży przełom w górę → LONG (nowy reżim byczy),
    w dół → SHORT. Brak świeżego przełomu → NEUTRAL z niską pewnością (rynek w trendzie,
    bez przełamania — to nie domena tego neuronu).
    """
    KLUCZ = "CP-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CLOSE_SERIES_60"
    KATEGORIA = "R"
    WAGA = 6
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_H = 5.0

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        serie = wskazniki.get("CLOSE_SERIES_60")
        if not serie or len(serie) < 21:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CLOSE_SERIES_60"])

        kier, sila = cusum_break(serie, prog_h=self._PROG_H)
        if kier is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.10,
                                       ["Brak świeżego przełomu CUSUM"])
        if kier == "LONG":
            return self._bazowy_sygnal(sila, "LONG", sila,
                [f"Przełom CUSUM w górę (siła {sila:.2f}) — nowy reżim byczy"])
        return self._bazowy_sygnal(sila, "SHORT", sila,
            [f"Przełom CUSUM w dół (siła {sila:.2f}) — nowy reżim niedźwiedzi"])


class NeuronBOCPD(MikroNeuron):
    """
    BOCPD-01 | Bayesian Online Change-Point Detection (Adams & MacKay 2007).

    Czyta CLOSE_SERIES_60 (Budowniczy). W każdym barze oblicza P(zmiana reżimu)
    jako margines posterior run-length = 0. Wysoka P(zmiana) + kierunek nowego reżimu
    (średni zwrot nowego vs poprzedniego run) → LONG lub SHORT.

    Ortogonalny do CP-01 (Prawo XVI): CP-01 = progowy detektor progowy; BOCPD = ciągłe
    prawdopodobieństwo Bayesowskie per-bar. Inna matematyka, inna kalibracja.
    Hazard λ=30 = oczekiwana długość reżimu 30 barów.
    """
    KLUCZ = "BOCPD-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CLOSE_SERIES_60"
    KATEGORIA = "R"
    WAGA = 6
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_P = 0.30       # próg P(zmiana) → sygnał kierunkowy
    _HAZARD_LAMBDA = 30  # oczekiwana długość reżimu (bary)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        serie = wskazniki.get("CLOSE_SERIES_60")
        if not serie or len(serie) < 12:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CLOSE_SERIES_60"])

        p_change, kier_sila = bocpd_changepoint_prob(
            serie, hazard_lambda=self._HAZARD_LAMBDA
        )
        if p_change is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Za mało danych BOCPD"])

        if p_change < self._PROG_P:
            return self._bazowy_sygnal(
                p_change, "NEUTRAL", p_change * 0.3,
                [f"P(zmiana)={p_change:.2f} < próg {self._PROG_P} — brak przełomu"]
            )

        # Kierunek: nowy reżim byczo/niedźwiedzi wg różnicy średnich run
        pewnosc = min(1.0, 0.30 + p_change * 0.7)
        if kier_sila > 0:
            return self._bazowy_sygnal(
                p_change, "LONG", pewnosc,
                [f"BOCPD P={p_change:.2f} — nowy reżim byczy (Δμ={kier_sila:.4f})"]
            )
        if kier_sila < 0:
            return self._bazowy_sygnal(
                p_change, "SHORT", pewnosc,
                [f"BOCPD P={p_change:.2f} — nowy reżim niedźwiedzi (Δμ={kier_sila:.4f})"]
            )
        return self._bazowy_sygnal(
            p_change, "NEUTRAL", p_change * 0.5,
            [f"BOCPD P={p_change:.2f} — zmiana bez wyraźnego kierunku"]
        )
