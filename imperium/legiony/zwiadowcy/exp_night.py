"""
🔱 IMV-ADO | EXP-08 Night Turbo Scalper — kontrarianski scalper nocny (mean-reversion)

Adoptowane z: Night Turbo EA
Seal: IMV-ADO v1.0 — naprawiony i wzmocniony na potrzeby Imperium

Naprawione błędy oryginału:
  1. PRAWDZIWY ATR: oryginał liczył (high-low).rolling.mean() = zaniżony przy gapach.
     Naprawione: True Range = max(H-L, |H-prevC|, |L-prevC|).
  2. ATR FAKTYCZNIE UŻYWANY: oryginał liczył atr i NIGDY go nie używał (martwy kod,
     utrata potencjału). Naprawione: próg wybicia jest adaptacyjny względem ATR,
     nie sztywny 0.1%.
  3. SESJA Z EPOCH TIMESTAMP: oryginał wymagał DatetimeIndex (df.index.hour).
     Nasze bary mają timestamp (epoch sekundy/ms) — liczymy godzinę UTC sami.

Koncept (zachowany — komplementarny do EXP-07):
  EXP-07 = pro-breakout (handel z wybiciem, wysoka zmienność).
  EXP-08 = anty-breakout (fade fałszywych wybić w nocnym range, niska zmienność).
  Mała świeca wybijająca w górę w nocy = prawdopodobny fakeout → SHORT (i odwrotnie).

Filtry (potrójna bramka):
  1. Sesja nocna (domyślnie 22:00–02:00 UTC) — niska płynność, range-bound
  2. Niska zmienność (range < 0.8× średniej z 50 barów) — potwierdzenie konsolidacji
  3. Ruch przekracza próg adaptacyjny (×ATR), ale nie jest prawdziwym breakoutem
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

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


def _godzina_utc(ts: Any) -> Optional[int]:
    """
    Wyciąga godzinę UTC z timestamp (epoch s lub ms) lub ISO string.
    Zwraca None jeśli brak/niepoprawny timestamp.
    """
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            # ms jeśli bardzo duża liczba
            sek = ts / 1000.0 if ts > 1e11 else float(ts)
            return datetime.fromtimestamp(sek, tz=timezone.utc).hour
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).hour
    except (ValueError, OverflowError, OSError):
        return None
    return None


def _sesja_nocna(godzina: Optional[int], start: int, koniec: int) -> bool:
    """Czy godzina mieści się w sesji nocnej (z wraparound przez północ)."""
    if godzina is None:
        return False
    if start <= koniec:
        return start <= godzina < koniec
    # wraparound (np. 22→2): noc to >=22 LUB <2
    return godzina >= start or godzina < koniec


class ZwiadowcaNightTurbo(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-08 Night Turbo Scalper
    Kontrarianski scalper nocny — fade fałszywych wybić w niskiej zmienności.
    """
    KLUCZ = "EXP-08"
    WSKAZNIK = "NIGHT_TURBO"
    LEGION = "SCALP"
    KATEGORIA = "M"  # mean-reversion momentum
    WAGA = 6

    NIGHT_START: int = 22       # UTC
    NIGHT_END: int = 2          # UTC
    ATR_PERIOD: int = 10
    PROG_ATR_MULT: float = 0.5  # ruch > 0.5×ATR = warty fade
    RANGE_MA: int = 50
    VOL_FACTOR: float = 0.8     # range < 0.8× średniej = niska zmienność
    WYMAGA_BAROW: int = 55

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        n = len(bary) - 1
        bar = bary[n]
        close = bar.get("close", 0)
        close_prev = bary[n - 1].get("close", 0)

        # 1. Sesja nocna
        godzina = _godzina_utc(bar.get("timestamp"))
        noc = _sesja_nocna(godzina, self.NIGHT_START, self.NIGHT_END)

        # 2. Prawdziwy ATR (faktycznie używany)
        trs = _atr_series(bary)
        atr = _atr_at(trs, n, self.ATR_PERIOD)

        # 3. Niska zmienność (range bieżący vs średnia)
        ranges = [
            (b.get("high", 0) - b.get("low", 0)) / b.get("close", 1)
            if b.get("close", 0) else 0.0
            for b in bary
        ]
        range_curr = ranges[n]
        range_ma = sum(ranges[-self.RANGE_MA:]) / len(ranges[-self.RANGE_MA:])
        low_vol = range_curr < range_ma * self.VOL_FACTOR

        # 4. Próg adaptacyjny względem ATR (naprawiony — nie sztywny 0.1%)
        prog = self.PROG_ATR_MULT * atr
        ruch = close - close_prev

        powody = [
            f"godzina_UTC={godzina}",
            f"noc={noc}",
            f"ATR={atr:.4f}",
            f"prog={prog:.4f}",
            f"ruch={ruch:+.4f}",
            f"low_vol={low_vol} (range={range_curr:.5f} vs MA×0.8={range_ma * self.VOL_FACTOR:.5f})",
        ]
        diag = {"main_value": ruch, "atr": atr}

        # Bramki: sesja nocna + niska zmienność
        if not noc:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Poza sesją nocną — scalper nieaktywny"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if not low_vol:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Zmienność za wysoka — to nie nocny range (ryzyko prawdziwego breakoutu)"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        # FADE: ruch w górę przekraczający próg → SHORT (i odwrotnie)
        if ruch > prog:
            sila = min(1.0, ruch / (atr * 2)) if atr > 0 else 0.5
            pewnosc = min(0.80, 0.55 + sila * 0.25)
            return self._buduj_raport(
                kierunek="SHORT", pewnosc=pewnosc,
                powody=[f"FADE wybicia w górę (ruch {ruch:+.4f} > prog {prog:.4f}) w nocnym range → SHORT"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if ruch < -prog:
            sila = min(1.0, abs(ruch) / (atr * 2)) if atr > 0 else 0.5
            pewnosc = min(0.80, 0.55 + sila * 0.25)
            return self._buduj_raport(
                kierunek="LONG", pewnosc=pewnosc,
                powody=[f"FADE wybicia w dół (ruch {ruch:+.4f} < -prog {prog:.4f}) w nocnym range → LONG"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=[f"Ruch ({ruch:+.4f}) poniżej progu fade ({prog:.4f})"] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
