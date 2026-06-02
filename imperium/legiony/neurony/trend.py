"""
⚔️ IMV-INS | Neurony Trendu — Legion XII Fulminata (Swing)
ADX, Ichimoku, Supertrend, EMA 50/200, Parabolic SAR
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
