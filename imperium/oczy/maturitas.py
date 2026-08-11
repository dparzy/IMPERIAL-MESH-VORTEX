"""📐 MATURITAS — na którym PIĘTRZE inżynierii stoi Imperium i czy pętle się domykają.

Rzymska *maturitas* to dojrzałość: nie wiek i nie rozmiar, lecz **stopień, do jakiego coś
doszło**. Ten organ odpowiada na trzy pytania Cezara, każde LICZBĄ Z KODU, nie z prozy:
  1. **PROMPT** — czy specyfikacja, którą pracuję, jest zdrowa (czy nie gnije i nie puchnie)?
  2. **LOOP**   — czy pętle się DOMYKAJĄ, czy tylko otwierają?
  3. **GRAPH**  — czy graf istnieje, czy graf DZIAŁA, i czy wpływa na DECYZJĘ?

POWÓD ISTNIENIA (rozkaz Cezara 2026-08-02: „pilnujmy i weryfikujmy stany prompt/loop/graph,
poziom rozwinięcia, pomiar działania i domknięcia — na otwarciu i zamknięciu"):
Doktryna „domykaj loop, otwieraj drogę na graph" była KRYTERIUM bez MIERNIKA. Wpisanie do
checklisty samego polecenia „zweryfikuj stan" dałoby zasadę bez mechanizmu — dokładnie tę
klasę, którą tego samego dnia złapaliśmy przy kontrakcie append-only (deklarowany w sześciu
organach, egzekwowany przez zero). Krok w checkliście ma WOŁAĆ POMIAR, nie prosić o refleksję.

DLACZEGO TO JEST INGENIUM, A NIE NOWY BYT (Prawo XVI):
`docs/INGENIUM_IQ_IMPERII.md` projektuje CENZORA ROZUMU — 7 kategorii liczonych z kodu.
Projekt istnieje od 2026-07-29 i **nie ma ani linii kodu**. Ten organ jest jego pierwszą
ŻYWĄ kategorią (ósmą w rejestrze: MATURITAS), zbudowaną wg zasad nienaruszalnych stamtąd:
  • każda składowa z KODU albo LEDGERA — zero liczb wpisanych ręcznie,
  • **`NIEZNANE` to wynik** — kategoria bez pomiaru nie dostaje punktów „z rozsądku",
  • **lustro, nie kierownica** — wynik NIGDY nie steruje decyzją handlową ani doborem wag,
  • **antywskaźnik obowiązkowy** — przy każdym piętrze zapisane, JAK można je oszukać,
  • **wynik ma być spadalny** — miernik, który nigdy nie spada, nie mierzy, tylko chwali.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ Nie liczy jednej „oceny Imperium" — trzy piętra mierzą rozłączne rzeczy i uśrednienie
    ukryłoby to, co najważniejsze (można mieć doskonały LOOP przy zerowym GRAPH).
  • ❌ Nie ocenia wyniku TRADINGOWEGO. Ścieżka decyzyjna handlowa nie zawiera LLM-a, więc
    piętro inżynierii poprawia pamięć i pracę Architekta — mylenie tego z zyskiem byłoby
    tym samym rozkalibrowaniem, które złapaliśmy przy frazach zwiadu.
  • ❌ Nie zgaduje tam, gdzie nie ma danych — brak pomiaru wychodzi jako `NIEZNANE`.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

KORZEN = Path(__file__).resolve().parent.parent.parent
DANE = KORZEN / "bibliotheca_ulpia" / "dane"

NIEZNANE = "NIEZNANE"
POZIOMY = {0: "ZALĄŻEK", 1: "POCZĄTEK", 2: "DZIAŁA", 3: "DOJRZAŁE", 4: "WPIĘTE W DECYZJĘ"}


def _git(*args: str) -> str:
    try:
        p = subprocess.run(["git", *args], cwd=KORZEN, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return ""
    return p.stdout if p.returncode == 0 else ""


def _jsonl(nazwa: str) -> List[dict]:
    plik = DANE / nazwa
    if not plik.exists():
        return []
    out = []
    for linia in plik.open(encoding="utf-8", errors="replace"):
        linia = linia.strip()
        if linia:
            try:
                out.append(json.loads(linia))
            except json.JSONDecodeError:
                continue          # uszkodzony wiersz to nie powód, żeby oślepnąć
    return out


def _poziom(warunki: List[bool]) -> int:
    """Poziom = ile kolejnych progów spełniono OD DOŁU.

    Kolejność jest istotą: piętro nie „przeskakuje" progu. Graf z tysiącem węzłów, którego
    nikt nie czyta przy decyzji, NIE jest dojrzalszy od małego grafu, który decyduje.
    """
    poziom = 0
    for w in warunki:
        if not w:
            break
        poziom += 1
    return poziom


def wiersze_stanu(tekst: str) -> List[tuple]:
    """Wiersze tabel ROADMAP jako `[(etykieta, stan)]` — JEDEN parser na całe Imperium.

    Publiczne, bo pyta o to więcej niż jeden organ: MATURITAS liczy, JAKA CZĘŚĆ pozycji jest
    domknięta, a CONDITOR LUSTRI pyta o KONKRETNE wiersze etapów LUSTRATIO. To jedno źródło
    i dwa pytania — nie dwa parsery. Powód zapisany w Księdze Wad (2026-07-17): „jeden format
    = jeden parser; dwa parsery rozjadą się co do znaku", a rozjazd byłby tu niewidoczny,
    bo obie strony dawałyby liczbę wyglądającą sensownie.
    """
    out: List[tuple] = []
    for w in tekst.splitlines():
        if not w.startswith("|") or w.count("|") < 4:
            continue
        kol = [c.strip() for c in w.split("|")]
        if len(kol) < 4 or not kol[1] or kol[1].startswith("-") or kol[1] == "#":
            continue
        out.append((kol[1], kol[3]))
    return out


def stan_domkniety(stan: str) -> Optional[bool]:
    """True = domknięte, False = otwarte, **None = nie wiem** (klasa K2: milczenie ≠ zieleń).

    PUBLICZNE tak samo jak `wiersze_stanu` i z tego samego powodu: czyta to więcej niż jeden
    organ (MATURITAS liczy udział domkniętych, CONDITOR LUSTRI pyta o etapy LUSTRATIO).
    Do 2026-08-05 nazywało się `_stan_domkniety` i CONDITOR importował je mimo podkreślnika —
    zmiana nazwy w tym module zamieniłaby jego kryterium ETAPY w ciche `NIE WIEM` (bo awarię
    producenta łapie tam `except`). Kontrakt między organami musi być nazwany kontraktem.
    """
    if "✅" in stan:
        return True
    if any(z in stan for z in ("🔴", "🟡", "⏸️")):
        return False
    return None


# Alias zgodności — istniejące wołania sprzed 2026-08-05. Nowy kod używa nazwy publicznej.
_stan_domkniety = stan_domkniety


# ── MAPA ORGANÓW I PIĘTER (rozkaz Cezara 2026-08-06) ────────────────────────────
# „chciałbym, żeby pokazywał (…) bardziej szczegółowo, jakie organy są wiązane w danym
# rodzaju etapu, gdzie jest brakująca opcja dopełnienia i czy mamy już opcję jej
# dopełnienia w ROADMAP" — trzy pytania, na które sam poziom 0–4 nie odpowiada.
#
# ŚCIEŻKI SĄ WERYFIKOWANE, NIE DEKLAROWANE: `organy_pietra()` odsiewa te, których nie ma
# na dysku, i zwraca je osobno jako WIDMA. Lista organów wpisana ręcznie i nigdy
# niesprawdzana byłaby tą samą klasą co API-widma z Warstwy 16 — a w organie, który ma
# mierzyć dojrzałość, brzmiałoby to szczególnie fałszywie.

ORGANY_PIETRA: Dict[str, List[str]] = {
    "PROMPT": ["CLAUDE.md", "imperium/biblioteki/sigillarium.py",
               "imperium/cesarz/aerarium.py", ".claude/skills"],
    "LOOP": ["docs/ROADMAP_IMPERIUM.md", "narzedzia/codex_probationum.py",
             "imperium/biblioteki/codex_notarum.py", "imperium/biblioteki/rejestr_wizji.py"],
    "GRAPH": ["imperium/biblioteki/graf_pamieci.py", "imperium/biblioteki/kustosz_pamieci.py",
              "imperium/biblioteki/pamiec_proweniencji.py"],
    "HARNESS": [".claude/settings.json", ".claude/hooks", ".github/workflows/ci.yml",
                "imperium/pretorianie/silentium.py", "imperium/pretorianie/custos_liminis.py",
                "imperium/pretorianie/vigil.py", "imperium/pretorianie/exactor.py"],
    "NEURO-SYM": ["narzedzia/audyt_spojnosci.py", "narzedzia/skan_wad_kodu.py",
                  "imperium/pretorianie/vindex.py", "imperium/pretorianie/recognitor.py",
                  "bibliotheca_ulpia/dane/index_falsorum.jsonl"],
}

# ── ZASIĘG MIERNIKA — SKORYGOWANY ZWIADEM 2026-08-06 ────────────────────────────
# ⚠️ LICZBA „9 PIĘTER" NIE MA POKRYCIA W ŹRÓDŁACH. Do 2026-08-06 ROADMAP notował przy
# CORONIE D, że MATURITAS mierzy „3 z 9" — dziewiątka pochodziła z materiału zewnętrznego
# wygenerowanego przez model językowy. FRUMENTARIUS (zwiad na rozkaz Cezara) ustalił:
#
#  1. Patent `US20230000000A1`, cytowany w TYM SAMYM materiale, **NIE ISTNIEJE** — Google
#     Patents zwraca 404, a numeracja publikacji USA startuje od `0000001`, więc numer
#     z samych zer jest strukturalnie niemożliwy. Klasyczny placeholder halucynacji.
#  2. **Żadne znalezione źródło nie podaje DZIEWIĘCIU etapów inżynierii agentowej.** Jedyna
#     znaleziona „dziewiątka" to filozoficzna oś Twemlowa (ANI→AGI→ASI→…) — INNA OŚ niż
#     warstwy inżynierii. Nasza dziewiątka to prawdopodobnie sklejka dwóch taksonomii,
#     czyli dokładnie ta klasa błędu, którą ten organ ma wykrywać.
#
# CO ISTNIEJE NAPRAWDĘ (najbliższe nam, potwierdzone): pięciowarstwowy model
# **Prompt → Context → Harness → Loop → Graph** (Rastogi; pokrewnie arXiv 2606.28270).
# `context engineering` (arXiv 2507.13334) i `harness engineering` (arXiv 2604.25850) to
# terminy ustalone lub ustalające się; `loop`/`graph engineering` dopiero się rodzą.
# Mierzymy CZTERY z tych pięciu (brak CONTEXT) plus NEURO-SYM, które jest nasze własne —
# termin naukowy starszy niż era LLM, w tamtej rodzinie nieobecny.
TAKSONOMIA_ZRODLO = ("Prompt/Context/Harness/Loop/Graph (Rastogi; arXiv 2606.28270) — "
                     "zweryfikowane zwiadem 2026-08-06; liczba 9 OBALONA")
PIETER_ZNANYCH = 6          # 5 warstw potwierdzonej taksonomii + NEURO-SYM (nasze własne)

# Próg rzadkości słowa w ROADMAP: powyżej niego słowo jest TŁEM dokumentu, nie nazwą rzeczy.
# Wartość 5 dobrana POMIAREM na żywym ROADMAP (2026-08-06): „decyzji" 20×, „roadmap" 13×,
# „kontekstu" 10×, „czytany" 7× — wszystkie odpadają jako tło; nazwy pozycji i organów
# występują 1–4 razy i przechodzą. Każdy próg ma mieć test granicy (Prawo XXI).
#
# ⚠️ TE LICZBY BYŁY NAJPIERW WPISANE Z GŁOWY (27×/58×/12×) i pomiar je obalił w tej samej
# minucie. Zapisuję to tutaj, bo to TRZECIE wystąpienie tej klasy jednego dnia (docstring
# RECOGNITORA, errata w Dzienniku, ten komentarz): liczba w prozie obok kodu, której nikt
# nie policzył. Warstwa 23 audytu łapie to w dokumentach .md, ale NIE w komentarzach .py.
PROG_RZADKOSCI = 5
PIETRA_NIEMIERZONE = [
    "CONTEXT — inżynieria kontekstu jako OSOBNE piętro (arXiv 2507.13334). Dziś mierzona "
    "częściowo wewnątrz PROMPT przez AERARIUM, ale bez własnego poziomu 0–4",
]

# Kandydaci SPOZA potwierdzonej taksonomii, wskazani przez zwiad jako osobne dojrzałe
# dziedziny. NIE są piętrami, dopóki Cezar nie osądzi, czy należą do TEJ osi —
# rozstrzygnięcie z CORONY D: wzorzec wchodzi do rejestru po ZATWIERDZENIU, nigdy
# z lektury materiału. Trzymamy ich tutaj jawnie, żeby nie zginęli i nie awansowali sami.
KANDYDACI_NA_PIETRA = [
    "OBSERVABILITY — obserwowalność agentów (osobna dziedzina narzędziowa 2026)",
    "GUARDRAILS — bramki bezpieczeństwa, sandboxing, policy checks",
    "INTENT — inżynieria intencji (piąta warstwa w arXiv 2606.28270)",
    "MEMORY — pamięć długoterminowa jako osobny nurt (arXiv 2512.13564)",
    "COORDINATION — orkiestracja wieloagentowa, odrębna od GRAPH (arXiv 2605.10052)",
    "AUTONOMIA L0–L5 — INNA OŚ (wzorzec SAE J3016), nie warstwa inżynierii (arXiv 2506.12469)",
]


def _warstwy_audytu() -> int:
    """Ile warstw audyt REALNIE egzekwuje — po znacznikach `[W..]`, nie po nazwach funkcji.

    Jedno źródło prawdy dla LOOP, HARNESS i NEURO-SYM: trzy piętra pytają o tę samą
    liczbę, a trzy własne parsery rozjechałyby się przy pierwszej zmianie formatu.
    """
    audyt = KORZEN / "narzedzia" / "audyt_spojnosci.py"
    if not audyt.exists():
        return 0
    return len(set(re.findall(r"\[W\d+[a-z]?\]",
                              audyt.read_text(encoding="utf-8", errors="replace"))))


def organy_pietra(pietro: str) -> Dict[str, List[str]]:
    """Organy wiązane z piętrem, rozdzielone na ŻYWE i WIDMA (ścieżka nie istnieje)."""
    zywe, widma = [], []
    for sciezka in ORGANY_PIETRA.get(pietro, []):
        (zywe if (KORZEN / sciezka).exists() else widma).append(sciezka)
    return {"zywe": zywe, "widma": widma}


def luka_w_planie(wask: str) -> str:
    """Czy wąskie gardło ma już POZYCJĘ W PLANIE — odpowiedź na trzecie pytanie Cezara.

    Szuka w ROADMAP wyłącznie słów RZADKICH — i to jest istota tej funkcji, nie detal.

    ⚠️ PIERWSZA WERSJA BYŁA MIARĄ ZBYT ŁAGODNĄ (naprawione tego samego dnia, 2026-08-06).
    Liczyła każde słowo dłuższe niż 5 znaków, więc „decyzji", „roadmap" i „domknięty"
    dawały trafienie ZAWSZE — ROADMAP jest o decyzjach i domykaniu. Wszystkie trzy wąskie
    gardła dostały ✅ „mamy to w planie", choć funkcja nie sprawdziła NICZEGO. To ta sama
    klasa, którą tego dnia złapaliśmy dwa razy w RECOGNITORZE: miara łagodna wobec własnego
    procesu, chwaląca zamiast mierzyć.

    Naprawa: słowo liczy się tylko wtedy, gdy w ROADMAP występuje RZADKO (< `PROG_RZADKOSCI`
    razy) — czyli jest nazwą rzeczy, nie tłem dokumentu. Werdykt świadomie nazwany
    WSKAZÓWKĄ, nie dowodem: dopasowanie po słowach nie umie odróżnić pozycji planu od
    zdania w prozie, a miernik ma mówić, ile wie, nie więcej.
    """
    plan = KORZEN / "docs" / "ROADMAP_IMPERIUM.md"
    if not wask or not plan.exists():
        return ""
    tresc = plan.read_text(encoding="utf-8", errors="replace").lower()
    slowa = {s.strip(".,:;()„”\"'—") for s in wask.lower().split() if len(s) > 5}
    rzadkie = {s: tresc.count(s) for s in slowa if 0 < tresc.count(s) < PROG_RZADKOSCI}
    if len(rzadkie) >= 2:
        naj = sorted(rzadkie, key=rzadkie.get)[:3]
        return ("🔎 WSKAZÓWKA: możliwa pozycja w ROADMAP (rzadkie słowa: "
                + ", ".join(f"{s}×{rzadkie[s]}" for s in naj) + ") — zweryfikuj ręcznie")
    return "🔴 BRAK POZYCJI W ROADMAP — luka bez planu dopełnienia"


# ── PIĘTRO 1: PROMPT — zdrowie specyfikacji ─────────────────────────────────────

def zmierz_prompt() -> Dict[str, Any]:
    """Czy specyfikacja, wg której pracuję, jest zdrowa: zwięzła, żywa i osiągalna."""
    konstytucja = (KORZEN / "CLAUDE.md")
    linie = len(konstytucja.read_text(encoding="utf-8", errors="replace").splitlines()) \
        if konstytucja.exists() else 0
    skille = sorted((KORZEN / ".claude" / "skills").glob("*/SKILL.md")) \
        if (KORZEN / ".claude" / "skills").exists() else []
    # Sigla MUSZĄ czytać kroki z konstytucji, nie mieć własnej kopii (żelazna zasada).
    try:
        from imperium.biblioteki import sigillarium
        sigla = {n: len(sigillarium.kroki(n)) for n in ("apertio", "clausura", "limes")}
    except Exception:  # noqa: BLE001
        sigla = {}
    puste = [n for n, ile in sigla.items() if ile == 0]

    wskazniki = {
        "CLAUDE.md_linii": linie,
        "limit_doktrynalny": 200,
        "skille_na_zadanie": len(skille),
        "sigla_kroki": sigla,
        "sigla_puste": puste,
    }
    poziom = _poziom([
        linie > 0,                       # 1 — specyfikacja w ogóle istnieje
        bool(sigla) and not puste,       # 2 — procedury są wyzwalane, nie przepisywane
        len(skille) >= 5,                # 3 — rozkazy ładowane na żądanie, nie na starcie
        linie <= 200,                    # 4 — i nie puchnie ponad limit
    ])
    return {
        "pietro": "PROMPT", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": (f"CLAUDE.md {linie} linii > 200 — dług kontekstu płacony w KAŻDEJ sesji"
                 if linie > 200 else "" ) or ("puste pieczęcie: " + ", ".join(puste) if puste else ""),
        "antywskaznik": "poziom rośnie od PRZENOSZENIA treści do skilli — a przeniesienie "
                        "rozkazu, którego nikt potem nie woła, POGARSZA stan, choć liczbę poprawia",
    }


# ── PIĘTRO 2: LOOP — czy pętle się domykają ─────────────────────────────────────

def zmierz_loop() -> Dict[str, Any]:
    """Nie „ile mamy pętli", tylko **jaka ich część jest DOMKNIĘTA**."""
    # ROADMAP: pozycje otwarte vs domknięte (stan czytany z tabel, nie z pamięci)
    rm = (KORZEN / "docs" / "ROADMAP_IMPERIUM.md")
    tekst = rm.read_text(encoding="utf-8", errors="replace") if rm.exists() else ""
    otw = dom = 0
    for _etykieta, stan in wiersze_stanu(tekst):
        czy = _stan_domkniety(stan)
        if czy is True:
            dom += 1
        elif czy is False:
            otw += 1

    # SUGESTIE: rekord zamknięcia jest OSOBNYM wpisem (ledger append-only), więc liczymy
    # po ostatnim statusie per element — inaczej wyjdzie fałszywy alarm. Zmierzone 2026-08-02:
    # filtr po nazwie statusu `ZAMKNIETA` zamiast `ZAMKNIETE` dał „zero zamkniętych".
    sug: Dict[str, str] = {}
    for r in _jsonl("rejestr_testow.jsonl"):
        if r.get("typ") == "SUGESTIA" and r.get("element"):
            sug[r["element"]] = str(r.get("status", "")).upper()
    zamkniete = sum(1 for s in sug.values()
                    if s.startswith(("ZAMKNIET", "ZREALIZOWAN", "ZABLOKOWAN")))
    otwarte_sug = len(sug) - zamkniete

    wizje = _jsonl("wizje_i_decyzje.jsonl")
    bez_werdyktu = sum(1 for w in wizje if w.get("status") in ("POMYSŁ", "PLANOWANE"))

    # KLASA K1 (naprawiona 2026-08-05): dług liczyliśmy TUTAJ jako `NOTA − CORONA`, czyli
    # drugą arytmetyką obok CODEX NOTARUM. Dwa błędy naraz: (1) odejmowanie LICZNIKÓW nie wie,
    # KTÓRA korona spłaca KTÓRĄ notę (5 koron i 3 niespłacone noty dają fałszywe zero),
    # (2) nie wie o ODROCZENIU wprowadzonym 2026-08-03. Dziś obie drogi dają 0, więc rozjazd
    # był NIEWIDOCZNY — i dokładnie tak wygląda K1, zanim zacznie kłamać. Fakt ma jednego
    # producenta; my go WOŁAMY.
    from imperium.biblioteki import codex_notarum
    dlug_honorowy = len(codex_notarum.dlug_honorowy())
    odroczonych = len(codex_notarum.odroczone())

    hooki = sorted((KORZEN / ".claude" / "hooks").glob("*.sh")) \
        if (KORZEN / ".claude" / "hooks").exists() else []
    # Warstwy liczy `_warstwy_audytu()` — po ZNACZNIKACH `[W..]`, nie po nazwach funkcji
    # (zmierzone: `def _warstwa_\d+` daje 15 przy realnych 24, bo część warstw żyje
    # w helperach). Wspólna funkcja, bo o tę samą liczbę pytają też HARNESS i NEURO-SYM.
    warstwy = _warstwy_audytu()

    razem = otw + dom
    domkniecie = round(100 * dom / razem, 1) if razem else None
    wskazniki = {
        "roadmap_domkniete": dom, "roadmap_otwarte": otw,
        "roadmap_domkniecie_proc": domkniecie if domkniecie is not None else NIEZNANE,
        "sugestie_zamkniete": zamkniete, "sugestie_otwarte": otwarte_sug,
        "wizje_bez_werdyktu": bez_werdyktu,
        "hooki": len(hooki), "warstwy_audytu": warstwy,
        "dlug_honorowy": dlug_honorowy,
        # Odroczenie zdejmuje BLOKADĘ, nie dług — więc musi być widoczne obok niego,
        # inaczej stałoby się cichym umorzeniem (klasa K4: wyciszenie bez powodu na widoku).
        "noty_odroczone": odroczonych,
    }
    poziom = _poziom([
        len(hooki) >= 1,                              # 1 — cokolwiek się samo sprawdza
        warstwy >= 10,                                # 2 — bramka ma realny zasięg
        dlug_honorowy == 0,                           # 3 — błędy są spłacane, nie kumulowane
        domkniecie is not None and domkniecie >= 50,  # 4 — DOMYKAMY więcej, niż otwieramy
    ])
    return {
        "pietro": "LOOP", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": (f"ROADMAP domknięty w {domkniecie}% ({dom}/{razem}) — otwieramy szybciej, "
                 f"niż zamykamy; {otwarte_sug} sugestii i {bez_werdyktu} wizji bez werdyktu"
                 if domkniecie is not None and domkniecie < 50 else ""),
        "antywskaznik": "wskaźnik domknięcia rośnie od USUWANIA pozycji z ROADMAP zamiast ich "
                        "robienia — i od niedopisywania nowych. Spadek po dopisaniu uczciwie "
                        "nazwanego zadania jest ZDROWY, nie zły",
    }


# ── PIĘTRO 3: GRAPH — czy graf istnieje, działa i DECYDUJE ──────────────────────

# Moduły ścieżki DECYZYJNEJ. Graf czytany tutaj znaczy co innego niż graf czytany
# w raporcie startowym — i to rozróżnienie jest całym sensem tego piętra.
SCIEZKA_DECYZJI = ("legatus.py", "brama", "roj_sygnalow.py", "dyrygent.py", "petla_live")


def zmierz_graph() -> Dict[str, Any]:
    """Rozróżnia trzy rzeczy, które łatwo pomylić: graf ISTNIEJE / DZIAŁA / DECYDUJE."""
    czytelnicy = [l for l in _git("grep", "-l", "-E", "graf_pamieci|GrafPamieci").split()
                  if l.endswith(".py")]
    czytelnicy_kodu = [c for c in czytelnicy if not c.startswith("tests/")]
    przy_decyzji = [c for c in czytelnicy_kodu if any(s in c for s in SCIEZKA_DECYZJI)]
    producenci = [l for l in _git("grep", "-l", "krawedzie", "--", "imperium/", "narzedzia/").split()
                  if l.endswith(".py")]

    wezly = krawedzie = NIEZNANE
    try:
        # `_wczytaj` jest prywatne, ale to JEDYNE miejsce podające rozmiar grafu — tak samo
        # czyta go `raport_startowy`. Własne parsowanie pliku byłoby drugim źródłem prawdy
        # o tej samej rzeczy, a to rozjeżdża się przy pierwszej zmianie formatu (Prawo XVI).
        from imperium.biblioteki import graf_pamieci
        stan = graf_pamieci._wczytaj()
        wezly, krawedzie = stan.get("n_wezlow", NIEZNANE), stan.get("n_krawedzi", NIEZNANE)
    except Exception:  # noqa: BLE001
        pass                     # brak odczytu to NIEZNANE, nie zero (Prawo I)

    wskazniki = {
        "wezly": wezly, "krawedzie": krawedzie,
        "czytelnicy_w_kodzie": len(czytelnicy_kodu),
        "czytelnicy_przy_decyzji": len(przy_decyzji),
        "kto_przy_decyzji": przy_decyzji or "NIKT",
        "producenci_krawedzi": len(producenci),
    }
    poziom = _poziom([
        wezly not in (NIEZNANE, 0),      # 1 — graf w ogóle istnieje
        len(czytelnicy_kodu) >= 2,       # 2 — ktoś go czyta (nie tylko sam siebie)
        len(producenci) >= 2,            # 3 — coś go KARMI, więc rośnie
        bool(przy_decyzji),              # 4 — czytany PRZY DECYZJI, nie tylko drukowany
    ])
    return {
        "pietro": "GRAPH", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": ("graf NIE jest czytany przy żadnej decyzji — karmi raport i zapominanie, "
                 "czyli poprawia PAMIĘĆ, nie WYBÓR" if not przy_decyzji else ""),
        "antywskaznik": "poziom rośnie od DOPISYWANIA węzłów, a węzły przybywają same z każdą "
                        "sesją. Rozstrzyga wyłącznie próg 4 (czytany przy decyzji) — reszta "
                        "mierzy rozmiar, nie pożytek",
    }


# ── PIĘTRO 4: HARNESS — czy reguła ma EGZEKUTORA, nie tylko zapis ───────────────
# DLACZEGO DOPISANE 2026-08-06 (rozkaz Cezara: „chciałbym, żeby pokazywał wszystkie etapy,
# nie tylko trzy"): ROADMAP przy CORONIE D notował od 2026-08-03, że MATURITAS mierzy
# **3 z 9** pięter, a DWA spoza trójki **JUŻ STOJĄ i nie są liczone** — HARNESS i
# NEURO-SYMBOLIC — więc „prawdopodobnie ZANIŻAMY własny stan". Miernik, który pomija
# zbudowane piętra, myli się w drugą stronę niż laurka, ale myli się tak samo.
#
# CZEMU AKURAT TE DWA, A NIE POZOSTAŁE CZTERY: te dwa mierzą rzeczy NASZE i policzalne
# z kodu (hooki, workflow, warstwy audytu). Pozostałe znamy z materiału zewnętrznego,
# którego NIE OSĄDZILIŚMY — a miernik zbudowany na cudzej, nieosądzonej taksonomii byłby
# dokładnie tą wadą, którą ma wykrywać (warunek uczciwości zapisany przy CORONIE D).

def zmierz_harness() -> Dict[str, Any]:
    """Czy reguły Imperium mają EGZEKUTORA — i czy ten egzekutor żyje poza maszyną Architekta.

    Rozróżnia cztery rzeczy, które łatwo pomylić: reguła ZAPISANA / obserwowana /
    ZAPOBIEGAJĄCA / egzekwowana POZA maszyną autora. Dowód, że to rozróżnienie jest realne:
    kontrakt append-only był deklarowany w sześciu organach i egzekwowany przez ZERO,
    a Prawo XXI miało 24 warstwy i zero egzekutorów poza terminalem Architekta aż do VALLUM.
    """
    zdarzenia: Dict[str, int] = {}
    ustawienia = KORZEN / ".claude" / "settings.json"
    try:
        dane = json.loads(ustawienia.read_text(encoding="utf-8", errors="replace"))
        for zdarzenie, wpisy in (dane.get("hooks") or {}).items():
            zdarzenia[zdarzenie] = len(wpisy) if isinstance(wpisy, list) else 1
    except Exception:  # noqa: BLE001
        pass                       # brak/zepsuty plik = pusto, nie zgadujemy (Prawo I)

    # Egzekutor POZA maszyną: workflow, który realnie woła bramkę Imperium. Sama obecność
    # pliku .yml nie wystarcza — CI drukujące „hello" byłoby tapetą (warunek Cezara).
    workflows = sorted((KORZEN / ".github" / "workflows").glob("*.yml")) \
        if (KORZEN / ".github" / "workflows").exists() else []
    wolajace_bramke = [w.name for w in workflows
                       if "run_tests.py" in w.read_text(encoding="utf-8", errors="replace")]

    warstwy = _warstwy_audytu()
    zapobiegawcze = zdarzenia.get("PreToolUse", 0)

    wskazniki = {
        "hooki_zdarzenia": zdarzenia or NIEZNANE,
        "hooki_razem": sum(zdarzenia.values()) if zdarzenia else 0,
        "zapobiegawcze_PreToolUse": zapobiegawcze,
        "warstwy_audytu": warstwy,
        "workflow_poza_maszyna": [w.name for w in workflows] or "BRAK",
        "workflow_wolajace_bramke": wolajace_bramke or "BRAK",
    }
    poziom = _poziom([
        bool(zdarzenia),                 # 1 — jakikolwiek automat w ogóle istnieje
        len(zdarzenia) >= 3,             # 2 — obejmuje wiele zdarzeń, nie tylko start sesji
        zapobiegawcze > 0,               # 3 — ODMAWIA przed szkodą, nie raportuje po niej
        bool(wolajace_bramke),           # 4 — egzekutor poza maszyną Architekta (VALLUM)
    ])
    wask = ""
    if not zdarzenia:
        wask = "ZERO hooków — każda reguła zależy od pamięci Architekta"
    elif not zapobiegawcze:
        wask = ("hooki tylko RAPORTUJĄ — nic nie odmawia przed szkodą "
                "(VINDEX wykrywa po fakcie, SILENTIUM zapobiega)")
    elif not wolajace_bramke:
        wask = ("bramka działa wyłącznie na maszynie Architekta — brak egzekutora w CI, "
                "więc commit z innego urządzenia albo przerwana sesja omija Prawo XXI")
    return {
        "pietro": "HARNESS", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki, "wask": wask,
        "organy": organy_pietra("HARNESS"),
        "antywskaznik": "poziom rośnie od DODAWANIA hooków, a hook, który nigdy nie odmówił, "
                        "jest nieodróżnialny od braku hooka. Rozstrzyga próg 3 (zapobiega) "
                        "i 4 (poza maszyną) — liczba hooków mierzy nakład, nie ochronę",
    }


# ── PIĘTRO 5: NEURO-SYMBOLIC — twarda reguła nad miękkim wyjściem ───────────────

def zmierz_neuro_symbolic() -> Dict[str, Any]:
    """Czy wyjście LLM-a (moje) jest sprawdzane REGUŁĄ DETERMINISTYCZNĄ, a nie drugim LLM-em.

    To jest piętro, na którym Imperium stoi wysoko od dawna, nigdy tego nie licząc:
    audyt spójności, INDEX FALSORUM i VINDEX to weryfikacja symboliczna wbudowana
    w architekturę, nie recenzja post-hoc. Zmierzony powód, dla którego to piętro ma
    znaczenie: DeepSeek halucynował w 94–96 % odpowiedzi z pamięci, a recenzent zewnętrzny
    cytował NIEISTNIEJĄCE reguły — obu złapały reguły twarde, nie drugi model.
    """
    warstwy = _warstwy_audytu()
    falsa = DANE / "index_falsorum.jsonl"
    ile_falsa = len(_jsonl("index_falsorum.jsonl")) if falsa.exists() else 0
    ksiega = len(_jsonl("ksiega_wad_kodu.jsonl"))

    # Czy weryfikacja UMIE ZATRZYMAĆ, czy tylko opisuje: bramka musi mieć kod wyjścia.
    audyt = KORZEN / "narzedzia" / "audyt_spojnosci.py"
    ma_exit = "sys.exit" in audyt.read_text(encoding="utf-8", errors="replace") \
        if audyt.exists() else False
    # Czy stoi PRZED zapisem (PreToolUse), czy dopiero po nim.
    przed_zapisem = []
    ustawienia = KORZEN / ".claude" / "settings.json"
    try:
        dane = json.loads(ustawienia.read_text(encoding="utf-8", errors="replace"))
        przed_zapisem = [h for h in (dane.get("hooks") or {}).get("PreToolUse", [])]
    except Exception:  # noqa: BLE001
        pass

    wskazniki = {
        "warstwy_regul": warstwy,
        "obalone_twierdzenia_pod_straza": ile_falsa,
        "klasy_wad_w_ksiedze": ksiega,
        "bramka_ma_kod_wyjscia": ma_exit,
        "weryfikacja_przed_zapisem": len(przed_zapisem),
    }
    poziom = _poziom([
        warstwy > 0,                     # 1 — istnieje jakakolwiek reguła twarda
        warstwy >= 10,                   # 2 — reguły pokrywają wiele wymiarów
        bool(ma_exit),                   # 3 — reguła UMIE ZATRZYMAĆ, nie tylko opisać
        bool(przed_zapisem),             # 4 — sprawdza PRZED zapisem, nie po szkodzie
    ])
    wask = ""
    if not warstwy:
        wask = "brak reguł deterministycznych — wyjście modelu nikt nie sprawdza twardo"
    elif not ma_exit:
        wask = "weryfikacja RAPORTUJE, ale nie zatrzymuje — cisza udająca zgodę"
    elif not przed_zapisem:
        wask = "weryfikacja działa PO fakcie — szkoda powstaje, zanim reguła się odezwie"
    return {
        "pietro": "NEURO-SYM", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki, "wask": wask,
        "organy": organy_pietra("NEURO-SYM"),
        "antywskaznik": "poziom rośnie od DOPISYWANIA warstw audytu, a warstwa o wąskim "
                        "zasięgu daje fałszywy spokój (zmierzone: W11 pilnowała 1 katalogu "
                        "z 11). Liczba warstw mierzy nakład, nie pokrycie",
    }


def zmierz() -> Dict[str, Any]:
    pietra = [zmierz_prompt(), zmierz_loop(), zmierz_graph(),
              zmierz_harness(), zmierz_neuro_symbolic()]
    for p in pietra:
        p.setdefault("organy", organy_pietra(p["pietro"]))
        p["luka_w_planie"] = luka_w_planie(p["wask"]) if p["wask"] else ""
    return {"pietra": pietra,
            "wask_gardla": [p["wask"] for p in pietra if p["wask"]],
            "poziomy": {p["pietro"]: p["poziom"] for p in pietra},
            "mierzone_pieter": len(pietra), "znane_pieter": PIETER_ZNANYCH,
            "niemierzone": list(PIETRA_NIEMIERZONE),
            "kandydaci": list(KANDYDACI_NA_PIETRA),
            "taksonomia": TAKSONOMIA_ZRODLO}


# ── MIGAWKI — bo „IQ 137" bez historii jest fikcją (zasada 3 projektu INGENIUM) ──

MIGAWKI = DANE / "maturitas_migawki.jsonl"


def zapisz_migawke(w: Optional[Dict[str, Any]] = None, sciezka: Path = MIGAWKI) -> Dict[str, Any]:
    """Dopisuje migawkę poziomów (append-only — VINDEX tego pilnuje).

    Zapisujemy WYŁĄCZNIE poziomy i garść liczb, nie cały raport: migawka ma służyć
    porównaniu, a nie być drugą kopią stanu, która zaraz rozjedzie się z kodem.
    """
    from datetime import date
    w = w or zmierz()
    wpis = {"data": date.today().isoformat(), "poziomy": w["poziomy"],
            "wask_gardla": len(w["wask_gardla"]),
            "loop": {k: v for k, v in w["pietra"][1]["wskazniki"].items()
                     if k in ("roadmap_domkniecie_proc", "sugestie_otwarte",
                              "wizje_bez_werdyktu", "dlug_honorowy")}}
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False, sort_keys=True) + "\n")
    return wpis


def delta(w: Optional[Dict[str, Any]] = None, sciezka: Path = MIGAWKI) -> Dict[str, Any]:
    """Różnica wobec OSTATNIEJ migawki. Brak historii to `NIEZNANE`, nie „bez zmian".

    Rozróżnienie jest istotne: „bez zmian" twierdzi, że porównaliśmy i wyszło zero.
    Przy pierwszym biegu nie porównaliśmy niczego — i tak ma to być powiedziane.
    """
    w = w or zmierz()
    if not sciezka.exists():
        return {"stan": NIEZNANE, "powod": "brak historii — to pierwsza migawka"}
    poprzednie = [json.loads(l) for l in sciezka.open(encoding="utf-8") if l.strip()]
    if not poprzednie:
        return {"stan": NIEZNANE, "powod": "brak historii — to pierwsza migawka"}
    ost = poprzednie[-1]
    zmiany = {p: w["poziomy"][p] - ost["poziomy"].get(p, 0)
              for p in w["poziomy"] if w["poziomy"][p] != ost["poziomy"].get(p, 0)}
    return {"stan": "zmiana" if zmiany else "bez zmian", "od": ost.get("data"),
            "zmiany_poziomow": zmiany, "poprzednie": ost["poziomy"], "obecne": w["poziomy"]}


def raport(w: Optional[Dict[str, Any]] = None) -> str:
    w = w or zmierz()
    linie = [f"📐 MATURITAS — piętra inżynierii Imperium (lustro, nie kierownica) — "
             f"mierzone {w['mierzone_pieter']} z {w['znane_pieter']} znanych:"]
    for p in w["pietra"]:
        pasek = "█" * p["poziom"] + "·" * (4 - p["poziom"])
        linie.append(f"   {p['pietro']:<9} [{pasek}] {p['poziom']}/4 {p['nazwa']}")
        for k, v in p["wskazniki"].items():
            linie.append(f"      · {k}: {v}")
        org = p.get("organy") or {}
        if org.get("zywe"):
            linie.append(f"      🏛️ organy ({len(org['zywe'])}): {', '.join(org['zywe'])}")
        if org.get("widma"):
            linie.append(f"      🚨 ORGANY-WIDMA (w mapie, brak na dysku): "
                         f"{', '.join(org['widma'])}")
        if p["wask"]:
            linie.append(f"      ⚠️ WĄSKIE GARDŁO: {p['wask']}")
            if p.get("luka_w_planie"):
                linie.append(f"      📋 dopełnienie: {p['luka_w_planie']}")
    if not w["wask_gardla"]:
        linie.append("   ✅ żadne piętro nie zgłasza wąskiego gardła")
    if w.get("niemierzone"):
        linie.append(f"   ❔ NIEMIERZONE ({len(w['niemierzone'])} z {w['znane_pieter']}) — "
                     "taksonomia z materiału, którego NIE OSĄDZILIŚMY (warunek CORONY D):")
        linie += [f"      · {n}" for n in w["niemierzone"]]
    linie.append("   ℹ️ Goodhart: ten wynik NIE steruje decyzją handlową ani wagami. "
                 "Podnosi się go wyłącznie naprawą tego, co mierzy (`--antywskazniki`).")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import sys

    ap = argparse.ArgumentParser(
        description="MATURITAS — na którym piętrze inżynierii stoi Imperium")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--antywskazniki", action="store_true",
                    help="jak można oszukać każde piętro (obowiązek z projektu INGENIUM)")
    ap.add_argument("--zwiezle", action="store_true", help="same poziomy, bez wskaźników")
    ap.add_argument("--zapisz", action="store_true", help="dopisz migawkę poziomów (append-only)")
    ap.add_argument("--delta", action="store_true", help="różnica wobec ostatniej migawki")
    args = ap.parse_args()

    wynik = zmierz()
    if args.delta:
        d = delta(wynik)
        print(f"📐 MATURITAS Δ: {d['stan']}" + (f" (od {d['od']})" if d.get("od") else ""))
        if d.get("powod"):
            print(f"   ℹ️ {d['powod']}")
        for p, z in (d.get("zmiany_poziomow") or {}).items():
            # `.get` z NIEZNANE, bo piętro DOPISANE po ostatniej migawce nie ma historii —
            # i to nie jest awaria, tylko normalny stan po rozszerzeniu miernika. Pierwsza
            # wersja czytała `d['poprzednie'][p]` wprost i wywaliła się `KeyError: 'HARNESS'`
            # w tej samej minucie, w której dopisałem HARNESS i NEURO-SYM (2026-08-07).
            # Klasa: miernik, który rozszerzenie własnego zasięgu traktuje jak błąd danych.
            skad = d["poprzednie"].get(p, NIEZNANE)
            strzalka = "🆕" if skad == NIEZNANE else ("📈" if z > 0 else "📉")
            print(f"   {strzalka} {p}: {skad} → {d['obecne'][p]}")
        if d["stan"] == "bez zmian":
            print(f"   poziomy: {d['obecne']}")
        sys.exit(0)
    if args.zapisz:
        print(f"📐 MATURITAS — migawka zapisana: {zapisz_migawke(wynik)}")
        sys.exit(0)
    if args.antywskazniki:
        print("📐 MATURITAS — jak można oszukać każde piętro (czytaj PRZED chwaleniem się):")
        for p in wynik["pietra"]:
            print(f"\n   {p['pietro']}: {p['antywskaznik']}")
    elif args.json:
        print(json.dumps(wynik, ensure_ascii=False, indent=2))
    elif args.zwiezle:
        print("📐 MATURITAS: " + " | ".join(
            f"{p['pietro']} {p['poziom']}/4 {p['nazwa']}" for p in wynik["pietra"]))
        for g in wynik["wask_gardla"]:
            print(f"   ⚠️ {g}")
    else:
        print(raport(wynik))
    sys.exit(0)
