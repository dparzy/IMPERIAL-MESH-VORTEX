"""
🌐 W-350/K | Neurony Makro — Dywizja Intermarket (Murphy, Technical Analysis rozdz. 15)

Kategoria K — makro/intermarket: DXY, złoto, przepływ kapitału poza krypto.

Murphy: korelacje między rynkami (waluta→surowce→obligacje→akcje) dają WYPRZEDZAJĄCE
sygnały trendowe. DXY ↑ → ryzykowne aktywa ↓ (negatywna korelacja BTC/DXY historyczna).
Złoto ↑ + DXY ↓ = risk-off bez paniki, często poprzedza alt-season.

UWAGA: K-01..K-02 wymagają zewnętrznych szeregów makro (DXY, XAUUSD).
Brama OHLCV NIE dostarcza tych danych. Neurony abstynują (NEUTRAL) bez danych —
tak samo jak PSY-01..04 bez API futures.

Jak dostarczyć dane (z laptopa):
  python narzedzia/pobierz_makro.py   # pobiera DXY/XAUUSD/SPX z Yahoo Finance do dane/makro/
  Następnie backtest_portfel(macro_pliki={"DXY": "dane/makro/DXY_1D.csv"})
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu

_POWOD_K = (
    "Wymaga zewnętrznych danych makro (DXY, XAUUSD). "
    "Uruchom narzedzia/pobierz_makro.py i podepnij macro_pliki= w backtest_portfel()."
)


class NeuronDXYTrend(MikroNeuron):
    """
    K-01 | DXY Trend — kierunek dolara amerykańskiego vs BTC.

    Negatywna korelacja DXY↔BTC (Murphy rozdz. 15, BIB-002 W-085):
      DXY momentum > +0.5σ → dolar się umacnia → presja na BTC/krypto → SHORT bias
      DXY momentum < -0.5σ → dolar słabnie → dopływ do ryzykownych → LONG bias
      DXY neutralny (±0.5σ) → NEUTRAL (brak makro-sygnału)

    DXY_MOM: znormalizowany momentum DXY = (DXY_now - DXY_EMA20) / std_20.
    Wstrzykiwany przez backtest_portfel() z pliku dane/makro/DXY_*.csv.
    """
    KLUCZ = "K-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "DXY_MOM"
    KATEGORIA = "K"
    WAGA = 5
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD_K
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        dxy = wskazniki.get("DXY_MOM")
        if dxy is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak DXY_MOM — uruchom pobierz_makro.py"])

        if dxy > 1.0:
            return self._bazowy_sygnal(dxy, "SHORT", 0.75,
                [f"DXY_MOM={dxy:+.2f}σ — silny dolar, presja na krypto"])
        if dxy > 0.5:
            return self._bazowy_sygnal(dxy, "SHORT", 0.55,
                [f"DXY_MOM={dxy:+.2f}σ — dolar rośnie, ostrożność"])
        if dxy < -1.0:
            return self._bazowy_sygnal(dxy, "LONG", 0.75,
                [f"DXY_MOM={dxy:+.2f}σ — słaby dolar, dopływ do krypto"])
        if dxy < -0.5:
            return self._bazowy_sygnal(dxy, "LONG", 0.55,
                [f"DXY_MOM={dxy:+.2f}σ — dolar słabnie, lekki tailwind"])
        return self._bazowy_sygnal(dxy, "NEUTRAL", 0.0,
            [f"DXY_MOM={dxy:+.2f}σ — dolar neutralny"])


class NeuronGoldBTC(MikroNeuron):
    """
    K-02 | Gold/BTC Ratio Momentum — intermarket: złoto vs Bitcoin.

    Murphy rozdz. 15 + Burniske/Tatar *Cryptoassets* (BIB-015, W-089):
    Gdy złoto rośnie szybciej niż BTC → risk-off (kapitał ucieka do bezpiecznych
    przystani) → to NIE jest alt-season, uważaj na longa.
    Gdy BTC rośnie szybciej niż złoto → risk-on (rynek wierzy w krypto) → LONG bias.

    GOLD_BTC_MOM: znormalizowane momentum stosunku XAUUSD/BTCUSD.
      > +0.5σ → złoto outperformuje → risk-off → SHORT
      < -0.5σ → BTC outperformuje → risk-on → LONG
    """
    KLUCZ = "K-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "GOLD_BTC_MOM"
    KATEGORIA = "K"
    WAGA = 4
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD_K
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        gbm = wskazniki.get("GOLD_BTC_MOM")
        if gbm is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak GOLD_BTC_MOM — uruchom pobierz_makro.py"])

        if gbm > 1.0:
            return self._bazowy_sygnal(gbm, "SHORT", 0.70,
                [f"GOLD/BTC_MOM={gbm:+.2f}σ — złoto silnie outperformuje, risk-off"])
        if gbm > 0.5:
            return self._bazowy_sygnal(gbm, "SHORT", 0.50,
                [f"GOLD/BTC_MOM={gbm:+.2f}σ — złoto rośnie vs BTC, ostrożność"])
        if gbm < -1.0:
            return self._bazowy_sygnal(gbm, "LONG", 0.70,
                [f"GOLD/BTC_MOM={gbm:+.2f}σ — BTC silnie outperformuje złoto, risk-on"])
        if gbm < -0.5:
            return self._bazowy_sygnal(gbm, "LONG", 0.50,
                [f"GOLD/BTC_MOM={gbm:+.2f}σ — BTC rośnie vs złoto, lekki tailwind"])
        return self._bazowy_sygnal(gbm, "NEUTRAL", 0.0,
            [f"GOLD/BTC_MOM={gbm:+.2f}σ — stosunek neutralny"])


class NeuronStablecoinFlow(MikroNeuron):
    """
    K-03 | Stablecoin Supply Flow — makro-płynność krypto („suchy proch").

    Druk stablecoinów (rosnąca podaż USDT/USDC) = świeży kapitał gotowy wejść =
    napływ = bullish. Umorzenia (spadek podaży) = kapitał wychodzi = bearish.
    Kierunek ZWALIDOWANY pomiarem: 7d % zmiana podaży ma IC +0.05..+0.10 @7-30d na
    zwroty BTC (narzedzia/pomiar_stablecoin_ic.py, AERARIUM, 2026-07-15) — DODATNI,
    trend-following (nie kontrariański). Sygnał wolny (tygodnie-miesiąc), makro.

    STABLE_FLOW: 7-dniowa % zmiana total supply (DefiLlama). Dostarcza AdapterStablecoin
    (opt-in --stablecoin). Bez adaptera abstynuje (Prawo XV). DOSTEPNY=True.
    """
    KLUCZ = "K-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "STABLE_FLOW"
    KATEGORIA = "K"
    WAGA = 6   # wstępna (walidacja jednoreżimowa)
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        flow = wskazniki.get("STABLE_FLOW")
        if flow is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak STABLE_FLOW"])

        if flow >= 0.015:
            return self._bazowy_sygnal(flow, "LONG", 0.70, [f"Podaż stablecoinów +{flow:.1%}/7d — silny druk, napływ kapitału"])
        if flow >= 0.004:
            return self._bazowy_sygnal(flow, "LONG", 0.50, [f"Podaż stablecoinów +{flow:.1%}/7d — druk, lekki napływ"])
        if flow <= -0.008:
            return self._bazowy_sygnal(flow, "SHORT", 0.50, [f"Podaż stablecoinów {flow:.1%}/7d — umorzenia, odpływ kapitału"])
        return self._bazowy_sygnal(flow, "NEUTRAL", 0.15, [f"Podaż stablecoinów {flow:+.1%}/7d — stabilna"])


class NeuronUSDStrength(MikroNeuron):
    """
    K-04 | USD Strength (DXY-proxy) — siła dolara vs zwroty BTC (BTC-DXY inverse).

    Silny USD (rozciągnięty vs ~6-mies. zakres) = odpływ z ryzyka = bearish BTC.
    Słaby USD = dopływ do krypto = bullish. Kierunek ZWALIDOWANY pomiarem: z-score
    poziomu USD na oknie 120d ma IC -0.17 @14d, -0.27 @30d na zwroty BTC (MONETA,
    narzedzia/pomiar_usd_ic.py, 2026-07-16). UWAGA (Prawo XVI): to INNA informacja niż
    K-01 DXYTrend (forma EMA20-momentum zmierzona jako SZUM) — tu z-score poziomu 120d.

    USD_ZSCORE: (USD_teraz − mean_120d)/std_120d. Dostarcza AdapterUSD (Frankfurter,
    opt-in --usd). Bez adaptera abstynuje (Prawo XV). DOSTEPNY=True. Sygnał wolny (makro).
    """
    KLUCZ = "K-04"
    LEGION = "WSPOLNY"
    WSKAZNIK = "USD_ZSCORE"
    KATEGORIA = "K"
    WAGA = 6
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        z = wskazniki.get("USD_ZSCORE")
        if z is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak USD_ZSCORE"])

        if z >= 1.5:
            return self._bazowy_sygnal(z, "SHORT", 0.70, [f"USD_z={z:+.2f} — silny dolar rozciągnięty, presja na BTC"])
        if z >= 0.7:
            return self._bazowy_sygnal(z, "SHORT", 0.50, [f"USD_z={z:+.2f} — dolar podwyższony, ostrożność"])
        if z <= -1.5:
            return self._bazowy_sygnal(z, "LONG", 0.70, [f"USD_z={z:+.2f} — słaby dolar, dopływ do krypto"])
        if z <= -0.7:
            return self._bazowy_sygnal(z, "LONG", 0.50, [f"USD_z={z:+.2f} — dolar słabnie, lekki tailwind"])
        return self._bazowy_sygnal(z, "NEUTRAL", 0.15, [f"USD_z={z:+.2f} — dolar w zakresie"])
