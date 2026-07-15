"""
📋 CENZUS ADAPTERÓW (Prawo XV) — spis żywych modułów adapterowych na REALNYCH danych.

Rzymski Censor przeprowadzał census: spis obywateli/żołnierzy — kto OBECNY i SPRAWNY.
To narzędzie robi to samo dla 22 modułów zależnych od adapterów (funding, news, CVD,
futures, radar-koszyk, on-chain, MTF), które audyt syntetyczny oznacza jako
„ŻYWE ale niezmierzone" — bo ciche w scenariuszach audytu bez żywych feedów.

DOWÓD, NIE ZAŁOŻENIE (Prawo I): pobiera realny OHLCV z giełdy (ccxt/MEXC), wpina
publiczne adaptery (jak petla_live), wstrzykuje kontekst radaru + cross-RS koszyka,
uruchamia realny cykl decyzyjny per symbol z rozgrzewką (stan kroczący NEWS W-382
ożywa po ≥2 barach) i sprawdza, które moduły produkują głos z NIEPUSTĄ wartością.

Moduł = ŻYWY, gdy w choć jednym symbolu produkuje SygnalNeuronu.wartosc is not None.
Moduł = CICHY warunkowo, gdy bramka projektowa nie jest spełniona TERAZ (brak zdarzenia
dla AUG-01; |lead-lag| < 0.20 dla RADAR-05) — Prawo I zabrania fabrykować warunek.

Uruchom:  python narzedzia/cenzus_adapterow.py
Opcje:    --symbole BTCUSDT ETHUSDT ...  --interwal 1H  --rozgrzewka 2  --arena
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 22 moduły zależne od adapterów (Prawo XV — audyt_spojnosci.py --luki).
CELE = [
    "AUG-01", "C-01", "NEWS-01", "NEWS-02", "NEWS-03", "NEWS-04",
    "OC-06", "OC-07", "OC-08", "PSY-01", "PSY-02", "PSY-03", "PSY-04",
    "RADAR-01", "RADAR-02", "RADAR-03", "RADAR-04", "RADAR-05",
    "V-03", "X-28", "Z-06", "Z-07",
]

# Powody warunkowej ciszy (bramka projektowa — Prawo I: nie fabrykujemy warunku).
POWODY_WARUNKOWE = {
    "AUG-01": "bramka zdarzenia: żywy dopiero w oknie zdarzenia fundamentalnego (EVENT_*)",
    "RADAR-05": "bramka siły: LEAD_BTC liczony gdy |lead-lag| ≥ 0.20 (filar siły, Prawo XVI)",
    "NEWS-03": "stan kroczący W-382: ożywa po ≥2 barach z feedem (rozgrzewka)",
    "NEWS-04": "stan kroczący W-382: ożywa po ≥2 barach z feedem (rozgrzewka)",
}


def _pasek(i, n, opis):
    """Pasek postępu na stderr (Prawo XXIV — widoczność operacyjna)."""
    print(f"\r[{i}/{n}] {opis:<44}", end="", file=sys.stderr, flush=True)
    if i == n:
        print("", file=sys.stderr, flush=True)


def main():
    p = argparse.ArgumentParser(description="Cenzus żywych modułów adapterowych (Prawo XV).")
    p.add_argument("--symbole", nargs="+",
                   default=["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"],
                   help="koszyk par (≥2 dla RADAR/cross-RS; domyślnie 5)")
    p.add_argument("--interwal", default="1H", help="interwał świec (domyślnie 1H)")
    p.add_argument("--limit", type=int, default=400, help="ile barów historii (domyślnie 400)")
    p.add_argument("--rozgrzewka", type=int, default=2,
                   help="ile cykli rozgrzewki (stan kroczący NEWS; domyślnie 2)")
    p.add_argument("--arena", action="store_true",
                   help="zapisz pomiar do arena_wyniki.db (rodzaj=XV_ZYWY)")
    args = p.parse_args()

    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    logging.disable(logging.WARNING)

    from imperium.koloseum.petla_live import (
        KonfigPetliLive, _buduj_dyrygencie, _df_do_barow,
    )
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.akwedukty.kwatermistrz_danych import DataLoader
    from imperium.legiony.radar_rynku import RadarRynku
    from imperium.legiony.przekroj_koszyka import cross_sectional_rs

    symbole = args.symbole
    n_sym = len(symbole)
    print(f"📋 CENZUS ADAPTERÓW (Prawo XV) — {n_sym} par {args.interwal}, "
          f"rozgrzewka {args.rozgrzewka} cykli. Dowód na żywych danych.\n")

    cfg = KonfigPetliLive(symbole=symbole, interwal=args.interwal,
                          limit_barow=args.limit, synapsy=False, auto_rezim=True)
    engine = PaperTradingEngine(kapital_startowy=10000.0, sesja_id="CENZUS-XV",
                                max_otwartych=n_sym, log_dir="logs")
    dyrygenci = _buduj_dyrygencie(symbole, cfg, engine)
    loader = DataLoader()
    radar = RadarRynku()

    # 1. Fetch realnego OHLCV (pasek postępu)
    bary_per = {}
    for i, sym in enumerate(symbole, 1):
        _pasek(i, n_sym, f"fetch {sym}")
        try:
            df = loader.fetch(sym, args.interwal, limit=args.limit)
            bary_per[sym] = _df_do_barow(df, sym, args.interwal)
        except Exception as e:
            print(f"\n  ⚠️  {sym}: fetch padł: {e}", file=sys.stderr)
    if not bary_per:
        print("❌ Brak danych z giełdy — cenzus niemożliwy (Prawo I: nie zgadujemy).")
        return 1

    # 2. Radar (kontekst BTC) — jak w petla_live
    btc = next((s for s in bary_per if s.upper().startswith("BTC")), None)
    if btc and len(bary_per) >= 2:
        close_btc = [b["close"] for b in bary_per[btc]]
        close_alty = {s: [b["close"] for b in bs] for s, bs in bary_per.items() if s != btc}
        vol_alty = {s: [b["volume"] for b in bs] for s, bs in bary_per.items() if s != btc}
        try:
            stan = radar.skanuj(close_btc, close_alty, vol_alty)
            for d in dyrygenci.values():
                d.stan_rynku = stan
                d.kontekst_dodatkowy.update(stan.jako_wskazniki())
        except Exception as e:
            print(f"  ⚠️  Radar padł: {e}", file=sys.stderr)

    # 3. Cross-sectional RS (C-01)
    if len(bary_per) >= 2:
        try:
            close_koszyk = {s: [b["close"] for b in bs] for s, bs in bary_per.items()}
            rs_map = cross_sectional_rs(close_koszyk, lookback=24)
            for s, d in dyrygenci.items():
                if s in rs_map:
                    d.kontekst_dodatkowy["CROSS_RS"] = rs_map[s]
        except Exception as e:
            print(f"  ⚠️  Cross-RS padł: {e}", file=sys.stderr)

    # 4. Cykle (rozgrzewka + pomiar) — union żywych po wszystkich cyklach/symbolach.
    # wartosc not None w choć jednym → ŻYWY (rolling NEWS ożywa od 2. cyklu).
    zebrane = {k: [] for k in CELE}   # klucz → [(sym, wartosc, kierunek)]
    n_cykli = args.rozgrzewka + 1
    krok = 0
    total = n_cykli * len(bary_per)
    for c in range(n_cykli):
        for sym, bary in bary_per.items():
            krok += 1
            faza = "rozgrzewka" if c < args.rozgrzewka else "POMIAR"
            _pasek(krok, total, f"{faza} cykl {c+1} — {sym}")
            try:
                dec = dyrygenci[sym].cykl(sym, bary, rezim="AUTO",
                                          timestamp=bary[-1]["timestamp"])
            except Exception as e:
                print(f"\n  ⚠️  cykl {sym} padł: {e}", file=sys.stderr)
                continue
            rap = getattr(dec, "raport", None)
            if rap is None or not rap.sygnaly:
                continue
            idx = {s.neuron_id: s for s in rap.sygnaly}
            for cel in CELE:
                for nid, s in idx.items():
                    if (nid == cel or nid.startswith(cel + "_")) and s.wartosc is not None:
                        zebrane[cel].append((sym, s.wartosc, s.kierunek))

    # 5. Raport + arena
    print("\n" + "=" * 74)
    print(" CENZUS 22 MODUŁÓW ADAPTEROWYCH — DOWÓD NA ŻYWYCH DANYCH (Prawo XV)")
    print("=" * 74)
    zywe, ciche = [], []
    wiersze_arena = []
    for cel in CELE:
        obs = zebrane[cel]
        if obs:
            zywe.append(cel)
            sym0, w0, k0 = obs[0]
            kier = sorted({k for _, _, k in obs})
            print(f"  ✅ {cel:9} ŻYWY   głosów={len(obs):<3} np. {sym0}={w0:+.4g} [{k0}]  kier={kier}")
            wiersze_arena.append(("XV_ZYWY", cel, float(w0),
                                  f"{args.interwal} n={len(obs)} kier={kier}"))
        else:
            ciche.append(cel)
            powod = POWODY_WARUNKOWE.get(cel, "brak danych z adaptera w tym oknie")
            print(f"  ⏸️  {cel:9} CICHY  — {powod}")

    print("=" * 74)
    print(f" ŻYWE: {len(zywe)}/22   |   CICHE (warunkowo): {len(ciche)}/22")
    if ciche:
        print(f" Ciche: {', '.join(ciche)} (bramki projektowe — Prawo I nie fabrykuje warunku)")

    if args.arena and wiersze_arena:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        n = zapisz_pomiary(wiersze_arena)
        print(f"\n 💾 Arena: zapisano {n} pomiarów (rodzaj=XV_ZYWY) do arena_wyniki.db")

    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
