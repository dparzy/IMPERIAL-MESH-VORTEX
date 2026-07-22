"""Testy CENSUS ORGANORUM (W17) + typu POMIAR w ledgerze — CORONY sesji doks20.

Reguła Test-Granic: bramka bez testu granicy to martwa asercja. Tu granicą jest
moduł, który POWSTAŁ i nie zameldował się — dokładnie przypadek `dispensator.py`,
który przeżył całą sesję niewidzialny (NOTA N-9992ba7b).

STYL (lekcja własna, 2026-07-20): funkcje modułowe `test_*`, NIE `unittest.TestCase`.
Runner Imperium zbiera tylko funkcje modułowe, a strażnik silent-skip w `run_tests.py`
zgłasza plik testowy bez nich jako błąd — złapał ten plik w pierwszym biegu, czyli
zadziałał przeciwko własnemu autorowi (dokładnie po to powstał).
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Wyłącznie przez pakiet `narzedzia` — import po wstrzyknięciu katalogu do sys.path
# dałby DRUGĄ kopię modułu z osobnym stanem, więc patch w teście nie dotyczyłby tego
# modułu, którego używa audyt (podwójna tożsamość modułu).
from narzedzia import census_organorum as census  # noqa: E402
from narzedzia.scriba_codex import zapisz_pomiar  # noqa: E402


def _tmp_ledger() -> Path:
    return Path(tempfile.mkdtemp()) / "ledger.jsonl"


# ── CENSUS ORGANORUM (Warstwa 17) ────────────────────────────────────────────

def test_zywy_kod_zgodny_z_dokumentem():
    """Stan repo: cenzus na dysku == cenzus z żywego kodu (bramka zielona)."""
    assert census.sprawdz() == [], "CENSUS_ORGANORUM rozjechany z kodem — uruchom --zapisz"


def test_wykrywa_modul_bez_meldunku():
    """GRANICA: moduł jest w kodzie, nie ma go w spisie → wykrywalne (cały sens W17)."""
    spis = census.spisz_moduly()
    katalog = "imperium/cesarz"
    assert katalog in spis, "spodziewany katalog organu nie istnieje"

    # Symulacja „moduł powstał po wygenerowaniu spisu" — czyli przypadek dispensatora.
    okrojony = dict(spis)
    usuniety = spis[katalog][0][0]
    okrojony[katalog] = okrojony[katalog][1:]

    odczyt = census._parsuj_sekcje(census.sekcja_md(okrojony))
    spisane = {f"{k}/{n}" for k, w in odczyt.items() for n, _ in w}
    assert f"{katalog}/{usuniety}" not in spisane
    assert f"`{usuniety}`" in census.sekcja_md(spis), "pełny spis musi go zawierać"


def test_wykrywa_widmo_w_spisie():
    """GRANICA odwrotna: moduł skasowany z kodu, wciąż w spisie → też błąd."""
    spis = census.spisz_moduly()
    spis.setdefault("imperium/cesarz", []).append(("nieistniejacy_widmo.py", "widmo"))
    odczyt = census._parsuj_sekcje(census.sekcja_md(spis))
    spisane = {f"{k}/{n}" for k, w in odczyt.items() for n, _ in w}
    zywe = {f"{k}/{n}" for k, w in census.spisz_moduly().items() for n, _ in w}
    assert spisane - zywe, "widmo w spisie musi być wykrywalne"


def test_brak_dokumentu_to_blad_nie_cisza():
    """GRANICA: brak pliku spisu = błąd, nie milczące „wszystko gra"."""
    prawdziwy = census.DOKUMENT
    try:
        census.DOKUMENT = os.path.join(tempfile.gettempdir(), "_nie_ma_takiego_.md")
        bledy = census.sprawdz()
        assert bledy and "W17" in bledy[0]
    finally:
        census.DOKUMENT = prawdziwy


def test_kazdy_modul_ma_docstring():
    """Prawo XV: moduł bez docstringu nie umie powiedzieć, po co istnieje."""
    nieme = [f"{k}/{n}" for k, w in census.spisz_moduly().items()
             for n, rola in w if rola.startswith("⚠️ BRAK DOCSTRINGU")]
    assert nieme == [], f"moduły bez docstringu: {nieme}"


def test_parsowanie_jest_odwrotnoscia_generowania():
    """Round-trip: sekcja → parser → ten sam komplet modułów (inaczej bramka kłamie)."""
    spis = census.spisz_moduly()
    odczyt = census._parsuj_sekcje(census.sekcja_md(spis))
    assert ({f"{k}/{n}" for k, w in spis.items() for n, _ in w}
            == {f"{k}/{n}" for k, w in odczyt.items() for n, _ in w})


def test_rola_bez_pipe_nie_rozwala_tabeli():
    """Docstring z `|` rozwaliłby komórkę Markdown — musi być neutralizowany."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write('"""Rola z | pionem w środku."""\n')
        sciezka = f.name
    try:
        assert "|" not in census._rola_modulu(sciezka)
    finally:
        os.unlink(sciezka)


# ── Typ POMIAR w ledgerze (CORONA za notę N-a0b792e1) ────────────────────────

def test_zapisuje_wielowariantowy_pomiar():
    p = _tmp_ledger()
    assert zapisz_pomiar(temat="interwaly", pytanie="ktory interwal", metryka="ROI %",
                         warianty={"4h": 3.26, "1H": -3.37}, werdykt="4H_LEPSZY",
                         zrodlo="test", sciezka=p)
    rek = json.loads(p.read_text(encoding="utf-8").strip())
    assert rek["typ"] == "POMIAR"
    assert rek["warianty"] == {"1H": -3.37, "4h": 3.26}


def test_pusty_zestaw_wariantow_to_blad():
    """GRANICA: pomiar bez wariantów nie ma czego porównać (Prawo I)."""
    try:
        zapisz_pomiar(temat="x", pytanie="y", metryka="z", warianty={},
                      werdykt="w", zrodlo="test", sciezka=_tmp_ledger())
    except ValueError:
        return
    raise AssertionError("pusty zestaw wariantów musi podnieść ValueError")


def test_idempotencja_ten_sam_pomiar():
    """Ten sam pomiar tego samego dnia nie mnoży linii (jak AB/IC)."""
    p = _tmp_ledger()
    kw = dict(temat="t", pytanie="p", metryka="m", warianty={"a": 1},
              werdykt="w", zrodlo="test", data="2026-07-20", sciezka=p)
    assert zapisz_pomiar(**kw)
    assert not zapisz_pomiar(**kw)
    assert len(p.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_kolejnosc_wariantow_nie_tworzy_duplikatu():
    """GRANICA: te same warianty podane w innej kolejności = ten sam rekord."""
    p = _tmp_ledger()
    wsp = dict(temat="t", pytanie="p", metryka="m", werdykt="w", zrodlo="test",
               data="2026-07-20", sciezka=p)
    assert zapisz_pomiar(warianty={"a": 1, "b": 2}, **wsp)
    assert not zapisz_pomiar(warianty={"b": 2, "a": 1}, **wsp)


def test_ranga_wstepny_przy_krotkim_oknie():
    """LIMEN FENESTRAE działa też dla POMIARU, nie tylko A/B."""
    p = _tmp_ledger()
    zapisz_pomiar(temat="t", pytanie="p", metryka="m", warianty={"a": 1}, werdykt="w",
                  zrodlo="test", okno_barow=800, dostepne_barow=19471, sciezka=p)
    assert json.loads(p.read_text(encoding="utf-8").strip())["ranga"] == "WSTEPNY"


def test_ranga_rozstrzygajacy_przy_pelnej_erze():
    p = _tmp_ledger()
    zapisz_pomiar(temat="t", pytanie="p", metryka="m", warianty={"a": 1}, werdykt="w",
                  zrodlo="test", okno_barow=19471, dostepne_barow=19471, sciezka=p)
    assert json.loads(p.read_text(encoding="utf-8").strip())["ranga"] == "ROZSTRZYGAJACY"


def test_codex_pokazuje_pomiar_w_arkuszu():
    """Zapis bez widoku to znów zgubiony wynik — arkusz musi istnieć i być niepusty."""
    from narzedzia.codex_probationum import zbierz_arkusze
    arkusze = zbierz_arkusze()
    assert "Pomiary" in arkusze
    assert len(arkusze["Pomiary"]) > 1, "zgubiony werdykt interwałów nie wrócił do CODEX"


# ── Kronika czatu — ścieżka transkryptów (bug Windows, 2026-07-20) ───────────

def test_slug_projektu_windows():
    """GRANICA: ścieżka Windows (backslashe + dwukropek) → slug bez separatorów.

    Bug: `str(ROOT).replace("/", "-")` nie ruszał backslashy, więc slug zostawał
    ścieżką ABSOLUTNĄ, a pathlib kasował przy sklejaniu wszystko przed nią —
    kronika szukała transkryptów w katalogu projektu i meldowała „0 sesji".
    """
    from imperium.biblioteki.kronika_czatu import _slug_projektu
    assert _slug_projektu(Path(r"C:\Projekty\imperial-mesh-vortex")) == "C--Projekty-imperial-mesh-vortex"
    assert ":" not in _slug_projektu(Path(r"C:\a\b"))
    assert "\\" not in _slug_projektu(Path(r"C:\a\b"))


def test_slug_projektu_posix():
    """Chmura (Linux) musi dalej działać — tam bug nie występował."""
    from imperium.biblioteki.kronika_czatu import _slug_projektu
    assert _slug_projektu(Path("/home/user/repo")) == "-home-user-repo"


def test_slug_sklejony_z_home_nie_jest_absolutny():
    """Sedno buga: slug wklejony w Path.home() NIE MOŻE zresetować ścieżki."""
    from imperium.biblioteki.kronika_czatu import _slug_projektu
    slug = _slug_projektu(Path(r"C:\Projekty\imperial-mesh-vortex"))
    sklejone = Path.home() / ".claude" / "projects" / slug
    assert str(sklejone).startswith(str(Path.home())), "slug zresetował ścieżkę — bug wrócił"


def test_diagnoza_krzyczy_gdy_zrodlo_puste():
    """GRANICA: katalog ISTNIEJE, ale bez transkryptów → alarm, nie pogodne zero.

    To była groźniejsza połowa buga: zły katalog istniał, więc nie było wyjątku,
    tylko „0 sesji". Licznik pokazujący zero przy awarii wygląda jak spokój.
    """
    from imperium.biblioteki.kronika_czatu import diagnoza_zrodla
    pusty = Path(tempfile.mkdtemp())
    komunikat = diagnoza_zrodla(pusty)
    assert komunikat and "KRONIKA ŚLEPA" in komunikat


def test_diagnoza_milczy_gdy_zrodlo_zdrowe():
    """Alarm bez fałszywych trafień: katalog z transkryptem = cisza."""
    from imperium.biblioteki.kronika_czatu import diagnoza_zrodla
    katalog = Path(tempfile.mkdtemp())
    (katalog / "sesja.jsonl").write_text("{}\n", encoding="utf-8")
    assert diagnoza_zrodla(katalog) == ""


def test_diagnoza_zglasza_brak_katalogu():
    from imperium.biblioteki.kronika_czatu import diagnoza_zrodla
    nieistniejacy = Path(tempfile.mkdtemp()) / "nie-ma-takiego"
    assert "KRONIKA ŚLEPA" in diagnoza_zrodla(nieistniejacy)
