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
                  pr_numer=None, gh_ok: bool = True, powod_bledu: str = "") -> dict:
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

    ostatnia = max(istotne, key=lambda r: r.get("kiedy", ""))
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

    zmergowany = (stan_pr or "").upper() == "MERGED"
    baza.update({"ile_po": len(commity_po), "commity_po": commity_po,
                 "naprawialne": not zmergowany})
    ogon = ("PR jest ZMERGOWANY — luka NIEODWRACALNA: nowy PR z tej gałęzi pokaże zero różnicy. "
            "Jedyna droga to własna recenzja adversarialna tego zakresu."
            if zmergowany else
            "PR otwarty — po pushu recenzent zobaczy te commity.")
    return {**baza, "status": "luka_zamknieta" if zmergowany else "luka_otwarta",
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
    istotne = [r for r in recenzje if _interesujacy(r["recenzent"])]
    po = _commity_po(max(istotne, key=lambda r: r["kiedy"])["commit"]) if istotne else []
    return ocen_pokrycie(head=head, recenzje=recenzje, commity_po=po,
                         stan_pr=stan, pr_numer=numer)


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
    p.add_argument("tryb", nargs="?", default="raport", choices=["banner", "raport", "json"])
    p.add_argument("--galaz", default="", help="gałąź (domyślnie bieżąca)")
    p.add_argument("--bramka", action="store_true",
                   help="kod wyjścia wg werdyktu (0 pokryte / 1 luka / 2 niezmierzone)")
    args = p.parse_args()

    werdykt = zbadaj(args.galaz)
    print(json.dumps(werdykt, ensure_ascii=False, indent=2) if args.tryb == "json"
          else banner(werdykt) if args.tryb == "banner" else raport(werdykt))
    sys.exit(werdykt["exit"] if args.bramka else 0)
