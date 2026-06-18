"""
⚔️ IMV-INS | Neurony Entropii/Pamięci — kategoria N (Entropia / Informacja).

Kategoria N:
  N-01 Permutation Entropy — META-BRAMA chaosu: czy rynek ma teraz STRUKTURĘ?
  N-02 Fractional Differentiation — META-MIERNIK PAMIĘCI: ile historii przeżywa
       stacjonaryzację? Niskie d → silna pamięć długiego zasięgu (persystencja),
       normalna wartość z_last mówi o kierunku zdekorelowanej składowej.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu
from imperium.legiony.frac_diff import frac_diff_signal


class NeuronPermutationEntropy(MikroNeuron):
    """
    N-01 | Permutation Entropy Chaos Gate — meta-brama chaosu z entropii porządkowej.

    Dla nowicjusza: Permutation Entropy (PE, entropia permutacyjna) mówi, czy rynek
    ma STRUKTURĘ, patrząc na wzorce porządku kolejnych cen (który punkt jest
    najmniejszy/średni/największy w oknie), a NIE na kierunek czy poziom ceny:
      PE > 0.85 → CHAOS: rynek efektywny, wszystkie wzorce równie częste → brak
                  przewagi → NEUTRAL z przekonaniem (meta-brama: „nie handluj" —
                  to jej NAJWAŻNIEJSZA rola, jak random walk dla H-01).
      PE < 0.65 → PRZEWIDYWALNOŚĆ: rynek nieefektywny, część wzorców „zakazana"
                  (forbidden patterns) → jest struktura → przewaga obecna. Ponieważ
                  PE jest BEZKIERUNKOWA, potwierdza bieżący mikro-ruch (CLOSE vs
                  CLOSE_PREV) ze skromną pewnością — jak H-01 czyta kierunek ceny.
      0.65–0.85 → szara strefa: NEUTRAL z niską pewnością.

    Dlaczego ORTOGONALNA do RSI/MACD (Prawo XVI): PE mierzy ZŁOŻONOŚĆ struktury
    porządku, nie poziom (RSI), nie crossover (MACD), nie magnitudę wahań (V), nie
    siłę kierunku (T). To inna oś informacji → dekoreluje z głosami kierunkowymi i
    z V/T/M. ~34% czulsza niż GARCH na klasteryzację zmienności. Korelacja do
    zmierzenia `diagnostyka_korelacji` po zebraniu danych paper-tradingu.

    Metoda: Bandt-Pompe PE z Bramy (`PERM_ENTROPY_100`, dim=3, delay=1, period=100),
    znormalizowana do [0,1] przez log(dim!).
    Źródło: Bandt & Pompe (2002), Phys. Rev. Lett. 88:174102,
            https://doi.org/10.1103/PhysRevLett.88.174102 (PMC7597144).
    """
    KLUCZ = "N-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "PERM_ENTROPY_100"
    KATEGORIA = "N"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PE_CHAOS = 0.85       # PE > _PE_CHAOS → chaos (brak przewagi, meta-brama STOP)
    _PE_STRUKTURA = 0.65   # PE < _PE_STRUKTURA → rynek przewidywalny (struktura)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        pe = wskazniki.get("PERM_ENTROPY_100")
        if pe is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak PERM_ENTROPY_100"])

        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")
        # Kierunek bieżącego mikro-ruchu; płaska cena (close == close_prev) NIE jest
        # kierunkowa — None oznacza brak ruchu (nie wymuszaj SHORT).
        if close is None or close_prev is None or close == close_prev:
            kierunek_ruchu = None
        else:
            kierunek_ruchu = "LONG" if close > close_prev else "SHORT"

        if pe > self._PE_CHAOS:
            # Chaos → meta-brama: brak przewagi (to NAJWAŻNIEJSZY sygnał gate'a)
            return self._bazowy_sygnal(pe, "NEUTRAL", 0.0,
                [f"PE={pe:.3f} > {self._PE_CHAOS} — rynek chaotyczny (efektywny), "
                 f"META-BRAMA: brak struktury, nie handluj"])

        if pe < self._PE_STRUKTURA:
            # Przewidywalność → struktura obecna → potwierdza bieżący mikro-ruch
            pewnosc = min(0.80, 0.55 + (self._PE_STRUKTURA - pe) * 1.2)
            if kierunek_ruchu is None:
                return self._bazowy_sygnal(pe, "NEUTRAL", 0.30,
                    [f"PE={pe:.3f} < {self._PE_STRUKTURA} — struktura, ale brak kierunku ceny"])
            return self._bazowy_sygnal(pe, kierunek_ruchu, round(pewnosc, 4),
                [f"PE={pe:.3f} < {self._PE_STRUKTURA} — rynek PRZEWIDYWALNY "
                 f"(nieefektywny, forbidden patterns) → potwierdź ruch"])

        # Szara strefa — brak wyraźnej struktury ani pełnego chaosu
        return self._bazowy_sygnal(pe, "NEUTRAL", 0.20,
            [f"PE={pe:.3f} — szara strefa ({self._PE_STRUKTURA}–{self._PE_CHAOS}), "
             f"struktura niejednoznaczna"])


class NeuronFracDiff(MikroNeuron):
    """
    N-02 | Fractional Differentiation — persystencja pamięci długiego zasięgu.

    DLA NOWICJUSZA: standardowe zwroty (d=1) niszczą całą pamięć historyczną.
    Raw log-cena (d=0) jest niestacjonarna. FracDiff (d∈[0.1,1.0]) to kompromis:
    minimalne d zachowujące stacjonarność + maksymalna pamięć (López de Prado AFML Ch5).

    Czyta CLOSE_SERIES_100 (Budowniczy). Znajduje minimalne d (ADF quasi-stacjonarność),
    oblicza z_last (z-score ostatniej wartości znormalizowanej serii frac-diff).

    Sygnał kierunkowy z z_last:
      z_last > +PROG → LONG (zdekorelowana składowa rośnie)
      z_last < −PROG → SHORT
      inaczej → NEUTRAL (w zakresie szumu)

    d_opt diagnostyczne: małe d (<0.4) → silna pamięć długiego zasięgu (trend persystuje),
    duże d (≈1.0) → rynek bliski random walk (mała pamięć).

    Ortogonalna do N-01 (PE mierzy złożoność wzorców, FracDiff mierzy persystencję
    po stacjonaryzacji — różne matematyki, Prawo XVI).
    """
    KLUCZ = "N-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CLOSE_SERIES_100"
    KATEGORIA = "N"
    WAGA = 6
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_Z = 1.5      # |z_last| > PROG_Z → sygnał kierunkowy

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        serie = wskazniki.get("CLOSE_SERIES_100")
        if not serie or len(serie) < 31:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CLOSE_SERIES_100"])

        d_opt, z_last = frac_diff_signal(serie)
        if d_opt is None or z_last is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Za mało danych FracDiff"])

        pewnosc = min(1.0, abs(z_last) / (self._PROG_Z * 2.0))

        if z_last > self._PROG_Z:
            return self._bazowy_sygnal(
                z_last, "LONG", pewnosc,
                [f"FracDiff z={z_last:.2f} > {self._PROG_Z} (d={d_opt}) — persystentny ruch w górę"]
            )
        if z_last < -self._PROG_Z:
            return self._bazowy_sygnal(
                z_last, "SHORT", pewnosc,
                [f"FracDiff z={z_last:.2f} < -{self._PROG_Z} (d={d_opt}) — persystentny ruch w dół"]
            )
        return self._bazowy_sygnal(
            z_last, "NEUTRAL", pewnosc * 0.3,
            [f"FracDiff z={z_last:.2f} ∈ (-{self._PROG_Z}, {self._PROG_Z}) (d={d_opt}) — brak sygnału"]
        )
