"""Testy EXACTORA — organ egzekwujący meldunek końcowy wobec checklisty CLAUSURY.

Prawda podstawowa pochodzi z KRONIKI (190 historycznych meldunków, 144 sesje) — tu
utrwalone są przypadki GRANICZNE, w tym dosłowne bloki z noty N-b74ce133, która zrodziła
ten organ, oraz dwie fałszywki, na których wyłożyła się pierwsza (fence'owa) reguła.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.pretorianie import exactor  # noqa: E402

KORZEN = Path(__file__).resolve().parent.parent
GALAZ = "claude/sleepy-fermi-dsdE4"

# Kroki-atrapa: zawierają wszystkie kotwice, więc testy rdzenia nie zależą od CLAUDE.md.
KROKI = [
    "1. **Bramka Prawo XXI:** `python tests/run_tests.py` (X/X zielone) + audyt (exit 0).",
    "4b. **BREVIARIUM — meldunek SŁUG na domknięcie**: `--delta` HYGINUSA i TIRO.",
    "5. **Prawo XV:** odpowiedz Cezarowi na pytanie o utratę potencjału — JAWNIE.",
    "6. **Dziennik Nieśmiertelny:** `python -m imperium.biblioteki.dziennik_niesmiertelny wpis`.",
    "8. **Push dla Cezara:** podaj pełny blok PowerShell (`cd` + `git push origin <branch>`).",
    "9. **Alarmy hooka = ZADANIA**: jawnie rozstrzygnij — nigdy milczeniem.",
]

MELDUNEK_PELNY = f"""## Wachta domknięta
Prawo XV: brak utraty potencjału — wszystkie organy wpięte.
BREVIARIUM: Hyginus 44 cząstki (bez zmian), TIRO 433 pary (+0).

```powershell
cd C:\\Projekty\\imperial-mesh-vortex; git push origin {GALAZ}
```
"""


def _zbadaj(tekst, **kw):
    kw.setdefault("galaz", GALAZ)
    return exactor.zbadaj_meldunek(tekst, kroki=KROKI, **kw)


# ── GRANICA 1: dosłowny grzech z noty N-b74ce133 ─────────────────────────────────

def test_goly_git_push_jest_lapany():
    """Dosłowny blok z noty: ```powershell\\ngit push\\n``` — sam push, bez cd i origin."""
    w = _zbadaj("Skrót do push:\n\n```powershell\ngit push\n```\n")
    assert w["status"] == "niespelniony", w
    assert w["exit"] == 1
    braki = {b["id"] for b in w["braki"]}
    assert "push_pelny_blok" in braki
    powod = next(b["powod"] for b in w["braki"] if b["id"] == "push_pelny_blok")
    assert "origin" in powod and "cd" in powod


def test_push_z_petla_retry_tez_jest_lapany():
    """Druga postać grzechu — pętla retry nadal nie jest blokiem gotowym do wklejenia."""
    w = _zbadaj('```powershell\ngit push\nfor ($i=1; $i -le 8; $i++) { git push }\n```')
    assert w["status"] == "niespelniony"
    assert any(b["id"] == "push_pelny_blok" for b in w["braki"])


def test_origin_bez_cd_jest_lapany():
    """Granica: origin JEST, `cd` NIE — meldunek nadal nie jest gotowy do wklejenia."""
    w = _zbadaj(f"## Gotowe do push\n\n```powershell\ngit push origin {GALAZ}\n```")
    assert w["status"] == "niespelniony"
    powod = next(b["powod"] for b in w["braki"] if b["id"] == "push_pelny_blok")
    assert "cd" in powod and "origin" not in powod


def test_pelny_blok_przechodzi():
    w = _zbadaj(f"```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin {GALAZ}\n```")
    assert w["status"] == "spelniony", w
    assert w["exit"] == 0
    assert w["poziom"] == "push"


def test_cd_w_osobnej_linii_tez_przechodzi():
    """Granica: `cd` i push w DWÓCH liniach — to nadal pełny blok."""
    w = _zbadaj(f"```powershell\ncd C:\\Projekty\\imperial-mesh-vortex\ngit push origin {GALAZ}\n```")
    assert w["status"] == "spelniony", w


def test_cudza_galaz_jest_lapana():
    """Blok wskazujący INNĄ gałąź niż bieżąca wypchnąłby nie to, co trzeba."""
    w = _zbadaj("```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin main\n```")
    assert w["status"] == "niespelniony"
    powod = next(b["powod"] for b in w["braki"] if b["id"] == "push_pelny_blok")
    assert "main" in powod and GALAZ in powod


def test_brak_galezi_w_kontekscie_nie_wywraca_werdyktu():
    """Granica: gdy nie znamy gałęzi bieżącej (brak gita), nie zmyślamy niezgodności."""
    w = _zbadaj("```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin main\n```",
                galaz="")
    assert w["status"] == "spelniony", w


# ── GRANICA 2: fałszywki, na których wyłożyła się reguła fence'owa ────────────────

def test_wzmianka_o_pushu_w_prozie_nie_jest_przekazaniem():
    """Cytowanie rozkazu to nie przekazanie komendy (kronika 198ed555#88)."""
    w = _zbadaj("CLAUDE.md krok 8 mówi wprost *„podaj pełny blok PowerShell "
                "(`cd` + `git push origin <branch>`)\"* — i miałeś rację.")
    assert w["status"] == "nie_dotyczy", w
    assert w["poziom"] == "brak"


def test_json_uprawnien_nie_jest_przekazaniem():
    """Fałszywka reguły fence'owej: `git push` wewnątrz konfiguracji deny (eecde318#88)."""
    w = _zbadaj('```json\n"permissions": {\n  "deny": ["Bash(git push:*)"]\n}\n```')
    assert w["status"] == "nie_dotyczy", w


def test_push_w_srodku_zdania_nie_jest_przekazaniem():
    """Fałszywka: instrukcja prozą „…commit z opisem, git push." (895ce14f#699)."""
    w = _zbadaj("Wykonaj: git add -A, commit z opisem, git push. Potwierdź working tree clean.")
    assert w["status"] == "nie_dotyczy", w


def test_cytat_inline_z_separatorem_nie_jest_przekazaniem():
    """Fałszywka złapana POMIAREM na korpusie (ea3446fd#64): proza cytuje `cd x && git push`
    jako przykład składni — separator stawia push na pozycji polecenia, a to nadal cytat."""
    w = _zbadaj("Dokumentacja mówi, że separatory to `&&`, `||`, `;` — czyli "
                "`cd x && git push` **jest** rozbijane na podpolecenia.")
    assert w["status"] == "nie_dotyczy", w


def test_cytat_inline_obok_prawdziwego_bloku_nie_zaslania_bloku():
    """Granica odwrotna: usuwanie cytatów NIE może zjeść prawdziwego przekazania."""
    w = _zbadaj("Wcześniej pisałem `git push` błędnie. Poprawny blok:\n\n"
                f"```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin {GALAZ}\n```")
    assert w["status"] == "spelniony", w


# ── GRANICA 3: dwa poziomy (pomiar 105 przekazań vs 4 domknięcia) ────────────────

def test_przekazanie_pushu_nie_wymaga_powinnosci_domknieciowych():
    """Push w ŚRODKU wachty nie jest domknięciem — Prawo XV i Dziennik go nie dotyczą."""
    w = _zbadaj(f"```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin {GALAZ}\n```")
    assert w["status"] == "spelniony"
    assert w["spelnione"] == ["push_pelny_blok"]


def test_domkniecie_wymaga_pelnej_checklisty():
    w = _zbadaj(f"```powershell\ncd C:\\Projekty\\imperial-mesh-vortex; git push origin {GALAZ}\n```",
                tryb="domkniecie")
    assert w["status"] == "niespelniony", w
    braki = {b["id"] for b in w["braki"]}
    assert {"prawo_xv", "meldunek_slug"} <= braki


def test_powinnosc_warunkowa_nie_jest_sprawdzana_ale_jest_widoczna():
    """Krok 9 (alarmy hooka) obowiązuje tylko, gdy alarm padł — organ tego nie zgaduje,
    ale MUSI pokazać, że nie pilnuje (lekcja „bramka o wąskim zasięgu")."""
    w = _zbadaj(MELDUNEK_PELNY, tryb="domkniecie")
    assert "alarmy" not in " ".join(b["id"] for b in w["braki"])
    assert any(k.lstrip().startswith("9.") for k in w["niepokryte"]), w["niepokryte"]


def test_kroki_wykonawcze_nie_sa_powinnoscia_meldunku():
    """Krok 1/6 każe WYKONAĆ pracę, nie przepisać ją do meldunku — pilnują ich bramka
    i audyt. Zmierzone: bez tego kryterium organ dawał 80% alarmów na domknięciach."""
    ids = {p.id for p in exactor.REJESTR}
    assert "bramka_liczbami" not in ids and "dziennik" not in ids and "dlug_honorowy" not in ids


def test_pelny_meldunek_domkniecia_przechodzi():
    w = _zbadaj(MELDUNEK_PELNY, tryb="domkniecie")
    assert w["status"] == "spelniony", w
    assert w["poziom"] == "domkniecie"
    assert len(w["spelnione"]) == len(exactor.REJESTR)


def test_deklaracja_domkniecia_w_tekscie_podnosi_poziom():
    """Gdy meldunek SAM mówi, że domyka wachtę, poziom rośnie bez flagi."""
    w = _zbadaj("Wachta domknięta — reszta jutro.")
    assert w["poziom"] == "domkniecie"
    assert w["status"] == "niespelniony"


def test_milczenie_o_prawie_xv_jest_lapane():
    """Krok 5 mówi wprost „odpowiedz Cezarowi… JAWNIE, nie milczeniem"."""
    w = _zbadaj("Wachta domknięta. BREVIARIUM: Hyginus bez zmian, TIRO +0.", tryb="domkniecie")
    assert {b["id"] for b in w["braki"]} == {"prawo_xv"}, w


# ── GRANICA 4: gnicie kotwic (żelazna zasada SIGILLARIUM) ────────────────────────

def test_kotwica_osierocona_podnosi_alarm_zamiast_cicho_pilnowac():
    """Gdy rozkaz zmieni brzmienie, organ ma KRZYCZEĆ, nie udawać, że wszystko gra."""
    kroki_bez_kroku8 = [k for k in KROKI if "pełny blok PowerShell" not in k]
    w = exactor.zbadaj_meldunek("```powershell\ngit push\n```",
                                kroki=kroki_bez_kroku8, galaz=GALAZ)
    assert w["status"] == "kotwica_osierocona", w
    assert w["exit"] == 2
    assert "push_pelny_blok" in w["osierocone"]


def test_kotwice_zyja_w_zywej_konstytucji():
    """Każda kotwica MUSI znaleźć swoją frazę w prawdziwym CLAUDE.md § KONIEC SESJI."""
    tresc = "\n".join(exactor.kroki_clausury()).lower()
    osierocone = [p.id for p in exactor.REJESTR if p.kotwica.lower() not in tresc]
    assert not osierocone, f"kotwice bez pokrycia w KONSTYTUCJI: {osierocone}"


def test_zasieg_bramki_jest_jawny():
    """Lekcja „bramka o wąskim zasięgu": kroki niesprawdzane mają być WIDOCZNE."""
    w = _zbadaj("```powershell\ngit push\n```")
    assert isinstance(w["niepokryte"], list)


# ── GRANICA 5: uodpornienie — organ sam podaje blok ─────────────────────────────

def test_blok_push_jest_gotowy_do_wklejenia():
    blok = exactor.blok_push(galaz=GALAZ, korzen=Path("C:/Projekty/imperial-mesh-vortex"))
    assert blok.startswith("cd ")
    assert f"git push origin {GALAZ}" in blok


def test_wlasny_blok_przechodzi_wlasne_sprawdzenie():
    """Niezmiennik: to, co organ podaje, MUSI przejść to, czego organ wymaga."""
    blok = exactor.blok_push(galaz=GALAZ, korzen=Path("C:/Projekty/imperial-mesh-vortex"))
    w = _zbadaj(f"```powershell\n{blok}\n```")
    assert w["status"] == "spelniony", w


# ── GRANICA 6: CLI ──────────────────────────────────────────────────────────────

def test_cli_bramka_zwraca_kod_wyjscia(tmp_path):
    plik = tmp_path / "meldunek.md"
    plik.write_text("```powershell\ngit push\n```", encoding="utf-8")
    p = subprocess.run([sys.executable, "-m", "imperium.pretorianie.exactor",
                        "--plik", str(plik), "--bramka"],
                       cwd=KORZEN, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=90)
    assert p.returncode == 1, p.stdout + p.stderr
    assert "EXACTOR" in p.stdout


def test_cli_bez_zrodla_nie_zgaduje():
    """Organ nie wymyśla, co jest meldunkiem — brak --plik/--stdin to błąd użycia."""
    p = subprocess.run([sys.executable, "-m", "imperium.pretorianie.exactor"],
                       cwd=KORZEN, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=90)
    assert p.returncode != 0
    assert "--plik" in (p.stderr + p.stdout)
