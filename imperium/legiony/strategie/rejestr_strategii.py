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
    ]


def klucze_uzyte_w_strategiach() -> set:
    """Wszystkie klucze neuronów użyte w rejestrze strategii (do audytu Klucznika)."""
    klucze = set()
    for s in wszystkie_strategie():
        klucze |= s.wszystkie_klucze()
    return klucze
