"""
⚔️ IMV-INS | Neurony Trendu — Legion XII Fulminata (Swing)
ADX, Ichimoku, Supertrend, EMA 50/200, Fibonacci, RSI Divergence, HMA, Donchian
"""

"""
⚔️ IMV-INS | Neurony Trendu — Legion XII Fulminata (Swing)
ADX, Ichimoku, Supertrend, EMA 50/200, Fibonacci, RSI Divergence, HMA, Donchian
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronADX(MikroNeuron):
    """
    XII-01 | ADX (14) — siła trendu (bez kierunku).
    ADX > 25 = trend. Kierunek z +DI/-DI.
    """
    KLUCZ = "XII-01"
    LEGION = "SWING"
    WSKAZNIK = "ADX_14"
    KATEGORIA = "T"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        adx = wskazniki.get("ADX_14")
        di_plus = wskazniki.get("DI_PLUS")
        di_minus = wskazniki.get("DI_MINUS")

        if adx is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak ADX"])

        if adx < 20:
            return self._bazowy_sygnal(adx, "NEUTRAL", 0.0, [f"ADX={adx:.1f} brak trendu"])

        if di_plus is None or di_minus is None:
            return self._bazowy_sygnal(adx, "NEUTRAL", 0.30, [f"ADX={adx:.1f} trend ale brak DI"])

        if adx >= 40:
            pewnosc_base = 0.90
        elif adx >= 25:
            pewnosc_base = 0.70
        else:
            pewnosc_base = 0.50

        if di_plus > di_minus:
            return self._bazowy_sygnal(adx, "LONG", pewnosc_base,
                [f"ADX={adx:.1f} trend strong, +DI={di_plus:.1f} > -DI={di_minus:.1f}"])
        return self._bazowy_sygnal(adx, "SHORT", pewnosc_base,
            [f"ADX={adx:.1f} trend strong, -DI={di_minus:.1f} > +DI={di_plus:.1f}"])


class NeuronIchimoku(MikroNeuron):
    """
    XII-02 | Ichimoku Cloud — cena vs chmura, tenkan/kijun cross.
    Kumo = strefa oporu/wsparcia. Powyżej kumo = bullish bias.
    """
    KLUCZ = "XII-02"
    LEGION = "SWING"
    WSKAZNIK = "ICHIMOKU"
    KATEGORIA = "T"
    WAGA = 8

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        senkou_a = wskazniki.get("ICHIMOKU_SENKOU_A")
        senkou_b = wskazniki.get("ICHIMOKU_SENKOU_B")
        tenkan = wskazniki.get("ICHIMOKU_TENKAN")
        kijun = wskazniki.get("ICHIMOKU_KIJUN")

        if None in (close, senkou_a, senkou_b):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Ichimoku"])

        kumo_top = max(senkou_a, senkou_b)
        kumo_bot = min(senkou_a, senkou_b)
        chmura_bull = senkou_a > senkou_b  # Bullish cloud

        powody = []
        score_long = 0
        score_short = 0

        # 1. Pozycja ceny względem chmury
        if close > kumo_top:
            score_long += 2
            powody.append(f"Cena {close:.2f} powyżej kumo ({kumo_top:.2f})")
        elif close < kumo_bot:
            score_short += 2
            powody.append(f"Cena {close:.2f} poniżej kumo ({kumo_bot:.2f})")
        else:
            powody.append("Cena w chmurze — konsolidacja")

        # 2. Kolor chmury
        if chmura_bull:
            score_long += 1
            powody.append("Chmura bullish (Senkou A > B)")
        else:
            score_short += 1
            powody.append("Chmura bearish (Senkou B > A)")

        # 3. Tenkan/Kijun
        if tenkan is not None and kijun is not None:
            if tenkan > kijun:
                score_long += 1
                powody.append(f"Tenkan ({tenkan:.2f}) > Kijun ({kijun:.2f}) bullish")
            elif tenkan < kijun:
                score_short += 1
                powody.append(f"Tenkan ({tenkan:.2f}) < Kijun ({kijun:.2f}) bearish")

        max_score = 4 if tenkan is not None else 3
        if score_long > score_short:
            pewnosc = score_long / max_score * 0.85
            return self._bazowy_sygnal(close, "LONG", pewnosc, powody)
        if score_short > score_long:
            pewnosc = score_short / max_score * 0.85
            return self._bazowy_sygnal(close, "SHORT", pewnosc, powody)
        return self._bazowy_sygnal(close, "NEUTRAL", 0.10, powody)


class NeuronEMA50_200(MikroNeuron):
    """
    XII-03 | EMA 50/200 — Golden Cross / Death Cross.
    Najsilniejszy sygnał trendu długoterminowego.
    """
    KLUCZ = "XII-03"
    LEGION = "SWING"
    WSKAZNIK = "EMA_50_200"
    KATEGORIA = "T"
    WAGA = 9

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ema50 = wskazniki.get("EMA_50")
        ema200 = wskazniki.get("EMA_200")
        ema50_prev = wskazniki.get("EMA_50_PREV")
        ema200_prev = wskazniki.get("EMA_200_PREV")

        if None in (ema50, ema200):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak EMA 50/200"])

        golden_cross = (ema50_prev is not None and ema200_prev is not None
                        and ema50_prev <= ema200_prev and ema50 > ema200)
        death_cross = (ema50_prev is not None and ema200_prev is not None
                       and ema50_prev >= ema200_prev and ema50 < ema200)

        if golden_cross:
            return self._bazowy_sygnal(ema50, "LONG", 0.95,
                [f"GOLDEN CROSS: EMA50 ({ema50:.2f}) przebił EMA200 ({ema200:.2f}) w górę"])
        if death_cross:
            return self._bazowy_sygnal(ema50, "SHORT", 0.95,
                [f"DEATH CROSS: EMA50 ({ema50:.2f}) przebił EMA200 ({ema200:.2f}) w dół"])

        roznica_pct = (ema50 - ema200) / ema200 if ema200 > 0 else 0
        if ema50 > ema200:
            pewnosc = min(0.75, 0.50 + abs(roznica_pct) * 5)
            return self._bazowy_sygnal(ema50, "LONG", pewnosc,
                [f"Bullish: EMA50 > EMA200 ({roznica_pct:+.2%})"])
        pewnosc = min(0.75, 0.50 + abs(roznica_pct) * 5)
        return self._bazowy_sygnal(ema50, "SHORT", pewnosc,
            [f"Bearish: EMA50 < EMA200 ({roznica_pct:+.2%})"])


class NeuronSupertrend(MikroNeuron):
    """
    XII-04 | Supertrend (ATR×3, period=10) — trend z dynamicznym SL.
    Gdy cena powyżej linii = LONG, poniżej = SHORT. Zmiana kierunku = silny sygnał.
    """
    KLUCZ = "XII-04"
    LEGION = "SWING"
    WSKAZNIK = "SUPERTREND"
    KATEGORIA = "T"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        supertrend = wskazniki.get("SUPERTREND")
        supertrend_dir = wskazniki.get("SUPERTREND_DIR")  # 1 = bull, -1 = bear
        supertrend_prev_dir = wskazniki.get("SUPERTREND_DIR_PREV")

        if None in (close, supertrend, supertrend_dir):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Supertrend"])

        zmiana = (supertrend_prev_dir is not None and supertrend_prev_dir != supertrend_dir)

        if supertrend_dir == 1:
            pewnosc = 0.90 if zmiana else 0.70
            return self._bazowy_sygnal(supertrend, "LONG", pewnosc,
                [f"Supertrend BULL {'(ZMIANA KIERUNKU)' if zmiana else ''} | linia={supertrend:.2f}"])
        pewnosc = 0.90 if zmiana else 0.70
        return self._bazowy_sygnal(supertrend, "SHORT", pewnosc,
            [f"Supertrend BEAR {'(ZMIANA KIERUNKU)' if zmiana else ''} | linia={supertrend:.2f}"])


class NeuronDonchian(MikroNeuron):
    """
    X-18 | Donchian Channel — wybicia krótkoterminowe. Kanał z 20 poprzednich barów.
    Close > górny kanał = wybicie LONG, close < dolny = wybicie SHORT.
    Dane z Bramy: CLOSE, DONCHIAN_UPPER, DONCHIAN_LOWER.
    """
    KLUCZ = "X-18"
    LEGION = "TREND"
    WSKAZNIK = "DONCHIAN"
    KATEGORIA = "T"
    WAGA = 5

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        up = wskazniki.get("DONCHIAN_UPPER")
        lo = wskazniki.get("DONCHIAN_LOWER")
        if close is None or up is None or lo is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych Donchian."])
        if close > up:
            return self._bazowy_sygnal(close, "LONG", 0.75, [f"Wybicie górą: close={close:.2f} > kanał={up:.2f}"])
        if close < lo:
            return self._bazowy_sygnal(close, "SHORT", 0.75, [f"Wybicie dołem: close={close:.2f} < kanał={lo:.2f}"])
        return self._bazowy_sygnal(close, "NEUTRAL", 0.20, [f"Cena w kanale [{lo:.2f}, {up:.2f}]"])


class NeuronFibonacci(MikroNeuron):
    """
    XII-05 | Fibonacci Retracement — poziomy wsparcia/oporu.

    Dla nowicjusza: Leonardo Fibonacci odkrył sekwencję liczbową (1,1,2,3,5,8...)
    gdzie każda liczba = suma dwóch poprzednich. Rynek "magicznie" zatrzymuje się
    na poziomach 38.2%, 50%, 61.8% poprzedniego ruchu. Dlaczego? Bo wielu traderów
    jednocześnie patrzy na te poziomy i reaguje — to staje się self-fulfilling prophecy.

    Logika:
      Zakres ceny: DONCHIAN_UPPER (szczyt) / DONCHIAN_LOWER (dołek)
      Złota strefa: 38.2%–61.8% od dołka (gdzie cena często "odbija")
      Gdy close jest w złotej strefie: bias zgodny z obecnym momentum (CLOSE vs CLOSE_PREV)
      Gdy close dokładnie na 50% (±1%): neutralny (walka bykow i niedźwiedzi)
    """
    KLUCZ = "XII-05"
    LEGION = "SWING"
    WSKAZNIK = "DONCHIAN"
    KATEGORIA = "T"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        donch_hi = wskazniki.get("DONCHIAN_UPPER")
        donch_lo = wskazniki.get("DONCHIAN_LOWER")
        close_prev = wskazniki.get("CLOSE_PREV")

        if None in (close, donch_hi, donch_lo):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych Fibonacci."])

        zakres = donch_hi - donch_lo
        if zakres < 1e-9:
            return self._bazowy_sygnal(close, "NEUTRAL", 0.0, ["Zakres Donchian zbyt mały."])

        # Pozycja ceny w zakresie (0.0 = dołek, 1.0 = szczyt)
        pozycja = (close - donch_lo) / zakres

        # Złota strefa: 38.2%–61.8%
        fib_382 = donch_lo + 0.382 * zakres
        fib_618 = donch_lo + 0.618 * zakres
        fib_500 = donch_lo + 0.500 * zakres

        powody = [f"Pozycja w kanale: {pozycja:.1%} | Złota strefa: [{fib_382:.2f}, {fib_618:.2f}]"]

        # Momentum cenowy (kierunek ostatniego ruchu)
        momentum_long = close_prev is not None and close > close_prev
        momentum_short = close_prev is not None and close < close_prev

        if 0.382 <= pozycja <= 0.618:
            # W złotej strefie — bias zgodny z momentum
            if abs(pozycja - 0.5) < 0.05:
                # Dokładnie na 50% — brak wyraźnego sygnału
                powody.append(f"Cena na 50% Fibonacci ({fib_500:.2f}) — walka sił")
                return self._bazowy_sygnal(close, "NEUTRAL", 0.20, powody)
            if momentum_long:
                pewnosc = 0.60 + (0.10 if pozycja < 0.5 else 0.0)
                powody.append(f"W złotej strefie + momentum w górę → wsparcie Fibo")
                return self._bazowy_sygnal(close, "LONG", pewnosc, powody)
            if momentum_short:
                pewnosc = 0.60 + (0.10 if pozycja > 0.5 else 0.0)
                powody.append(f"W złotej strefie + momentum w dół → opór Fibo")
                return self._bazowy_sygnal(close, "SHORT", pewnosc, powody)

        elif pozycja > 0.618:
            # Powyżej złotej strefy — trend silny, oczekuj kontynuacji
            powody.append(f"Cena powyżej 61.8% ({fib_618:.2f}) — silny trend wzrostowy")
            return self._bazowy_sygnal(close, "LONG", 0.55, powody)
        else:
            # Poniżej 38.2% — trend silny w dół
            powody.append(f"Cena poniżej 38.2% ({fib_382:.2f}) — silny trend spadkowy")
            return self._bazowy_sygnal(close, "SHORT", 0.55, powody)

        return self._bazowy_sygnal(close, "NEUTRAL", 0.15, powody)


class NeuronRSIDiv(MikroNeuron):
    """
    XII-07 | RSI Divergence — dywergencja RSI vs cena.

    Dla nowicjusza: Wyobraź sobie samochód jadący pod górę. Motor (RSI) zaczyna
    się dławić zanim auto jeszcze zatrzyma. Cena rośnie, ale "silnik" (momentum)
    już słabnie. To właśnie dywergencja — jeden z najlepszych sygnałów odwrócenia.

    Bycza dywergencja: cena robi NIŻSZY dołek, ale RSI robi WYŻSZY dołek → LONG
    Niedźwiedzia dyw.: cena robi WYŻSZY szczyt, ale RSI robi NIŻSZY szczyt → SHORT

    Uwaga: z dwóch świec (CLOSE + CLOSE_PREV, RSI + RSI_PREV) wykrywamy kierunek
    rozbieżności. Dla pełnej dywergencji (2+ szczytów) potrzeba więcej historii —
    tu dajemy wczesny sygnał ostrzegawczy.
    """
    KLUCZ = "XII-07"
    LEGION = "SWING"
    WSKAZNIK = "RSI_14"
    KATEGORIA = "T"
    WAGA = 7

    _MIN_RSI_DELTA = 0.3   # Minimum zmiana RSI (0.3 punktu — reaguje na dziennych barach)
    _MIN_CENA_DELTA = 0.0005  # Minimum zmiana ceny (0.05%)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        rsi = wskazniki.get("RSI_14")
        rsi_prev = wskazniki.get("RSI_PREV")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if None in (rsi, rsi_prev, close, close_prev):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych RSI Div."])

        delta_rsi = rsi - rsi_prev
        delta_cena_pct = (close - close_prev) / (close_prev + 1e-9)

        # Brak istotnej zmiany — ignoruj
        if abs(delta_rsi) < self._MIN_RSI_DELTA or abs(delta_cena_pct) < self._MIN_CENA_DELTA:
            return self._bazowy_sygnal(rsi, "NEUTRAL", 0.10,
                [f"Delta RSI={delta_rsi:.1f}, cena={delta_cena_pct:.2%} — za małe do dywergencji"])

        cena_rosnie = delta_cena_pct > 0
        rsi_rosnie = delta_rsi > 0

        powody = [f"RSI: {rsi_prev:.1f}→{rsi:.1f} ({delta_rsi:+.1f}) | Cena: {delta_cena_pct:+.2%}"]

        if cena_rosnie and not rsi_rosnie:
            # Cena w górę, RSI w dół → NIEDŹWIEDZIA dywergencja → SHORT
            sila = min(0.85, 0.55 + abs(delta_rsi) / 20)
            powody.append("🔴 Niedźwiedzia dywergencja: cena↑ ale RSI↓ — momentum słabnie")
            return self._bazowy_sygnal(rsi, "SHORT", sila, powody)

        if not cena_rosnie and rsi_rosnie:
            # Cena w dół, RSI w górę → BYCZA dywergencja → LONG
            sila = min(0.85, 0.55 + abs(delta_rsi) / 20)
            powody.append("🟢 Bycza dywergencja: cena↓ ale RSI↑ — sprzedający słabną")
            return self._bazowy_sygnal(rsi, "LONG", sila, powody)

        # Brak dywergencji — sygnały zgodne
        return self._bazowy_sygnal(rsi, "NEUTRAL", 0.10,
            [f"Brak dywergencji: cena i RSI idą w tym samym kierunku"])


class NeuronHMA(MikroNeuron):
    """
    X-10 | Hull Moving Average — szybki trend o minimalnym opóźnieniu.
    Nachylenie HMA (HMA vs HMA_PREV) daje kierunek bez lagu klasycznych EMA.
    Potwierdzenie ceną (CLOSE po właściwej stronie HMA) wzmacnia sygnał.
    Dane z Bramy: HMA, HMA_PREV, CLOSE.
    """
    KLUCZ = "X-10"
    LEGION = "SCALP"
    WSKAZNIK = "HMA"
    KATEGORIA = "T"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        hma = wskazniki.get("HMA")
        prev = wskazniki.get("HMA_PREV")
        close = wskazniki.get("CLOSE")
        if hma is None or prev is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych HMA."])
        rosnie = hma > prev
        opada = hma < prev
        # potwierdzenie ceną: close po tej samej stronie co nachylenie
        potw_long = close is not None and close >= hma
        potw_short = close is not None and close <= hma
        if rosnie and potw_long:
            return self._bazowy_sygnal(hma, "LONG", 0.70, [f"HMA rośnie ({hma:.2f}>{prev:.2f}) i cena nad HMA"])
        if opada and potw_short:
            return self._bazowy_sygnal(hma, "SHORT", 0.70, [f"HMA opada ({hma:.2f}<{prev:.2f}) i cena pod HMA"])
        if rosnie:
            return self._bazowy_sygnal(hma, "LONG", 0.45, [f"HMA rośnie ({hma:.2f}>{prev:.2f}), cena bez potw."])
        if opada:
            return self._bazowy_sygnal(hma, "SHORT", 0.45, [f"HMA opada ({hma:.2f}<{prev:.2f}), cena bez potw."])
        return self._bazowy_sygnal(hma, "NEUTRAL", 0.15, [f"HMA płaska ({hma:.2f})"])


class NeuronOBZone(MikroNeuron):
    """
    XII-06 | Order Block — strefa gdzie "big money" zostawił ślad.

    Dla nowicjusza: Przed wielką ruchą w górę (impulse) zazwyczaj jest ostatnia
    świeca SPADKOWA — tam market maker zbierał zlecenia (kupował cicho podczas
    spadku, zanim popchnął cenę w górę). Ta niedźwiedzia świeca to "bullish order
    block". Gdy cena do niej wraca → wielki gracz kupuje ponownie → LONG.
    Odwrotnie dla bearish order block.

    Wersja OHLCV (uproszczona, bez zewnętrznego feedu SMC):
      Bullish OB: poprzedni bar był wyraźnie bearish (CLOSE_PREV < OPEN_PREV o min.
                  _PROG_CIALA kanału Donchian), a CURRENT CLOSE jest powyżej OPEN_PREV
                  (cena wróciła do OB i poszła dalej w górę) → LONG
      Bearish OB: poprzedni bar był wyraźnie bullish (CLOSE_PREV > OPEN_PREV), ale
                  CURRENT CLOSE jest poniżej OPEN_PREV → SHORT

    Ograniczenie: to jest uproszczenie — prawdziwy SMC-OB wymaga kontekstu impulsu
    z wielu barów. Ta wersja identyfikuje sam "punkt wejścia", nie cały kontekst SMC.
    """
    KLUCZ = "XII-06"
    LEGION = "SWING"
    WSKAZNIK = "CLOSE_PREV"
    KATEGORIA = "T"
    WAGA = 6

    _PROG_CIALA = 0.20  # ciało PREV musi stanowić min. tę frakcję zakresu Donchian

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        c = wskazniki.get("CLOSE")
        o_prev = wskazniki.get("OPEN_PREV")
        c_prev = wskazniki.get("CLOSE_PREV")
        donch_hi = wskazniki.get("DONCHIAN_UPPER")
        donch_lo = wskazniki.get("DONCHIAN_LOWER")

        if None in (c, o_prev, c_prev):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych OrderBlock."])

        if donch_hi is not None and donch_lo is not None:
            zakres_ref = donch_hi - donch_lo
        else:
            zakres_ref = abs(c_prev - o_prev) * 2 + 1e-9

        if zakres_ref < 1e-9:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.0, ["Zakres zerowy."])

        cialo_prev = abs(c_prev - o_prev)
        frakcja = cialo_prev / zakres_ref

        if frakcja < self._PROG_CIALA:
            return self._bazowy_sygnal(c, "NEUTRAL", 0.10,
                [f"Poprzedni bar zbyt mały ({frakcja:.0%} kanału) — brak wyraźnego OB"])

        # Bullish OB: bearish bar PREV + CURRENT wrócił POWYŻEJ wejścia w PREV
        if c_prev < o_prev and c > o_prev:
            gleb = (c - o_prev) / zakres_ref
            sila = min(0.80, 0.55 + gleb * 1.5)
            return self._bazowy_sygnal(c, "LONG", sila,
                [f"🟢 BULLISH OB: PREV bearish {frakcja:.0%} kanału, "
                 f"CLOSE={c:.2f} powyżej OPEN_PREV={o_prev:.2f} — strefa OB aktywna"])

        # Bearish OB: bullish bar PREV + CURRENT wrócił PONIŻEJ wejścia w PREV
        if c_prev > o_prev and c < o_prev:
            gleb = (o_prev - c) / zakres_ref
            sila = min(0.80, 0.55 + gleb * 1.5)
            return self._bazowy_sygnal(c, "SHORT", sila,
                [f"🔴 BEARISH OB: PREV bullish {frakcja:.0%} kanału, "
                 f"CLOSE={c:.2f} poniżej OPEN_PREV={o_prev:.2f} — strefa OB aktywna"])

        return self._bazowy_sygnal(c, "NEUTRAL", 0.10,
            [f"Brak sygnału OB: PREV {frakcja:.0%} kanału, cena nie przełamała strefy"])
