"""
🏛️ NAMIESTNIK — Regime-Aware Gating Network (Meta-Controller).

Architektura inspirowana:
  • Volatility-Adaptive MoE (arXiv:2508.02686, 2025) — reżim przełącza eksperta
  • Adaptive Regime-Aware Prediction (arXiv:2603.19136) — autoencoder + RL dla reżimu
  • Meta-Learning Optimal Mixture (arXiv:2505.03659) — MAML dynamiczna selekcja
  • MRC/Shapley (arXiv:2605.24490) — wagi dynamiczne z atrybutem Shapleya (Faza 2)

Rola w łańcuchu decyzyjnym:
    bary
      │
      ▼
    klasyfikuj_rezim() → rezim
      │
      ▼
  [NAMIESTNIK]  ◄──── Punkt adaptacji: reżim → {tryb, wagi, lewar, próg, pas}
      │
      ▼
    Legatus + Klucznik → Kalkulator → pozycja

FAZA 1 (bieżąca): Deterministyczna tablica reżim→parametry.
FAZA 2 (Shapley): Online learning wag z arXiv:2605.24490 (MRC).
FAZA 3 (MAML):    Meta-learning selekcji strategii z arXiv:2505.03659.

Prawo I: Namiestnik NIE liczy wskaźników. Dostaje gotowy reżim od klasyfikatora.
Prawo XV: Gdy rezim=PANIC lub czy_grac=False → cisza (świadoma, nie błąd).
Prawo XVI: Parametry taablicy mają tabele dowodową w docs/MANIFEST_KODU.md.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger("Namiestnik")


@dataclass
class UstawieniaRezimu:
    """
    Kompletny zestaw parametrów dla jednego reżimu rynku.

    tryb:           jak Dyrygent używa Klucznika ('agregat' / 'filtr' / 'strategia')
    lewar_factor:   mnożnik dźwigni względem auto_dzwignia (0.3 = defensywnie)
    prog_pewnosci:  minimalny próg pewności agregatu do wejścia w pozycję
    czy_grac:       False = stój z boku (RANGING, PANIC) — świadoma cisza
    wagi_override:  opcjonalne nadpisanie kategorycznych wag w WAGI_REZIMU
    opis:           czytelny powód dla DecyzjaCyklu.powod
    """
    tryb: str
    lewar_factor: float
    prog_pewnosci: float
    czy_grac: bool
    wagi_override: Optional[Dict[str, float]] = None
    opis: str = ""

    def __post_init__(self):
        assert self.tryb in ("agregat", "filtr", "strategia"), \
            f"Nieznany tryb Namiestnika: {self.tryb}"
        assert 0.0 < self.lewar_factor <= 2.0, \
            f"lewar_factor poza zakresem: {self.lewar_factor}"
        assert 0.5 <= self.prog_pewnosci <= 1.0, \
            f"prog_pewnosci poza zakresem: {self.prog_pewnosci}"


# ─── Tablica reżimów (Faza 1 — deterministyczna) ─────────────────────────────
#
# Dowody empiryczne (Prawo XVI — Prawo XVI: 12 backtestów 2026-06-02):
#   TREND_STRONG  → filtr +43% ETH 1D (tryb filtr potwierdził przewagę nad agregatem)
#   RANGING       → agregat daje za dużo sygnałów, prog 0.72 redukuje szum
#   VOLATILE      → strategia przełącza na Klucznik (breakout/volatility strategies)
#   PANIC         → stop (2026-06-02: zawsze trap wejście w PANIC)
#   NORMAL        → agregat + lewar 0.8 (ostrożnie, brak pewności reżimu)
#
# lewar_factor mnoży wynik auto_dzwignia(pewnosc, rezim) z KalkulatorLewara.
# prog_pewnosci zastępuje Dyrygent.min_pewnosc dla tego reżimu.
_TABLICA: Dict[str, UstawieniaRezimu] = {
    "TREND_STRONG": UstawieniaRezimu(
        tryb="filtr",
        lewar_factor=1.2,
        prog_pewnosci=0.55,
        czy_grac=True,
        wagi_override={"T": 1.5, "M": 1.2, "S": 1.3, "O": 0.7},
        opis="Silny trend — filtr strategii, pełna dźwignia",
    ),
    "TREND_WEAK": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.7,
        prog_pewnosci=0.60,
        czy_grac=True,
        opis="Słaby trend — agregat, obniżona dźwignia",
    ),
    "RANGING": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.4,
        prog_pewnosci=0.72,
        czy_grac=False,
        wagi_override={"M": 1.5, "F": 1.2, "T": 0.4},
        opis="Rynek w konsolidacji — stój z boku (zbyt wiele fałszywych sygnałów)",
    ),
    "VOLATILE": UstawieniaRezimu(
        tryb="strategia",
        lewar_factor=0.5,
        prog_pewnosci=0.65,
        czy_grac=True,
        wagi_override={"A": 2.0, "V": 1.5, "L": 0.3},
        opis="Wysoka zmienność — Klucznik wybiera strategię, ostrożna dźwignia",
    ),
    "PANIC": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.1,
        prog_pewnosci=0.90,
        czy_grac=False,
        opis="Reżim PANIC — pełna cisza (kapitał chroniony)",
    ),
    "NORMAL": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.8,
        prog_pewnosci=0.60,
        czy_grac=True,
        opis="Normalny rynek — ostrożny agregat",
    ),
    "ON-CHAIN_BULLISH": UstawieniaRezimu(
        tryb="filtr",
        lewar_factor=1.1,
        prog_pewnosci=0.58,
        czy_grac=True,
        wagi_override={"O": 2.0, "L": 0.8},
        opis="Sygnały on-chain bycze — filtr, wzmocnione wagi O",
    ),
    "SMC_ACTIVE": UstawieniaRezimu(
        tryb="strategia",
        lewar_factor=0.9,
        prog_pewnosci=0.62,
        czy_grac=True,
        wagi_override={"S": 2.0, "F": 1.2, "T": 1.1},
        opis="Aktywna struktura SMC — Klucznik + wagi S",
    ),
}

# Fallback gdy reżim nieznany
_FALLBACK = UstawieniaRezimu(
    tryb="agregat",
    lewar_factor=0.5,
    prog_pewnosci=0.65,
    czy_grac=True,
    opis="Nieznany reżim — ultraostrożny fallback",
)


# ─── Warstwa STYLU INTERWAŁOWEGO (Timeframe-Aware Gating) ─────────────────────
#
# Deep-research (2026-06-03): auto-selekcja timeframe+strategia wg reżimu to
# OTWARTY PROBLEM — Freqtrade/Jesse/Nautilus/OctoBot wymagają ręcznej konfiguracji
# per styl. Standardy praktyków:
#   SCALP (M1-M15):  RSI 4-7, lewar 5-10×, FUTURES, szybkie wejścia
#   SWING (30M-4H):  RSI ~20, lewar 2-5×, FUTURES/SPOT
#   INVEST (1D-1W):  RSI 14, lewar spot/1-2×, SPOT, selektywne
#
# Prawo XV: ożywia martwe metadane strategii (interwaly/styl/dzwignia ignorowane
# przez dobierz_najlepsze). Namiestnik teraz rozróżnia styl wg interwału.


@dataclass
class ProfilStylu:
    """
    Profil handlowy zależny od interwału (timeframe → styl).

    styl:         SCALP / SWING / INVEST
    lewar_cap:    twardy sufit dźwigni dla tego stylu (deep-research: scalp≤10, swing≤5, invest≤2)
    rynek:        preferowany rynek: 'FUTURES' / 'SPOT' / 'OBA'
    mnoznik_progu:korekta progu pewności (scalp szybciej, invest selektywniej)
    opis:         czytelny powód
    """
    styl: str
    lewar_cap: int
    rynek: str
    mnoznik_progu: float
    opis: str


# Mapa interwał → profil stylu (Prawo XVI: progi/lewary z deep-research praktyków)
_PROFILE_STYLU: Dict[str, ProfilStylu] = {
    "SCALP": ProfilStylu("SCALP", lewar_cap=10, rynek="FUTURES", mnoznik_progu=0.95,
                         opis="Scalp M1-M15: szybkie wejścia, futures, wysoka dźwignia"),
    "SWING": ProfilStylu("SWING", lewar_cap=5, rynek="OBA", mnoznik_progu=1.0,
                         opis="Swing 30M-4H: zbalansowane, futures lub spot"),
    "INVEST": ProfilStylu("INVEST", lewar_cap=2, rynek="SPOT", mnoznik_progu=1.1,
                          opis="Invest 1D-1W: spot, niska dźwignia, selektywne"),
}

# Mapa interwału (z danych/strategii) → styl. Normalizacja wielkości liter.
_INTERWAL_NA_STYL: Dict[str, str] = {
    "M1": "SCALP", "1M": "SCALP", "M3": "SCALP", "3M": "SCALP",
    "M5": "SCALP", "5M": "SCALP", "M15": "SCALP", "15M": "SCALP",
    "M30": "SWING", "30M": "SWING", "1H": "SWING", "H1": "SWING",
    "2H": "SWING", "4H": "SWING", "H4": "SWING",
    "1D": "INVEST", "D1": "INVEST", "D": "INVEST", "3D": "INVEST",
    "1W": "INVEST", "W1": "INVEST", "W": "INVEST", "1M_MIES": "INVEST",
}

_PROFIL_FALLBACK = ProfilStylu("SWING", lewar_cap=5, rynek="OBA", mnoznik_progu=1.0,
                               opis="Nieznany interwał — domyślny profil SWING")


def styl_interwalu(interwal: Optional[str]) -> str:
    """Mapuje interwał (np. '1H','M5','1D') na styl SCALP/SWING/INVEST."""
    if not interwal:
        return "SWING"
    return _INTERWAL_NA_STYL.get(interwal.upper().strip(), "SWING")


def profil_stylu(interwal: Optional[str]) -> ProfilStylu:
    """Zwraca ProfilStylu dla interwału. Nigdy nie rzuca."""
    return _PROFILE_STYLU.get(styl_interwalu(interwal), _PROFIL_FALLBACK)


@dataclass
class DecyzjaNamiestnika:
    """
    Pełna decyzja Namiestnika: reżim × styl interwałowy.
    Łączy UstawieniaRezimu (co robić w tym reżimie) z ProfilStylu (jak na tym TF).
    """
    rezim: str
    styl: str
    tryb: str
    prog_pewnosci: float        # już skorygowany mnoznikiem stylu
    lewar_factor: float
    lewar_cap: int              # twardy sufit dźwigni stylu
    rynek: str                  # FUTURES / SPOT / OBA
    czy_grac: bool
    wagi_override: Optional[Dict[str, float]]
    opis: str


class Namiestnik:
    """
    Gating Network: (reżim, interwał) → kompletny zestaw parametrów dla jednego cyklu.

    Dwie warstwy:
      1. Reżim  (UstawieniaRezimu)  — CO robić w danym stanie rynku
      2. Styl   (ProfilStylu)       — JAK na danym interwale (lewar_cap, rynek, próg)

    Użycie w Dyrygencie:
        ustaw = namiestnik.decyduj(rezim, interwal)
        if not ustaw.czy_grac: ... cisza
        # ustaw.tryb, ustaw.prog_pewnosci, ustaw.lewar_factor, ustaw.lewar_cap, ustaw.rynek
    """

    def __init__(self, tablica: Optional[Dict[str, UstawieniaRezimu]] = None) -> None:
        self._tablica = tablica if tablica is not None else _TABLICA

    def decyduj(self, rezim: str, interwal: Optional[str] = None) -> DecyzjaNamiestnika:
        """
        Łączy reżim ze stylem interwałowym. Gdy interwal=None → czysty profil reżimu
        (SWING domyślnie). Nigdy nie rzuca wyjątku.
        """
        baza = self._tablica.get(rezim)
        if baza is None:
            logger.warning(f"[Namiestnik] Nieznany reżim '{rezim}' → fallback ostrożny")
            baza = _FALLBACK
        prof = profil_stylu(interwal)

        # INVEST na spot nie używa dźwigni futures — łączymy reguły.
        # Futures/spot: reżimy obronne (VOLATILE/PANIC) wymuszają SPOT niezależnie od stylu.
        rynek = prof.rynek
        if rezim in ("PANIC", "VOLATILE") and rynek == "FUTURES":
            rynek = "SPOT"  # obrona: bez dźwigni w chaosie nawet na scalpie

        return DecyzjaNamiestnika(
            rezim=rezim,
            styl=prof.styl,
            tryb=baza.tryb,
            prog_pewnosci=round(min(1.0, baza.prog_pewnosci * prof.mnoznik_progu), 4),
            lewar_factor=baza.lewar_factor,
            lewar_cap=prof.lewar_cap,
            rynek=rynek,
            czy_grac=baza.czy_grac,
            wagi_override=baza.wagi_override,
            opis=f"{baza.opis} | {prof.opis}",
        )

    def skaluj_dzwignie(self, dzwignia_base: int, rezim: str,
                        interwal: Optional[str] = None) -> int:
        """
        Aplikuje lewar_factor (reżim) do dźwigni, potem przycina sufitem stylu (lewar_cap).
        Wynik: int w przedziale [1, lewar_cap].
        """
        d = self.decyduj(rezim, interwal)
        scaled = int(round(dzwignia_base * d.lewar_factor))
        return max(1, min(scaled, d.lewar_cap))

    def decyduj_z_radarem(
        self,
        rezim: str,
        interwal: Optional[str] = None,
        stan_rynku: Optional[object] = None,
    ) -> "DecyzjaNamiestnika":
        """
        Opcja A — radar-aware gating: bazowa decyzja (decyduj), potem RadarRynku
        moduluje PARAMETRY (lewar_factor, prog_pewnosci), nie zmieniając trybu ani
        czy_grac — bo zmienianie trybu psuje "filtr" (STRATEGIA_BRAK gdy brak dop.).

        Reguły modulacji (Prawo XVI — bez look-ahead, bez wyłączania handlu):
          • Bycze tło (BTC>0.3 AND PRZEPLYW>0.60):
              lewar_factor ×1.20 (do 2.0), prog_pewnosci ×0.97
          • Niedźwiedzie + stres (STRES>0.80 AND BTC<0.0):
              lewar_factor ×0.65 (od 0.1), prog_pewnosci ×1.05 (do 0.98)
          • Czyste PANIC/VOLATILE — bez zmian (tryb_aktywny i tak defensywny).

        Gdy stan_rynku=None → identyczny wynik jak decyduj().
        """
        if stan_rynku is None:
            return self.decyduj(rezim, interwal)

        dec = self.decyduj(rezim, interwal)

        btc = getattr(stan_rynku, "btc_trend", None)
        przeplyw = getattr(stan_rynku, "przeplyw", None)
        stres = getattr(stan_rynku, "stres_korelacji", None)

        lewar_factor = dec.lewar_factor
        prog = dec.prog_pewnosci

        if (btc is not None and btc > 0.3
                and przeplyw is not None and przeplyw > 0.60):
            lewar_factor = round(min(2.0, lewar_factor * 1.20), 3)
            prog = round(max(0.50, prog * 0.97), 4)
        elif (stres is not None and stres > 0.80
              and btc is not None and btc < 0.0):
            lewar_factor = round(max(0.1, lewar_factor * 0.65), 3)
            prog = round(min(0.98, prog * 1.05), 4)

        return DecyzjaNamiestnika(
            rezim=dec.rezim,
            styl=dec.styl,
            tryb=dec.tryb,
            prog_pewnosci=prog,
            lewar_factor=lewar_factor,
            lewar_cap=dec.lewar_cap,
            rynek=dec.rynek,
            czy_grac=dec.czy_grac,
            wagi_override=dec.wagi_override,
            opis=dec.opis,
        )

    def tablica_rezimu(self) -> Dict[str, UstawieniaRezimu]:
        """Pełna tablica reżimów do inspekcji / diagnostyki."""
        return dict(self._tablica)

    def profile_stylu(self) -> Dict[str, ProfilStylu]:
        """Pełna mapa profili stylu do inspekcji."""
        return dict(_PROFILE_STYLU)

    def raport(self) -> str:
        """Czytelny raport tablicy reżimów + profili stylu dla logów / dashboardu."""
        linie = ["🏛️ NAMIESTNIK — Tablica reżimów (Faza 1):"]
        for rezim, u in self._tablica.items():
            gra = "✅ GRAJ" if u.czy_grac else "🛑 CISZA"
            linie.append(
                f"  {rezim:<20} │ {gra} │ tryb={u.tryb:<10} │ "
                f"lewar×{u.lewar_factor:.1f} │ próg={u.prog_pewnosci:.0%}"
            )
        linie.append("🕒 Profile stylu interwałowego (Timeframe-Aware):")
        for styl, p in _PROFILE_STYLU.items():
            linie.append(
                f"  {styl:<8} │ lewar≤{p.lewar_cap:>2}× │ rynek={p.rynek:<8} │ "
                f"próg×{p.mnoznik_progu:.2f}"
            )
        return "\n".join(linie)



# ─── Singleton dla użycia w Dyrygencie ───────────────────────────────────────
_instancja: Optional[Namiestnik] = None


def get_namiestnik() -> Namiestnik:
    """Zwraca globalny singleton Namiestnika (bez wielokrotnej inicjalizacji)."""
    global _instancja
    if _instancja is None:
        _instancja = Namiestnik()
    return _instancja
