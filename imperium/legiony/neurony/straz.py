"""
🛡️ IMV-INS | Neurony Straży — Dywizja Anty-Manipulacji (KATEGORIA A)

WIZJA (Cezar): musimy znać zagrywki przeciwnika (giełdy, market makerów, wielorybów)
i umieć je ROZPOZNAĆ oraz ODPOWIEDNIO ZAREAGOWAĆ. Te neurony to "kontrwywiad" Imperium —
wykrywają ślady manipulacji w czystej cenie OHLCV, bez potrzeby API.

Dlaczego KATEGORIA A jest ważna:
  W WAGI_REZIMU litera A ma najwyższe wagi w trudnych warunkach:
    VOLATILE → A ×2.0   |   PANIC → A ×3.0
  Bo gdy rynek szaleje, najważniejsze jest rozpoznać KTO gra nieczysto.
  Do tej pory litera A była "uśpiona" (pre-zarejestrowana, brak neuronu).
  Te neurony JĄ OŻYWIAJĄ — Prawo XV (potencjał wykorzystany).

Wszystkie neurony tu działają na czystym OHLCV (HIGH/LOW/CLOSE/OPEN + Donchian/ATR).
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronStopHunt(MikroNeuron):
    """
    A-01 | Stop Hunt / Liquidity Sweep — wykrywanie polowania na stop-lossy.

    Dla nowicjusza: Wielcy gracze (market makerzy) wiedzą, gdzie tłum ustawia
    stop-lossy — tuż pod ostatnim dołkiem lub nad ostatnim szczytem. Czasem
    celowo "pchają" cenę tam, żeby uruchomić te zlecenia (zebrać płynność),
    a potem gwałtownie zawracają. To "stop hunt" albo "liquidity sweep".

    Jak rozpoznajemy (sygnał kontrariański — gramy PRZECIW pułapce):
      Bullish sweep: LOW przebił dołek kanału (DONCHIAN_LOWER), ale CLOSE wrócił
                     POWYŻEJ niego → stopy poniżej zebrane, teraz odbicie → LONG
      Bearish sweep: HIGH przebił szczyt kanału (DONCHIAN_UPPER), ale CLOSE wrócił
                     PONIŻEJ niego → stopy powyżej zebrane, teraz spadek → SHORT

    Istotność: przebicie musi być znaczące względem zmienności (ATR_DEVIATION).
    """
    KLUCZ = "A-01"
    LEGION = "STRAZ"
    WSKAZNIK = "DONCHIAN"
    KATEGORIA = "A"
    WAGA = 8

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        high = wskazniki.get("HIGH")
        low = wskazniki.get("LOW")
        close = wskazniki.get("CLOSE")
        donch_hi = wskazniki.get("DONCHIAN_UPPER")
        donch_lo = wskazniki.get("DONCHIAN_LOWER")

        if None in (high, low, close, donch_hi, donch_lo):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych Stop Hunt."])

        zakres = donch_hi - donch_lo
        if zakres < 1e-9:
            return self._bazowy_sygnal(close, "NEUTRAL", 0.0, ["Kanał zbyt wąski."])

        # Bullish sweep: knot przebił dół, ale zamknięcie wróciło nad poziom
        if low < donch_lo and close > donch_lo:
            gleb = (donch_lo - low) / zakres  # jak głęboko sięgnął sweep
            pewnosc = min(0.85, 0.55 + gleb * 3)
            return self._bazowy_sygnal(close, "LONG", pewnosc,
                [f"🛡️ STOP HUNT BULL: LOW={low:.2f} przebił dół kanału ({donch_lo:.2f}), "
                 f"CLOSE={close:.2f} wrócił nad — stopy zebrane, odbicie (głęb. {gleb:.1%})"])

        # Bearish sweep: knot przebił górę, ale zamknięcie wróciło pod poziom
        if high > donch_hi and close < donch_hi:
            gleb = (high - donch_hi) / zakres
            pewnosc = min(0.85, 0.55 + gleb * 3)
            return self._bazowy_sygnal(close, "SHORT", pewnosc,
                [f"🛡️ STOP HUNT BEAR: HIGH={high:.2f} przebił szczyt kanału ({donch_hi:.2f}), "
                 f"CLOSE={close:.2f} wrócił pod — stopy zebrane, spadek (głęb. {gleb:.1%})"])

        return self._bazowy_sygnal(close, "NEUTRAL", 0.10,
            ["Brak sweepu — cena bez polowania na płynność"])


class NeuronWickRejection(MikroNeuron):
    """
    A-02 | Wick Rejection — odrzucenie poziomu przez długi knot.

    Dla nowicjusza: Świeca ma "ciało" (między open a close) i "knoty/cienie"
    (do high i low). Długi knot oznacza, że cena PRÓBOWAŁA iść w jakąś stronę,
    ale została gwałtownie ODRZUCONA — ktoś duży bronił poziomu.

    Logika (sygnał kontrariański względem odrzuconej strony):
      Długi GÓRNY knot + małe ciało → odrzucenie wyższych cen → SHORT
      Długi DOLNY knot + małe ciało → odrzucenie niższych cen → LONG

    Knot musi być znacznie większy od ciała (≥2×) i od przeciwnego knota.
    To klasyka price action — "pin bar" / "rejection candle".
    """
    KLUCZ = "A-02"
    LEGION = "STRAZ"
    WSKAZNIK = "OPEN"
    KATEGORIA = "A"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        o = wskazniki.get("OPEN")
        h = wskazniki.get("HIGH")
        low = wskazniki.get("LOW")
        c = wskazniki.get("CLOSE")

        if None in (o, h, low, c):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych Wick Rejection."])

        spread = h - low
        if spread < 1e-9:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.0, ["Świeca bez zakresu (doji płaski)."])

        cialo = abs(c - o)
        gorny_knot = h - max(o, c)
        dolny_knot = min(o, c) - low

        # Ciało nie może dominować (knot musi być wyraźny)
        cialo_frakcja = cialo / spread

        # Długi górny knot → odrzucenie góry → SHORT
        if gorny_knot >= 2 * cialo and gorny_knot > 1.5 * dolny_knot and cialo_frakcja < 0.4:
            sila = min(0.80, 0.50 + (gorny_knot / spread) * 0.5)
            return self._bazowy_sygnal(c, "SHORT", sila,
                [f"🛡️ WICK REJECT GÓRA: górny knot {gorny_knot:.2f} ≫ ciało {cialo:.2f} — "
                 f"odrzucenie wyższych cen ({gorny_knot/spread:.0%} świecy)"])

        # Długi dolny knot → odrzucenie dołu → LONG
        if dolny_knot >= 2 * cialo and dolny_knot > 1.5 * gorny_knot and cialo_frakcja < 0.4:
            sila = min(0.80, 0.50 + (dolny_knot / spread) * 0.5)
            return self._bazowy_sygnal(c, "LONG", sila,
                [f"🛡️ WICK REJECT DÓŁ: dolny knot {dolny_knot:.2f} ≫ ciało {cialo:.2f} — "
                 f"odrzucenie niższych cen ({dolny_knot/spread:.0%} świecy)"])

        return self._bazowy_sygnal(c, "NEUTRAL", 0.12,
            [f"Brak wyraźnego odrzucenia (ciało {cialo_frakcja:.0%} świecy)"])
