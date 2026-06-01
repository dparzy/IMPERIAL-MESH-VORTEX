"""
🏗️ IMV-EXP | EXP-05 ZwiadowcaSMC — wykrywacz struktur Smart Money

DLACZEGO W EXPLORATORES:
  Order Blocks, Fair Value Gaps i Break of Structure wymagają analizy SERII barów:
  - swing high/low (pivot) potrzebuje N barów w lewo i w prawo
  - Order Block to ostatnia świeca przeciwnego koloru przed impulsem (multi-bar)
  - FVG to luka między high[i-2] a low[i] (trzy bary)
  - BOS/MSS porównuje aktualne ekstrema z poprzednimi swingami
  Brama (jeden snapshot) tego nie policzy — stąd Exploratores.

ROLA UNIKALNA — MOST DO NEURONÓW SMC:
  EXP-05 nie tylko produkuje własny RaportZwiadowcy. Ma też metodę wstrzyknij(),
  która DODAJE wykryte strefy do dict `wskazniki`. Dzięki temu martwe dotąd neurony
  SMC-01 (OrderBlock), SMC-02 (FVG), SMC-03 (BOS) BUDZĄ SIĘ i interpretują strefy.

  Przepływ:
    bary → EXP-05.wstrzyknij(wskazniki) → wskazniki ma teraz BULL_OB_HIGH itp.
         → ustaw SMC-01/02/03 DOSTEPNY=True → Rój je odpala → interpretacja

  Jeden zwiadowca odblokowuje trzy neurony. To jest most, nie duplikat.

KLUCZE WSTRZYKIWANE (zgodne z struktura.py):
  BULL_OB_HIGH/LOW, BEAR_OB_HIGH/LOW         (SMC-01)
  BULL_FVG_HIGH/LOW, BEAR_FVG_HIGH/LOW       (SMC-02)
  BOS_BULLISH, BOS_BEARISH, MSS_BULLISH, MSS_BEARISH, CLOSE  (SMC-03)
"""

import time
from typing import List, Dict, Any, Optional, Tuple

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _swing_pivots(bary: List[Dict], lewo: int = 2, prawo: int = 2) -> Tuple[List[int], List[int]]:
    """
    Wykrywa swing high i swing low (fraktalne pivoty).
    Swing high w i: high[i] > high każdego z `lewo` barów w lewo i `prawo` w prawo.
    Zwraca (indeksy_swing_high, indeksy_swing_low).
    """
    sh, sl = [], []
    n = len(bary)
    for i in range(lewo, n - prawo):
        hi = bary[i]["high"]
        lo = bary[i]["low"]
        is_high = all(hi > bary[j]["high"] for j in range(i - lewo, i)) and \
                  all(hi > bary[j]["high"] for j in range(i + 1, i + prawo + 1))
        is_low = all(lo < bary[j]["low"] for j in range(i - lewo, i)) and \
                 all(lo < bary[j]["low"] for j in range(i + 1, i + prawo + 1))
        if is_high:
            sh.append(i)
        if is_low:
            sl.append(i)
    return sh, sl


def _wykryj_order_blocks(bary: List[Dict], impuls_prog: float = 1.5) -> Dict[str, Optional[float]]:
    """
    Order Block = ostatnia świeca przeciwnego koloru przed silnym impulsem.
    Bullish OB: ostatnia czerwona świeca przed serią zielonych (silny wzrost).
    Bearish OB: ostatnia zielona świeca przed serią czerwonych (silny spadek).

    impuls_prog = ile razy zakres impulsu musi przewyższać średni zakres.
    """
    out = {"BULL_OB_HIGH": None, "BULL_OB_LOW": None,
           "BEAR_OB_HIGH": None, "BEAR_OB_LOW": None}
    n = len(bary)
    if n < 5:
        return out

    zakresy = [b["high"] - b["low"] for b in bary]
    sredni_zakres = sum(zakresy) / len(zakresy) if zakresy else 0
    if sredni_zakres == 0:
        return out

    # Szukaj od najnowszych barów wstecz (najświeższy OB = najważniejszy)
    for i in range(n - 2, 1, -1):
        cur = bary[i]
        nast = bary[i + 1]
        cur_bull = cur["close"] >= cur["open"]
        impuls_zakres = abs(nast["close"] - nast["open"])

        # Bullish OB: bieżąca czerwona, następna silnie zielona
        if (out["BULL_OB_HIGH"] is None and not cur_bull
                and nast["close"] > nast["open"]
                and impuls_zakres > impuls_prog * sredni_zakres):
            out["BULL_OB_HIGH"] = cur["high"]
            out["BULL_OB_LOW"] = cur["low"]

        # Bearish OB: bieżąca zielona, następna silnie czerwona
        if (out["BEAR_OB_HIGH"] is None and cur_bull
                and nast["close"] < nast["open"]
                and impuls_zakres > impuls_prog * sredni_zakres):
            out["BEAR_OB_HIGH"] = cur["high"]
            out["BEAR_OB_LOW"] = cur["low"]

        if out["BULL_OB_HIGH"] is not None and out["BEAR_OB_HIGH"] is not None:
            break
    return out


def _wykryj_fvg(bary: List[Dict]) -> Dict[str, Optional[float]]:
    """
    Fair Value Gap (3-świecowy imbalance):
    Bullish FVG: low[i] > high[i-2] — luka w górę (między high sprzed 2 barów a low aktualnym).
    Bearish FVG: high[i] < low[i-2] — luka w dół.
    Zwraca najświeższą niewypełnioną lukę każdego typu.
    """
    out = {"BULL_FVG_HIGH": None, "BULL_FVG_LOW": None,
           "BEAR_FVG_HIGH": None, "BEAR_FVG_LOW": None}
    n = len(bary)
    if n < 3:
        return out

    for i in range(n - 1, 1, -1):
        h2 = bary[i - 2]["high"]
        l2 = bary[i - 2]["low"]
        hi = bary[i]["high"]
        lo = bary[i]["low"]

        # Bullish FVG: luka między high[i-2] a low[i]
        if out["BULL_FVG_LOW"] is None and lo > h2:
            out["BULL_FVG_HIGH"] = lo      # górna krawędź luki = low aktualnego
            out["BULL_FVG_LOW"] = h2       # dolna krawędź = high sprzed 2 barów

        # Bearish FVG: luka między low[i-2] a high[i]
        if out["BEAR_FVG_HIGH"] is None and hi < l2:
            out["BEAR_FVG_HIGH"] = l2
            out["BEAR_FVG_LOW"] = hi

        if out["BULL_FVG_LOW"] is not None and out["BEAR_FVG_HIGH"] is not None:
            break
    return out


def _wykryj_bos_mss(bary: List[Dict], lewo: int = 2, prawo: int = 2) -> Dict[str, bool]:
    """
    BOS (Break of Structure) + MSS (Market Structure Shift).
    BOS bullish: cena przebija ostatni swing high (kontynuacja w trendzie wzrostowym).
    BOS bearish: cena przebija ostatni swing low.
    MSS bullish: w trendzie SPADKOWYM cena przebija swing high (zmiana charakteru).
    MSS bearish: w trendzie WZROSTOWYM cena przebija swing low.
    """
    out = {"BOS_BULLISH": False, "BOS_BEARISH": False,
           "MSS_BULLISH": False, "MSS_BEARISH": False}
    sh, sl = _swing_pivots(bary, lewo, prawo)
    if len(sh) < 1 or len(sl) < 1:
        return out

    close = bary[-1]["close"]
    ostatni_sh = bary[sh[-1]]["high"]
    ostatni_sl = bary[sl[-1]]["low"]

    # Określ trend z kolejności ostatnich pivotów (uproszczone HH/HL vs LH/LL)
    trend_wzrostowy = None
    if len(sh) >= 2:
        trend_wzrostowy = bary[sh[-1]]["high"] > bary[sh[-2]]["high"]

    przebicie_gora = close > ostatni_sh
    przebicie_dol = close < ostatni_sl

    if przebicie_gora:
        if trend_wzrostowy is False:
            out["MSS_BULLISH"] = True   # był spadek, łamie strukturę w górę
        else:
            out["BOS_BULLISH"] = True   # kontynuacja wzrostu
    if przebicie_dol:
        if trend_wzrostowy is True:
            out["MSS_BEARISH"] = True   # był wzrost, łamie strukturę w dół
        else:
            out["BOS_BEARISH"] = True   # kontynuacja spadku
    return out


class ZwiadowcaSMC(ZwiadowcaElitarny):
    """
    🏗️ IMV-EXP | EXP-05 ZwiadowcaSMC
    Wykrywa Order Blocks, FVG, BOS/MSS z serii barów.
    Most do neuronów SMC-01/02/03 przez metodę wstrzyknij().
    """
    KLUCZ = "EXP-05"
    WSKAZNIK = "SMC_STRUCTURE"
    KATEGORIA = "S"
    WAGA = 9
    WYMAGA_BAROW = 20
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "Wykrywa struktury Smart Money (OB/FVG/BOS/MSS) z serii barów. "
        "Most do SMC-01/02/03 — wstrzykuje strefy do dict Bramy. "
        "Wymaga multi-bar pivotów, niemożliwe w jednym snapshocie."
    )

    PIVOT_LEWO = 2
    PIVOT_PRAWO = 2
    IMPULS_PROG = 1.5

    def _oblicz_strefy(self, bary: List[Dict]) -> Dict[str, Any]:
        """Liczy wszystkie strefy SMC i zwraca dict gotowy do wstrzyknięcia."""
        strefy: Dict[str, Any] = {}
        strefy.update(_wykryj_order_blocks(bary, self.IMPULS_PROG))
        strefy.update(_wykryj_fvg(bary))
        strefy.update(_wykryj_bos_mss(bary, self.PIVOT_LEWO, self.PIVOT_PRAWO))
        strefy["CLOSE"] = bary[-1]["close"]
        return strefy

    def wstrzyknij(self, wskazniki: dict, bary: List[Dict[str, Any]]) -> dict:
        """
        MOST DO NEURONÓW SMC.
        Dodaje wykryte strefy SMC do dict `wskazniki` (in-place + zwraca).
        Po wywołaniu SMC-01/02/03 mają komplet danych do interpretacji.

        Użycie w pipeline Legatusa:
            wskazniki = pobierz_wskazniki(symbol)      # z Bramy
            exp05.wstrzyknij(wskazniki, bary)          # dodaje strefy SMC
            sygnaly = roj.zbierz_sygnaly(wskazniki)    # SMC budzą się
        """
        ok, _ = self._waliduj_bary(bary)
        if not ok:
            return wskazniki
        wskazniki.update(self._oblicz_strefy(bary))
        return wskazniki

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()

        ok, komunikat = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(komunikat)

        strefy = self._oblicz_strefy(bary)
        close = strefy["CLOSE"]
        czas_ms = (time.time() - t0) * 1000
        pewnosc_metody = sum(1 for b in bary if b.get("close", 0) > 0) / len(bary)

        diagnostics = {"main_value": close}
        diagnostics.update({k: v for k, v in strefy.items() if v is not None})

        powody = []
        kierunek = "NEUTRAL"
        pewnosc = 0.0

        # MSS > BOS > strefy (hierarchia siły sygnału, zgodnie z SMC-03)
        if strefy["MSS_BULLISH"]:
            kierunek, pewnosc = "LONG", 0.90
            powody.append("MSS BULLISH: zmiana struktury w górę — instytucje akumulują")
        elif strefy["MSS_BEARISH"]:
            kierunek, pewnosc = "SHORT", 0.90
            powody.append("MSS BEARISH: zmiana struktury w dół — instytucje dystrybuują")
        elif strefy["BOS_BULLISH"]:
            kierunek, pewnosc = "LONG", 0.75
            powody.append("BOS BULLISH: przebicie Higher High — kontynuacja wzrostów")
        elif strefy["BOS_BEARISH"]:
            kierunek, pewnosc = "SHORT", 0.75
            powody.append("BOS BEARISH: przebicie Lower Low — kontynuacja spadków")
        else:
            # Brak BOS/MSS — sprawdź czy cena reaguje na strefę OB/FVG
            if (strefy["BULL_OB_LOW"] is not None
                    and strefy["BULL_OB_LOW"] <= close <= strefy["BULL_OB_HIGH"]):
                kierunek, pewnosc = "LONG", 0.70
                powody.append(f"Cena w Bullish OB [{strefy['BULL_OB_LOW']:.2f}-{strefy['BULL_OB_HIGH']:.2f}]")
            elif (strefy["BEAR_OB_LOW"] is not None
                    and strefy["BEAR_OB_LOW"] <= close <= strefy["BEAR_OB_HIGH"]):
                kierunek, pewnosc = "SHORT", 0.70
                powody.append(f"Cena w Bearish OB [{strefy['BEAR_OB_LOW']:.2f}-{strefy['BEAR_OB_HIGH']:.2f}]")
            else:
                powody.append("Brak aktywnej struktury SMC — cena poza strefami")

        return self._buduj_raport(
            kierunek=kierunek, pewnosc=pewnosc, powody=powody,
            diagnostics=diagnostics, n_barow=len(bary),
            pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
        )


def aktywuj_neurony_smc() -> List[str]:
    """
    Budzi neurony SMC-01/02/03 (DOSTEPNY=True).
    Wywołaj RAZ przy starcie pipeline, gdy ZwiadowcaSMC jest podpięty i wstrzykuje strefy.
    Bez EXP-05 te neurony pozostają wyciszone (brak danych = zero fałszywych NEUTRAL).

    Zwraca listę kluczy aktywowanych neuronów.
    """
    from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS
    aktywowane = []
    for klasa in (NeuronOrderBlock, NeuronFVG, NeuronBOS):
        klasa.DOSTEPNY = True
        klasa.POWOD_NIEDOSTEPNOSCI = ""
        aktywowane.append(klasa.KLUCZ)
    return aktywowane
