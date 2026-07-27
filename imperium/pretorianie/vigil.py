"""🔦 VIGIL — Straż Nocna: skan KAŻDEGO zapisanego pliku .py natychmiast (PostToolUse).

Rzymscy *vigiles* nie zapobiegali pożarom — patrolowali i reagowali, gdy już buchnął, póki
ogień był mały. Ten organ robi to samo z kodem: nie ocenia zamiaru (od tego jest CUSTOS
LIMINIS u progu), tylko ogląda SKUTEK zapisu, zanim zdąży urosnąć.

POWÓD ISTNIENIA (zmierzone 2026-07-27):
Księga Wad Kodu ma 126 klas semantycznych i **16 wzorców regex** — czyli automatycznie
egzekwowanych jest ~13%. Reszta to wiedza czekająca, aż ktoś sam sobie o niej przypomni
podczas recenzji. Do tego skan uruchamiał się dopiero na bramce, czyli po całej serii zmian:
wada nazwana rano wracała po południu, bo nikt jej nie sprawdzał w chwili powstania. Dowód
z tego samego dnia: klasa „commitowanie ścieżek domowych" została nazwana 07-26, a 07-27
wróciła w 277 egzemplarzach.

CO ROBI: po każdym zapisie/edycji pliku `.py` uruchamia dwa istniejące organy — `ruff`
(bugi i martwy kod) oraz `skan_wad_kodu` (znane wzorce z Księgi Wad) — i wstrzykuje wynik
jako kontekst dla Architekta. **Nic nie blokuje**: PostToolUse działa PO fakcie, a udawanie
bariery po czasie byłoby teatrem.

ZASADA WYDRUKU (ta sama, co w hooku startowym): CISZA GDY ZIELONE, KRZYK GDY CZERWONE.
Strażnik meldujący „czysto" po każdym zapisie zamieniłby się w tapetę i przestałby być
czytany — a wtedy jego pierwszy prawdziwy alarm też zostałby pominięty.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ nie uruchamia testów — sekunda na zapis to jedno, minuty to co innego (bramka od tego jest),
  • ❌ nie skanuje plików spoza repo ani nie-`.py` (Księga Wad zna wzorce Pythona),
  • ❌ nie „naprawia" niczego automatycznie — poprawka bez zrozumienia to nowa wada.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
LIMIT_LINII = 12          # dłuższy meldunek i tak nie zostanie przeczytany
_TIMEOUT = 30


def _uruchom(args: List[str]) -> Optional[str]:
    """stdout+stderr narzędzia albo None, gdy nie dało się uruchomić (brak = nie alarm)."""
    try:
        p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=_TIMEOUT)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return (p.stdout or "") + (p.stderr or "")


def _plik_do_skanu(tool_input: Dict[str, Any]) -> Optional[Path]:
    """Ścieżka do skanu albo None. Pomijanie NIE-`.py` jest ciche; nieosiągalny `.py` — nie.

    ROZRÓŻNIENIE JEST ISTOTĄ (zmierzone 2026-07-27 przy weryfikacji end-to-end). Pominięcie
    pliku `.md` czy `.json` to normalna praca i ma być bezgłośne. Ale plik `.py`, którego
    strażnik NIE UMIAŁ znaleźć, to co innego: wtedy nie wiadomo, czy kod jest czysty, czy
    tylko niezbadany — a cicha zgoda w takiej sytuacji jest dokładnie tą klasą wady, którą
    ten organ ma ścigać. Złapane na ścieżce POSIX z Git Basha (`/c/Projekty/...`), którą
    Python na Windowsie rozwiązuje jako `C:\\c\\Projekty\\...` i nie znajduje. Narzędzia
    `Write`/`Edit` podają tu ścieżki windowsowe, więc na produkcji to nie zachodzi — ale
    strażnik ma mówić, gdy czegoś nie sprawdził, a nie zakładać, że nie było czego.
    """
    surowa = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not surowa:
        return None
    sciezka = Path(str(surowa))
    if sciezka.suffix.lower() != ".py":
        return None            # nie nasz rodzaj pliku — cisza uzasadniona
    if not sciezka.exists():
        print(f"[vigil] NIE ZBADANO {surowa} — pliku nie ma pod tą ścieżką "
              "(to nie znaczy, że kod jest czysty)", file=sys.stderr)
        return None
    try:                       # tylko pliki repo — cudzych nie recenzujemy
        sciezka.resolve().relative_to(ROOT)
    except ValueError:
        print(f"[vigil] NIE ZBADANO {surowa} — plik leży poza repo Imperium", file=sys.stderr)
        return None
    return sciezka


def zbadaj(sciezka: Path) -> List[str]:
    """Lista zarzutów do pliku. Pusta = cisza (plik czysty albo narzędzia niedostępne)."""
    zarzuty: List[str] = []
    wyj = _uruchom(["-m", "ruff", "check", str(sciezka)])
    if wyj and "All checks passed" not in wyj:
        zarzuty += [f"[ruff] {w.strip()}" for w in wyj.splitlines()
                    if w.strip() and not w.strip().startswith("Found")][:LIMIT_LINII]
    wyj = _uruchom(["narzedzia/skan_wad_kodu.py", str(sciezka)])
    if wyj and "czysto" not in wyj:
        zarzuty += [f"[Księga Wad] {w.strip()}" for w in wyj.splitlines()
                    if w.strip() and not w.strip().startswith("📋")][:LIMIT_LINII]
    return zarzuty


def main() -> int:
    try:
        zdarzenie = json.load(sys.stdin)
    except Exception as e:  # noqa: BLE001
        print(f"[vigil] nie odczytałem zdarzenia hooka: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    sciezka = _plik_do_skanu(zdarzenie.get("tool_input") or {})
    if sciezka is None:
        return 0
    try:
        zarzuty = zbadaj(sciezka)
    except Exception as e:  # noqa: BLE001
        print(f"[vigil] błąd skanu {sciezka}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if not zarzuty:
        return 0            # CISZA GDY ZIELONE
    tresc = (f"🔦 VIGIL — świeży zapis `{sciezka.name}` ma zarzuty (napraw TERAZ, "
             f"nie na bramce):\n" + "\n".join(f"   • {z}" for z in zarzuty))
    # ASCII w transporcie — patrz ten sam komentarz w `custos_liminis`: strona kodowa cp1250
    # na Windowsie nie zna emoji ani polskich znaków, a meldunek strażnika nie ma prawa zginąć
    # przez kodowanie. Odbiorca dekoduje \uXXXX z powrotem.
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": tresc}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
