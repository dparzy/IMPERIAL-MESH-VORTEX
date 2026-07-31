"""🪙 EXACTOR RENUNTIATIONIS — egzekwuje, czy MELDUNEK KOŃCOWY spłaca checklistę.

W Rzymie *exactor* ściągał to, co należne — nie doradzał, nie oceniał zamiaru, pytał
o dostarczenie. Ten organ robi jedno: bierze **tekst meldunku, który ma pójść do Cezara**,
i sprawdza go wobec **żywej checklisty CLAUSURY czytanej z KONSTYTUCJI**. Nie czyta kodu,
nie ocenia wachty, nie ma zdania o jakości pracy. Odpowiada na jedno pytanie:
**czy to, co za chwilę powiem Cezarowi, zawiera to, co rozkaz stały każe mu dać.**

POWÓD ISTNIENIA (nota N-b74ce133, TALAR wagi 2, zatwierdzony przez Cezara 2026-07-30):
Krok 8 CLAUSURY nakazuje podać PEŁNY blok PowerShell (`cd` + `git push origin <gałąź>`).
Dałem sam `git push`, potem `git push` z pętlą retry — i Cezar musiał pytać DWA RAZY,
zanim dostał komendę gotową do wklejenia. Rozkaz stał w CLAUDE.md kroku 8, w pamięci
prywatnej, a pieczęć CLAUSURA **wydrukowała mi go na ekran kilka minut wcześniej**.
Złamanie nie wynikało z braku wiedzy — wynikało z braku MECHANIZMU, który porównuje
meldunek z checklistą. Wiedza była; sprawdzenia nie było.

KLASA WADY: „rozkaz przeczytany, meldunek go nie realizuje". Siostra klasy runbooka W11
(dokument z własną treścią gnije) i ciszy recenzenta (RECOGNITOR). Wszystkie trzy mają tę
samą postać: **coś było prawdą na ekranie i nieprawdą w dostarczeniu.**

DLACZEGO ODDZIELNY ORGAN, A NIE WARSTWA AUDYTU (Prawo XVI):
`audyt_spojnosci.py` bada zgodność KODU z DOKUMENTAMI. Tu przedmiotem badania jest
**tekst, którego nie ma jeszcze w żadnym pliku** — mój własny meldunek przed wysłaniem.
To rozłączny przedmiot, więc rozłączny organ. Żaden inny organ Imperium nie czyta tego,
co mówię Cezarowi (zmierzone: `grep` po `imperium/` i `narzedzia/` — zero trafień).

ŻELAZNA ZASADA (ta sama, co w SIGILLARIUM): kotwice powinności **nie są kopią rozkazu** —
każda musi znaleźć swoją frazę w ŻYWEJ treści CLAUSURY z `CLAUDE.md`. Gdy rozkaz zmieni
brzmienie, powinność zgłasza się jako OSIEROCONA zamiast cicho pilnować nieboszczyka.

CO ZMIERZONE (kalibracja na PRAWDZIE PODSTAWOWEJ, 2026-07-30):
Korpus: **190 meldunków Architekta z kroniki 144 sesji**, każdy zawierający `git push`.
Podział organu: 34 „nie dotyczy" (wzmianka w prozie: zakaz pushu, `deny` w uprawnieniach,
błąd 403), 126 przekazań pushu, 30 domknięć.
  • **krok 8 — SKALIBROWANY:** na 156 przekazaniach **4 alarmy, recall 4/4** wobec ręcznie
    osądzonej prawdy (w tym oba bloki z samej noty), **0 fałszywych**.
  • **kroki 5 i 4b — ZMIERZONE, nie w pełni skalibrowane:** na pierwszym domknięciu każdej
    sesji (20 sesji) Prawo XV pominięte w **25%** meldunków, meldunek sług w **12,5%**
    (8 sesji od daty rozkazu 2026-07-21). Każda powinność sądzi wyłącznie meldunki MŁODSZE
    od swojego rozkazu — sądzenie sprzed rozkazu byłoby pomiarem poza zakresem przyrządu.
    Czego NIE WIEMY: nie ma ręcznej etykiety „tu naprawdę należało to napisać", więc te
    dwie liczby są wskazaniem, nie werdyktem. Rozstrzygnie je dopiero użycie na żywo.
Reguła fence'owa (`git push` w bloku ```) była GORSZA: dawała 2 fałszywki (JSON uprawnień,
prompt dla subagenta) i **gubiła poprawny meldunek** `6b1d4683#49`, bo parowanie ```
przesuwa się po nieparzystym fence. Dlatego regułą jest LINIA POLECENIA, nie blok.

DWA POZIOMY — WYNIK POMIARU, NIE PROJEKTU (2026-07-30):
Pierwsza wersja traktowała KAŻDE przekazanie pushu jak domknięcie wachty i krzyczała
o Prawo XV na 66% meldunków, o Dziennik na 81%. To NIE był dowód, że meldunki były złe —
rozstrzygnęła arytmetyka: 39 sesji, a „domknięć" wyszło 109. Cezar pushuje kilka razy
w wachcie, więc przekazanie pushu ≠ koniec sesji. Stąd:
  • poziom „push"       — obowiązuje przy KAŻDYM przekazaniu komendy (krok 8),
  • poziom „domkniecie" — reszta powinności, **deklarowana przez wołającego**
    (`--domkniecie`), bo fraza o domknięciu stoi tylko w 20 sesjach z 39.
Organ świadomie NIE ZGADUJE, że wachta się kończy — zgadywanie byłoby tą samą ciszą
udającą wynik, którą łapiemy gdzie indziej.

KTÓRY KROK JEST POWINNOŚCIĄ MELDUNKU (kryterium rozstrzygnięte pomiarem, nie gustem):
tylko krok, którego WŁASNE BRZMIENIE każe coś DAĆ Cezarowi („podaj", „odpowiedz",
„melduj", „nigdy milczeniem"). Kroki nakazujące WYKONAĆ pracę (bramka, Dziennik, commit)
pilnują bramka i audyt — meldunek nie jest od ich przepisywania. Bez tego kryterium organ
dawał **80% alarmów** na 20 domknięciach, karząc m.in. w 45% za nieprzepisanie bilansu
długu, którego krok 5b wcale nie każe przepisywać. Strażnik krzyczący na cztery meldunki
z pięciu uczy ignorowania siebie — to ta sama klasa, co „alarm jako tapeta".

Powinność WARUNKOWA (krok 9: alarmy hooka) świadomie NIE weszła do rejestru: obowiązuje
tylko, gdy alarm padł, a tego z samego meldunku nie da się rozstrzygnąć. Zamiast zgadywać,
organ pokazuje ten krok w polu `niepokryte` — zasięg bramki ma być JAWNY (lekcja „bramka
o wąskim zasięgu daje fałszywy spokój": NORMA K7 badała kanon i przepuściła okna).

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ Nie ocenia, czy praca wachty była dobra — sprawdza DOSTARCZENIE, nie jakość.
  • ❌ Nie czyta transkryptu sam z siebie i nie zgaduje, który tekst jest meldunkiem;
    dostaje go wprost (`--plik` / `--stdin` / hook). Zgadywanie „to już koniec sesji"
    byłoby dokładnie tym milczeniem udającym wynik, które łapiemy gdzie indziej.
  • ❌ Nie sprawdza powinności, których nie da się rozstrzygnąć z samego tekstu (np. czy
    commit naprawdę powstał) — od tego są bramka i audyt. Powinność niesprawdzalna
    deterministycznie NIE wchodzi do rejestru; wchodzi do listy NIEPOKRYTYCH, jawnie.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from imperium.biblioteki import sigillarium

KORZEN = Path(__file__).resolve().parent.parent.parent

# ── WZORCE ───────────────────────────────────────────────────────────────────────
# Uwaga: `cd` i ścieżka Windows wymagają odwrotnego ukośnika — trzymamy go w stałej,
# bo w powłokach pośredniczących literał bywa zjadany (zmierzone 2026-07-30).
_UK = chr(92)
_SCIEZKA = r"[A-Za-z]:[" + _UK + _UK + r"/]"

# PRZEKAZANIE = `git push` na POZYCJI POLECENIA: początek linii albo po separatorze
# powłoki (`;`, `&&`, `|`). Sam separator jest konieczny — bez niego wracają fałszywki
# z prozy („…commit z opisem, git push.") i z konfiguracji (`["Bash(git push:*)"]`).
_POZYCJA_POLECENIA = r"(?:^|[;&|]\s*)\s*(?:PS[^>\n]*>\s*)?"
WZ_LINIA_PUSH = re.compile(_POZYCJA_POLECENIA + r"git\s+push\b", re.M)
WZ_PUSH_ORIGIN = re.compile(_POZYCJA_POLECENIA + r"git\s+push\s+origin\s+(\S+)", re.M)
WZ_CD = re.compile(r"^\s*cd\s+[\"']?(" + _SCIEZKA + r"[^\"';&|\n]*)", re.M)
WZ_CD_INLINE = re.compile(r"cd\s+[\"']?" + _SCIEZKA + r"[^\"';&|\n]*[;&]+\s*git\s+push")

# Jawna DEKLARACJA domknięcia — w obu szykach, bo po polsku pada i „domykam wachtę",
# i „Wachta domknięta". Nigdy nie jest to JEDYNY sygnał domknięcia (patrz `tryb`).
WZ_DOMKNIECIE = re.compile(
    r"\b(?:domykam|domykamy|domkni[eę]t|zamykam|zamykamy|zamkni[eę]t)\w*\s+(?:t[ęe]\s+)?"
    r"(?:wacht|sesj)|\b(?:wacht|sesj)\w*\s+(?:domkni[eę]t|zamkni[eę]t)", re.I)


@dataclass
class Powinnosc:
    """Jedna rzecz, którą checklista każe DOSTARCZYĆ Cezarowi w meldunku.

    `poziom` rozstrzyga, KIEDY powinność obowiązuje — i jest wynikiem pomiaru, nie wygody
    (patrz DWA POZIOMY w docstringu modułu):
      • "push"       — każde przekazanie komendy push, także w środku wachty,
      • "domkniecie" — wyłącznie meldunek domykający całą wachtę.
    """

    id: str
    krok: str
    kotwica: str                      # fraza, która MUSI stać w żywej CLAUSURZE
    opis: str
    sprawdz: Callable                 # (tekst, kontekst) -> (ok, powod)
    poziom: str = "domkniecie"


# ── SPRAWDZENIA ──────────────────────────────────────────────────────────────────

def _spr_push(tekst: str, kontekst: dict):
    """Krok 8 — pełny blok PowerShell. Powinność, której złamanie zrodziło ten organ."""
    if not WZ_LINIA_PUSH.search(tekst):
        return None, "meldunek nie przekazuje żadnej komendy push"
    braki = []
    galezie = WZ_PUSH_ORIGIN.findall(tekst)
    if not galezie:
        braki.append("brak `git push origin <gałąź>` — sam `git push` polega na upstreamie, "
                     "którego Cezar nie ma jak zobaczyć")
    if not (WZ_CD.search(tekst) or WZ_CD_INLINE.search(tekst)):
        braki.append("brak `cd <ścieżka projektu>` — komenda nie jest gotowa do wklejenia")
    biezaca = kontekst.get("galaz") or ""
    if galezie and biezaca and biezaca not in galezie:
        braki.append(f"gałąź w bloku {galezie[0]!r} ≠ gałąź bieżąca {biezaca!r}")
    return (not braki), "; ".join(braki)


def _spr_fraza(fraza: str, powod: str):
    wz = re.compile(fraza, re.I)
    return lambda tekst, kontekst: (bool(wz.search(tekst)), powod)


# KRYTERIUM WEJŚCIA DO REJESTRU (rozstrzygnięte pomiarem 2026-07-30, patrz docstring):
# powinnością jest WYŁĄCZNIE krok, którego własne brzmienie nakazuje COŚ DAĆ CEZAROWI
# („podaj", „odpowiedz", „melduj", „nigdy milczeniem"). Kroki nakazujące WYKONAĆ pracę
# (uruchom bramkę, dopisz do Dziennika, zrób commit) sprawdzają bramka i audyt — nie tekst.
# Bez tego kryterium organ karał meldunki za to, czego rozkaz od nich nie żądał: na 20
# meldunkach domykających dawał 80% alarmów, w tym 45% za nieprzepisanie bilansu długu.
REJESTR: List[Powinnosc] = [
    Powinnosc(
        id="push_pelny_blok", krok="8",
        kotwica="pełny blok PowerShell",
        opis="pełny blok PowerShell (cd + git push origin <gałąź>) gotowy do wklejenia",
        sprawdz=_spr_push, poziom="push"),
    Powinnosc(
        id="prawo_xv", krok="5",
        kotwica="odpowiedz Cezarowi",
        opis="jawna odpowiedź na Prawo XV (utrata potencjału), nigdy milczeniem",
        sprawdz=_spr_fraza(r"prawo\s+XV|utrat\w*\s+potencja",
                           "meldunek nie odpowiada na Prawo XV")),
    Powinnosc(
        id="meldunek_slug", krok="4b",
        kotwica="meldunek SŁUG",
        opis="meldunek sług (HYGINUS / TIRO) z deltą wobec otwarcia",
        sprawdz=_spr_fraza(r"BREVIARIUM|HYGINUS|Hyginus|TIRO",
                           "meldunek nie podaje stanu sług (BREVIARIUM: Hyginus / TIRO)")),
]
# ŚWIADOMIE POZA REJESTREM (i przez to WIDOCZNE w `niepokryte`): krok 9 „alarmy hooka
# = ZADANIA". Powinność jest WARUNKOWA — obowiązuje tylko, gdy alarm w ogóle padł, a tego
# z samego meldunku nie da się rozstrzygnąć. Zmierzone: strażnik na słowo „alarm" krzyczał
# na 45% poprawnych domknięć, czyli uczyłby mnie ignorowania siebie. Reguła własna organu:
# powinność niesprawdzalna deterministycznie NIE wchodzi do rejestru — idzie na widok.

# Czasowniki, którymi checklista nakazuje COŚ DAĆ Cezarowi. Krok zawierający taki
# czasownik, a nieobjęty żadną powinnością, jest raportowany jako NIEPOKRYTY —
# lepiej znać zasięg bramki, niż mieć fałszywy spokój (lekcja „bramka o wąskim zasięgu").
WZ_POWINNOSC_W_KROKU = re.compile(
    r"\bpodaj\b|\bmelduj\w*\b|\bmeldunek\b|\bodpowiedz\b|\bpoka[żz]\b|\bzaraportuj\b"
    r"|\brozstrzygnij\b|\bzapytaj\b|nigdy milczeniem", re.I)


# ── RDZEŃ — czysty, bez wejścia/wyjścia, w pełni testowalny ──────────────────────

WZ_FENCE = re.compile(r"```.*?```", re.S)
WZ_CYTAT_INLINE = re.compile(r"`[^`\n]+`")


def bez_cytatow_inline(tekst: str) -> str:
    """Usuwa CYTATY w pojedynczych grawisach, zostawiając bloki ``` nietknięte.

    Powód zmierzony (2026-07-30, dwie fałszywki `ea3446fd#64` i `#118`): proza cytująca
    `cd x && git push` jako PRZYKŁAD stawia `git push` na pozycji polecenia i wyglądała
    jak przekazanie komendy. Meldunek przekazuje komendę BLOKIEM, nie w środku zdania —
    więc cytat inline nie jest przekazaniem, a blok ``` pozostaje.
    """
    czesci, koniec = [], 0
    for m in WZ_FENCE.finditer(tekst):
        czesci.append(WZ_CYTAT_INLINE.sub(" ", tekst[koniec:m.start()]))
        czesci.append(m.group(0))
        koniec = m.end()
    czesci.append(WZ_CYTAT_INLINE.sub(" ", tekst[koniec:]))
    return "".join(czesci)

def zbadaj_meldunek(tekst: str, *, kroki: List[str], galaz: str = "",
                    tryb: str = "auto") -> dict:
    """Werdykt o meldunku wobec ŻYWEJ checklisty CLAUSURY.

    `kroki` to lista kroków przeczytana z KONSTYTUCJI (nie kopia!). `galaz` pozwala
    złapać blok wskazujący cudzą gałąź. `tryb="domkniecie"` deklaruje wprost, że to
    meldunek zamykający wachtę — organ tego NIE ZGADUJE (zmierzone: fraza o domknięciu
    stoi tylko w 4 z 39 sesji, więc detekcja z samego tekstu przegapiłaby resztę).

    Zwraca `status`/`ikona`/`exit` — kod wyjścia jest częścią kontraktu bramki:
    0 wolno wyłącznie, gdy meldunek naprawdę spłaca listę na swoim poziomie.
    """
    tresc_krokow = "\n".join(kroki)
    kontekst = {"galaz": galaz}
    tekst = bez_cytatow_inline(tekst)

    ma_push = bool(WZ_LINIA_PUSH.search(tekst))
    # `tylko_push` ODCINA poziom domknięcia nawet wtedy, gdy tekst sam deklaruje domknięcie —
    # używa go hook, któremu wolno sięgać wyłącznie po powinność SKALIBROWANĄ (krok 8).
    if tryb == "tylko_push":
        poziom = "push" if ma_push else "brak"
    else:
        domkniecie = tryb == "domkniecie" or bool(WZ_DOMKNIECIE.search(tekst))
        poziom = "domkniecie" if domkniecie else ("push" if ma_push else "brak")

    braki, spelnione, osierocone, nieaktywne = [], [], [], []
    for p in REJESTR:
        if p.kotwica.lower() not in tresc_krokow.lower():
            osierocone.append(p)
            continue
        # Powinność „domknięciowa" NIE obowiązuje przy zwykłym przekazaniu pushu w środku
        # wachty — inaczej organ krzyczałby na 105 poprawnych meldunków (zmierzone).
        if p.poziom == "domkniecie" and poziom != "domkniecie":
            nieaktywne.append(p)
            continue
        if p.poziom == "push" and poziom == "brak":
            nieaktywne.append(p)
            continue
        ok, powod = p.sprawdz(tekst, kontekst)
        if ok is None:                       # powinność nie dotyczy tego meldunku
            nieaktywne.append(p)
        elif ok:
            spelnione.append(p)
        else:
            braki.append((p, powod))

    kroki_z_powinnoscia = [k for k in kroki if WZ_POWINNOSC_W_KROKU.search(k)]
    pokryte_kroki = {p.krok for p in REJESTR}
    niepokryte = [k for k in kroki_z_powinnoscia
                  if not any(k.lstrip().startswith(f"{nr}.") or k.lstrip().startswith(f"{nr}b.")
                             for nr in pokryte_kroki)]

    baza = {"poziom": poziom, "osierocone": [], "niepokryte": niepokryte}

    if osierocone:
        return {
            **baza, "status": "kotwica_osierocona", "ikona": "🚨", "exit": 2,
            "braki": [], "spelnione": [p.id for p in spelnione],
            "osierocone": [p.id for p in osierocone],
            "opis": "KOTWICA OSIEROCONA — powinność " +
                    ", ".join(f"`{p.id}` (fraza {p.kotwica!r})" for p in osierocone) +
                    " nie znajduje już swojej frazy w CLAUDE.md § KONIEC SESJI. "
                    "Rozkaz zmienił brzmienie albo zniknął: napraw ŹRÓDŁO, zanim zaufasz werdyktowi.",
        }
    if poziom == "brak":
        return {
            **baza, "status": "nie_dotyczy", "ikona": "ℹ️", "exit": 0,
            "braki": [], "spelnione": [],
            "opis": "Meldunek nie przekazuje pushu i nie deklaruje domknięcia wachty — "
                    "checklista CLAUSURY go nie dotyczy.",
        }
    if braki:
        return {
            **baza, "status": "niespelniony", "ikona": "🚨", "exit": 1,
            "braki": [{"id": p.id, "krok": p.krok, "opis": p.opis, "powod": powod}
                      for p, powod in braki],
            "spelnione": [p.id for p in spelnione],
            "opis": f"MELDUNEK NIE SPŁACA CHECKLISTY (poziom: {poziom}) — "
                    f"{len(braki)} powinność(-ci) z kroków "
                    f"{', '.join(sorted({p.krok for p, _ in braki}))} niedostarczona.",
        }
    return {
        **baza, "status": "spelniony", "ikona": "✅", "exit": 0,
        "braki": [], "spelnione": [p.id for p in spelnione],
        "opis": f"Meldunek spłaca checklistę CLAUSURY na poziomie {poziom!r} "
                f"({len(spelnione)} powinność(-ci) sprawdzona(-e)).",
    }


# ── UODPORNIENIE — organ SAM podaje blok, którego wymaga ─────────────────────────

def blok_push(galaz: str = "", korzen: Path = None) -> str:
    """Gotowy blok PowerShell kroku 8 — policzony z ŻYWEGO repozytorium.

    Sedno uodpornienia: skoro pamięć zawiodła przy przepisywaniu dwóch linii, nie ma
    powodu, żeby te dwie linie w ogóle przepisywać z pamięci.
    """
    korzen = korzen or KORZEN
    galaz = galaz or galaz_biezaca()
    return f"cd {korzen}; git push origin {galaz}"


# ── ADAPTERY ─────────────────────────────────────────────────────────────────────

def galaz_biezaca() -> str:
    try:
        p = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=KORZEN,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=15)
    except (OSError, subprocess.SubprocessError):
        return ""
    return p.stdout.strip() if p.returncode == 0 else ""


def kroki_clausury() -> List[str]:
    """Kroki z KONSTYTUCJI — nigdy z własnej kopii (żelazna zasada SIGILLARIUM)."""
    return sigillarium.kroki("clausura")


def zbadaj(tekst: str, tryb: str = "auto") -> dict:
    return zbadaj_meldunek(tekst, kroki=kroki_clausury(), galaz=galaz_biezaca(), tryb=tryb)


# ── HOOK `Stop` — sprawdzenie BEZ UDZIAŁU MOJEJ PAMIĘCI ─────────────────────────
#
# Sonda pomiarowa (2026-07-31) rozstrzygnęła to, czego nie wolno było zakładać:
# zdarzenie `Stop` niesie GOTOWE pole `last_assistant_message` z pełnym tekstem
# meldunku (a także `transcript_path` i `stop_hook_active`). Dopiero ten pomiar
# uprawnił do zbudowania strażnika — kolejność odwrotna byłaby powtórzeniem błędu,
# za który powstał cały ten organ.
#
# ZASIĘG ŚWIADOMIE WĄSKI: hook bada WYŁĄCZNIE krok 8 (`tryb="tylko_push"`), bo tylko
# ten ma zmierzone ZERO fałszywych alarmów na 156 przekazaniach. Poziom „domkniecie"
# nie jest skalibrowany — w automacie, który odpala się po KAŻDEJ turze, zamieniłby
# się w tapetę, a tapeta uczy ignorowania strażnika (lekcja: „alarm to zadanie, nie tło").

def ocen_zdarzenie_hooka(zdarzenie: dict, *, kroki: List[str], galaz: str = "") -> dict:
    """Werdykt hooka `Stop`. Czysty — zdarzenie jest DANYMI, nie źródłem.

    Milczy zawsze, gdy nie ma pewności: brak meldunku, powtórne wejście
    (`stop_hook_active`), albo meldunek nieprzekazujący pushu. Blokuje wyłącznie
    wtedy, gdy KROK 8 jest naprawdę niespełniony — i wtedy od razu podaje gotowy blok,
    żeby naprawa nie zależała od tej samej pamięci, która zawiodła.
    """
    if zdarzenie.get("stop_hook_active"):
        # Powtórne wejście: gdybyśmy blokowali znowu, powstałaby pętla. Bezpiecznik
        # protokołu jest ważniejszy niż jeszcze jedno przypomnienie.
        return {"blokuj": False, "powod": "", "status": "powtorne_wejscie"}

    tekst = (zdarzenie.get("last_assistant_message") or "").strip()
    if not tekst:
        return {"blokuj": False, "powod": "", "status": "brak_meldunku"}

    w = zbadaj_meldunek(tekst, kroki=kroki, galaz=galaz, tryb="tylko_push")
    if w["status"] != "niespelniony":
        return {"blokuj": False, "powod": "", "status": w["status"], "werdykt": w}

    braki = "; ".join(b["powod"] for b in w["braki"])
    return {
        "blokuj": True, "status": "niespelniony", "werdykt": w,
        "powod": (
            "EXACTOR (krok 8 CLAUSURY): przekazujesz Cezarowi komendę push, ale blok nie jest "
            f"gotowy do wklejenia — {braki}. Rozkaz stały każe podać PEŁNY blok PowerShell. "
            f"Popraw meldunek, wklejając dokładnie to:\n\n    {blok_push(galaz=galaz)}\n\n"
            "Nie przepisuj go z pamięci — to ona zawiodła przy nocie N-b74ce133."
        ),
    }


def hook_stop(zdarzenie: dict) -> dict:
    return ocen_zdarzenie_hooka(zdarzenie, kroki=kroki_clausury(), galaz=galaz_biezaca())


# ── WYDRUK ───────────────────────────────────────────────────────────────────────

def banner(w: dict) -> str:
    return f"{w['ikona']} EXACTOR (meldunek vs CLAUSURA): {w['opis']}"


def raport(w: dict) -> str:
    linie = [banner(w)]
    for b in w.get("braki", []):
        linie.append(f"   ❌ krok {b['krok']} — {b['opis']}")
        linie.append(f"      powód: {b['powod']}")
    if w.get("braki") and any(b["id"] == "push_pelny_blok" for b in w["braki"]):
        linie.append(f"      gotowy blok: {blok_push()}")
    if w.get("niepokryte"):
        linie.append(f"   ℹ️ zasięg: {len(w['niepokryte'])} krok(ów) z powinnością wobec "
                     "Cezara NIE jest sprawdzanych deterministycznie:")
        for k in w["niepokryte"]:
            linie.append(f"      • {k.strip()[:110]}")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(
        description="EXACTOR — czy meldunek końcowy spłaca checklistę CLAUSURY")
    ap.add_argument("tryb", nargs="?", default="raport", choices=["banner", "raport", "json"])
    ap.add_argument("--plik", help="plik z tekstem meldunku")
    ap.add_argument("--stdin", action="store_true", help="czytaj meldunek ze stdin")
    ap.add_argument("--blok-push", action="store_true",
                    help="wypisz gotowy blok kroku 8 i zakończ")
    ap.add_argument("--hook", action="store_true",
                    help="tryb hooka Stop: czytaj zdarzenie z stdin, badaj WYŁĄCZNIE krok 8")
    ap.add_argument("--domkniecie", action="store_true",
                    help="to jest meldunek ZAMYKAJĄCY wachtę — sprawdź pełną checklistę "
                         "(organ tego nie zgaduje)")
    ap.add_argument("--bramka", action="store_true",
                    help="kod wyjścia wg werdyktu (0 spełniony / 1 brak / 2 kotwica osierocona)")
    args = ap.parse_args()

    if args.blok_push:
        print(blok_push())
        sys.exit(0)

    if args.hook:
        # Awaria strażnika NIE MOŻE zatrzymać pracy — ale też nie milczy (stderr).
        try:
            wynik = hook_stop(json.load(sys.stdin))
        except Exception as e:  # noqa: BLE001
            print(f"[exactor] nie odczytałem zdarzenia hooka: {type(e).__name__}: {e}",
                  file=sys.stderr)
            sys.exit(0)
        if wynik["blokuj"]:
            # ensure_ascii=True z rozmysłu: na Windowsie strumień bywa cp1250, w której
            # polskie znaki nie istnieją — strażnik nie ma prawa paść przez KOSMETYKĘ
            # (ta sama decyzja co w CUSTOS LIMINIS).
            print(json.dumps({"decision": "block", "reason": wynik["powod"]}))
        sys.exit(0)

    if args.plik:
        tekst = Path(args.plik).read_text(encoding="utf-8", errors="replace")
    elif args.stdin:
        tekst = sys.stdin.read()
    else:
        ap.error("podaj --plik albo --stdin (organ nie zgaduje, co jest meldunkiem)")

    werdykt = zbadaj(tekst, tryb="domkniecie" if args.domkniecie else "auto")
    print(json.dumps(werdykt, ensure_ascii=False, indent=2) if args.tryb == "json"
          else banner(werdykt) if args.tryb == "banner" else raport(werdykt))
    sys.exit(werdykt["exit"] if args.bramka else 0)
