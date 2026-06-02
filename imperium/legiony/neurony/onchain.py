"""
⚔️ IMV-INS | Neurony On-Chain — Dywizja Wieszczowie
MVRV-Z, SOPR, Puell Multiple, NVT, Exchange Netflow.
Dane fundamentalne on-chain — cykle makro.

UWAGA: OC-01..OC-04 wymagają zewnętrznego API on-chain (Glassnode/CryptoQuant).
Brama Kalkulatora NIE dostarcza tych danych — neurony są wyciszone (DOSTEPNY=False)
do czasu podpięcia adapterów API. Logika interpretacji jest gotowa i poprawna.
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
        netflow_ma7 = wskazniki.get("EXCHANGE_NETFLOW_MA7")
        if netflow is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak Exchange Netflow"])

        if netflow_ma7 is not None:
            trend_napływu = netflow > netflow_ma7
        else:
            trend_napływu = netflow > 0

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
