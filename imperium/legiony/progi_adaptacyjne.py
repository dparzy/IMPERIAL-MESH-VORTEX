"""
W-334 — Progi adaptacyjne (P3): kameleon progów RSI/ADX wg reżimu i zmienności.

Problem (Prawo XV): progi 30/70 (RSI) i 25 (ADX) są SZTYWNE. W silnym trendzie
RSI siedzi >70 godzinami — sztywny próg każe grać kontra-trend (strata). W ciasnym
range RSI rzadko dotyka 30/70 — neuron milczy, choć mean-reversion działa.

Rozwiązanie: progi przesuwają się wg kontekstu:
  - TREND_STRONG → rozsuń RSI (20/80): trudniej grać przeciw trendowi.
  - RANGING      → zsuń RSI (35/65): łatwiej łapać mean-reversion.
  - wysoka zmienność (ATR%) → rozsuń dalej (więcej szumu = wyższy próg).
  - niska zmienność → zsuń (czysty sygnał, niższy próg wystarczy).

Prawo I: czy to POMAGA — rozstrzyga A/B (narzedzia/ab_w334_progi.py), nie opinia.
Prawo XV: brak kontekstu (rezim=None, atr_pct=None) → progi bazowe = zero regresji.

Wszystkie progi w bezpiecznych granicach (RSI 5–95, ADX 15–35) — nigdy absurdu.
"""

from typing import Optional, Tuple

# Bazowe progi (stan sprzed W-334 — fallback bez kontekstu)
RSI_DOLNY_BAZA = 30.0
RSI_GORNY_BAZA = 70.0
ADX_BAZA = 25.0

# Granice bezpieczeństwa — próg nigdy nie wyjdzie poza ten zakres
RSI_DOLNY_MIN, RSI_DOLNY_MAX = 5.0, 45.0
RSI_GORNY_MIN, RSI_GORNY_MAX = 55.0, 95.0
ADX_MIN, ADX_MAX = 15.0, 35.0

# Progi zmienności (ATR/cena): poniżej = spokój, powyżej = chaos
ATR_PCT_NISKA = 0.01   # <1% ATR/cena = rynek spokojny
ATR_PCT_WYSOKA = 0.05  # >5% ATR/cena = rynek bardzo zmienny


def atr_pct(wskazniki: dict) -> Optional[float]:
    """Zmienność znormalizowana: ATR_14 / CLOSE. None gdy brak danych."""
    atr = wskazniki.get("ATR_14")
    close = wskazniki.get("CLOSE")
    if atr is None or close is None or close <= 0:
        return None
    return atr / close


def progi_rsi(rezim: Optional[str] = None,
              atr_p: Optional[float] = None) -> Tuple[float, float]:
    """
    Zwraca (dolny, gorny) progi RSI dostosowane do reżimu i zmienności.

    Bez kontekstu → (30, 70) bazowe. Trend rozsuwa, range zsuwa.
    Zmienność rozsuwa (wysoka) lub zsuwa (niska). Klamrowane do granic.
    """
    dolny, gorny = RSI_DOLNY_BAZA, RSI_GORNY_BAZA

    if rezim == "TREND_STRONG":
        dolny, gorny = 20.0, 80.0   # trudniej grać kontra-trend
    elif rezim == "RANGING":
        dolny, gorny = 35.0, 65.0   # łatwiej łapać mean-reversion
    elif rezim in ("VOLATILE", "PANIC"):
        dolny, gorny = 25.0, 75.0   # lekko rozsunięte (szum)

    if atr_p is not None:
        if atr_p >= ATR_PCT_WYSOKA:
            dolny -= 5.0
            gorny += 5.0
        elif atr_p <= ATR_PCT_NISKA:
            dolny += 3.0
            gorny -= 3.0

    dolny = max(RSI_DOLNY_MIN, min(RSI_DOLNY_MAX, dolny))
    gorny = max(RSI_GORNY_MIN, min(RSI_GORNY_MAX, gorny))
    return dolny, gorny


def prog_adx(rezim: Optional[str] = None,
             atr_p: Optional[float] = None) -> float:
    """
    Zwraca próg ADX (siła trendu) dostosowany do reżimu i zmienności.

    W chaosie (VOLATILE/PANIC) wymagamy MOCNIEJSZEGO trendu (wyższy próg),
    by nie mylić szarpaniny z trendem. W spokoju niższy próg wystarczy.
    """
    prog = ADX_BAZA

    if rezim in ("VOLATILE", "PANIC"):
        prog = 30.0   # tylko wyraźny trend liczy się w chaosie
    elif rezim == "TREND_STRONG":
        prog = 22.0   # trend już potwierdzony — niższy próg ok
    elif rezim == "RANGING":
        prog = 28.0   # w range podnieś poprzeczkę (mniej fałszywych trendów)

    if atr_p is not None and atr_p >= ATR_PCT_WYSOKA:
        prog += 2.0

    return max(ADX_MIN, min(ADX_MAX, prog))
