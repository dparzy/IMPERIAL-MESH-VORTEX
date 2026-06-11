"""
🗡️💎 PRAEDA (Łupieżca) — TRYB ŁOWCY: kontrolowana, AUTO-skalowana chciwość (W-291).

WIZJA CEZARA: Imperium jako jeden organizm-łowca — skanuje monety, szuka OFIARY
(najlepszej okazji), sam dobiera agresję i łupi maksymalnie w potwierdzonych
momentach. Agresja NIE jest sztywnym parametrem — system DECYDUJE sam wg SIŁY OKAZJI.

RDZEŃ (unikat — "kontrolowana chciwość"): agresja rośnie TYLKO gdy WYGRYWASZ i jest
BEZPIECZNIE. Przeciwieństwo revenge-tradingu (który dokłada ryzyka, gdy przegrywasz).

`Okazjon` liczy SIŁĘ OKAZJI ∈ [0,1] z konfluencji wielu bram (wszystkie z tego, co
żywy pipeline dostarcza — brak danej bramy = neutralna, Prawo XV):
  • ZGODA — pewność agregatu + odsetek zgodnych neuronów (rdzeń przewagi)
  • REŻIM — TREND_STRONG (okazja kierunkowa) lub świeży master-switch
  • SENTYMENT — Fear&Greed / funding ekstremalny ZGODNY z kierunkiem (kontrarian)
  • ZDARZENIE — Augur prob ≥ 70% w tę stronę (wiatr fundamentalny)
  • BEZPIECZEŃSTWO (BRAMKI WETO, nie punkty): VPIN nietoksyczny, brak bańki/kaskady,
    brak blackoutu FOMC. Jeśli któraś czerwona → okazja NIEpotwierdzona (zero łupu).

AUTO-DECYZJA: z siły okazji wynikają mnożniki (ciągłe, capowane):
  mnoznik_lewara  = 1 + sila × WZMOCNIENIE_LEWARA   (twardy cap)
  mnoznik_rozmiaru= 1 + sila × WZMOCNIENIE_ROZMIARU (twardy cap)
  pyramiding      = sila ≥ PROG_PYRAMIDA (dokładanie do wygrywających, anti-martingale)

NIENARUSZALNA KLATKA: Praeda tylko AMPLIFIKUJE wewnątrz istniejących bezpieczników
(AOA 30%, Reguła 6% Eldera, breaker krzywej, cap MAX_DZWIGNIA, clamp 50% kapitału).
Wyłącza się w drawdownie (DD-control ≠ NORMAL → sila=0). Mierzona DSR/PBO jak wszystko.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("Praeda")

# Twarde capy wzmocnień (Praeda nigdy poza nie wyjdzie; MAX_DZWIGNIA i clamp 50%
# kapitału w Kalkulatorze są nadrzędne — to dodatkowy, miękki bezpiecznik).
WZMOCNIENIE_LEWARA = 1.0     # sila=1 → lewar ×2.0 (ale i tak cap MAX_DZWIGNIA)
WZMOCNIENIE_ROZMIARU = 1.0   # sila=1 → rozmiar ×2.0 (ale i tak clamp 50% kapitału)
PROG_OKAZJI = 0.55           # poniżej → okazja zwykła (mnożniki ≈1, brak łupu)
PROG_PYRAMIDA = 0.80         # tylko WYJĄTKOWE okazje uprawniają do dokupu


@dataclass
class SilaOkazji:
    """Werdykt Okazjona — siła + dlaczego (Prawo I: jawność)."""
    sila: float                 # 0.0–1.0 (0 = brak/niebezpiecznie)
    potwierdzona: bool          # czy bramki bezpieczeństwa czyste i sila ≥ próg
    mnoznik_lewara: float       # ×lewar (1.0 = bez zmian)
    mnoznik_rozmiaru: float     # ×rozmiar (1.0 = bez zmian)
    pyramiding: bool            # czy wolno dokładać do wygrywającej pozycji
    powody: list                # czytelne uzasadnienie


class Okazjon:
    """
    Wykrywacz okazji — liczy SilaOkazji z raportu Legatusa + wskaźników.

    Użycie (w Dyrygencie, tryb łowcy):
        ok = Okazjon().ocen(raport, wskazniki, kierunek, dd_normal=True)
        if ok.potwierdzona:
            lewar *= ok.mnoznik_lewara; rozmiar *= ok.mnoznik_rozmiaru
    """

    def __init__(self, prog_okazji: float = PROG_OKAZJI,
                 prog_pyramida: float = PROG_PYRAMIDA):
        self.prog_okazji = prog_okazji
        self.prog_pyramida = prog_pyramida

    def ocen(self, raport, wskazniki: dict, kierunek: str,
             dd_normal: bool = True) -> SilaOkazji:
        """
        raport: RaportLegatusa (pewnosc_agregatu, rezim, zgodnych/aktywnych neuronów).
        wskazniki: dict z Bramy/adapterów (VPIN, EVENT_*, FEAR_GREED_INDEX, FUNDING...).
        kierunek: LONG/SHORT planowanej pozycji.
        dd_normal: czy DD-control = NORMAL (False → Praeda śpi, sila=0).
        """
        powody = []
        # ── BRAMKI BEZPIECZEŃSTWA (weto — czerwona = zero łupu) ──────────────
        if not dd_normal:
            return self._brak("DD-control ≠ NORMAL — Praeda śpi (łup tylko gdy wygrywasz)")
        if wskazniki.get("EVENT_BLACKOUT"):
            return self._brak("BLACKOUT zdarzenia (FOMC) — bez łupu przed FED")
        vpin = wskazniki.get("VPIN_50")
        if vpin is not None and vpin > 0.7:
            return self._brak(f"VPIN {vpin:.2f} > 0.7 — toksyczny flow, ofiara to MY")
        if wskazniki.get("CASCADE_FLAG"):
            return self._brak("Kaskada likwidacji — nie wchodzimy w lawinę")
        # RADAR RYNKU (W-292): ekstremalny stres korelacji = cały koszyk leci razem
        # (dywersyfikacja znika, ryzyko systemowe). Chciwość w kaskadzie = samobójstwo.
        stres = wskazniki.get("STRES_KORELACJI")
        if stres is not None and stres > 0.85:
            return self._brak(f"STRES korelacji {stres:.2f} > 0.85 — koszyk w kaskadzie, brak dywersyfikacji")
        # RADAR BTC (W-291): BTC prowadzi rynek — gdy BTC mocno SPADA, alty lecą za
        # nim (lead-lag). LONG przeciw spadającemu BTC = pływanie pod prąd → weto.
        btc_trend = wskazniki.get("BTC_TREND")
        if btc_trend is not None:
            if kierunek == "LONG" and btc_trend < -0.6:
                return self._brak(f"RADAR BTC: BTC spada ({btc_trend:+.2f}) — alty lecą za nim, nie łapiemy spadającego noża")
            if kierunek == "SHORT" and btc_trend > 0.6:
                return self._brak(f"RADAR BTC: BTC mocno rośnie ({btc_trend:+.2f}) — nie shortujemy pod prąd lidera")

        # ── KONFLUENCJA (model BONUSOWY — więcej potwierdzeń STACKUJE siłę,
        #    nigdy nie uśrednia w dół; zgodna brama dodaje, niezgodna jest neutralna).
        powody = []

        # RDZEŃ: zgoda roju (pewność + odsetek zgodnych) × kierunkowość reżimu.
        pew = getattr(raport, "pewnosc_agregatu", 0.0) or 0.0
        akt = max(1, getattr(raport, "aktywnych_neuronow", 1))
        zgod = getattr(raport, "zgodnych_neuronow", 0) / akt
        zgoda = max(0.0, (pew - 0.55) / 0.45) * 0.5 + min(1.0, zgod / 0.6) * 0.5
        rezim = getattr(raport, "rezim", "NORMAL")
        rez = 1.0 if rezim == "TREND_STRONG" else (0.6 if rezim in ("NORMAL", "ON-CHAIN_BULLISH") else 0.3)
        baza = zgoda * (0.6 + 0.4 * rez)   # rdzeń ∈ [0,1]
        powody.append(f"rdzeń zgoda={zgoda:.2f}×reżim({rezim})={baza:.2f}")

        # BONUSY za każdą dodatkową ZGODNĄ bramę (kontekst wspierający — radar):
        sila = baza
        sent = self._sentyment(wskazniki, kierunek)
        if sent:
            sila += sent * 0.25
            powody.append(f"+sentyment {sent:.2f}")
        ev = self._zdarzenie(wskazniki, kierunek)
        if ev:
            sila += ev * 0.20
            powody.append(f"+Augur {ev:.2f}")
        btc = self._radar_btc(wskazniki, kierunek)
        if btc:
            sila += btc * 0.25
            powody.append(f"+RadarBTC {btc:.2f}")
        dom = self._dominacja(wskazniki, kierunek)
        if dom:
            sila += dom * 0.15
            powody.append(f"+Dominacja {dom:.2f}")
        sila = min(1.0, sila)

        potwierdzona = sila >= self.prog_okazji
        mn_lew = 1.0 + (sila * WZMOCNIENIE_LEWARA if potwierdzona else 0.0)
        mn_roz = 1.0 + (sila * WZMOCNIENIE_ROZMIARU if potwierdzona else 0.0)
        pyr = sila >= self.prog_pyramida
        if potwierdzona:
            powody.insert(0, f"🗡️ OKAZJA sila={sila:.2f} → lewar×{mn_lew:.2f} "
                             f"rozmiar×{mn_roz:.2f}{' +PYRAMIDA' if pyr else ''}")
        return SilaOkazji(round(sila, 3), potwierdzona, round(mn_lew, 3),
                          round(mn_roz, 3), pyr, powody)

    # ── pomocnicze ───────────────────────────────────────────────────────────

    @staticmethod
    def _sentyment(w: dict, kierunek: str):
        """Fear&Greed / funding ekstremalny ZGODNY z kierunkiem (kontrarian)."""
        fg = w.get("FEAR_GREED_INDEX")
        fund = w.get("FUNDING_RATE")
        wynik = None
        if fg is not None:
            if kierunek == "LONG" and fg <= 25:        # ekstremalny strach → kup
                wynik = max(wynik or 0, (25 - fg) / 25)
            elif kierunek == "SHORT" and fg >= 75:     # ekstremalna chciwość → sprzedaj
                wynik = max(wynik or 0, (fg - 75) / 25)
            else:
                wynik = 0.0
        if fund is not None:
            # tłum przepłacony po jednej stronie → kontrarian zgodny z nami
            if kierunek == "LONG" and fund < -0.0005:
                wynik = max(wynik or 0, min(1.0, -fund / 0.0015))
            elif kierunek == "SHORT" and fund > 0.0005:
                wynik = max(wynik or 0, min(1.0, fund / 0.0015))
            elif wynik is None:
                wynik = 0.0
        return wynik

    @staticmethod
    def _radar_btc(w: dict, kierunek: str):
        """
        Wiatr od lidera (BTC). BTC_TREND ∈ [-1,+1] (z RadarBTC):
        LONG zyskuje gdy BTC rośnie; SHORT gdy BTC spada. Niezgodny → 0 (neutralny;
        twarde weto na silny przeciwprąd jest osobno w bramkach bezpieczeństwa).
        """
        bt = w.get("BTC_TREND")
        if bt is None:
            return None
        return max(0.0, bt) if kierunek == "LONG" else max(0.0, -bt)

    @staticmethod
    def _dominacja(w: dict, kierunek: str):
        """
        BTC_DOMINANCJA ∈ [-1,+1] (RadarRynku). Dla ALTA: <0 = alt-season (kapitał
        płynie w alty) wspiera LONG; >0 = ucieczka do BTC wspiera SHORT alta. To
        proxy przepływu kapitału między BTC a koszykiem — wsparcie bocznej flanki.
        """
        dom = w.get("BTC_DOMINANCJA")
        if dom is None:
            return None
        return max(0.0, -dom) if kierunek == "LONG" else max(0.0, dom)

    @staticmethod
    def _zdarzenie(w: dict, kierunek: str):
        """Augur: prob_wzrostu zgodne z kierunkiem (≥70% dla LONG, ≤30% dla SHORT)."""
        prob = w.get("EVENT_PROB_WZROSTU")
        n = w.get("EVENT_N")
        if prob is None or n is None or n < 2:
            return None
        if kierunek == "LONG":
            return max(0.0, (prob - 50) / 50)
        return max(0.0, (50 - prob) / 50)

    @staticmethod
    def _brak(powod: str) -> SilaOkazji:
        return SilaOkazji(0.0, False, 1.0, 1.0, False, [f"🛑 {powod}"])
