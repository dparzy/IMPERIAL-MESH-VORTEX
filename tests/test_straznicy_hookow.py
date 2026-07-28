"""Testy strażników hooków: CUSTOS LIMINIS (PreToolUse) i VIGIL (PostToolUse).

Powód powstania (zmierzone 2026-07-27): Imperium używało 2 z 31 zdarzeń hooka (liczba
zweryfikowana schematem konfiguracji, nie pamięcią — w Dzienniku stało błędne „~9"), a rozkaz
NIENARUSZALNY („Claude nigdy nie pushuje") przez 16 dni nie miał żadnego mechanizmu.
Łata z 07-27 (`permissions.deny`) zapina JEDNĄ powłokę z dwóch — reguły PowerShella to
osobna przestrzeń nazw, a PowerShell jest tu powłoką podstawową.

Testy pilnują OBU stron granicy: zakazane formy mają być zatrzymane, a codzienna praca
(`git status`, `git commit`, `git log --grep push`) ma iść bez tarcia. Strażnik, który
zatrzymuje niewinne polecenia, zostaje wyłączony przez człowieka i przestaje bronić czegokolwiek.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.pretorianie import custos_liminis as cl  # noqa: E402
from imperium.pretorianie import vigil as vg  # noqa: E402


def _cmd(polecenie: str, narzedzie: str = "Bash"):
    return cl.ocen(narzedzie, {"command": polecenie})


# ── CUSTOS LIMINIS — push we wszystkich formach ──────────────────────────────────

def test_push_zablokowany_w_formie_podstawowej():
    w = _cmd("git push origin claude/sleepy-fermi-dsdE4")
    assert w and w["permissionDecision"] == "deny"
    assert "NIENARUSZALNY" in w["permissionDecisionReason"]


def test_push_zablokowany_TAKZE_w_PowerShellu():
    """SEDNO LUKI: `permissions.deny` ma tylko regułę `Bash(...)`, a reguły PowerShella to
    osobna przestrzeń nazw — przy powłoce podstawowej PowerShell rozkaz był nieegzekwowany."""
    w = _cmd("git push origin main", narzedzie="PowerShell")
    assert w and w["permissionDecision"] == "deny"


def test_push_zablokowany_gdy_schowany_za_flaga_z_wartoscia():
    """`git -C /repo push` nie ma prefiksu `git push`, więc reguła wzorcowa go nie widzi —
    to jest ta szczelina, której hook ma pilnować (a nie polecenia złożone: te silnik
    uprawnień rozbija sam, co potwierdziła dokumentacja)."""
    for forma in ("git -C /inny/repo push", "git --git-dir=/x/.git push --force",
                  "git -c user.name=X push"):
        assert _cmd(forma), f"forma przepuszczona: {forma!r}"


def test_push_zablokowany_w_podpoleceniu_i_po_przypisaniu():
    assert _cmd("cd /repo && git push origin main")
    assert _cmd("git status; git push")
    assert _cmd("GIT_SSH_COMMAND=ssh git push")


def test_push_zablokowany_przy_pelnej_sciezce_do_gita():
    """Ścieżka ze spacją w cudzysłowie to na Windowsie forma codzienna — gołe `split()`
    rozbijało ją na `"C:\\Program` i przepuszczało push (złapane przy pisaniu testów)."""
    assert _cmd('"C:\\Program Files\\Git\\bin\\git.exe" push origin main')
    assert _cmd(r"C:\Git\bin\git.exe push")
    assert _cmd("/usr/bin/git push")


# ── CUSTOS LIMINIS — GRANICA: codzienna praca bez tarcia ─────────────────────────

def test_zwykle_polecenia_gita_przechodza_bez_slowa():
    for forma in ("git status --short", "git commit -m 'x'", "git log --oneline -5",
                  "git diff HEAD", "git add -A", "git fetch origin"):
        assert _cmd(forma) is None, f"fałszywe zatrzymanie: {forma!r}"


def test_slowo_push_w_argumencie_NIE_jest_pushem():
    """Fałszywy alarm uczy ignorowania strażnika — dlatego czytamy PODPOLECENIE gita,
    a nie samo wystąpienie słowa."""
    assert _cmd("git log --grep push") is None
    assert _cmd("git log --grep=push --oneline") is None
    assert _cmd("grep -rn 'git push' docs/") is None
    assert _cmd("echo git push") is None


def test_PROZA_cytujaca_push_po_separatorze_nie_jest_rozkazem():
    """WADA ZŁAPANA NA ŻYWO przy pierwszym zadziałaniu strażnika (2026-07-28).

    Wpis do Dziennika CYTOWAŁ obaloną tezę („deny nie złapie `cd x && git push`") w treści
    argumentu. Pierwsza wersja cięła surowy napis po separatorach PRZED uwzględnieniem
    cudzysłowów, więc proza stawała się „podpoleceniem" — strażnik zablokował opis własnej
    naprawy. Fałszywe zatrzymanie nie jest bezpieczną stroną błędu: uczy obchodzić strażnika.
    """
    assert _cmd("python -m dziennik wpis --co 'teza: cd x && git push nie zadziala'") is None
    assert _cmd('echo "przyklad: git status && git push origin main"') is None
    # GRANICA DRUGIEJ STRONY: prawdziwy `&&` POZA cudzysłowem nadal musi być widziany.
    assert _cmd("cd /repo && git push origin main"), "zawężenie zabiło prawdziwe wykrycie"


def test_niepowloke_narzedzia_ignorowane():
    assert cl.ocen("Read", {"file_path": "x.py"}) is None


# ── CUSTOS LIMINIS — archiwum: PYTANIE, nie blokada ──────────────────────────────

def test_zapis_do_archiwum_PYTA_zamiast_blokowac():
    """Konstytucja: archiwum otwiera się TYLKO na rozkaz Cezara — więc decyduje Cezar,
    a nie skrypt. `deny` zabierałoby mu tę decyzję, cisza oddawałaby ją mnie."""
    w = cl.ocen("Write", {"file_path": str(ROOT / "archiwum" / "stare.md")})
    assert w and w["permissionDecision"] == "ask"


def test_slowo_archiwum_w_NAZWIE_pliku_nie_wyzwala_pytania():
    """`archiwum` musi być SEGMENTEM ścieżki, nie fragmentem nazwy — inaczej każdy
    dokument o archiwizacji pytałby o zgodę."""
    assert cl.ocen("Write", {"file_path": "docs/ARCHIWIZACJA_zasady.md"}) is None
    assert cl.ocen("Edit", {"file_path": "docs/PAMIEC_SESJI_ARCHIWUM.md"}) is None


# ── VIGIL — skan po zapisie ──────────────────────────────────────────────────────

def test_vigil_ignoruje_pliki_nie_py(tmp_path):
    p = tmp_path / "notatka.md"
    p.write_text("tekst", encoding="utf-8")
    assert vg._plik_do_skanu({"file_path": str(p)}) is None


def _skan_i_stderr(wejscie: dict):
    """(wynik, stderr) — stderr przechwytujemy RĘCZNIE, nie fixture'em `capsys`.

    Runner Imperium (`tests/run_tests.py`) jest bezzależnościowy i zna tylko `tmp_path`,
    więc test z `capsys` przechodzi pod pytestem, a pod bramką pada na brakującym argumencie.
    Ta lekcja stoi już przy teście widoczności pominięć w `test_centrum_pamieci` — powtórzyłem
    ją mimo to, bo skopiowałem wzorzec z pytesta zamiast z sąsiedniego testu Imperium.
    Test ma bronić w OBU biegach; inaczej broni tylko tam, gdzie i tak patrzę.
    """
    import contextlib
    import io
    bufor = io.StringIO()
    with contextlib.redirect_stderr(bufor):
        wynik = vg._plik_do_skanu(wejscie)
    return wynik, bufor.getvalue()


def test_vigil_ignoruje_pliki_spoza_repo(tmp_path):
    """Cudzych plików nie recenzujemy — ale MÓWIMY, że ich nie zbadaliśmy.

    Pominięcie `.md` jest ciche (normalna praca); nieosiągalny `.py` nie — inaczej „nie
    sprawdziłem" wyglądałoby jak „sprawdziłem i jest czysto"."""
    p = tmp_path / "obcy.py"
    p.write_text("x = 1\n", encoding="utf-8")
    wynik, err = _skan_i_stderr({"file_path": str(p)})
    assert wynik is None
    assert "NIE ZBADANO" in err


def test_vigil_mowi_gdy_sciezki_py_nie_da_sie_znalezc():
    """Ścieżka POSIX z Git Basha na Windowsie nie rozwiązuje się do pliku — strażnik ma
    wtedy powiedzieć, że NIE ZBADAŁ, zamiast milczeć jak przy czystym pliku."""
    wynik, err = _skan_i_stderr({"file_path": "/c/nie/ma/takiego/pliku.py"})
    assert wynik is None
    assert "NIE ZBADANO" in err


def test_vigil_milczy_na_plikach_innego_rodzaju():
    """GRANICA: zapis dokumentu czy JSON-a nie jest pominięciem wartym alarmu."""
    wynik, err = _skan_i_stderr({"file_path": "docs/LOG_ZMIAN.md"})
    assert wynik is None
    assert err == ""


def test_vigil_bierze_zywy_plik_py_z_repo():
    cel = ROOT / "imperium" / "pretorianie" / "vigil.py"
    assert vg._plik_do_skanu({"file_path": str(cel)}) == cel


def test_vigil_milczy_na_czystym_pliku():
    """CISZA GDY ZIELONE: meldunek po każdym zapisie zamieniłby strażnika w tapetę."""
    assert vg.zbadaj(ROOT / "imperium" / "pretorianie" / "vigil.py") == []


def test_vigil_krzyczy_na_pliku_z_bledem(tmp_path):
    """Plik z realnym błędem ruffa (nieużywany import) musi dać zarzut — w repo, nie w tmp."""
    cel = ROOT / "_vigil_probka_tymczasowa.py"
    cel.write_text("import os\nx = 1\n", encoding="utf-8")
    try:
        zarzuty = vg.zbadaj(cel)
    finally:
        cel.unlink(missing_ok=True)
    assert any("ruff" in z for z in zarzuty), f"VIGIL przepuścił martwy import: {zarzuty}"
