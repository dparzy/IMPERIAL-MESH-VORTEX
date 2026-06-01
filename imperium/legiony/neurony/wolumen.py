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
    KATEGORIA = "V"
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
    KATEGORIA = "V"
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
    KATEGORIA = "V"
    WAGA = 8
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = (
        "CVD wymaga danych o stronie agresora (buy/sell volume z tick/trade feed). "
        "OHLCV tego nie zawiera. Aktywuje się przy podpięciu trade feed z MEXC."
    )

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        cvd = wskazniki.get("CVD")
        cvd_prev = wskazniki.get("CVD_PREV")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if cvd is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak CVD"])

        powody = []

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
    KATEGORIA = "V"
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


class NeuronRVOL(MikroNeuron):
    """
    X-11 | Relative Volume — czy ruch ma wsparcie wolumenu. RVOL = vol / średnia(20).
    Wysoki RVOL + ruch w górę = LONG (wsparcie), + w dół = SHORT. Niski = brak siły.
    Dane z Bramy: RVOL, CLOSE, CLOSE_PREV.
    """
    KLUCZ = "X-11"
    LEGION = "VOLUME"
    WSKAZNIK = "RVOL"
    KATEGORIA = "V"
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
