"""
🛰️🌐💎 RADAR RYNKU — wielowymiarowy strażnik kontekstu (W-292, rozwój W-291).

WIZJA CEZARA: "Czy radar BTC sprawdza tylko cenę, czy też odpływ kapitału, wolumen,
dominację BTC, przepływ kapitału i inne ukryte/tajne rzeczy, które można skorelować
i zsynchronizować, by mieć większą pewność co do przyszłych ruchów?"

ODPOWIEDŹ W KODZIE: RadarBTC (W-291) patrzył TYLKO na momentum ceny BTC. To była
jedna flanka. RadarRynku dokłada trzy KAUZALNE, policzone z barów koszyka sygnały —
bez żadnego API (Cezar na telefonie, klucze nie podpięte). Wszystko z OHLCV, które
i tak mamy:

  1. BTC_TREND          — momentum lidera (z RadarBTC, [-1,+1]).
  2. BTC_DOMINANCJA     — siła względna BTC vs koszyk altów [-1,+1].
                          >0 = kapitał ucieka do BTC (risk-off dla altów),
                          <0 = alt-season (kapitał płynie w alty, risk-on).
                          Proxy dominacji BTC bez danych zewnętrznych: różnica
                          stóp zwrotu BTC vs średnia altów (Murphy: siła względna).
  3. PRZEPLYW_KAPITALU  — szerokość rynku (breadth) ważona momentum wolumenu [0,1].
                          Ułamek koszyka nad własną EMA × czy wolumen rośnie.
                          Wysoki = napływ kapitału (risk-on), niski = odpływ.
  4. STRES_KORELACJI    — średnia korelacja par w koszyku [0,1]. →1 = wszystko
                          leci razem (kaskada, "alty za BTC w dół") = NIEBEZPIECZNIE.
                          Detektor stresu rynkowego — Prawo XVI (korelacja mierzona).

Realizuje WIZJONER: W-071 (Transfer Entropy BTC→alty), W-085/086 (intermarket /
siła względna, Murphy BIB-002), W-016 (reżim korelacyjny). Czysta matematyka,
zero look-ahead (Prawo I): wszystko liczone z barów DO bieżącej świecy włącznie.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import math

from imperium.legiony.radar_btc import RadarBTC, _ema


@dataclass
class StanRynku:
    """Wielowymiarowy kontekst rynku — jeden ruch, wiele flank."""
    btc_trend: Optional[float] = None        # [-1,+1] momentum lidera
    dominacja: Optional[float] = None        # [-1,+1] siła BTC vs alty
    przeplyw: Optional[float] = None         # [0,1] breadth × wolumen
    stres_korelacji: Optional[float] = None  # [0,1] kaskada
    powody: List[str] = field(default_factory=list)

    def jako_wskazniki(self) -> Dict[str, float]:
        """Eksport do słownika wskaźników (inject do altów, neuronów, Praedy)."""
        out: Dict[str, float] = {}
        if self.btc_trend is not None:
            out["BTC_TREND"] = self.btc_trend
        if self.dominacja is not None:
            out["BTC_DOMINANCJA"] = self.dominacja
        if self.przeplyw is not None:
            out["PRZEPLYW_KAPITALU"] = self.przeplyw
        if self.stres_korelacji is not None:
            out["STRES_KORELACJI"] = self.stres_korelacji
        return out


def frakcja_korelacyjna(n: int, rho: Optional[float]) -> float:
    """
    🛡️ STER KORELACYJNY — czynnik skalujący rozmiar pozycji w koszyku N par tak,
    by zmienność portfela pozostała ~stała niezależnie od reżimu korelacji.

    Teoria portfela (NIE strojona stała): N pozycji o korelacji ρ ma zmienność
    ∝ √(1+(N-1)ρ) względem jednej. By sprowadzić ekspozycję do poziomu
    zdekorelowanego (ρ=0), skaluj każdą pozycję przez 1/√(1+(N-1)ρ).

      • ρ→0 (dywersyfikacja działa)  → 1.0 (pełny rozmiar, nie blokujemy potencjału)
      • ρ→1 (kaskada, wszystko razem) → 1/√N (tnij, bo to faktycznie jedna pozycja N×)

    n: liczba par w koszyku. rho: STRES_KORELACJI ∈ [0,1] (None → brak cięcia).
    """
    if n <= 1 or rho is None:
        return 1.0
    return 1.0 / math.sqrt(1.0 + (n - 1) * max(0.0, min(1.0, rho)))


def _zwroty(close: Sequence[float], okno: int) -> List[float]:
    """Ostatnie `okno` stóp zwrotu (proste), pomijając zerowe mianowniki."""
    c = [float(x) for x in close if x is not None]
    if len(c) < okno + 1:
        return []
    return [(c[i] - c[i - 1]) / c[i - 1]
            for i in range(len(c) - okno, len(c)) if c[i - 1] > 0]


def _korelacja(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    """Pearson dwóch serii równej długości. None gdy zerowa wariancja/za krótkie."""
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[-n:], b[-n:]
    ma = sum(a) / n
    mb = sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return None
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return max(-1.0, min(1.0, cov / (va ** 0.5 * vb ** 0.5)))


class RadarRynku:
    """
    Wielowymiarowy radar koszyka. Bezstanowy: dostaje surowe serie, zwraca StanRynku.

    Użycie (w backteście, przyczynowo — serie DO bieżącej świecy):
        radar = RadarRynku()
        stan = radar.skanuj(
            close_btc=[...],                       # zamknięcia BTC do teraz
            close_alty={"ETH":[...], "SOL":[...]}, # zamknięcia altów do teraz
            vol_alty={"ETH":[...], ...},           # wolumeny (opcjonalnie)
        )
        wskazniki.update(stan.jako_wskazniki())
    """

    def __init__(self, okno_rs: int = 20, okno_breadth: int = 30,
                 okno_korelacji: int = 30, ema_breadth: int = 20):
        if okno_rs < 5 or okno_breadth < 5 or okno_korelacji < 5:
            raise ValueError("okna muszą być ≥ 5 (statystyka, nie szum)")
        self.okno_rs = okno_rs
        self.okno_breadth = okno_breadth
        self.okno_korelacji = okno_korelacji
        self.ema_breadth = ema_breadth
        self._radar_btc = RadarBTC()

    def skanuj(self, close_btc: Sequence[float],
               close_alty: Dict[str, Sequence[float]],
               vol_alty: Optional[Dict[str, Sequence[float]]] = None) -> StanRynku:
        stan = StanRynku()

        # 1. BTC_TREND — momentum lidera (deleguje do RadarBTC).
        stan.btc_trend = self._radar_btc.trend(list(close_btc))

        # 2. BTC_DOMINANCJA — siła względna BTC vs średnia altów.
        zr_btc = _zwroty(close_btc, self.okno_rs)
        if zr_btc:
            ret_btc = sum(zr_btc)
            rety_alt = []
            for c in close_alty.values():
                z = _zwroty(c, self.okno_rs)
                if z:
                    rety_alt.append(sum(z))
            if rety_alt:
                ret_alt = sum(rety_alt) / len(rety_alt)
                # różnica stóp znormalizowana przez rozproszenie ruchów (tanh→[-1,1])
                skala = (abs(ret_btc) + abs(ret_alt)) or 1e-9
                stan.dominacja = max(-1.0, min(1.0,
                                               math.tanh((ret_btc - ret_alt) / skala)))
                if stan.dominacja > 0.3:
                    stan.powody.append("BTC dominuje (risk-off dla altów)")
                elif stan.dominacja < -0.3:
                    stan.powody.append("alt-season (kapitał płynie w alty)")

        # 3. PRZEPLYW_KAPITALU — breadth (ułamek nad EMA) × momentum wolumenu.
        serie = {"BTC": close_btc, **close_alty}
        nad_ema = 0
        liczone = 0
        for c in serie.values():
            cc = [float(x) for x in c if x is not None]
            if len(cc) < self.ema_breadth + 1:
                continue
            e = _ema(cc[-self.ema_breadth * 3:], self.ema_breadth)
            liczone += 1
            if cc[-1] > e:
                nad_ema += 1
        if liczone:
            breadth = nad_ema / liczone
            wol_mult = 1.0
            if vol_alty:
                rosnacy = 0
                wl = 0
                for v in vol_alty.values():
                    vv = [float(x) for x in v if x is not None]
                    if len(vv) < self.okno_breadth + 1:
                        continue
                    wl += 1
                    sredni_stary = sum(vv[-self.okno_breadth:-self.okno_breadth // 2]) or 1e-9
                    sredni_nowy = sum(vv[-self.okno_breadth // 2:])
                    if sredni_nowy > sredni_stary:
                        rosnacy += 1
                if wl:
                    wol_mult = 0.5 + 0.5 * (rosnacy / wl)  # [0.5,1.0]
            stan.przeplyw = max(0.0, min(1.0, breadth * wol_mult))
            if stan.przeplyw > 0.7:
                stan.powody.append("napływ kapitału (breadth wysoki)")
            elif stan.przeplyw < 0.3:
                stan.powody.append("odpływ kapitału (breadth niski)")

        # 4. STRES_KORELACJI — średnia |korelacja| par koszyka (Prawo XVI).
        zwroty_serie = []
        for c in serie.values():
            z = _zwroty(c, self.okno_korelacji)
            if len(z) >= 3:
                zwroty_serie.append(z)
        if len(zwroty_serie) >= 2:
            kor = []
            for i in range(len(zwroty_serie)):
                for j in range(i + 1, len(zwroty_serie)):
                    k = _korelacja(zwroty_serie[i], zwroty_serie[j])
                    if k is not None:
                        kor.append(abs(k))
            if kor:
                stan.stres_korelacji = sum(kor) / len(kor)
                if stan.stres_korelacji > 0.8:
                    stan.powody.append("KASKADA — wszystko leci razem (ryzyko)")

        return stan
