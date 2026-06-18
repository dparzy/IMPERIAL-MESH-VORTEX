"""
⚔️ IMV-INS | Neuron Zmiany Reżimu — kategoria R (Regime).

CP-01 wykrywa PRZEŁOM strukturalny (CUSUM change-point), nie siłę trwającego ruchu.
Ortogonalny do momentum/trendu (Prawo XVI): sygnał wczesny o ZMIANIE, nie podążający.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu
from imperium.legiony.zmiana_rezimu import cusum_break


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
