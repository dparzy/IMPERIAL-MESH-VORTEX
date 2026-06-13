"""
🧠 PAMIĘĆ REFLEKSYJNA — zamknięta pętla uczenia narracyjnego Brain (W-295).

Inspiracja: TradingAgents (arXiv:2412.20138 § 3.3 Memory Module),
FinMem (arXiv:2408.14900) — reflective memory dla LLM trading agentów.

DLA NOWICJUSZA: MWU (Multiplicative Weights Update) uczy się NUMERYCZNIE
(które neurony głosowały trafnie). Pamięć Refleksyjna dodaje uczenie NARRACYJNE:
po każdej serii zamkniętych transakcji zapisuje "lekcję" w czytelnej formie
i wstrzykuje ją do kolejnych promptów Senatu/Cesarza jako kontekst historyczny.

Przykładowa lekcja:
  "W reżimie RANGING z wysokim funding rate (PSY-01>0.05%) transakcje LONG
   traciły 3× więcej niż zyskały. Unikaj LONG gdy PSY-01 wysoki w RANGING."

Działa BEZ klucza API (zapisuje i odtwarza lekcje lokalnie w JSONL).
Z kluczem DeepSeek: kompresuje długoterminowe wzorce przez LLM.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


PLIK_DOMYSLNY = "logs/pamiec_refleksyjna.jsonl"


@dataclass
class Lekcja:
    """Jedna lekcja z doświadczenia rynkowego."""
    data: str                         # ISO timestamp UTC
    rezim: str                        # TRENDING/RANGING/VOLATILE/NORMAL
    interwal: str                     # 1D/4H/1H
    wynik: str                        # "ZYSK" | "STRATA"
    pnl_usdt: float
    n_transakcji: int
    win_rate: float
    kontekst: Dict[str, Any]          # dodatkowe dane (radar, neurony, etc.)
    lekcja_tekst: str                 # treść lekcji (auto lub DeepSeek)
    zrodlo: str                       # "auto" | "deepseek" | "manual"


class PamiecRefleksyjna:
    """
    Pamięć refleksyjna Imperium — dziennik lekcji rynkowych.

    Przechowuje wyniki sesji tradingowych jako ustrukturyzowane lekcje
    i dostarcza je do promptów Senatu/Cesarza jako kontekst historyczny.

    Analogia do TradingAgents: "Reflective long-term memory that distils
    patterns from historical trading sessions into actionable lessons."
    """

    def __init__(self, plik: str = PLIK_DOMYSLNY):
        self.plik = Path(plik)
        self.plik.parent.mkdir(parents=True, exist_ok=True)

    # ── zapis ─────────────────────────────────────────────────────────────────

    def zapisz_lekcje(self, lekcja: Lekcja) -> None:
        """Dopisuje lekcję do dziennika JSONL."""
        with self.plik.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(lekcja), ensure_ascii=False) + "\n")

    def zapisz_wynik(
        self,
        pnl_lista: List[float],
        rezim: str = "NORMAL",
        interwal: str = "1D",
        kontekst: Optional[Dict[str, Any]] = None,
        lekcja_tekst: Optional[str] = None,
    ) -> Lekcja:
        """
        Tworzy i zapisuje lekcję z listy P&L zamkniętych transakcji.
        Jeśli lekcja_tekst=None → generuje automatyczną narrację.
        """
        n = len(pnl_lista)
        laczny_pnl = sum(pnl_lista)
        wygrane = sum(1 for p in pnl_lista if p > 0)
        wr = wygrane / n if n > 0 else 0.0

        if lekcja_tekst is None:
            lekcja_tekst = _generuj_auto(pnl_lista, rezim, interwal)

        lekcja = Lekcja(
            data=datetime.utcnow().isoformat(),
            rezim=rezim,
            interwal=interwal,
            wynik="ZYSK" if laczny_pnl > 0 else "STRATA",
            pnl_usdt=round(laczny_pnl, 2),
            n_transakcji=n,
            win_rate=round(wr, 4),
            kontekst=kontekst or {},
            lekcja_tekst=lekcja_tekst,
            zrodlo="auto",
        )
        self.zapisz_lekcje(lekcja)
        return lekcja

    # ── odczyt ────────────────────────────────────────────────────────────────

    def wczytaj_wszystkie(self) -> List[Lekcja]:
        """Wczytuje wszystkie lekcje z pliku JSONL."""
        if not self.plik.exists():
            return []
        lekcje: List[Lekcja] = []
        with self.plik.open("r", encoding="utf-8") as f:
            for linia in f:
                linia = linia.strip()
                if linia:
                    try:
                        d = json.loads(linia)
                        lekcje.append(Lekcja(**d))
                    except Exception:
                        pass
        return lekcje

    def pobierz_lekcje(
        self,
        n: int = 5,
        rezim: Optional[str] = None,
        tylko_straty: bool = False,
    ) -> List[Lekcja]:
        """
        Zwraca N najnowszych lekcji (opcjonalnie filtrowane).
        Przeznaczony do wstrzyknięcia w prompt Senatu/Cesarza.
        """
        lekcje = self.wczytaj_wszystkie()
        if rezim:
            lekcje = [l for l in lekcje if l.rezim == rezim]
        if tylko_straty:
            lekcje = [l for l in lekcje if l.wynik == "STRATA"]
        return lekcje[-n:] if n > 0 else lekcje

    # ── formatowanie dla LLM ──────────────────────────────────────────────────

    def formatuj_dla_llm(
        self,
        n: int = 5,
        rezim: Optional[str] = None,
    ) -> str:
        """
        Formatuje lekcje jako tekst do wstrzyknięcia w prompt LLM.
        Kompatybilne z formatem promptu Senatu/Cesarza.
        """
        lekcje = self.pobierz_lekcje(n=n, rezim=rezim)
        if not lekcje:
            return "Brak historycznych lekcji rynkowych."
        linie = ["=== LEKCJE Z PRZESZŁOŚCI ==="]
        for i, l in enumerate(lekcje, 1):
            linie.append(
                f"{i}. [{l.data[:10]}] {l.rezim}/{l.interwal} → {l.wynik} "
                f"(PnL: {l.pnl_usdt:+.1f}$, WR: {l.win_rate:.0%}): {l.lekcja_tekst}"
            )
        linie.append("=== KONIEC LEKCJI ===")
        return "\n".join(linie)

    # ── statystyki ────────────────────────────────────────────────────────────

    def statystyki(self) -> Dict[str, Any]:
        """Podstawowe statystyki dziennika lekcji."""
        lekcje = self.wczytaj_wszystkie()
        if not lekcje:
            return {"n_lekcji": 0, "lacznie_pnl": 0.0, "win_rate_historii": 0.0,
                    "rezim_czestotliwosc": {}}
        laczny = sum(l.pnl_usdt for l in lekcje)
        zyski = sum(1 for l in lekcje if l.pnl_usdt > 0)
        rezim_cnt: Dict[str, int] = {}
        for l in lekcje:
            rezim_cnt[l.rezim] = rezim_cnt.get(l.rezim, 0) + 1
        return {
            "n_lekcji": len(lekcje),
            "lacznie_pnl": round(laczny, 2),
            "win_rate_historii": round(zyski / len(lekcje), 4),
            "rezim_czestotliwosc": rezim_cnt,
        }

    def wyczysc(self) -> None:
        """Usuwa wszystkie lekcje (NIEODWRACALNE — tylko do testów/resetu)."""
        if self.plik.exists():
            self.plik.unlink()


# ─── helpers ──────────────────────────────────────────────────────────────────

def _generuj_auto(pnl_lista: List[float], rezim: str, interwal: str) -> str:
    """Generuje automatyczną narrację lekcji bez LLM."""
    n = len(pnl_lista)
    if n == 0:
        return f"Pusta seria w {rezim}/{interwal}."
    laczny = sum(pnl_lista)
    wygrane = sum(1 for p in pnl_lista if p > 0)
    wr = wygrane / n
    najlepsza = max(pnl_lista)
    najgorsza = min(pnl_lista)

    if laczny > 0:
        return (
            f"Seria {n} transakcji w {rezim}/{interwal}: zysk {laczny:+.1f}$, "
            f"WR={wr:.0%}. Najlepsza: +{najlepsza:.1f}$, najgorsza: {najgorsza:.1f}$. "
            f"System działał zgodnie z oczekiwaniami w tym reżimie."
        )
    return (
        f"Seria {n} transakcji w {rezim}/{interwal}: STRATA {laczny:+.1f}$, "
        f"WR={wr:.0%}. Najlepsza: +{najlepsza:.1f}$, najgorsza: {najgorsza:.1f}$. "
        f"Rozważ zmniejszenie wagi lub przegląd parametrów dla {rezim}/{interwal}."
    )
