"""
Skaner Okazji (W-316) — łowca najlepszych setupów w CAŁYM koszyku.

DLA NOWICJUSZA: dotąd Imperium grało jak „N osobnych botów" — każda waluta osobno,
kapitał dzielony po równo. Wizja Cezara jest inna: JEDEN łowca, który patrzy na
WSZYSTKIE monety naraz, ocenia każdą okazję, układa ranking i bierze tylko KILKA
NAJLEPSZYCH. To różnica między „puszczeniem automatu na jednej walucie" a polowaniem
na najmocniejsze okazje w stadzie.

Skaner liczy dla każdej monety OCENĘ OKAZJI (opportunity score) z czterech składników,
wszystkie znormalizowane PRZEKROJOWO (cross-sectional z-score — czyli „jak ta moneta
wypada na tle reszty koszyka W TYM MOMENCIE", nie względem własnej historii):

  • momentum  — ROC (zmiana ceny w oknie); cross-sectional z-score = relative strength
                (kto jest liderem/maruderem koszyka). Źródło: cross-sectional momentum,
                FXEmpire; Moskowitz/Ooi/Pedersen 2012.
  • trend     — ADX (siła trendu); mocny trend = czystsza okazja (Wilder 1978).
  • wolumen   — VOLUME / VOLUME_MA20 (klimaks/zaangażowanie kapitału).
  • zmienność — ATR% (potencjał ruchu; za mała = nuda, ranking ją odsiewa).

KIERUNEK okazji wynika ze znaku momentum: lider rosnący → LONG, marauder spadający →
SHORT. Siła okazji = |momentum_z| + trend_z + wolumen_z + zmiennosc_z.

Skaner NIE handluje — tylko RANKUJE i zwraca TOP-N. Decyzję wejścia podejmuje dalej
Dyrygent (neurony, Pretorianie, filtry). To warstwa SELEKCJI ponad rojem — realizuje
„mało trade'ów wysokiej pewności": zamiast wchodzić wszędzie, wybieramy najmocniejsze.

Czysty OHLCV: wszystkie składniki liczalne z barów (przez Budowniczego). Brak danych
dla monety → pomijana (Prawo XV — nie zgadujemy).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class OkazjaRank:
    """Pojedyncza okazja w rankingu koszyka."""
    symbol: str
    score: float                 # łączna ocena okazji (im wyżej, tym lepiej)
    kierunek: str                # "LONG" / "SHORT"
    momentum: float              # surowy ROC (zmiana w oknie)
    skladniki: Dict[str, float] = field(default_factory=dict)  # z-score'y składników


def _zscore(wartosci: List[float]) -> List[float]:
    """Cross-sectional z-score; przy zerowej wariancji → same zera (brak przewagi)."""
    n = len(wartosci)
    if n == 0:
        return []
    srednia = sum(wartosci) / n
    war = sum((x - srednia) ** 2 for x in wartosci) / n
    if war < 1e-12:
        return [0.0] * n
    std = war ** 0.5
    return [(x - srednia) / std for x in wartosci]


@dataclass
class SkanerOkazji:
    """
    Skaner rankingujący okazje w koszyku (W-316).

    waga_momentum/trend/wolumen/zmiennosc: wagi składników oceny.
    min_adx:   próg odsiewający monety bez trendu (ADX < min_adx → poza rankingiem,
               bo to chop — zgodne z lekcją Filtra Asymetrii W-314).
    lookback:  ile barów wstecz liczyć ROC (≈24h na 4H przy 6).
    """
    waga_momentum: float = 1.0
    waga_trend: float = 0.8
    waga_wolumen: float = 0.6
    waga_zmiennosc: float = 0.4
    min_adx: float = 20.0
    lookback: int = 6

    def _roc(self, wsk: Dict[str, Any]) -> Optional[float]:
        closes = wsk.get("CLOSE_SERIES_20")
        if not closes or len(closes) < self.lookback + 1:
            return None
        baza = closes[-1 - self.lookback]
        if baza is None or abs(baza) < 1e-9:
            return None
        return (closes[-1] - baza) / baza

    def skanuj(self, wskazniki_per: Dict[str, Dict[str, Any]],
               top_n: Optional[int] = None) -> List[OkazjaRank]:
        """
        wskazniki_per: {symbol: wskazniki} — komplet wskaźników każdej monety w czasie T.
        Zwraca ranking malejąco wg score; top_n obcina do N najlepszych (None = wszystkie).
        """
        # 1. Zbierz surowe składniki dla monet z kompletem danych i trendem ≥ min_adx.
        surowe = []  # (symbol, roc, adx, vol_spike, atr_pct)
        for sym, wsk in wskazniki_per.items():
            roc = self._roc(wsk)
            adx = wsk.get("ADX_14")
            vol = wsk.get("VOLUME")
            vol_ma = wsk.get("VOLUME_MA20")
            atr = wsk.get("ATR_14")
            close = wsk.get("CLOSE")
            if None in (roc, adx, vol, vol_ma, atr, close):
                continue
            if vol_ma < 1e-9 or close < 1e-9:
                continue
            if adx < self.min_adx:        # chop → poza rankingiem (lekcja W-314)
                continue
            surowe.append((sym, roc, adx, vol / vol_ma, atr / close))

        if not surowe:
            return []

        # 2. Cross-sectional z-score każdego składnika (na tle koszyka W TYM momencie).
        roc_z = _zscore([r[1] for r in surowe])
        adx_z = _zscore([r[2] for r in surowe])
        vol_z = _zscore([r[3] for r in surowe])
        atr_z = _zscore([r[4] for r in surowe])

        # 3. Złóż ocenę. Kierunek ze znaku momentum; siła = |momentum| + trend + vol + zmienność.
        rank = []
        for i, (sym, roc, _adx, _vs, _ap) in enumerate(surowe):
            kierunek = "LONG" if roc >= 0 else "SHORT"
            score = (self.waga_momentum * abs(roc_z[i])
                     + self.waga_trend * adx_z[i]
                     + self.waga_wolumen * vol_z[i]
                     + self.waga_zmiennosc * atr_z[i])
            rank.append(OkazjaRank(
                symbol=sym, score=round(score, 4), kierunek=kierunek,
                momentum=round(roc, 4),
                skladniki={"momentum_z": round(roc_z[i], 3), "trend_z": round(adx_z[i], 3),
                           "wolumen_z": round(vol_z[i], 3), "zmiennosc_z": round(atr_z[i], 3)},
            ))

        rank.sort(key=lambda o: o.score, reverse=True)
        return rank[:top_n] if top_n is not None else rank
