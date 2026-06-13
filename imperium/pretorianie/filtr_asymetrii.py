"""
Filtr Asymetrii Reżimu (W-314) — brama wejścia oparta na trendzie i jego sile.

DLA NOWICJUSZA: pomiar OOS (2024-10..2026-06, BTC płaski +0,8%) pokazał, że rój
TRACI na rynku bez trendu — wchodzi za często, gdy nie ma czego złapać (piła/chop),
a prowizje i whipsaw zjadają cienką przewagę. Ten filtr podnosi poprzeczkę pewności
w dwóch niekorzystnych sytuacjach, ZAMIAST przepuszczać każdy sygnał:

  1. RYNEK BOCZNY (ADX < prog_adx_range) — brak trendu → wymagamy WYSOKIEJ pewności,
     bo to teren, gdzie historycznie tracimy. Słaby sygnał w chopie = weto.
  2. KONTR-TREND (sygnał przeciw kierunkowi EMA-200 przy silnym ADX) — łapanie
     spadającego noża / shortowanie silnej hossy → wymagamy WYŻSZEJ pewności niż
     dla wejścia zgodnego z trendem.

Wejście ZGODNE z trendem przy realnej sile (ADX ≥ prog_adx_trend) przechodzi
normalnym progiem — nie utrudniamy tego, co działa.

PODSTAWA (literatura):
  • Time-Series Momentum — Moskowitz, Ooi, Pedersen (2012), Journal of Financial
    Economics — trade'y zgodne z trendem niosą wyższą oczekiwaną stopę zwrotu niż
    kontr-trendowe. Stąd asymetria progu kierunku.
    https://www.sciencedirect.com/science/article/abs/pii/S0304405X11002613
  • ADX (Average Directional Index) — J. Welles Wilder (1978), "New Concepts in
    Technical Trading Systems" — ADX < 20-25 = brak trendu (rynek boczny),
    ≥ 25 = trend wyraźny. Próg 25 to kanoniczna granica „silnego trendu".

CZYSTY OHLCV: filtr używa wyłącznie CLOSE, EMA_200, ADX_14 — wskaźników, które
Budowniczy produkuje zawsze z samych świec. W przeciwieństwie do neuronów R
(funding/OI — czekają na feed futures) NIGDY nie jest martwym głosem w backteście.

ABSTYNENCJA (Prawo XV): gdy brak EMA_200 lub ADX (za krótka historia) — filtr
PRZEPUSZCZA (nie blokuje przy niewiedzy). Lepiej nie filtrować niż filtrować na ślepo.

Użycie:
    f = FiltrAsymetriiRezimu()
    w = f.ocen(kierunek, pewnosc, wskazniki)
    if not w.dozwolone:
        ...  # weto wejścia, powód w w.powod
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("FiltrAsymetrii")


@dataclass
class WerdyktAsymetrii:
    """Wynik oceny filtra: czy wejście dozwolone + diagnostyka."""
    dozwolone: bool
    powod: str
    trend: str            # "UP" / "DOWN" / "BRAK"
    adx: float            # siła trendu (0 gdy brak danych)
    prog_wymagany: float  # próg pewności, który trzeba było przebić
    kontr_trend: bool     # czy sygnał był przeciw trendowi


@dataclass
class FiltrAsymetriiRezimu:
    """
    Asymetryczna brama wejścia (W-314).

    prog_adx_trend:  ADX ≥ ten próg = trend wyraźny (Wilder: 25).
    prog_adx_range:  ADX < ten próg = rynek boczny/chop (Wilder: 20).
                     Strefa pomiędzy (range..trend) jest neutralna — bez kary.
    prog_kontr:      minimalna pewność dla wejścia KONTR-trendowego przy silnym ADX.
    prog_range:      minimalna pewność dla wejścia w rynku bocznym (ADX < range).
    """
    prog_adx_trend: float = 25.0
    prog_adx_range: float = 20.0
    prog_kontr: float = 0.65
    prog_range: float = 0.70

    def ocen(self, kierunek: str, pewnosc: float, wskazniki: dict) -> WerdyktAsymetrii:
        close = wskazniki.get("CLOSE")
        ema = wskazniki.get("EMA_200")
        adx = wskazniki.get("ADX_14")

        # Abstynencja (Prawo XV) — brak danych trendu → przepuść bez kary.
        if close is None or ema is None or adx is None:
            return WerdyktAsymetrii(True, "brak danych trendu — abstynencja",
                                    "BRAK", 0.0, 0.0, False)

        trend = "UP" if close > ema else "DOWN"
        aligned = (kierunek == "LONG" and trend == "UP") or \
                  (kierunek == "SHORT" and trend == "DOWN")
        kontr = not aligned

        # 1. Rynek boczny (brak trendu) — najwyższa poprzeczka, tu tracimy najwięcej.
        if adx < self.prog_adx_range:
            if pewnosc < self.prog_range:
                return WerdyktAsymetrii(
                    False, f"rynek boczny (ADX {adx:.0f} < {self.prog_adx_range:.0f}) — "
                           f"pewność {pewnosc:.2f} < próg {self.prog_range:.2f}",
                    trend, adx, self.prog_range, kontr)
            return WerdyktAsymetrii(True, f"boczny ale pewność {pewnosc:.2f} ≥ {self.prog_range:.2f}",
                                    trend, adx, self.prog_range, kontr)

        # 2. Kontr-trend przy SILNYM trendzie — wyższy próg (Moskowitz 2012).
        if kontr and adx >= self.prog_adx_trend:
            if pewnosc < self.prog_kontr:
                return WerdyktAsymetrii(
                    False, f"kontr-trend ({kierunek} vs trend {trend}, ADX {adx:.0f}) — "
                           f"pewność {pewnosc:.2f} < próg {self.prog_kontr:.2f}",
                    trend, adx, self.prog_kontr, kontr)
            return WerdyktAsymetrii(True, f"kontr-trend ale pewność {pewnosc:.2f} ≥ {self.prog_kontr:.2f}",
                                    trend, adx, self.prog_kontr, kontr)

        # 3. Zgodne z trendem lub strefa neutralna — przepuść normalnie.
        return WerdyktAsymetrii(True, "zgodne z trendem / strefa neutralna",
                                trend, adx, 0.0, kontr)
