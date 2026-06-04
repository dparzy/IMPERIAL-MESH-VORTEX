"""
⚔️ IMV-INS | Neurony Fraktalne — kategoria H (Hurst / pamięć długiego zasięgu).

Kategoria H to META-BRAMA reżimu: nie kolejny głos kierunkowy, lecz odpowiedź na
pytanie „czy rynek W OGÓLE ma teraz przewagę i jakiego typu?". Mierzy pamięć
długiego zasięgu wykładnikiem Hursta — odrębna oś informacji od Trendu (T, siła
kierunku) i Zmienności (V, magnituda wahań).
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronHurstDFA(MikroNeuron):
    """
    H-01 | Hurst-DFA Regime Gate — meta-brama reżimu z pamięci długiego zasięgu.

    Dla nowicjusza: wykładnik Hursta (H) mówi, czy rynek ma „pamięć":
      H > 0.55 → PERSYSTENCJA: trend ma kontynuację → potwierdza trend-following
                 (kierunek wg lokalnej EMA — podążaj za ruchem).
      H < 0.45 → ANTYPERSYSTENCJA: mean-reversion → graj PRZECIW bieżącemu ruchowi.
      0.45–0.55 → BŁĄDZENIE LOSOWE: brak przewagi → NEUTRAL z przekonaniem
                 (meta-brama mówi „nie handluj" — to jej najważniejsza rola).

    Metoda: DFA (Detrended Fluctuation Analysis) z Bramy (`HURST_DFA_100`).
    DFA detrenduje każde okno wielomianem, więc jest odporny na niestacjonarność
    (trendy) — w przeciwieństwie do R/S. To czyni H-01 KOMPLEMENTARNYM, nie
    redundantnym, względem EXP-03 ZwiadowcaHurst (R/S): na silnie trendującym
    krypto oba estymatory dają różne H → dekorelacja (Prawo XVI, krzyżowe
    potwierdzenie jak duet Higuchi FD + Hurst R/S). Korelacja do zmierzenia
    `diagnostyka_korelacji` po zebraniu danych paper-tradingu.

    Źródło: Peng i in. (1994), Phys. Rev. E 49:1685.
    """
    KLUCZ = "H-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "HURST_DFA_100"
    KATEGORIA = "H"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _H_TREND = 0.55      # H > _H_TREND → persystencja (trend)
    _H_MEANREV = 0.45    # H < _H_MEANREV → antypersystencja (mean-reversion)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        h = wskazniki.get("HURST_DFA_100")
        if h is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak HURST_DFA_100"])

        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")
        # Płaska cena (close == close_prev) NIE jest kierunkowa — None = brak ruchu.
        if close is None or close_prev is None or close == close_prev:
            kierunek_ruchu = None
        else:
            kierunek_ruchu = "LONG" if close > close_prev else "SHORT"

        if h > self._H_TREND:
            # Persystencja → potwierdza podążanie za bieżącym ruchem
            pewnosc = min(0.90, 0.60 + (h - self._H_TREND) * 1.5)
            if kierunek_ruchu is None:
                return self._bazowy_sygnal(h, "NEUTRAL", 0.30,
                    [f"H={h:.3f} > {self._H_TREND} — persystencja, ale brak kierunku ceny"])
            return self._bazowy_sygnal(h, kierunek_ruchu, round(pewnosc, 4),
                [f"H={h:.3f} > {self._H_TREND} — PERSYSTENCJA (DFA), trend ma pamięć → podążaj"])

        if h < self._H_MEANREV:
            # Antypersystencja → kontrariańsko, przeciw bieżącemu ruchowi
            pewnosc = min(0.85, 0.58 + (self._H_MEANREV - h) * 1.5)
            if kierunek_ruchu is None:
                return self._bazowy_sygnal(h, "NEUTRAL", 0.30,
                    [f"H={h:.3f} < {self._H_MEANREV} — mean-reversion, ale brak kierunku ceny"])
            kontra = "SHORT" if kierunek_ruchu == "LONG" else "LONG"
            return self._bazowy_sygnal(h, kontra, round(pewnosc, 4),
                [f"H={h:.3f} < {self._H_MEANREV} — ANTYPERSYSTENCJA (DFA), mean-reversion → kontra"])

        # Random walk — meta-brama: brak przewagi (to NAJWAŻNIEJSZY sygnał gate'a)
        return self._bazowy_sygnal(h, "NEUTRAL", 0.0,
            [f"H={h:.3f} — błądzenie losowe ({self._H_MEANREV}–{self._H_TREND}), "
             f"META-BRAMA: brak przewagi, nie handluj"])
