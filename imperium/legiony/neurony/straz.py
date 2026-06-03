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


class NeuronWashVol(MikroNeuron):
    """
    A-03 | Wash Volume — wykrywanie prania wolumenu (fake volume).

    Dla nowicjusza: Manipulatorzy czasem kupują i sprzedają TO SAMO między sobą
    (albo własne konta), żeby na wykresie pojawił się wielki wolumen i przyciągnąć
    innych graczy. Zdradza ich POŁĄCZENIE: duży wolumen + mały ruch ceny.
    Normalny wolumen → cena się rusza. Pranie → wolumen rośnie, cena stoi.

    Logika:
      Warunek prania: VOLUME > 2× VOLUME_MA20 (spike) i jednocześnie
                      HIGH - LOW < 0.4 × donchian_zakres (mała świeca)
      Kierunek (kto za tym stoi):
        CLOSE > OPEN → dystrybutor pompuje, żeby sprzedać wyżej → SHORT
        CLOSE < OPEN → akumulator "przecenia", żeby kupić taniej  → LONG
    """
    KLUCZ = "A-03"
    LEGION = "STRAZ"
    WSKAZNIK = "VOLUME"
    KATEGORIA = "A"
    WAGA = 6

    _VOL_PROG = 2.0   # wolumen musi być co najmniej tyle razy powyżej MA20
    _ZAKRES_MAX = 0.4  # świeca musi być krótsza niż ta frakcja zakresu Donchian

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        vol = wskazniki.get("VOLUME")
        vol_ma = wskazniki.get("VOLUME_MA20")
        o = wskazniki.get("OPEN")
        h = wskazniki.get("HIGH")
        low = wskazniki.get("LOW")
        c = wskazniki.get("CLOSE")
        donch_hi = wskazniki.get("DONCHIAN_UPPER")
        donch_lo = wskazniki.get("DONCHIAN_LOWER")

        if None in (vol, vol_ma, o, h, low, c) or vol_ma < 1:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych WashVol."])

        # Zakres odniesienia: Donchian lub sam ten bar
        if donch_hi is not None and donch_lo is not None:
            zakres_ref = donch_hi - donch_lo
        else:
            zakres_ref = h - low

        if zakres_ref < 1e-9:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.0, ["Zakres zerowy."])

        spike = vol / vol_ma
        zakres_swiecy = h - low
        frakcja = zakres_swiecy / zakres_ref

        if spike < self._VOL_PROG or frakcja >= self._ZAKRES_MAX:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.10,
                [f"Brak prania: vol×{spike:.1f} MA, zakres {frakcja:.0%} kanału"])

        # Spike wolumenu + mała świeca = wash trading
        sila = min(0.80, 0.50 + (spike - self._VOL_PROG) * 0.08)
        if c >= o:
            return self._bazowy_sygnal(c, "SHORT", sila,
                [f"🛡️ WASH VOL BEAR: vol×{spike:.1f} MA, świeca {frakcja:.0%} — "
                 f"dystrybucja: pompują wolumen żeby sprzedać wyżej"])
        else:
            return self._bazowy_sygnal(c, "LONG", sila,
                [f"🛡️ WASH VOL BULL: vol×{spike:.1f} MA, świeca {frakcja:.0%} — "
                 f"akumulacja: przeceniają żeby kupić taniej"])


class NeuronBartPattern(MikroNeuron):
    """
    A-05 | Bart Pattern — manipulacja na niskiej płynności (głowa Barta Simpsona).

    Dla nowicjusza: Wzorzec Barta wygląda jak głowa postaci z Simpsonów:
      - Cena gwałtownie skacze w górę (włosy na czubku głowy)
      - Chwilę zostaje wysoko (płaski płaskowyż)
      - Potem gwałtownie wraca do punktu startowego
    (lub odwrotnie: nagły spadek → płaskowyż nisko → powrót)
    To klasyka niskiej płynności (nocna sesja, weekend): małe zlecenie może
    "wbić" cenę daleko, potem market maker ją "prostuje" z powrotem.

    Detekcja (z 2 barów: PREV i CURRENT):
      Bull Bart: PREV był olbrzymim bullish barem (CLOSE_PREV ≫ OPEN_PREV),
                 ale CURRENT zamknął SIĘ poniżej OPEN_PREV — powrót → SHORT
      Bear Bart: PREV był olbrzymim bearish barem (CLOSE_PREV ≪ OPEN_PREV),
                 ale CURRENT zamknął SIĘ powyżej OPEN_PREV — powrót → LONG
    """
    KLUCZ = "A-05"
    LEGION = "STRAZ"
    WSKAZNIK = "CLOSE_PREV"
    KATEGORIA = "A"
    WAGA = 6

    _PROG_CIALA = 0.10  # ciało PREV musi stanowić min. tę frakcję zakresu Donchian

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        c = wskazniki.get("CLOSE")
        o_prev = wskazniki.get("OPEN_PREV")
        c_prev = wskazniki.get("CLOSE_PREV")
        donch_hi = wskazniki.get("DONCHIAN_UPPER")
        donch_lo = wskazniki.get("DONCHIAN_LOWER")

        if None in (c, o_prev, c_prev):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych BartPattern."])

        # Zakres odniesienia do oceny "olbrzymiego" baru
        if donch_hi is not None and donch_lo is not None:
            zakres_ref = donch_hi - donch_lo
        else:
            zakres_ref = abs(c_prev - o_prev) * 2 + 1e-9

        if zakres_ref < 1e-9:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.0, ["Zakres zerowy."])

        cialo_prev = abs(c_prev - o_prev)
        cialo_frakcja = cialo_prev / zakres_ref

        if cialo_frakcja < self._PROG_CIALA:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.10,
                [f"Poprzedni bar zbyt mały ({cialo_frakcja:.0%} kanału) — brak Barta"])

        # Bull Bart (skok w górę → powrót): PREV bullish + CURRENT poniżej OPEN_PREV
        if c_prev > o_prev and c < o_prev:
            powrot = (c_prev - c) / cialo_prev
            sila = min(0.80, 0.55 + powrot * 0.25)
            return self._bazowy_sygnal(c, "SHORT", sila,
                [f"🛡️ BART BULL→CRASH: PREV+{cialo_frakcja:.0%} kanału, "
                 f"CLOSE wrócił {powrot:.0%} ciała PREV — manipulacja nocna"])

        # Bear Bart (skok w dół → powrót): PREV bearish + CURRENT powyżej OPEN_PREV
        if c_prev < o_prev and c > o_prev:
            powrot = (c - c_prev) / cialo_prev
            sila = min(0.80, 0.55 + powrot * 0.25)
            return self._bazowy_sygnal(c, "LONG", sila,
                [f"🛡️ BART BEAR→PUMP: PREV-{cialo_frakcja:.0%} kanału, "
                 f"CLOSE wrócił {powrot:.0%} ciała PREV — manipulacja nocna"])

        return self._bazowy_sygnal(c, "NEUTRAL", 0.10,
            [f"Brak wzorca Barta (ciało {cialo_frakcja:.0%}, brak powrotu)"])
