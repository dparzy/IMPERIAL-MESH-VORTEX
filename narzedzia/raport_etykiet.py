"""
🏷️ RAPORT ETYKIET — Triple-Barrier + CUSUM (López de Prado, W-357, AFML Ch.3-4).

Odkopuje `imperium/legiony/triple_barrier.py` (był gotowy, ale bez wejścia — Prawo XV).
Etykietuje serię cen metodą Triple-Barrier z barierami skalowanymi zmiennością, próbkuje
zdarzenia filtrem CUSUM i liczy sample-uniqueness (obserwacje z nakładającymi się oknami
NIE są IID — waga próbki = jej unikalność).

Po co (dla nowicjusza): naiwna etykieta „cena wzrosła w następnym barze = LONG" ignoruje
ścieżkę i zmienność. Triple-Barrier pyta „która bariera padła PIERWSZA (TP/SL/czas)" z
progami ×σ — uczciwsza prawda o tym, czy sygnał był dobry. To fundament pod trening ML.

Dane rynkowe LOKALNE (poza gitem) — uruchamiaj u siebie:
    python narzedzia/raport_etykiet.py dane/4h/Binance_BTCUSDT_4h.csv 4h
    python narzedzia/raport_etykiet.py dane/dzienne/Binance_ETHUSDT_d.csv 1d --k-tp 2 --k-sl 1
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def raport_z_close(close, k_tp: float = 2.0, k_sl: float = 1.0, max_hold: int = 20,
                   h_cusum: float = 0.01, zmiennosc_okno: int = 20) -> str:
    """Rdzeń (testowalny bez CSV): CUSUM → triple-barrier → statystyki + uniqueness."""
    from imperium.legiony.triple_barrier import (
        filtr_cusum,
        sample_uniqueness,
        statystyki_barier,
        triple_barrier,
    )
    if len(close) < zmiennosc_okno + 2:
        return "🏷️ RAPORT ETYKIET — za mało barów do etykietowania."
    zdarzenia = filtr_cusum(close, h=h_cusum)
    if not zdarzenia:
        return ("🏷️ RAPORT ETYKIET — CUSUM nie wykrył zdarzeń (próg h za wysoki?). "
                "Zmniejsz --h-cusum.")
    bariery = triple_barrier(close, zdarzenia, k_tp=k_tp, k_sl=k_sl,
                             max_hold=max_hold, zmiennosc_okno=zmiennosc_okno)
    st = statystyki_barier(bariery)
    uniq = sample_uniqueness(bariery, len(close))
    avg_uniq = sum(uniq) / len(uniq) if uniq else 0.0
    return "\n".join([
        f"🏷️ RAPORT ETYKIET (Triple-Barrier + CUSUM, W-357) — {st['n']} zdarzeń",
        f"   próbkowanie CUSUM h={h_cusum} | bariery: TP={k_tp}σ SL={k_sl}σ | max_hold={max_hold}",
        "",
        f"   TP (+1, dobry):   {st['tp_pct']:>5}%",
        f"   SL (-1, zły):     {st['sl_pct']:>5}%",
        f"   time-out (0):     {st['timeout_pct']:>5}%",
        f"   średni zysk/trade: {st['avg_zysk_pct']:+.3f}%",
        f"   avg uniqueness:    {avg_uniq:.3f}  (1.0=nienakładające się; <1 = koreluj wagi ML)",
    ])


def _wczytaj_close(plik: str, interwal: str) -> list:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    return [float(b["close"]) for b in wczytaj_csv(plik, interwal)]


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Raport etykiet Triple-Barrier (W-357)")
    p.add_argument("plik")
    p.add_argument("interwal")
    p.add_argument("--k-tp", type=float, default=2.0)
    p.add_argument("--k-sl", type=float, default=1.0)
    p.add_argument("--max-hold", type=int, default=20)
    p.add_argument("--h-cusum", type=float, default=0.01)
    args = p.parse_args()
    try:
        close = _wczytaj_close(args.plik, args.interwal)
    except Exception as e:  # noqa: BLE001
        print(f"Nie wczytano {args.plik}: {e}")
        sys.exit(1)
    print(raport_z_close(close, k_tp=args.k_tp, k_sl=args.k_sl,
                         max_hold=args.max_hold, h_cusum=args.h_cusum))
