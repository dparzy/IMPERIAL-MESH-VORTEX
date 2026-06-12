"""
⏰ IMV-SES | Neurony Zegarów Rynku — sesje, rytm fundingu, sezonowość (Faza C, W-286).

Krypto handluje 24/7, ale NIE jednorodnie — rynek ma ZEGARY:
  • sesje instytucjonalne (Azja 00–08, Londyn 08–16, NY 13–21 UTC),
  • rytm fundingu perpetuali co 8h (00/08/16 UTC) — wokół settlement
    spready/zachowanie się zmieniają (spread peak ~2h po settlement),
  • sezonowość godzinowa BTC (najsilniejsze zwroty 21–23 UTC, efekt piątku).

ŹRÓDŁA (ZPO — pełne linki, zwiad 2026-06-10):
  • Sesje/Azja Range: docs/WIZJONER.md W-011 + docs/SKAN_AZJA.md (katalog).
  • Rytm fundingu: "Temporal Dynamics of Market Microstructure in Cryptocurrency
    Perpetual Futures" (MDPI 2026), https://www.mdpi.com/2227-7072/14/5/103 —
    spready statystycznie powiązane z settlement, szczyt ~2h po 00/08/16 UTC.
  • Sezonowość godzinowa: QuantPedia "The Seasonality of Bitcoin",
    https://quantpedia.com/the-seasonality-of-bitcoin/ (21:00–23:00 UTC, piątek)
    + "Turn-of-the-candle effect", https://pmc.ncbi.nlm.nih.gov/articles/PMC10015199/
    ⚠️ efekty publikowane = mogły osłabnąć; neuron daje SŁABE sygnały kontekstowe,
    nie samodzielne wejścia (waga niska, pomiar zdecyduje).

Dane: WYŁĄCZNIE timestamp + OHLC z Budowniczego (ASIA_HIGH/ASIA_LOW/ASIA_GOTOWA,
TIMESTAMP) — działa w backteście CSV bez żadnego API (Prawo XV).
"""

from datetime import datetime, timezone

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu

_H = 3_600_000  # ms w godzinie


def _godzina_utc(ts_ms) -> "int | None":
    if ts_ms is None:
        return None
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).hour


def _dzien_tygodnia_utc(ts_ms) -> "int | None":
    """0=poniedziałek … 4=piątek … 6=niedziela."""
    if ts_ms is None:
        return None
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).weekday()


class NeuronZegarSesji(MikroNeuron):
    """
    SES-01 | Zegar Sesji i Rytmu Fundingu — kontekst czasu, nie kierunek ceny.

    Logika (badania w docstringu modułu):
      • 0–2h PO settlement fundingu (00/08/16 UTC) → NEUTRAL z podwyższoną
        pewnością kontekstu "ostrożność" (spread peak — gorsze wykonanie).
      • Piątek 21–23 UTC → słaby LONG-bias (udokumentowana sezonowość BTC).
      • Poza tym → NEUTRAL niski (zegar nie ma zdania).
    """
    KLUCZ = "SES-01"
    LEGION = "SCALP"
    WSKAZNIK = "ZEGAR_SESJI"
    KATEGORIA = "S"
    WAGA = 4   # kontekst, nie silnik — niska waga z założenia

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        ts = wskazniki.get("TIMESTAMP")
        if ts is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak TIMESTAMP"])
        godz = _godzina_utc(ts)
        dz = _dzien_tygodnia_utc(ts)
        # minuty od ostatniego settlementu fundingu (00/08/16 UTC)
        ms_w_cyklu = int(ts) % (8 * _H)
        po_settlement_h = ms_w_cyklu / _H

        if po_settlement_h < 2.0:
            return self._bazowy_sygnal(po_settlement_h, "NEUTRAL", 0.55,
                [f"⏰ {po_settlement_h:.1f}h po settlement fundingu — spread peak, "
                 f"gorsze wykonanie (MDPI 2026); ostrożność z wejściami"])
        if dz == 4 and 21 <= godz < 23:
            return self._bazowy_sygnal(float(godz), "LONG", 0.58,
                ["⏰ Piątek 21–23 UTC — udokumentowana dodatnia sezonowość BTC "
                 "(QuantPedia); słaby LONG-bias"])
        return self._bazowy_sygnal(float(godz), "NEUTRAL", 0.10,
            [f"⏰ Zegar bez anomalii (godz {godz} UTC)"])


class NeuronAzjaRange(MikroNeuron):
    """
    SES-02 | Azja Range Breakout (W-011) — instytucjonalny edge sesyjny.

    Sesja azjatycka (00–08 UTC) buduje zakres; Londyn/NY go rozstrzygają:
      • ASIA_GOTOWA i close > ASIA_HIGH → LONG (breakout z akumulacji)
      • ASIA_GOTOWA i close < ASIA_LOW  → SHORT
      • wewnątrz zakresu / Azja trwa    → NEUTRAL (czekamy na rozstrzygnięcie)
    Im dalej od zakresu (w % szerokości), tym wyższa pewność (cap 0.85).
    """
    KLUCZ = "SES-02"
    LEGION = "SCALP"
    WSKAZNIK = "ASIA_RANGE"
    KATEGORIA = "S"
    WAGA = 7

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        close = wskazniki.get("CLOSE")
        hi = wskazniki.get("ASIA_HIGH")
        lo = wskazniki.get("ASIA_LOW")
        gotowa = wskazniki.get("ASIA_GOTOWA")
        if close is None or hi is None or lo is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak zakresu Azji"])
        if not gotowa:
            return self._bazowy_sygnal(close, "NEUTRAL", 0.10,
                ["Sesja azjatycka trwa — zakres niedomknięty (bez look-ahead)"])
        szer = hi - lo
        if szer <= 0:
            return self._bazowy_sygnal(close, "NEUTRAL", 0.0,
                ["Zdegenerowany zakres Azji (szerokość ≤ 0)"])
        if close > hi:
            sila = min(0.85, 0.60 + (close - hi) / szer * 0.5)
            return self._bazowy_sygnal(close, "LONG", sila,
                [f"🌅 Breakout > Asia High {hi:.2f} (zakres {szer:.2f}) — W-011"])
        if close < lo:
            sila = min(0.85, 0.60 + (lo - close) / szer * 0.5)
            return self._bazowy_sygnal(close, "SHORT", sila,
                [f"🌅 Breakdown < Asia Low {lo:.2f} (zakres {szer:.2f}) — W-011"])
        return self._bazowy_sygnal(close, "NEUTRAL", 0.15,
            [f"Wewnątrz zakresu Azji [{lo:.2f}–{hi:.2f}] — bez rozstrzygnięcia"])


class NeuronAugur(MikroNeuron):
    """
    AUG-01 | Augur Zdarzeń (W-289 💎 v2) — głos historycznych analogii.

    Czyta kontekst Kronikarza (AdapterKronikarz → EVENT_*) i głosuje:
      • BLACKOUT (FED w ≤2 dni PRZED nami) → NEUTRAL-ostrożność (pewność 0.55):
        nie zgadujemy kierunku przed posiedzeniem, sygnalizujemy redukcję ryzyka.
      • n ≥ 2, prob ≥ 65% → LONG; prob ≤ 35% → SHORT. Pewność modulowana:
        bazowa × WAGA_ZANIKU (świeże zdarzenie mocniej) × bonus za ZGODNOŚĆ
        kierunkową historycznych epizodów (wszystkie w tę samą stronę = pewniej).
      • n < 2 (za mało historii) lub prob w środku → NEUTRAL z kontekstem.
    Poza oknem wpływu (brak EVENT_*) → abstynencja (Prawo XV).
    """
    KLUCZ = "AUG-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "EVENT_PROB_WZROSTU"
    KATEGORIA = "R"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        prob = wskazniki.get("EVENT_PROB_WZROSTU")
        n = wskazniki.get("EVENT_N")
        typ = wskazniki.get("EVENT_TYP")
        dni = wskazniki.get("EVENT_DNI_PO")
        waga = wskazniki.get("EVENT_WAGA")
        zgodne = wskazniki.get("EVENT_ZGODNE")
        blackout = wskazniki.get("EVENT_BLACKOUT")
        if typ is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak okna zdarzenia (Augur milczy)"])
        if blackout:
            dni_do = wskazniki.get("EVENT_DNI_DO", abs(dni) if dni is not None else "?")
            return self._bazowy_sygnal(0.0, "NEUTRAL", 0.55,
                [f"⚠️📜 {typ} za ~{dni_do}d — BLACKOUT: zredukuj ryzyko przed posiedzeniem"])
        if prob is None or n is None or n < 2:
            return self._bazowy_sygnal(prob, "NEUTRAL", 0.30,
                [f"📜 {typ} ({dni}d po): tylko {n or 0} epizodów w historii — "
                 f"za mało na werdykt (Prawo I)"])
        # Modulatory pewności: świeżość (decay) × zgodność kierunkowa.
        mod_waga = waga if isinstance(waga, (int, float)) else 1.0
        mod_zgod = 1.0 if zgodne else 0.8
        if prob >= 65.0:
            pewnosc = min(0.80, prob / 100.0 * mod_waga * mod_zgod)
            return self._bazowy_sygnal(prob, "LONG", pewnosc,
                [f"📜 {typ} ({dni}d po): {prob:.0f}% wzrostów w n={n} epizodach "
                 f"(waga {mod_waga:.2f}, {'zgodne' if zgodne else 'rozsypane'}) — LONG"])
        if prob <= 35.0:
            pewnosc = min(0.80, (100.0 - prob) / 100.0 * mod_waga * mod_zgod)
            return self._bazowy_sygnal(prob, "SHORT", pewnosc,
                [f"📜 {typ} ({dni}d po): tylko {prob:.0f}% wzrostów w n={n} epizodach "
                 f"(waga {mod_waga:.2f}, {'zgodne' if zgodne else 'rozsypane'}) — SHORT"])
        return self._bazowy_sygnal(prob, "NEUTRAL", 0.25,
            [f"📜 {typ} ({dni}d po): {prob:.0f}% w n={n} — historia bez przewagi"])


class NeuronRadarBTC(MikroNeuron):
    """
    RADAR-01 💎 | Strażnik BTC (W-291, lead-lag) — wsparcie kontekstowe dla altów.

    BTC prowadzi rynek: gdy lider rośnie, alty mają wiatr w plecy; gdy spada, lecą
    za nim. Ten neuron czyta BTC_TREND ∈ [-1,+1] (z RadarBTC, wstrzyknięty do
    wskaźników) i głosuje JAKO RADAR — nie zastępuje analizy alta, lecz mówi
    "uważaj / teraz" zgodnie z liderem:
      • BTC_TREND ≥ +0.30 → LONG-wsparcie (siła ~ |trend|, cap 0.7)
      • BTC_TREND ≤ −0.30 → SHORT-wsparcie / ostrzeżenie
      • między → NEUTRAL (lider niezdecydowany)
    Brak BTC_TREND (np. para = sam BTC bez kontekstu) → abstynencja (Prawo XV).
    Waga umiarkowana: to RADAR wspierający, nie samodzielny silnik.
    """
    KLUCZ = "RADAR-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BTC_TREND"
    KATEGORIA = "R"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        bt = wskazniki.get("BTC_TREND")
        if bt is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak kontekstu BTC (radar milczy)"])
        if bt >= 0.30:
            return self._bazowy_sygnal(bt, "LONG", min(0.70, abs(bt)),
                [f"🛰️ RADAR BTC: lider w trendzie↑ ({bt:+.2f}) — wiatr w plecy altów"])
        if bt <= -0.30:
            return self._bazowy_sygnal(bt, "SHORT", min(0.70, abs(bt)),
                [f"🛰️ RADAR BTC: lider spada ({bt:+.2f}) — uważaj, alty lecą za BTC"])
        return self._bazowy_sygnal(bt, "NEUTRAL", 0.15,
            [f"🛰️ RADAR BTC: lider niezdecydowany ({bt:+.2f})"])


class NeuronDominacja(MikroNeuron):
    """
    RADAR-02 💎 | Strażnik Dominacji BTC (W-292) — przepływ kapitału BTC↔alty.

    BTC_DOMINANCJA ∈ [-1,+1] (z RadarRynku): siła względna BTC vs koszyk altów.
    Z perspektywy ALTA (większość koszyka) głosuje jako RADAR bocznej flanki:
      • DOMINANCJA ≤ −0.30 → alt-season (kapitał płynie w alty) → LONG-wsparcie
      • DOMINANCJA ≥ +0.30 → ucieczka do BTC (alty słabną) → SHORT-ostrzeżenie
      • między → NEUTRAL (przepływ niejednoznaczny)
    Brak BTC_DOMINANCJA → abstynencja (Prawo XV). Waga umiarkowana — kontekst
    wspierający, nie samodzielny silnik (jak RADAR-01).
    """
    KLUCZ = "RADAR-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "BTC_DOMINANCJA"
    KATEGORIA = "R"
    WAGA = 5

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        dom = wskazniki.get("BTC_DOMINANCJA")
        if dom is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak dominacji BTC (radar milczy)"])
        if dom <= -0.30:
            return self._bazowy_sygnal(dom, "LONG", min(0.65, abs(dom)),
                [f"🌐 DOMINACJA {dom:+.2f}: alt-season — kapitał płynie w alty (LONG-wsparcie)"])
        if dom >= 0.30:
            return self._bazowy_sygnal(dom, "SHORT", min(0.65, abs(dom)),
                [f"🌐 DOMINACJA {dom:+.2f}: ucieczka do BTC — alty słabną (SHORT-ostrzeżenie)"])
        return self._bazowy_sygnal(dom, "NEUTRAL", 0.15,
            [f"🌐 DOMINACJA {dom:+.2f}: przepływ kapitału niejednoznaczny"])


class NeuronPrzeplyw(MikroNeuron):
    """
    RADAR-03 💎 | Strażnik Przepływu Kapitału (W-292) — breadth × momentum wolumenu.

    PRZEPLYW_KAPITALU ∈ [0,1] (z RadarRynku): ułamek koszyka nad własną EMA ważony
    momentum wolumenu. To barometr risk-on/risk-off całego rynku:
      • PRZEPLYW ≥ 0.65 → napływ kapitału (breadth szeroki) → LONG-wsparcie (risk-on)
      • PRZEPLYW ≤ 0.35 → odpływ kapitału (rynek wąski) → SHORT-ostrzeżenie (risk-off)
      • między → NEUTRAL (rynek bez wyraźnego kierunku kapitału)
    Brak PRZEPLYW_KAPITALU → abstynencja (Prawo XV). Waga umiarkowana — kontekst.
    """
    KLUCZ = "RADAR-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "PRZEPLYW_KAPITALU"
    KATEGORIA = "R"
    WAGA = 5

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        pk = wskazniki.get("PRZEPLYW_KAPITALU")
        if pk is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak przepływu kapitału (radar milczy)"])
        if pk >= 0.65:
            return self._bazowy_sygnal(pk, "LONG", min(0.60, (pk - 0.5) * 1.2),
                [f"💧 PRZEPŁYW {pk:.2f}: napływ kapitału, breadth szeroki (risk-on, LONG-wsparcie)"])
        if pk <= 0.35:
            return self._bazowy_sygnal(pk, "SHORT", min(0.60, (0.5 - pk) * 1.2),
                [f"💧 PRZEPŁYW {pk:.2f}: odpływ kapitału, rynek wąski (risk-off, SHORT-ostrzeżenie)"])
        return self._bazowy_sygnal(pk, "NEUTRAL", 0.15,
            [f"💧 PRZEPŁYW {pk:.2f}: kapitał bez wyraźnego kierunku"])
