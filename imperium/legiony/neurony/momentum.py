"""
⚔️ IMV-INS | Neurony Momentum — Legion X Equestris (Scalp)
Interpretują wartości z Bramy bez samodzielnego liczenia.

Neurony: RSI, StochRSI, MACD, BBands, ADX, EMA Cross, Williams %R, ATR Deviation
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronRSI(MikroNeuron):
    """
    X-01 | RSI (14) — klasyczny momentum oscillator.
    Progi: <30 wyprzedanie → LONG, >70 wykupienie → SHORT.
    Ekstremalne: <20 / >80 = pewność 0.9.
    """
    KLUCZ = "X-01"
    LEGION = "SCALP"
    WSKAZNIK = "RSI_14"
    KATEGORIA = "M"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        rsi = wskazniki.get("RSI_14")
        if rsi is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak RSI_14"])

        if rsi <= 20:
            return self._bazowy_sygnal(rsi, "LONG", 0.90, [f"RSI={rsi:.1f} ekstremalnie wyprzedany"])
        if rsi <= 30:
            return self._bazowy_sygnal(rsi, "LONG", 0.70, [f"RSI={rsi:.1f} wyprzedany"])
        if rsi >= 80:
            return self._bazowy_sygnal(rsi, "SHORT", 0.90, [f"RSI={rsi:.1f} ekstremalnie wykupiony"])
        if rsi >= 70:
            return self._bazowy_sygnal(rsi, "SHORT", 0.70, [f"RSI={rsi:.1f} wykupiony"])
        if rsi > 50:
            return self._bazowy_sygnal(rsi, "LONG", 0.40, [f"RSI={rsi:.1f} lekki byk"])
        if rsi < 50:
            return self._bazowy_sygnal(rsi, "SHORT", 0.40, [f"RSI={rsi:.1f} lekki niedźwiedź"])
        return self._bazowy_sygnal(rsi, "NEUTRAL", 0.0, [f"RSI={rsi:.1f} neutralne"])


class NeuronMACD(MikroNeuron):
    """
    X-03 | MACD (12/26/9) — trend + momentum.
    Sygnał: MACD > Signal → LONG, histogram rośnie = dodatkowa pewność.
    """
    KLUCZ = "X-03"
    LEGION = "SCALP"
    WSKAZNIK = "MACD"
    KATEGORIA = "M"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        macd = wskazniki.get("MACD")
        signal = wskazniki.get("MACD_SIGNAL")
        hist = wskazniki.get("MACD_HIST")
        hist_prev = wskazniki.get("MACD_HIST_PREV")

        if macd is None or signal is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak MACD"])

        krzyzowanie_bull = macd > signal
        krzyzowanie_bear = macd < signal
        histogram_rosnie = hist is not None and hist_prev is not None and hist > hist_prev
        histogram_spada = hist is not None and hist_prev is not None and hist < hist_prev

        if krzyzowanie_bull:
            pewnosc = 0.65 + (0.15 if histogram_rosnie else 0.0)
            return self._bazowy_sygnal(macd, "LONG", pewnosc,
                [f"MACD crossover bullish ({macd:.4f} > {signal:.4f})",
                 "Histogram rośnie" if histogram_rosnie else ""])
        if krzyzowanie_bear:
            pewnosc = 0.65 + (0.15 if histogram_spada else 0.0)
            return self._bazowy_sygnal(macd, "SHORT", pewnosc,
                [f"MACD crossover bearish ({macd:.4f} < {signal:.4f})",
                 "Histogram spada" if histogram_spada else ""])
        return self._bazowy_sygnal(macd, "NEUTRAL", 0.20, ["MACD konsolidacja"])


class NeuronBBands(MikroNeuron):
    """
    X-04 | Bollinger Bands (20,2) — mean-reversion + squeeze.
    Dotknięcie dolnej wstęgi = LONG, górnej = SHORT.
    Squeeze (wąskie pasmo) = brak sygnału.
    """
    KLUCZ = "X-04"
    LEGION = "SCALP"
    WSKAZNIK = "BBANDS"
    KATEGORIA = "M"
    WAGA = 5

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        upper = wskazniki.get("BB_UPPER")
        middle = wskazniki.get("BB_MIDDLE")
        lower = wskazniki.get("BB_LOWER")
        close = wskazniki.get("CLOSE")

        if None in (upper, middle, lower, close):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak BB"])

        bandwidth = (upper - lower) / middle if middle > 0 else 0
        squeeze = bandwidth < 0.02  # <2% szerokości = squeeze

        if squeeze:
            return self._bazowy_sygnal(bandwidth, "NEUTRAL", 0.0,
                [f"BB Squeeze: bandwidth={bandwidth:.3f} — czekaj na wybicie"])

        if close <= lower:
            pewnosc = 0.75 if close < lower else 0.60
            return self._bazowy_sygnal(close, "LONG", pewnosc,
                [f"Cena {close:.2f} dotknęła/poniżej dolnej BB {lower:.2f}"])
        if close >= upper:
            pewnosc = 0.75 if close > upper else 0.60
            return self._bazowy_sygnal(close, "SHORT", pewnosc,
                [f"Cena {close:.2f} dotknęła/powyżej górnej BB {upper:.2f}"])

        poz_w_pasmie = (close - lower) / (upper - lower)
        if poz_w_pasmie > 0.5:
            return self._bazowy_sygnal(close, "LONG", 0.35, [f"BB pozycja={poz_w_pasmie:.0%} górna połowa"])
        return self._bazowy_sygnal(close, "SHORT", 0.35, [f"BB pozycja={poz_w_pasmie:.0%} dolna połowa"])


class NeuronEMACross(MikroNeuron):
    """
    X-05 | EMA Cross (9/21) — trend direction.
    EMA9 > EMA21 → bullish, EMA9 < EMA21 → bearish.
    Aktualne skrzyżowanie (zmiana w ostatnim barze) = wyższe prawdopodobieństwo.
    """
    KLUCZ = "X-05"
    LEGION = "SCALP"
    WSKAZNIK = "EMA_CROSS"
    KATEGORIA = "T"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ema9 = wskazniki.get("EMA_9")
        ema21 = wskazniki.get("EMA_21")
        ema9_prev = wskazniki.get("EMA_9_PREV")
        ema21_prev = wskazniki.get("EMA_21_PREV")

        if ema9 is None or ema21 is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak EMA"])

        bull_cross = (ema9_prev is not None and ema21_prev is not None
                      and ema9_prev <= ema21_prev and ema9 > ema21)
        bear_cross = (ema9_prev is not None and ema21_prev is not None
                      and ema9_prev >= ema21_prev and ema9 < ema21)

        roznica_pct = abs(ema9 - ema21) / ema21 if ema21 > 0 else 0

        if bull_cross:
            return self._bazowy_sygnal(ema9, "LONG", 0.85,
                [f"ŚWIEŻE skrzyżowanie EMA9 ({ema9:.2f}) > EMA21 ({ema21:.2f})"])
        if bear_cross:
            return self._bazowy_sygnal(ema9, "SHORT", 0.85,
                [f"ŚWIEŻE skrzyżowanie EMA9 ({ema9:.2f}) < EMA21 ({ema21:.2f})"])
        if ema9 > ema21:
            pewnosc = min(0.65, 0.40 + roznica_pct * 10)
            return self._bazowy_sygnal(ema9, "LONG", pewnosc,
                [f"EMA9 > EMA21 (roznica={roznica_pct:.2%}) — trend bull"])
        pewnosc = min(0.65, 0.40 + roznica_pct * 10)
        return self._bazowy_sygnal(ema9, "SHORT", pewnosc,
            [f"EMA9 < EMA21 (roznica={roznica_pct:.2%}) — trend bear"])


class NeuronWilliamsR(MikroNeuron):
    """
    X-06 | Williams %R (14) — wykupienie/wyprzedanie.
    Skala odwrócona: -80 do -100 = wyprzedany → LONG, 0 do -20 = wykupiony → SHORT.
    """
    KLUCZ = "X-06"
    LEGION = "SCALP"
    WSKAZNIK = "WILLIAMS_R"
    KATEGORIA = "M"
    WAGA = 4

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        wr = wskazniki.get("WILLIAMS_R")
        if wr is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Williams %R"])

        if wr <= -80:
            pewnosc = 0.80 if wr <= -90 else 0.65
            return self._bazowy_sygnal(wr, "LONG", pewnosc, [f"W%R={wr:.1f} wyprzedany"])
        if wr >= -20:
            pewnosc = 0.80 if wr >= -10 else 0.65
            return self._bazowy_sygnal(wr, "SHORT", pewnosc, [f"W%R={wr:.1f} wykupiony"])
        return self._bazowy_sygnal(wr, "NEUTRAL", 0.20, [f"W%R={wr:.1f} strefa neutralna"])


class NeuronATRDeviation(MikroNeuron):
    """
    🔱 IMV-ADO v1.0 | ATR Deviation (Arsi Smart Buy Sell — odtworzony + naprawiony)
    Oryginał: Arsi Scalper Pro (Arsalan Riaz, MQL5, closed-source, $50).
    Adopcja: z-score odchylenia ceny od wygładzonej średniej, znormalizowany ATR.

    Nasze ulepszenia względem oryginału:
      1. NAPRAWIONY BŁĄD LOGIKI: oryginalny kod kupował gdy cena WYSOKO nad
         średnią (to momentum, nie mean-reversion). My obsługujemy OBA tryby
         poprawnie i wybieramy wg reżimu (filozofia Kameleon/Parrondo).
      2. Tryb adaptacyjny: RANGING → mean-reversion, TREND → momentum.
      3. MinDisplacement: ignoruje odchylenia < 1.0 ATR (filtr szumu).
      4. Filtr ADX: momentum tylko gdy ADX > próg (realny trend).

    Brama dostarcza:
      ATR_DEVIATION = (close - smooth_mean) / atr   (z-score na ATR)
      ADX_14 (opcjonalnie), REZIM (opcjonalnie: "TREND_*"/"RANGING")
    Progi: NearFactor (domyślnie 1.0 = MinDisplacement), FarFactor (2.0).
    """
    KLUCZ = "X-25"
    LEGION = "SCALP"
    WSKAZNIK = "ATR_DEVIATION"
    KATEGORIA = "M"
    WAGA = 6

    MIN_DISPLACEMENT = 1.0   # NearFactor — poniżej = szum, ignoruj
    FAR_FACTOR = 2.0         # ekstremalne odchylenie = wyższa pewność
    ADX_TREND_PROG = 25.0    # momentum tylko gdy realny trend

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        dev = wskazniki.get("ATR_DEVIATION")
        if dev is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak ATR_DEVIATION"])

        # MinDisplacement — odfiltruj szum
        if abs(dev) < self.MIN_DISPLACEMENT:
            return self._bazowy_sygnal(dev, "NEUTRAL", 0.10,
                [f"Odchylenie={dev:+.2f} ATR < MinDisplacement {self.MIN_DISPLACEMENT} — szum"])

        # Wybór trybu wg reżimu (Kameleon)
        rezim = str(wskazniki.get("REZIM", "")).upper()
        adx = wskazniki.get("ADX_14")
        if rezim.startswith("TREND"):
            tryb_trend = True
        elif rezim == "RANGING":
            tryb_trend = False
        elif adx is not None:
            tryb_trend = adx > self.ADX_TREND_PROG
        else:
            tryb_trend = False  # bezpieczny default: mean-reversion (oryginalna intencja)

        # Siła sygnału — skaluj z wielkością odchylenia
        ekstremalne = abs(dev) >= self.FAR_FACTOR
        pewnosc = 0.80 if ekstremalne else 0.60

        if tryb_trend:
            # MOMENTUM: cena daleko nad średnią → kontynuacja w górę
            if dev > 0:
                return self._bazowy_sygnal(dev, "LONG", pewnosc,
                    [f"TREND momentum: cena {dev:+.2f} ATR nad średnią — kontynuacja wzrostu",
                     f"ADX={adx:.1f}" if adx is not None else f"reżim={rezim}"])
            return self._bazowy_sygnal(dev, "SHORT", pewnosc,
                [f"TREND momentum: cena {dev:+.2f} ATR pod średnią — kontynuacja spadku",
                 f"ADX={adx:.1f}" if adx is not None else f"reżim={rezim}"])
        else:
            # MEAN-REVERSION (poprawna logika): cena daleko nad średnią → SHORT (powrót)
            if dev > 0:
                return self._bazowy_sygnal(dev, "SHORT", pewnosc,
                    [f"MEAN-REV: cena {dev:+.2f} ATR nad średnią — oczekuj powrotu w dół"])
            return self._bazowy_sygnal(dev, "LONG", pewnosc,
                [f"MEAN-REV: cena {dev:+.2f} ATR pod średnią — oczekuj powrotu w górę"])
