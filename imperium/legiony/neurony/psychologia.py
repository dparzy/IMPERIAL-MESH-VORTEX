"""
🏛️ IMV-ORI | Neurony Psychologii — Dywizja Wyrocznia (PSY)
Fear & Greed, Funding Rate Extreme, Capitulation, Panika Detaliczna.
Behawioralne wzorce rynku — wyjście z tłumu.

DOSTĘPNOŚĆ (Faza B — obudzone przez adaptery publiczne, bez klucza API):
  PSY-01 FUNDING_RATE     — AdapterFutures (Binance fapi publiczne, bez klucza).
  PSY-02 LONG_SHORT_RATIO — AdapterFutures (Binance futures/data publiczne).
  PSY-03 FEAR_GREED_INDEX — AdapterFearGreed (alternative.me, darmowe bez klucza).
  PSY-04 OPEN_INTEREST    — AdapterFutures (Binance fapi openInterest publiczne).
  Wszystkie AKTYWNE (DOSTEPNY=True) — adaptery wpięte w pipeline (Dyrygent).
  Prawo XV: w czystym backteście z CSV (bez kolumny funding/OI) neuron ABSTYNUJE
  (zwraca NEUTRAL, rój wyklucza go z głosu kierunkowego — nie martwy ciężar).
  W trybie live/paper adapter dolewa realne dane → neuron głosuje.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu

_POWOD_FUTURES = "Wymaga API futures (MEXC). Ustaw MEXC_API_KEY i podepnij adapter."
_POWOD_SENTIMENT = "Wymaga zewnętrznego API sentymentu (alternative.me / CoinGlass)."


class NeuronFearGreed(MikroNeuron):
    """
    PSY-03 | Fear & Greed Index (0-100) — sentyment rynku.
    Ekstremalny strach (<15) = okazja LONG (contrarian).
    Ekstremalna chciwość (>85) = okazja SHORT (contrarian).
    """
    KLUCZ = "PSY-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "FEAR_GREED"
    KATEGORIA = "R"
    WAGA = 7
    DOSTEPNY = True   # AdapterFearGreed (alternative.me, bez klucza)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        fg = wskazniki.get("FEAR_GREED_INDEX")
        if fg is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak F&G Index"])

        if fg <= 10:
            return self._bazowy_sygnal(fg, "LONG", 0.90, [f"F&G={fg:.0f} EKSTREMALNY STRACH — contrarian LONG"])
        if fg <= 20:
            return self._bazowy_sygnal(fg, "LONG", 0.75, [f"F&G={fg:.0f} Extreme Fear — contrarian LONG"])
        if fg <= 35:
            return self._bazowy_sygnal(fg, "LONG", 0.55, [f"F&G={fg:.0f} Fear — umiarkowany LONG"])
        if fg >= 90:
            return self._bazowy_sygnal(fg, "SHORT", 0.90, [f"F&G={fg:.0f} EKSTREMALNA CHCIWOŚĆ — contrarian SHORT"])
        if fg >= 80:
            return self._bazowy_sygnal(fg, "SHORT", 0.75, [f"F&G={fg:.0f} Extreme Greed — contrarian SHORT"])
        if fg >= 65:
            return self._bazowy_sygnal(fg, "SHORT", 0.50, [f"F&G={fg:.0f} Greed — umiarkowany SHORT"])
        return self._bazowy_sygnal(fg, "NEUTRAL", 0.20, [f"F&G={fg:.0f} strefa neutralna"])


class NeuronFundingExtreme(MikroNeuron):
    """
    PSY-01 | Funding Rate Extreme — ekstremalny koszt utrzymania pozycji.
    Bardzo wysoki funding (>0.1%) = wszyscy są LONG = ryzyko squeeze SHORT.
    Bardzo niski (<-0.05%) = wszyscy są SHORT = ryzyko squeeze LONG.
    Kontrariański: idź przeciwko tłumowi gdy funding ekstremalny.
    """
    KLUCZ = "PSY-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "FUNDING_EXTREME"
    KATEGORIA = "R"
    WAGA = 8
    DOSTEPNY = True   # AdapterFutures (Binance fapi, bez klucza)

    FUNDING_HIGH = 0.001    # 0.1% per 8H — dużo longerów
    FUNDING_LOW = -0.0005   # -0.05% per 8H — dużo shorterów

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        funding = wskazniki.get("FUNDING_RATE")
        if funding is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Funding Rate"])

        if funding >= self.FUNDING_HIGH * 2:
            return self._bazowy_sygnal(funding, "SHORT", 0.85,
                [f"Funding EKSTREMALNIE wysoki ({funding:.4%}) — crowded long, squeeze SHORT"])
        if funding >= self.FUNDING_HIGH:
            return self._bazowy_sygnal(funding, "SHORT", 0.65,
                [f"Funding wysoki ({funding:.4%}) — długi dominują"])
        if funding <= self.FUNDING_LOW * 2:
            return self._bazowy_sygnal(funding, "LONG", 0.85,
                [f"Funding EKSTREMALNIE niski ({funding:.4%}) — crowded short, squeeze LONG"])
        if funding <= self.FUNDING_LOW:
            return self._bazowy_sygnal(funding, "LONG", 0.65,
                [f"Funding niski ({funding:.4%}) — krótcy dominują"])
        return self._bazowy_sygnal(funding, "NEUTRAL", 0.10,
            [f"Funding neutralny ({funding:.4%})"])


class NeuronPanikaDetal(MikroNeuron):
    """
    PSY-02 | Panika Detalisty — Long/Short Ratio ekstremalny.
    Gdy 80%+ rynku jest PO JEDNEJ STRONIE = kontrariański sygnał.
    """
    KLUCZ = "PSY-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "LS_RATIO"
    KATEGORIA = "R"
    WAGA = 7
    DOSTEPNY = True   # AdapterFutures (Binance fapi, bez klucza)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ls_ratio = wskazniki.get("LONG_SHORT_RATIO")  # long/(long+short), 0.0-1.0
        if ls_ratio is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak L/S Ratio"])

        long_pct = ls_ratio * 100
        short_pct = (1 - ls_ratio) * 100

        if long_pct >= 80:
            return self._bazowy_sygnal(ls_ratio, "SHORT", 0.80,
                [f"L/S={long_pct:.0f}%/{short_pct:.0f}% — tłum LONG — contrarian SHORT"])
        if long_pct >= 70:
            return self._bazowy_sygnal(ls_ratio, "SHORT", 0.60,
                [f"L/S={long_pct:.0f}%/{short_pct:.0f}% — lekka dominacja longów"])
        if short_pct >= 80:
            return self._bazowy_sygnal(ls_ratio, "LONG", 0.80,
                [f"L/S={long_pct:.0f}%/{short_pct:.0f}% — tłum SHORT — contrarian LONG"])
        if short_pct >= 70:
            return self._bazowy_sygnal(ls_ratio, "LONG", 0.60,
                [f"L/S={long_pct:.0f}%/{short_pct:.0f}% — lekka dominacja shortów"])
        return self._bazowy_sygnal(ls_ratio, "NEUTRAL", 0.20,
            [f"L/S={long_pct:.0f}%/{short_pct:.0f}% — balans"])


class NeuronOIDiv(MikroNeuron):
    """
    PSY-04 | Open Interest Divergence — OI vs cena.
    OI rośnie + cena rośnie = potwierdzona siła bull.
    OI spada + cena rośnie = słaby wzrost, dużo zamknięć = ryzyko.
    OI rośnie + cena spada = potwierdzona siła bear.
    """
    KLUCZ = "PSY-04"
    LEGION = "WSPOLNY"
    WSKAZNIK = "OI_DIVERGENCE"
    KATEGORIA = "R"
    WAGA = 7
    DOSTEPNY = True   # AdapterFutures (Binance fapi, bez klucza)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        oi = wskazniki.get("OPEN_INTEREST")
        oi_prev = wskazniki.get("OPEN_INTEREST_PREV")
        close = wskazniki.get("CLOSE")
        close_prev = wskazniki.get("CLOSE_PREV")

        if None in (oi, oi_prev, close, close_prev):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak OI/cena"])

        oi_rosnie = oi > oi_prev
        cena_rosnie = close > close_prev
        oi_zmiana_pct = (oi - oi_prev) / oi_prev if oi_prev > 0 else 0

        if cena_rosnie and oi_rosnie:
            pewnosc = min(0.80, 0.55 + abs(oi_zmiana_pct) * 3)
            return self._bazowy_sygnal(oi, "LONG", pewnosc,
                [f"OI rośnie (+{oi_zmiana_pct:.1%}) + cena↑ — potwierdzona siła BULL"])
        if not cena_rosnie and oi_rosnie:
            pewnosc = min(0.80, 0.55 + abs(oi_zmiana_pct) * 3)
            return self._bazowy_sygnal(oi, "SHORT", pewnosc,
                [f"OI rośnie (+{oi_zmiana_pct:.1%}) + cena↓ — potwierdzona siła BEAR"])
        if cena_rosnie and not oi_rosnie:
            return self._bazowy_sygnal(oi, "SHORT", 0.60,
                ["DYWERGENCJA: cena↑ ale OI spada — słaby wzrost, dużo zamknięć"])
        return self._bazowy_sygnal(oi, "LONG", 0.60,
            ["DYWERGENCJA: cena↓ ale OI spada — krótcy zamykają pozycje"])
