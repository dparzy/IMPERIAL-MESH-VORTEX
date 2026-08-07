"""🔎 RECOGNITOR — poświadcza, czy RECENZJA POKRYWA DZISIEJSZY STAN kodu.

W Rzymie *recognitor* był urzędnikiem od `recognitio` — urzędowego sprawdzenia, czy dokument
odpowiada stanowi faktycznemu. Tu robi dokładnie to jedno: pyta, czy commit, który widział
recenzent, to nadal ten commit, który mamy. Nic więcej nie ocenia — nie czyta kodu, nie
powtarza recenzji, nie ma zdania o wadach. Odpowiada na jedno pytanie: **czy recenzent
w ogóle patrzył na to, co dziś stoi w gałęzi.**

POWÓD ISTNIENIA (zmierzone 2026-07-27, wachta po PR #134):
Cezar zapytał, czy cubic znalazł NOWE błędy. Odpowiedź brzmiała „nie" — i była prawdziwa
w literze, a myląca w treści. Pomiar: recenzent wykonał DOKŁADNIE JEDEN przebieg
(`review-run=2242666a`, 10:34:58 UTC), a wszystkie 15 uwag napisał wobec commita `bfb5e26`.
Potem na gałąź weszły TRZY commity — w tym `bc4913c`, który naprawiał jego własne uwagi
i dokładał nowy organ (NOMENCLATOR, 295 linii) — i PR został zmergowany o 12:25 UTC bez
drugiego przebiegu. **756 linii .py weszło do `main` bez recenzji zewnętrznej.**

KLASA WADY: „cisza recenzenta czytana jako zgoda". Siostra klasy z 2026-07-27 (zakaz pushu
bez mechanizmu) i z pomiaru alarmu na stderr: brak nowych uwag wyglądał identycznie jak
brak wad, bo NIC nie pytało, czy recenzent nadążył. Rzecz niemierzona nie jest zielona —
jest niezmierzona, a to dwie różne rzeczy (Prawo I).

DLACZEGO ODDZIELNY ORGAN, A NIE WARSTWA AUDYTU (Prawo XVI + doktryna wydruku startowego):
`narzedzia/audyt_spojnosci.py` jest OFFLINE i stdlib-only, bo chodzi przy każdym starcie
sesji. Ten pomiar WYMAGA SIECI (GitHub API przez `gh`), więc na starcie byłby wolny i kruchy —
dokładnie z tego powodu poza hookiem startowym stoi już cenzus adapterów. RECOGNITOR chodzi
tam, gdzie jest potrzebny: w kroku 3 domknięcia wachty (adversarial pre-push) i w `/limes`.

⚠️ TO ZDANIE BYŁO FAŁSZEM PRZEZ DZIEWIĘĆ DNI (zmierzone 2026-08-06). Organ powstał 2026-07-28
i od razu deklarował powyżej, że „chodzi w `/limes`" — a `SIGLA["LIMES"]` trzymało twardą listę
komend, do której nigdy go nie dopisano. Docstring opisywał zamiar, nie stan; nic tego nie
sprawdzało, bo strażnik pieczęci pytał wyłącznie „czy komenda LIMES wskazuje na żywy moduł",
nigdy „czy nakazana komenda w ogóle do LIMES trafiła". Od 2026-08-06 zdanie ma egzekutora:
`sigillarium.komendy_konstytucji_poza_pieczecia()` + `test_limes_wola_recognitora`. Wnioskiem
NIE jest „poprawiono docstring", tylko: **wołacz zadeklarowany w prozie to wołacz-widmo,
dopóki nie wskaże go test** — dokładnie jak ścieżka .py cytowana w docs (Warstwa 16).

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ Nie ocenia jakości recenzji ani trafności uwag — to praca sędziego (zmierzone: 20/22
    uwag cubica słuszne w PR #133, ale jedyne P1 cytowało dwie NIEISTNIEJĄCE reguły).
  • ❌ Nie odróżnia „recenzent przeczytał i nie miał uwag" od „recenzent nie przyszedł" na
    podstawie samych komentarzy inline — dlatego pyta endpoint `reviews` (zdarzenia recenzji
    istnieją także bez ani jednej uwagi), a nie tylko `comments`. Gdy i to milczy, mówi
    „BRAK RECENZJI" wprost, zamiast zgadywać.
  • ❌ Nie próbuje niczego naprawić. Gdy PR jest już zmergowany, luka jest NIEODWRACALNA
    (nowy PR z tej gałęzi pokazałby zero różnicy) — organ mówi to wprost, żeby sędzia wiedział,
    że jedyną drogą jest własna recenzja adversarialna, nie czekanie na cudze oczy.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# Recenzenci, których milczenie ma być pilnowane. Pusty zbiór = dowolny recenzent.
# Prefiks, nie równość — boty GitHuba noszą sufiks `[bot]` (`cubic-dev-ai[bot]`).
RECENZENCI = ("cubic",)

_TIMEOUT = 45


# ── ADAPTERY (sieć / git) — cienkie z rozmysłem, cała logika w `ocen_pokrycie` ────

def _uruchom(cmd: list) -> tuple:
    """(ok, stdout) — nigdy nie rzuca. Brak narzędzia/sieci to WYNIK, nie wyjątek."""
    exe = shutil.which(cmd[0])
    if not exe:
        return False, f"brak narzędzia `{cmd[0]}` w PATH"
    try:
        p = subprocess.run([exe, *cmd[1:]], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=_TIMEOUT)
    except (subprocess.TimeoutExpired, OSError) as e:
        return False, f"{type(e).__name__}: {e}"
    if p.returncode != 0:
        return False, (p.stderr or p.stdout or "").strip()[:300]
    return True, p.stdout


def _git(*args) -> tuple:
    return _uruchom(["git", *args])


def _gh_json(*args):
    """Wynik `gh ... --json`/`gh api` sparsowany; None gdy się nie udało."""
    ok, out = _uruchom(["gh", *args])
    if not ok:
        return None
    try:
        return json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return None


def _galaz_biezaca() -> str:
    ok, out = _git("symbolic-ref", "--short", "HEAD")
    return out.strip() if ok else ""


def _head() -> str:
    ok, out = _git("rev-parse", "HEAD")
    return out.strip() if ok else ""


def _commity_po(commit: str) -> list:
    """Commity między `commit` a HEAD. None = commita nie ma lokalnie (np. po force-push)."""
    ok, _ = _git("cat-file", "-e", f"{commit}^{{commit}}")
    if not ok:
        return None
    ok, out = _git("log", "--oneline", f"{commit}..HEAD")
    if not ok:
        return None
    return [linia for linia in out.splitlines() if linia.strip()]


def _interesujacy(login: str) -> bool:
    return not RECENZENCI or any(login.lower().startswith(r) for r in RECENZENCI)


# ── RDZEŃ — czysty, bez sieci, w pełni testowalny ────────────────────────────────

def ocen_pokrycie(*, head: str, recenzje: list, commity_po, stan_pr: str,
                  pr_numer=None, gh_ok: bool = True, powod_bledu: str = "",
                  head_pr: str = "") -> dict:
    """Werdykt: czy ostatnia recenzja pokrywa HEAD gałęzi.

    Argumenty są DANYMI, nie źródłami — dzięki temu każdy stan (luka, merge, force-push,
    brak `gh`) da się przetestować bez sieci. `commity_po=None` znaczy „nie wiadomo",
    i taki stan NIGDY nie jest zielony.

    Zwraca słownik z `status`, `ikona`, `opis`, `exit` — kod wyjścia jest częścią kontraktu
    bramki: 0 wolno tylko wtedy, gdy naprawdę zmierzyliśmy pokrycie.
    """
    baza = {"head": head, "pr": pr_numer, "stan_pr": stan_pr,
            "recenzowany": None, "ile_po": None, "commity_po": [], "naprawialne": None}

    if not gh_ok:
        return {**baza, "status": "niezmierzone", "ikona": "❔", "exit": 2,
                "opis": f"NIEZMIERZONE — nie dało się odpytać GitHuba ({powod_bledu or 'brak powodu'}). "
                        "To nie jest zielone światło: nie wiemy, czy recenzent widział ten kod."}

    if pr_numer is None:
        return {**baza, "status": "brak_pr", "ikona": "ℹ️", "exit": 0,
                "opis": "Gałąź nie ma PR — nie ma recenzenta, którego milczenie można źle odczytać."}

    istotne = [r for r in recenzje if _interesujacy(r.get("recenzent", ""))]
    if not istotne:
        return {**baza, "status": "brak_recenzji", "ikona": "🚨", "exit": 1,
                "opis": f"PR #{pr_numer} NIE MA ANI JEDNEJ recenzji od {' / '.join(RECENZENCI) or 'kogokolwiek'}. "
                        "Brak uwag = brak spojrzenia, nie brak wad."}

    # ⚠️ SZKIC NIE JEST RECENZJĄ (naprawa 2026-08-07, wada nr 1 własnej recenzji adversarialnej —
    # ZMIERZONA SZERZEJ, NIŻ JĄ ZGŁOSZONO). Recenzja zgłosiła ten ślepy punkt w `ocen_historie`
    # (miernik). Pomiar przed naprawą pokazał, że siedzi ON TAKŻE TUTAJ, czyli w ŚCIEŻCE BRAMKOWEJ:
    # `ocen_pokrycie(head='abc', recenzje=[{'commit':'abc','kiedy':''}])` zwracało `pokryte, exit 0`.
    # GitHub oddaje w `reviews` również szkice — mają `commit_id`, ale `submitted_at = null` (stan
    # PENDING). Bez tego filtra ROZPOCZĘCIE pisania recenzji zielenił bramkę mocniej niż jej
    # ZŁOŻENIE. Data złożenia jest tu jedynym DOWODEM, że ktokolwiek nacisnął „submit"; jej brak
    # to niewiedza, a niewiedza nigdy nie jest zielona (Prawo I).
    zlozone = [r for r in istotne if r.get("kiedy")]
    if not zlozone:
        return {**baza, "status": "recenzja_niezlozona", "ikona": "🚨", "exit": 1,
                "opis": f"PR #{pr_numer}: recenzja ISTNIEJE, ale NIE ZOSTAŁA ZŁOŻONA "
                        "(brak `submitted_at` — stan PENDING). Szkic recenzenta nie jest "
                        "spojrzeniem: tych uwag nie zobaczył jeszcze nikt."}

    ostatnia = max(zlozone, key=lambda r: r.get("kiedy", ""))
    recenzowany = ostatnia.get("commit", "")
    baza["recenzowany"] = recenzowany
    baza["kiedy"] = ostatnia.get("kiedy", "")

    if recenzowany == head:
        return {**baza, "status": "pokryte", "ikona": "✅", "exit": 0, "ile_po": 0,
                "opis": f"Recenzja pokrywa HEAD ({head[:7]}) — recenzent widział dokładnie ten kod."}

    if commity_po is None:
        return {**baza, "status": "commit_nieznany", "ikona": "❔", "exit": 2,
                "opis": f"Recenzowany commit {recenzowany[:7]} nie istnieje w tym repo "
                        "(force-push albo niepobrana gałąź) — pokrycia NIE DA SIĘ policzyć."}

    # „ZMERGOWANY" NIE ZNACZY JESZCZE „NIEODWRACALNY" (naprawa 2026-07-28, wykryta przez UŻYCIE
    # tego organu w checkliście domknięcia — pierwszy dzień jego życia). Pierwsza wersja pisała
    # przy każdym zmergowanym PR: „nowy PR z tej gałęzi pokaże zero różnicy". To prawda TYLKO
    # dopóki HEAD stoi na commicie, który wszedł do mergu. Gdy gałąź poszła dalej, nowe commity
    # da się objąć NOWYM PR-em — a mój werdykt odradzał wtedy jedyną skuteczną drogę. Strażnik
    # mówiący „nie da się" tam, gdzie się da, jest gorszy od milczenia: zniechęca do naprawy.
    zmergowany = (stan_pr or "").upper() == "MERGED"
    poza_mergem = bool(head_pr) and head != head_pr
    nieodwracalna = zmergowany and not poza_mergem
    baza.update({"ile_po": len(commity_po), "commity_po": commity_po,
                 "naprawialne": not nieodwracalna})
    if nieodwracalna:
        ogon = ("PR ZMERGOWANY, a gałąź stoi na commicie mergu — luka NIEODWRACALNA: nowy PR "
                "pokaże zero różnicy. Jedyna droga to własna recenzja adversarialna tego zakresu.")
    elif zmergowany:
        ogon = ("PR zmergowany, ale gałąź poszła DALEJ — te commity obejmie NOWY PR "
                "(po pushu Cezara). Commity sprzed mergu pozostają nieodwracalnie nieprzejrzane.")
    else:
        ogon = "PR otwarty — po pushu recenzent zobaczy te commity."
    return {**baza, "status": "luka_zamknieta" if nieodwracalna else "luka_otwarta",
            "ikona": "🚨", "exit": 1,
            "opis": f"LUKA: recenzja stoi na {recenzowany[:7]}, a HEAD to {head[:7]} — "
                    f"{len(commity_po)} commit(ów) NIKT nie zrecenzował. {ogon}"}


# ── POMIAR NA ŻYWO ───────────────────────────────────────────────────────────────

def zbadaj(galaz: str = "") -> dict:
    """Zmierz pokrycie recenzji dla gałęzi (domyślnie bieżącej). Wymaga `gh` i sieci."""
    galaz = galaz or _galaz_biezaca()
    head = _head()
    if not head:
        return ocen_pokrycie(head="", recenzje=[], commity_po=None, stan_pr="",
                             gh_ok=False, powod_bledu="to nie jest repozytorium git")

    pr = _gh_json("pr", "list", "--head", galaz, "--state", "all", "--limit", "1",
                  "--json", "number,state,headRefOid")
    if pr is None:
        return ocen_pokrycie(head=head, recenzje=[], commity_po=None, stan_pr="",
                             gh_ok=False, powod_bledu="`gh pr list` nie odpowiedział")
    if not pr:
        return ocen_pokrycie(head=head, recenzje=[], commity_po=None, stan_pr="", pr_numer=None)

    numer, stan = pr[0]["number"], pr[0].get("state", "")
    surowe = _gh_json("api", f"repos/{{owner}}/{{repo}}/pulls/{numer}/reviews?per_page=100")
    if surowe is None:
        return ocen_pokrycie(head=head, recenzje=[], commity_po=None, stan_pr=stan,
                             pr_numer=numer, gh_ok=False,
                             powod_bledu=f"`gh api .../pulls/{numer}/reviews` nie odpowiedział")

    recenzje = [{"commit": r.get("commit_id") or "",
                 "kiedy": r.get("submitted_at") or "",
                 "recenzent": (r.get("user") or {}).get("login", "")}
                for r in surowe]
    # Ten sam filtr co w rdzeniu: punktem odniesienia jest recenzja ZŁOŻONA, nie szkic.
    zlozone = [r for r in recenzje if _interesujacy(r["recenzent"]) and r["kiedy"]]
    po = _commity_po(max(zlozone, key=lambda r: r["kiedy"])["commit"]) if zlozone else []
    return ocen_pokrycie(head=head, recenzje=recenzje, commity_po=po, stan_pr=stan,
                         pr_numer=numer, head_pr=pr[0].get("headRefOid") or "")


# ── FENESTRA RECOGNITIONIS — OKNO RECENZJI (2026-08-06) ──────────────────────────
# `zbadaj()` odpowiada o JEDNEJ gałęzi i tylko „teraz". To za mało, żeby zobaczyć KLASĘ:
# pojedynczy PR bez recenzji wygląda na potknięcie, dopiero rozkład po całym repo pokazuje
# regułę. Zmierzone 2026-08-06 na wszystkich 141 PR: 92 (65,2%) nie miało ANI JEDNEJ
# recenzji — czyli stan normalny, nie wyjątek.
#
# CO TO MIERZY, A CZEGO NIE: nie jakość recenzji i nie to, czy recenzent miał rację —
# tylko czy w ogóle ISTNIAŁO OKNO, w którym mógł się wypowiedzieć. Zmierzony rozdział
# w próbce 12 ostatnich PR był doskonały: każdy PR żyjący sekundy (9–35 s) nie miał
# recenzji, każdy żyjący minuty/godziny (37 min – 4 h 55) miał. Przyczyną nie było więc
# milczenie recenzenta ani zapominalstwo Architekta, tylko to, że PR bywał mergowany,
# ZANIM recenzent zdążył wystartować. Dlatego miara nazywa się OKNEM, nie POKRYCIEM.

def mediana(liczby: list):
    """Mediana bez zależności (stdlib-only, jak reszta organu). None dla pustej listy."""
    s = sorted(x for x in liczby if x is not None)
    if not s:
        return None
    srodek = len(s) // 2
    return s[srodek] if len(s) % 2 else (s[srodek - 1] + s[srodek]) / 2


def _sekundy(od: str, do: str):
    """Różnica dwóch znaczników ISO-8601 z GitHuba w sekundach; None gdy któregoś brak."""
    if not od or not do:
        return None
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        return (datetime.strptime(do, fmt) - datetime.strptime(od, fmt)).total_seconds()
    except (ValueError, TypeError):
        return None


def ocen_historie(pry: list) -> dict:
    """Rozkład pokrycia recenzji po CAŁEJ historii PR — czysty rdzeń, bez sieci.

    `pry`: [{"numer", "utworzony", "zmergowany", "head", "recenzje": [...]}]. Jak
    w `ocen_pokrycie`, argumenty są DANYMI, więc każdy rozkład da się przetestować bez sieci.

    „Pokryty" znaczy: istnieje recenzja od pilnowanego recenzenta ZŁOŻONA NA TYM SAMYM
    commicie, który stoi na gałęzi. PR z recenzją na STARSZYM commicie liczy się jako
    `z_recenzja`, ale NIE jako `pokryte` — to dokładnie ta różnica, którą `ocen_pokrycie`
    łapie dla jednej gałęzi (klasa PR #134: recenzja była, tyle że trzy commity wcześniej),
    i zatarcie jej w statystyce zamieniłoby miernik w pochlebcę.

    ⚠️ DRUGI WYMIAR — NA CZAS (dodany 2026-08-06, w godzinę po pierwszej wersji, bo
    PIERWSZY POMIAR TYM MIERNIKIEM OBALIŁ JEGO WŁASNĄ WYSTARCZALNOŚĆ). Pokrycie commitu
    nie mówi nic o tym, czy recenzja przyszła NA CZAS. Zmierzone: z 49 PR z recenzją
    cubica **36 (73%) dostało ją PO MERGU** — kod był już w `main`, więc recenzja nie
    pełniła funkcji bramy, tylko sekcji zwłok. Miernik liczący je jako sukces chwaliłby
    proces za coś, co nikogo nie chroniło. Prawdziwa liczba to `pokryte_przed_mergem`:
    **10 ze 141 PR (7,1%)** — pomiar z 2026-08-06 komendą `recognitor historia`.

    ⚠️ TA LICZBA BYŁA W TYM DOCSTRINGU FAŁSZYWA (wada nr 2 własnej recenzji, naprawiona
    2026-08-07). Stało tu „13 ze 141 (9,2%)", a ten sam kod na tym samym repo zwracał 10
    (7,1%): dziewiątka pochodziła z mojego RĘCZNEGO rachunku 49−36, zrobionego ZANIM
    dołożyłem warunek `kryje_commit`. Klasa: Warstwa 23 (liczby w prozie niezgodne z kodem)
    — tyle że w docstringu `.py`, którego W23 nie skanuje. Dlatego liczba nosi teraz DATĘ
    i KOMENDĘ: twierdzenie o przeszłym pomiarze nie gnije, twierdzenie o „stanie" gnije zawsze.

    Ta poprawka jest tą samą klasą, przed którą ostrzega akapit wyżej — miara zbyt
    łagodna wobec własnego procesu. Raz złapana na cudzym wymiarze (commit), raz na
    własnym (czas).
    """
    ogolem = len(pry)
    pokryte, pokryte_przed, z_recenzja, po_mergu = 0, 0, 0, 0
    niezlozone, czas_nieznany = 0, 0
    okna_z, okna_bez = [], []
    niepokryte = []
    for pr in pry:
        istotne = [r for r in pr.get("recenzje", []) if _interesujacy(r.get("recenzent", ""))]
        # Szkic recenzenta (PENDING, `submitted_at = null`) NIE liczy się jako recenzja —
        # uzasadnienie i pomiar przy tym samym filtrze w `ocen_pokrycie`.
        zlozone = [r for r in istotne if r.get("kiedy")]
        okno = _sekundy(pr.get("utworzony", ""), pr.get("zmergowany", ""))
        if istotne and not zlozone:
            niezlozone += 1
        if zlozone:
            z_recenzja += 1
            okna_z.append(okno)
            ostatnia = max(zlozone, key=lambda r: r.get("kiedy", ""))
            kryje_commit = bool(ostatnia.get("commit")) and ostatnia["commit"] == pr.get("head")
            # Brak daty mergu (PR otwarty) NIE jest spóźnieniem — nic jeszcze nie weszło.
            data_mergu = pr.get("zmergowany", "")
            opoznienie = _sekundy(data_mergu, ostatnia["kiedy"]) if data_mergu else None
            spozniona = opoznienie is not None and opoznienie > 0
            # „NA CZAS" WYMAGA DOWODU, nie braku dowodu przeciwnego (ta sama klasa co wada nr 1):
            # albo PR nie jest jeszcze zmergowany, albo różnicę dat DAŁO SIĘ policzyć. Znacznik
            # nieparsowalny to niewiedza — dawne `(_sekundy(...) or 0) > 0` zamieniało ją w sukces.
            czas_zmierzony = (not data_mergu) or opoznienie is not None
            czas_nieznany += 0 if czas_zmierzony else 1
            na_czas = kryje_commit and czas_zmierzony and not spozniona
            po_mergu += 1 if spozniona else 0
            pokryte += 1 if kryje_commit else 0
            pokryte_przed += 1 if na_czas else 0
            if not na_czas:
                niepokryte.append(pr.get("numer"))
        else:
            okna_bez.append(okno)
            niepokryte.append(pr.get("numer"))
    return {
        "ogolem": ogolem,
        "pokryte": pokryte,
        "pokryte_przed_mergem": pokryte_przed,
        "recenzja_po_mergu": po_mergu,
        "z_recenzja": z_recenzja,
        "bez_recenzji": ogolem - z_recenzja,
        "recenzje_niezlozone": niezlozone,
        "czas_nieporownywalny": czas_nieznany,
        "odsetek_pokrycia": round(100.0 * pokryte / ogolem, 1) if ogolem else None,
        "odsetek_na_czas": round(100.0 * pokryte_przed / ogolem, 1) if ogolem else None,
        # MIARA GŁÓWNA ZADEKLAROWANA MASZYNOWO (wada nr 5 własnej recenzji, 2026-08-07).
        # Obok siebie stoją dwie liczby: `odsetek_pokrycia` (32,6% — wlicza recenzje PO
        # mergu) i `odsetek_na_czas` (7,1% — tylko te, które mogły cokolwiek zatrzymać).
        # Pochlebna jest pierwsza. Dopóki zwycięzca istniał wyłącznie w mojej głowie i w
        # kolejności linii raportu, wystarczyłaby jedna wygodna edycja nagłówka, żeby
        # miernik zaczął chwalić — bez żadnego czerwonego testu. Teraz wybór jest DANĄ,
        # której pilnuje test granicy (`test_miara_glowna_jest_ta_surowsza`).
        "miara_glowna": "odsetek_na_czas",
        "mediana_okna_z_recenzja_s": mediana(okna_z),
        "mediana_okna_bez_recenzji_s": mediana(okna_bez),
        "niepokryte_numery": niepokryte,
    }


def zbadaj_historie(limit: int = 200) -> dict:
    """Zmierz rozkład pokrycia na żywym repo. Wymaga `gh` i sieci."""
    surowe = _gh_json("pr", "list", "--state", "all", "--limit", str(limit),
                      "--json", "number,createdAt,mergedAt,headRefOid,reviews")
    if surowe is None:
        return {"ogolem": 0, "odsetek_pokrycia": None,
                "blad": "`gh pr list` nie odpowiedział — pomiar NIEZMIERZONY, nie zielony"}
    pry = [{"numer": p.get("number"), "utworzony": p.get("createdAt") or "",
            "zmergowany": p.get("mergedAt") or "", "head": p.get("headRefOid") or "",
            "recenzje": [{"commit": (r.get("commit") or {}).get("oid") or "",
                          "kiedy": r.get("submittedAt") or "",
                          "recenzent": (r.get("author") or {}).get("login", "")}
                         for r in (p.get("reviews") or [])]}
           for p in surowe]
    return ocen_historie(pry)


def _okno_czytelnie(sek) -> str:
    if sek is None:
        return "—"
    if sek < 90:
        return f"{sek:.0f} s"
    if sek < 5400:
        return f"{sek / 60:.0f} min"
    return f"{sek / 3600:.1f} h"


def raport_historii(w=None, limit: int = 200) -> str:
    w = zbadaj_historie(limit) if w is None else w
    if w.get("blad"):
        return f"❔ FENESTRA RECOGNITIONIS: {w['blad']}"
    # Nagłówek CZYTA zadeklarowaną miarę główną zamiast powtarzać jej nazwę — dzięki temu
    # `miara_glowna` nie jest ozdobnym kluczem, tylko nośnikiem: podmiana deklaracji na
    # łagodniejszą liczbę natychmiast zapala test granicy, a nie tylko zmienia wydruk.
    glowna = w.get("miara_glowna", "odsetek_na_czas")
    linie = [
        f"🔎 FENESTRA RECOGNITIONIS — okno recenzji na {w['ogolem']} PR:",
        f"   ⭐ PRZEJRZANE NA CZAS (recenzja na commicie gałęzi PRZED mergem): "
        f"{w['pokryte_przed_mergem']} ({w[glowna]}%)",
        f"   pokryte commitowo, ale PO MERGU (sekcja zwłok): {w['recenzja_po_mergu']}",
        f"   z jakąkolwiek recenzją: {w['z_recenzja']} | BEZ ANI JEDNEJ: {w['bez_recenzji']}",
        f"   mediana okna utworzenie→merge: z recenzją {_okno_czytelnie(w['mediana_okna_z_recenzja_s'])}"
        f" | bez recenzji {_okno_czytelnie(w['mediana_okna_bez_recenzji_s'])}",
    ]
    # Odrzucone dane MUSZĄ być widoczne. Cichy filtr jest tą samą klasą co cicha zeroizacja,
    # którą właśnie naprawiamy — tyle że o jedno piętro wyżej (Prawo I).
    if w.get("recenzje_niezlozone"):
        linie.append(f"   ✍️ PR ze SZKICEM recenzji (PENDING, nigdy nie złożona): "
                     f"{w['recenzje_niezlozone']} — liczone jako BEZ recenzji, bo nikt ich nie widział")
    if w.get("czas_nieporownywalny"):
        linie.append(f"   ❔ PR z nieporównywalnymi znacznikami czasu: {w['czas_nieporownywalny']} "
                     "— NIE zaliczone jako „na czas\", bo tego nie zmierzyliśmy")
    if w["recenzja_po_mergu"] > w["pokryte_przed_mergem"]:
        linie.append("   🚨 Recenzji PO mergu jest WIĘCEJ niż na czas — recenzent opisuje kod, "
                     "który już wszedł do `main`. To nie brama, to protokół powypadkowy.")
    if w["bez_recenzji"] and (w["mediana_okna_bez_recenzji_s"] or 0) < 90:
        linie.append("   ⚖️ Mediana okna „bez recenzji\" liczona w SEKUNDACH znaczy, że przyczyną "
                     "NIE jest milczenie recenzenta — PR bywa zmergowany, zanim ten zdąży ruszyć.")
    return "\n".join(linie)


def banner(w=None) -> str:
    """Jedna linia — zgodnie z ZASADĄ WYDRUKU (cisza gdy zielone, krzyk gdy czerwone)."""
    w = zbadaj() if w is None else w
    return f"{w['ikona']} RECOGNITOR (pokrycie recenzji): {w['opis']}"


def raport(w=None) -> str:
    w = zbadaj() if w is None else w
    linie = [banner(w)]
    if w.get("commity_po"):
        linie.append(f"   niezrecenzowane commity ({w['ile_po']}):")
        linie += [f"   • {c}" for c in w["commity_po"][:15]]
        if w["ile_po"] > 15:
            linie.append(f"   • … i {w['ile_po'] - 15} więcej")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(
        description="RECOGNITOR — czy recenzja pokrywa dzisiejszy HEAD (Prawo I: cisza ≠ zgoda)")
    p.add_argument("tryb", nargs="?", default="raport",
                   choices=["banner", "raport", "json", "historia"])
    p.add_argument("--galaz", default="", help="gałąź (domyślnie bieżąca)")
    p.add_argument("--limit", type=int, default=200,
                   help="ile PR obejmuje tryb `historia` (domyślnie 200)")
    p.add_argument("--bramka", action="store_true",
                   help="kod wyjścia wg werdyktu (0 pokryte / 1 luka / 2 niezmierzone)")
    args = p.parse_args()

    # FENESTRA jest MIERNIKIEM, nie bramką: świadomie zawsze kończy zerem. Rozkład po całej
    # historii opisuje przeszłość, której commit „naprawić" nie może — blokowanie nim commita
    # karałoby Architekta za PR-y sprzed miesiąca i nauczyłoby obchodzenia bramki.
    #
    # ⚠️ ODMOWA JEST GŁOŚNA (wada nr 4 własnej recenzji, naprawiona 2026-08-07). Wcześniej
    # `historia --bramka` kończyło się `sys.exit(0)` PRZED spojrzeniem na flagę: CLI przyjmowało
    # ją bez słowa i nie robiło nic. Ktokolwiek wpiąłby tę komendę w bramkę, dostałby wieczną
    # zieleń i wierzył, że coś pilnuje. Świadoma decyzja projektowa musi ODMAWIAĆ, nie MILCZEĆ —
    # ta sama różnica, którą cały ten organ wytyka recenzentowi (cisza ≠ zgoda).
    if args.tryb == "historia":
        if args.bramka:
            p.error("tryb `historia` NIE JEST bramką i świadomie nią nie będzie: opisuje rozkład "
                    "po całej historii PR, więc kod wyjścia karałby dzisiejszy commit za PR-y "
                    "sprzed miesiąca. Bramką jest `recognitor --bramka` (tryb domyślny).")
        print(raport_historii(limit=args.limit))
        sys.exit(0)

    werdykt = zbadaj(args.galaz)
    print(json.dumps(werdykt, ensure_ascii=False, indent=2) if args.tryb == "json"
          else banner(werdykt) if args.tryb == "banner" else raport(werdykt))
    sys.exit(werdykt["exit"] if args.bramka else 0)
