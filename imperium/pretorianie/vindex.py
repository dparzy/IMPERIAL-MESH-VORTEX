"""⚖️ VINDEX — obrońca zapisu: czy ktoś zmienił to, co miało zostać niezmienne.

Rzymski *vindex* to ten, kto **występuje w obronie naruszonego prawa** — nie doradza,
nie ocenia zamiaru, staje po stronie zapisu, gdy ten został tknięty. Ten organ robi
jedno: pyta, czy zmiana w repozytorium **złamała kontrakt swojego pliku**.

POWÓD ISTNIENIA (zmierzony 2026-08-02, rozkaz Cezara — zakres B):
Kontrakt „append-only" jest DEKLAROWANY w docstringach co najmniej sześciu organów
(`codex_notarum`, `index_falsorum`, `dziennik_niesmiertelny`, Scriba Codex…) oraz
w nagłówku `LOG_ZMIAN.md` („wpisów NIE aktualizujemy wstecz — ROZKAZ STAŁY, Prawo I").
`grep` po `imperium/`, `narzedzia/` i `tests/` pokazuje **same deklaracje — zero
egzekucji**. To ta sama klasa co runbook W11: zasada zapisana, mechanizmu brak.

Stawka jest wyższa niż przy obcych plikach: `rejestr_testow.jsonl` jest źródłem prawdy
naszych POMIARÓW. Cicha zmiana jednej starej linii unieważnia wyniki, na których stoją
decyzje o składzie roju — i nikt się nie dowie. Dowód, że to nie teoria: `bc4913c`
usunął z `index_falsorum` wpis, który miał już wypełnione pole `wycofane`, czyli
nagrobek mający „zostać na zawsze". Wpis wrócił później dopisany na nowo, więc szkoda
się nie utrwaliła — ale **przez sześć dni nikt tego nie zauważył, bo nic nie patrzyło**.

DLACZEGO KLASY, A NIE JEDEN ALARM NA KAŻDĄ ZMIANĘ:
879 plików w repo, 449 `.py`. Strażnik krzyczący na każdą edycję jest tapetą, a tapeta
uczy ignorowania siebie — mamy to ZMIERZONE na EXACTORZE (pierwsza wersja: 80% alarmów
na poprawnych meldunkach). Wartość jest nie w wykryciu ZMIANY, tylko w wykryciu zmiany
łamiącej kontrakt DANEGO pliku.

KONTRAKTY POCHODZĄ Z POMIARU, NIE Z NAZWY PLIKU (kalibracja 2026-08-02 na `git log
--numstat`, 25 plików — 9 ledgerów JSONL + 16 dokumentów typu ACTA):
  • **ŚCISŁY** — zero usunięć w CAŁEJ historii: `codex_notarum` (29 commitów),
    `dziennik_niesmiertelny` (140), `tiro_pary_nauczyciela` (28). Usunięcie linii to
    zdarzenie bez precedensu → ALARM.
  • **KORYGOWALNY** — usunięcia rzadkie i uzasadnione: `rejestr_testow` (1 na 48 —
    migracja formatu przy Scribie), `ksiega_wad_kodu` (2 na 57 — naprawa martwych
    wzorców regex), `index_falsorum` (1 na 9), `ab_plon_hyginusa` (1 na 3). Korekta
    bywa legalna → PYTANIE o uzasadnienie, nie blokada.
  • **MUTOWALNY Z NATURY** — `wizje_i_decyzje` (4 na 83: status POMYSŁ→WDROŻONA jest
    całym sensem tego ledgera) i `procedury` (3 na 4: runbooki aktualizuje hook W11).
    Tu zmiana istniejącej linii jest POPRAWNYM zachowaniem → CISZA.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ **Nie kasuje i nie przenosi obcych plików** — rozkaz Cezara z 2026-07-28: obcy
    plik ma trafić do kwarantanny/wrzutni z pytaniem „co to jest", nigdy do kosza.
    Organ WSKAZUJE i pyta; ruch wykonuje człowiek.
  • ❌ **Nie sądzi dokumentów ACTA (`.md`) miarą liniową** — i to jest granica ZMIERZONA,
    nie przeoczona. W JSONL linia = rekord, więc usunięcie jest jednoznaczne. W markdownie
    zmiana `stan_na:` we frontmatterze też jest „usuniętą linią": `LOG_ZMIAN.md` ma 330
    takich na 379 commitów. Objęcie ACTA tą miarą zbudowałoby generator fałszywek.
    Dlatego ACTA idą do pola `niepokryte` — JAWNIE, jak krok 9 u EXACTORA (lekcja:
    „bramka o wąskim zasięgu daje fałszywy spokój" — leczy się ją nazwaniem zasięgu,
    nie udawaniem, że go nie ma).
  • ❌ Nie ocenia TREŚCI zmiany — czy nowy wpis jest mądry, rozstrzyga sąd, nie strażnik.

CO ZMIERZONE O CZĘSTOTLIWOŚCI: ~8 zdarzeń „usunięta linia w ledgerze" na ~230 commitów
dotykających ledgerów ≈ **3,5%**. Strażnik odzywający się raz na trzydzieści commitów
jest czytany; ten odzywający się zawsze — nie.

DROGA NA GRAF (doktryna Cezara 2026-08-02: „domykać loop, otwierać drogę na graph"):
`krawedzie()` zwraca każdy werdykt jako trójkę **(plik) —[naruszenie|korekta]→ (commit)**
z klasą i powodem. To jest gotowy materiał na węzły i krawędzie grafu W8 — pamięć
o tym, CO było ruszane i DLACZEGO, w postaci relacji, a nie płaskiego wpisu do czytania.
"""
from __future__ import annotations

import fnmatch
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

KORZEN = Path(__file__).resolve().parent.parent.parent

# ── KONTRAKTY (z kalibracji na historii gita, nie z nazw) ────────────────────────
SCISLY = "scisly"              # zero usunięć w historii → usunięcie = ALARM
KORYGOWALNY = "korygowalny"    # usunięcia rzadkie i uzasadnione → PYTANIE
MUTOWALNY = "mutowalny"        # zmiana istniejącej linii to poprawne zachowanie → CISZA

KONTRAKTY: Dict[str, str] = {
    "bibliotheca_ulpia/dane/codex_notarum.jsonl": SCISLY,
    "bibliotheca_ulpia/dane/dziennik_niesmiertelny.jsonl": SCISLY,
    "bibliotheca_ulpia/dane/tiro_pary_nauczyciela.jsonl": SCISLY,
    "bibliotheca_ulpia/dane/rejestr_testow.jsonl": KORYGOWALNY,
    "bibliotheca_ulpia/dane/ksiega_wad_kodu.jsonl": KORYGOWALNY,
    "bibliotheca_ulpia/dane/index_falsorum.jsonl": KORYGOWALNY,
    "bibliotheca_ulpia/dane/ab_plon_hyginusa.jsonl": KORYGOWALNY,
    "bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl": MUTOWALNY,
    "bibliotheca_ulpia/dane/procedury.jsonl": MUTOWALNY,
    # Ledger migawek MATURITASA (2026-08-02) — jedyny wpis, którego podstawą NIE jest
    # historia, bo jej jeszcze nie ma. Podstawą jest KOD (Prawo XIX): `zapisz_migawke`
    # otwiera plik wyłącznie w trybie "a", a migawka ma sens tylko jako ciąg w czasie —
    # nadpisanie starej odbiera organowi zdolność mierzenia DELTY, czyli jego rację bytu.
    "bibliotheca_ulpia/dane/maturitas_migawki.jsonl": SCISLY,
}

# Miejsca, gdzie NOWY plik jest normalną pracą, a nie zjawiskiem do wyjaśnienia.
# Wrzutnia jest z definicji miejscem na rzeczy przyniesione z zewnątrz przez Cezara;
# kronika rośnie sama po każdej sesji. Alarm tutaj byłby alarmem na oddychanie.
KATALOGI_SWOBODNE: Tuple[str, ...] = (
    "wrzutnia/",
    "bibliotheca_ulpia/dane/kronika/",
    "raporty/",
)

# Nowy plik o tym rozszerzeniu w miejscu nieswobodnym pyta GŁOŚNIEJ: kod i dane wchodzą
# do Imperium przez deklarację (CENSUS, TABULARIUM), nie przez samo pojawienie się.
ROZSZERZENIA_WAZNE: Tuple[str, ...] = (".py", ".jsonl", ".json", ".sh", ".md")


def klasa_pliku(sciezka: str) -> Optional[str]:
    """Kontrakt pliku albo None, gdy plik nie jest objęty strażą.

    Dopasowanie po ścieżce znormalizowanej do ukośników POSIX — repo bywa czytane
    i na Windowsie, i w chmurze, a strażnik rozpoznający plik tylko na jednym systemie
    to strażnik niespójny ze sobą (ta sama klasa, co wada E1 EXACTORA).
    """
    return KONTRAKTY.get(sciezka.replace("\\", "/").lstrip("./"))


# ── RDZEŃ — czysty, bez gita i bez wejścia/wyjścia ───────────────────────────────

def ocen_zmiane(sciezka: str, dodane: int, usuniete: int,
                klasa: Optional[str] = None) -> Dict[str, Any]:
    """Werdykt o JEDNEJ zmianie pliku. `dodane`/`usuniete` to liczby linii z `numstat`.

    Sedno miary: commit, który TYLKO dopisuje na końcu, ma `usuniete == 0`. Każde
    usunięcie znaczy, że istniejąca treść została zmieniona albo skasowana — a w pliku
    JSONL linia jest rekordem, więc to nie jest kosmetyka formatowania.
    """
    klasa = klasa or klasa_pliku(sciezka)
    if klasa is None:
        return {"plik": sciezka, "klasa": None, "werdykt": "POZA_STRAZA", "ikona": "·",
                "usuniete": usuniete, "dodane": dodane,
                "opis": "plik nie ma zadeklarowanego kontraktu — straż go nie obejmuje"}
    if usuniete == 0:
        return {"plik": sciezka, "klasa": klasa, "werdykt": "DOPISANIE", "ikona": "✅",
                "usuniete": 0, "dodane": dodane,
                "opis": f"tylko dopisanie ({dodane} linii) — kontrakt zachowany"}
    if klasa == MUTOWALNY:
        return {"plik": sciezka, "klasa": klasa, "werdykt": "ZMIANA_DOZWOLONA", "ikona": "·",
                "usuniete": usuniete, "dodane": dodane,
                "opis": "ten ledger z natury aktualizuje istniejące wpisy (statusy, runbooki)"}
    if klasa == KORYGOWALNY:
        return {"plik": sciezka, "klasa": klasa, "werdykt": "KOREKTA_DO_UZASADNIENIA",
                "ikona": "⚠️", "usuniete": usuniete, "dodane": dodane,
                "opis": f"usunięto/zmieniono {usuniete} istniejących linii. W historii tego "
                        "pliku korekta zdarzała się rzadko i zawsze miała powód (migracja "
                        "formatu, naprawa martwego wzorca) — podaj powód albo cofnij"}
    return {"plik": sciezka, "klasa": klasa, "werdykt": "NARUSZENIE_ZAPISU", "ikona": "🚨",
            "usuniete": usuniete, "dodane": dodane,
            "opis": f"usunięto/zmieniono {usuniete} istniejących linii w ledgerze, który "
                    "w CAŁEJ historii nie miał ani jednego takiego zdarzenia. To zapis "
                    "deklarujący niezmienność (Prawo I: historii się nie falsyfikuje)"}


def ocen_obcy(sciezka: str) -> Dict[str, Any]:
    """Werdykt o pliku nieśledzonym. NIGDY nie proponuje kasowania (rozkaz Cezara)."""
    p = sciezka.replace("\\", "/")
    if any(p.startswith(k) for k in KATALOGI_SWOBODNE):
        return {"plik": sciezka, "werdykt": "SWOBODNY", "ikona": "·",
                "opis": "katalog, w którym nowe pliki są normalną pracą"}
    wazny = p.endswith(ROZSZERZENIA_WAZNE)
    return {
        "plik": sciezka, "werdykt": "OBCY_WAZNY" if wazny else "OBCY", "ikona": "⚠️",
        "opis": ("nieśledzony plik kodu/danych poza katalogami swobodnymi — zadeklaruj go "
                 "(CENSUS/TABULARIUM) albo przenieś do `wrzutnia/`. Nie kasuj: rzecz "
                 "nieznana bywa cudzą pracą, a nie śmieciem"
                 if wazny else
                 "nieśledzony plik poza katalogami swobodnymi — wyjaśnij, czym jest"),
    }


def podsumuj(werdykty: List[Dict[str, Any]], obce: List[Dict[str, Any]],
             niepokryte: Optional[List[str]] = None) -> Dict[str, Any]:
    """Zbiorczy werdykt + kod wyjścia. `exit` jest częścią kontraktu bramki."""
    naruszenia = [w for w in werdykty if w["werdykt"] == "NARUSZENIE_ZAPISU"]
    korekty = [w for w in werdykty if w["werdykt"] == "KOREKTA_DO_UZASADNIENIA"]
    obce_wazne = [o for o in obce if o["werdykt"] == "OBCY_WAZNY"]
    if naruszenia:
        status, ikona, kod = "naruszenie", "🚨", 1
    elif korekty or obce_wazne:
        status, ikona, kod = "do_wyjasnienia", "⚠️", 1
    else:
        status, ikona, kod = "czysto", "✅", 0
    return {
        "status": status, "ikona": ikona, "exit": kod,
        "naruszenia": naruszenia, "korekty": korekty,
        "obce": [o for o in obce if o["werdykt"] != "SWOBODNY"],
        "zbadane": len([w for w in werdykty if w["klasa"]]),
        # Zasięg JAWNY, nie domyślny — patrz docstring modułu.
        "niepokryte": niepokryte if niepokryte is not None else [
            "dokumenty ACTA (.md) — miara liniowa daje tam fałszywki (frontmatter `stan_na`)",
            "pliki ignorowane przez .gitignore — poza zasięgiem gita, więc i straży",
        ],
    }


def krawedzie(werdykty: List[Dict[str, Any]], commit: str = "ROBOCZE") -> List[Dict[str, str]]:
    """Werdykty jako KRAWĘDZIE dla grafu pamięci (W8) — doktryna „otwieraj drogę na graph".

    Płaski raport ginie po przeczytaniu; relacja `(plik) —[typ]→ (commit)` zostaje
    i daje się później pytać: co ruszaliśmy, kiedy i z jakim werdyktem.
    """
    return [{"od": w["plik"], "relacja": w["werdykt"], "do": commit,
             "klasa": w["klasa"] or "", "powod": w["opis"]}
            for w in werdykty if w["klasa"] and w["werdykt"] not in ("DOPISANIE",)]


# ── ADAPTERY GITA ────────────────────────────────────────────────────────────────

def _git(*args: str) -> Optional[str]:
    """stdout gita albo None przy awarii — brak gita NIE jest naruszeniem (Prawo I)."""
    try:
        p = subprocess.run(["git", *args], cwd=KORZEN, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def _numstat(surowe: Optional[str]) -> List[Tuple[str, int, int]]:
    """Parsuje `--numstat` → [(ścieżka, dodane, usunięte)]. Binaria („-") pomijane."""
    wynik = []
    for linia in (surowe or "").splitlines():
        czesci = linia.split("\t")
        if len(czesci) != 3 or not czesci[0].isdigit() or not czesci[1].isdigit():
            continue
        wynik.append((czesci[2].strip(), int(czesci[0]), int(czesci[1])))
    return wynik


class GitNieodpowiada(RuntimeError):
    """Git nie dał odpowiedzi — stan repozytorium jest NIEZNANY, nie czysty.

    Naprawa P1 z recenzji cubic PR #139. `_git()` zwraca `None` przy awarii, a `_numstat`
    zamieniało to na pustą listę — więc padnięty git, brak repozytorium czy timeout
    dawały werdykt `czysto` z kodem wyjścia 0. Hook zatwierdzał wtedy repozytorium,
    KTÓREGO NIE OBEJRZAŁ. To jest ta sama klasa, którą sam VINDEX powstał ścigać:
    cisza raportowana jako spokój. Brak wiedzy musi mieć własną nazwę.
    """


# `--no-renames` JEST WARUNKIEM POPRAWNOŚCI, nie kosmetyką (P1, cubic PR #139): przy
# wykrywaniu zmian nazw git pisze `0\t0\tdocs/{stary.md => nowy.md}`, czyli ZERO usunięć
# pod ścieżką, która nie pasuje do żadnego chronionego ledgera. Ktoś mógłby więc usunąć
# ledger o kontrakcie ŚCISŁYM przez zwykły `git mv`, a strażnik zameldowałby czysto.
# Bez tej flagi stara ścieżka jest liczona jako usunięcie — i tak ma być.
_ARG_BEZ_RENAME = "--no-renames"


OKNO_SWIEZOSCI_S = 120


def _commit_swiezy(okno_s: int = OKNO_SWIEZOSCI_S) -> bool:
    """Czy HEAD powstał w ciągu ostatnich `okno_s` sekund (czyli mógł być dziełem
    komendy, po której właśnie odpalił się hook).

    Okno, nie „zawsze": doklejanie zawartości HEAD do KAŻDEGO badania drzewa roboczego
    kazałoby strażnikowi w kółko oceniać dawno zatwierdzone commity i zamieniłoby
    jednorazowe naruszenie w alarm powtarzany bez końca — a alarm, którego nie da się
    wyciszyć, uczy ignorowania alarmów (lekcja z Refleksji W9, 2026-07-20).
    """
    surowe = _git("log", "-1", "--format=%ct")
    if surowe is None or not surowe.strip().isdigit():
        return False
    return (time.time() - int(surowe.strip())) <= okno_s


def zmiany_robocze() -> List[Dict[str, Any]]:
    """Niezacommitowane zmiany w drzewie roboczym (łącznie z poczekalnią)."""
    surowe = _git("diff", _ARG_BEZ_RENAME, "--numstat", "HEAD")
    if surowe is None:
        raise GitNieodpowiada("git diff nie odpowiedział — stan drzewa roboczego NIEZNANY")
    return [ocen_zmiane(s, d, u) for s, d, u in _numstat(surowe)]


def zmiany_commitu(ref: str = "HEAD") -> List[Dict[str, Any]]:
    """Zmiany JEDNEGO commitu — do bramki i do wglądu wstecz."""
    surowe = _git("show", _ARG_BEZ_RENAME, "--numstat", "--format=", ref)
    if surowe is None:
        raise GitNieodpowiada(f"git show {ref} nie odpowiedział — zawartość commitu NIEZNANA")
    return [ocen_zmiane(s, d, u) for s, d, u in _numstat(surowe)]


def _ignorowane_dodatkowo() -> Tuple[str, ...]:
    """Wzorce z `.gitignore`, których git czasem nie zastosuje (np. plik już śledzony)."""
    plik = KORZEN / ".gitignore"
    if not plik.exists():
        return ()
    return tuple(l.strip() for l in plik.read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.strip() and not l.startswith("#"))


def obce_pliki() -> List[Dict[str, Any]]:
    """Pliki nieśledzone przez gita (git sam odfiltrowuje `.gitignore`)."""
    surowe = _git("status", "--porcelain", "--untracked-files=all")
    wzorce = _ignorowane_dodatkowo()
    wynik = []
    for linia in (surowe or "").splitlines():
        if not linia.startswith("??"):
            continue
        sciezka = linia[3:].strip().strip('"')
        if any(fnmatch.fnmatch(sciezka, w) for w in wzorce):
            continue
        wynik.append(ocen_obcy(sciezka))
    return wynik


def zbadaj(ref: Optional[str] = None, *, tylko_kontrakty: bool = False) -> Dict[str, Any]:
    """Pełny werdykt: zmiany (robocze albo z commitu) + obce pliki.

    `tylko_kontrakty=True` ODCINA badanie obcych plików — i jest to decyzja z pomiaru,
    nie z wygody. Hook po komendzie powłoki odpala się dziesiątki razy na wachtę, a plik
    roboczy jest „obcy" od chwili powstania aż do `git add`: przy pełnym zasięgu strażnik
    krzyczałby na KAŻDY nowy plik, który sam właśnie tworzę (złapane na sobie —
    `vindex.py` był pierwszym obcym plikiem, jaki ten organ zgłosił).

    To ta sama zasada, którą EXACTOR stosuje do kroku 8: w automacie odpalanym stale
    wolno badać WYŁĄCZNIE powinność o zmierzonej odzywalności. Kontrakty ledgerów mają
    2,0% na 254 commitach; obce pliki nie mają takiego pomiaru i idą do bramki, która
    chodzi raz na zadanie.
    """
    try:
        werdykty = zmiany_commitu(ref) if ref else zmiany_robocze()
    except GitNieodpowiada as e:
        # NIEZNANE ≠ CZYSTO (P1, cubic PR #139). Nie udajemy werdyktu, którego nie mamy:
        # meldujemy wprost, że badanie się nie odbyło, i mówimy to głośno w raporcie.
        return {"status": "nieznane", "ikona": "🚨", "zbadane": 0,
                "naruszenia": [], "korekty": [], "obce": [], "krawedzie": [],
                "zasieg": "ŻADEN — git nie odpowiedział",
                "niepokryte": [f"CAŁE repozytorium: {e}"]}
    # ŚWIEŻY COMMIT TEŻ JEST BADANY (P1, cubic PR #139). Hook po komendzie powłoki
    # porównywał wyłącznie drzewo robocze z HEAD — więc komenda, która JEDNOCZEŚNIE
    # zmieniała ledger i commitowała (`git commit -am`), znikała strażnikowi z oczu:
    # zmiana była już w HEAD, a drzewo czyste. Naruszenie popełnione i zatwierdzone
    # w jednym ruchu było NIEWIDZIALNE. Dokładamy zawartość ostatniego commitu, jeśli
    # powstał w ciągu okna komendy — koszt jeden `git show`, zysk domknięcie luki.
    if ref is None:
        try:
            if _commit_swiezy():
                werdykty = werdykty + zmiany_commitu("HEAD")
        except GitNieodpowiada:
            pass  # brak wiedzy o commicie nie może skasować wiedzy o drzewie roboczym
    wynik = podsumuj(werdykty, [] if tylko_kontrakty else obce_pliki())
    wynik["krawedzie"] = krawedzie(werdykty, ref or "ROBOCZE")
    wynik["zasieg"] = "kontrakty" if tylko_kontrakty else "pelny"
    if tylko_kontrakty:
        wynik["niepokryte"] = ["obce pliki — badane przez bramkę, nie przez hook "
                               "(plik roboczy jest obcy aż do `git add`)"] + wynik["niepokryte"]
    return wynik


# ── WYDRUK ───────────────────────────────────────────────────────────────────────

def raport(w: Dict[str, Any]) -> str:
    """CISZA GDY ZIELONE, KRZYK GDY CZERWONE — ta sama zasada, co u VIGILA."""
    linie = [f"{w['ikona']} VINDEX (obrońca zapisu): {w['zbadane']} plików pod kontraktem"]
    for n in w["naruszenia"]:
        linie.append(f"   🚨 {n['plik']} — {n['opis']}")
    for k in w["korekty"]:
        linie.append(f"   ⚠️ {k['plik']} — {k['opis']}")
    for o in w["obce"]:
        linie.append(f"   ⚠️ OBCY PLIK: {o['plik']} — {o['opis']}")
    if w["status"] == "czysto":
        linie.append("   kontrakty zachowane, brak obcych plików wymagających wyjaśnienia")
    linie.append(f"   ℹ️ zasięg (JAWNY): {len(w['niepokryte'])} obszarów NIE jest badanych:")
    for n in w["niepokryte"]:
        linie.append(f"      • {n}")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(
        description="VINDEX — czy zmiana złamała kontrakt swojego pliku")
    ap.add_argument("--commit", nargs="?", const="HEAD", default=None,
                    help="zbadaj commit (domyślnie: niezacommitowane zmiany robocze)")
    ap.add_argument("--kontrakty", action="store_true", help="wypisz kontrakty i zakończ")
    ap.add_argument("--tylko-kontrakty", action="store_true",
                    help="pomiń obce pliki (tryb hooka: bada wyłącznie kontrakty ledgerów)")
    ap.add_argument("--hook", action="store_true",
                    help="tryb hooka PostToolUse: cisza gdy zielone, krzyk gdy czerwone")
    ap.add_argument("--krawedzie", action="store_true", help="wypisz krawędzie dla grafu W8")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--bramka", action="store_true", help="kod wyjścia wg werdyktu")
    args = ap.parse_args()

    if args.kontrakty:
        print("⚖️ VINDEX — kontrakty (zmierzone na historii gita 2026-08-02):")
        for klasa, opis in ((SCISLY, "zero usunięć w historii → usunięcie = ALARM"),
                            (KORYGOWALNY, "korekta rzadka i uzasadniona → PYTANIE"),
                            (MUTOWALNY, "aktualizacja wpisów to sens tego ledgera → CISZA")):
            pliki = [p for p, k in KONTRAKTY.items() if k == klasa]
            print(f"\n   {klasa.upper()} — {opis}")
            for p in sorted(pliki):
                print(f"      • {p}")
        sys.exit(0)

    if args.hook:
        # CISZA GDY ZIELONE (ta sama zasada, co u VIGILA): strażnik meldujący „czysto"
        # po każdej komendzie zamieniłby się w tapetę i przestałby być czytany.
        # Awaria NIE MOŻE zatrzymać pracy — ale też nie milczy (stderr).
        try:
            w = zbadaj(tylko_kontrakty=True)
        except Exception as e:  # noqa: BLE001
            print(f"[vindex] nie zbadałem repozytorium: {type(e).__name__}: {e}",
                  file=sys.stderr)
            sys.exit(0)
        if w["status"] != "czysto":
            print(raport(w), file=sys.stderr)
        sys.exit(0)

    werdykt = zbadaj(args.commit, tylko_kontrakty=args.tylko_kontrakty)
    if args.krawedzie:
        print(json.dumps(werdykt["krawedzie"], ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(werdykt, ensure_ascii=False, indent=2))
    else:
        print(raport(werdykt))
    sys.exit(werdykt["exit"] if args.bramka else 0)
