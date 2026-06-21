"""
⚔️ IMV-INS | Neurony On-Chain — Dywizja Wieszczowie
MVRV-Z, SOPR, Puell Multiple, NVT, Exchange Netflow + Wash Trading Detection.
Dane fundamentalne on-chain — cykle makro.

UWAGA: OC-01..OC-04 wymagają zewnętrznego API on-chain (Glassnode/CryptoQuant).
Brama Kalkulatora NIE dostarcza tych danych — neurony są wyciszone (DOSTEPNY=False)
do czasu podpięcia adapterów API. Logika interpretacji jest gotowa i poprawna.

OC-05 (NeuronWashTrading) działa na czystym OHLCV — dostępny od razu (DOSTEPNY=True).
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu

_POWOD = "Wymaga on-chain API (Glassnode/CryptoQuant). Podepnij adapter w pobierz_wskazniki()."


class NeuronMVRV(MikroNeuron):
    """
    OC-01 | MVRV-Z Score — Market Value vs Realized Value.
    Z-Score < -0.5 = historyczne dno (kapituacja), > 6 = szczyt bańki.
    """
    KLUCZ = "OC-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "MVRV_Z"
    KATEGORIA = "O"
    WAGA = 9
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        mvrv_z = wskazniki.get("MVRV_Z_SCORE")
        if mvrv_z is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak MVRV-Z"])

        if mvrv_z <= -0.5:
            return self._bazowy_sygnal(mvrv_z, "LONG", 0.95,
                [f"MVRV-Z={mvrv_z:.2f} — historyczna KAPITUACJA, ekstremalnie tanie"])
        if mvrv_z <= 1.0:
            return self._bazowy_sygnal(mvrv_z, "LONG", 0.70,
                [f"MVRV-Z={mvrv_z:.2f} — poniżej realizowanej wartości, okazja"])
        if mvrv_z <= 3.5:
            return self._bazowy_sygnal(mvrv_z, "LONG", 0.45,
                [f"MVRV-Z={mvrv_z:.2f} — fair value, neutralny bias bull"])
        if mvrv_z <= 6.0:
            return self._bazowy_sygnal(mvrv_z, "SHORT", 0.70,
                [f"MVRV-Z={mvrv_z:.2f} — przewartościowanie, podwyższone ryzyko"])
        return self._bazowy_sygnal(mvrv_z, "SHORT", 0.95,
            [f"MVRV-Z={mvrv_z:.2f} — SZCZYT BAŃKI historycznie — SHORT/SELL"])


class NeuronSOPR(MikroNeuron):
    """
    OC-02 | SOPR (Spent Output Profit Ratio) — czy holderzy sprzedają z zyskiem.
    SOPR < 1 = sprzedaż ze stratą (kapituacja) → dno.
    SOPR > 1.05 + spada = dystrybucja → szczyt.
    """
    KLUCZ = "OC-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "SOPR"
    KATEGORIA = "O"
    WAGA = 8
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        sopr = wskazniki.get("SOPR")
        sopr_prev = wskazniki.get("SOPR_PREV")
        if sopr is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak SOPR"])

        sopr_spada = sopr_prev is not None and sopr < sopr_prev

        if sopr < 0.95:
            return self._bazowy_sygnal(sopr, "LONG", 0.85,
                [f"SOPR={sopr:.3f} < 1 — kapituacja, sprzedaż ze stratą → dno bliskie"])
        if sopr < 1.0:
            return self._bazowy_sygnal(sopr, "LONG", 0.60,
                [f"SOPR={sopr:.3f} lekko < 1 — słaba kapituacja"])
        if sopr > 1.05 and sopr_spada:
            return self._bazowy_sygnal(sopr, "SHORT", 0.75,
                [f"SOPR={sopr:.3f} > 1.05 i SPADA — dystrybucja, holderzy realizują zyski"])
        if sopr > 1.10:
            return self._bazowy_sygnal(sopr, "SHORT", 0.55,
                [f"SOPR={sopr:.3f} wysoki — duże zyski realizowane"])
        return self._bazowy_sygnal(sopr, "NEUTRAL", 0.20,
            [f"SOPR={sopr:.3f} neutralny"])


class NeuronPuellMultiple(MikroNeuron):
    """
    OC-03 | Puell Multiple — dzienne wydobycie BTC vs roczna średnia.
    Mierzy presję sprzedaży górników.
    <0.5 = ekstremalnie mało sprzedaży → dno. >4 = górnicy masowo sprzedają → szczyt.
    """
    KLUCZ = "OC-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "PUELL_MULTIPLE"
    KATEGORIA = "O"
    WAGA = 7
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        puell = wskazniki.get("PUELL_MULTIPLE")
        if puell is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Puell Multiple"])

        if puell <= 0.50:
            return self._bazowy_sygnal(puell, "LONG", 0.90,
                [f"Puell={puell:.2f} — górnicy pod presją, historyczne dno"])
        if puell <= 0.80:
            return self._bazowy_sygnal(puell, "LONG", 0.65,
                [f"Puell={puell:.2f} — niska presja sprzedaży górników"])
        if puell >= 4.0:
            return self._bazowy_sygnal(puell, "SHORT", 0.90,
                [f"Puell={puell:.2f} — MASOWA sprzedaż górników — szczyt bańki"])
        if puell >= 2.5:
            return self._bazowy_sygnal(puell, "SHORT", 0.65,
                [f"Puell={puell:.2f} — podwyższona sprzedaż górników"])
        return self._bazowy_sygnal(puell, "NEUTRAL", 0.20,
            [f"Puell={puell:.2f} — normalny zakres"])


class NeuronExchangeNetflow(MikroNeuron):
    """
    OC-04 | Exchange Netflow — przepływ BTC na/z giełd.
    Napływ na giełdy = presja sprzedaży. Odpływ = akumulacja (self-custody).
    """
    KLUCZ = "OC-04"
    LEGION = "WSPOLNY"
    WSKAZNIK = "EXCHANGE_NETFLOW"
    KATEGORIA = "O"
    WAGA = 8
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        netflow = wskazniki.get("EXCHANGE_NETFLOW_BTC")  # BTC: + = napływ, - = odpływ
        if netflow is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Exchange Netflow"])

        if netflow < -5000:
            return self._bazowy_sygnal(netflow, "LONG", 0.85,
                [f"Netflow={netflow:.0f} BTC — MASOWY ODPŁYW z giełd — akumulacja, cena ↑"])
        if netflow < 0:
            pewnosc = min(0.65, 0.45 + abs(netflow) / 10000 * 0.20)
            return self._bazowy_sygnal(netflow, "LONG", pewnosc,
                [f"Netflow={netflow:.0f} BTC — odpływ z giełd — bullish signal"])
        if netflow > 5000:
            return self._bazowy_sygnal(netflow, "SHORT", 0.80,
                [f"Netflow={netflow:.0f} BTC — MASOWY NAPŁYW na giełdy — presja sprzedaży"])
        if netflow > 0:
            pewnosc = min(0.60, 0.40 + netflow / 10000 * 0.20)
            return self._bazowy_sygnal(netflow, "SHORT", pewnosc,
                [f"Netflow={netflow:.0f} BTC — napływ na giełdy — bearish signal"])
        return self._bazowy_sygnal(netflow, "NEUTRAL", 0.10, ["Netflow neutralny"])


class NeuronWashTrading(MikroNeuron):
    """
    OC-05 | Wash Trading Detection — Benford + zaokrąglenia (W-061).

    Dla nowicjusza: Na nieregulowanych giełdach (MEXC, Binance w przeszłości)
    giełdy lub market makerzy sztucznie handlują sami ze sobą, żeby wyglądać
    na popularne. Fałszywy wolumen niszczy ALL nasze wskaźniki wolumenowe
    (VPIN, OBV, Flow). Ten neuron to „detektor kłamstwa" dla danych.

    Dwa testy statystyczne (czyste OHLCV, bez API):
      1. Prawo Benforda — w naturalnych danych pierwsza cyfra wolumenu
         jest silnie asymetryczna (1=30%, 2=18%...). Boty używają okrągłych
         liczb → chi² odstępstwo wykrywa to wzorzec.
      2. Klasterowanie zaokrągleń — legalne transakcje są losowe; boty
         preferują 100, 500, 1000 (round numbers). Frakcja zaokrąglonych > 40% → alarm.

    Zachowanie (meta-gate defensywna, jak VPIN/Entropy):
      WASH_SCORE < 0.35 → NEUTRAL (niska pewność, brak sygnału manipulacji)
      0.35–0.65 → ostrzeżenie: HIGH pewnosc_przeciwnika (tłumi rój globalnie)
      > 0.65    → silny sygnał wash: NEUTRAL + bardzo wysoka pewnosc_przeciwnika

    Nigdy nie głosuje kierunkowo (LONG/SHORT) — manipulacja nie mówi „dokąd",
    tylko „nie ufaj tym danym". Tłumi rój poprzez pewnosc_przeciwnika.

    Źródło: Cong, Li, Tang, Yang (2023), "Crypto Wash Trading", NBER w30783,
            https://www.nber.org/papers/w30783
    Weryfikacja: ✅ zweryfikowane peer-reviewed (NBER working paper, 2023)
    """
    KLUCZ = "OC-05"
    LEGION = "WSPOLNY"
    WSKAZNIK = "WASH_SCORE_100"
    KATEGORIA = "O"
    WAGA = 8
    ELITARNY = False

    _PROG_OSTRZEZENIE = 0.35   # powyżej → tłumienie roju
    _PROG_SILNY       = 0.65   # powyżej → silny alarm manipulacji

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        score = wskazniki.get("WASH_SCORE_100")
        if score is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak danych WashTrading (za mało barów wolumenu)"])

        if score < self._PROG_OSTRZEZENIE:
            return self._bazowy_sygnal(score, "NEUTRAL", 0.05,
                [f"Wolumen naturalny (Benford OK): score={score:.3f}"])

        if score < self._PROG_SILNY:
            # Ostrzeżenie: tłumimy rój, nie głosujemy kierunkowo
            pewnosc_p = round(min(0.70, 0.40 + (score - self._PROG_OSTRZEZENIE) * 1.0), 4)
            s = self._bazowy_sygnal(score, "NEUTRAL", 0.0,
                [f"⚠️ WASH SIGNAL (umiarkowany): score={score:.3f} — "
                 f"wolumen podejrzany (Benford + zaokrąglenia), tłumię rój"])
            s.pewnosc_przeciwnika = pewnosc_p
            s.policz_finalna()
            return s

        # Silny sygnał fałszywego wolumenu
        pewnosc_p = round(min(0.90, 0.70 + (score - self._PROG_SILNY) * 0.80), 4)
        s = self._bazowy_sygnal(score, "NEUTRAL", 0.0,
            [f"🚨 WASH TRADING ALARM: score={score:.3f} — "
             f"wolumen prawdopodobnie sfałszowany, NIE HANDLUJ na tych danych"])
        s.pewnosc_przeciwnika = pewnosc_p
        s.policz_finalna()
        return s


# ---------------------------------------------------------------------------
# OC-06 / OC-07 / OC-08 — deterministyczne neurony BTC on-chain
# Źródło: BIB-030 Ammous "The Bitcoin Standard" (INF-41)
# Nie wymagają zewnętrznego API — wyliczane z block height i harmonogramu halvingów.
# ---------------------------------------------------------------------------

# Harmonogram halvingów BTC (deterministyczny)
_HALVING_EPOCHS = [
    (0,       50.0),      # blok 0 — genesis
    (210_000, 25.0),      # 1. halving ~2012
    (420_000, 12.5),      # 2. halving ~2016
    (630_000, 6.25),      # 3. halving ~2020
    (840_000, 3.125),     # 4. halving ~2024
    (1_050_000, 1.5625),  # 5. halving ~2028
    (1_260_000, 0.78125), # 6. halving ~2032
]
_MAX_SUPPLY_BTC = 21_000_000.0
_BLOKI_NA_EPOKE = 210_000
_SREDNI_CZAS_BLOKU_MIN = 10.0

# Kotwice (block_height, unix_timestamp) — znane daty halvingów (dla interpolacji).
# Źródło: blockchain (deterministyczne). Pozwala oszacować block_height z timestampu
# baru BEZ sieci — działa też w backteście (Prawo XV: ożywia OC-06..08).
_KOTWICE_BLOKOW = [
    (0,       1_231_006_505),   # genesis 2009-01-03
    (210_000, 1_354_116_278),   # 1. halving 2012-11-28
    (420_000, 1_468_082_773),   # 2. halving 2016-07-09
    (630_000, 1_589_225_023),   # 3. halving 2020-05-11
    (840_000, 1_713_571_200),   # 4. halving 2024-04-20
]


def szacuj_block_height(timestamp: float) -> int:
    """
    Szacuje wysokość bloku BTC z unixowego timestampu (sekundy).
    Interpolacja liniowa między znanymi kotwicami halvingów; ekstrapolacja
    poza ostatnią kotwicą wg 10 min/blok. Deterministyczne, bez sieci.
    """
    ts = float(timestamp)
    # Normalizacja jednostki: system używa timestampów w MILISEKUNDACH (bary MEXC).
    # Kotwice są w sekundach. Jeśli ts wygląda na ms (>1e11) → konwersja na sekundy.
    if ts > 1e11:
        ts = ts / 1000.0
    kotwice = _KOTWICE_BLOKOW

    if ts <= kotwice[0][1]:
        return 0

    # interpolacja w obrębie znanych przedziałów
    for i in range(len(kotwice) - 1):
        b0, t0 = kotwice[i]
        b1, t1 = kotwice[i + 1]
        if t0 <= ts < t1:
            frac = (ts - t0) / (t1 - t0) if t1 > t0 else 0.0
            return int(b0 + frac * (b1 - b0))

    # ekstrapolacja po ostatniej kotwicy: 10 min/blok = 600 s
    b_last, t_last = kotwice[-1]
    return int(b_last + (ts - t_last) / (_SREDNI_CZAS_BLOKU_MIN * 60))


def _info_bloku(block_height: int) -> dict:
    """Wylicza nagrode, epokę, S2F i dni-do-halvingu z block_height."""
    # Aktualna nagroda
    nagroda = 50.0
    for prog, rew in _HALVING_EPOCHS:
        if block_height >= prog:
            nagroda = rew
        else:
            break

    # Następny próg halvingu
    nastepna_epoka_idx = (block_height // _BLOKI_NA_EPOKE) + 1
    nastepny_prog = nastepna_epoka_idx * _BLOKI_NA_EPOKE
    bloki_do = nastepny_prog - block_height
    dni_do = bloki_do * _SREDNI_CZAS_BLOKU_MIN / (60 * 24)

    # Szacowana aktualna podaż (trójkąt geometryczny)
    podaz = 0.0
    ep_rew = 50.0
    for i, (prog, rew) in enumerate(_HALVING_EPOCHS):
        nastepny = _HALVING_EPOCHS[i + 1][0] if i + 1 < len(_HALVING_EPOCHS) else block_height
        if block_height <= prog:
            break
        bloki_w_epoce = min(block_height, nastepny) - prog
        podaz += bloki_w_epoce * ep_rew
        ep_rew = rew

    # Roczna emisja = nagroda_blokowa * 6 bloków/h * 24h * 365
    roczna_emisja = nagroda * 6 * 24 * 365
    s2f = podaz / roczna_emisja if roczna_emisja > 0 else 0.0
    inflacja_pct = (roczna_emisja / podaz * 100) if podaz > 0 else 0.0

    return {
        "nagroda_blokowa": nagroda,
        "podaz_btc": round(podaz, 2),
        "roczna_emisja": round(roczna_emisja, 4),
        "s2f": round(s2f, 2),
        "inflacja_pct": round(inflacja_pct, 4),
        "dni_do_halvingu": round(dni_do, 1),
        "bloki_do_halvingu": bloki_do,
    }


_POWOD_BLOK = "Wymaga BTC_BLOCK_HEIGHT w wskaznikach (adapter blockchain lub REST BTC node)."


class NeuronS2F(MikroNeuron):
    """
    OC-06 | BTC Stock-to-Flow Ratio — twardość monetarna (W-377).
    S2F = podaż_całkowita / roczna_nowa_emisja.
    S2F > 50 (jak złoto) = historycznie bull phase (po halvingach).
    Dane: deterministyczne z block_height — zero zewnętrznych API poza numerem bloku.
    Źródło: BIB-030 Ammous, INF-41.
    """
    KLUCZ = "OC-06"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BTC_S2F"
    KATEGORIA = "O"
    WAGA = 6
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        block_height = wskazniki.get("BTC_BLOCK_HEIGHT")
        if not block_height:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak BTC_BLOCK_HEIGHT — neuron abstynuje (DOSTEPNY po wstrzyknięciu)"])

        info = _info_bloku(int(block_height))
        s2f = info["s2f"]

        if s2f >= 100:
            return self._bazowy_sygnal(s2f, "LONG", 0.75,
                [f"S2F={s2f:.0f} — po halvingu, BTC twardszy niż złoto (S2F złota≈55)",
                 f"Roczna inflacja podaży: {info['inflacja_pct']:.3f}%"])
        if s2f >= 50:
            return self._bazowy_sygnal(s2f, "LONG", 0.55,
                [f"S2F={s2f:.0f} — poziom złota (~55x), środek cyklu bull"])
        if s2f >= 25:
            return self._bazowy_sygnal(s2f, "NEUTRAL", 0.0,
                [f"S2F={s2f:.0f} — przed halvingiem, neutralny makro-kontekst"])
        return self._bazowy_sygnal(s2f, "NEUTRAL", 0.0,
            [f"S2F={s2f:.0f} — wczesna faza (niska twardość monetarna)"])


class NeuronDaysToHalving(MikroNeuron):
    """
    OC-07 | Dni do halvingu BTC — supply shock countdown (W-378).
    Rynek historycznie dyskontuje halving z wyprzedzeniem ~180 dni.
    Źródło: BIB-030 Ammous, INF-41. Deterministyczne z block_height.
    """
    KLUCZ = "OC-07"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BTC_DAYS_TO_HALVING"
    KATEGORIA = "O"
    WAGA = 7
    DOSTEPNY = True

    _PROG_BLISKI = 180    # dni — historyczne okno dyskontowania halvingu
    _PROG_BARDZO_BLISKI = 60

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        block_height = wskazniki.get("BTC_BLOCK_HEIGHT")
        if not block_height:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak BTC_BLOCK_HEIGHT"])

        info = _info_bloku(int(block_height))
        dni = info["dni_do_halvingu"]

        if dni <= self._PROG_BARDZO_BLISKI:
            return self._bazowy_sygnal(dni, "LONG", 0.80,
                [f"Halving za {dni:.0f} dni — SUPPLY SHOCK bliski",
                 f"Nagroda blokowa: {info['nagroda_blokowa']} BTC → po halvingu: {info['nagroda_blokowa']/2:.4f}"])
        if dni <= self._PROG_BLISKI:
            return self._bazowy_sygnal(dni, "LONG", 0.60,
                [f"Halving za {dni:.0f} dni — okno dyskontowania (historycznie bull)",
                 f"S2F po halvingu wzrośnie 2× (do {info['s2f']*2:.0f}x)"])
        return self._bazowy_sygnal(dni, "NEUTRAL", 0.0,
            [f"Halving za {dni:.0f} dni — poza oknem historycznego dyskontowania ({self._PROG_BLISKI} dni)"])


class NeuronBTCSupplyInflation(MikroNeuron):
    """
    OC-08 | BTC Supply Inflation Rate — tempo wzrostu podaży (W-379).
    Im niższa inflacja, tym twardszy pieniądz → fundamentalny bull factor.
    Deterministyczne: 0 zewnętrznych API poza numerem bloku.
    Źródło: BIB-030 Ammous, INF-41.
    """
    KLUCZ = "OC-08"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BTC_SUPPLY_INFLATION_PCT"
    KATEGORIA = "O"
    WAGA = 5
    DOSTEPNY = True

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        block_height = wskazniki.get("BTC_BLOCK_HEIGHT")
        if not block_height:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak BTC_BLOCK_HEIGHT"])

        info = _info_bloku(int(block_height))
        inf_pct = info["inflacja_pct"]

        if inf_pct <= 1.0:
            return self._bazowy_sygnal(inf_pct, "LONG", 0.60,
                [f"BTC inflacja={inf_pct:.3f}% < 1% rocznie — twardszy niż złoto (~1.7%)",
                 f"Nagroda blokowa: {info['nagroda_blokowa']} BTC"])
        if inf_pct <= 2.0:
            return self._bazowy_sygnal(inf_pct, "LONG", 0.40,
                [f"BTC inflacja={inf_pct:.3f}% — porównywalna ze złotem"])
        return self._bazowy_sygnal(inf_pct, "NEUTRAL", 0.0,
            [f"BTC inflacja={inf_pct:.3f}% — przed halvingiem (wyższa podaż)"])
