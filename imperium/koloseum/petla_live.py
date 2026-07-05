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
    dry_run: bool = False                 # paper=False+dry_run=True: realny klucz, zlecenia tylko logowane (MEXC bez testnetu)
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
    # W-327: źródło funding/OI dla PSY-01/04. True=MEXC (rodzime — funding który
    # FAKTYCZNIE płacisz na MEXC), False=Binance fapi. L/S ratio (PSY-02) zawsze z
    # Binance (MEXC nie ma łatwego public L/S; sentyment rynkowy cross-giełdowy OK).
    funding_mexc: bool = False
    plik_pamieci: str = "logs/pamiec_refleksyjna.jsonl"
    log_dir: Optional[str] = "logs"
    # Pauza po każdym barze (s). None = oblicz z interwal (zalecane).
    pauza_sekundy: Optional[int] = None
    # Liczba barów pomiędzy odświeżeniem RADAR (domyślnie co bar = 1).
    radar_co_bar: int = 1
    # W-329: decay synaps reżimowych — co ile barów wołać synapsy.zapomnij() (higiena
    # pamięci). Bez decay martwe pary nigdy nie wygasają w długim live (luka P4 audytu).
    # 0 = wyłączone. Domyślnie 50 barów (≈ 8 dni na 4h) — łagodne sprzątanie.
    synapsy_decay_co_bar: int = 50
    # W-330: auto-dobór par z giełdy (SelektorPar — płynność × dekorelacja od BTC).
    # False=sztywna lista cfg.symbole. True=zastąp listę rankingiem TOP-N (wymaga loadera).
    auto_discover: bool = False
    auto_discover_top_n: int = 5
    auto_discover_min_obrot: float = 5_000_000.0
    # W-343 LiveMonitor (Prawo XXIV): TUI panel w terminalu co bar. OFF domyślnie.
    monitor: bool = False
    # W-346 Web dashboard (Panel Kapitolu): serwer HTTP localhost co bar. OFF domyślnie.
    dashboard: bool = False
    dashboard_port: int = 8777
    # W-343 TelegramAlert (Prawo XXIV): alerty na wejścia/zamknięcia/weto PANIC.
    # Wymaga TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID w zmiennych środowiskowych.
    telegram: bool = False
    # W-343 Senat Debaty (Prawo XXII): KonsulSenatu per symbol weryfikuje kierunek.
    senat: bool = False
    # W-352: Persystencja uczenia (cross-session). None = bez zapisu stanu.
    # Gdy podane — MWU, Igrzyska i Synapsy ładują stan na starcie i zapisują na końcu.
    sciezka_mwu: Optional[str] = "logs/mwu_stan.json"
    sciezka_igrzyska: Optional[str] = "logs/igrzyska_stan.json"
    sciezka_synapsy: Optional[str] = "logs/synapsy_{sym}.json"  # {sym} → symbol
    # W-354: TradingView Webhook Receiver. True = uruchom POST /webhook/tv obok dashboardu.
    # Wymaga dashboard=True (serwer HTTP musi być uruchomiony).
    # Sekret: WEBHOOK_TV_SEKRET w env (Prawo bezpieczeństwa — nigdy w kodzie/configu).
    webhook_tv: bool = False
    # Arena auto-log (opt-in, OFF): każde zamknięcie loguje realny PnL% do bazy areny
    # (arena_wyniki.db, rodzaj='LIVE_PNL') → Claude czyta skuteczność live MCP-em arena_pytaj.
    # Domyślnie False = ZERO zmiany zachowania (wzorzec opt-in jak mwu/igrzyska).
    arena_log: bool = False
    # ML-36: bramka konformalna progu pewności (opt-in, OFF). Po serii strat PODNOSI
    # próg (rój wchodzi rzadziej/pewniej); tylko zaostrza — nie zwiększa liczby wejść.
    kalibruj_prog: bool = False


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
    from imperium.akwedukty.adaptery import (
        AdapterFutures, AdapterMEXCFutures, AdapterFearGreed, AdapterCVD, AdapterNewsLLM,
    )

    # W-327: lista adapterów sentymentu/flow. Gdy funding_mexc → MEXC dokładany PO
    # Binance, więc nadpisuje funding+OI rodzimymi (L/S zostaje z Binance — MEXC go
    # nie dostarcza, więc nie nadpisze). Kolejność = priorytet ostatniego dla klucza.
    # NEWS-01 dostaje żywy feed RSS (CoinDesk/CT/Decrypt) — unlock 2026-06-30. Graceful:
    # brak sieci → fetcher zwraca [] → NEWS-01 abstynuje (Prawo XV), nic się nie psuje.
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS
    adaptery_sentymentu = [AdapterFutures(), AdapterFearGreed(), AdapterCVD(),
                           AdapterNewsLLM(fetcher=FetcherNewsRSS())]
    if getattr(cfg, "funding_mexc", False):
        adaptery_sentymentu.insert(1, AdapterMEXCFutures())

    namiestnik = get_namiestnik() if cfg.auto_rezim else None
    budowniczy = BudowniczyWskaznikow()
    n = len(symbole)
    kapital_per = cfg.kapital_startowy / n

    dyrygenci = {}
    for sym in symbole:
        legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
        if cfg.synapsy:
            from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe
            sciezka_syn = (
                cfg.sciezka_synapsy.replace("{sym}", sym)
                if cfg.sciezka_synapsy else None
            )
            legatus.synapsy = SynapsyRezimowe(sciezka_stanu=sciezka_syn)
        if cfg.mwu:
            from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
            mwu = HedgeMWUzPamieciaRezimu()
            if cfg.sciezka_mwu:
                # per-symbol: logs/mwu_BTCUSDT.json
                sch = cfg.sciezka_mwu.replace(".json", f"_{sym}.json")
                mwu.wczytaj(sch)
                mwu._sciezka = sch
            legatus.mwu = mwu

        d = Dyrygent(
            legatus=legatus,
            kalkulator=KalkulatorLewara(),
            engine=engine,
            budowniczy=budowniczy,
            min_pewnosc=cfg.min_pewnosc,
            namiestnik=namiestnik,
            adaptery=adaptery_sentymentu,
            filtr_asymetrii=cfg.filtr_asymetrii,
        )
        d.kapital_sizing = kapital_per
        if cfg.igrzyska:
            from imperium.biblioteki.igrzyska import Igrzyska as _Igrzyska
            ig = _Igrzyska()
            if cfg.sciezka_igrzyska:
                sch = cfg.sciezka_igrzyska.replace(".json", f"_{sym}.json")
                ig.wczytaj(sch)
                ig._sciezka = sch
            d._igrzyska = ig
        if cfg.ksiega_wad:
            from imperium.cesarz.ksiega_wad import KsiegaWad as _KsiegaWad
            d.ksiega_wad = _KsiegaWad()
        if getattr(cfg, "senat", False):
            from imperium.senat.debata_senatu import KonsulSenatu as _KonsulSenatu
            d._senat = _KonsulSenatu()
        if getattr(cfg, "kalibruj_prog", False):
            from imperium.legiony.kalibrator_konformalny import BramkaPewnosciKonformalna
            d.bramka_kalibr = BramkaPewnosciKonformalna(cel_trafnosci=cfg.min_pewnosc)
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

    # W-330: auto-dobór par z giełdy (płynność × dekorelacja od BTC). Gdy włączony,
    # zastępuje sztywną listę cfg.symbole rankingiem SelektorPar. Bez sieci/loadera →
    # zostaje lista z konfiguracji (Prawo XV — nie zgadujemy).
    if cfg.auto_discover and _loader is not None:
        try:
            from imperium.koloseum.selektor_par import SelektorPar
            sel = SelektorPar(_loader)
            wybrane = sel.wybierz(top_n=cfg.auto_discover_top_n,
                                  min_obrot_usd=cfg.auto_discover_min_obrot)
            if wybrane:
                logger.info(f"[PętlaLive] Auto-discover: {len(wybrane)} par → {wybrane}")
                cfg.symbole = wybrane
            else:
                logger.warning("[PętlaLive] Auto-discover pusty — zostaję przy liście z konfiguracji.")
        except Exception as e:
            logger.error(f"[PętlaLive] Auto-discover padł: {e} — lista z konfiguracji.")

    btc_sym = next((s for s in cfg.symbole if s.upper().startswith("BTC")), None)

    # Engine: paper lub realne zlecenia MEXC (W-331)
    if cfg.paper:
        engine = PaperTradingEngine(
            kapital_startowy=cfg.kapital_startowy,
            sesja_id=f"LIVE-{cfg.interwal}-{len(cfg.symbole)}x",
            max_otwartych=len(cfg.symbole),
            log_dir=cfg.log_dir,
        )
    else:
        from imperium.drogi.real_order_router import RealOrderRouter
        prefix = "DRYRUN" if cfg.dry_run else "REAL"
        engine = RealOrderRouter(
            kapital_startowy=cfg.kapital_startowy,
            sesja_id=f"{prefix}-{cfg.interwal}-{len(cfg.symbole)}x",
            max_otwartych=len(cfg.symbole),
            log_dir=cfg.log_dir,
            dry_run=cfg.dry_run,
        )
        # W-333: odtwórz otwarte pozycje z MEXC (bezpieczeństwo po restarcie —
        # inaczej pozycja wisi na giełdzie bez kontroli SL/TP roju).
        try:
            n_sync = engine.synchronizuj_pozycje(interwal=cfg.interwal)
            if n_sync:
                logger.warning(f"[PętlaLive] SYNC: odtworzono {n_sync} pozycji z MEXC.")
        except Exception as e:
            logger.error(f"[PętlaLive] Synchronizacja pozycji padła: {e}")
    dyrygenci = _buduj_dyrygencie(cfg.symbole, cfg, engine)
    pamiec = PamiecRefleksyjna(plik=cfg.plik_pamieci)
    radar = RadarRynku()
    statystyki = StatystykiPetli()

    # W-343 LiveMonitor (Prawo XXIV): TUI panel + TelegramAlert
    monitor = None
    telegram = None
    if getattr(cfg, "monitor", False):
        from imperium.swiatynie.live_monitor import LiveMonitor
        monitor = LiveMonitor()
    if getattr(cfg, "telegram", False):
        from imperium.swiatynie.live_monitor import TelegramAlert
        telegram = TelegramAlert()
        if not telegram.aktywny:
            logger.warning("[PętlaLive] TelegramAlert wyłączony — brak TELEGRAM_BOT_TOKEN/CHAT_ID")
    serwer_web = None
    odbiornik_tv = None
    if getattr(cfg, "dashboard", False):
        from imperium.swiatynie.web_dashboard import SerwerDashboard
        serwer_web = SerwerDashboard(port=getattr(cfg, "dashboard_port", 8777))
        if getattr(cfg, "webhook_tv", False):
            from imperium.swiatynie.webhook_tradingview import OdbiornikWebhook
            odbiornik_tv = OdbiornikWebhook()
            serwer_web.podepnij_webhook(odbiornik_tv)
            logger.info("[PętlaLive] W-354 Webhook TV aktywny → POST /webhook/tv")
        serwer_web.start()

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

            # 1b. W-354 Webhook TV — dołącz alerty z TradingView do bary_per.
            # Alert = jeden nowy bar → appendujemy na koniec historii danego symbolu.
            if odbiornik_tv is not None:
                for alert in odbiornik_tv.pobierz_wszystkie():
                    sym_tv = alert.symbol
                    bar_tv = alert.jako_bar()
                    bar_tv["symbol"] = sym_tv
                    bar_tv["interwal"] = alert.interwal
                    # timestamp z alertu lub now
                    try:
                        ts_tv = int(float(alert.czas)) if alert.czas else int(time.time() * 1000)
                    except (ValueError, TypeError):
                        import datetime as _dt
                        try:
                            ts_tv = int(_dt.datetime.fromisoformat(alert.czas.replace("Z", "+00:00")).timestamp() * 1000)
                        except Exception:
                            ts_tv = int(time.time() * 1000)
                    bar_tv["timestamp"] = ts_tv
                    if sym_tv not in bary_per:
                        bary_per[sym_tv] = []
                    bary_per[sym_tv].append(bar_tv)
                    # Zarejestruj dyrygenta dla nowego symbolu z TV (jeśli nieznany)
                    if sym_tv not in dyrygenci:
                        try:
                            dyrygenci[sym_tv] = _buduj_dyrygencie(sym_tv, cfg, engine, pamiec)
                            logger.info("[PętlaLive] W-354 Nowy symbol z TV: %s", sym_tv)
                        except Exception as e:
                            logger.warning("[PętlaLive] W-354 Nie udało się dodać %s: %s", sym_tv, e)

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

            # 2b. Cross-sectional RS (C-01, W-335) — z-score zwrotu vs koszyk.
            # Tylko pętla portfelowa widzi wszystkie symbole naraz. Bez koszyka (1 para)
            # → pusty dict → neuron C-01 abstynuje (Prawo XV).
            if len(bary_per) >= 2:
                try:
                    from imperium.legiony.przekroj_koszyka import cross_sectional_rs
                    close_koszyk = {s: [b["close"] for b in bs]
                                    for s, bs in bary_per.items()}
                    rs_map = cross_sectional_rs(close_koszyk, lookback=24)
                    for s, d in dyrygenci.items():
                        if s in rs_map:
                            d.kontekst_dodatkowy["CROSS_RS"] = rs_map[s]
                except Exception as e:
                    logger.warning(f"[PętlaLive] Cross-sectional RS padł: {e}")

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
                        if telegram is not None:
                            telegram.alert_sygnal(
                                symbol=sym,
                                kierunek=decyzja.kierunek,
                                pewnosc=decyzja.pewnosc,
                                rezim=decyzja.rezim,
                                kapital=engine.kapital_calkowity,
                            )
                    elif "WETO" in decyzja.etap:
                        statystyki.weta += 1
                        if decyzja.etap == "SENAT_WETO" and telegram is not None:
                            telegram.alert_weto(decyzja.powod, decyzja.rezim)
                    else:
                        statystyki.decyzje_neutralne += 1
                except Exception as e:
                    statystyki.bledy += 1
                    logger.error(f"[PętlaLive] Błąd cyklu {sym}: {e}")

            # 3b. Decay synaps (W-329, P4) — higiena pamięci: martwe pary łagodnie
            # wygasają. Bez tego silos synaps rośnie bez końca w długim live.
            if (cfg.synapsy and cfg.synapsy_decay_co_bar > 0
                    and bar_nr % cfg.synapsy_decay_co_bar == 0):
                for d in dyrygenci.values():
                    syn = getattr(getattr(d, "legatus", None), "synapsy", None)
                    if syn is not None:
                        try:
                            syn.zapomnij()
                        except Exception as e:
                            logger.warning(f"[PętlaLive] Decay synaps padł: {e}")

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

                # ML-36: karm bramkę konformalną per symbol wynikiem zamknięć (opt-in).
                if cfg.kalibruj_prog:
                    for w in nowe:
                        sym_w = getattr(w, "symbol", None)
                        d = dyrygenci.get(sym_w) if sym_w else None
                        if d is not None and getattr(d, "bramka_kalibr", None) is not None:
                            d.bramka_kalibr.zaktualizuj(getattr(w, "pnl_usdt", 0.0) > 0)

                # Arena auto-log (opt-in): realny PnL% każdego zamknięcia → baza areny.
                if cfg.arena_log:
                    try:
                        from imperium.biblioteki.arena_baza import zapisz_pomiar
                        for w in nowe:
                            if not hasattr(w, "pnl_pct"):
                                continue
                            sym = getattr(w, "symbol", None) or "ROJ"
                            rez = getattr(w, "rezim", None) or "NORMAL"
                            zapisz_pomiar("LIVE_PNL", str(sym), float(w.pnl_pct),
                                          nota=f"{cfg.interwal} {rez} bar{bar_nr}")
                    except Exception as e:
                        logger.warning(f"[PętlaLive] Arena auto-log padł: {e}")

            # 4b. Alerty Telegram dla nowych zamknięć
            hist_now_new = len(engine.historia_zamkniec)
            if telegram is not None and hist_now_new > statystyki._pamiec_zamkniec:
                nowe_zam = engine.historia_zamkniec[statystyki._pamiec_zamkniec:]
                for zam in nowe_zam:
                    if hasattr(zam, "pnl_pct"):
                        telegram.alert_zamkniecie(
                            symbol=getattr(zam, "symbol", "?"),
                            pnl_pct=zam.pnl_pct,
                            kapital=engine.kapital_calkowity,
                        )

            # 4c. LiveMonitor TUI render + Web dashboard (współdzielą StanDashboardu)
            if monitor is not None or serwer_web is not None:
                try:
                    from imperium.swiatynie.live_monitor import StanPozycji, StanDashboardu
                    from datetime import datetime
                    aktualny_rezim = (
                        list(dyrygenci.values())[0]._ostatni_rezim if dyrygenci else "NORMAL"
                    )
                    pozycje_tui = [
                        StanPozycji(
                            symbol=p.symbol,
                            kierunek=getattr(p, "kierunek", "?"),
                            wejscie=getattr(p, "cena_wejscia", 0.0),
                            aktualny=bary_per.get(p.symbol, [{}])[-1].get("close", 0.0),
                            wielkosc=getattr(p, "rozmiar_usdt", 0.0),
                            sl=getattr(p, "stop_loss", 0.0),
                            tp=getattr(p, "take_profit", 0.0),
                        )
                        for p in engine.otwarte.values()
                    ]
                    stan = StanDashboardu(
                        symbol=", ".join(cfg.symbole[:3]),
                        rezim=aktualny_rezim,
                        kapital=engine.kapital_calkowity,
                        kapital_start=cfg.kapital_startowy,
                        pozycje=pozycje_tui,
                        bary_przetworzone=statystyki.bary_przetworzone,
                        decyzje_wejscia=statystyki.decyzje_wejscia,
                        weta=statystyki.weta,
                        bledy=statystyki.bledy,
                        czas_ostatniego_bara=datetime.now(),
                    )
                    if monitor is not None:
                        monitor.aktualizuj(stan)
                        monitor.render()
                    if serwer_web is not None:
                        serwer_web.aktualizuj(stan)
                except Exception as e:
                    logger.debug(f"[PętlaLive] Monitor/dashboard render padł: {e}")

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

    # W-352: Zapisz stan uczenia (cross-session persistence)
    for sym, d in dyrygenci.items():
        try:
            leg = getattr(d, "legatus", None)
            if leg is None:
                continue
            mwu = getattr(leg, "mwu", None)
            if mwu is not None:
                sch = getattr(mwu, "_sciezka", None)
                if sch:
                    mwu.zapisz(sch)
            syn = getattr(leg, "synapsy", None)
            if syn is not None:
                syn.zapisz()
            ig = getattr(d, "_igrzyska", None)
            if ig is not None:
                sch = getattr(ig, "_sciezka", None)
                if sch:
                    ig.zapisz(sch)
        except Exception as e:
            logger.warning(f"[PętlaLive] Zapis stanu uczenia {sym} padł: {e}")
    logger.info("[PętlaLive] Stan uczenia zapisany (MWU/Igrzyska/Synapsy).")

    # Domknij otwarte po ostatniej cenie (paper mode)
    if cfg.paper:
        ostatnie = {}
        for sym, bary in bary_per.items():
            if bary:
                ostatnie[sym] = bary[-1]["close"]
        if ostatnie:
            engine.zamknij_wszystkie(ostatnie, powod="PETLA_STOP")

    if serwer_web is not None:
        serwer_web.stop()

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
