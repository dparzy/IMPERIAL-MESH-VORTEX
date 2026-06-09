"""
🚨 IMV-INS | Neurony Zagrożenia — kategoria Z (Zagrożenie / Threat).

Kategoria Z to tarcza przed manipulacją rynkową. Dwa neurony:

Z-01 NeuronToxicFlow (meta-brama obronna):
  Mierzy TOKSYCZNOŚĆ PRZEPŁYWU (VPIN) — czy wieloryby handlują przeciwko tłumowi.
  Tłumi rój przez pewnosc_przeciwnika. Nigdy kierunkowy.

Z-02 NeuronPumpDetect (kierunkowy, LONG):
  Wykrywa AKUMULACJĘ PRZED PUMPEM — ciche gromadzenie pozycji przez smart money
  przy podniesionym wolumenie i zawężonym zakresie cenowym.
  Daje sygnał LONG: „ktoś zbiera" → cena pójdzie w górę.
  Źródło: arXiv 2504.15790 (2025) — akumulacja koncentruje się w ostatniej
  godzinie przed pumpem, >99% accuracy na krypto.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronToxicFlow(MikroNeuron):
    """
    Z-01 | VPIN ToxicFlow — radar toksycznego przepływu (meta-brama obronna).

    Dla nowicjusza: VPIN (Volume-Synchronized Probability of Informed Trading —
    wolumenowo-synchronizowane prawdopodobieństwo handlu poinformowanego) mierzy
    „toksyczność" przepływu zleceń: czy duzi, poinformowani gracze (wieloryby,
    market makerzy) handlują przeciwko tłumowi. Liczony metodą BVC (Bulk Volume
    Classification — masowa klasyfikacja wolumenu): z czystych zmian ceny szacujemy,
    jaka część wolumenu była „kupnem", a jaka „sprzedażą", i sumujemy ich nierównowagę.

    Z-01 to META-BRAMA OBRONNA — NIE wybiera LONG/SHORT, tylko sygnalizuje POZIOM
    ZAGROŻENIA i tłumi cały rój przez pewnosc_przeciwnika:
      VPIN < 0.3  → SPOKÓJ: przepływ nietoksyczny, NEUTRAL, pewnosc_przeciwnika 0.0.
      0.3–0.7     → CZUJNOŚĆ: przepływ częściowo toksyczny, NEUTRAL ze skromnym
                    pewnosc_przeciwnika skalowanym VPIN-em (lekkie tłumienie).
      VPIN > 0.7  → 🚨 CZERWONY ALARM: TOKSYCZNY PRZEPŁYW, ryzyko kaskady likwidacji
                    → NEUTRAL z WYSOKIM pewnosc_przeciwnika (silne tłumienie roju:
                    „nie wchodź / schodź z lewara"). To jego NAJWAŻNIEJSZA rola.

    Dlaczego ORTOGONALNY (Prawo XVI): VPIN mierzy KTO handluje (struktura przepływu),
    nie GDZIE idzie cena. To inna oś niż Momentum/Trend/Zmienność i komplementarna do
    kategorii A (anty-manipulacja): A wykrywa ŚLAD konkretnej zagrywki (stop hunt,
    wash vol) w jednej świecy, Z mierzy AGREGAT toksyczności przepływu w oknie —
    krzyżowe potwierdzenie zagrożenia z dwóch niezależnych perspektyw.

    Metoda: VPIN z Bramy (`VPIN_50`, BVC, n_buckets=50, proxy barowy), wynik ∈ [0,1].
    Źródło: Easley, López de Prado, O'Hara (2012), „Flow Toxicity and Liquidity in a
            High-Frequency World", Review of Financial Studies 25(5):1457,
            https://doi.org/10.1093/rfs/hhs053
    """
    KLUCZ = "Z-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "VPIN_50"
    KATEGORIA = "Z"
    WAGA = 8
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _VPIN_SPOKOJ = 0.3    # VPIN < _VPIN_SPOKOJ → spokój, przepływ nietoksyczny
    _VPIN_ALARM = 0.7     # VPIN > _VPIN_ALARM → czerwony alarm, toksyczny przepływ

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        v = wskazniki.get("VPIN_50")
        if v is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak VPIN_50"])

        if v < self._VPIN_SPOKOJ:
            return self._bazowy_sygnal(v, "NEUTRAL", 0.0,
                [f"VPIN={v:.3f} < {self._VPIN_SPOKOJ} — spokój, przepływ nietoksyczny"])

        if v > self._VPIN_ALARM:
            # Czerwony alarm — silne tłumienie roju przez pewnosc_przeciwnika
            przeciwnik = min(0.95, 0.6 + (v - self._VPIN_ALARM) * 1.5)
            s = self._bazowy_sygnal(v, "NEUTRAL", 0.0,
                [f"VPIN={v:.3f} > {self._VPIN_ALARM} — 🚨 TOKSYCZNY PRZEPŁYW, "
                 f"ryzyko kaskady likwidacji — nie wchodź / schodź z lewara"])
            s.pewnosc_przeciwnika = round(przeciwnik, 4)
            s.policz_finalna()
            return s

        # Czujność — skromne tłumienie skalowane VPIN-em
        przeciwnik = round(v * 0.5, 4)
        s = self._bazowy_sygnal(v, "NEUTRAL", 0.0,
            [f"VPIN={v:.3f} — czujność, przepływ częściowo toksyczny"])
        s.pewnosc_przeciwnika = przeciwnik
        s.policz_finalna()
        return s


class NeuronPumpDetect(MikroNeuron):
    """
    Z-02 | Pump Detect — wykrywanie cichej akumulacji przed pumpem (W-042).

    Dla nowicjusza: przed każdym dużym ruchem w górę (pumpem) smart money cicho
    zbiera pozycję. Zdradza ich połączenie trzech sygnałów:
      1. WOLUMEN PONAD NORMĘ — kupują więcej niż zwykle, ale nie panicznie
      2. WĄSKI ZAKRES ŚWIECY — cena stoi w miejscu mimo dużego wolumenu (ukrywają)
      3. OBV ROŚNIE — On-Balance Volume biegnie w górę, choć cena stoi (netto: kupno)

    Gdy wszystkie trzy naraz → „ktoś zbiera" → spodziewamy się ruchu w górę → LONG.

    Dlaczego ORTOGONALNY (Prawo XVI):
      - Z-01 VPIN mierzy TOKSYCZNOŚĆ (kto gra przeciw tłumowi — ochrona)
      - Z-02 PumpDetect mierzy AKUMULACJĘ (kto zbiera przed ruchem — okazja)
      - Dwie różne perspektywy manipulacji: obrona (Z-01) + ofensywa (Z-02)

    Algorytm (pure OHLCV, bez API):
      Vol_spike   = VOLUME / VOLUME_MA20 ∈ [1.5, 4.0] — ponad normę, ale nie panika
      Zakres_ok   = (HIGH - LOW) < zakres_prog × ATR_14  — świeca wąska (cicha akum.)
      OBV_rosnace = OBV > OBV_EMA_20 × (1 + obv_prog)   — net buying pressure
      Wynik       = Vol_spike × zakres_prog_score × obv_score

    Kierunek zawsze LONG (akumulacja = przygotowanie do ruchu w górę).
    Pewność ∈ [0.55, 0.85] skalowana stopniem spełnienia trzech warunków.

    Źródło: arXiv 2504.15790 (2025) — "Microstructure patterns before crypto pumps:
             accumulation concentrates in the last hour before the event" (>99% accuracy).
             ⚠️ niezweryfikowane peer-review (preprint 2025), wyniki wstępne.
    """
    KLUCZ = "Z-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "OBV"
    KATEGORIA = "Z"
    WAGA = 7
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    _VOL_MIN  = 1.5    # wolumen co najmniej 1.5× MA20 (zaczyna się akumulacja)
    _VOL_MAX  = 4.0    # wolumen < 4× MA20 (powyżej = panika, nie akumulacja)
    _ZAKRES   = 0.75   # świeca musi być krótsza niż ta frakcja ATR (wąski zakres)
    _OBV_PROG = 0.005  # OBV musi być > OBV_EMA_20 × (1 + 0.5%) — trend OBV w górę

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        vol    = wskazniki.get("VOLUME")
        vol_ma = wskazniki.get("VOLUME_MA20")
        high   = wskazniki.get("HIGH")
        low    = wskazniki.get("LOW")
        atr    = wskazniki.get("ATR_14")
        obv    = wskazniki.get("OBV")
        obv_e  = wskazniki.get("OBV_EMA_20")

        if None in (vol, vol_ma, high, low, atr, obv, obv_e):
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak danych PumpDetect (wymaga VOL/ATR/OBV)"])
        if vol_ma < 1 or atr < 1e-9:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["vol_ma/ATR bliskie zeru"])

        # 1. Wolumen: ponad normę, ale nie panika
        spike = vol / vol_ma
        if spike < self._VOL_MIN or spike > self._VOL_MAX:
            return self._bazowy_sygnal(spike, "NEUTRAL", 0.05,
                [f"Vol spike={spike:.2f}× — poza oknem akumulacji "
                 f"[{self._VOL_MIN}×–{self._VOL_MAX}×]"])

        # 2. Zakres świecy: wąski mimo wolumenu (ukrywają ruch)
        zakres = (high - low) / atr
        if zakres >= self._ZAKRES:
            return self._bazowy_sygnal(spike, "NEUTRAL", 0.05,
                [f"Zakres={zakres:.2f}× ATR ≥ {self._ZAKRES} — ruch zbyt duży, "
                 f"to nie cicha akumulacja"])

        # 3. OBV rośnie (net buying pressure): OBV > OBV_EMA × (1 + prog)
        obv_prog_abs = abs(obv_e) * self._OBV_PROG if obv_e != 0 else 1.0
        obv_rosnace = obv > obv_e + obv_prog_abs
        if not obv_rosnace:
            return self._bazowy_sygnal(spike, "NEUTRAL", 0.10,
                [f"OBV={obv:.0f} ≤ OBV_EMA={obv_e:.0f} — brak presji kupna"])

        # ── Wszystkie 3 warunki spełnione → sygnał AKUMULACJI ──
        # Pewność skalowana siłą każdego komponentu
        vol_score  = min(1.0, (spike - self._VOL_MIN) / (self._VOL_MAX - self._VOL_MIN))
        zakr_score = 1.0 - zakres / self._ZAKRES   # mniejszy zakres = silniejszy sygnał
        obv_score  = min(1.0, (obv - obv_e) / max(abs(obv_e) * 0.05, 1.0))
        sila = 0.55 + 0.30 * (vol_score * 0.4 + zakr_score * 0.3 + obv_score * 0.3)
        sila = round(min(0.85, sila), 4)

        return self._bazowy_sygnal(spike, "LONG", sila,
            [f"🚀 AKUMULACJA WYKRYTA: vol×{spike:.2f} MA, zakres {zakres:.2f}× ATR, "
             f"OBV>{obv_e:.0f} — smart money zbiera pozycję → LONG ({sila:.0%})"])


class NeuronBubbleCrash(MikroNeuron):
    """
    Z-03 | Bubble/Crash Kill-Switch — defensywna meta-brama (W-278, BIB-020 Harris rozdz. 28).

    Dla nowicjusza: to bezpiecznik przed dwoma najgroźniejszymi dla kapitału stanami
    rynku — PĘKAJĄCĄ BAŃKĄ i KRACHEM KASKADOWYM. Łączy trzy niezależne sygnały
    liczone z samego OHLCV (Prawo XV — żadnych nowych danych nie trzeba):

      1. BUBBLE_Z — odchylenie ceny od EMA-200 w jednostkach σ. Bańka = cena
         oderwana od długoterminowej grawitacji (granice Fischera Blacka).
      2. VoV (Volatility-of-Volatility) — czy sama zmienność jest niestabilna.
         Przed krachem ATR skacze z baru na bar (rozpad konsensusu cenowego).
      3. AR1 — autokorelacja zwrotów lag-1. Dodatnia = refleksywność: ceny napędzają
         same siebie (kaskada momentum / margin calls), klasyczna dynamika krachu/paraboli.

    Z-03 to META-BRAMA OBRONNA (jak Z-01) — NIGDY nie wybiera LONG/SHORT. Tłumi cały rój
    przez pewnosc_przeciwnika, skalowany siłą najgroźniejszego z trzech sygnałów:
      • Próg ALARM (bubble_z>3.5 LUB VoV>1.2 LUB AR1>0.40) → 🚨 KILL-SWITCH:
        maksymalne tłumienie (pewnosc_przeciwnika do 0.97) — „nie wchodź, schodź z ryzyka".
      • Strefa CZUJNOŚCI (bubble_z>2.5 / VoV>0.8 / AR1>0.25) → umiarkowane tłumienie.
      • Poniżej → spokój, NEUTRAL bez tłumienia.

    Dlaczego ORTOGONALNY (Prawo XVI): Z-01 mierzy toksyczność przepływu (KTO handluje),
    Z-03 mierzy NIESTABILNOŚĆ STRUKTURY CENY (bańka/krach). Inna oś zagrożenia.
    ⚠️ Nakładka do zmierzenia: AR1 vs HURST_DFA (H-01) i VoV vs Yang-Zhang — różne okna
    i konstrukcja, ale warto sprawdzić |r| przed podniesieniem wagi (Prawo XVI).

    Źródło: Harris, "Trading and Exchanges: Market Microstructure for Practitioners"
            (Oxford 2003), rozdz. 28 "Bubbles, Crashes, and Circuit Breakers".
            Wizja W-278 (docs/WIZJONER.md, BIB-020).
    """
    KLUCZ = "Z-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BUBBLE_Z_200"
    KATEGORIA = "Z"
    WAGA = 9
    ELITARNY = False
    POWOD_ELITARNOSCI = ""

    # Progi ALARM (kill-switch) — dowolny przekroczony → maksymalne tłumienie
    _BUBBLE_ALARM = 3.5
    _VOV_ALARM    = 1.2
    _AR1_ALARM    = 0.40
    # Progi CZUJNOŚĆ — umiarkowane tłumienie skalowane
    _BUBBLE_CZUJ  = 2.5
    _VOV_CZUJ     = 0.8
    _AR1_CZUJ     = 0.25

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        bz  = wskazniki.get("BUBBLE_Z_200")
        vov = wskazniki.get("VOV_20")
        ar1 = wskazniki.get("RET_AR1_20")

        if bz is None and vov is None and ar1 is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak danych Bubble/Crash (wymaga BUBBLE_Z/VoV/AR1 — za mało barów)"])

        abz = abs(bz) if bz is not None else 0.0
        vovv = vov if vov is not None else 0.0
        aar1 = ar1 if ar1 is not None else 0.0

        # ── Próg ALARM — dowolny sygnał skrajny → KILL-SWITCH ──
        alarmy = []
        if abz >= self._BUBBLE_ALARM:
            alarmy.append(f"bubble_z={bz:+.2f} (|{abz:.2f}|≥{self._BUBBLE_ALARM})")
        if vovv >= self._VOV_ALARM:
            alarmy.append(f"VoV={vovv:.2f}≥{self._VOV_ALARM}")
        if aar1 >= self._AR1_ALARM:
            alarmy.append(f"AR1={aar1:+.2f}≥{self._AR1_ALARM}")

        if alarmy:
            # Tłumienie skaluje się ponad próg, ale nie spada poniżej 0.85 przy alarmie
            nadwyzka = max(
                (abz - self._BUBBLE_ALARM) / self._BUBBLE_ALARM if abz >= self._BUBBLE_ALARM else 0.0,
                (vovv - self._VOV_ALARM) / self._VOV_ALARM if vovv >= self._VOV_ALARM else 0.0,
                (aar1 - self._AR1_ALARM) / self._AR1_ALARM if aar1 >= self._AR1_ALARM else 0.0,
            )
            przeciwnik = round(min(0.97, 0.85 + nadwyzka * 0.5), 4)
            s = self._bazowy_sygnal(bz, "NEUTRAL", 0.0,
                [f"🚨 BUBBLE/CRASH KILL-SWITCH: {', '.join(alarmy)} — "
                 f"niestabilność struktury ceny, HALT/schodź z ryzyka"])
            s.pewnosc_przeciwnika = przeciwnik
            s.policz_finalna()
            return s

        # ── Strefa CZUJNOŚCI — umiarkowane tłumienie skalowane ──
        czuj_score = max(
            (abz - self._BUBBLE_CZUJ) / (self._BUBBLE_ALARM - self._BUBBLE_CZUJ) if abz > self._BUBBLE_CZUJ else 0.0,
            (vovv - self._VOV_CZUJ) / (self._VOV_ALARM - self._VOV_CZUJ) if vovv > self._VOV_CZUJ else 0.0,
            (aar1 - self._AR1_CZUJ) / (self._AR1_ALARM - self._AR1_CZUJ) if aar1 > self._AR1_CZUJ else 0.0,
        )
        if czuj_score > 0.0:
            przeciwnik = round(min(0.6, czuj_score * 0.6), 4)
            s = self._bazowy_sygnal(bz, "NEUTRAL", 0.0,
                [f"⚠️ Czujność: bubble_z={bz if bz is not None else 0:+.2f}, "
                 f"VoV={vovv:.2f}, AR1={aar1:+.2f} — rosnąca niestabilność struktury"])
            s.pewnosc_przeciwnika = przeciwnik
            s.policz_finalna()
            return s

        # ── Spokój ──
        return self._bazowy_sygnal(bz, "NEUTRAL", 0.0,
            [f"Struktura stabilna: bubble_z={bz if bz is not None else 0:+.2f}, "
             f"VoV={vovv:.2f}, AR1={aar1:+.2f}"])
