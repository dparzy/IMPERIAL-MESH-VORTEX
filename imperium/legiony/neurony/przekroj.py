"""
⚔️ IMV-INS | Neurony Przekrojowe — kategoria C (Cross-sectional / Relative Strength).

Kategoria C to NOWA OŚ informacji (deep research W-335): wszystkie pozostałe 72 neurony
patrzą na POJEDYNCZE aktywo w czasie (szereg czasowy). C patrzy PRZEKROJOWO — jak dane
aktywo wypada względem KOSZYKA pozostałych w tym samym momencie.

Dla nowicjusza: „relative strength" to nie RSI. To pytanie „czy ETH rośnie SZYBCIEJ niż
reszta koszyka?". Lider koszyka (najwyższy z-score zwrotu) ma tendencję do kontynuacji
(cross-sectional momentum — Jegadeesh-Titman 1993, potwierdzone dla krypto: Trend Factor
JFQA 2024). Maruder — do dalszego pozostawania w tyle. To informacja STRUKTURALNIE
ortogonalna do każdego sygnału jednoskładnikowego (Prawo XVI): zależy od RELACJI między
aktywami, nie od historii jednego.

Wejście: wskaznik CROSS_RS — z-score zwrotu tego aktywa względem koszyka, wstrzykiwany
przez pętlę portfelową (petla_live / backtest_portfel), która jako jedyna widzi wszystkie
symbole naraz. Bez koszyka (handel 1 aktywa) → brak CROSS_RS → neuron abstynuje (Prawo XV).

Źródło: cross-sectional momentum — Jegadeesh & Titman (1993); A Trend Factor for the
Cross Section of Cryptocurrency Returns, JFQA 2024 (⚠️ do potwierdzenia pełnego tekstu).
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronRelativeStrength(MikroNeuron):
    """
    C-01 | Cross-Sectional Relative Strength — siła względna w koszyku.

    Czyta CROSS_RS = z-score zwrotu aktywa względem koszyka (liczony przez pętlę
    portfelową, lookback konfigurowalny). Interpretacja (cross-sectional momentum):
      CROSS_RS ≥ +prog_silny  → lider koszyka → LONG (kontynuacja siły)
      CROSS_RS ≤ -prog_silny  → maruder       → SHORT (kontynuacja słabości)
      |CROSS_RS| w strefie pośredniej → słabszy głos proporcjonalny
      blisko 0 → NEUTRAL (zachowuje się jak koszyk, brak przewagi przekrojowej)

    Pewność rośnie z |z-score|, klamrowana (skrajne z-score bywają szumem/outlierem).
    """
    KLUCZ = "C-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "CROSS_RS"
    KATEGORIA = "C"
    WAGA = 6
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG_SILNY = 1.0       # |z| ≥ 1.0 → wyraźny lider/maruder
    _PROG_SLABY = 0.3       # |z| < 0.3 → praktycznie jak koszyk → NEUTRAL

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        rs = wskazniki.get("CROSS_RS")
        if rs is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                                       ["Brak CROSS_RS (handel pojedynczego aktywa?)"])

        if abs(rs) < self._PROG_SLABY:
            return self._bazowy_sygnal(rs, "NEUTRAL", 0.10,
                [f"RS={rs:+.2f} ~ koszyk (brak przewagi przekrojowej)"])

        # Pewność: liniowo od progu słabego do silnego, klamrowana 0.25..0.70
        sila = min(0.70, 0.25 + (abs(rs) - self._PROG_SLABY) * 0.30)
        if rs >= self._PROG_SILNY:
            return self._bazowy_sygnal(rs, "LONG", min(0.70, sila + 0.10),
                [f"RS={rs:+.2f} LIDER koszyka → kontynuacja siły"])
        if rs <= -self._PROG_SILNY:
            return self._bazowy_sygnal(rs, "SHORT", min(0.70, sila + 0.10),
                [f"RS={rs:+.2f} MARUDER koszyka → kontynuacja słabości"])
        # Strefa pośrednia: słabszy głos w kierunku znaku
        if rs > 0:
            return self._bazowy_sygnal(rs, "LONG", sila,
                [f"RS={rs:+.2f} lekka przewaga nad koszykiem"])
        return self._bazowy_sygnal(rs, "SHORT", sila,
            [f"RS={rs:+.2f} lekka słabość vs koszyk"])
