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
    AUG-01 | Augur Zdarzeń (W-289 💎) — głos historycznych analogii.

    Czyta kontekst Kronikarza Zdarzeń (AdapterKronikarz → EVENT_*): jeśli
    jesteśmy w oknie wpływu zdarzenia fundamentalnego, głosuje wg PRZYCZYNOWO
    policzonych statystyk wcześniejszych epizodów tego typu:
      • n ≥ 2 i prob_wzrostu ≥ 65% → LONG (pewność ~ prob, cap 0.8)
      • n ≥ 2 i prob_wzrostu ≤ 35% → SHORT
      • n < 2 (za mało historii) lub prob w środku → NEUTRAL z kontekstem
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
        if prob is None or typ is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak okna zdarzenia (Augur milczy)"])
        if n is None or n < 2:
            return self._bazowy_sygnal(prob, "NEUTRAL", 0.30,
                [f"📜 {typ} ({dni}d po): tylko {n or 0} epizodów w historii — "
                 f"za mało na werdykt (Prawo I)"])
        if prob >= 65.0:
            pewnosc = min(0.80, prob / 100.0)
            return self._bazowy_sygnal(prob, "LONG", pewnosc,
                [f"📜 {typ} ({dni}d po): {prob:.0f}% wzrostów w n={n} "
                 f"historycznych epizodach — analogia LONG"])
        if prob <= 35.0:
            pewnosc = min(0.80, (100.0 - prob) / 100.0)
            return self._bazowy_sygnal(prob, "SHORT", pewnosc,
                [f"📜 {typ} ({dni}d po): tylko {prob:.0f}% wzrostów w n={n} "
                 f"epizodach — analogia SHORT"])
        return self._bazowy_sygnal(prob, "NEUTRAL", 0.25,
            [f"📜 {typ} ({dni}d po): {prob:.0f}% w n={n} — historia bez przewagi"])
