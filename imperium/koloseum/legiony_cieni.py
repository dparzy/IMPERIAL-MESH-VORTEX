"""
👥 LEGIONY CIENI — Kontrfaktyczne Kolosseum (perełka końca wachty → KOD, Prawo XIX).

IDEA (jedno zdanie):
  Za każdym barem, obok realnej decyzji Imperium, maszerują widmowe kopie roju, które
  podjęły decyzje INNE — i mierzymy, ile kosztowała nas każda ostrożność i każda odwaga.

PROBLEM, KTÓREGO NIKT NIE MIERZY:
  Każdy system zna wynik decyzji PODJĘTYCH. Nikt nie zna wyniku NIEPODJĘTYCH: ile
  kosztowało weto? ile zarobiłby próg 0.45 zamiast 0.55? Dziś odpowiada A/B backtest PO
  fakcie. Cienie odpowiadają NA ŻYWO, per bar, per reżim. To Prawo XV podniesione do
  potęgi: alarm o niewykorzystanych DECYZJACH, nie tylko modułach.

DLACZEGO MY, A NIE KONKURENCJA (sedno przewagi, Prawo XXV):
  Nasz rój jest DETERMINISTYCZNY (Brama liczy, kod głosuje, zero LLM w pętli). Ten sam bar
  + ta sama konfiguracja = zawsze ta sama decyzja. Dlatego „co by było gdyby" można odtworzyć
  UCZCIWIE — przepuszczając ten sam bar przez wariant konfiguracji. Systemy agentowe na LLM
  mają nieodtwarzalne kontrfaktyczne „gdyby". Nasz determinizm = broń badawcza.

FUNDAMENT (ZPO):
  Counterfactual Regret Minimization (CFR) — Zinkevich, Johanson, Bowling, Piccione,
  „Regret Minimization in Games with Incomplete Information", NeurIPS 2007.
  ⚠️ link do weryfikacji: https://papers.nips.cc/paper/2007/hash/08d98638c6fcd194a4b1e6992063e944-Abstract.html
  Rodzina CFR pokonała ludzi w pokerze (Libratus 2017, Pluribus 2019, Brown & Sandholm).
  WERSJA 1 (ten moduł): nie pełny CFR, lecz POMIAR ŻALU per wariant konfiguracji — uczciwy,
  prosty, mierzalny. Faza 2 (żal → wagi MWU) dopiero po walidacji ≥100 barów (osobna decyzja).

ARCHITEKTURA (na tym co JUŻ mamy — Prawo XVI reuse):
  Cień = zwykły PaperTradingEngine + Dyrygent z wariantem konfiguracji (wszystko istnieje).
  Menedżer prowadzi N cieni równolegle; po każdym barze zapisuje ich zamknięcia jako
  CIEN_PNL do bazy areny (arena_baza). Koszt: ~N× czas cyklu paper (pomijalny na 1H/4H).

ZASADA WPIĘCIA: opt-in `cienie=False` w KonfigPetliLive — zero zmiany domyślnego zachowania.
  Cienie NIE wpływają na realne zlecenia; to obserwatorzy (papierowe silniki obok głównego).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("LegionyCieni")

# Rodzaj pomiaru w bazie areny (spójny z wizją — filtrowalny przez arena_pytaj)
RODZAJ_ARENA = "CIEN_PNL"

# O ile luzujemy/zaostrzamy próg pewności w wariantach progowych (pkt prawdopodobieństwa)
DELTA_PROGU = 0.10


@dataclass
class Cien:
    """Jeden wariant widmowy: nazwa + jego Dyrygent + papierowy silnik + opis wariantu."""
    nazwa: str
    dyrygent: Any
    engine: Any
    opis: str = ""
    _watermark: int = field(default=0, repr=False)   # ile zamknięć już zapisano do areny


def warianty_domyslne(bazowy_prog: float = 0.55) -> List[Dict[str, Any]]:
    """
    Trzy startowe cienie (wizja): mierzą cenę ostrożności i cenę odwagi.
      • bez_wet      — odważny: bezpieczniki OFF (breaker/6%/asymetria) → ile kosztuje weto
      • prog_lagodny — próg −0.10: wchodzi CZĘŚCIEJ → ile zarabia/traci luźniejsze wejście
      • prog_surowy  — próg +0.10: wchodzi RZADZIEJ/pewniej → ile kosztuje/oszczędza ostrożność
    Progi przycięte do [0,1] (granica — bazowy_prog blisko 0/1 nie wypada poza zakres).
    """
    return [
        {"nazwa": "bez_wet", "min_pewnosc": bazowy_prog, "bez_wet": True,
         "opis": "odważny — bezpieczniki OFF (breaker krzywej / reguła 6% / filtr asymetrii)"},
        {"nazwa": "prog_lagodny", "min_pewnosc": round(max(0.0, bazowy_prog - DELTA_PROGU), 4), "bez_wet": False,
         "opis": f"próg −{DELTA_PROGU:.2f} — wchodzi częściej"},
        {"nazwa": "prog_surowy", "min_pewnosc": round(min(1.0, bazowy_prog + DELTA_PROGU), 4), "bez_wet": False,
         "opis": f"próg +{DELTA_PROGU:.2f} — wchodzi rzadziej/pewniej"},
    ]


class LegionyCieni:
    """
    Menedżer N cieni. Prowadzi każdy wariant przez te same bary co realny rój i zapisuje
    ich zamknięcia (CIEN_PNL) do bazy areny. Odporny na awarię pojedynczego cienia (graceful,
    Prawo XV — jeden cień nie może zabić pomiaru pozostałych ani realnego handlu).
    """

    def __init__(self, cienie: List[Cien], db_path=None,
                 arena_zapis: Optional[Callable[[list], int]] = None):
        """
        cienie:      lista Cien (zbudowanych fabryką lub wstrzykniętych w testach).
        arena_zapis: callable(wiersze)->int do zapisu pomiarów. None → arena_baza.zapisz_pomiary.
                     Wstrzykiwalny dla testów offline (bez SQLite).
        """
        self.cienie = list(cienie)
        self._db_path = db_path
        self._arena_zapis = arena_zapis

    # ── Zapis do areny (wstrzykiwalny) ───────────────────────────────────────
    def _zapisz(self, wiersze: list) -> int:
        if not wiersze:
            return 0
        if self._arena_zapis is not None:
            return self._arena_zapis(wiersze)
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        return zapisz_pomiary(wiersze, db_path=self._db_path) if self._db_path \
            else zapisz_pomiary(wiersze)

    # ── Krok na jednym barze ─────────────────────────────────────────────────
    def krok(self, symbol: str, bary: List[Dict[str, Any]],
             rezim: str = "NORMAL", timestamp: Optional[int] = None) -> Dict[str, Any]:
        """
        Przepuszcza jeden bar przez KAŻDY cień i zapisuje jego NOWE zamknięcia do areny.

        Zwraca {nazwa: {'weszedl': bool, 'nowe_zamkniecia': int}} — diagnostyka per cień.
        Batch: JEDNO połączenie SQLite na krok (wszystkie cienie razem — jak petla_live).
        """
        wynik: Dict[str, Any] = {}
        do_zapisu: list = []

        for c in self.cienie:
            weszedl = False
            try:
                decyzja = c.dyrygent.cykl(symbol, bary, rezim=rezim, timestamp=timestamp)
                weszedl = bool(getattr(decyzja, "wszedl", False))
            except Exception as e:  # noqa: BLE001 — cień nie może zabić pomiaru reszty
                logger.warning(f"[Cień:{c.nazwa}] cykl padł dla {symbol}: {e}")

            # Nowe zamknięcia od ostatniego watermarku → CIEN_PNL
            hist = getattr(c.engine, "historia_zamkniec", [])
            nowe = hist[c._watermark:]
            for w in nowe:
                if hasattr(w, "pnl_pct"):
                    nota = f"{getattr(w, 'symbol', symbol)} {getattr(w, 'rezim', rezim) or rezim}"
                    do_zapisu.append((RODZAJ_ARENA, c.nazwa, float(w.pnl_pct), nota))
            c._watermark = len(hist)
            wynik[c.nazwa] = {"weszedl": weszedl, "nowe_zamkniecia": len(nowe)}

        if do_zapisu:
            try:
                self._zapisz(do_zapisu)
            except Exception as e:  # noqa: BLE001 — awaria bazy nie może zabić pętli
                logger.warning(f"[LegionyCieni] zapis CIEN_PNL padł: {e}")

        return wynik

    # ── Raport zbiorczy (Kronika Żyć Nieprzeżytych — v1) ──────────────────────
    def raport(self) -> List[Dict[str, Any]]:
        """Zbiorczy wynik każdego cienia: liczba trade'ów, suma i średnia PnL%, kapitał."""
        raport = []
        for c in self.cienie:
            hist = getattr(c.engine, "historia_zamkniec", [])
            pnl = [float(w.pnl_pct) for w in hist if hasattr(w, "pnl_pct")]
            raport.append({
                "cien": c.nazwa,
                "opis": c.opis,
                "trades": len(pnl),
                "pnl_pct_suma": round(sum(pnl), 4),
                "pnl_pct_srednia": round(sum(pnl) / len(pnl), 4) if pnl else 0.0,
                "kapital": round(float(getattr(c.engine, "kapital_calkowity", 0.0)), 2),
            })
        return raport


# ─── Fabryka produkcyjna (3 cienie na papierowych silnikach) ─────────────────

def zbuduj_cienie_paper(
    symbole: List[str],
    bazowy_prog: float = 0.55,
    kapital_startowy: float = 10000.0,
    db_path=None,
    adaptery_factory: Optional[Callable[[], List[Any]]] = None,
    namiestnik: Optional[Any] = None,
    bazowy_breaker: bool = True,
    bazowy_6pct: bool = False,
    bazowy_asymetria: bool = False,
    arena_zapis: Optional[Callable[[list], int]] = None,
) -> LegionyCieni:
    """
    Buduje domyślne 3 cienie jako papierowe silniki + Dyrygenci (Prawo XVI reuse pełnego stosu).

    Warianty progowe (prog_lagodny/prog_surowy) DZIEDZICZĄ realne bezpieczniki (bazowy_*),
    różniąc się tylko progiem pewności — czysty pomiar wpływu progu. Wariant bez_wet ma
    WSZYSTKIE bezpieczniki OFF — pomiar łącznego kosztu wet. Każdy cień ma WŁASNEGO Legatusa
    (świeży MWU/synapsy — cienie się nie kontaminują nawzajem ani z realnym rojem).

    adaptery_factory: callable()->lista NOWYCH adapterów, wołane PER CIEŃ (nie współdzielona
      lista!). Krytyczne: adaptery jak AdapterFutures trzymają stan per-symbol (OI_PREV);
      współdzielenie instancji między cieniami psułoby dywergencję OI (cień 2/3 widziałby
      OI==OI_PREV z odczytu cienia 1 w tym samym barze). None → cienie bez adapterów.
    """
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.koloseum.paper_trading import PaperTradingEngine

    budowniczy = BudowniczyWskaznikow()   # bezstanowy — współdzielony bezpiecznie
    cienie: List[Cien] = []
    for w in warianty_domyslne(bazowy_prog):
        bez_wet = w["bez_wet"]
        engine = PaperTradingEngine(
            kapital_startowy=kapital_startowy,
            sesja_id=f"CIEN-{w['nazwa']}",
            max_otwartych=max(1, len(symbole)),
        )
        legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
        dyr = Dyrygent(
            legatus=legatus,
            kalkulator=KalkulatorLewara(),
            engine=engine,
            budowniczy=budowniczy,
            min_pewnosc=w["min_pewnosc"],
            namiestnik=namiestnik,
            adaptery=adaptery_factory() if adaptery_factory else [],  # ŚWIEŻE per cień
            breaker_krzywej=False if bez_wet else bazowy_breaker,
            regula_6pct=False if bez_wet else bazowy_6pct,
            filtr_asymetrii=False if bez_wet else bazowy_asymetria,
        )
        cienie.append(Cien(nazwa=w["nazwa"], dyrygent=dyr, engine=engine, opis=w["opis"]))

    return LegionyCieni(cienie, db_path=db_path, arena_zapis=arena_zapis)
