"""
🗺️ IMV | Rejestr Strategii — strategie z bazy ludzi, zmapowane na ŻYWE neurony

Każda strategia tu wskazuje TYLKO klucze neuronów, które FAKTYCZNIE istnieją w
kodzie i są aktywne (DOSTEPNY=True). To jest "Klucznik" w praktyce — most między
katalogiem strategii (docs/KATALOG_STRATEGII.md) a żywym rojem.

Źródło przepisów: docs/KATALOG_STRATEGII.md (zmapowane na realne klucze kodu).
Strategie wymagające neuronów jeszcze nieistniejących (OrderFlow, CVD, SMC, on-chain)
NIE wchodzą tu, dopóki ich neurony nie są aktywne — inaczej Klucznik podniósłby alarm.

Rozbudowa: gdy ożywiamy nowy neuron, możemy dodać/wzbogacić strategie, które go używają.
"""

from imperium.legiony.strategie.baza import Strategia


def wszystkie_strategie() -> list:
    """Strategie zmapowane na żywe, aktywne neurony (klucze istnieją w kodzie)."""
    return [
        # ── Legio X Equestris (Scalp) ────────────────────────────────────────
        Strategia(
            id="X-SC-001", nazwa="PIORUN CEZARA", legion="X", styl="SC",
            warunki="ADX>25, wyraźny trend jednokierunkowy (M5)",
            zrodlo="IMV (syntetyczna)",
            neurony_wejscie=["X-05", "X-02"],   # EMA cross + StochRSI ekstremum
            neurony_filtr=["V-02", "XII-01"],   # VWAP + ADX siła trendu
            neurony_wyjscie=["X-02", "X-25"],   # StochRSI ekstremum / ATR dewiacja
            interwaly=["M5"], rezim_preferowany="TREND_STRONG",
            dzwignia="5×–10×", rr="1:2", status="SZKIC",
        ),
        Strategia(
            id="X-SC-002", nazwa="TORPEDA VWAP", legion="X", styl="SC",
            warunki="zakres dzienny, ruch od VWAP",
            zrodlo="klasyka day-traderów",
            neurony_wejscie=["V-02", "X-02"],   # VWAP odbicie + StochRSI ekstremum
            neurony_filtr=["X-05"],             # EMA trend wspiera odbicie
            neurony_wyjscie=["V-02", "X-25"],
            interwaly=["M5", "M15"], rezim_preferowany="RANGING",
            dzwignia="3×–7×", rr="1:1.5", status="SZKIC",
        ),
        # ── Legio XII Fulminata (Swing) ──────────────────────────────────────
        Strategia(
            id="XII-TR-001", nazwa="ZŁOTY ORZEŁ", legion="XII", styl="TR",
            warunki="EMA(50) przebija EMA(200) — Golden Cross (4H/1D)",
            zrodlo="klasyka — Golden Cross",
            neurony_wejscie=["XII-03", "XII-04"],   # EMA50/200 + Supertrend
            neurony_filtr=["XII-01", "V-01"],       # ADX siła + OBV wolumen
            neurony_wyjscie=["XII-03", "XII-04"],
            interwaly=["4H", "1D"], rezim_preferowany="TREND_STRONG",
            dzwignia="1×–3×", rr="1:3", status="SZKIC",
        ),
        Strategia(
            id="XII-BK-001", nazwa="PIORUNOWA BRAMA", legion="XII", styl="BK",
            warunki="BB squeeze → gwałtowne wybicie (4H/1D)",
            zrodlo="John Bollinger — squeeze play",
            neurony_wejscie=["X-04", "X-18"],       # BBands + Donchian wybicie
            neurony_filtr=["XII-04", "V-01"],       # Supertrend kierunek + OBV
            neurony_wyjscie=["X-04", "X-03"],       # BBands / MACD słabnie
            interwaly=["4H", "1D"], rezim_preferowany="VOLATILE",
            dzwignia="3×–8×", rr="1:2", status="SZKIC",
        ),
        # ── Multi-legion / klasyka świata ────────────────────────────────────
        Strategia(
            id="IMV-TR-001", nazwa="STRATEGIA TURTLES", legion="IMV", styl="TR",
            warunki="wybicie kanału Donchiana (1D)",
            zrodlo="Dennis/Eckhardt — Turtle Traders",
            neurony_wejscie=["X-18"],               # Donchian breakout
            neurony_filtr=["V-01", "XII-01", "X-25"],  # OBV + ADX + ATR sizing
            neurony_wyjscie=["X-18", "XII-04"],
            interwaly=["1D"], rezim_preferowany="TREND_STRONG",
            dzwignia="1×–2×", rr="1:4", status="SZKIC",
        ),
        Strategia(
            id="IMV-HY-003", nazwa="ICHIMOKU SHOGUN", legion="IMV", styl="HY",
            warunki="cena nad/pod chmurą Ichimoku (4H/1D)",
            zrodlo="Goichi Hosoda",
            neurony_wejscie=["XII-02", "X-05"],     # Ichimoku + EMA trend
            neurony_filtr=["V-01", "X-02"],         # OBV + StochRSI timing
            neurony_wyjscie=["XII-02", "XII-04"],
            interwaly=["4H", "1D"], rezim_preferowany="TREND_STRONG",
            dzwignia="1×–3×", rr="1:3", status="SZKIC",
        ),
        Strategia(
            id="IMV-TR-003", nazwa="MISTRZ MINERVINI", legion="IMV", styl="TR",
            warunki="Trend Template: cena>MA50>MA200, wszystkie rosnące (1D)",
            zrodlo="Mark Minervini — SEPA",
            neurony_wejscie=["XII-03", "XII-04"],   # EMA50/200 układ + Supertrend
            neurony_filtr=["V-01", "X-11"],         # OBV + RVOL (potwierdzenie VCP)
            neurony_wyjscie=["XII-03", "XII-01"],
            interwaly=["1D"], rezim_preferowany="TREND_STRONG",
            dzwignia="1×–3×", rr="1:3", status="SZKIC",
        ),
        # ── Legio XII Fulminata (Swing) — odwrócenie ────────────────────────
        Strategia(
            id="XII-RV-001", nazwa="BUMERANG SENATU", legion="XII", styl="RV",
            warunki="Dywergencja RSI + Fibonacci złota strefa → odwrócenie trendu (4H/1D)",
            zrodlo="Lawrence McMillan + klasyczna analiza techniczna",
            neurony_wejscie=["XII-07", "XII-05"],  # RSI dywergencja + Fibonacci strefa
            neurony_filtr=["XII-01", "V-01"],      # ADX (trend słabnie) + OBV potwierdzenie
            neurony_wyjscie=["XII-07", "XII-04"],  # Dywergencja zanika / Supertrend zmiana
            interwaly=["4H", "1D"], rezim_preferowany="RANGING",
            dzwignia="1×–3×", rr="1:2.5", status="SZKIC",
        ),
        # ── Faza 2: nowe strategie (aktywowane 2026-06-02) ───────────────────
        Strategia(
            id="X-SC-003", nazwa="BROOKS M2B", legion="X", styl="SC",
            warunki="Pullback do EMA, drugie wejście (M2B/M2S) z potwierdzeniem RSI",
            zrodlo="Al Brooks — Reading Price Action",
            neurony_wejscie=["X-05", "X-01"],   # EMA Cross trend + RSI poziom
            neurony_filtr=["X-02", "X-11"],     # StochRSI ekstremum + RVOL wolumen
            neurony_wyjscie=["X-25", "X-01"],   # ATR dewiacja / RSI reversal
            interwaly=["M5", "M15"], rezim_preferowany="TRENDING",
            dzwignia="3×–7×", rr="1:2", status="SZKIC",
        ),
        Strategia(
            id="IMV-TR-002", nazwa="PUDEŁKO DARVASA", legion="IMV", styl="TR",
            warunki="Wybicie z konsolidacji (Darvas Box): Donchian + BB — ruch ma wolumen",
            zrodlo="Nicolas Darvas — How I Made $2,000,000 in the Stock Market",
            neurony_wejscie=["X-18", "X-04"],   # Donchian wybicie + BBands rozszerzenie
            neurony_filtr=["V-01", "X-11"],     # OBV rośnie + RVOL potwierdzenie
            neurony_wyjscie=["X-18", "X-25"],   # Donchian odwrót / ATR-Z ekstremum
            interwaly=["4H", "1D"], rezim_preferowany="TREND_STRONG",
            dzwignia="1×–5×", rr="1:3", status="SZKIC",
        ),
        Strategia(
            id="IMV-RG-001", nazwa="STREET SMARTS", legion="IMV", styl="RG",
            warunki="Mean-reversion: wyprzedanie w konsolidacji przy VWAP",
            zrodlo="Larry Connors & Linda Raschke — Street Smarts",
            neurony_wejscie=["X-02", "V-02"],   # StochRSI ekstremum + VWAP poziom
            neurony_filtr=["XII-01", "X-25"],   # ADX niski (brak trendu) + ATR-dev
            neurony_wyjscie=["X-02", "V-02"],   # StochRSI powrót + VWAP środek
            interwaly=["M15", "1H"], rezim_preferowany="RANGING",
            dzwignia="2×–5×", rr="1:1.5", status="SZKIC",
        ),
        Strategia(
            id="IMV-SC-002", nazwa="WSCHÓD SŁOŃCA", legion="IMV", styl="SC",
            warunki="Breakout na otwarciu sesji azjatyckiej/londyńskiej przy VWAP",
            zrodlo="IMV (syntetyczna) — dawn breakout",
            neurony_wejscie=["V-02", "X-05"],   # VWAP kierunek + EMA Cross impuls
            neurony_filtr=["X-11", "X-04"],     # RVOL potwierdza ruch + BB kierunek
            neurony_wyjscie=["X-25", "V-02"],   # ATR-Z ekstremum / VWAP opór
            interwaly=["M5", "M15"], rezim_preferowany="TREND_STRONG",
            dzwignia="5×–10×", rr="1:2", status="SZKIC",
        ),
        Strategia(
            id="IMV-RG-002", nazwa="RYTM LIVERMORE'A", legion="IMV", styl="RG",
            warunki="Kanał Donchiana jako zakres — handel w granicach, pivot points",
            zrodlo="Jesse Livermore — Reminiscences of a Stock Operator",
            neurony_wejscie=["X-18", "X-01"],   # Donchian granice + RSI poziom
            neurony_filtr=["V-02", "X-25"],     # VWAP jako środek + ATR-dev spokojny
            neurony_wyjscie=["X-18", "X-03"],   # Donchian druga strona / MACD zmiana
            interwaly=["1H", "4H"], rezim_preferowany="RANGING",
            dzwignia="1×–3×", rr="1:2", status="SZKIC",
        ),
        # ── Dywizja Straży: kontra na manipulację (aktywowane 2026-06-02) ─────
        Strategia(
            id="IMV-DEF-001", nazwa="TARCZA PRETORIANÓW (Wash Trading Detection)", legion="IMV", styl="RV",
            warunki="Kontra na stop hunt / wick rejection — gramy PRZECIW pułapce MM (VOLATILE)",
            zrodlo="IMV (syntetyczna) — anty-manipulacja",
            neurony_wejscie=["A-01", "A-02"],   # Stop Hunt + Wick Rejection (kontrariański)
            neurony_filtr=["X-02", "V-02"],     # StochRSI ekstremum + VWAP poziom
            neurony_wyjscie=["A-01", "X-25"],   # sweep zanika / ATR-dev normalizuje
            interwaly=["M15", "1H"], rezim_preferowany="VOLATILE",
            dzwignia="2×–5×", rr="1:2", status="SZKIC",
        ),
        Strategia(
            id="IMV-DEF-002", nazwa="MUR KONTRWYWIADU (Iceberg Order Detector)", legion="IMV", styl="RV",
            warunki="Pranie wolumenu + wzorzec Barta — kontra na fałszywą aktywność MM (VOLATILE/niska płynność)",
            zrodlo="IMV (syntetyczna) — anty-manipulacja vol+płynność",
            neurony_wejscie=["A-03", "A-05"],   # Wash Volume + Bart Pattern (kontrariański)
            neurony_filtr=["X-11", "V-02"],     # RVOL (anomalia wolumenu) + VWAP poziom
            neurony_wyjscie=["A-05", "X-25"],   # Bart wraca do normy / ATR-dev normalizuje
            interwaly=["M15", "1H"], rezim_preferowany="VOLATILE",
            dzwignia="2×–4×", rr="1:2", status="SZKIC",
        ),
        # ── Legio VI Ferrata: Futures/Leverage (Faza B — kat. R obudzona) ────
        Strategia(
            id="VI-LV-001", nazwa="ŻELAZNY KLIN (Funding Rate Contrarian)", legion="VI", styl="LV",
            warunki="Ekstremalny funding = tłum po jednej stronie — gramy contrarian na squeeze (futures)",
            zrodlo="VI Ferrata — funding/sentyment futures (Binance fapi publiczne)",
            neurony_wejscie=["PSY-01", "PSY-02"],  # Funding extreme + Long/Short ekstremum
            neurony_filtr=["VI-13", "V-13"],       # ATR-Lev (bezpieczna dźwignia) + Realized Vol
            neurony_wyjscie=["PSY-01", "X-25"],    # funding normalizuje / ATR-dev wraca do normy
            interwaly=["1H", "4H"], rezim_preferowany="VOLATILE",
            dzwignia="2×–5×", rr="1:2", status="SZKIC",
        ),
        Strategia(
            id="VI-LV-002", nazwa="KASKADA STALOWA (Liquidation Cascade Hunt)", legion="VI", styl="LV",
            warunki="Stop hunt + dywergencja OI = kaskada likwidacji — łapiemy odbicie po zmiataniu (futures)",
            zrodlo="VI Ferrata — liquidation hunt (OI + struktura)",
            neurony_wejscie=["A-01", "PSY-04"],    # Stop Hunt + OI Divergence (kaskada)
            neurony_filtr=["VI-13", "V-13"],       # ATR-Lev + Realized Vol (kontrola ryzyka)
            neurony_wyjscie=["A-01", "VI-13"],     # sweep zanika / ATR-Lev sygnalizuje spokój
            interwaly=["M15", "1H"], rezim_preferowany="VOLATILE",
            dzwignia="2×–4×", rr="1:3", status="SZKIC",
        ),
    ]


def klucze_uzyte_w_strategiach() -> set:
    """Wszystkie klucze neuronów użyte w rejestrze strategii (do audytu Klucznika)."""
    klucze = set()
    for s in wszystkie_strategie():
        klucze |= s.wszystkie_klucze()
    return klucze
