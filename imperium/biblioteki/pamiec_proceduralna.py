"""
🛠️ Pamięć Proceduralna — W11 Centrum Pamięci W-360 v11 (taksonomia CoALA — UNIKAT)

ROZKAZ CEZARA (2026-06-29): „jeszcze kilka warstw pamięci, poszukaj, wg zasad."

DEEP RESEARCH (ZPO): CoALA — Cognitive Architectures for Language Agents
(https://arxiv.org/abs/2309.02427) definiuje KANONICZNĄ czwórkę pamięci agenta:
  • robocza (working) — aktywny cel/kontekst bieżącego cyklu      → W12 (pamiec_robocza)
  • epizodyczna (episodic) — przeszłe zdarzenia/przebieg sesji     → mamy: kronika W3b
  • semantyczna (semantic) — uogólnione fakty/wiedza               → mamy: lekcje W3 + RAG W2
  • PROCEDURALNA (procedural) — JAK wykonać zadanie (runbooki)     → TA WARSTWA (W11) — brakowało!

Procedura = nazwany przepis: kiedy użyć (wyzwalacz) + KROKI do wykonania + źródło.
To „skrystalizowane know-how" Imperium: jak dodać neuron, jak naprawić audyt W11,
jak bezpiecznie commitować. Raz wypracowane — nigdy nie wyprowadzane od zera (Prawo XV:
koniec utraty potencjału). Gdy sesja dotyka tematu, właściwa procedura jest pod ręką.

RÓŻNICA OD LEKCJI (W3, semantyczna): lekcja mówi CO wiemy („bug Force Index przy fi2==0").
Procedura mówi JAK działać („kroki dodania neuronu: 1. klasa 2. rejestr 3. WAGI 4. MANIFEST 5. test").
To dwa różne typy pamięci wg CoALA — nie redundancja (Prawo XVI), lecz domknięcie taksonomii.

Deterministyczna (bez API), JSONL → git (chmura↔lokal). Pod zarządem Kustosza (W7).

CLI:
  python -m imperium.biblioteki.pamiec_proceduralna lista
  python -m imperium.biblioteki.pamiec_proceduralna szukaj "dodać neuron"
  python -m imperium.biblioteki.pamiec_proceduralna dodaj "nazwa" --wyzwalacz "a,b" --kroki "k1" "k2"
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
PLIK_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "procedury.jsonl"


def _dzis() -> str:
    return date.today().isoformat()


def _wczytaj(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    if plik is None:
        plik = PLIK_DOMYSLNY
    if not plik.exists():
        return []
    out = []
    for ln in plik.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except (json.JSONDecodeError, ValueError):
            continue
    return out


def dodaj(nazwa: str, kroki: List[str], wyzwalacz: str = "",
          zrodlo: str = "", data: Optional[str] = None,
          plik: Optional[Path] = None, dedup: bool = True) -> bool:
    """
    Dodaje procedurę (runbook). Zwraca True gdy dopisano, False gdy duplikat nazwy.
    wyzwalacz: słowa kluczowe (po przecinku) — kiedy ta procedura jest istotna.
    kroki: lista kroków do wykonania (kolejność ma znaczenie).
    """
    if plik is None:
        plik = PLIK_DOMYSLNY
    nazwa = nazwa.strip()
    if dedup:
        for p in _wczytaj(plik):
            if p.get("nazwa", "").strip().lower() == nazwa.lower():
                return False
    wpis = {
        "nazwa": nazwa,
        "wyzwalacz": [w.strip().lower() for w in re.split(r"[,;]", wyzwalacz) if w.strip()],
        "kroki": [k.strip() for k in kroki if k.strip()],
        "zrodlo": zrodlo.strip(),
        "data": data or _dzis(),
    }
    plik.parent.mkdir(parents=True, exist_ok=True)
    with plik.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False) + "\n")
    return True


def wszystkie(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    return _wczytaj(plik)


def szukaj(zapytanie: str, limit: int = 5, plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Znajduje procedury istotne dla zapytania (po SŁOWACH: nazwa + wyzwalacze + kroki).
    Ranking = liczba trafionych słów. Zwraca procedury gotowe do wykonania.
    """
    slowa = [s for s in re.findall(r"\w{3,}", zapytanie.lower())]
    if not slowa:
        return []
    wyniki = []
    for p in _wczytaj(plik):
        tekst = (p.get("nazwa", "") + " " + " ".join(p.get("wyzwalacz", []))
                 + " " + " ".join(p.get("kroki", []))).lower()
        n = sum(1 for s in slowa if s in tekst)
        if n:
            wyniki.append((n, p))
    wyniki.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in wyniki[:limit]]


def pobierz(nazwa: str, plik: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Procedura po dokładnej nazwie (case-insensitive)."""
    for p in _wczytaj(plik):
        if p.get("nazwa", "").strip().lower() == nazwa.strip().lower():
            return p
    return None


# ─── ZIARNO: realne procedury Imperium (skrystalizowane know-how) ──────────────

_ZIARNO = [
    {
        "nazwa": "Dodać nowy neuron",
        "wyzwalacz": "neuron, dodać neuron, nowy neuron, mikroneuron",
        "kroki": [
            "Utwórz klasę dziedziczącą MikroNeuron z KLUCZ/WSKAZNIK/KATEGORIA/WAGA/DOSTEPNY",
            "Zarejestruj w imperium/legiony/rejestr.py (import + lista wszystkie_neurony)",
            "Dodaj literę KATEGORIA do WAGI_REZIMU jeśli nowa (legatus.py) — zero martwych liter",
            "Upewnij się, że Budowniczy produkuje WSKAZNIK (wskazniki['KLUCZ'])",
            "Dopisz klucz do docs/MANIFEST_KODU.md i docs/MAPA_KLUCZY.md (Prawo XXI)",
            "Napisz testy granic (0/None/±/próg — Reguła Test-Granic)",
            "python tests/run_tests.py (zielone) + python narzedzia/audyt_spojnosci.py (exit 0)",
        ],
        "zrodlo": "Prawo XXI + ZASADA SYMBIOZY",
    },
    {
        "nazwa": "Naprawić audyt W11 (moduł nie w INDEKS)",
        "wyzwalacz": "audyt, w11, indeks, moduł nie wymieniony, biblioteki",
        "kroki": [
            "Otwórz docs/INDEKS_IMPERIUM.md, znajdź wiersz imperium/biblioteki/",
            "Dopisz nazwę nowego modułu .py do listy w tym wierszu z krótkim opisem (ZPO)",
            "python narzedzia/audyt_spojnosci.py — sprawdź czy W11 znika",
        ],
        "zrodlo": "Audyt Warstwa 11",
    },
    {
        "nazwa": "Bezpieczny commit (bramka Prawo XXI)",
        "wyzwalacz": "commit, push, bramka, przed commitem",
        "kroki": [
            "python tests/run_tests.py — musi być X/X zielone",
            "python narzedzia/audyt_spojnosci.py — musi być exit 0 (w tym ruff W13)",
            "Dopisz wpis do Dziennika Nieśmiertelnego (ROZKAZ STAŁY)",
            "Zaktualizuj 'Stan na:' w MANIFEST/README na datę commitu",
            "git add -A && git commit (pre-commit hook zweryfikuje); git push -u origin <branch>",
        ],
        "zrodlo": "TRYB AUTONOMICZNY + Prawo XXI",
    },
    {
        "nazwa": "Dodać warstwę pamięci (W-360)",
        "wyzwalacz": "warstwa pamięci, nowy moduł pamięci, w-360, centrum pamięci",
        "kroki": [
            "Utwórz imperium/biblioteki/<nazwa>.py z docstringiem ZPO (źródła+arxiv)",
            "Wepnij raport_startowy() do centrum_pamieci.podsumowanie_startowe (try/except)",
            "Dopisz do docs/INDEKS_IMPERIUM.md (wiersz biblioteki) — inaczej audyt W11",
            "Napisz tests/test_<nazwa>.py (granice + anti-utrwalanie jeśli dotyczy)",
            "Wpis LOG_ZMIAN + Dziennik; testy zielone + audyt exit 0; commit+push",
        ],
        "zrodlo": "Sesje W-360 v4-v10",
    },
]


def zasiej(plik: Optional[Path] = None) -> int:
    """Wpisuje ziarno procedur (jeśli brak). Zwraca ile dodano. Idempotentne (dedup)."""
    dodano = 0
    for z in _ZIARNO:
        if dodaj(z["nazwa"], z["kroki"], ",".join(z["wyzwalacz"].split(",")),
                 z.get("zrodlo", ""), plik=plik):
            dodano += 1
    return dodano


def raport_startowy(plik: Optional[Path] = None) -> str:
    n = len(_wczytaj(plik))
    if n == 0:
        return ""
    return f"   🛠️ Pamięć proceduralna (W11): {n} procedur (runbooków) gotowych"


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Pamięć Proceduralna — W11 CoALA (W-360 v11)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("lista", help="Wszystkie procedury")
    sub.add_parser("zasiej", help="Wpisz ziarno procedur Imperium")
    psz = sub.add_parser("szukaj", help="Znajdź procedurę")
    psz.add_argument("zapytanie")
    pd = sub.add_parser("dodaj", help="Dodaj procedurę")
    pd.add_argument("nazwa")
    pd.add_argument("--wyzwalacz", default="")
    pd.add_argument("--kroki", nargs="+", required=True)
    args = p.parse_args()

    if args.cmd == "zasiej":
        print(f"✅ Dodano {zasiej()} procedur (ziarno).")
    elif args.cmd == "szukaj":
        for pr in szukaj(args.zapytanie):
            print(f"🛠️ {pr['nazwa']} (źródło: {pr.get('zrodlo','—')})")
            for i, k in enumerate(pr["kroki"], 1):
                print(f"   {i}. {k}")
    elif args.cmd == "dodaj":
        ok = dodaj(args.nazwa, args.kroki, args.wyzwalacz)
        print("✅ Dodano" if ok else "— Duplikat nazwy")
    else:
        for pr in wszystkie():
            print(f"🛠️ {pr['nazwa']} — wyzwalacze: {', '.join(pr.get('wyzwalacz', []))} "
                  f"({len(pr.get('kroki', []))} kroków)")
