"""
🖋️ SCRIBA CODEX PROBATIONUM — skryba, który dopisuje wyniki testów do ledgera.

Rzymski *scriba* = urzędnik-pisarz prowadzący oficjalne rejestry (acta). Tutaj:
jedyny, reużywalny appender do `bibliotheca_ulpia/dane/rejestr_testow.jsonl` —
wersjonowanego źródła prawdy wyników A/B i IC, z którego CODEX_PROBATIONUM.xlsx
generuje arkusze (patrz narzedzia/codex_probationum.py).

CEL (ROZKAZ CODEX, Cezar 2026-07-18): narzędzia A/B i pomiar-IC dopisują wynik do
ledgera SAM (flaga --ledger), żeby CODEX rósł bez ręcznego wklejania linii JSON.

GWARANCJE:
- **Append-only** (Prawo I: nic nie kasujemy) — nowy pomiar = nowa linia.
- **Idempotentny** — dwa identyczne biegi (te same parametry, ten sam wynik, ten
  sam dzień) NIE mnożą linii: identyczny rekord jest pomijany. Inny wynik/inny dzień
  = nowa linia (historia pomiarów, o to chodzi w rejestrze testów).
- **Klucze zgodne ze schematem** czytanym przez codex_probationum (Prawo XXI): AB i IC
  mają dokładnie te pola, których oczekuje generator arkuszy.

Nie liczy niczego — tylko formatuje i dopisuje. Pomiar robi narzędzie wołające.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "bibliotheca_ulpia" / "dane" / "rejestr_testow.jsonl"

# Kolejność pól = schemat czytany przez codex_probationum (Prawo XXI: bez aliasów).
POLA_AB = ("typ", "sygnal", "neuron", "interwal", "okno_barow", "roi_b", "roi_a",
           "delta_pp", "maxdd_delta", "werdykt", "data", "zrodlo", "uwaga")
POLA_IC = ("typ", "sygnal", "neuron", "horyzont", "ic", "tryb", "prog", "werdykt",
           "kierunek", "data", "zrodlo", "uwaga")


def _dzis() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _wczytaj(sciezka: Path) -> list[dict]:
    """Czyta ledger (jeden rekord na linię). Brak pliku → []."""
    if not sciezka.exists():
        return []
    out = []
    for ln in sciezka.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def _linia(rekord: dict) -> str:
    """Deterministyczna serializacja (klucze wg schematu) — porównywalna bit-w-bit."""
    return json.dumps(rekord, ensure_ascii=False, sort_keys=True)


def _dopisz(rekord: dict, sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord, jeśli identyczny jeszcze nie istnieje. Zwraca True gdy dopisano.

    Idempotencja po CAŁYM rekordzie (z datą): ten sam bieg tego samego dnia nie
    mnoży linii; zmieniony wynik lub inny dzień = nowa linia.
    """
    istniejace = {_linia(r) for r in _wczytaj(sciezka)}
    if _linia(rekord) in istniejace:
        return False
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


def zapisz_ab(*, sygnal: str, neuron: str, interwal: str, okno_barow: int,
              roi_b: float, roi_a: float, maxdd_delta: float, werdykt: str,
              zrodlo: str, uwaga: str = "", data: str | None = None,
              sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord A/B (Δ PnL). delta_pp liczone tu (roi_a - roi_b).

    werdykt: krótki token ("POMAGA"/"SZKODZI"/"NEUTRALNE"/…), NIE długi baner z emoji.
    """
    rekord = {
        "typ": "AB", "sygnal": sygnal, "neuron": neuron, "interwal": interwal,
        "okno_barow": int(okno_barow), "roi_b": round(float(roi_b), 2),
        "roi_a": round(float(roi_a), 2), "delta_pp": round(float(roi_a) - float(roi_b), 2),
        "maxdd_delta": round(float(maxdd_delta), 2), "werdykt": werdykt,
        "data": data or _dzis(), "zrodlo": zrodlo, "uwaga": uwaga,
    }
    return _dopisz(rekord, sciezka)


def zapisz_ic(*, sygnal: str, neuron: str, horyzont: str, ic: float, tryb: str,
              prog: float, werdykt: str, kierunek: str, zrodlo: str, uwaga: str = "",
              data: str | None = None, sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord IC (skill sygnału na horyzoncie)."""
    rekord = {
        "typ": "IC", "sygnal": sygnal, "neuron": neuron, "horyzont": str(horyzont),
        "ic": round(float(ic), 4), "tryb": tryb, "prog": round(float(prog), 4),
        "werdykt": werdykt, "kierunek": kierunek, "data": data or _dzis(),
        "zrodlo": zrodlo, "uwaga": uwaga,
    }
    return _dopisz(rekord, sciezka)
