"""
👁️ WALIDACJA ZMYSŁÓW — czy adaptery faktycznie BUDZĄ neurony na ŻYWYCH danych (Prawo XV).

PROBLEM (Prawo XV — utrata potencjału):
  Audyt statyczny (`audyt_spojnosci.py`) odpala rój na scenariuszach SYNTETYCZNYCH bez
  sieci — więc PSY-01..04 / NEWS-01..04 / V-03 / OC-06..08 / RADAR abstynują i lądują na
  liście „czekają na adaptery (22)". To NIE dowodzi, że są martwe — dowodzi tylko, że audyt
  nie ma danych. Ten sam neuron na REALNYM funding/fear&greed/nagłówku/dacie ODDAJE GŁOS.

CO ROBI TO NARZĘDZIE (pomiar, nie opinia):
  Uruchamia CAŁY rój DWA razy na tej samej serii cen (realny timestamp → on-chain ożywa):
    1. BAZA     — same wskaźniki OHLCV (Budowniczy), bez adapterów
    2. ZMYSŁY   — OHLCV + wszystkie żywe adaptery (Futures/FearGreed/CVD/News RSS)
  RÓŻNICA aktywnych głosów = dokładnie to, co ZMYSŁY odblokowały. Dla każdego neuronu
  sensorycznego raportuje: GŁOS (kierunek+pewność) albo ABSTYNUJE (+powód z samego neuronu).

INTERPRETACJA:
  • GŁOS na żywych danych              → zmysł DZIAŁA, potencjał wykorzystany ✅
  • ABSTYNUJE z powodem (próg/1. bar)  → legalne milczenie (Prawo XV — cisza ≠ martwy głos)
  • ABSTYNUJE mimo obecnego klucza     → 🚨 kandydat na martwy głos (do zbadania)
  • Adapter padł (brak sieci)          → nie walidujemy — zgłoś offline, nie zgaduj (Prawo I)

Użycie (na LAPTOPIE z siecią — w chmurze endpointy bywają niedostępne):
  python narzedzia/waliduj_zmysly.py                 # BTCUSDT, wszystkie zmysły
  python narzedzia/waliduj_zmysly.py --symbol ETHUSDT
  python narzedzia/waliduj_zmysly.py --bez-sieci     # tylko on-chain (realna data, bez API)
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Neurony sensoryczne: ich dane pochodzą z adapterów / realnej daty, nie z czystego OHLCV.
# (KATALOG_NEURONOW: R=sentyment/reżim, N=informacja; V-03=CVD flow; OC=on-chain BTC.)
KLUCZE_SENSORYCZNE = {
    "PSY-01", "PSY-02", "PSY-03", "PSY-04",         # futures + fear&greed
    "NEWS-01", "NEWS-02", "NEWS-03", "NEWS-04",     # news RSS/LLM
    "V-03",                                          # CVD (flow)
    "OC-06", "OC-07", "OC-08",                       # on-chain BTC (realny timestamp)
    "RADAR-01", "RADAR-02", "RADAR-03", "RADAR-04", "RADAR-05",  # kontekst BTC (pętla portfelowa)
}


def _bary_realny_timestamp(n: int = 360, baza_px: float = 63000.0) -> list:
    """Seria świec z REALNYM timestampem (on-chain neurony liczą prawdziwy block height).

    Cena syntetyczna — celowo: walidujemy WKŁAD ZMYSŁÓW (adaptery/data), nie sygnał cenowy.
    Neurony cenowe głosują identycznie w BAZA i ZMYSŁY, więc znoszą się w różnicy.
    """
    ts_now = int(time.time() * 1000)
    bary = []
    for i in range(n):
        ts = ts_now - (n - i) * 4 * 3600 * 1000  # świece 4h wstecz
        px = baza_px + 500 * math.sin(i / 20)
        bary.append({
            "timestamp": ts, "open": px, "high": px * 1.01, "low": px * 0.99,
            "close": px, "volume": 1000 + i, "symbol": "BTCUSDT", "interwal": "4h",
        })
    return bary


def _zbuduj_adaptery(bez_sieci: bool) -> list:
    """Żywe adaptery sentymentu/flow (identyczny zestaw co petla_live._buduj_dyrygencie)."""
    if bez_sieci:
        return []
    from imperium.akwedukty.adaptery import (
        AdapterFutures, AdapterFearGreed, AdapterCVD, AdapterNewsLLM,
    )
    from imperium.akwedukty.news_fetcher import FetcherNewsRSS
    return [
        AdapterFutures(), AdapterFearGreed(), AdapterCVD(),
        AdapterNewsLLM(fetcher=FetcherNewsRSS()),
    ]


def _kierunek(sygnal) -> str:
    return str(sygnal.kierunek).replace("Kierunek.", "")


def waliduj(symbol: str = "BTCUSDT", bez_sieci: bool = False) -> dict:
    """Odpala rój BAZA vs ZMYSŁY, zwraca raport wkładu zmysłów (Prawo XV)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.mikro_neuron import Roj

    bary = _bary_realny_timestamp()
    wsk_baza = BudowniczyWskaznikow().zbuduj(bary)

    # ZMYSŁY: kopia bazy + adaptery dolewają klucze API. Adapter, który padnie, jest
    # pomijany (wzbogac() bezpieczny) — offline nie wywala walidacji, tylko zawęża zakres.
    wsk_zmysly = dict(wsk_baza)
    adaptery = _zbuduj_adaptery(bez_sieci)
    zywe_adaptery, martwe_adaptery = [], []
    for a in adaptery:
        nazwa = getattr(a, "NAZWA", type(a).__name__)
        klucze_przed = set(wsk_zmysly)
        try:
            a.wzbogac(wsk_zmysly, symbol)
            nowe = set(wsk_zmysly) - klucze_przed
            (zywe_adaptery if nowe else martwe_adaptery).append((nazwa, sorted(nowe)))
        except Exception as e:  # noqa: BLE001 — raportujemy, nie przerywamy walidacji
            martwe_adaptery.append((nazwa, [f"PADŁ: {e}"]))

    neurony = wszystkie_neurony()
    syg_baza = {s.neuron_id: s for s in Roj(neurony).zbierz_sygnaly(wsk_baza)}
    syg_zmysly = {s.neuron_id: s for s in Roj(neurony).zbierz_sygnaly(wsk_zmysly)}

    def _aktywne(syg: dict) -> set:
        return {k for k, s in syg.items() if _kierunek(s) != "NEUTRAL"}

    odblokowane = sorted(_aktywne(syg_zmysly) - _aktywne(syg_baza))

    # Szczegóły per neuron sensoryczny
    detale = []
    for n in neurony:
        if n.KLUCZ not in KLUCZE_SENSORYCZNE:
            continue
        s = syg_zmysly.get(n.KLUCZ)
        if s is None:
            detale.append((n.KLUCZ, n.WSKAZNIK, "POMINIĘTY", 0.0, "neuron wyciszony (DOSTEPNY=False)"))
            continue
        kier = _kierunek(s)
        powod = (s.powody[0] if getattr(s, "powody", None) else "")
        detale.append((n.KLUCZ, n.WSKAZNIK, kier, s.pewnosc, powod))

    return {
        "symbol": symbol,
        "bez_sieci": bez_sieci,
        "zywe_adaptery": zywe_adaptery,
        "martwe_adaptery": martwe_adaptery,
        "odblokowane": odblokowane,
        "detale": detale,
        "aktywne_baza": len(_aktywne(syg_baza)),
        "aktywne_zmysly": len(_aktywne(syg_zmysly)),
    }


def _drukuj(r: dict) -> None:
    print("=" * 70)
    print(f"👁️  WALIDACJA ZMYSŁÓW — {r['symbol']}"
          f"{'  [BEZ SIECI: tylko on-chain]' if r['bez_sieci'] else ''}")
    print("=" * 70)

    print("\n🔌 Adaptery (żywe = dostarczyły klucze):")
    for nazwa, klucze in r["zywe_adaptery"]:
        print(f"   ✅ {nazwa:28} → {', '.join(klucze)}")
    for nazwa, info in r["martwe_adaptery"]:
        print(f"   ❌ {nazwa:28} → {', '.join(info) or 'brak nowych kluczy'}")
    if not r["zywe_adaptery"] and not r["martwe_adaptery"]:
        print("   (adaptery pominięte — tryb --bez-sieci)")

    print(f"\n🧠 Aktywne głosy roju: BAZA {r['aktywne_baza']} → ZMYSŁY {r['aktywne_zmysly']}"
          f"  (+{r['aktywne_zmysly'] - r['aktywne_baza']} odblokowanych)")
    if r["odblokowane"]:
        print(f"   Odblokowane przez zmysły: {', '.join(r['odblokowane'])}")

    print("\n📡 Neurony sensoryczne (na żywych danych):")
    for klucz, wskaznik, kier, pewnosc, powod in r["detale"]:
        ikona = "🟢" if kier not in ("NEUTRAL", "POMINIĘTY") else ("⚪" if kier == "NEUTRAL" else "💤")
        stan = f"{kier:8} pewność={pewnosc:.2f}" if kier not in ("POMINIĘTY",) else "wyciszony"
        print(f"   {ikona} {klucz:8} {wskaznik:24} {stan}")
        if powod:
            print(f"        └─ {powod[:78]}")

    print()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Walidacja zmysłów Imperium (Prawo XV)")
    p.add_argument("--symbol", default="BTCUSDT", help="Symbol do walidacji (domyślnie BTCUSDT)")
    p.add_argument("--bez-sieci", action="store_true",
                   help="Pomiń adaptery API — waliduj tylko on-chain na realnej dacie")
    args = p.parse_args(argv)

    logging.disable(logging.CRITICAL)  # wycisz gadatliwą Bramę — chcemy czysty raport
    r = waliduj(symbol=args.symbol, bez_sieci=args.bez_sieci)
    _drukuj(r)

    # Kod wyjścia: 0 zawsze (to raport diagnostyczny, nie bramka). Sygnał „coś śpi mimo
    # sieci" idzie wizualnie (💤/⚪), bo powód milczenia bywa w pełni legalny (Prawo XV).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
