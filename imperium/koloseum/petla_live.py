"""
🔴 PĘTLA LIVE — W-302 | Główny entrypoint systemu tradingowego.

Spina wszystkie warstwy Imperium w jedną pętlę:
  DataLoader (OHLCV) → RadarRynku (kontekst BTC) → Dyrygent.cykl() per symbol
  → PamiecRefleksyjna (cross-session learning) → powiadomienie/log.

ARCHITEKTURA (Prawo I — zero lookahead):
  ┌─────────────────────────────────────────────────────────┐
  │  RAZ NA BAR (co `interwal`)                             │
  │  1. Pobierz bary dla wszystkich symboli (DataLoader)    │
  │  2. odswiez_kontekst_rynku(close_btc, close_alty)       │
  │     → BTC_TREND/DOMINACJA/PRZEPLYW → RADAR-01/02/03    │
  │  3. Dla każdego symbolu: dyrygent.cykl(sym, bary)       │
  │  4. Wykryj nowe zamknięcia → PamiecRefleksyjna.zapisz  │
  │  5. Czekaj do następnego baru                          │
  └─────────────────────────────────────────────────────────┘

BEZPIECZEŃSTWO (Prawo I — klucze NIGDY w kodzie):
  MEXC_API_KEY, MEXC_SECRET — wyłącznie os.getenv().
  W trybie paper: klucze niepotrzebne (DataLoader tylko fetch OHLCV, bez zleceń).

TRYB STARTOWY:
  - paper=True (domyślnie): symuluje trade (PaperTradingEngine) — bez prawdziwych zleceń.
  - paper=False: integracja z nexus_hub (RealOrderRouter) — wymaga kluczy API.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# Mapowanie interwal → sekundy — na ile spać po barze
_INTERWAL_SEKUNDY: Dict[str, int] = {
    "1m": 60,  "3m": 180,  "5m": 300, "15m": 900, "30m": 1800,
    "1H": 3600, "2H": 7200, "4H": 14400, "6H": 21600, "1D": 86400,
}


@dataclass
class KonfigPetliLive:
    """Konfiguracja pętli live — jeden obiekt zamiast 20 argumentów."""
    symbole: List[str]                    # np. ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    interwal: str = "1H"                  # interwał świec
    limit_barow: int = 400                # ile świec historii pobierać co bar
    kapital_startowy: float = 10_000.0    # kapitał startowy (paper lub realny)
    min_pewnosc: float = 0.55             # próg pewności Legatusa
    paper: bool = True                    # True=paper trading, False=realne zlecenia
    auto_rezim: bool = True               # True=auto-klasyfikacja reżimu (Namiestnik)
    synapsy: bool = True                  # True=SynapsyRezimowe per symbol
    # W-307: warstwy uczenia wag neuronów (Prawo XV — opt-in, domyślnie OFF).
    #   mwu      — HedgeMWU online (eksponencjalne, po każdym trade'cie)
    #   igrzyska — Igrzyska batch (kumulatywny ranking accuracy/stability)
    # Gdy oba True: mnożniki łączone (MWU × ranga Igrzysk) w Legatusie.
    mwu: bool = False
    igrzyska: bool = False
    # W-309: KsięgaWad — prewencyjny filtr wad setupu (rezim/interwal). Opt-in, OFF.
    ksiega_wad: bool = False
    # W-314: Filtr Asymetrii Reżimu — weto na rynku bocznym (ADX) i kontr-trendzie. OFF.
    filtr_asymetrii: bool = False
    plik_pamieci: str = "logs/pamiec_refleksyjna.jsonl"
    log_dir: Optional[str] = "logs"
    # Pauza po każdym barze (s). None = oblicz z interwal (zalecane).
    pauza_sekundy: Optional[int] = None
    # Liczba barów pomiędzy odświeżeniem RADAR (domyślnie co bar = 1).
    radar_co_bar: int = 1


@dataclass
class StatystykiPetli:
    """Bieżące statystyki pętli — raportowane w logach co N barów."""
    bary_przetworzone: int = 0
    decyzje_wejscia: int = 0
    decyzje_neutralne: int = 0
    weta: int = 0
    bledy: int = 0
    zamkniec_w_sesji: int = 0
    _pamiec_zamkniec: int = 0   # poprzedni odczyt historia_zamkniec


def _df_do_barow(df, symbol: str, interwal: str) -> List[Dict]:
    """Konwertuje DataFrame z DataLoadera do List[Dict] wymaganej przez Dyrygent.cykl()."""
    bary = []
    for row in df.itertuples(index=False):
        ts = row.timestamp
        # DataLoader.fetch zwraca timestamp jako datetime (pd.Timestamp); zamieniamy
        # na ms (int) których wymaga PaperTradingEngine i RADAR (bisect).
        if hasattr(ts, "value"):
            ts_ms = int(ts.value // 1_000_000)         # pandas Timestamp → ms
        elif hasattr(ts, "timestamp"):
            ts_ms = int(ts.timestamp() * 1000)         # datetime → ms
        else:
            ts_ms = int(ts)                             # już int (ms)
        bary.append({
            "timestamp": ts_ms,
            "open":   float(row.open),
            "high":   float(row.high),
            "low":    float(row.low),
            "close":  float(row.close),
            "volume": float(row.volume),
            "symbol": symbol,
            "interwal": interwal,
        })
    return bary


def _buduj_dyrygencie(
    symbole: List[str],
    cfg: KonfigPetliLive,
    engine,
) -> Dict:
    """Tworzy słownik per-symbol Dyrygentów współdzielących jeden Engine."""
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.koloseum.namiestnik import get_namiestnik
    from imperium.akwedukty.adaptery import AdapterFutures, AdapterFearGreed, AdapterCVD, AdapterNewsLLM

    namiestnik = get_namiestnik() if cfg.auto_rezim else None
    budowniczy = BudowniczyWskaznikow()
    n = len(symbole)
    kapital_per = cfg.kapital_startowy / n

    dyrygenci = {}
    for sym in symbole:
        legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
        if cfg.synapsy:
            from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe
            legatus.synapsy = SynapsyRezimowe()
        if cfg.mwu:
            from imperium.biblioteki.hedge_mwu import HedgeMWU
            legatus.mwu = HedgeMWU()

        d = Dyrygent(
            legatus=legatus,
            kalkulator=KalkulatorLewara(),
            engine=engine,
            budowniczy=budowniczy,
            min_pewnosc=cfg.min_pewnosc,
            namiestnik=namiestnik,
            adaptery=[AdapterFutures(), AdapterFearGreed(), AdapterCVD(), AdapterNewsLLM()],
            filtr_asymetrii=cfg.filtr_asymetrii,
        )
        d.kapital_sizing = kapital_per
        if cfg.igrzyska:
            from imperium.biblioteki.igrzyska import Igrzyska as _Igrzyska
            d._igrzyska = _Igrzyska()
        if cfg.ksiega_wad:
            from imperium.cesarz.ksiega_wad import KsiegaWad as _KsiegaWad
            d.ksiega_wad = _KsiegaWad()
        dyrygenci[sym] = d

    return dyrygenci


def _bootstrap_ksiega_wad(dyrygenci: Dict, pamiec) -> int:
    """
    W-310: zasila KsięgęWad każdego Dyrygenta lekcjami z persystentnej
    PamięciRefleksyjnej (cross-session learning). Zwraca liczbę wczytanych lekcji.

    Domyka pętlę pamięci (Prawo XV): lekcje pisane do JSONL co sesja były dotąd
    nigdy nie czytane w produkcji — teraz oflagowują stratne setupy od 1. baru.
    """
    n_lekcji = 0
    for d in dyrygenci.values():
        if getattr(d, "ksiega_wad", None) is not None:
            n_lekcji = d.ksiega_wad.ucz_z_pamieci(pamiec)
    return n_lekcji


def handluj_live(
    konfiguracja: KonfigPetliLive,
    max_barow: Optional[int] = None,      # None = nieskończona pętla; int = limit (testy)
    _loader=None,                          # wstrzykiwalny loader (testy bez sieci)
) -> StatystykiPetli:
    """
    Główna pętla live Imperium.

    Parametry:
      konfiguracja: KonfigPetliLive z wszystkimi opcjami.
      max_barow:    ile barów obsłużyć (None = nieskończona pętla produkcyjna).
      _loader:      wstrzykiwalny DataLoader (testy offline z syntetycznymi danymi).

    Zwraca:
      StatystykiPetli po zakończeniu (lub zatrzymaniu).
    """
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.cesarz.pamiec_refleksyjna import PamiecRefleksyjna
    from imperium.legiony.radar_rynku import RadarRynku

    cfg = konfiguracja
    pauza = cfg.pauza_sekundy or _INTERWAL_SEKUNDY.get(cfg.interwal, 3600)
    btc_sym = next((s for s in cfg.symbole if s.upper().startswith("BTC")), None)

    # Engine: paper lub (przyszłe) realne zlecenia
    engine = PaperTradingEngine(
        kapital_startowy=cfg.kapital_startowy,
        sesja_id=f"LIVE-{cfg.interwal}-{len(cfg.symbole)}x",
        max_otwartych=len(cfg.symbole),
        log_dir=cfg.log_dir,
    )
    dyrygenci = _buduj_dyrygencie(cfg.symbole, cfg, engine)
    pamiec = PamiecRefleksyjna(plik=cfg.plik_pamieci)
    radar = RadarRynku()
    statystyki = StatystykiPetli()

    # W-310: domknięcie pętli pamięci — bootstrap KsięgiWad z PERSYSTENTNYCH lekcji
    # poprzednich sesji (Prawo XV: lekcje były pisane, nigdy czytane w produkcji).
    if cfg.ksiega_wad:
        n_lekcji = _bootstrap_ksiega_wad(dyrygenci, pamiec)
        logger.info(f"[PętlaLive] KsięgaWad: bootstrap z {n_lekcji} lekcji "
                    f"PamięciRefleksyjnej (cross-session, Prawo XV)")

    # Loader: wstrzykiwany (testy) lub prawdziwy DataLoader
    if _loader is None:
        from imperium.akwedukty.kwatermistrz_danych import DataLoader
        loader = DataLoader()
    else:
        loader = _loader

    logger.info(f"[PętlaLive] Start: {cfg.symbole}, interwal={cfg.interwal}, "
                f"paper={cfg.paper}, synapsy={cfg.synapsy}, "
                f"mwu={cfg.mwu}, igrzyska={cfg.igrzyska}, ksiega_wad={cfg.ksiega_wad}, "
                f"filtr_asymetrii={cfg.filtr_asymetrii}")

    bar_nr = 0
    try:
        while max_barow is None or bar_nr < max_barow:
            bar_nr += 1
            bary_per: Dict[str, List[Dict]] = {}

            # 1. Pobierz bary wszystkich symboli
            for sym in cfg.symbole:
                try:
                    df = loader.fetch(sym, cfg.interwal, limit=cfg.limit_barow)
                    bary_per[sym] = _df_do_barow(df, sym, cfg.interwal)
                except Exception as e:
                    logger.warning(f"[PętlaLive] Fetch {sym} padł: {e}")

            if not bary_per:
                logger.error("[PętlaLive] Brak danych dla żadnego symbolu — czekam.")
                if max_barow is not None:
                    break
                time.sleep(min(pauza, 60))
                continue

            # 2. Radar rynku — raz na bar (BTC = kontekst wspólny koszyka)
            if bar_nr % cfg.radar_co_bar == 0 and btc_sym and btc_sym in bary_per:
                close_btc = [b["close"] for b in bary_per[btc_sym]]
                close_alty = {s: [b["close"] for b in bs]
                              for s, bs in bary_per.items() if s != btc_sym}
                vol_alty = {s: [b["volume"] for b in bs]
                            for s, bs in bary_per.items() if s != btc_sym}
                try:
                    stan = radar.skanuj(close_btc, close_alty, vol_alty)
                    for d in dyrygenci.values():
                        d.stan_rynku = stan
                        d.kontekst_dodatkowy.update(stan.jako_wskazniki())
                except Exception as e:
                    logger.warning(f"[PętlaLive] Radar padł: {e}")

            # 3. Cykl decyzyjny per symbol
            for sym, bary in bary_per.items():
                if sym not in dyrygenci:
                    continue
                try:
                    ts = bary[-1]["timestamp"]
                    decyzja = dyrygenci[sym].cykl(sym, bary, timestamp=ts)
                    statystyki.bary_przetworzone += 1
                    if decyzja.wszedl:
                        statystyki.decyzje_wejscia += 1
                        logger.info(f"[PętlaLive] WEJŚCIE {sym} {decyzja.kierunek} "
                                    f"pewność={decyzja.pewnosc:.0%} reżim={decyzja.rezim}")
                    elif "WETO" in decyzja.etap:
                        statystyki.weta += 1
                    else:
                        statystyki.decyzje_neutralne += 1
                except Exception as e:
                    statystyki.bledy += 1
                    logger.error(f"[PętlaLive] Błąd cyklu {sym}: {e}")

            # 4. Zamknięcia → PamięćRefleksyjna (per sesja, na koniec każdego baru)
            hist_now = len(engine.historia_zamkniec)
            if hist_now > statystyki._pamiec_zamkniec:
                nowe = engine.historia_zamkniec[statystyki._pamiec_zamkniec:]
                statystyki._pamiec_zamkniec = hist_now
                statystyki.zamkniec_w_sesji += len(nowe)
                # Agregujemy nowe zamknięcia do jednej lekcji na bar
                pnl_nowe = [w.pnl_pct for w in nowe if hasattr(w, "pnl_pct")]
                if pnl_nowe:
                    try:
                        pamiec.zapisz_wynik(
                            pnl_lista=pnl_nowe,
                            rezim=nowe[-1].rezim if hasattr(nowe[-1], "rezim") else "NORMAL",
                            interwal=cfg.interwal,
                            kontekst={
                                "symbole": list(bary_per.keys()),
                                "bar_nr": bar_nr,
                                "kapital": round(engine.kapital_calkowity, 2),
                            },
                        )
                    except Exception as e:
                        logger.warning(f"[PętlaLive] PamięćRefleksyjna padła: {e}")

            # 5. Logi diagnostyczne co 10 barów
            if bar_nr % 10 == 0:
                logger.info(f"[PętlaLive] Bar #{bar_nr} | "
                            f"Kapitał: {engine.kapital_calkowity:.0f} | "
                            f"Wejścia: {statystyki.decyzje_wejscia} | "
                            f"Zamknięcia: {statystyki.zamkniec_w_sesji} | "
                            f"Błędy: {statystyki.bledy}")

            if max_barow is None:
                time.sleep(pauza)

    except KeyboardInterrupt:
        logger.info("[PętlaLive] Zatrzymano (Ctrl+C). Zamykam otwarte pozycje...")

    # Domknij otwarte po ostatniej cenie (paper mode)
    if cfg.paper:
        ostatnie = {}
        for sym, bary in bary_per.items():
            if bary:
                ostatnie[sym] = bary[-1]["close"]
        if ostatnie:
            engine.zamknij_wszystkie(ostatnie, powod="PETLA_STOP")

    return statystyki


def uruchom(
    symbole: List[str],
    interwal: str = "1H",
    kapital: float = 10_000.0,
    paper: bool = True,
) -> None:
    """
    Skrót do uruchomienia pętli live z domyślnymi ustawieniami.

    Przykład:
        from imperium.koloseum.petla_live import uruchom
        uruchom(["BTCUSDT", "ETHUSDT", "SOLUSDT"], interwal="4H")
    """
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    kfg = KonfigPetliLive(symbole=symbole, interwal=interwal,
                          kapital_startowy=kapital, paper=paper)
    handluj_live(kfg)
