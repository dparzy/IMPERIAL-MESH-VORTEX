"""
🔱 IMV-ADO | EXP-10 Displacement Scalper — impuls strukturalny (Gold Scalper engine)

Adoptowane z: Gold Scalper Pro (XAUUSD, "structural inefficiencies")
Seal: IMV-ADO v1.0 — naprawiony i wzmocniony na potrzeby Imperium

Naprawione błędy oryginału:
  1. PRAWDZIWY ATR: True Range z previous close zamiast (high-low).rolling.mean().
  2. SYMETRYCZNE PRZEMIESZCZENIE: oryginał liczył inefficiency tylko z 'high'
     ((high - high[lookback])/close) — ignorował 'low', więc ruchy w dół były
     niedoszacowane. Naprawione: bierzemy max przemieszczenia high I low (oba
     kierunki traktowane symetrycznie).

Koncept (Structural Inefficiency / Displacement — komplementarny do EXP-05):
  EXP-05 FVG = statyczne strefy luki (3-świecowa imbalance).
  EXP-10 = dynamiczny SPIKE przemieszczenia: cena pokonała w ostatnich `lookback`
  barach dystans znacznie większy niż zwykle = impuls strukturalny (smart money
  displacement). Handlujemy KONTYNUACJĘ impulsu, gdy zmienność jest umiarkowana
  (nie w chaotycznym ekstremum).

Logika:
  displacement = max(|high-high[lookback]|, |low-low[lookback]|) / close
  spike        = displacement > 1.5× swojej średniej z 20 barów
  filtr_zmiennosci = ATR < 1.2× ATR_MA50 (unikaj chaosu)
  kierunek     = znak (close - close[lookback]) — dokąd poszedł impuls
"""

from typing import List, Dict

from .baza import ZwiadowcaElitarny, RaportZwiadowcy


def _atr_series(bary: List[Dict]) -> List[float]:
    """Prawdziwy True Range — uwzględnia previous close."""
    trs = [bary[0].get("high", 0) - bary[0].get("low", 0)] if bary else []
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        pc = bary[i - 1].get("close", 0)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return trs


def _atr_at(trs: List[float], idx: int, period: int) -> float:
    start = max(0, idx - period + 1)
    window = trs[start:idx + 1]
    return sum(window) / len(window) if window else 0.0


def _displacement_series(bary: List[Dict], lookback: int) -> List[float]:
    """
    Symetryczne przemieszczenie strukturalne dla każdego bara.
    disp[i] = max(|high[i]-high[i-lookback]|, |low[i]-low[i-lookback]|) / close[i]
    """
    disp = []
    for i in range(len(bary)):
        if i < lookback:
            disp.append(0.0)
            continue
        c = bary[i].get("close", 0) or 1.0
        dh = abs(bary[i].get("high", 0) - bary[i - lookback].get("high", 0))
        dl = abs(bary[i].get("low", 0) - bary[i - lookback].get("low", 0))
        disp.append(max(dh, dl) / c)
    return disp


class ZwiadowcaDisplacement(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-10 Displacement Scalper
    Detektor impulsu strukturalnego — kontynuacja po spike przemieszczenia.
    """
    KLUCZ = "EXP-10"
    WSKAZNIK = "DISPLACEMENT"
    LEGION = "SCALP"
    KATEGORIA = "S"  # Struktura
    WAGA = 7

    LOOKBACK: int = 5
    ATR_PERIOD: int = 10
    DISP_MA: int = 20
    DISP_MULT: float = 1.5     # spike > 1.5× średniej
    ATR_MA: int = 50
    ATR_MAX_MULT: float = 1.2  # ATR < 1.2× MA50 = zmienność umiarkowana
    WYMAGA_BAROW: int = 55

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        n = len(bary) - 1
        disp = _displacement_series(bary, self.LOOKBACK)
        disp_curr = disp[n]
        disp_ma = sum(disp[-self.DISP_MA:]) / len(disp[-self.DISP_MA:])

        trs = _atr_series(bary)
        atr = _atr_at(trs, n, self.ATR_PERIOD)
        atr_ma_vals = [_atr_at(trs, i, self.ATR_PERIOD)
                       for i in range(max(0, n - self.ATR_MA), n + 1)]
        atr_ma = sum(atr_ma_vals) / len(atr_ma_vals) if atr_ma_vals else atr
        atr_ok = atr < atr_ma * self.ATR_MAX_MULT

        close = bary[n].get("close", 0)
        close_lb = bary[n - self.LOOKBACK].get("close", 0)
        kierunek_impulsu = close - close_lb

        spike = disp_curr > disp_ma * self.DISP_MULT

        powody = [
            f"displacement={disp_curr:.5f} vs MA×{self.DISP_MULT}={disp_ma * self.DISP_MULT:.5f}",
            f"spike={spike}",
            f"ATR={atr:.4f} (filtr<{atr_ma * self.ATR_MAX_MULT:.4f}: {atr_ok})",
            f"kierunek_impulsu={kierunek_impulsu:+.4f}",
        ]
        diag = {"main_value": disp_curr, "atr": atr}

        if not spike:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Brak spike przemieszczenia — rynek bez impulsu strukturalnego"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if not atr_ok:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Zmienność za wysoka (chaos) — impuls niewiarygodny"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        # Siła: jak bardzo displacement przekracza średnią
        nadwyzka = disp_curr / (disp_ma * self.DISP_MULT) if disp_ma > 0 else 1.0
        sila = min(1.0, (nadwyzka - 1.0))
        pewnosc = min(0.85, 0.60 + sila * 0.25)

        if kierunek_impulsu > 0:
            return self._buduj_raport(
                kierunek="LONG", pewnosc=pewnosc,
                powody=["IMPULS STRUKTURALNY w górę (kontynuacja) → LONG"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if kierunek_impulsu < 0:
            return self._buduj_raport(
                kierunek="SHORT", pewnosc=pewnosc,
                powody=["IMPULS STRUKTURALNY w dół (kontynuacja) → SHORT"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=["Spike bez wyraźnego kierunku impulsu"] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
