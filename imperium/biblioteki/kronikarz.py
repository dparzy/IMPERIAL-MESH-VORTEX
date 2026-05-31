"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Kronikarz (The Chronicler) — Logi i Dziennik Postępu v1.0             ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                            ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-LOG-001  (nowa kategoria LOG — do potwierdzenia w ZBADANE) |
| Nazwa oryginalna    | Chronicler (oryginał Kingdom Pixel)                         |
| Nazwa w Imperium    | Kronikarz                                                    |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/LOG-001_Kronikarz.py                |
| Kategoria           | LOG / Raportowanie i dziennik postępu                       |
| Wpływ na Imperium   | MOST DIAGNOZY: po każdym biegu pisze raport (JSON+MD), który |
|                     | Komendant wgrywa, a Jack czyta i kalibruje. Dziennik pokazuje|
|                     | postęp wersja-po-wersji. (Data Lineage — Prawo XIII.)        |
| Powiązane moduły    | N-STRAT-001 (paper-bot), N-MEM-206 (Mnemosyne), N-BACK-210  |

────────────────────────── PO CO TO (dla Komendanta) ───────────────────────────────
Jack nie pamięta między sesjami. Kronikarz to most: bot oddaje wyniki Kronikarzowi,
ten zapisuje je do plików. Ty wgrywasz pliki następną sesją, Jack czyta i mówi
co poprawić. Dziennik (DZIENNIK_WYNIKOW.md) dokleja każdy bieg → widać postęp.

CHANGELOG:
  v1.0 (2026-05-28) — raport biegu (JSON + czytelny MD), dziennik skumulowany,
        rejestr wersji i parametrów (żeby wiedzieć, co dało jaki wynik).
═════════════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("Kronikarz")


@dataclass
class RunReport:
    """Pełny ślad jednego biegu bota."""
    bot: str
    version: str
    params: Dict[str, Any]
    data_source: str                 # np. "MEXC BTC/USDT 1h" lub "SYNTETYCZNE"
    trades: List[Dict[str, Any]] = field(default_factory=list)
    start_capital: float = 0.0
    end_capital: float = 0.0
    win_rate: float = 0.0
    benchmark_pct: float = 0.0       # "kup i trzymaj" — uczciwy punkt odniesienia
    max_drawdown: float = 0.0        # najgłębszy zjazd kapitału od szczytu (ryzyko)
    halted_reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def return_pct(self) -> float:
        if self.start_capital <= 0:
            return 0.0
        return (self.end_capital - self.start_capital) / self.start_capital

    @property
    def beats_benchmark(self) -> bool:
        return self.return_pct > self.benchmark_pct


class Kronikarz:
    def __init__(self, out_dir: str = "."):
        self.out_dir = out_dir
        self.journal_path = os.path.join(out_dir, "DZIENNIK_WYNIKOW.md")

    def zapisz(self, report: RunReport) -> Dict[str, str]:
        """Zapisuje raport JSON + MD i dokleja wpis do dziennika. Zwraca ścieżki."""
        stamp = report.timestamp.replace(":", "-").split(".")[0]
        base = f"raport_biegu_{report.bot}_{stamp}"
        json_path = os.path.join(self.out_dir, base + ".json")
        md_path = os.path.join(self.out_dir, base + ".md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._render_md(report))

        self._append_journal(report)
        logger.info(f"[Kronikarz] Raport zapisany: {os.path.basename(md_path)} (+ .json) i dopisany do dziennika.")
        return {"json": json_path, "md": md_path, "journal": self.journal_path}

    def _render_md(self, r: RunReport) -> str:
        lines = [
            f"# 📋 Raport biegu — {r.bot} {r.version}",
            f"> {r.timestamp} | Dane: {r.data_source}",
            "",
            "## Wynik",
            f"- Kapitał: ${r.start_capital:.2f} → ${r.end_capital:.2f} (**{r.return_pct:+.1%}**)",
            f"- Kup i trzymaj (benchmark): {r.benchmark_pct:+.1%} → "
            f"{'POBITY ✅' if r.beats_benchmark else 'PRZEGRANY ❌ (gorzej niż samo trzymanie)'}",
            f"- Transakcje: {len(r.trades)} | Win rate: {r.win_rate:.1%}",
            f"- Max drawdown (najgłębszy zjazd): **-{r.max_drawdown:.1%}**",
            f"- Zatrzymanie: {r.halted_reason or 'brak (bieg do końca)'}",
            "",
            "## Parametry",
        ]
        for k, v in r.params.items():
            lines.append(f"- {k}: {v}")
        lines += ["", "## Transakcje (dla diagnozy Jacka)"]
        if r.trades:
            lines.append("| # | wejście | wyjście | wynik | powód |")
            lines.append("|:--|:--|:--|:--|:--|")
            for i, t in enumerate(r.trades, 1):
                lines.append(f"| {i} | {t.get('entry','?')} | {t.get('exit','?')} | "
                             f"{t.get('pnl_pct','?')}% | {t.get('reason','?')} |")
        else:
            lines.append("Brak transakcji w tym biegu.")
        lines += ["", "---", "*Wgraj ten plik następną sesją — Jack go przeczyta i doradzi kalibrację.*"]
        return "\n".join(lines)

    def _append_journal(self, r: RunReport):
        new = not os.path.exists(self.journal_path)
        with open(self.journal_path, "a", encoding="utf-8") as f:
            if new:
                f.write("# 📓 DZIENNIK WYNIKÓW — Kingdom Pixel\n")
                f.write("> Skumulowany postęp wszystkich biegów. Najnowsze na dole.\n\n")
                f.write("| Data | Bot | Wersja | Dane | Transakcje | WR | Zwrot | B&H | Werdykt | MaxDD | Pauzy/stop |\n")
                f.write("|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|\n")
            f.write(f"| {r.timestamp.split('T')[0]} | {r.bot} | {r.version} | {r.data_source} | "
                    f"{len(r.trades)} | {r.win_rate:.0%} | {r.return_pct:+.1%} | {r.benchmark_pct:+.0%} | "
                    f"{'✅ pobity' if r.beats_benchmark else '❌ gorzej'} | -{r.max_drawdown:.0%} | {r.halted_reason or '—'} |\n")


def main():
    logger.info("=== Kronikarz v1.0 Demo ===")
    # Przykładowe wyniki biegu (w praktyce poda je bot)
    report = RunReport(
        bot="PaperBot", version="v1.0",
        params={"rsi_low": 35, "rsi_high": 65, "ema_period": 50, "stop_pct": 0.03, "take_pct": 0.05},
        data_source="SYNTETYCZNE (offline)",
        start_capital=50.0, end_capital=45.16, win_rate=0.0,
        halted_reason="AegisShield CIRCUIT_BREAKER (3 straty)",
        trades=[
            {"entry": 63613, "exit": 61414, "pnl_pct": -3.5, "reason": "STOP"},
            {"entry": 59850, "exit": 57017, "pnl_pct": -4.7, "reason": "STOP"},
            {"entry": 59209, "exit": 58144, "pnl_pct": -1.8, "reason": "cena<EMA"},
        ],
    )
    k = Kronikarz(out_dir=os.path.dirname(os.path.abspath(__file__)))
    paths = k.zapisz(report)
    logger.info(f"Pliki: {os.path.basename(paths['md'])}, {os.path.basename(paths['json'])}, {os.path.basename(paths['journal'])}")
    print("\n✅ Kronikarz v1.0 — demo zakończone. Raporty gotowe do wgrania Jackowi.")


if __name__ == "__main__":
    main()
