"""🤫 SILENTIUM — cisza nad repozytorium na czas biegu bramki.

Rzymskie *silentium* to nie brak dźwięku, tylko **nakazana cisza podczas czynności
świętej**: auspicja unieważniało byle drgnienie, więc ciszy się nie proszono — ją
ogłaszano, a złamanie unieważniało obrzęd. Ten organ robi dokładnie to z bramką:
na czas biegu testów i audytu **odmawia zapisu do repozytorium**.

════════════════════════════════════════════════════════════════════════════════
POWÓD ISTNIENIA (zmierzony, nie wyobrażony)
════════════════════════════════════════════════════════════════════════════════
`tests/run_tests.py` ma od 2026-07-26 STRAŻNIKA CZYSTOŚCI, który po biegu porównuje
`git status` przed i po. Wykrywa zabrudzenie **po fakcie** i sam przyznaje, że nie umie
rozstrzygnąć przyczyny — jego własny komunikat wymienia dwie możliwości i kończy się
zdaniem „to fałszywe oskarżenie, powtórz bieg sam". VINDEX (2026-08-02) dokłada
wykrywanie naruszeń kontraktu plików — również **po fakcie**.

Czyli: mieliśmy DWA organy patrzące wstecz i **zero** zapobiegających. Zmierzony skutek —
4 unieważnione biegi bramki w 4 dni, z czego **dwa w jednej wachcie (2026-08-03) przez
tego samego Architekta, który zasadę „nie edytuj w trakcie biegu" zapisał 2026-07-31**.
To jest dowód rozstrzygający, mocniejszy od każdego argumentu: sama wiedza o regule nie
wystarcza, bo koszt złamania płaci się dopiero 20 minut później, a wtedy pamięć o edycji
już wyparowała. Reguła bez mechanizmu jest tą samą klasą co runbook W11 i kontrakt
append-only deklarowany w 6 organach przy zerowej egzekucji.

════════════════════════════════════════════════════════════════════════════════
DLACZEGO BLOKADĘ ZAKŁADA PROCES BRAMKI, A NIE HOOK ROZPOZNAJĄCY KOMENDĘ
════════════════════════════════════════════════════════════════════════════════
Kuszące było, by `PreToolUse` rozpoznał „to jest komenda bramki" i sam założył blokadę.
Ta droga jest ZŁA i wiem to z pomiaru, nie z przeczucia: bieg w tle **wraca z narzędzia
natychmiast**, a proces żyje dalej. Hook zdejmujący blokadę na powrocie narzędzia
zdjąłby ją w pierwszej sekundzie 20-minutowego biegu — czyli chroniłby dokładnie wtedy,
gdy nie trzeba, i milczał przez cały czas realnego ryzyka. To ta sama klasa co E7
(„kotwica osierocona traktowana jak sukces": strażnik milknie dokładnie wtedy, gdy jego
kontrakt przestaje obowiązywać).

Dlatego blokadę zakłada i zdejmuje **sam proces bramki** (`cisza()` jako menedżer
kontekstu). Blokada żyje wtedy dokładnie tyle, co bieg — w pierwszym planie i w tle
identycznie — a `atexit` + żywotność PID-u domykają przypadek awarii.

════════════════════════════════════════════════════════════════════════════════
TRZY BEZPIECZNIKI PRZED ZAMUROWANIEM REPOZYTORIUM
════════════════════════════════════════════════════════════════════════════════
Strażnik, który potrafi trwale odciąć Architekta od pracy, jest gorszy od braku
strażnika. Blokada wygasa więc na TRZY niezależne sposoby:
  1. **Żywotność PID-u** — proces bramki zniknął (crash, Ctrl-C, zabity terminal)
     → blokada jest martwa i sprzątana przy pierwszym odczycie.
  2. **TTL** — twardy sufit czasu (domyślnie 45 min). Nawet gdyby PID został
     przetworzony przez system, cisza kończy się sama.
  3. **Furtka jawna** — `zdejmij --sila` oraz zmienna `SILENTIUM_OFF=1`.

`os.kill(pid, 0)` JEST TU ZAKAZANY I TO NIE JEST STYLISTYKA (Windows, gdzie stoi to
Imperium): `os.kill` na Windowsie dla sygnału innego niż CTRL_C_EVENT/CTRL_BREAK_EVENT
woła `TerminateProcess` — czyli sprawdzenie „czy żyjesz" **ZABIŁOBY** proces bramki.
Żywotność badamy `OpenProcess` + `GetExitCodeProcess` (STILL_ACTIVE = 259), a na POSIX
sygnałem 0. Klasa: „przyrząd pomiarowy zmienia to, co mierzy".

════════════════════════════════════════════════════════════════════════════════
CO BLOKUJEMY, A CO ŚWIADOMIE PRZEPUSZCZAMY
════════════════════════════════════════════════════════════════════════════════
  • `Write/Edit/NotebookEdit` w ścieżkę **wewnątrz repo** → DENY. Tu nie ma zgadywania:
    ścieżkę znamy dokładnie, więc precyzja jest z konstrukcji, nie z kalibracji.
  • `Bash/PowerShell` **piszące do repo** (git add/commit, przekierowanie `>`, kasowanie,
    znane organy-ledgery) → DENY. To jedyny fragment heurystyczny, więc ma pomiar
    na 5568 realnych komendach z transkryptów (patrz `narzedzia/kalibracja_silentium.py`).
  • **Odczyt jest zawsze wolny** — `git status`, `cat`, `grep`, `python -c` liczące.
    Strażnik blokujący czytanie zmusiłby do czekania bezczynnie, a bezczynne czekanie
    uczy obchodzenia strażnika. Cisza dotyczy PISANIA, nie patrzenia.
  • Ścieżki **poza repo** (scratchpad, `%TEMP%`), katalogi ignorowane (`raporty/`,
    `logs/`, `__pycache__`) i sam plik blokady → wolne.

Sam proces bramki NIE jest przez to ograniczony: hook widzi wyłącznie wywołania narzędzi
Architekta. Testy i audyt piszą swoje artefakty (pieczęć, raporty) normalnie.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

KORZEN = Path(__file__).resolve().parent.parent.parent
PLIK_BLOKADY = KORZEN / "bibliotheca_ulpia" / "dane" / "silentium.lock"

TTL_DOMYSLNY_S = 45 * 60          # sufit dla najdłuższego znanego biegu (bramka ~20 min)
_STILL_ACTIVE = 259               # kod „proces wciąż żyje" z GetExitCodeProcess (WinAPI)

# Katalogi, w których zapis NIE brudzi repozytorium (są w .gitignore albo poza gitem).
# Świadomie krótka lista: każdy dopisek tutaj to dziura w ciszy, więc rośnie tylko z pomiaru.
_WOLNE_KATALOGI = ("raporty", "logs", "__pycache__", ".pytest_cache", ".ruff_cache", "dane/_kopie")

NARZEDZIA_ZAPISU = ("Write", "Edit", "NotebookEdit", "MultiEdit")
NARZEDZIA_POWLOKI = ("Bash", "PowerShell")

# ── Klasyfikator komend piszących ────────────────────────────────────────────────
# WSZYSTKIE poniższe listy i reguły są WYNIKIEM POMIARU na 120 zaetykietowanych realnych
# komendach (`narzedzia/kalibracja_silentium.py`), a nie intuicji autora. Pierwsza wersja,
# pisana „na wyczucie", dała precyzję 63.3% i przepuszczała 11/60 zapisów — była więc
# gorsza od braku strażnika, bo dawałaby fałszywy spokój. Każda zmiana niżej wskazuje
# konkretną pomyłkę, którą naprawia.

# Podpolecenia gita zmieniające drzewo robocze albo indeks.
# `fetch`, `gc`, `prune` ŚWIADOMIE POZA LISTĄ (pomiar: 3 fałszywe alarmy z 22): aktualizują
# referencje zdalne i obiekty, ale `git status` po nich pokazuje to samo. Bramki nie psują.
_GIT_PISZE = frozenset({
    "add", "commit", "rm", "mv", "checkout", "restore", "reset", "stash", "merge",
    "rebase", "apply", "cherry-pick", "revert", "clean", "switch", "update-index",
    "am", "pull", "worktree", "submodule", "sparse-checkout",
})
# Programy POSIX-owe, których samo wywołanie oznacza zapis.
_EXE_PISZE = frozenset({
    "rm", "mv", "cp", "touch", "mkdir", "rmdir", "tee", "dd", "install", "ln",
    "truncate", "chmod", "chown", "patch", "unzip", "tar",
})
# Cmdlety PowerShella zmieniające pliki (dopasowanie bez względu na wielkość liter).
_PS_PISZE = frozenset({
    "set-content", "out-file", "add-content", "clear-content", "new-item", "remove-item",
    "move-item", "copy-item", "rename-item", "set-itemproperty", "export-csv",
    "export-clixml", "start-transcript",
})
# Organy Imperium dopisujące do WERSJONOWANYCH ledgerów.
_ORGANY = (
    "dziennik_niesmiertelny", "codex_notarum", "scriba_codex", "index_falsorum",
    "pamiec_absolutna", "centrum_pamieci", "kustosz_pamieci", "wizje_i_decyzje",
    "codex_probationum", "tabularium", "maturitas", "ksiega_wad_kodu", "vindex",
    "rejestr_wizji", "rejestr_strategii", "pamiec_proceduralna",
)
# ODWRÓCONA LOGIKA WOBEC PIERWSZEJ WERSJI (pomiar: 5 fałszywych alarmów z 22).
# Pierwotnie flagowałem KAŻDE wywołanie organu i próbowałem odsiewać tryby odczytu listą
# słów-kluczy. To pękło na dwa sposoby naraz: `tabularium katalog` (tryb odczytu spoza mojej
# listy) był oskarżany, a `dziennik wpis --co "…długa proza zawierająca słowo »stan«…"`
# był PRZEPUSZCZANY, bo słowo z listy odczytu trafiało się w treści wpisu. Dokładnie ta sama
# klasa, którą CUSTOS LIMINIS złapał 2026-07-28: PROZA CZYTANA JAK SKŁADNIA.
# Teraz flagujemy wyłącznie na JAWNY CZASOWNIK ZAPISU — czego nie znam, tego nie oskarżam.
_WERBY_PISZACE = re.compile(
    r"(?:^|[\s;])(?:wpis|nota|corona|talar|dodaj|zapisz|zamknij|wycofaj|napraw)\w*\b"
    r"|--(?:zapisz|ledger|napraw|odswiez|zatwierdz|wpisz)\b")
# Skrypty, których uruchomienie samo w sobie brudzi repo (pomiar: 3 przecieki z 11).
# `run_tests.py` odciska SIGILLUM PROBATIONIS do `bibliotheca_ulpia/dane/` — czyli bramka
# jest jednocześnie pisarzem. Drugi bieg bramki w trakcie pierwszego ma być zatrzymany.
_SKRYPTY_PISZACE = ("tests/run_tests.py", "tests\\run_tests.py")
_SED_INPLACE = re.compile(r"^-[a-zA-Z]*i")     # `sed -i`, `sed -ri`, ale nie `sed -n`

# Kod Pythona wykonywany z `-c` albo z heredoca. Wzorce dobrane tak, by NIE łapać odczytu:
# `open(p, encoding="ascii")` nie może udawać `open(p, "a")`, dlatego tryb musi być krótkim,
# całym napisem w cudzysłowie, a nie dowolnym słowem zaczynającym się od litery trybu.
_PY_PISZE = re.compile(
    r"\.write_text\(|\.write\(|\bopen\([^)]*['\"][rbt+]*[wax][rbt+]*['\"]|"
    r"shutil\.(?:copy|move|rmtree)|\.unlink\(|\.mkdir\(|\.touch\(|"
    r"os\.(?:remove|rename|replace|unlink)|json\.dump\(|['\"]commit['\"]|['\"]add['\"]")


@dataclass(frozen=True)
class Blokada:
    """Zapis ciszy. Niezmienny — zmiana stanu to nowy plik, nie edycja istniejącego."""
    zeton: str
    pid: int
    powod: str
    zalozona: str          # ISO-8601, sekundy
    zalozona_ts: float     # monotonicznie porównywalny czas systemowy (TTL)
    ttl_s: int

    @property
    def wiek_s(self) -> float:
        return max(0.0, time.time() - self.zalozona_ts)

    @property
    def przeterminowana(self) -> bool:
        return self.wiek_s > self.ttl_s


# ══════════════════════════════════════════════════════════════════════════════
#  Żywotność procesu
# ══════════════════════════════════════════════════════════════════════════════
def proces_zyje(pid: int) -> bool:
    """Czy proces o tym PID-zie nadal żyje.

    Na Windowsie ŚWIADOMIE nie używamy `os.kill(pid, 0)`: dla sygnału spoza
    CTRL_C_EVENT/CTRL_BREAK_EVENT `os.kill` woła `TerminateProcess`, więc badanie
    żywotności zabiłoby badany proces — przyrząd zmieniający mierzoną wielkość.

    Zwracamy True przy niepewności (np. odmowa dostępu): fałszywe „żyje" kosztuje
    najwyżej czekanie do TTL, fałszywe „umarł" zdejmuje ciszę w trakcie biegu.
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            uchwyt = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if not uchwyt:
                # ERROR_INVALID_PARAMETER (87) = takiego procesu nie ma. Inne kody
                # (np. 5 = odmowa dostępu) znaczą „nie wiem" → nie zdejmujemy ciszy.
                return ctypes.get_last_error() != 87
            try:
                kod = wintypes.DWORD()
                if k32.GetExitCodeProcess(uchwyt, ctypes.byref(kod)):
                    return kod.value == _STILL_ACTIVE
                return True
            finally:
                k32.CloseHandle(uchwyt)
        except Exception:  # noqa: BLE001 — brak ctypes/WinAPI: nie zgadujemy śmierci
            return True
    try:
        os.kill(pid, 0)          # POSIX: sygnał 0 tylko sprawdza istnienie
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True              # istnieje, tylko cudzy
    except OSError:
        return True


# ══════════════════════════════════════════════════════════════════════════════
#  Stan blokady
# ══════════════════════════════════════════════════════════════════════════════
def _wczytaj() -> Optional[Blokada]:
    try:
        surowe = json.loads(PLIK_BLOKADY.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        # Plik uszkodzony (przerwany zapis). Uszkodzona blokada NIE blokuje — inaczej
        # jeden pół-zapisany bajt zamurowałby repo aż do ręcznej interwencji.
        return None
    try:
        return Blokada(
            zeton=str(surowe["zeton"]),
            pid=int(surowe["pid"]),
            powod=str(surowe.get("powod", "?")),
            zalozona=str(surowe.get("zalozona", "?")),
            zalozona_ts=float(surowe.get("zalozona_ts", 0.0)),
            ttl_s=int(surowe.get("ttl_s", TTL_DOMYSLNY_S)),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _usun_plik() -> None:
    try:
        PLIK_BLOKADY.unlink()
    except OSError:
        pass


def stan() -> Optional[Blokada]:
    """Żywa blokada albo None. Martwą (zgasły PID / po TTL) sprząta przy okazji.

    Sprzątanie w odczycie jest celowe: gdyby czekało na osobne wywołanie, po każdym
    crashu bramki repo zostawałoby zamurowane do chwili, gdy ktoś sobie przypomni.
    """
    if os.environ.get("SILENTIUM_OFF") == "1":
        return None
    b = _wczytaj()
    if b is None:
        return None
    # pid == 0 → CISZA RĘCZNA, bez procesu-właściciela (CLI `zaloz`). Bez tej gałęzi
    # ręczna blokada byłaby martwa w chwili narodzin: proces CLI kończy się natychmiast
    # po zapisie pliku, więc badanie żywotności PID-u zawsze orzekłoby śmierć. Wtedy
    # jedynym bezpiecznikiem jest TTL — i to wystarcza, bo ciszę ręczną zakłada człowiek.
    if b.przeterminowana or (b.pid > 0 and not proces_zyje(b.pid)):
        _usun_plik()
        return None
    return b


def aktywna() -> bool:
    return stan() is not None


def zaloz(powod: str, ttl_s: int = TTL_DOMYSLNY_S, pid: Optional[int] = None) -> Blokada:
    """Zakłada ciszę. Rzuca `RuntimeError`, gdy inna ŻYWA cisza już trwa.

    Tworzenie jest atomowe (`O_CREAT|O_EXCL`), więc dwa równoległe biegi bramki nie
    nadpiszą sobie żetonu — drugi dostanie wyjątek zamiast po cichu przejąć cudzą ciszę
    i zdjąć ją, kończąc się pierwszy.
    """
    biezaca = stan()
    if biezaca is not None:
        raise RuntimeError(
            f"SILENTIUM już trwa: {biezaca.powod} (pid {biezaca.pid}, "
            f"{biezaca.wiek_s:.0f}s). Poczekaj albo `zdejmij --sila`.")
    b = Blokada(
        zeton=uuid.uuid4().hex[:12],
        pid=int(pid if pid is not None else os.getpid()),
        powod=powod,
        zalozona=datetime.now().isoformat(timespec="seconds"),
        zalozona_ts=time.time(),
        ttl_s=int(ttl_s),
    )
    PLIK_BLOKADY.parent.mkdir(parents=True, exist_ok=True)
    tresc = json.dumps(asdict(b), ensure_ascii=False, indent=2)
    try:
        uchwyt = os.open(str(PLIK_BLOKADY), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as e:
        # Ktoś zdążył między `stan()` a `os.open`. Jeśli tamta jest martwa — sprzątamy
        # i próbujemy raz jeszcze; jeśli żywa, przegrywamy wyścig świadomie.
        if stan() is not None:
            raise RuntimeError("SILENTIUM: wyścig o blokadę — inny bieg był szybszy.") from e
        _usun_plik()
        uchwyt = os.open(str(PLIK_BLOKADY), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(uchwyt, "w", encoding="utf-8") as f:
        f.write(tresc)
    return b


def zdejmij(zeton: Optional[str] = None, sila: bool = False) -> bool:
    """Zdejmuje ciszę. Bez `sila` wymaga zgodnego żetonu — cudzej ciszy się nie zdejmuje."""
    b = _wczytaj()
    if b is None:
        return False
    if not sila and zeton is not None and b.zeton != zeton:
        return False
    _usun_plik()
    return True


@contextmanager
def cisza(powod: str, ttl_s: int = TTL_DOMYSLNY_S) -> Iterator[Optional[Blokada]]:
    """Menedżer kontekstu bramki: `with cisza("bramka testów"): ...`.

    Awaria założenia ciszy NIE przerywa bramki (oddajemy None i idziemy dalej, głośno) —
    strażnik jest szelkami, nie warunkiem istnienia biegu. Odwrotnie byłoby absurdem:
    testy nie mogłyby ruszyć, bo nie dało się ich ochronić przed edycją.
    """
    b: Optional[Blokada] = None
    try:
        b = zaloz(powod, ttl_s=ttl_s)
        print(f"🤫 SILENTIUM: cisza nad repo na czas biegu ({powod}, pid {b.pid}) — "
              f"zapisy Architekta odmawiane do końca.")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ SILENTIUM nie założone ({type(e).__name__}: {e}) — bieg idzie BEZ ochrony.")
    try:
        yield b
    finally:
        if b is not None and zdejmij(b.zeton):
            print("🤫 SILENTIUM: cisza zdjęta — repo znów otwarte na zapis.")


# ══════════════════════════════════════════════════════════════════════════════
#  Klasyfikacja: czy TO wywołanie pisze do repozytorium
# ══════════════════════════════════════════════════════════════════════════════
def _w_repo(sciezka: str) -> bool:
    """Czy ścieżka celuje w wersjonowaną część repozytorium.

    DWA PRZYPADKI ZMIERZONE JAKO FAŁSZYWE ALARMY (2 z 22 w pierwszej wersji):
      • `$TEMP/x.txt`, `$env:TEMP\\x.txt`, `%TEMP%\\x` — powłoka rozwinie je POZA repo,
        ale `Path` widzi napis względny i doklejał go do korzenia repozytorium;
      • `/tmp/x` — na Windowsie `Path("/tmp/x").is_absolute()` jest FAŁSZEM (brak litery
        dysku), więc ścieżka rdzennie POSIX-owa również lądowała „w repo".
    W obu razach strażnik blokowałby zapis do katalogu tymczasowego, czyli karałby
    zachowanie, którego sam wymaga (pisz do scratchpada, nie do repo).
    """
    if not sciezka:
        return False
    if "$" in sciezka or "%" in sciezka or sciezka.startswith("~"):
        return False                   # nierozwinięta zmienna — celu nie znamy, nie zgadujemy
    if sciezka.startswith("/") and not sciezka.startswith("//"):
        return False                   # ścieżka POSIX-owa (/tmp, /c/…) — nie nasze drzewo
    try:
        p = Path(sciezka)
        if not p.is_absolute():
            p = KORZEN / p
        p = Path(os.path.normpath(str(p)))
        wzgledna = p.relative_to(KORZEN)
    except (ValueError, OSError):
        return False               # poza repo (scratchpad, %TEMP%) — wolne
    if p == PLIK_BLOKADY:
        return False
    czesci = [c.lower() for c in wzgledna.parts]
    for wolny in _WOLNE_KATALOGI:
        elementy = [e.lower() for e in wolny.split("/")]
        if czesci[:len(elementy)] == elementy or elementy[-1] in czesci:
            return False
    return True


_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def rozdziel_kod(cmd: str) -> Tuple[str, List[str]]:
    """Komenda → (szkielet powłoki, lista ciał kodu).

    CIAŁO HEREDOCA NIE JEST SKŁADNIĄ POWŁOKI — to naprawa 8 z 22 zmierzonych fałszywych
    alarmów, największej pojedynczej klasy. Skrypt `python - <<'PY' … PY` czytający CSV
    zawierał w treści `>` albo nazwę organu i wyglądał jak zapis do repo. Ciało wraca
    osobno, bo dla `python` jest KODEM (zapis rozpoznajemy w nim inaczej), a dla powłoki
    jest DANYMI — ta sama zasada co „cudzysłów to treść" w CUSTOS LIMINIS.

    Obsługujemy też here-stringi PowerShella (`@'…'@`, `@"…"@`): na tej maszynie to forma
    codzienna, a jeden zmierzony przeciek — `python -c @"… dodaj(…) "@` dopisujący do
    INDEX FALSORUM — przechodził właśnie tędy.
    """
    tekst = cmd or ""
    ciala: List[str] = []
    for otw, zam in (("@'", "'@"), ('@"', '"@')):
        while True:
            i = tekst.find(otw)
            if i < 0:
                break
            j = tekst.find(zam, i + len(otw))
            if j < 0:
                break
            ciala.append(tekst[i + len(otw):j])
            tekst = tekst[:i] + " " + tekst[j + len(zam):]

    linie = tekst.split("\n")
    szkielet: List[str] = []
    i = 0
    while i < len(linie):
        znaleziony = _HEREDOC.search(linie[i])
        szkielet.append(_HEREDOC.sub(" ", linie[i]))
        if znaleziony:
            znacznik = znaleziony.group(2)
            cialo: List[str] = []
            i += 1
            while i < len(linie) and linie[i].strip() != znacznik:
                cialo.append(linie[i])
                i += 1
            ciala.append("\n".join(cialo))
        i += 1
    return "\n".join(szkielet), ciala


_SEPARATORY_ZNAKI = ("&&", "||", "|&", ";", "|", "\n")
_PREFIKSY_DO_ZDJECIA = ("{", "(", "then", "do", "else", "!", "time", "sudo", "exec")


def podziel_polecenia(tekst: str) -> List[str]:
    """Tekst powłoki → surowe podpolecenia, z SEPARATORAMI ROZPOZNAWANYMI POZA CUDZYSŁOWEM.

    Automat znakowy zamiast dzielenia napisu regexem — i to jest naprawa dwóch przeciwnych
    wad zmierzonych na realnych komendach:
      • cięcie po `\\n` przed tokenizacją rozrywało `python -c "…wielolinijkowy kod…"`,
        więc zapis schowany w kodzie stawał się niewidoczny (3 przecieki);
      • tokenizacja przed cięciem gubiła separator przyklejony do zamkniętego cudzysłowu
        (`cd "C:/repo"; git commit …`), więc `git commit` znikał w argumentach `cd`.
    Automat widzi jedno i drugie, bo zna stan cytowania w każdym punkcie.
    """
    czesci: List[str] = []
    biezaca: List[str] = []
    cudzyslow: Optional[str] = None
    i = 0
    tekst = tekst or ""
    while i < len(tekst):
        z = tekst[i]
        if cudzyslow:
            biezaca.append(z)
            if z == cudzyslow:
                cudzyslow = None
            i += 1
            continue
        if z in ("'", '"'):
            cudzyslow = z
            biezaca.append(z)
            i += 1
            continue
        trafiony = next((s for s in _SEPARATORY_ZNAKI if tekst.startswith(s, i)), None)
        if trafiony:
            czesci.append("".join(biezaca))
            biezaca = []
            i += len(trafiony)
            continue
        biezaca.append(z)
        i += 1
    czesci.append("".join(biezaca))
    return [c.strip() for c in czesci if c.strip()]


def _rozbij(cmd: str) -> List[List[str]]:
    """Szkielet powłoki → lista podpoleceń jako listy tokenów.

    Ze zdjętymi prefiksami, które NIE SĄ programem (`{`, `cd …`, `sudo`, `time`).
    Zmierzony przeciek: `… && { python tests/run_tests.py …; }` — pierwszym tokenem był
    nawias klamrowy, więc bramka odpalona w grupie poleceń nie była rozpoznana wcale.
    """
    grupy: List[List[str]] = []
    for kawalek in podziel_polecenia(cmd or ""):
        try:
            tokeny = shlex.split(kawalek, posix=False)
        except ValueError:
            tokeny = kawalek.split()
        while tokeny and tokeny[0] in _PREFIKSY_DO_ZDJECIA:
            tokeny = tokeny[1:]
        # `cd <gdzieś>` przed właściwym poleceniem — zdejmujemy wraz z argumentem.
        while len(tokeny) >= 2 and _nazwa_programu(tokeny[0]) == "cd":
            tokeny = tokeny[2:]
        if tokeny:
            grupy.append(tokeny)
    return grupy


def _nazwa_programu(token: str) -> str:
    exe = token.strip("'\"").replace("\\", "/").rsplit("/", 1)[-1].lower()
    return exe[:-4] if exe.endswith(".exe") else exe


def _cel_przekierowania(tokeny: List[str]) -> Optional[str]:
    """Ścieżka po `>` / `>>` albo None. `2>&1` i `>$null` nie są zapisem do pliku."""
    for i, t in enumerate(tokeny):
        if t[:1] in ("'", '"'):
            continue
        m = re.search(r"(?<!\d)>{1,2}(.*)$", t)
        if not m:
            continue
        cel = m.group(1).strip("'\"")
        if not cel and i + 1 < len(tokeny):
            cel = tokeny[i + 1].strip("'\"")
        if not cel or cel.startswith("&") or cel.lower() in ("$null", "/dev/null", "nul"):
            continue
        return cel
    return None


_LITERAL = re.compile(r"""[rbf]?['"]([^'"\n]{2,200})['"]""")
_ODBIORCA = re.compile(r"(\w+)\s*\.\s*(?:write_text|write|open|unlink|mkdir|touch)\s*\(")


def _wyglada_na_sciezke(s: str) -> bool:
    return "/" in s or "\\" in s or s in (".", "..") or bool(re.search(r"\.\w{1,5}$", s))


def _zapis_poza_repo(linia: str, wczesniejsze: List[str]) -> bool:
    """Czy zapis w TEJ linii kodu na pewno celuje poza repozytorium.

    Rozstrzygamy po ŚCIEŻCE PRZYPISANEJ DO ZAPISU, nie po dowolnym napisie w skrypcie —
    inaczej `sys.path.insert(0,'narzedzia/rag')` (ścieżka w repo) kazałoby oskarżyć skrypt,
    który zapisuje wyłącznie do scratchpada. Gdy odbiorcy nie da się rozwiązać, wracamy
    do oskarżenia: niewiedza ma kosztować czekanie, nie unieważniony bieg.
    """
    kandydaci = [s for s in _LITERAL.findall(linia) if _wyglada_na_sciezke(s)]
    odbiorca = _ODBIORCA.search(linia)
    if odbiorca:
        nazwa = odbiorca.group(1)
        przypisanie = re.compile(rf"\b{re.escape(nazwa)}\b\s*(?:=|in)\s")
        for wczesniej in [linia, *reversed(wczesniejsze)]:
            if przypisanie.search(wczesniej):
                kandydaci += [s for s in _LITERAL.findall(wczesniej) if _wyglada_na_sciezke(s)]
                break
    return bool(kandydaci) and not any(_w_repo(s) for s in kandydaci)


def _kod_pisze(cialo: str) -> Optional[str]:
    """Czy ciało kodu Pythona zapisuje DO REPO — albo None.

    Dwie drogi: (a) prymitywy zapisu (`write_text`, `open(…, "w")`, `unlink`…),
    (b) organ Imperium wywołany z czasownikiem zapisu (`index_falsorum` + `dodaj`).
    Ciała bez żadnej z nich to skrypty czytające — najliczniejsza grupa w tym repo.

    Zapis do scratchpada, `%TEMP%` i katalogu pamięci NIE liczy się jako brud (zmierzone:
    4 z 6 pozostałych fałszywych alarmów to były heredoki piszące poza repo).
    """
    linie = cialo.split("\n")
    zapisy = [(i, ln) for i, ln in enumerate(linie) if _PY_PISZE.search(ln)]
    if zapisy and not all(_zapis_poza_repo(ln, linie[:i]) for i, ln in zapisy):
        return "kod Pythona zapisuje plik w repo (write/open-w/unlink)"
    maly = cialo.lower()
    for organ in _ORGANY:
        if organ in maly and _WERBY_PISZACE.search(maly):
            return f"kod woła organ `{organ}` w trybie zapisu"
    return None


def komenda_pisze(cmd: str) -> Optional[str]:
    """Powód, dla którego komenda pisze do repo — albo None (czyta / pisze poza repo).

    HEURYSTYKA Z POMIAREM, NIE Z INTUICJI: to jedyny nieoczywisty fragment SILENTIUM,
    więc ma kalibrację na 120 zaetykietowanych realnych komendach z transkryptów tego
    projektu (`narzedzia/kalibracja_silentium.py`, korpus 5571 unikalnych). Przyrząd bez
    pomiaru samego siebie nie istnieje (LEX TALARUS) — a pierwsza, „oczywista" wersja tego
    klasyfikatora miała precyzję 63% i przepuszczała 11 z 60 zapisów.
    """
    szkielet, ciala = rozdziel_kod(cmd or "")
    for cialo in ciala:
        powod = _kod_pisze(cialo)
        if powod:
            return powod
    for tokeny in _rozbij(szkielet):
        if not tokeny:
            continue
        # przypisania zmiennych na przedzie (`FOO=bar git add .`)
        i = 0
        while i < len(tokeny) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokeny[i]):
            i += 1
        czyste = tokeny[i:]
        if not czyste:
            continue
        exe = _nazwa_programu(czyste[0])

        cel = _cel_przekierowania(czyste)
        if cel is not None and _w_repo(cel):
            return f"przekierowanie do `{cel}` (zapis w repo)"

        if exe == "git":
            j = 1
            while j < len(czyste):
                t = czyste[j]
                if t in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"):
                    j += 2
                    continue
                if t.startswith("-"):
                    j += 1
                    continue
                if t.lower() in _GIT_PISZE:
                    return f"`git {t.lower()}` zmienia drzewo/indeks repozytorium"
                break
            continue

        if exe in _EXE_PISZE:
            # Cel bierzemy z pierwszego argumentu niebędącego opcją; brak celu = nie zgadujemy.
            for t in czyste[1:]:
                if t.startswith("-"):
                    continue
                if _w_repo(t.strip("'\"")):
                    return f"`{exe}` pisze do `{t.strip(chr(39) + chr(34))}`"
                break
            continue

        if exe == "sed" and any(_SED_INPLACE.match(t) for t in czyste[1:]):
            return "`sed -i` nadpisuje plik w miejscu"

        if exe in ("python", "python3", "py"):
            # Argumenty CYTOWANE są treścią (prozą wpisu), nie składnią — po nich nie
            # szukamy czasownika zapisu. To dokładnie ta pomyłka, przez którą długi
            # `dziennik wpis --co "…"` uchodził za odczyt, gdy w prozie trafiło się
            # słowo z listy trybów odczytu.
            skladnia = " ".join(t for t in czyste if t[:1] not in ("'", '"')).lower()
            if "--help" in skladnia or "-h" == skladnia.split()[-1:]:
                continue
            for skrypt in _SKRYPTY_PISZACE:
                if skrypt.replace("\\", "/") in skladnia.replace("\\", "/"):
                    return f"`{skrypt}` odciska SIGILLUM PROBATIONIS w repo (to sama bramka)"
            trafiony = next((o for o in _ORGANY if o in skladnia), None)
            if trafiony and _WERBY_PISZACE.search(skladnia):
                return f"organ `{trafiony}` dopisuje do wersjonowanego ledgera"
            # `python -c "<kod>"` — cudzysłów jest tu WYKONYWANY, więc treść to kod.
            if "-c" in czyste:
                for t in czyste[czyste.index("-c") + 1:]:
                    powod = _kod_pisze(t.strip("'\""))
                    if powod:
                        return powod
                    break
            continue

        if exe.lower() in _PS_PISZE or any(_nazwa_programu(t) in _PS_PISZE for t in czyste[:1]):
            for t in czyste[1:]:
                if t.startswith("-"):
                    continue
                if _w_repo(t.strip("'\"")):
                    return f"`{czyste[0]}` pisze do `{t.strip(chr(39) + chr(34))}`"
                break
    return None


def ocen(tool_name: str, tool_input: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Werdykt dla hooka PreToolUse albo None (cisza strażnika = zwykły tryb uprawnień)."""
    b = stan()
    if b is None:
        return None
    ogon = max(0, b.ttl_s - int(b.wiek_s))
    stopka = (f"Bramka trwa: {b.powod} (pid {b.pid}, {b.wiek_s:.0f}s, TTL za {ogon}s). "
              f"Zapis TERAZ unieważnia bieg — poczekaj na wynik. Awaryjnie: "
              f"`python -m imperium.pretorianie.silentium zdejmij --sila`.")

    if tool_name in NARZEDZIA_ZAPISU:
        sciezka = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if _w_repo(sciezka):
            return {"permissionDecision": "deny",
                    "permissionDecisionReason": f"🤫 SILENTIUM: zapis do `{sciezka}`. {stopka}"}
        return None

    if tool_name in NARZEDZIA_POWLOKI:
        powod = komenda_pisze(str(tool_input.get("command") or ""))
        if powod:
            return {"permissionDecision": "deny",
                    "permissionDecisionReason": f"🤫 SILENTIUM: {powod}. {stopka}"}
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  Protokół hooka + CLI
# ══════════════════════════════════════════════════════════════════════════════
def _hook() -> int:
    try:
        zdarzenie = json.load(sys.stdin)
    except Exception as e:  # noqa: BLE001 — awaria strażnika nie blokuje pracy, ale krzyczy
        print(f"[silentium] nie odczytałem zdarzenia hooka: {type(e).__name__}: {e}",
              file=sys.stderr)
        return 1
    try:
        werdykt = ocen(zdarzenie.get("tool_name") or "", zdarzenie.get("tool_input") or {})
    except Exception as e:  # noqa: BLE001
        print(f"[silentium] błąd oceny: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if werdykt is None:
        return 0
    # ensure_ascii=True świadomie — konsola cp1250 nie uniesie emoji, a mojibake
    # w protokole hooka skasowałby barierę przez KOSMETYKĘ (lekcja CUSTOS LIMINIS).
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **werdykt}}))
    return 0


def _opis_stanu() -> Tuple[str, int]:
    b = stan()
    if b is None:
        return "🤫 SILENTIUM: brak ciszy — repo otwarte na zapis.", 0
    return (f"🤫 SILENTIUM AKTYWNE: {b.powod}\n"
            f"   pid {b.pid} | żeton {b.zeton} | założona {b.zalozona} "
            f"| wiek {b.wiek_s:.0f}s | TTL {b.ttl_s}s", 1)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "hook":
        return _hook()
    polecenie = argv[0]
    if polecenie == "stan":
        if "--json" in argv:
            b = stan()
            print(json.dumps(asdict(b) if b else {}, ensure_ascii=False))
            return 0
        tekst, kod = _opis_stanu()
        print(tekst)
        return kod
    if polecenie == "zaloz":
        powod = argv[1] if len(argv) > 1 and not argv[1].startswith("-") else "ręczna cisza"
        try:
            b = zaloz(powod, pid=0)          # cisza ręczna: właścicielem jest człowiek, nie proces
        except RuntimeError as e:
            print(f"❌ {e}")
            return 1
        print(f"🤫 SILENTIUM założone: {powod} (żeton {b.zeton}, pid {b.pid})")
        return 0
    if polecenie == "zdejmij":
        if zdejmij(sila="--sila" in argv):
            print("🤫 SILENTIUM zdjęte.")
            return 0
        print("🤫 Nie było czego zdejmować (albo żeton się nie zgadza — użyj --sila).")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
