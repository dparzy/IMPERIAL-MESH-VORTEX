"""
🚨 IMV-INS | Neurony Zagrożenia — kategoria Z (Zagrożenie / Threat).

Kategoria Z to META-BRAMA OBRONNA: nie kolejny głos kierunkowy (LONG/SHORT), lecz
odpowiedź na pytanie „jak NIEBEZPIECZNIE jest teraz handlować?". Mierzy toksyczność
przepływu zleceń (VPIN) — czy gracze poinformowani (wieloryby, market makerzy)
handlują PRZECIWKO tłumowi, co poprzedza kaskady likwidacji. Jak H-01 (Hurst) i
N-01 (Permutation Entropy) — to brama, nie głos. Tłumi rój przez
`pewnosc_przeciwnika`, nigdy nie wskazuje kierunku.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronToxicFlow(MikroNeuron):
    """
    Z-01 | VPIN ToxicFlow — radar toksycznego przepływu (meta-brama obronna).

    Dla nowicjusza: VPIN (Volume-Synchronized Probability of Informed Trading —
    wolumenowo-synchronizowane prawdopodobieństwo handlu poinformowanego) mierzy
    „toksyczność" przepływu zleceń: czy duzi, poinformowani gracze (wieloryby,
    market makerzy) handlują przeciwko tłumowi. Liczony metodą BVC (Bulk Volume
    Classification — masowa klasyfikacja wolumenu): z czystych zmian ceny szacujemy,
    jaka część wolumenu była „kupnem", a jaka „sprzedażą", i sumujemy ich nierównowagę.

    Z-01 to META-BRAMA OBRONNA — NIE wybiera LONG/SHORT, tylko sygnalizuje POZIOM
    ZAGROŻENIA i tłumi cały rój przez pewnosc_przeciwnika:
      VPIN < 0.3  → SPOKÓJ: przepływ nietoksyczny, NEUTRAL, pewnosc_przeciwnika 0.0.
      0.3–0.7     → CZUJNOŚĆ: przepływ częściowo toksyczny, NEUTRAL ze skromnym
                    pewnosc_przeciwnika skalowanym VPIN-em (lekkie tłumienie).
      VPIN > 0.7  → 🚨 CZERWONY ALARM: TOKSYCZNY PRZEPŁYW, ryzyko kaskady likwidacji
                    → NEUTRAL z WYSOKIM pewnosc_przeciwnika (silne tłumienie roju:
                    „nie wchodź / schodź z lewara"). To jego NAJWAŻNIEJSZA rola.

    Dlaczego ORTOGONALNY (Prawo XVI): VPIN mierzy KTO handluje (struktura przepływu),
    nie GDZIE idzie cena. To inna oś niż Momentum/Trend/Zmienność i komplementarna do
    kategorii A (anty-manipulacja): A wykrywa ŚLAD konkretnej zagrywki (stop hunt,
    wash vol) w jednej świecy, Z mierzy AGREGAT toksyczności przepływu w oknie —
    krzyżowe potwierdzenie zagrożenia z dwóch niezależnych perspektyw.

    Metoda: VPIN z Bramy (`VPIN_50`, BVC, n_buckets=50, proxy barowy), wynik ∈ [0,1].
    Źródło: Easley, López de Prado, O'Hara (2012), „Flow Toxicity and Liquidity in a
            High-Frequency World", Review of Financial Studies 25(5):1457,
            https://doi.org/10.1093/rfs/hhs053
    """
    KLUCZ = "Z-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "VPIN_50"
    KATEGORIA = "Z"
    WAGA = 8
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _VPIN_SPOKOJ = 0.3    # VPIN < _VPIN_SPOKOJ → spokój, przepływ nietoksyczny
    _VPIN_ALARM = 0.7     # VPIN > _VPIN_ALARM → czerwony alarm, toksyczny przepływ

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        v = wskazniki.get("VPIN_50")
        if v is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak VPIN_50"])

        if v < self._VPIN_SPOKOJ:
            return self._bazowy_sygnal(v, "NEUTRAL", 0.0,
                [f"VPIN={v:.3f} < {self._VPIN_SPOKOJ} — spokój, przepływ nietoksyczny"])

        if v > self._VPIN_ALARM:
            # Czerwony alarm — silne tłumienie roju przez pewnosc_przeciwnika
            przeciwnik = min(0.95, 0.6 + (v - self._VPIN_ALARM) * 1.5)
            s = self._bazowy_sygnal(v, "NEUTRAL", 0.0,
                [f"VPIN={v:.3f} > {self._VPIN_ALARM} — 🚨 TOKSYCZNY PRZEPŁYW, "
                 f"ryzyko kaskady likwidacji — nie wchodź / schodź z lewara"])
            s.pewnosc_przeciwnika = round(przeciwnik, 4)
            s.policz_finalna()
            return s

        # Czujność — skromne tłumienie skalowane VPIN-em
        przeciwnik = round(v * 0.5, 4)
        s = self._bazowy_sygnal(v, "NEUTRAL", 0.0,
            [f"VPIN={v:.3f} — czujność, przepływ częściowo toksyczny"])
        s.pewnosc_przeciwnika = przeciwnik
        s.policz_finalna()
        return s
