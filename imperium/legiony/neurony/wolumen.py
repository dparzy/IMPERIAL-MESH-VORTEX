"""
⚔️ IMV-INS | Neurony Wolumenu — OBV, CVD, VWAP, Volume Profile
Wolumen = "głosowanie rynku". Potwierdzenie ruchom cenowym.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronOBV(MikroNeuron):
    """
    V-01 | On-Balance Volume — kumulacyjna różnica wolumenu.
    OBV rośnie = akumulacja, OBV spada = dystrybucja.
    Dywergencja OBV vs cena = najsilniejszy sygnał.
    """
    KLUCZ = "V-01"
    LEGION = "SWING"
    WSKAZNIK = "OBV"
    KATEGORIA = "F"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        obv = wskazniki.get("OBV")
        obv_ema = wskazniki.get("OBV_EMA_20")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if obv is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak OBV"])

        powody = []
        if obv_ema is None:
            # Bez EMA — prosty kierunek
            kierunek = "LONG" if obv > 0 else "SHORT"
            return self._bazowy_sygnal(obv, kierunek, 0.50, [f"OBV={obv:.0f}"])

        # Dywergencja OBV vs cena
        if close is not None and close_prev is not None:
            cena_rosnie = close > close_prev
            obv_rosnie = obv > obv_ema

            if cena_rosnie and not obv_rosnie:
                powody.append("⚠️ DYWERGENCJA NIEDŹWIEDZIA: cena rośnie, OBV spada — słaby wzrost")
                return self._bazowy_sygnal(obv, "SHORT", 0.75, powody)
            if not cena_rosnie and obv_rosnie:
                powody.append("📢 DYWERGENCJA BYKA: cena spada, OBV rośnie — akumulacja")
                return self._bazowy_sygnal(obv, "LONG", 0.75, powody)

        if obv > obv_ema:
            return self._bazowy_sygnal(obv, "LONG", 0.60, [f"OBV ({obv:.0f}) > EMA20 — akumulacja"])
        return self._bazowy_sygnal(obv, "SHORT", 0.60, [f"OBV ({obv:.0f}) < EMA20 — dystrybucja"])


class NeuronVWAP(MikroNeuron):
    """
    V-02 | VWAP — Volume Weighted Average Price.
    Kluczowy poziom instytucjonalny. Cena powyżej VWAP = bull bias.
    Odchylenie +/-2 std = overbought/oversold (V-WAPS).
    """
    KLUCZ = "V-02"
    LEGION = "SWING"
    WSKAZNIK = "VWAP"
    KATEGORIA = "F"
    WAGA = 8

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        vwap = wskazniki.get("VWAP")
        vwap_std = wskazniki.get("VWAP_STD")

        if None in (close, vwap):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak VWAP"])

        odchylenie_pct = (close - vwap) / vwap if vwap > 0 else 0

        if vwap_std and vwap_std > 0:
            odchylenie_std = (close - vwap) / vwap_std
            if odchylenie_std <= -2:
                return self._bazowy_sygnal(close, "LONG", 0.85,
                    [f"Cena {odchylenie_std:.1f}σ poniżej VWAP — mean reversion LONG"])
            if odchylenie_std >= 2:
                return self._bazowy_sygnal(close, "SHORT", 0.85,
                    [f"Cena {odchylenie_std:.1f}σ powyżej VWAP — mean reversion SHORT"])
            if odchylenie_std >= 0:
                return self._bazowy_sygnal(close, "LONG", 0.55,
                    [f"Cena powyżej VWAP ({odchylenie_pct:+.2%})"])
            return self._bazowy_sygnal(close, "SHORT", 0.55,
                [f"Cena poniżej VWAP ({odchylenie_pct:+.2%})"])

        # Bez std — prosta pozycja względem VWAP
        if close > vwap:
            pewnosc = min(0.70, 0.50 + abs(odchylenie_pct) * 5)
            return self._bazowy_sygnal(close, "LONG", pewnosc,
                [f"Cena ({close:.2f}) powyżej VWAP ({vwap:.2f}), delta={odchylenie_pct:+.2%}"])
        pewnosc = min(0.70, 0.50 + abs(odchylenie_pct) * 5)
        return self._bazowy_sygnal(close, "SHORT", pewnosc,
            [f"Cena ({close:.2f}) poniżej VWAP ({vwap:.2f}), delta={odchylenie_pct:+.2%}"])


class NeuronCVD(MikroNeuron):
    """
    V-03 | CVD (Cumulative Volume Delta) — netto kupno vs sprzedaż.
    CVD > 0 → dominacja kupujących, CVD < 0 → sprzedający.
    Dywergencja CVD vs cena = spot odwrócenia.
    """
    KLUCZ = "V-03"
    LEGION = "SCALP"
    WSKAZNIK = "CVD"
    KATEGORIA = "F"
    WAGA = 8
    DOSTEPNY = True   # AdapterCVD (Binance aggTrades publiczne, bez klucza) — Faza C
    # Prawo XV: w backteście CSV (bez trade-feedu) abstynuje (NEUTRAL); live/paper
    # AdapterCVD liczy CVD z publicznego aggTrades → V-03 głosuje.

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        cvd = wskazniki.get("CVD")
        cvd_prev = wskazniki.get("CVD_PREV")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if cvd is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CVD"])

        # Dywergencja
        if cvd_prev is not None and close is not None and close_prev is not None:
            cvd_rosnie = cvd > cvd_prev
            cena_rosnie = close > close_prev

            if cena_rosnie and not cvd_rosnie:
                return self._bazowy_sygnal(cvd, "SHORT", 0.80,
                    [f"CVD DYWERGENCJA BEAR: cena↑ ale CVD↓ ({cvd:.0f} < {cvd_prev:.0f})"])
            if not cena_rosnie and cvd_rosnie:
                return self._bazowy_sygnal(cvd, "LONG", 0.80,
                    [f"CVD DYWERGENCJA BULL: cena↓ ale CVD↑ ({cvd:.0f} > {cvd_prev:.0f})"])

        if cvd > 0:
            return self._bazowy_sygnal(cvd, "LONG", 0.60, [f"CVD={cvd:.0f} pozytywny — kupujący dominują"])
        return self._bazowy_sygnal(cvd, "SHORT", 0.60, [f"CVD={cvd:.0f} negatywny — sprzedający dominują"])


class NeuronVolumeAnomaly(MikroNeuron):
    """
    V-04 | Volume Anomaly — wolumen vs średnia.
    Wolumen 3× powyżej 20MA = anomalia → potwierdzenie ruchu.
    """
    KLUCZ = "V-04"
    LEGION = "SCALP"
    WSKAZNIK = "VOLUME_ANOMALY"
    KATEGORIA = "F"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        vol = wskazniki.get("VOLUME")
        vol_ma20 = wskazniki.get("VOLUME_MA20")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if vol is None or vol_ma20 is None or vol_ma20 == 0:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych wolumenu"])

        ratio = vol / vol_ma20

        if ratio < 1.5:
            return self._bazowy_sygnal(ratio, "NEUTRAL", 0.10,
                [f"Wolumen normalny: {ratio:.1f}× średniej"])

        if close is not None and close_prev is not None:
            cena_rosnie = close > close_prev
        else:
            cena_rosnie = None

        if ratio >= 3.0:
            pewnosc = 0.85
            opis = f"ANOMALIA WOLUMENU: {ratio:.1f}× powyżej MA20"
        else:
            pewnosc = 0.65
            opis = f"Podwyższony wolumen: {ratio:.1f}× MA20"

        if cena_rosnie is True:
            return self._bazowy_sygnal(ratio, "LONG", pewnosc, [opis + " — potwierdza wzrost"])
        if cena_rosnie is False:
            return self._bazowy_sygnal(ratio, "SHORT", pewnosc, [opis + " — potwierdza spadek"])
        return self._bazowy_sygnal(ratio, "NEUTRAL", pewnosc * 0.5, [opis + " — brak kierunku ceny"])


class NeuronForceIndex(MikroNeuron):
    """
    V-05 | Force Index Eldera (BIB-015, Alexander Elder "Trading for a Living").
    Siła ruchu = kierunek × dystans × wolumen, wygładzona EMA.

    Dwie skale (jak w Triple Screen Eldera):
      • FI(13) — trend średnioterminowy (2. ekran): >0 byki, <0 niedźwiedzie
      • FI(2)  — krótkoterminowy trigger pullbacku (wejście)

    Doktryna Eldera: kupuj w trendzie wzrostowym (FI13>0), gdy FI(2) chwilowo
    spadnie poniżej zera (pullback) — i odwrotnie dla short. To łączy kierunek
    z timingiem w jednym głosie (Prawo XV — pełne wykorzystanie obu skal).
    """
    KLUCZ = "V-05"
    LEGION = "SWING"
    WSKAZNIK = "FORCE_INDEX"
    KATEGORIA = "F"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        fi13 = wskazniki.get("FORCE_INDEX_13")
        fi2 = wskazniki.get("FORCE_INDEX_2")

        if fi13 is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Force Index"])

        # FI(13) == 0 → brak przewagi byków/niedźwiedzi (płaska siła trendu) → NEUTRAL.
        # Nie zgadujemy kierunku na zerze (Prawo XV — bez fałszywego głosu).
        if fi13 == 0:
            return self._bazowy_sygnal(fi13, "NEUTRAL", 0.10,
                ["Force Index(13)=0 — brak przewagi byków/niedźwiedzi"])

        # Trend średnioterminowy (2. ekran) — znak FI(13) ściśle dodatni/ujemny
        trend_long = fi13 > 0

        if fi2 is None:
            # Bez krótkiej skali — sam kierunek trendu
            kierunek = "LONG" if trend_long else "SHORT"
            return self._bazowy_sygnal(fi13, kierunek, 0.55,
                [f"Force Index(13)={fi13:.0f} — {'byki' if trend_long else 'niedźwiedzie'}"])

        # FI(2) == 0 → krótkoterminowa siła płaska, brak triggera wejścia → słaby głos trendu
        # (nie spadamy implicytnie do SHORT — to był błąd graniczny przy trendzie↑).
        if fi2 == 0:
            kierunek = "LONG" if trend_long else "SHORT"
            return self._bazowy_sygnal(fi13, kierunek, 0.40,
                [f"FI(2)=0 brak triggera — słaby głos trendu FI(13)={fi13:.0f}"])

        # Pullback Eldera: trend↑ + FI(2)<0 = okazja LONG (kupuj słabość w sile)
        if trend_long and fi2 < 0:
            return self._bazowy_sygnal(fi13, "LONG", 0.80,
                [f"Pullback Eldera: FI(13)={fi13:.0f}>0 (trend↑), FI(2)={fi2:.0f}<0 — kup słabość"])
        if not trend_long and fi2 > 0:
            return self._bazowy_sygnal(fi13, "SHORT", 0.80,
                [f"Odbicie Eldera: FI(13)={fi13:.0f}<0 (trend↓), FI(2)={fi2:.0f}>0 — sprzedaj siłę"])

        # Momentum zgodny w obu skalach (słabszy sygnał — ruch już trwa).
        # Tu pozostają tylko: (trend↑ & FI(2)>0) → LONG, (trend↓ & FI(2)<0) → SHORT.
        if trend_long:   # fi2 > 0
            return self._bazowy_sygnal(fi13, "LONG", 0.58,
                [f"Force Index zgodny↑: FI(13)={fi13:.0f}, FI(2)={fi2:.0f} — byki napierają"])
        return self._bazowy_sygnal(fi13, "SHORT", 0.58,   # not trend_long & fi2 < 0
            [f"Force Index zgodny↓: FI(13)={fi13:.0f}, FI(2)={fi2:.0f} — niedźwiedzie napierają"])


class NeuronRVOL(MikroNeuron):
    """
    X-11 | Relative Volume — czy ruch ma wsparcie wolumenu. RVOL = vol / średnia(20).
    Wysoki RVOL + ruch w górę = LONG (wsparcie), + w dół = SHORT. Niski = brak siły.
    Dane z Bramy: RVOL, CLOSE, CLOSE_PREV.
    """
    KLUCZ = "X-11"
    LEGION = "VOLUME"
    WSKAZNIK = "RVOL"
    KATEGORIA = "F"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        rvol = wskazniki.get("RVOL")
        close = wskazniki.get("CLOSE")
        prev = wskazniki.get("CLOSE_PREV")
        if rvol is None or close is None or prev is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych RVOL."])
        if rvol >= 1.5:
            pewnosc = 0.75 if rvol >= 2.5 else 0.60
            if close > prev:
                return self._bazowy_sygnal(rvol, "LONG", pewnosc, [f"RVOL={rvol:.2f}× + ruch↑ → wsparcie wolumenu"])
            if close < prev:
                return self._bazowy_sygnal(rvol, "SHORT", pewnosc, [f"RVOL={rvol:.2f}× + ruch↓ → presja podaży"])
        if rvol < 0.7:
            return self._bazowy_sygnal(rvol, "NEUTRAL", 0.15, [f"RVOL={rvol:.2f}× niski → brak zainteresowania"])
        return self._bazowy_sygnal(rvol, "NEUTRAL", 0.25, [f"RVOL={rvol:.2f}× przeciętny"])


class NeuronDeltaDivergence(MikroNeuron):
    """
    V-06 | Delta Divergence — dywergencja cena↔delta wolumenu (SCALP, W-322).

    Dla nowicjusza: „delta" to różnica między agresywnym kupnem a sprzedażą w barze.
    Bez feedu L2 liczymy ją z OHLCV (proxy): jeśli świeca zamyka się przy szczycie =
    presja kupna (+), przy dnie = presja sprzedaży (−). Sumujemy → CVD-proxy. Gdy
    CENA robi nowy szczyt, a CVD-proxy NIE potwierdza (spada) → presja kupna słabnie
    → wczesny sygnał REWERSJI (klasyka order-flow / footprint).

    Sygnał (wartość ∈ [−1, 1] z Bramy):
      • DELTA_DIV > +prog → cena↓ ale delta↑ (akumulacja w spadku) → LONG (rewersja w górę).
      • DELTA_DIV < −prog → cena↑ ale delta↓ (dystrybucja w wzroście) → SHORT (rewersja w dół).
      • |DELTA_DIV| ≤ prog → NEUTRAL (cena i delta zgodne — brak dywergencji).

    Dlaczego ORTOGONALNY (Prawo XVI): V-03 CVD mierzy POZIOM delty (kierunek presji),
    V-06 mierzy DYWERGENCJĘ delty względem ceny (rozjazd) — inna informacja, wczesny
    sygnał wyczerpania ruchu. V-06 jest OHLCV-only (żywy bez feedu, w przeciwieństwie do V-03).

    Źródło: order-flow / footprint (LiteFinance, NinjaTrader 2026) — delta divergence
            jako wczesny sygnał rewersji.
    """
    KLUCZ = "V-06"
    LEGION = "WSPOLNY"
    WSKAZNIK = "DELTA_DIV"
    KATEGORIA = "F"
    WAGA = 5
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG = 0.15   # |dywergencja| powyżej = sygnał kierunkowy

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        dd = wskazniki.get("DELTA_DIV")
        if dd is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak DELTA_DIV (wymaga ≥15 barów)"])

        if abs(dd) <= self._PROG:
            return self._bazowy_sygnal(round(dd, 4), "NEUTRAL", 0.0,
                [f"Cena i delta zgodne: dywergencja {dd:+.2f} (|{abs(dd):.2f}| ≤ {self._PROG})"])

        pewnosc = round(min(0.80, 0.45 + (abs(dd) - self._PROG) * 0.7), 4)
        if dd > 0:
            return self._bazowy_sygnal(round(dd, 4), "LONG", pewnosc,
                [f"📉→📈 DELTA DIVERGENCE: cena↓ ale delta↑ ({dd:+.2f}) — akumulacja → LONG ({pewnosc:.0%})"])
        return self._bazowy_sygnal(round(dd, 4), "SHORT", pewnosc,
            [f"📈→📉 DELTA DIVERGENCE: cena↑ ale delta↓ ({dd:+.2f}) — dystrybucja → SHORT ({pewnosc:.0%})"])


class NeuronAnchoredVWAP(MikroNeuron):
    """
    V-07 | Anchored VWAP — VWAP kotwiczony od pivotu (SWING, W-322).

    Dla nowicjusza: zwykły VWAP (V-02) liczy średnią ważoną wolumenem od początku okna.
    Anchored VWAP kotwiczy ją od OSTATNIEGO ISTOTNEGO PIVOTU (swing high/low) — przez co
    pokazuje średni koszt uczestników OD tego wydarzenia. Cena nad AVWAP = kupujący od
    pivotu są na plusie (przewaga byków); pod AVWAP = na minusie (przewaga niedźwiedzi).

    Sygnał (odchylenie ceny od AVWAP, w %):
      • CLOSE > AVWAP × (1 + prog) → LONG (przewaga kupujących od pivotu).
      • CLOSE < AVWAP × (1 − prog) → SHORT (przewaga sprzedających).
      • w paśmie ±prog wokół AVWAP → NEUTRAL (równowaga przy kotwicy).

    Dlaczego ORTOGONALNY (Prawo XVI): V-02 VWAP to średnia OD POCZĄTKU OKNA (sesyjna),
    V-07 kotwiczy od PIVOTU STRUKTURALNEGO — inny punkt odniesienia, inna informacja.

    Źródło: Highstrike / XS 2025 — anchored VWAP w swing tradingu.
    """
    KLUCZ = "V-07"
    LEGION = "WSPOLNY"
    WSKAZNIK = "AVWAP"
    KATEGORIA = "F"
    WAGA = 5
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _PROG = 0.005   # ±0.5% pasmo neutralne wokół AVWAP

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        avwap = wskazniki.get("AVWAP")
        close = wskazniki.get("CLOSE")
        if avwap is None or close is None or avwap <= 0:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak AVWAP/CLOSE"])

        odchyl = (close - avwap) / avwap
        if abs(odchyl) <= self._PROG:
            return self._bazowy_sygnal(round(odchyl, 4), "NEUTRAL", 0.0,
                [f"Cena przy AVWAP: odchyl {odchyl:+.2%} (|{abs(odchyl):.2%}| ≤ {self._PROG:.1%})"])

        pewnosc = round(min(0.78, 0.50 + (abs(odchyl) - self._PROG) * 8.0), 4)
        if odchyl > 0:
            return self._bazowy_sygnal(round(odchyl, 4), "LONG", pewnosc,
                [f"Cena {odchyl:+.2%} nad AVWAP ({avwap:.2f}) — kupujący od pivotu na plusie → LONG ({pewnosc:.0%})"])
        return self._bazowy_sygnal(round(odchyl, 4), "SHORT", pewnosc,
            [f"Cena {odchyl:+.2%} pod AVWAP ({avwap:.2f}) — sprzedający od pivotu na plusie → SHORT ({pewnosc:.0%})"])
