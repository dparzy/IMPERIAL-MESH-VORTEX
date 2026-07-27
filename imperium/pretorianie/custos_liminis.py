"""🚧 CUSTOS LIMINIS — Strażnik Progu: bariera PRZED zadziałaniem narzędzia (PreToolUse).

Rzymski *custos liminis* pilnował progu domu — nie sprzątał po wejściu, tylko decydował, kto
wchodzi. Ten organ robi to samo z wywołaniem narzędzia: dostaje zamiar, zanim cokolwiek się
wydarzy, i odpowiada `deny` / `ask` / milczeniem.

POWÓD ISTNIENIA (zmierzone 2026-07-27):
Imperium używało 2 z **31** zdarzeń hooka (6.5%), a jedyny rozkaz oznaczony jako NIENARUSZALNY
(„Claude NIGDY nie pushuje", 2026-07-11) przez 16 dni nie miał ŻADNEGO mechanizmu — dopiero 07-27
doszedł `permissions.deny: Bash(git push:*)`.

LICZBA 31 JEST ZMIERZONA, NIE ZAPAMIĘTANA (2026-07-27, na pytanie Cezara). Wcześniej w Dzienniku,
w pamięci i w moich własnych meldunkach żyło „~9" — powtarzane bez sprawdzenia. Źródło rozstrzygające:
schemat konfiguracji `json.schemastore.org/claude-code-settings.json` (maszynowy, wylicza klucze
`hooks`). Dokumentacja narracyjna dała 30 i sama sobie przeczyła w nagłówku („32"), więc liczby
stamtąd nie bierzemy — bierzemy listę. Skala pomyłki: pokrycie to 12.9% (4/31), nie 44% (4/9).

I ta łata wciąż zapina JEDNĄ POWŁOWĘ Z DWÓCH. Dokumentacja uprawnień mówi wprost, że reguły
PowerShella to osobna przestrzeń nazw („PowerShell permission rules use the same shape as Bash
rules"), a w tym środowisku PowerShell jest powłoką PODSTAWOWĄ. Reguła `Bash(...)` nie ma prawa
zatrzymać wywołania narzędzia `PowerShell`. Naprawiamy to dwutorowo: regułą `PowerShell(git
push:*)` w konfiguracji ORAZ tym strażnikiem — bo reguła wzorcowa dopasowuje PREFIKS polecenia,
a `git -C /repo push` prefiksem `git push` nie jest.

CZEGO SIĘ NAUCZYŁEM BUDUJĄC TO (Prawo I — premisa też wymaga pomiaru):
Zacząłem od tezy „deny nie łapie `cd x && git push`, bo dopasowuje prefiks". Dokumentacja tę
tezę OBALIŁA: Claude Code zna operatory powłoki i rozbija polecenia złożone na podpolecenia
(`&&`, `||`, `;`, `|`, `|&`, `&`, nowa linia), a reguła musi pasować do każdego z osobna.
Gdybym nie sprawdził, zbudowałbym barierę uzasadnioną fałszywą przesłanką — dokładnie to, co
zrobił FRUMENTARIUS, cytując zmyśloną liczbę. Prawdziwe szczeliny są dwie: inna POWŁOKA
i inna SKŁADNIA tego samego polecenia.

ZASADA DZIAŁANIA — asymetria kosztów:
  • `git push` w dowolnej formie → **deny**. Rozkaz jest nienaruszalny, a koszt fałszywego
    zatrzymania to jedno zdanie Cezara; koszt przepuszczenia to złamany rozkaz.
  • zapis do `archiwum/` → **ask**, nie deny. Konstytucja mówi „archiwum otwierasz TYLKO na
    rozkaz Cezara" — więc decyzja należy do niego, a nie do skryptu. `ask` pyta jego, zamiast
    zgadywać za niego w którąkolwiek stronę.
  • cokolwiek innego → CISZA (brak wyjścia = zwykły tryb uprawnień). Strażnik, który zabiera
    głos przy każdym poleceniu, przestaje być słyszany.

AWARIA STRAŻNIKA NIE BLOKUJE PRACY, ALE NIE MILCZY: przy własnym błędzie wypisuje powód
i kończy się kodem 1 (błąd nieblokujący, widoczny w transkrypcie). Twardą barierą pozostaje
`permissions.deny` w konfiguracji — ten organ jest szelkami do tamtego pasa, więc jego awaria
nie może zatrzymać całej wachty, ale też nie ma prawa wyglądać na zielone światło.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, Optional

# Separatory podpoleceń — ta sama lista, którą dokumentacja uprawnień wymienia jako
# rozpoznawane przez Claude Code. Trzymamy się jej świadomie: strażnik ma widzieć polecenie
# tak samo jak silnik uprawnień, inaczej jedno z dwóch miałoby ślepą plamę.
_SEPARATORY = re.compile(r"&&|\|\||;|\|&|\||&|\n")

# Flagi `git`, które POŁYKAJĄ następny token — bez tego `git -C /repo push` wyglądałby jak
# polecenie `-C`, a `push` schowałoby się w argumentach.
_FLAGI_Z_WARTOSCIA = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"})

NARZEDZIA_POWLOKI = ("Bash", "PowerShell")
NARZEDZIA_ZAPISU = ("Write", "Edit", "NotebookEdit", "MultiEdit")


def _podpolecenia(cmd: str):
    return [c.strip() for c in _SEPARATORY.split(cmd or "") if c.strip()]


def _tokeny(fragment: str):
    """Podział na tokeny SZANUJĄCY CUDZYSŁOWY (zmierzone przy pisaniu testów 2026-07-27).

    Gołe `split()` rozbijało `"C:\\Program Files\\Git\\bin\\git.exe" push` na `"C:\\Program`
    i resztę, więc pierwszy token nie wyglądał na gita i push przechodził. Ścieżka ze spacją
    w cudzysłowie to na Windowsie forma codzienna, nie egzotyczna.

    `posix=False` jest tu istotne: w trybie POSIX-owym `shlex` traktuje backslash jako znak
    ucieczki i zjadłby separatory ścieżek Windows. Gdy i to zawiedzie (niedomknięty cudzysłów),
    wracamy do `split()` — strażnik ma wtedy widzieć MNIEJ, ale nigdy nie wywalić się z wyjątkiem.
    """
    import shlex
    try:
        surowe = shlex.split(fragment, posix=False)
    except ValueError:
        surowe = fragment.split()
    return [t.strip("'\"") for t in surowe]


def _bez_przypisan(tokeny):
    """Usuwa wiodące przypisania zmiennych (`FOO=bar git push`) — silnik uprawnień też je mija."""
    i = 0
    while i < len(tokeny) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokeny[i]):
        i += 1
    return tokeny[i:]


def _polecenie_gita(tokeny) -> Optional[str]:
    """Podpolecenie gita (`push`, `status`, …) albo None, gdy to nie jest wywołanie gita.

    Czytamy PIERWSZY token niebędący opcją — dzięki temu `git log --grep push` NIE uchodzi
    za push (fałszywe zatrzymanie jest tanie, ale nie darmowe: uczy ignorowania strażnika).
    """
    tokeny = _bez_przypisan(tokeny)
    if not tokeny:
        return None
    exe = tokeny[0].strip("'\"").replace("\\", "/").rsplit("/", 1)[-1].lower()
    if exe.endswith(".exe"):
        exe = exe[:-4]
    if exe != "git":
        return None
    i = 1
    while i < len(tokeny):
        t = tokeny[i]
        if t in _FLAGI_Z_WARTOSCIA:
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        return t.lower()
    return None


def _sciezka_w_archiwum(sciezka: str) -> bool:
    czesci = [c.lower() for c in re.split(r"[\\/]+", sciezka or "") if c]
    return "archiwum" in czesci


def ocen(tool_name: str, tool_input: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Werdykt strażnika albo None (= milczenie, zwykły tryb uprawnień).

    Czysta funkcja: cały protokół hooka jest na zewnątrz, więc każdy przypadek da się
    przetestować bez uruchamiania powłoki.
    """
    if tool_name in NARZEDZIA_POWLOKI:
        cmd = tool_input.get("command") or ""
        for pod in _podpolecenia(cmd):
            if _polecenie_gita(_tokeny(pod)) == "push":
                return {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "🚧 CUSTOS LIMINIS: `git push` jest zastrzeżony dla Cezara (rozkaz stały "
                        "z 2026-07-11, NIENARUSZALNY). Architekt melduje gotowość i podaje blok "
                        "PowerShell do wykonania ręcznie — nigdy nie pushuje sam."),
                }
    if tool_name in NARZEDZIA_ZAPISU:
        sciezka = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if _sciezka_w_archiwum(str(sciezka)):
            return {
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    f"📦 CUSTOS LIMINIS: zapis do `archiwum/` ({sciezka}). Konstytucja: archiwum "
                    "otwiera się TYLKO na rozkaz Cezara, a przed przeniesieniem pliku czyta się go "
                    "w CAŁOŚCI. Decyzja należy do Cezara — dlatego pytanie, nie blokada."),
            }
    return None


def main() -> int:
    try:
        zdarzenie = json.load(sys.stdin)
    except Exception as e:  # noqa: BLE001 — awaria strażnika nie blokuje pracy, ale krzyczy
        print(f"[custos_liminis] nie odczytałem zdarzenia hooka: {type(e).__name__}: {e}",
              file=sys.stderr)
        return 1
    try:
        werdykt = ocen(zdarzenie.get("tool_name") or "", zdarzenie.get("tool_input") or {})
    except Exception as e:  # noqa: BLE001
        print(f"[custos_liminis] błąd oceny: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if werdykt is None:
        return 0            # cisza = zwykły tryb uprawnień (nie „allow"!)
    # `ensure_ascii=True` (domyślne) JEST TU DECYZJĄ, NIE PRZEOCZENIEM (zmierzone 2026-07-27):
    # na Windowsie strumień wyjściowy potrafi mieć stronę kodową cp1250, w której emoji ani
    # polskie „ą" z komunikatu nie istnieją — protokół hooka padłby wtedy na UnicodeEncodeError
    # albo wypluł mojibake, czyli bariera zniknęłaby przez KOSMETYKĘ. JSON z sekwencjami \uXXXX
    # jest czystym ASCII w transporcie, a odbiorca dekoduje go z powrotem do pełnych znaków.
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **werdykt}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
