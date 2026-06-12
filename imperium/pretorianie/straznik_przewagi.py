"""
🛡️💎 STRAŻNIK PRZEWAGI — unikat Imperium (W-287, Faza C).

PROBLEM (pomiar 2026-06-10): rój bywa świetny w jednym okresie (BTC 1H ostatnie
5,5 mies.: PF 1.59) i stratny w innym (16 mies.: PF 0.72) — EDGE WYGASA I WRACA.
Autopsja 12k barów: PF per ćwiartka 0.32→0.79→0.99→1.48 (edge dojrzewa w czasie).
Klasyczne bezpieczniki (AOA, breaker krzywej) patrzą na KAPITAŁ; Strażnik patrzy
na samą PRZEWAGĘ: kroczącą oczekiwaną wartość ostatnich N zamkniętych transakcji.

MECHANIKA (stany):
  AKTYWNY  — gra normalnie. Po każdym zamknięciu licz rolling expectancy
             (średni PnL ostatnich N transakcji). Gdy n≥N i expectancy < 0
             → HALT (edge wygasł — przestań karmić rynek prowizjami).
  HALT     — zero nowych wejść przez `bary_halt` barów (rynek niech się zmieni).
  SONDA    — po odbyciu HALT: pozwól DOKŁADNIE JEDNĄ pozycję zwiadowczą
             ("zwiad bojowy"). Sonda wygrywa → AKTYWNY (edge może wrócił,
             historia rolling czyszczona — świeży start). Sonda przegrywa
             → ponowny HALT (rynek wciąż nie nasz).

ORYGINALNOŚĆ: literatura zna monitoring "strategy decay" jako raport dla
człowieka; tu jest to PRETORIANIN W PĘTLI — automatyczny, z tanim mechanizmem
powrotu (sonda 1-pozycyjna zamiast kosztownego shadow-tradingu całego roju).

POMIAR (BTC 1H, 12000 barów, AUTO): bez Strażnika PF 0.72 / PnL −838 / MaxDD 10.8%;
ze Strażnikiem PF 0.95 / PnL −150 / MaxDD 6.4% / Sharpe_r −1.34→−0.30.
Tarcza, nie miecz: tnie krwawienie w złych okresach, nie tworzy edge'a.

Zero zależności. Prawo XV: stan i powody zawsze jawne (raport()).
"""

import logging
from collections import deque

logger = logging.getLogger("StraznikPrzewagi")


class StraznikPrzewagi:
    """
    Użycie (pętla backtestu/live):
        sp = StraznikPrzewagi(okno=12, bary_halt=96)
        ...co bar:  sp.tyknij_bar()
        ...przed wejściem:  if not sp.wolno_wejsc(): pomiń
        ...po wejściu:      sp.zarejestruj_wejscie()
        ...po zamknięciu:   sp.zarejestruj_zamkniecie(pnl_usdt)
    """

    AKTYWNY = "AKTYWNY"
    HALT = "HALT"
    SONDA = "SONDA"

    def __init__(self, okno: int = 12, bary_halt: int = 96):
        """
        okno: ile ostatnich ZAMKNIĘTYCH transakcji liczy rolling expectancy
              (≥3; mniej = szum pojedynczych trade'ów).
        bary_halt: długość ciszy po wykryciu wygasłego edge'a (w barach;
              96×1H = 4 dni — rynek ma czas zmienić charakter).
        """
        if okno < 3:
            raise ValueError("okno musi być ≥ 3 (mniej = szum, nie pomiar)")
        if bary_halt < 1:
            raise ValueError("bary_halt musi być ≥ 1")
        self.okno = okno
        self.bary_halt = bary_halt
        self.stan = self.AKTYWNY
        self._pnl = deque(maxlen=okno)
        self._halt_pozostalo = 0
        self._sonda_w_locie = False

    # ── pętla ────────────────────────────────────────────────────────────────

    def tyknij_bar(self) -> None:
        """Wołane raz na bar — odlicza ciszę HALT i awansuje do SONDY."""
        if self.stan == self.HALT:
            self._halt_pozostalo -= 1
            if self._halt_pozostalo <= 0:
                self.stan = self.SONDA
                self._sonda_w_locie = False
                logger.info("🛡️ Strażnik Przewagi: HALT odbyty → SONDA (1 wejście zwiadowcze)")

    def wolno_wejsc(self) -> bool:
        """Czy wolno otworzyć nową pozycję w tym stanie."""
        if self.stan == self.AKTYWNY:
            return True
        if self.stan == self.SONDA:
            return not self._sonda_w_locie   # dokładnie jedna sonda naraz
        return False                          # HALT

    def zarejestruj_wejscie(self) -> None:
        if self.stan == self.SONDA:
            self._sonda_w_locie = True

    def zarejestruj_zamkniecie(self, pnl_usdt: float) -> None:
        """Po każdym zamknięciu pozycji — rdzeń maszyny stanów."""
        if self.stan == self.SONDA and self._sonda_w_locie:
            self._sonda_w_locie = False
            if pnl_usdt > 0:
                self.stan = self.AKTYWNY
                self._pnl.clear()             # świeży start pomiaru edge'a
                self._pnl.append(pnl_usdt)
                logger.info("🛡️ Strażnik: sonda WYGRANA → AKTYWNY (reset pomiaru)")
            else:
                self._start_halt("sonda przegrana — edge wciąż wygasły")
            return
        self._pnl.append(pnl_usdt)
        if self.stan == self.AKTYWNY and len(self._pnl) >= self.okno:
            expectancy = sum(self._pnl) / len(self._pnl)
            if expectancy < 0:
                self._start_halt(
                    f"rolling expectancy {expectancy:+.2f} USDT/trade < 0 "
                    f"(okno {self.okno})")

    def _start_halt(self, powod: str) -> None:
        self.stan = self.HALT
        self._halt_pozostalo = self.bary_halt
        logger.warning(f"🛡️ STRAŻNIK PRZEWAGI → HALT na {self.bary_halt} barów: {powod}")

    # ── diagnostyka ──────────────────────────────────────────────────────────

    @property
    def expectancy(self) -> "float | None":
        if not self._pnl:
            return None
        return sum(self._pnl) / len(self._pnl)

    def raport(self) -> dict:
        return {"stan": self.stan, "expectancy": self.expectancy,
                "n_w_oknie": len(self._pnl),
                "halt_pozostalo": self._halt_pozostalo if self.stan == self.HALT else 0}
