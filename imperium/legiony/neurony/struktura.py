"""
⚔️ IMV-INS | Neurony Struktury Rynku — SMC/ICT/VSA
Order Blocks, Fair Value Gaps, Break of Structure, Market Structure Shift.
Analiza instytucjonalnych śladów w cenach.

ARCHITEKTURA SMC:
  SMC-01..03 to WARSTWY INTERPRETACJI — interpretują z gotowych stref.
  Strefy (OB/FVG/BOS) muszą być wykryte przez Exploratores (wymaga serii barów).
  EXP-05 ZwiadowcaSMC oblicza strefy → wstrzykuje je do wskazniki dict →
  SMC-01..03 interpretują. EXP-05 jest aktywny → SMC-01..03 AKTYWNE (2026-06-09).

  VSA-01 działa z bieżącego baru (HIGH/LOW/CLOSE/VOL) — dostępny od razu.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu

_POWOD_SMC = ""  # EXP-05 aktywny → SMC-01..03 dostępne (2026-06-09, Prawo XV)


class NeuronOrderBlock(MikroNeuron):
    """
    SMC-01 | Order Block — strefa koncentracji instytucjonalnych zleceń.
    Bullish OB: ostatni czerwony świecznik przed silnym wzrostem.
    Bearish OB: ostatni zielony świecznik przed silnym spadkiem.
    Cena powracająca do OB = reakcja.
    """
    KLUCZ = "SMC-01"
    LEGION = "SWING"
    WSKAZNIK = "ORDER_BLOCK"
    KATEGORIA = "S"
    WAGA = 8
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        bull_ob_high = wskazniki.get("BULL_OB_HIGH")
        bull_ob_low = wskazniki.get("BULL_OB_LOW")
        bear_ob_high = wskazniki.get("BEAR_OB_HIGH")
        bear_ob_low = wskazniki.get("BEAR_OB_LOW")

        if close is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych OB"])

        # Cena w strefie Bullish Order Block
        if bull_ob_high is not None and bull_ob_low is not None:
            if bull_ob_low <= close <= bull_ob_high:
                return self._bazowy_sygnal(close, "LONG", 0.85,
                    [f"Cena {close:.2f} w Bullish OB [{bull_ob_low:.2f}-{bull_ob_high:.2f}] — reakcja instytucji"])

        # Cena w strefie Bearish Order Block
        if bear_ob_high is not None and bear_ob_low is not None:
            if bear_ob_low <= close <= bear_ob_high:
                return self._bazowy_sygnal(close, "SHORT", 0.85,
                    [f"Cena {close:.2f} w Bearish OB [{bear_ob_low:.2f}-{bear_ob_high:.2f}] — strefa dystrybucji"])

        return self._bazowy_sygnal(close, "NEUTRAL", 0.10, ["Cena poza strefami OB"])


class NeuronFVG(MikroNeuron):
    """
    SMC-02 | Fair Value Gap (FVG / Imbalance) — luka cenowa w struktyrze.
    Rynek zawsze wypełnia FVG. Bullish FVG = wsparcie (LONG).
    Bearish FVG = opór (SHORT).
    """
    KLUCZ = "SMC-02"
    LEGION = "SCALP"
    WSKAZNIK = "FVG"
    KATEGORIA = "S"
    WAGA = 7
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        bull_fvg_high = wskazniki.get("BULL_FVG_HIGH")
        bull_fvg_low = wskazniki.get("BULL_FVG_LOW")
        bear_fvg_high = wskazniki.get("BEAR_FVG_HIGH")
        bear_fvg_low = wskazniki.get("BEAR_FVG_LOW")

        if close is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych FVG"])

        if bull_fvg_high is not None and bull_fvg_low is not None:
            if bull_fvg_low <= close <= bull_fvg_high:
                return self._bazowy_sygnal(close, "LONG", 0.80,
                    [f"Cena {close:.2f} w Bullish FVG [{bull_fvg_low:.2f}-{bull_fvg_high:.2f}] — wypełnianie luki"])

        if bear_fvg_high is not None and bear_fvg_low is not None:
            if bear_fvg_low <= close <= bear_fvg_high:
                return self._bazowy_sygnal(close, "SHORT", 0.80,
                    [f"Cena {close:.2f} w Bearish FVG [{bear_fvg_low:.2f}-{bear_fvg_high:.2f}] — opór luki"])

        return self._bazowy_sygnal(close, "NEUTRAL", 0.10, ["Cena poza FVG"])


class NeuronBOS(MikroNeuron):
    """
    SMC-03 | Break of Structure (BOS) + Market Structure Shift (MSS).
    BOS: rynek kontynuuje trend — przebicie poprzedniego LL/HH.
    MSS: rynek odwraca strukturę — zmiana charakteru (Change of Character).
    """
    KLUCZ = "SMC-03"
    LEGION = "SWING"
    WSKAZNIK = "BOS_MSS"
    KATEGORIA = "S"
    WAGA = 9
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        bos_bull = wskazniki.get("BOS_BULLISH")        # bool: ostatni bar przebił HH
        bos_bear = wskazniki.get("BOS_BEARISH")        # bool: ostatni bar przebił LL
        mss_bull = wskazniki.get("MSS_BULLISH")        # bool: zmiana struktury na bullish
        mss_bear = wskazniki.get("MSS_BEARISH")        # bool: zmiana struktury na bearish
        close = wskazniki.get("CLOSE")

        if close is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych BOS"])

        # MSS > BOS (silniejszy sygnał)
        if mss_bull:
            return self._bazowy_sygnal(close, "LONG", 0.90,
                ["MSS BULLISH: zmiana struktury na wzrostową — instytucje akumulują"])
        if mss_bear:
            return self._bazowy_sygnal(close, "SHORT", 0.90,
                ["MSS BEARISH: zmiana struktury na spadkową — instytucje dystrybuują"])
        if bos_bull:
            return self._bazowy_sygnal(close, "LONG", 0.75,
                ["BOS BULLISH: przebicie Higher High — kontynuacja wzrostów"])
        if bos_bear:
            return self._bazowy_sygnal(close, "SHORT", 0.75,
                ["BOS BEARISH: przebicie Lower Low — kontynuacja spadków"])
        return self._bazowy_sygnal(close, "NEUTRAL", 0.15,
            ["Brak aktywnego BOS/MSS — konsolidacja"])


class NeuronVSA(MikroNeuron):
    """
    VSA-01 | Volume Spread Analysis — analiza spread/wolumen/close.
    Wygaszający wolumen + zawężony spread + cena blisko góry świecy = siła.
    Ultra-high volume + węski spread = stop volume (zawrócenie).
    """
    KLUCZ = "VSA-01"
    LEGION = "SWING"
    WSKAZNIK = "VSA"
    KATEGORIA = "F"
    WAGA = 8

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        high = wskazniki.get("HIGH")
        low = wskazniki.get("LOW")
        close = wskazniki.get("CLOSE")
        vol = wskazniki.get("VOLUME")
        vol_ma20 = wskazniki.get("VOLUME_MA20")

        if None in (high, low, close, vol, vol_ma20) or vol_ma20 == 0:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych VSA"])

        spread = high - low
        close_poz = (close - low) / spread if spread > 0 else 0.5  # 0=dół, 1=góra świecy
        vol_ratio = vol / vol_ma20

        # Stop Volume: ultra-high vol + wąski spread → zatrzymanie ruchu
        if vol_ratio > 3.0 and spread < (spread * 0.5):  # wąski relative
            if close_poz > 0.5:
                return self._bazowy_sygnal(vol_ratio, "LONG", 0.75,
                    [f"VSA STOP VOLUME BULL: {vol_ratio:.1f}× vol, close wysoko — zatrzymanie sprzedaży"])
            return self._bazowy_sygnal(vol_ratio, "SHORT", 0.75,
                [f"VSA STOP VOLUME BEAR: {vol_ratio:.1f}× vol, close nisko — zatrzymanie kupna"])

        # Siła (wysiłek vs wynik)
        if vol_ratio > 1.5 and close_poz > 0.70:
            return self._bazowy_sygnal(vol_ratio, "LONG", 0.65,
                [f"VSA SIŁA: {vol_ratio:.1f}× vol, zamknięcie w górnej ćwiartce"])
        if vol_ratio > 1.5 and close_poz < 0.30:
            return self._bazowy_sygnal(vol_ratio, "SHORT", 0.65,
                [f"VSA SŁABOŚĆ: {vol_ratio:.1f}× vol, zamknięcie w dolnej ćwiartce"])

        # Brak wysiłku
        if vol_ratio < 0.5:
            return self._bazowy_sygnal(vol_ratio, "NEUTRAL", 0.20,
                [f"VSA: niski wolumen ({vol_ratio:.1f}×) — brak przekonania"])

        return self._bazowy_sygnal(vol_ratio, "NEUTRAL", 0.15, [f"VSA normalny ({vol_ratio:.1f}×)"])
