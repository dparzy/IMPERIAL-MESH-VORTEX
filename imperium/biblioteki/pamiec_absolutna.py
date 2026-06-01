"""
Pamięć Absolutna — centralny system logowania Imperium.

Każdy sygnał, analiza, trade i test zostawia ImperiumLog.
Bez logu = bez dowodu. Lex Memoriae (Prawo IX).
"""

import uuid
import json
import os
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger("PamiecAbsolutna")

LOG_DIR = Path(os.getenv("IMPERIUM_LOG_DIR", "imperium/biblioteki/pamiec/logi"))


# ─── Typy logów ──────────────────────────────────────────────────────────────

class TypLogu:
    SYGNAL      = "SYGNAŁ"
    TRADE_OPEN  = "TRADE_OPEN"
    TRADE_CLOSE = "TRADE_CLOSE"
    ANALIZA     = "ANALIZA"
    TEST        = "TEST"
    SENAT       = "SENAT"
    WETO        = "WETO"
    IGRZYSKA    = "IGRZYSKA"
    DORADCY     = "DORADCY"


# ─── Główny rekord ────────────────────────────────────────────────────────────

@dataclass
class ImperiumLog:
    # Identyfikacja
    log_typ: str
    sesja_id: str
    symbol: str
    interwal: str

    # Kontekst rynku
    cena_close: float = 0.0
    cena_open: float = 0.0
    cena_high: float = 0.0
    cena_low: float = 0.0
    wolumen: float = 0.0
    rezim: str = "NORMAL"
    sesja_rynkowa: str = ""
    btc_dominacja: float = 0.0
    funding_rate: float = 0.0

    # Neurony
    neurony_aktywne: int = 0
    neurony_long: int = 0
    neurony_short: int = 0
    neurony_neutral: int = 0
    sygnaly_json: str = ""
    top3_long: str = ""
    top3_short: str = ""

    # Legatus
    legatus_kierunek: str = ""
    legatus_pewnosc: float = 0.0
    legatus_sila_long: float = 0.0
    legatus_sila_short: float = 0.0
    legatus_weto: bool = False
    legatus_powod_weta: str = ""

    # Senat
    senat_aktywny: bool = False
    senat_wynik: str = ""
    senat_populares: float = 0.0
    senat_optimates: float = 0.0
    senat_runda: int = 0

    # Plan pozycji
    plan_aktywny: bool = False
    kierunek_pozycji: str = ""
    cena_wejscia: float = 0.0
    dzwignia: int = 0
    cena_likwidacji: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    rozmiar_usdt: float = 0.0
    ryzyko_usdt: float = 0.0
    rr_ratio: float = 0.0

    # Trade execution
    trade_id: str = ""
    trade_status: str = "PAPER"
    cena_wykonania: float = 0.0
    slippage_pct: float = 0.0
    prowizja_usdt: float = 0.0
    kapital_przed: float = 0.0
    kapital_po: float = 0.0
    pnl_usdt: float = 0.0
    pnl_pct: float = 0.0
    czas_trwania_min: int = 0
    powod_zamkniecia: str = ""
    mae_pct: float = 0.0          # Maximum Adverse Excursion
    mfe_pct: float = 0.0          # Maximum Favorable Excursion

    # Źródła informacji
    kanaly_aktywne: str = ""
    on_chain_snapshot: str = ""
    sentyment_snapshot: str = ""
    macro_snapshot: str = ""

    # Jakość danych
    hash_sha256: str = ""
    bramka_wersja: str = "1.0"
    kompletnosc_danych: float = 1.0

    # Metadane systemu
    wersja_systemu: str = "v0.1.0"
    strategia_id: str = ""
    igrzyska_wagi: str = ""
    notatka: str = ""

    # Auto-generowane
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sekwencja: int = 0
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "ImperiumLog":
        return cls(**json.loads(s))


# ─── Zapisywacz ──────────────────────────────────────────────────────────────

class PamiecAbsolutna:
    """
    Centralny punkt zapisu wszystkich logów Imperium.

    Użycie:
        pamiec = PamiecAbsolutna()
        pamiec.zapisz(log)
        logi = pamiec.wczytaj(symbol="BTCUSDT", data="2026-06-01")
    """

    def __init__(self, katalog: Path = LOG_DIR):
        self.katalog = Path(katalog)
        self._sekwencja: Dict[str, int] = {}

    def _sciezka(self, symbol: str, typ: str, data: str) -> Path:
        rok, mies = data[:4], data[5:7]
        folder = self.katalog / rok / mies
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{data}_{symbol}_{typ.lower()}.jsonl"

    def _nastepna_sekwencja(self, sesja_id: str) -> int:
        self._sekwencja[sesja_id] = self._sekwencja.get(sesja_id, 0) + 1
        return self._sekwencja[sesja_id]

    def zapisz(self, log: ImperiumLog) -> str:
        """Zapisuje log do pliku JSONL. Zwraca log_id."""
        data = log.timestamp_utc[:10]
        log.sekwencja = self._nastepna_sekwencja(log.sesja_id)
        sciezka = self._sciezka(log.symbol, log.log_typ, data)
        with open(sciezka, "a", encoding="utf-8") as f:
            f.write(log.to_json() + "\n")
        logger.debug(f"[PA] {log.log_typ} {log.symbol} → {sciezka.name}")
        return log.log_id

    def wczytaj(self, symbol: str = "", data: str = "",
                log_typ: str = "") -> List[ImperiumLog]:
        """Wczytuje logi z pliku/folderu pasującego do kryteriów."""
        wyniki = []
        if not self.katalog.exists():
            return wyniki
        wzorzec = f"{data}*{symbol}*{log_typ.lower()}*".replace("**", "*")
        for plik in self.katalog.rglob("*.jsonl"):
            if self._pasuje(plik.name, symbol, data, log_typ):
                with open(plik, encoding="utf-8") as f:
                    for linia in f:
                        linia = linia.strip()
                        if linia:
                            try:
                                wyniki.append(ImperiumLog.from_json(linia))
                            except Exception as e:
                                logger.warning(f"Błąd parsowania logu: {e}")
        return wyniki

    def _pasuje(self, nazwa: str, symbol: str, data: str, log_typ: str) -> bool:
        if symbol and symbol.lower() not in nazwa.lower():
            return False
        if data and data not in nazwa:
            return False
        if log_typ and log_typ.lower() not in nazwa.lower():
            return False
        return True

    def podsumowanie_sesji(self, sesja_id: str,
                           logi: List[ImperiumLog]) -> Dict[str, Any]:
        """Generuje podsumowanie jednej sesji tradingowej."""
        tradingi = [l for l in logi if l.sesja_id == sesja_id
                    and l.log_typ == TypLogu.TRADE_CLOSE]
        if not tradingi:
            return {"sesja_id": sesja_id, "trade_count": 0}

        pnl_lista = [t.pnl_pct for t in tradingi]
        wygrane = [p for p in pnl_lista if p > 0]
        return {
            "sesja_id": sesja_id,
            "trade_count": len(tradingi),
            "win_rate": round(len(wygrane) / len(tradingi), 4),
            "avg_pnl_pct": round(sum(pnl_lista) / len(pnl_lista), 4),
            "total_pnl_pct": round(sum(pnl_lista), 4),
            "best_trade_pct": round(max(pnl_lista), 4),
            "worst_trade_pct": round(min(pnl_lista), 4),
            "avg_mae": round(sum(t.mae_pct for t in tradingi) / len(tradingi), 4),
            "avg_mfe": round(sum(t.mfe_pct for t in tradingi) / len(tradingi), 4),
        }


# ─── Fabryki logów (pomocnicze) ───────────────────────────────────────────────

def log_sygnal(sesja_id: str, symbol: str, interwal: str,
               raport, rezim: str = "NORMAL") -> ImperiumLog:
    """Tworzy log z RaportLegatusa."""
    sygnaly = [{"k": s.klucz, "d": s.kierunek, "p": round(s.pewnosc_finalna, 3),
                "w": s.waga} for s in raport.sygnaly]
    top_long = sorted([s for s in raport.sygnaly if s.kierunek == "LONG"],
                      key=lambda x: x.pewnosc_finalna * x.waga, reverse=True)[:3]
    top_short = sorted([s for s in raport.sygnaly if s.kierunek == "SHORT"],
                       key=lambda x: x.pewnosc_finalna * x.waga, reverse=True)[:3]
    return ImperiumLog(
        log_typ=TypLogu.SYGNAL,
        sesja_id=sesja_id,
        symbol=symbol,
        interwal=interwal,
        rezim=rezim,
        neurony_aktywne=raport.aktywnych_neuronow,
        neurony_long=len([s for s in raport.sygnaly if s.kierunek == "LONG"]),
        neurony_short=len([s for s in raport.sygnaly if s.kierunek == "SHORT"]),
        neurony_neutral=len([s for s in raport.sygnaly if s.kierunek == "NEUTRAL"]),
        sygnaly_json=json.dumps(sygnaly),
        top3_long=",".join(s.klucz for s in top_long),
        top3_short=",".join(s.klucz for s in top_short),
        legatus_kierunek=raport.kierunek,
        legatus_pewnosc=raport.pewnosc_agregatu,
        legatus_sila_long=raport.sila_long,
        legatus_sila_short=raport.sila_short,
        legatus_weto=raport.weto,
        legatus_powod_weta=raport.powod_weta,
    )


def log_trade_open(sesja_id: str, plan, kapital: float,
                   trade_id: str = "", status: str = "PAPER") -> ImperiumLog:
    """Tworzy log otwarcia pozycji z PlanPozycji."""
    return ImperiumLog(
        log_typ=TypLogu.TRADE_OPEN,
        sesja_id=sesja_id,
        symbol=plan.symbol,
        interwal="",
        plan_aktywny=True,
        kierunek_pozycji=plan.kierunek,
        cena_wejscia=plan.cena_wejscia,
        dzwignia=plan.dzwignia,
        cena_likwidacji=plan.cena_likwidacji,
        stop_loss=plan.stop_loss,
        take_profit=plan.take_profit,
        rozmiar_usdt=plan.rozmiar_usdt,
        ryzyko_usdt=plan.ryzyko_usdt,
        rr_ratio=plan.rr_ratio,
        trade_id=trade_id,
        trade_status=status,
        cena_wykonania=plan.cena_wejscia,
        kapital_przed=kapital,
    )


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    logging.basicConfig(level=logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmp:
        pamiec = PamiecAbsolutna(katalog=Path(tmp))
        sesja = str(uuid.uuid4())[:8]

        log1 = ImperiumLog(
            log_typ=TypLogu.SYGNAL,
            sesja_id=sesja,
            symbol="BTCUSDT",
            interwal="1H",
            rezim="TREND_STRONG",
            legatus_kierunek="LONG",
            legatus_pewnosc=0.78,
            neurony_aktywne=42,
            neurony_long=28,
            neurony_short=10,
            neurony_neutral=4,
        )
        pamiec.zapisz(log1)

        log2 = ImperiumLog(
            log_typ=TypLogu.TRADE_CLOSE,
            sesja_id=sesja,
            symbol="BTCUSDT",
            interwal="1H",
            pnl_pct=1.85,
            mae_pct=-0.4,
            mfe_pct=2.3,
            powod_zamkniecia="TP",
        )
        pamiec.zapisz(log2)

        wczytane = pamiec.wczytaj(symbol="BTCUSDT")
        print(f"\nZapisano i wczytano: {len(wczytane)} logów")
        for l in wczytane:
            print(f"  [{l.log_typ}] {l.symbol} {l.interwal} | "
                  f"kierunek={l.legatus_kierunek or '-'} | pnl={l.pnl_pct}%")
        print("\n✅ Pamięć Absolutna działa poprawnie")
