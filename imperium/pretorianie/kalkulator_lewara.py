"""
Kalkulator Lewara — matematyka przeżycia.

Przed każdą pozycją lewarowaną MUSI policzyć:
  - dokładną cenę likwidacji
  - stop-loss (min 50% drogi do likwidacji)
  - take-profit (min R:R 1:2)
  - rozmiar pozycji (max 2% kapitału)
  - dźwignię dynamiczną (z pewności agregatu)

Zasada Żelazna: jeśli cokolwiek nie przejdzie checklist → WETO.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("KalkulatorLewara")

OPLATA_UTRZYMANIA = 0.005  # 0.5% — typowe dla Binance/MEXC
MAX_DZWIGNIA = 20
MAX_RYZYKO = 0.02           # 2% kapitału max per trade
MIN_RR = 2.0                # minimum Risk:Reward 1:2
MAX_DRAWDOWN_STOP = 0.30    # AOA: "nigdy nie kochaj pozycji" — 30% obsunięcia = STOP

# ── Volatility Targeting (wizja W-059) ───────────────────────────────────────
# Standard instytucjonalny: rozmiar pozycji ∝ vol_target / vol_realized.
# Gdy rynek bardziej zmienny niż cel → przytnij pozycję; spokojniejszy → powiększ
# (w bezpiecznych granicach). vol_realized podaje się jako annualizowana vol —
# idealnie YANG_ZHANG_20 z Bramy (W-055), ta sama skala co cel poniżej.
VOL_TARGET_DEFAULT = 0.60   # 60% annualizowanej zmienności — typowy cel portfela krypto
SKALA_VOL_MIN = 0.25        # nie schodź poniżej 1/4 bazowego rozmiaru
SKALA_VOL_MAX = 1.50        # nie powiększaj ponad 1.5× (ostrożność > chciwość)


@dataclass
class BezpiecznikKapitalu:
    """
    Bezpiecznik AOA (reguła W-028) — twardy circuit-breaker portfela.

    Śledzi szczyt kapitału. Gdy bieżący kapitał spadnie o MAX_DRAWDOWN_STOP
    od szczytu → bezpiecznik się przepala (tripped) i blokuje WSZYSTKIE
    nowe pozycje aż do ręcznego resetu przez Komendanta.

    Użycie:
        bezp = BezpiecznikKapitalu(kapital_startowy=5000)
        bezp.aktualizuj(4200)        # po serii strat
        if bezp.przepalony: ...      # blokada wejść
    """
    kapital_startowy: float
    kapital_szczyt: float = 0.0
    kapital_biezacy: float = 0.0
    przepalony: bool = False

    def __post_init__(self):
        if self.kapital_szczyt <= 0:
            self.kapital_szczyt = self.kapital_startowy
        if self.kapital_biezacy <= 0:
            self.kapital_biezacy = self.kapital_startowy

    def aktualizuj(self, kapital_biezacy: float) -> None:
        """Po każdym zamknięciu pozycji — zaktualizuj stan kapitału."""
        self.kapital_biezacy = kapital_biezacy
        if kapital_biezacy > self.kapital_szczyt:
            self.kapital_szczyt = kapital_biezacy
        if self.drawdown >= MAX_DRAWDOWN_STOP:
            self.przepalony = True
            logger.warning(
                f"🛑 BEZPIECZNIK AOA PRZEPALONY! Drawdown {self.drawdown:.1%} "
                f"≥ {MAX_DRAWDOWN_STOP:.0%}. Wszystkie pozycje zablokowane."
            )

    @property
    def drawdown(self) -> float:
        """Obsunięcie od szczytu (0.0–1.0)."""
        if self.kapital_szczyt <= 0:
            return 0.0
        return max(0.0, (self.kapital_szczyt - self.kapital_biezacy) / self.kapital_szczyt)

    def reset(self) -> None:
        """Ręczny reset przez Komendanta po przeglądzie (Lex Paenitentiae)."""
        self.przepalony = False
        self.kapital_szczyt = self.kapital_biezacy
        logger.info("✅ Bezpiecznik AOA zresetowany ręcznie. Nowy szczyt = bieżący kapitał.")


@dataclass
class BezpiecznikKrzywejKapitalu:
    """
    Equity-Curve Circuit Breaker (wizja W-062) — meta-poziomowa ochrona anti-tail.

    DLA NOWICJUSZA: ten bezpiecznik traktuje WŁASNĄ krzywą kapitału roju jak
    instrument. Liczy średnią kroczącą (MA = Moving Average) na punktach kapitału
    i pilnuje obsunięcia (drawdown) od szczytu. Ma trzy stany:

      • NORMAL  — kapitał powyżej MA i drawdown mały  → grasz pełnym rozmiarem (×1.0)
      • REDUCED — kapitał poniżej MA LUB drawdown umiarkowany → rozmiar ×0.5
      • HALT    — drawdown duży (≥ prog_dd_halt) → blokada WSZYSTKICH nowych wejść

    Powrót: gdy kapitał wróci ponad MA i drawdown spadnie poniżej prog_dd_reduced
    → NORMAL. Z HALT wychodzimy dopiero gdy drawdown spadnie poniżej prog_dd_reduced
    (HISTEREZA — nie migocz na granicy progu HALT).

    GDZIE SIĘ PLASUJE: ten bezpiecznik siedzi PONAD twardym BezpiecznikKapitalu
    (reguła AOA W-028, twardy STOP przy 30% obsunięcia). Jest WARSTWĄ MIĘKSZĄ,
    reagującą WCZEŚNIEJ: najpierw przycina rozmiar (REDUCED), potem wstrzymuje
    wejścia (HALT przy 20%), zanim AOA przepali się twardo przy 30%. To realizacja
    Prawa XV (ochrona potencjału) w kodzie.

    ŹRÓDŁO: ⚠️ to ugruntowana praktyka system-tradingu (traktowanie equity curve
    jak instrumentu + MA filter), NIE pojedyncza recenzowana publikacja peer-review.

    Użycie:
        br = BezpiecznikKrzywejKapitalu(okno_ma=20)
        br.aktualizuj(4200)              # po każdym zamknięciu pozycji
        rozmiar *= br.frakcja_pozycji()  # NORMAL=1.0, REDUCED=0.5, HALT=0.0
        if br.halt: ...                  # blokada wejść w checklist
    """
    okno_ma: int = 20
    prog_dd_reduced: float = 0.10
    prog_dd_halt: float = 0.20
    frakcja_reduced: float = 0.5
    historia_kapitalu: list = None
    kapital_szczyt: float = 0.0
    stan: str = "NORMAL"

    def __post_init__(self):
        if self.historia_kapitalu is None:
            self.historia_kapitalu = []

    def aktualizuj(self, kapital_biezacy: float) -> str:
        """Po każdym zamknięciu pozycji — dolicz punkt do krzywej, przelicz stan."""
        self.historia_kapitalu.append(kapital_biezacy)
        if kapital_biezacy > self.kapital_szczyt:
            self.kapital_szczyt = kapital_biezacy

        dd = self.drawdown
        ma = self.ma_kapitalu
        poprzedni = self.stan

        if dd >= self.prog_dd_halt:
            nowy = "HALT"
        elif self.stan == "HALT" and dd >= self.prog_dd_reduced:
            # HISTEREZA: z HALT wychodzimy dopiero gdy dd < prog_dd_reduced
            nowy = "HALT"
        elif dd >= self.prog_dd_reduced or (ma is not None and kapital_biezacy < ma):
            nowy = "REDUCED"
        else:
            nowy = "NORMAL"

        self.stan = nowy
        if nowy != poprzedni:
            logger.warning(
                f"🔻 BREAKER KRZYWEJ: {poprzedni} → {nowy} "
                f"(equity DD {dd:.1%}, MA={ma if ma is None else round(ma, 2)}, "
                f"kapitał={kapital_biezacy:.2f})"
            )
        return nowy

    @property
    def drawdown(self) -> float:
        """Obsunięcie od szczytu krzywej kapitału (0.0–1.0)."""
        if self.kapital_szczyt <= 0 or not self.historia_kapitalu:
            return 0.0
        return max(0.0, (self.kapital_szczyt - self.historia_kapitalu[-1]) / self.kapital_szczyt)

    @property
    def ma_kapitalu(self):
        """Średnia krocząca z ostatnich okno_ma punktów; None gdy za mało danych."""
        if len(self.historia_kapitalu) < self.okno_ma:
            return None
        okno = self.historia_kapitalu[-self.okno_ma:]
        return sum(okno) / len(okno)

    def frakcja_pozycji(self) -> float:
        """Mnożnik rozmiaru pozycji: NORMAL=1.0, REDUCED=frakcja_reduced, HALT=0.0."""
        if self.stan == "HALT":
            return 0.0
        if self.stan == "REDUCED":
            return self.frakcja_reduced
        return 1.0

    @property
    def halt(self) -> bool:
        """Czy bezpiecznik wstrzymuje nowe wejścia (stan HALT)."""
        return self.stan == "HALT"

    def reset(self) -> None:
        """Reset stanu i krzywej (np. po przeglądzie Komendanta)."""
        self.historia_kapitalu = []
        self.kapital_szczyt = 0.0
        self.stan = "NORMAL"
        logger.info("✅ Breaker krzywej kapitału zresetowany.")


@dataclass
class PlanPozycji:
    symbol: str
    kierunek: str              # LONG / SHORT
    cena_wejscia: float
    dzwignia: int
    cena_likwidacji: float
    stop_loss: float
    take_profit: float
    rozmiar_usdt: float        # wielkość pozycji w USDT (po skalowaniu vol-targeting)
    ryzyko_usdt: float         # max strata w USDT
    rr_ratio: float
    bufor_likwidacji_pct: float  # ile % między SL a likwidacją (bezpieczeństwo)
    checklist_ok: bool
    powod_veto: str            # "" jeśli checklist OK
    skala_vol: float = 1.0     # mnożnik volatility-targeting (W-059); 1.0 = brak skalowania
    frakcja_breaker: float = 1.0  # mnożnik breakera krzywej kapitału (W-062); 1.0=NORMAL, 0.5=REDUCED, 0.0=HALT


class KalkulatorLewara:
    """
    Użycie:
        kalk = KalkulatorLewara()
        plan = kalk.policz("BTCUSDT", "LONG", 100_000, dzwignia=10,
                            kapital_usdt=5000, pewnosc=0.78, rezim="TREND_STRONG")
        if plan.checklist_ok:
            # wyślij zlecenia do giełdy
    """

    def policz(self, symbol: str, kierunek: str, cena_wejscia: float,
               dzwignia: int, kapital_usdt: float,
               pewnosc: float = 0.7, rezim: str = "NORMAL",
               pretorianie_ok: bool = True,
               bezpiecznik: "BezpiecznikKapitalu | None" = None,
               vol_realized: "float | None" = None,
               vol_target: float = VOL_TARGET_DEFAULT,
               breaker_krzywej: "BezpiecznikKrzywejKapitalu | None" = None) -> PlanPozycji:

        kierunek = kierunek.upper()
        assert kierunek in ("LONG", "SHORT"), "kierunek musi być LONG lub SHORT"

        # 1. Dźwignia dynamiczna (jeśli nie podana = auto)
        if dzwignia <= 0:
            dzwignia = self.auto_dzwignia(pewnosc, rezim)

        # 2. Cena likwidacji
        likwidacja = self._likwidacja(cena_wejscia, kierunek, dzwignia)

        # 3. Stop-loss (50% drogi do likwidacji)
        stop_loss = self._stop_loss(cena_wejscia, likwidacja, kierunek)

        # 4. Bufor bezpieczeństwa
        odl_sl_od_lik = abs(likwidacja - stop_loss) / abs(cena_wejscia - likwidacja)
        bufor_pct = round(odl_sl_od_lik * 100, 1)

        # 5. Rozmiar pozycji (max ryzyko)
        stop_pct = abs(cena_wejscia - stop_loss) / cena_wejscia
        ryzyko_usdt = kapital_usdt * MAX_RYZYKO
        rozmiar_usdt = ryzyko_usdt / stop_pct if stop_pct > 0 else 0

        # 5b. Volatility Targeting (W-059): przeskaluj rozmiar do celu zmienności.
        # Wysoka realized vol → mniejsza pozycja; spokojny rynek → większa (w granicach).
        # Brak vol_realized → skala 1.0 (kompatybilność wsteczna, zero zmian).
        skala_vol = self.skala_vol_targeting(vol_realized, vol_target)
        rozmiar_usdt *= skala_vol

        # 5c. Equity-Curve Circuit Breaker (W-062): meta-poziom anti-tail.
        # REDUCED → ×0.5 rozmiaru; HALT → blokada w checklist (rozmiar nieistotny).
        # Brak breakera → frakcja 1.0 (kompatybilność wsteczna, zero zmian).
        frakcja_breaker = breaker_krzywej.frakcja_pozycji() if breaker_krzywej is not None else 1.0
        if frakcja_breaker > 0.0:
            rozmiar_usdt *= frakcja_breaker

        # 6. Take-profit (min R:R 1:2)
        ruch_sl = abs(cena_wejscia - stop_loss)
        if kierunek == "LONG":
            take_profit = cena_wejscia + ruch_sl * MIN_RR
        else:
            take_profit = cena_wejscia - ruch_sl * MIN_RR

        rr_ratio = MIN_RR  # zawsze minimum 2:1

        # 7. Checklist
        ok, powod = self._checklist(
            kierunek, dzwignia, pewnosc, rezim,
            pretorianie_ok, bufor_pct, rozmiar_usdt, kapital_usdt,
            bezpiecznik, breaker_krzywej
        )

        return PlanPozycji(
            symbol=symbol,
            kierunek=kierunek,
            cena_wejscia=cena_wejscia,
            dzwignia=dzwignia,
            cena_likwidacji=round(likwidacja, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            rozmiar_usdt=round(rozmiar_usdt, 2),
            ryzyko_usdt=round(ryzyko_usdt, 2),
            rr_ratio=rr_ratio,
            bufor_likwidacji_pct=bufor_pct,
            checklist_ok=ok,
            powod_veto=powod,
            skala_vol=round(skala_vol, 4),
            frakcja_breaker=round(frakcja_breaker, 4),
        )

    # ── Volatility Targeting (W-059) ────────────────────────────────────────────

    @staticmethod
    def skala_vol_targeting(vol_realized: "float | None",
                            vol_target: float = VOL_TARGET_DEFAULT) -> float:
        """
        Mnożnik rozmiaru = vol_target / vol_realized, przycięty do [MIN, MAX].

        vol_realized: annualizowana realized vol (np. YANG_ZHANG_20). None/≤0 →
                      brak danych → skala 1.0 (neutralnie, Prawo XV: bez halucynacji).
        Zwraca skalę w [SKALA_VOL_MIN, SKALA_VOL_MAX].
        """
        if vol_realized is None or vol_realized <= 0 or vol_target <= 0:
            return 1.0
        skala = vol_target / vol_realized
        return max(SKALA_VOL_MIN, min(SKALA_VOL_MAX, skala))

    # ── Wzory ──────────────────────────────────────────────────────────────────

    def _likwidacja(self, cena: float, kierunek: str, dzwignia: int) -> float:
        if kierunek == "LONG":
            return cena * (1 - 1/dzwignia + OPLATA_UTRZYMANIA)
        else:
            return cena * (1 + 1/dzwignia - OPLATA_UTRZYMANIA)

    def _stop_loss(self, cena: float, likwidacja: float, kierunek: str) -> float:
        """Stop-loss w połowie drogi do likwidacji."""
        if kierunek == "LONG":
            return cena - (cena - likwidacja) * 0.5
        else:
            return cena + (likwidacja - cena) * 0.5

    # ── Checklist Pretorianów ──────────────────────────────────────────────────

    def _checklist(self, kierunek: str, dzwignia: int, pewnosc: float,
                   rezim: str, pretorianie_ok: bool,
                   bufor_pct: float, rozmiar: float, kapital: float,
                   bezpiecznik: "BezpiecznikKapitalu | None" = None,
                   breaker_krzywej: "BezpiecznikKrzywejKapitalu | None" = None):
        if breaker_krzywej is not None and breaker_krzywej.halt:
            return False, (f"🛑 BREAKER KRZYWEJ: HALT — equity DD "
                           f"{breaker_krzywej.drawdown:.1%} ≥ "
                           f"{breaker_krzywej.prog_dd_halt:.0%}, nowe wejścia wstrzymane")
        if bezpiecznik is not None and bezpiecznik.przepalony:
            return False, (f"🛑 BEZPIECZNIK AOA przepalony — drawdown "
                           f"{bezpiecznik.drawdown:.1%} ≥ {MAX_DRAWDOWN_STOP:.0%}. "
                           f"Wymaga ręcznego resetu Komendanta.")
        if not pretorianie_ok:
            return False, "Pretorianie nałożyli VETO (warunki zewnętrzne)"
        if rezim == "PANIC":
            return False, "Reżim PANIC — zero pozycji lewarowanych"
        if dzwignia > MAX_DZWIGNIA:
            return False, f"Dźwignia {dzwignia}× przekracza max {MAX_DZWIGNIA}×"
        if pewnosc < 0.55:
            return False, f"Zbyt słaby sygnał: {pewnosc:.0%} < 55%"
        if bufor_pct < 20:
            return False, f"Bufor do likwidacji zbyt mały: {bufor_pct:.1f}% < 20%"
        if rozmiar > kapital * 0.5:
            return False, f"Pozycja zbyt duża vs kapitał ({rozmiar:.0f} > 50% kapitału)"
        return True, ""

    # ── Automatyczna dźwignia ──────────────────────────────────────────────────

    @staticmethod
    def auto_dzwignia(pewnosc: float, rezim: str = "NORMAL") -> int:
        if pewnosc < 0.55:   baza = 0
        elif pewnosc < 0.65: baza = 2
        elif pewnosc < 0.75: baza = 5
        elif pewnosc < 0.85: baza = 10
        elif pewnosc < 0.92: baza = 15
        else:                baza = 20

        korektor = {
            "VOLATILE": 0.5, "PANIC": 0.1, "RANGING": 0.7,
            "TREND_STRONG": 1.2, "NORMAL": 1.0, "ON-CHAIN_BULLISH": 1.1,
        }.get(rezim, 1.0)

        return min(max(int(baza * korektor), 1), MAX_DZWIGNIA)

    def drukuj_plan(self, plan: PlanPozycji):
        status = "✅ CHECKLIST OK" if plan.checklist_ok else f"⛔ VETO: {plan.powod_veto}"
        print(f"""
╔══════════════════════════════════════════════════════╗
║  PLAN POZYCJI: {plan.symbol} {plan.kierunek} ×{plan.dzwignia}
╠══════════════════════════════════════════════════════╣
║  Cena wejścia:   {plan.cena_wejscia:>12.2f} USDT
║  Stop-Loss:      {plan.stop_loss:>12.2f} USDT
║  Take-Profit:    {plan.take_profit:>12.2f} USDT
║  Likwidacja:     {plan.cena_likwidacji:>12.2f} USDT
║  Bufor do lik:   {plan.bufor_likwidacji_pct:>11.1f}%
║──────────────────────────────────────────────────────
║  Rozmiar:        {plan.rozmiar_usdt:>12.2f} USDT (vol×{plan.skala_vol:.2f})
║  Max ryzyko:     {plan.ryzyko_usdt:>12.2f} USDT
║  R:R ratio:      1:{plan.rr_ratio:.1f}
╠══════════════════════════════════════════════════════╣
║  {status}
╚══════════════════════════════════════════════════════╝""")


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    kalk = KalkulatorLewara()

    print("=== Kalkulator Lewara — Demo ===\n")

    # BTC LONG, 10×, kapitał 5000 USDT
    plan = kalk.policz(
        symbol="BTCUSDT", kierunek="LONG",
        cena_wejscia=100_000, dzwignia=10,
        kapital_usdt=5_000, pewnosc=0.78,
        rezim="TREND_STRONG"
    )
    kalk.drukuj_plan(plan)

    # ETH SHORT, auto-dźwignia (pewność 0.82), reżim VOLATILE
    plan2 = kalk.policz(
        symbol="ETHUSDT", kierunek="SHORT",
        cena_wejscia=3_500, dzwignia=0,  # 0 = auto
        kapital_usdt=5_000, pewnosc=0.82,
        rezim="VOLATILE"
    )
    kalk.drukuj_plan(plan2)

    # Demo bezpiecznika AOA (W-028): kapitał spada z 5000 do 3400 (-32%)
    print("\n=== Bezpiecznik AOA (reguła 30%) ===")
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(4_500)   # -10% — ok
    print(f"Po -10%: drawdown={bezp.drawdown:.1%}, przepalony={bezp.przepalony}")
    bezp.aktualizuj(3_400)   # -32% od szczytu — STOP
    print(f"Po -32%: drawdown={bezp.drawdown:.1%}, przepalony={bezp.przepalony}")

    plan3 = kalk.policz(
        symbol="BTCUSDT", kierunek="LONG",
        cena_wejscia=100_000, dzwignia=10,
        kapital_usdt=3_400, pewnosc=0.85,
        rezim="TREND_STRONG", bezpiecznik=bezp
    )
    kalk.drukuj_plan(plan3)
    assert not plan3.checklist_ok, "Bezpiecznik powinien zablokować!"
    print("✅ Bezpiecznik AOA poprawnie zablokował wejście po 32% obsunięciu")
