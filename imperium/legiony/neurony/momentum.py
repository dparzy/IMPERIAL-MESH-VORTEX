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
    ELITARNY = True
    POWOD_ELITARNOSCI = "E4 (kameleon RANGING↔TREND) + E5 (IMV-ADO 🔱, naprawiony oryginał)"

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


class NeuronHAScalper(MikroNeuron):
    """
    🔱 IMV-ADO v1.0 | HA Scalper (MSX Hybrid Heiken Scalper — odtworzony + naprawiony)
    Oryginał: MSX Hybrid Heiken Scalper (MQL5, closed-source, $50-$100).

    Technika: kolor i kształt świec Heiken Ashi (HA) jako sygnał kierunku,
    potwierdzony momentum. Kluczowa zaleta oryginału: HA bez repainting
    (obliczane ze zwykłych OHLC — zamknięta świeca się nie zmienia).

    Nasze poprawki:
      1. Prawo I: neuron NIE liczy HA/ATR sam — pyta Bramę o gotowe wartości.
      2. Usunięta redundantna tautologia: Mid_Price < HA_Close jest zawsze
         prawdą gdy HA_Close > HA_Open — zastąpiona filtrem Volatility_Index.
      3. Filtr reżimu: w RANGING → wymaga wyższego Volatility_Index (≥ 0.008).
         Agresywny scalper bez filtra w konsolidacji = strata pewna.
      4. Tryby aggressive/conservative jako parametr pewności wejścia.

    Brama dostarcza (z danych HA obliczonych na surowych OHLC, bez wygładzania):
      HA_BULL: bool (HA_Close > HA_Open — świeca bycza)
      HA_BEAR: bool (HA_Close < HA_Open — świeca niedźwiedzia)
      HA_MOMENTUM: float (Mid_Price[t] - Mid_Price[t-1], znorm. ATR)
      HA_VOLATILITY_INDEX: float (ATR / MidPrice_MA20 — normalizacja bezwymiarowa)
      REZIM (opcjonalnie): str
    """
    KLUCZ = "X-26"
    LEGION = "SCALP"
    WSKAZNIK = "HA_SCALPER"
    KATEGORIA = "M"
    WAGA = 7
    ELITARNY = True
    POWOD_ELITARNOSCI = "E4 (multi-reżim) + E5 (IMV-ADO 🔱) + E7 (filtr Volatility Index + potrójne potwierdzenie)"

    # Tryby (aggressive = niższy próg = więcej sygnałów)
    VOLATILITY_MIN_RANGING = 0.008  # filtr dla RANGING — wymagaj realnej zmienności
    VOLATILITY_MIN_TREND = 0.003    # w trendzie wystarczy mniejsza

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ha_bull = wskazniki.get("HA_BULL")
        ha_bear = wskazniki.get("HA_BEAR")
        ha_momentum = wskazniki.get("HA_MOMENTUM")   # znormalizowane przez ATR, >0 = byk
        vol_idx = wskazniki.get("HA_VOLATILITY_INDEX")
        tryb = str(wskazniki.get("TRYB", "aggressive")).lower()
        rezim = str(wskazniki.get("REZIM", "")).upper()

        if ha_bull is None or ha_bear is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych HA"])

        # Filtr Volatility_Index wg reżimu (naprawiona tautologia oryginału)
        jest_ranging = rezim == "RANGING" or (not rezim.startswith("TREND"))
        vol_min = self.VOLATILITY_MIN_RANGING if jest_ranging else self.VOLATILITY_MIN_TREND

        if vol_idx is not None and vol_idx < vol_min:
            return self._bazowy_sygnal(vol_idx, "NEUTRAL", 0.0,
                [f"HA: Volatility_Index={vol_idx:.4f} < {vol_min:.3f} — konsolidacja, brak sygnału"])

        # Bazowa pewność wg trybu (aggressive = wyższy próg akceptacji)
        pewnosc_bazowa = 0.65 if tryb == "aggressive" else 0.55

        # Potwierdzenie momentum (naprawiony warunek — nie tautologia)
        mom_potwierdza_bull = ha_momentum is not None and ha_momentum > 0
        mom_potwierdza_bear = ha_momentum is not None and ha_momentum < 0

        if ha_bull and not ha_bear:
            if mom_potwierdza_bull:
                pewnosc = pewnosc_bazowa + 0.15
                powody = [f"HA BULL: świeca bycza + momentum↑ ({ha_momentum:+.3f} ATR)"]
            elif ha_momentum is None:
                pewnosc = pewnosc_bazowa
                powody = ["HA BULL: świeca bycza (brak momentum)"]
            else:
                # Świeca bycza ale momentum spada — słaby sygnał
                pewnosc = pewnosc_bazowa - 0.15
                powody = [f"HA BULL słaby: świeca bycza ale momentum↓ ({ha_momentum:+.3f} ATR)"]

            if vol_idx is not None:
                powody.append(f"VolIdx={vol_idx:.4f}")
            return self._bazowy_sygnal(vol_idx, "LONG", max(0.0, pewnosc), powody)

        if ha_bear and not ha_bull:
            if mom_potwierdza_bear:
                pewnosc = pewnosc_bazowa + 0.15
                powody = [f"HA BEAR: świeca niedźwiedzia + momentum↓ ({ha_momentum:+.3f} ATR)"]
            elif ha_momentum is None:
                pewnosc = pewnosc_bazowa
                powody = ["HA BEAR: świeca niedźwiedzia (brak momentum)"]
            else:
                pewnosc = pewnosc_bazowa - 0.15
                powody = [f"HA BEAR słaby: świeca niedźwiedzia ale momentum↑ ({ha_momentum:+.3f} ATR)"]

            if vol_idx is not None:
                powody.append(f"VolIdx={vol_idx:.4f}")
            return self._bazowy_sygnal(vol_idx, "SHORT", max(0.0, pewnosc), powody)

        return self._bazowy_sygnal(None, "NEUTRAL", 0.10,
            ["HA Doji/niejednoznaczna świeca — brak sygnału"])


class NeuronStochRSI(MikroNeuron):
    """
    X-02 | Stochastic RSI — ekstrema wykupienia/wyprzedania (szybsze niż RSI).
    Linia %K (0–100): <20 = wyprzedanie → LONG, >80 = wykupienie → SHORT.
    Dane z Bramy: klucz STOCHRSI (talib.STOCHRSI fastk).
    """
    KLUCZ = "X-02"
    LEGION = "SCALP"
    WSKAZNIK = "STOCHRSI"
    KATEGORIA = "M"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        v = wskazniki.get("STOCHRSI")
        if v is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych StochRSI."])
        if v < 20:
            pewnosc = 0.85 if v < 10 else 0.75
            return self._bazowy_sygnal(v, "LONG", pewnosc,
                [f"StochRSI={v:.1f} < 20 → strefa wyprzedania, możliwe odbicie"])
        if v > 80:
            pewnosc = 0.85 if v > 90 else 0.75
            return self._bazowy_sygnal(v, "SHORT", pewnosc,
                [f"StochRSI={v:.1f} > 80 → strefa wykupienia, możliwa korekta"])
        return self._bazowy_sygnal(v, "NEUTRAL", 0.30, [f"StochRSI={v:.1f} w strefie neutralnej"])


class NeuronTRIX(MikroNeuron):
    """
    X-17 | TRIX — potrójnie wygładzony ROC. Filtruje szum, łapie zmianę momentum.
    Przejście przez zero w górę = LONG, w dół = SHORT (świeże przejście = mocniej).
    Dane z Bramy: TRIX, TRIX_PREV.
    """
    KLUCZ = "X-17"
    LEGION = "SCALP"
    WSKAZNIK = "TRIX"
    KATEGORIA = "M"
    WAGA = 4

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        trix = wskazniki.get("TRIX")
        prev = wskazniki.get("TRIX_PREV")
        if trix is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych TRIX."])
        if prev is not None and trix > 0 and prev <= 0:
            return self._bazowy_sygnal(trix, "LONG", 0.80, [f"TRIX przeciął zero w górę ({trix:+.4f})"])
        if prev is not None and trix < 0 and prev >= 0:
            return self._bazowy_sygnal(trix, "SHORT", 0.80, [f"TRIX przeciął zero w dół ({trix:+.4f})"])
        if trix > 0:
            return self._bazowy_sygnal(trix, "LONG", 0.45, [f"TRIX>0 momentum dodatnie ({trix:+.4f})"])
        if trix < 0:
            return self._bazowy_sygnal(trix, "SHORT", 0.45, [f"TRIX<0 momentum ujemne ({trix:+.4f})"])
        return self._bazowy_sygnal(trix, "NEUTRAL", 0.20, ["TRIX≈0 brak momentum"])


class NeuronAwesome(MikroNeuron):
    """
    X-08 | Awesome Oscillator = SMA(median,5) − SMA(median,34).
    AO>0 i rosnący = LONG, AO<0 i opadający = SHORT. Median price = mniej szumu close.
    Dane z Bramy: AO, AO_PREV.
    """
    KLUCZ = "X-08"
    LEGION = "SCALP"
    WSKAZNIK = "AO"
    KATEGORIA = "M"
    WAGA = 5

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ao = wskazniki.get("AO")
        prev = wskazniki.get("AO_PREV")
        if ao is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych AO."])
        if prev is not None and ao > 0 and prev <= 0:
            return self._bazowy_sygnal(ao, "LONG", 0.80, [f"AO przeciął zero w górę ({ao:+.4f})"])
        if prev is not None and ao < 0 and prev >= 0:
            return self._bazowy_sygnal(ao, "SHORT", 0.80, [f"AO przeciął zero w dół ({ao:+.4f})"])
        rosnacy = prev is not None and ao > prev
        opadajacy = prev is not None and ao < prev
        if ao > 0 and rosnacy:
            return self._bazowy_sygnal(ao, "LONG", 0.60, [f"AO>0 i rośnie ({ao:+.4f})"])
        if ao < 0 and opadajacy:
            return self._bazowy_sygnal(ao, "SHORT", 0.60, [f"AO<0 i opada ({ao:+.4f})"])
        return self._bazowy_sygnal(ao, "NEUTRAL", 0.25, [f"AO={ao:+.4f} bez wyraźnego momentum"])


class NeuronAccelerator(MikroNeuron):
    """
    X-09 | Accelerator Oscillator (Bill Williams) = AO − SMA(AO, 5).
    Mierzy PRZYSPIESZENIE momentum (2. pochodna ceny) — wyprzedza AO.
    Zmiana znaku AC = wczesny sygnał zmiany momentum, ZANIM zareaguje AO.
    Dane z Bramy: AC, AC_PREV.
    """
    KLUCZ = "X-09"
    LEGION = "SCALP"
    WSKAZNIK = "AC"
    KATEGORIA = "M"
    WAGA = 4

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ac = wskazniki.get("AC")
        prev = wskazniki.get("AC_PREV")
        if ac is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych AC."])
        if prev is not None and ac > 0 and prev <= 0:
            return self._bazowy_sygnal(ac, "LONG", 0.75, [f"AC przyspiesza w górę — przeciął zero ({ac:+.4f})"])
        if prev is not None and ac < 0 and prev >= 0:
            return self._bazowy_sygnal(ac, "SHORT", 0.75, [f"AC przyspiesza w dół — przeciął zero ({ac:+.4f})"])
        rosnacy = prev is not None and ac > prev
        opadajacy = prev is not None and ac < prev
        if ac > 0 and rosnacy:
            return self._bazowy_sygnal(ac, "LONG", 0.55, [f"AC>0 i rośnie — momentum przyspiesza ({ac:+.4f})"])
        if ac < 0 and opadajacy:
            return self._bazowy_sygnal(ac, "SHORT", 0.55, [f"AC<0 i opada — momentum przyspiesza w dół ({ac:+.4f})"])
        return self._bazowy_sygnal(ac, "NEUTRAL", 0.20, [f"AC={ac:+.4f} bez wyraźnego przyspieszenia"])


class NeuronBBSqueeze(MikroNeuron):
    """
    X-12 | Bollinger Squeeze — detektor kompresji zmienności.

    Dla nowicjusza: wyobraź sobie sprężynę. Gdy rynek się "ściska" (Bollinger Bands
    zwężają się), energia się kumuluje. Gdy sprężyna pęka → gwałtowny ruch.
    Ten neuron wykrywa moment "ściśnięcia" i kierunek potencjalnego wybicia.

    Logika:
      BB_width = (BB_UPPER - BB_LOWER) / BB_MIDDLE (normalizacja do ceny)
      Squeeze = BB_width < 0.04 (wstęgi poniżej 4% ceny środkowej)
      Kierunek wybicia: CLOSE vs BB_MIDDLE (cena w górnej/dolnej połówce)
      Potwierdzenie: ATR_DEVIATION musi być niskie (<1.0) — spokojny rynek, nie po wybuchu
    """
    KLUCZ = "X-12"
    LEGION = "SCALP"
    WSKAZNIK = "BB_UPPER"
    KATEGORIA = "M"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        bb_upper = wskazniki.get("BB_UPPER")
        bb_lower = wskazniki.get("BB_LOWER")
        bb_mid = wskazniki.get("BB_MIDDLE")
        close = wskazniki.get("CLOSE")
        atr_dev = wskazniki.get("ATR_DEVIATION", 1.0)

        if None in (bb_upper, bb_lower, bb_mid, close):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych BB."])

        bb_width = (bb_upper - bb_lower) / (bb_mid + 1e-9)

        # Brak ściśnięcia = neutralny
        if bb_width >= 0.025:
            return self._bazowy_sygnal(bb_width, "NEUTRAL", 0.15,
                [f"BB szeroki ({bb_width:.3f}) — brak ściśnięcia"])

        # Ściśnięcie potwierdzone
        powody = [f"BB SQUEEZE: szerokość={bb_width:.3f} (<4%) | ATR_dev={atr_dev:.2f}"]

        # Kierunek wybicia — cena w górnej/dolnej połowie wstęgi
        polowa = (bb_upper + bb_lower) / 2
        if close > polowa:
            pewnosc = 0.60 + (0.15 if atr_dev < 1.0 else 0.0)
            powody.append(f"Cena ({close:.2f}) w górnej połowie → bias LONG")
            return self._bazowy_sygnal(bb_width, "LONG", pewnosc, powody)
        else:
            pewnosc = 0.60 + (0.15 if atr_dev < 1.0 else 0.0)
            powody.append(f"Cena ({close:.2f}) w dolnej połowie → bias SHORT")
            return self._bazowy_sygnal(bb_width, "SHORT", pewnosc, powody)
