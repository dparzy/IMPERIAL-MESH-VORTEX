"""Testy SILENTIUM — ciszy nad repozytorium na czas biegu bramki.

Trzy warstwy, bo organ ma trzy zupełnie różne rodzaje ryzyka:
  1. **Cykl życia blokady** — najgroźniejszy błąd to nie „nie zablokował", tylko
     „zamurował repo na zawsze". Każdy z trzech bezpieczników ma tu własny test.
  2. **Klasyfikacja ścieżek i komend** — granice, na których organ ma milczeć.
  3. **Kalibracja** — regresja wobec WERSJONOWANEJ prawdy podstawowej; bez tego
     przyrząd mógłby się pogorszyć po cichu przy dowolnej późniejszej zmianie.
"""
import io
import json
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.pretorianie import silentium as S  # noqa: E402


def _przekieruj(monkeypatch, tmp_path):
    """Blokada w tmp_path — test NIGDY nie dotyka produkcyjnego pliku blokady."""
    monkeypatch.setattr(S, "PLIK_BLOKADY", tmp_path / "silentium.lock")
    monkeypatch.delenv("SILENTIUM_OFF", raising=False)


# ── 1. CYKL ŻYCIA ────────────────────────────────────────────────────────────────
def test_zaloz_i_zdejmij(monkeypatch, tmp_path):
    _przekieruj(monkeypatch, tmp_path)
    assert not S.aktywna()
    b = S.zaloz("bramka testowa")
    assert S.aktywna() and S.stan().powod == "bramka testowa"
    assert S.zdejmij(b.zeton)
    assert not S.aktywna()


def test_druga_cisza_reczna_nie_przejmuje_pierwszej(monkeypatch, tmp_path):
    """Cisza RĘCZNA (CLI `zaloz`) jest wyłączna: druga dostaje wyjątek, NIE cudzy żeton.

    Wyłączność została tylko na drodze człowieka. Biegi bramki idą przez `cisza()` i
    współdzielą blokadę — patrz test niżej, zbudowany na zmierzonej wadzie z 2026-08-03.
    """
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("pierwszy")
    try:
        S.zaloz("drugi")
        assert False, "druga cisza ręczna powinna była odmówić"
    except RuntimeError as e:
        assert "już trwa" in str(e)


def test_drugi_bieg_dolacza_zamiast_zostac_bez_ochrony(monkeypatch, tmp_path):
    """REGRESJA na wadę ZMIERZONĄ 2026-08-03 (dwie sesje o 10:03, dowód w plikach hooka).

    Pierwsza wersja organu odmawiała drugiemu biegowi i pisała „bieg idzie BEZ ochrony" —
    NIEPRAWDĘ, bo repo było chronione cudzą ciszą. Komunikat kłamiący o stanie ochrony
    uczy ignorować alarm, czyli zabija strażnika skuteczniej niż brak strażnika.
    """
    _przekieruj(monkeypatch, tmp_path)
    # Przechwytywanie stdout RĘCZNIE, nie fixture `capsys`: bramką Imperium jest własny
    # `tests/run_tests.py` (stdlib, bez pytest), który fixtur nie wstrzykuje. Test pisany
    # pod samo pytest przechodził u mnie i padał na bramce — zmierzone w tej wachcie.
    bufor = io.StringIO()
    with redirect_stdout(bufor):
        with S.cisza("bramka: testy"):
            with S.cisza("bramka: audyt"):
                assert len(S.uczestnicy()) == 2, "oba biegi mają być zapisane jako uczestnicy"
    wydruk = bufor.getvalue()
    assert "BEZ ochrony" not in wydruk, "trwająca cisza to ochrona, nie jej brak"
    assert "DOŁĄCZAM" in wydruk


def test_wyjscie_pierwszego_nie_zdejmuje_ciszy_drugiemu(monkeypatch, tmp_path):
    """DRUGA połowa tej samej wady: pierwszy bieg kończył się i otwierał repo w środku
    cudzej, wciąż trwającej bramki. Cisza ma trwać, dopóki nie wyjdzie OSTATNI."""
    _przekieruj(monkeypatch, tmp_path)
    pierwszy, ilu = S.dolacz("bramka: testy")
    assert ilu == 1
    drugi, ilu = S.dolacz("bramka: audyt")
    assert ilu == 2

    assert S.zdejmij(pierwszy.zeton)
    assert S.aktywna(), "drugi bieg wciąż trwa — repo musi zostać zamknięte"
    assert S.stan().powod == "bramka: audyt"

    assert S.zdejmij(drugi.zeton)
    assert not S.aktywna(), "po wyjściu ostatniego cisza znika"
    assert not S.PLIK_BLOKADY.exists()


def test_martwy_uczestnik_nie_zdejmuje_ciszy_zywemu(monkeypatch, tmp_path):
    """GRANICA sprzątania: zgasły PID znika z listy, ale cisza żywego biegu zostaje.

    Bez tego bezpiecznik „martwy PID zwalnia repo" stałby się dziurą: jeden padnięty
    bieg otwierałby repo w środku drugiego, który ma się dobrze.
    """
    _przekieruj(monkeypatch, tmp_path)
    # Podmiana PRZED dołączeniem, nie po: `dolacz` sam odsiewa martwych, więc przy
    # prawdziwym `proces_zyje` sztuczny pid=1 wypadłby już w chwili dopisywania trupa
    # i test badałby pustą listę zamiast granicy, o którą pyta.
    monkeypatch.setattr(S, "proces_zyje", lambda pid: pid == 1)
    zywy, _ = S.dolacz("bramka żywa", pid=1)
    trup, _ = S.dolacz("bramka, która padła", pid=999_999_999)

    zywi = S.uczestnicy()
    assert [b.zeton for b in zywi] == [zywy.zeton], "martwy wypada, żywy zostaje"
    assert S.aktywna()
    assert trup.zeton not in S.PLIK_BLOKADY.read_text(encoding="utf-8")


def test_stary_format_pliku_wciaz_czytany(monkeypatch, tmp_path):
    """Plik zapisany przed ciszą współdzieloną (pojedynczy obiekt) nadal obowiązuje.

    Blokada bywa na dysku w chwili wgrania nowej wersji — gdyby nowy kod jej nie rozumiał,
    trwająca bramka zostałaby bezgłośnie odsłonięta.
    """
    _przekieruj(monkeypatch, tmp_path)
    S.PLIK_BLOKADY.write_text(json.dumps({
        "zeton": "stary123", "pid": 0, "powod": "bieg sprzed zmiany",
        "zalozona": "2026-08-03T10:03:00", "zalozona_ts": S.time.time(), "ttl_s": 600,
    }), encoding="utf-8")
    b = S.stan()
    assert b is not None and b.powod == "bieg sprzed zmiany"


def test_pliki_pomocnicze_ciszy_nie_sa_zapisem_do_repo(monkeypatch, tmp_path):
    """Strażnik nie może blokować własnego zamka — dopisanie uczestnika JEST zapisem.

    Gdyby `.mx` liczyło się jako zapis do repo, hook zablokowałby operację, przez którą
    sam działa: organ udusiłby się własną regułą.

    ŚWIADOMIE bez `_przekieruj`: pytanie brzmi „czy ta ścieżka leży w repo", więc badana
    ścieżka musi być PRODUKCYJNA. Na `tmp_path` test przeszedłby zawsze — z powodu
    położenia poza drzewem, nie z powodu reguły, której pilnuje.
    """
    for rozszerzenie in ("", ".mx", ".12345.tmp"):
        assert not S._w_repo(str(S.PLIK_BLOKADY) + rozszerzenie)
    assert S._w_repo(str(S.PLIK_BLOKADY.parent / "inny_plik.json")), \
        "sąsiad w tym samym katalogu MA być chroniony — zwolnienie dotyczy plików ciszy"


def test_cudzego_zetonu_nie_zdejmiesz(monkeypatch, tmp_path):
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("cudzy bieg")
    assert not S.zdejmij("nieswoj-zeton")
    assert S.aktywna()
    assert S.zdejmij(sila=True)          # furtka awaryjna działa zawsze


def test_bezpiecznik_1_martwy_pid_zwalnia_repo(monkeypatch, tmp_path):
    """GRANICA: proces bramki zniknął → cisza NIE obowiązuje i plik znika.

    Bez tego każdy crash testów zamurowywałby repozytorium do ręcznej interwencji.
    """
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("bieg, który padnie", pid=999_999_999)
    monkeypatch.setattr(S, "proces_zyje", lambda pid: False)
    assert S.stan() is None
    assert not S.PLIK_BLOKADY.exists(), "martwa blokada ma być posprzątana, nie tylko zignorowana"


def test_bezpiecznik_2_ttl_granica(monkeypatch, tmp_path):
    """GRANICA TTL: równo na progu jeszcze cisza, sekundę po progu już nie.

    ZEGAR ZAMROŻONY, nie ścienny — pierwsza wersja tego testu odejmowała TTL od
    `time.time()` i oblewała, bo między zapisem a odczytem mijały mikrosekundy. Test
    granicy mierzony ruchomą miarką bada dryf zegara, a nie próg, którego pilnuje.
    """
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("bieg z TTL", ttl_s=100)
    dane = json.loads(S.PLIK_BLOKADY.read_text(encoding="utf-8"))
    monkeypatch.setattr(S.time, "time", lambda: 1000.0)

    dane["uczestnicy"][0]["zalozona_ts"] = 900.0     # wiek == TTL → jeszcze w środku
    S.PLIK_BLOKADY.write_text(json.dumps(dane), encoding="utf-8")
    assert S.stan() is not None, "na samym progu TTL cisza jeszcze obowiązuje"

    dane["uczestnicy"][0]["zalozona_ts"] = 899.0     # wiek > TTL → wygasła
    S.PLIK_BLOKADY.write_text(json.dumps(dane), encoding="utf-8")
    assert S.stan() is None, "sekundę po TTL cisza musi wygasnąć sama"


def test_bezpiecznik_3_wylacznik_srodowiskowy(monkeypatch, tmp_path):
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("bieg")
    monkeypatch.setenv("SILENTIUM_OFF", "1")
    assert S.stan() is None and not S.aktywna()


def test_uszkodzona_blokada_nie_blokuje(monkeypatch, tmp_path):
    """Pół-zapisany JSON to awaria, nie rozkaz ciszy — inaczej jeden bajt murowałby repo."""
    _przekieruj(monkeypatch, tmp_path)
    S.PLIK_BLOKADY.write_text('{"zeton": "urwan', encoding="utf-8")
    assert S.stan() is None


def test_menedzer_kontekstu_zdejmuje_po_wyjatku(monkeypatch, tmp_path):
    """Bramka wywalona wyjątkiem MUSI oddać repo — `finally`, nie „jak się uda"."""
    _przekieruj(monkeypatch, tmp_path)
    try:
        with S.cisza("bramka, która padnie"):
            assert S.aktywna()
            raise ValueError("padło w środku biegu")
    except ValueError:
        pass
    assert not S.aktywna()


def test_proces_zyje_nie_zabija_wlasnego_procesu():
    """Badanie żywotności NIE MOŻE zabijać — na Windowsie `os.kill(pid,0)` to TerminateProcess.

    Test jest tautologiczny tylko z pozoru: gdyby implementacja użyła `os.kill`, ten proces
    testowy zginąłby w tej linii i pakiet nigdy by się nie skończył.
    """
    assert S.proces_zyje(os.getpid()) is True
    assert S.proces_zyje(-1) is False


# ── 2. KLASYFIKACJA ──────────────────────────────────────────────────────────────
def test_sciezki_w_repo_i_poza():
    assert S._w_repo("imperium/legiony/rejestr.py")
    assert S._w_repo(str(S.KORZEN / "docs" / "LOG_ZMIAN.md"))
    assert not S._w_repo("raporty/wykres.png")            # katalog ignorowany
    assert not S._w_repo("$TEMP/wynik.txt")               # nierozwinięta zmienna
    assert not S._w_repo("/tmp/msg.txt")                  # ścieżka POSIX-owa
    assert not S._w_repo(r"C:\Users\Ian\AppData\Local\Temp\x.txt")
    assert not S._w_repo(str(S.PLIK_BLOKADY))             # sam plik blokady


def test_komendy_piszace_rozpoznane():
    assert S.komenda_pisze("git add -A && git commit -m 'x'")
    assert S.komenda_pisze("cd /c/Projekty/imperial-mesh-vortex\ngit add docs/LOG_ZMIAN.md")
    assert S.komenda_pisze("echo x > docs/LOG_ZMIAN.md")
    assert S.komenda_pisze("python -m imperium.biblioteki.dziennik_niesmiertelny wpis --co 'x'")
    assert S.komenda_pisze("python tests/run_tests.py 2>&1 | tail -3")
    assert S.komenda_pisze("rm imperium/legiony/rejestr.py")


def test_komendy_czytajace_przepuszczone():
    """GRANICA: strażnik blokujący ODCZYT zmusiłby do bezczynnego czekania."""
    assert not S.komenda_pisze("git status --short")
    assert not S.komenda_pisze("git fetch origin main; git rev-parse HEAD")
    assert not S.komenda_pisze("grep -rn 'wpis' docs/ | head")
    assert not S.komenda_pisze("python -m pytest tests/test_silentium.py -q")
    assert not S.komenda_pisze("python narzedzia/audyt_spojnosci.py")
    assert not S.komenda_pisze("echo x > $TEMP/wynik.txt")
    assert not S.komenda_pisze("cat docs/LOG_ZMIAN.md")


def test_proza_nie_jest_skladnia():
    """Treść w cudzysłowie to DANE. Klasa złapana na żywo 2026-07-28 w CUSTOS LIMINIS."""
    assert not S.komenda_pisze(
        "python -m imperium.biblioteki.breviarium --delta "
        "--notatka 'przed commitem trzeba git add, ale tu tylko o tym piszę'")


def test_cialo_heredoca_to_dane_nie_polecenia():
    czytajacy = ("python - <<'PY'\n"
                 "from pathlib import Path\n"
                 "print(Path('dane/x.csv').read_text())\n"
                 "PY")
    assert not S.komenda_pisze(czytajacy)
    piszacy = ("python - <<'PY'\n"
               "from pathlib import Path\n"
               "Path('docs/LOG_ZMIAN.md').write_text('nowa tresc')\n"
               "PY")
    assert S.komenda_pisze(piszacy)


def test_zapis_heredoca_poza_repo_jest_wolny():
    """GRANICA: ten sam prymityw zapisu — decyduje CEL, nie sama czynność."""
    poza = ("python - <<'PY'\n"
            "from pathlib import Path\n"
            "out = Path(r'C:\\Users\\Ian\\AppData\\Local\\Temp\\raport.txt')\n"
            "out.write_text('x')\n"
            "PY")
    assert not S.komenda_pisze(poza)


# ── 3. WERDYKT HOOKA ─────────────────────────────────────────────────────────────
def test_hook_milczy_bez_ciszy(monkeypatch, tmp_path):
    _przekieruj(monkeypatch, tmp_path)
    assert S.ocen("Write", {"file_path": "docs/LOG_ZMIAN.md"}) is None


def test_hook_blokuje_zapis_w_ciszy(monkeypatch, tmp_path):
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("bramka")
    w = S.ocen("Write", {"file_path": "docs/LOG_ZMIAN.md"})
    assert w and w["permissionDecision"] == "deny"
    assert "zdejmij --sila" in w["permissionDecisionReason"], "werdykt musi podać furtkę"
    assert S.ocen("Write", {"file_path": r"C:\Users\Ian\AppData\Local\Temp\x.md"}) is None
    assert S.ocen("Read", {"file_path": "docs/LOG_ZMIAN.md"}) is None


def test_hook_zwraca_czysty_ascii(monkeypatch, tmp_path, capsys=None):
    """Protokół hooka musi przejść przez konsolę cp1250 — inaczej bariera ginie na emoji."""
    _przekieruj(monkeypatch, tmp_path)
    S.zaloz("bramka")
    w = S.ocen("Bash", {"command": "git add -A"})
    ładunek = json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **w}})
    ładunek.encode("ascii")               # rzuciłoby UnicodeEncodeError przy złym ensure_ascii


# ── 4. KALIBRACJA (regresja na prawdzie podstawowej) ─────────────────────────────
def test_kalibracja_na_realnych_komendach():
    """Klasyfikator nie ma prawa cicho zgnić poniżej ZMIERZONEGO poziomu.

    Progi są ustawione lekko poniżej wyniku z dnia kalibracji (precyzja 93.5%,
    czułość ważona populacją 98.3%), żeby test łapał REGRESJĘ, a nie szum jednej komendy.
    """
    sys.path.insert(0, str(S.KORZEN / "narzedzia"))
    from kalibracja_silentium import raport

    w = raport()
    assert w["n"] >= 100, "prawda podstawowa musi zostać w repo (co najmniej 100 etykiet)"
    assert w["precyzja"] >= 0.90, f"precyzja spadła do {w['precyzja']:.1%} (kalibracja: 93.5%)"
    assert w["czulosc"] >= 0.90, f"czułość spadła do {w['czulosc']:.1%} (kalibracja: 97.7%)"


def test_sciezka_windows_pod_posixem_nie_jest_nasza(monkeypatch):
    """LUSTRO reguły POSIX-owej: ścieżka z literą dysku oglądana spod Linuksa NIE jest repo.

    ZMIERZONA WADA (2026-08-06, PIERWSZY bieg VALLUM na ubuntu-latest): organ obsługiwał
    tylko JEDEN kierunek przenośności. Pod POSIX-em ścieżka windowsowa nie jest absolutna,
    więc `Path` doklejał ją do korzenia repozytorium i strażnik pilnował windowsowego
    katalogu tymczasowego jak własnego drzewa — cztery testy ciszy padły, a kalibracja
    spadła z 93,5% na 89,6% precyzji. Asymetria widoczna WYŁĄCZNIE poza maszyną autora.

    Test udaje `os.name`, więc bada OBA systemy niezależnie od tego, gdzie biegnie —
    inaczej sam byłby strażnikiem działającym na jednej maszynie, czyli powielałby
    dokładnie tę wadę, którą ma łapać.
    """
    B = chr(92)   # backslash budowany jawnie — literał w cudzysłowie zbyt łatwo zgubić
    windowsowa = "C:" + B + "Users" + B + "Ian" + B + "AppData" + B + "Local" + B + "Temp" + B + "x.md"
    unc = B + B + "serwer" + B + "udzial" + B + "plik.md"

    monkeypatch.setattr(S.os, "name", "posix")
    assert S._obca_sciezka_windows(windowsowa) is True, "windowsowy temp pod POSIX-em to NIE nasze repo"
    assert S._obca_sciezka_windows("c:/users/ian/temp/x.md") is True, "mała litera i ukośniki też"
    assert S._obca_sciezka_windows(unc) is True, "UNC (dwa backslashe) również nie jest nasz"
    assert S._obca_sciezka_windows("docs/LOG_ZMIAN.md") is False, "nasz plik względny zostaje nasz"
    assert S._obca_sciezka_windows("/tmp/x.md") is False, "ścieżkę POSIX-ową obsługuje osobna reguła"
    assert S._w_repo(windowsowa) is False, "strażnik nie może pilnować cudzego katalogu tymczasowego"

    # GRANICA W DRUGĄ STRONĘ — tu leży realne ryzyko tej naprawy: gdyby reguła odezwała
    # się pod Windowsem, uznałaby WŁASNE repo Cezara (C:\...) za obce i rozbroiła
    # strażnika na jedynej maszynie, na której on naprawdę pracuje.
    monkeypatch.setattr(S.os, "name", "nt")
    assert S._obca_sciezka_windows(windowsowa) is False, "pod Windowsem reguła MUSI milczeć"
    assert S._obca_sciezka_windows(unc) is False, "pod Windowsem UNC też nie jest obcy z tego powodu"

