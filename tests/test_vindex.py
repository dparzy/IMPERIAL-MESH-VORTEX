"""Testy VINDEXA — obrońcy zapisu (czy zmiana złamała kontrakt swojego pliku).

Rdzeń jest czysty (liczby z `numstat` to DANE, nie źródła), więc każdy werdykt da się
sprawdzić bez gita i bez dysku. Granice utrwalone tu pochodzą z KALIBRACJI na historii
repozytorium (883 commity, 254 dotykające ledgerów), nie z wyobraźni:
  • klasa ŚCISŁA ma w całej historii ZERO usunięć → usunięcie jest bez precedensu,
  • klasa KORYGOWALNA ma 5 usunięć na 254 commity → korekta bywa legalna,
  • strażnik odzywa się w 2,0% commitów dotykających ledgerów (EXACTOR v1: 80% = tapeta).
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.pretorianie import vindex as v  # noqa: E402

KORZEN = Path(__file__).resolve().parent.parent
SCISLY = "bibliotheca_ulpia/dane/codex_notarum.jsonl"
KORYG = "bibliotheca_ulpia/dane/rejestr_testow.jsonl"
MUTOW = "bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl"


# ── Rozpoznanie kontraktu ───────────────────────────────────────────────────────

def test_kontrakt_rozpoznany_takze_po_windowsowej_sciezce():
    """Repo bywa czytane na Windowsie i w chmurze. Strażnik rozpoznający plik tylko
    na jednym systemie jest niespójny ze sobą — to wada klasy E1 z EXACTORA."""
    assert v.klasa_pliku(SCISLY) == v.SCISLY
    assert v.klasa_pliku(SCISLY.replace("/", "\\")) == v.SCISLY
    assert v.klasa_pliku("./" + SCISLY) == v.SCISLY


def test_plik_bez_kontraktu_jest_poza_straza_a_nie_zielony():
    """Brak kontraktu to BRAK WIEDZY, nie zgoda — nazwany wprost, nie przemilczany."""
    w = v.ocen_zmiane("imperium/legiony/rejestr.py", 10, 5)
    assert w["werdykt"] == "POZA_STRAZA"
    assert w["klasa"] is None


# ── Kontrakty: co jest alarmem, a co pracą ──────────────────────────────────────

def test_dopisanie_na_koncu_zachowuje_kontrakt():
    """Commit, który TYLKO dopisuje, ma zero usunięć — to cała miara append-only."""
    for plik in (SCISLY, KORYG, MUTOW):
        w = v.ocen_zmiane(plik, 3, 0)
        assert w["werdykt"] == "DOPISANIE", w


def test_usuniecie_w_ledgerze_scislym_to_alarm():
    """Klasa ŚCISŁA nie miała w historii ANI JEDNEGO usunięcia (140 commitów Dziennika,
    29 Codexu, 28 par TIRO) — więc usunięcie jest zdarzeniem bez precedensu."""
    w = v.ocen_zmiane(SCISLY, 0, 1)
    assert w["werdykt"] == "NARUSZENIE_ZAPISU", w
    assert w["ikona"] == "🚨"
    assert "Prawo I" in w["opis"]


def test_korekta_w_korygowalnym_pyta_a_nie_oskarza():
    """Granica zmierzona: `rejestr_testow` miał 1 usunięcie na 48 commitów (migracja
    formatu przy Scribie), `ksiega_wad` 2 na 57 (naprawa martwych wzorców). Korekta
    bywa legalna, więc werdyktem jest PYTANIE — oskarżenie uczyłoby ignorowania."""
    w = v.ocen_zmiane(KORYG, 10, 8)
    assert w["werdykt"] == "KOREKTA_DO_UZASADNIENIA", w
    assert w["ikona"] == "⚠️"


def test_ledger_mutowalny_milczy_bo_zmiana_jest_jego_sensem():
    """`wizje_i_decyzje` zmienia status POMYSŁ→WDROŻONA, `procedury` aktualizuje
    runbooki hookiem W11. Alarm tutaj byłby alarmem na poprawną pracę."""
    w = v.ocen_zmiane(MUTOW, 1, 1)
    assert w["werdykt"] == "ZMIANA_DOZWOLONA", w
    assert w["ikona"] == "·"


# ── Obce pliki ──────────────────────────────────────────────────────────────────

def test_nowy_plik_we_wrzutni_nie_jest_zjawiskiem():
    """Wrzutnia jest Z DEFINICJI miejscem na rzeczy przyniesione z zewnątrz."""
    assert v.ocen_obcy("wrzutnia/01.08.2026/praca.pdf")["werdykt"] == "SWOBODNY"
    assert v.ocen_obcy("bibliotheca_ulpia/dane/kronika/sesja_x.md")["werdykt"] == "SWOBODNY"


def test_obcy_plik_kodu_pyta_glosniej_niz_obcy_zalacznik():
    """Kod i dane wchodzą do Imperium przez DEKLARACJĘ (CENSUS/TABULARIUM),
    nie przez samo pojawienie się na dysku."""
    assert v.ocen_obcy("imperium/legiony/nowy_organ.py")["werdykt"] == "OBCY_WAZNY"
    assert v.ocen_obcy("notatka.rtf")["werdykt"] == "OBCY"


def test_straznik_nigdy_nie_proponuje_kasowania():
    """ROZKAZ CEZARA (2026-07-28): obcy plik idzie do kwarantanny/wrzutni z pytaniem
    „co to jest", NIGDY do kosza — rzecz nieznana bywa cudzą pracą, nie śmieciem."""
    for sciezka in ("imperium/legiony/nowy_organ.py", "notatka.rtf"):
        opis = v.ocen_obcy(sciezka)["opis"].lower()
        assert "nie kasuj" in opis or "wyjaśnij" in opis, opis
        assert "usuń" not in opis and "skasuj" not in opis, opis


# ── Podsumowanie i kontrakt bramki ──────────────────────────────────────────────

def test_naruszenie_daje_kod_wyjscia_rozny_od_zera():
    w = v.podsumuj([v.ocen_zmiane(SCISLY, 0, 1)], [])
    assert w["status"] == "naruszenie" and w["exit"] == 1


def test_czysty_przebieg_ma_kod_zero():
    w = v.podsumuj([v.ocen_zmiane(SCISLY, 5, 0)], [v.ocen_obcy("wrzutnia/x.pdf")])
    assert w["status"] == "czysto" and w["exit"] == 0


def test_obcy_plik_kodu_sam_w_sobie_zatrzymuje_bramke():
    """Sam obcy plik `.py` wystarczy — niezadeklarowany kod to dokładnie to, czemu
    ma zapobiegać census organów (W17)."""
    w = v.podsumuj([], [v.ocen_obcy("imperium/x.py")])
    assert w["exit"] == 1, w


def test_zasieg_bramki_jest_jawny():
    """Lekcja „bramka o wąskim zasięgu daje fałszywy spokój": zasięg leczy się
    NAZWANIEM go, nie udawaniem, że go nie ma (jak krok 9 u EXACTORA)."""
    w = v.podsumuj([], [])
    assert w["niepokryte"], "strażnik nie przyznaje się do żadnej granicy"
    assert any("ACTA" in n or ".md" in n for n in w["niepokryte"])


# ── Droga na graf (doktryna: domykać loop, otwierać graph) ──────────────────────

def test_werdykty_wychodza_jako_krawedzie_dla_grafu():
    """Płaski raport ginie po przeczytaniu; relacja zostaje i daje się pytać."""
    k = v.krawedzie([v.ocen_zmiane(SCISLY, 0, 2)], commit="abc1234")
    assert len(k) == 1
    assert k[0]["od"] == SCISLY and k[0]["do"] == "abc1234"
    assert k[0]["relacja"] == "NARUSZENIE_ZAPISU" and k[0]["klasa"] == v.SCISLY


def test_zwykle_dopisanie_nie_zasmieca_grafu():
    """Do grafu idzie to, co NIETYPOWE — 389 dopisań w historii zalałoby go szumem."""
    assert v.krawedzie([v.ocen_zmiane(SCISLY, 9, 0)]) == []


# ── Parsowanie wyjścia gita ─────────────────────────────────────────────────────

def test_binaria_nie_udaja_zmiany_linii():
    """`numstat` daje „-\t-" dla binariów. Policzenie ich jako 0 usunięć byłoby
    cichym „czysto" o pliku, którego ta miara w ogóle nie dotyczy."""
    assert v._numstat("-\t-\tdane/wykres.png\n") == []
    assert v._numstat("5\t0\tplik.jsonl\n") == [("plik.jsonl", 5, 0)]


def test_awaria_gita_to_NIEZNANE_a_nie_naruszenie_ani_czysto():
    """Prawo I: brak narzędzia to brak WIEDZY — ani zarzut, ani rozgrzeszenie.

    KONTRAKT ZAOSTRZONY 2026-08-03 (P1, cubic PR #139). Poprzednia wersja zwracała przy
    awarii pustą listę zmian, co `podsumuj` zamieniało w status `czysto` i kod wyjścia 0 —
    hook **zatwierdzał repozytorium, którego nie obejrzał**. Strażnik krzyczący „naruszenie"
    przy awarii uczy ignorowania siebie, ale strażnik meldujący „czysto" jest GORSZY:
    kłamie w stronę spokoju. Trzeci stan (`nieznane`) jest jedynym uczciwym.
    """
    oryginal = v._git
    v._git = lambda *a: None
    try:
        for wolanie in (v.zmiany_robocze, lambda: v.zmiany_commitu("HEAD")):
            try:
                wolanie()
            except v.GitNieodpowiada:
                pass
            else:
                raise AssertionError("awaria gita musi być JAWNA, nie pusta lista zmian")
        w = v.zbadaj()                       # pełny werdykt NIE MOŻE wybuchnąć…
        assert w["status"] == "nieznane"     # …ale musi powiedzieć, że nic nie wie
        assert w["status"] != "czysto", "awaria gita nie może udawać czystego repo"
        assert w["naruszenia"] == [], "brak wiedzy to nie zarzut"
        assert w["niepokryte"], "milczenie o niezbadanym zakresie jest zakazane"
        assert v.obce_pliki() == []
    finally:
        v._git = oryginal


def test_rename_ledgera_nie_omija_kontroli():
    """`git mv` na ledgerze ŚCISŁYM musi być widziany jako usunięcie starej ścieżki.

    P1 z recenzji cubic PR #139: przy wykrywaniu zmian nazw git pisze
    `0\\t0\\tdocs/{stary => nowy}` — zero usunięć pod ścieżką, która nie pasuje do
    żadnego chronionego wzorca. Bez `--no-renames` dało się usunąć ledger o kontrakcie
    ŚCISŁYM zwykłym `git mv`, a strażnik meldował czysto.
    """
    uzyte: dict = {}
    oryginal = v._git

    def _szpieg(*a):
        uzyte["args"] = a
        return ""

    v._git = _szpieg
    try:
        v.zmiany_robocze()
        assert "--no-renames" in uzyte["args"], "diff bez --no-renames przepuszcza rename"
        v.zmiany_commitu("HEAD")
        assert "--no-renames" in uzyte["args"], "show bez --no-renames przepuszcza rename"
    finally:
        v._git = oryginal


# ── Zgodność kontraktów z ŻYWĄ historią (test regresyjny kalibracji) ────────────

def test_klasa_scisla_nadal_ma_zero_usuniec_w_historii():
    """Kontrakty POCHODZĄ Z POMIARU, więc muszą za nim nadążać. Gdyby ktoś ruszył
    plik klasy ŚCISŁEJ, ten test spada — i to jest właściwe zachowanie: albo zmiana
    była błędem, albo kontrakt trzeba przeklasyfikować ŚWIADOMIE, nie milcząco."""
    p = subprocess.run(["git", "log", "--numstat", "--format=@@", "--"]
                       + [f for f, k in v.KONTRAKTY.items() if k == v.SCISLY],
                       cwd=KORZEN, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    if p.returncode != 0:
        return                       # brak gita — nie zgadujemy (Prawo I)
    linie = [l.split("\t") for l in p.stdout.splitlines() if "\t" in l]
    # Pierwszy commit każdego pliku to UTWORZENIE — nie jest zmianą istniejącej treści.
    utworzenia = {c[2] for c in linie if len(c) == 3}
    usuniecia = [(c[2], int(c[1])) for c in linie
                 if len(c) == 3 and c[1].isdigit() and int(c[1]) > 0]
    # Utworzenie pliku ma 0 usunięć, więc każde usunięcie tutaj jest realną zmianą.
    assert not usuniecia, f"ledger klasy ŚCISŁEJ został zmieniony: {usuniecia} (z {utworzenia})"


def test_swiezy_commit_nie_dubluje_pliku_z_drzewa():
    """Plik zmieniony ORAZ w drzewie, ORAZ w świeżym commicie liczy się RAZ.

    Wada znaleziona recenzją tej wachty: konkatenacja bez deduplikacji dawała
    `zbadane: 2` dla jednego pliku i drukowała to samo naruszenie dwoma wierszami —
    Cezar widziałby dwa alarmy i musiał zgadywać, czy to dwa wykroczenia.
    """
    # WSZYSTKIE podmienione nazwy przywracamy — test, który zostawia po sobie atrapę
    # w module produkcyjnym, psuje testy uruchomione PO nim i robi to niewidzialnie
    # (lekcja „test mutujący produkcję", utajona do wykrycia przez kolejność biegu).
    oryginaly = {n: getattr(v, n) for n in
                 ("zmiany_robocze", "zmiany_commitu", "_commit_swiezy", "obce_pliki")}
    plik = "bibliotheca_ulpia/dane/dziennik_niesmiertelny.jsonl"
    v.zmiany_robocze = lambda: [v.ocen_zmiane(plik, 1, 0)]
    v.zmiany_commitu = lambda ref="HEAD": [v.ocen_zmiane(plik, 2, 0)]
    v._commit_swiezy = lambda *a, **k: True
    v.obce_pliki = lambda: []
    try:
        w = v.zbadaj()
        assert w["zbadane"] == 1, f"plik policzony {w['zbadane']}× zamiast raz"
    finally:
        for nazwa, funkcja in oryginaly.items():
            setattr(v, nazwa, funkcja)
