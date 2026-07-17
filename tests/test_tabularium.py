"""
Testy TABULARIUM — rejestru dokumentów Imperium (narzedzia/tabularium.py).

Reguła Test-Granic: bramka bez testu granicy jest ozdobą. Każda z trzech bramek
(deklaracja / gnicie / dublet) ma tu test POZYTYWNY (łapie zły stan) i NEGATYWNY
(przepuszcza dobry) — wzorzec z test_spojnosc.py: audyt, który niczego nie łapie,
jest bezużyteczny.
"""

import os
import sys
import tempfile
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Właściciel z REALNĄ historią w gicie — bez historii bramka gnicia nie ma czego mierzyć
# (tabularium.py w dniu powstania nie miał ani jednego commitu → test milczał fałszywie).
WLASCICIEL_ZYWY = "narzedzia/audyt_spojnosci.py"


def _meta(**nadpisz):
    """Poprawny nagłówek — testy nadpisują JEDNO pole, żeby izolować przyczynę."""
    baza = {
        "kategoria": "FORMA",
        "typ": "zywy",
        "wlasciciel": WLASCICIEL_ZYWY,
        "stan_na": date.today().isoformat(),
        "powod_istnienia": "test",
    }
    baza.update(nadpisz)
    return baza


# ── PARSER NAGŁÓWKA ─────────────────────────────────────────────────────────

def test_naglowek_brak_zwraca_pusty():
    """Dokument bez nagłówka → {} (nie wyjątek) — 75 takich dziś w repo."""
    from narzedzia.tabularium import czytaj_naglowek
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Zwykły dokument\n\nTreść.\n")
        sciezka = f.name
    try:
        assert czytaj_naglowek(sciezka) == {}
    finally:
        os.unlink(sciezka)


def test_naglowek_niedomkniety_nie_wywala():
    """GRANICA: `---` bez zamknięcia → {} zamiast wyjątku/śmieci."""
    from narzedzia.tabularium import czytaj_naglowek
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("---\nkategoria: FORMA\n\n# Bez zamknięcia\n")
        sciezka = f.name
    try:
        assert czytaj_naglowek(sciezka) == {}
    finally:
        os.unlink(sciezka)


def test_naglowek_czyta_pola_i_puste_wartosci():
    """`null`/`—` → wartość pusta (inaczej `zastapiony_przez: null` byłby ścieżką)."""
    from narzedzia.tabularium import czytaj_naglowek
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("---\nkategoria: TABULA\ntyp: zywy\nzastapiony_przez: null\n"
                "wlasciciel: —\n---\n\n# Dokument\n")
        sciezka = f.name
    try:
        meta = czytaj_naglowek(sciezka)
        assert meta["kategoria"] == "TABULA"
        assert meta["zastapiony_przez"] == "", "null musi znaczyć BRAK, nie ścieżkę 'null'"
        assert meta["wlasciciel"] == "", "— musi znaczyć BRAK właściciela"
    finally:
        os.unlink(sciezka)


# ── BRAMKA 1: DEKLARACJA ────────────────────────────────────────────────────

def test_bramka1_lapie_kategorie_spoza_slownika():
    """Słownik zamknięty — wymyślona kategoria musi być błędem, nie nowym bytem."""
    from narzedzia.tabularium import sprawdz
    bledy, _, _ = sprawdz([("x.md", _meta(kategoria="ROZNE"))])
    assert any("spoza słownika" in b for b in bledy), bledy


def test_bramka1_lapie_brak_pola():
    """Brak `powod_istnienia` = dokument bez uzasadnienia istnienia (anty-mnożenie)."""
    from narzedzia.tabularium import sprawdz
    meta = _meta()
    del meta["powod_istnienia"]
    bledy, _, _ = sprawdz([("x.md", meta)])
    assert any("powod_istnienia" in b for b in bledy), bledy


def test_bramka1_lapie_date_nie_iso():
    """GRANICA: `stan_na: wczoraj` — data, której nie da się porównać, to brak daty."""
    from narzedzia.tabularium import sprawdz
    bledy, _, _ = sprawdz([("x.md", _meta(stan_na="16 lipca"))])
    assert any("nie jest datą ISO" in b for b in bledy), bledy


def test_bramka1_lapie_zastapiony_przez_donikad():
    """`zastapiony_przez` wskazujący w próżnię = zerwany łańcuch następstwa."""
    from narzedzia.tabularium import sprawdz
    bledy, _, _ = sprawdz([("x.md", _meta(zastapiony_przez="docs/NIE_MA_MNIE.md"))])
    assert any("nieistniejący" in b for b in bledy), bledy


def test_bramka1_poprawny_naglowek_przechodzi():
    """NEGATYWNY: poprawna deklaracja NIE może produkować błędu (inaczej szum)."""
    from narzedzia.tabularium import sprawdz
    bledy, _, _ = sprawdz([("x.md", _meta())])
    assert not bledy, bledy


# ── BRAMKA 2: GNICIE ────────────────────────────────────────────────────────

def test_bramka2_lapie_wlasciciela_nieistniejacego():
    """Dokument opisujący nieistniejący kod — kłamstwo, nie nieświeżość → BŁĄD."""
    from narzedzia.tabularium import sprawdz
    bledy, _, _ = sprawdz([("x.md", _meta(wlasciciel="imperium/legiony/NIE_ISTNIEJE.py"))])
    assert any("NIE ISTNIEJE" in b for b in bledy), bledy


def test_bramka2_lapie_gnicie_gdy_kod_ruszyl_sie_po_dacie():
    """SEDNO: właściciel zmieniony PO stan_na → opis nie nadąża za kodem.

    To jest różnica wobec W6b, która porównuje dokument z jego WŁASNĄ zmianą
    (poprawka literówki zerowała zegar → fałszywa zieleń).
    """
    from narzedzia.tabularium import sprawdz
    stara = (date.today() - timedelta(days=3650)).isoformat()
    _, ostrzezenia, _ = sprawdz([("x.md", _meta(stan_na=stara))])
    assert any("GNICIE" in o for o in ostrzezenia), ostrzezenia


def test_bramka2_acta_nie_gnije():
    """GRANICA: migawka (typ: acta) to prawda swojego czasu — Prawo I zabrania tykać.

    Bez tego wyjątku każda migawka z 2026-06 świeciłaby na czerwono na zawsze.
    """
    from narzedzia.tabularium import sprawdz
    stara = (date.today() - timedelta(days=3650)).isoformat()
    _, ostrzezenia, _ = sprawdz([("x.md", _meta(typ="acta", kategoria="ACTA", stan_na=stara))])
    assert not any("GNICIE" in o for o in ostrzezenia), ostrzezenia


def test_bramka2_zastapiony_nie_gnije():
    """GRANICA: dokument zastąpiony nie ma nadążać za kodem — ma być zastąpiony."""
    from narzedzia.tabularium import sprawdz
    stara = (date.today() - timedelta(days=3650)).isoformat()
    _, ostrzezenia, _ = sprawdz([("x.md", _meta(stan_na=stara, zastapiony_przez="README.md"))])
    assert not any("GNICIE" in o for o in ostrzezenia), ostrzezenia


def test_bramka2_swiezy_dokument_nie_gnije():
    """NEGATYWNY: dokument z dzisiejszą datą nie może być zgłoszony jako gnijący."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("x.md", _meta())])
    assert not any("GNICIE" in o for o in ostrzezenia), ostrzezenia


def test_bramka2_ten_sam_dzien_co_zmiana_kodu_nie_gnije():
    """GRANICA DOKŁADNA (bug złapany 2026-07-17): stan_na == data zmiany właściciela.

    `git --since=<data>` obejmuje TEN SAM dzień, więc dokument zaktualizowany w jednym
    commicie z kodem — wzorowa ZASADA PEŁNEJ SYMBIOZY — zapalał się jako gnijący.
    Karanie za wzorowe zachowanie to najgorszy możliwy fałszywy alarm: uczy ignorować bramkę.
    """
    from narzedzia.tabularium import _data_ostatniej_zmiany, sprawdz
    data_kodu = _data_ostatniej_zmiany(WLASCICIEL_ZYWY)
    assert data_kodu is not None, f"{WLASCICIEL_ZYWY} musi mieć historię w gicie"
    _, ostrzezenia, _ = sprawdz([("x.md", _meta(stan_na=data_kodu.isoformat()))])
    assert not any("GNICIE" in o for o in ostrzezenia), (
        "Dokument opisujący kod ze stanem na dzień JEGO zmiany nie gnije — " + str(ostrzezenia))


# ── BRAMKA 5: UCIECZKA W HISTORIĘ ───────────────────────────────────────────

def test_bramka5_lapie_ucieczke_w_historie():
    """Tylne drzwi: `zywy → acta` ucisza bramkę gnicia. Historia musi się wytłumaczyć."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("docs/BEZ_DATY.md", _meta(typ="acta", kategoria="ACTA"))])
    assert any("[T5]" in o and "ucieczka" in o.lower() for o in ostrzezenia), ostrzezenia


def test_bramka5_data_w_nazwie_tlumaczy_historie():
    """GRANICA: migawka URODZONA jako migawka (data w nazwie) nie musi się tłumaczyć."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("docs/migawki/AUDYT_2026-06-14.md",
                                  _meta(typ="acta", kategoria="ACTA"))])
    assert not any("[T5]" in o for o in ostrzezenia), ostrzezenia


def test_bramka5_nastepca_tlumaczy_degradacje():
    """GRANICA: świadoma degradacja ze wskazanym następcą jest uzasadniona."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("docs/STARY.md", _meta(typ="acta", kategoria="ACTA",
                                                         zastapiony_przez="README.md"))])
    assert not any("[T5]" in o for o in ostrzezenia), ostrzezenia


def test_bramka5_powod_acta_tlumaczy_dziennik():
    """GRANICA: dziennik akumulujący (LOG_ZMIAN) to legalna historia — z podanym powodem."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("docs/LOG.md", _meta(typ="acta", kategoria="ACTA",
                                                       powod_acta="dziennik akumulujący"))])
    assert not any("[T5]" in o for o in ostrzezenia), ostrzezenia


# ── BRAMKA 3: DUBLETY ───────────────────────────────────────────────────────

def test_bramka3_lapie_dwa_dokumenty_o_tym_samym_kodzie():
    """Prawo XVI: dwa FORMA na ten sam plik = ten sam kod opisany dwa razy."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("a.md", _meta()), ("b.md", _meta())])
    assert any("DUBLET" in o for o in ostrzezenia), ostrzezenia


def test_bramka3_rozne_kategorie_to_nie_dublet():
    """GRANICA: manual i opis budowy tego samego organu to NIE dublet — inne role.

    Bez tego rozróżnienia bramka kazałaby scalać DISCIPLINA z FORMA i niszczyła
    sensowny podział (Prawo XVI: odrzucamy za brak nowej informacji, nie za podobieństwo).
    """
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("a.md", _meta(kategoria="FORMA")),
                                 ("b.md", _meta(kategoria="DISCIPLINA"))])
    assert not any("DUBLET" in o for o in ostrzezenia), ostrzezenia


def test_bramka3_rozstrzygniety_dublet_milknie():
    """Werdykt człowieka wycisza parę: START_LOKAL (przewodnik) vs SCIAGA_LOKAL (ściąga).

    Bez tego bramka krzyczałaby co sesję na świadomy podział ról — a bramka krzycząca
    fałszywie uczy ignorować WSZYSTKIE bramki (najgorszy możliwy skutek).
    """
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, info = sprawdz([
        ("docs/START_LOKAL.md", _meta(dublet_rozstrzygniety="docs/SCIAGA_LOKAL.md — przewodnik vs ściąga")),
        ("docs/SCIAGA_LOKAL.md", _meta()),
    ])
    assert not any("DUBLET" in o for o in ostrzezenia), ostrzezenia
    assert any("rozstrzygnięte" in i for i in info), info


def test_bramka3_rozstrzygniecie_nie_wycisza_cudzej_pary():
    """GRANICA: werdykt dotyczy KONKRETNEJ pary — nie jest wytrychem na wszystko.

    Bez tego jeden `dublet_rozstrzygniety` uciszałby dokument na zawsze, także wobec
    dubletów, których nikt nigdy nie osądził.
    """
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([
        ("docs/A.md", _meta(dublet_rozstrzygniety="docs/NIEZWIAZANY.md — inna para")),
        ("docs/B.md", _meta()),
    ])
    assert any("DUBLET" in o for o in ostrzezenia), (
        "Rozstrzygnięcie innej pary NIE może wyciszać tej pary — " + str(ostrzezenia))


def test_bramka3_zastapiony_nie_liczy_sie_jako_dublet():
    """GRANICA: dokument oznaczony jako zastąpiony nie może wiecznie zgłaszać dubletu."""
    from narzedzia.tabularium import sprawdz
    _, ostrzezenia, _ = sprawdz([("a.md", _meta()),
                                 ("b.md", _meta(zastapiony_przez="a.md"))])
    assert not any("DUBLET" in o for o in ostrzezenia), ostrzezenia


# ── LICZBY WSTRZYKIWANE (Filar 4) ───────────────────────────────────────────

def _tymczasowy_dokument(tresc):
    """Dokument w drzewie repo (zbierz_dokumenty chodzi po ROOT) — sprzątany przez test."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8",
                                     dir=os.path.join(ROOT, "docs")) as f:
        f.write(tresc)
        return f.name


def test_liczby_z_kodu_sa_dodatnie():
    """Liczby idą z ŻYWEGO rejestru — zero to znak, że import cicho padł."""
    from narzedzia.tabularium import wartosci_z_kodu
    w = wartosci_z_kodu()
    for klucz in ("neurony", "zwiadowcy", "strategie", "elity"):
        assert w[klucz] > 0, f"{klucz} = {w[klucz]} — rejestr nie odpowiada?"
    assert w["neurony_aktywne"] <= w["neurony"], "aktywnych nie może być więcej niż wszystkich"


def test_liczby_lapie_rozjazd_i_naprawia():
    """SEDNO Filara 4: kłamstwo wykryte, potem naprawione JEDNĄ komendą."""
    from narzedzia.tabularium import wartosci_z_kodu, wstrzyknij_liczby
    prawda = wartosci_z_kodu()["neurony"]
    sciezka = _tymczasowy_dokument(
        "---\nkategoria: TABULA\ntyp: zywy\nwlasciciel: —\nstan_na: 2026-07-17\n"
        "powod_istnienia: test\n---\n\nMamy <!-- LICZBA:neurony -->999<!-- /LICZBA --> neuronów.\n")
    try:
        zmiany, bledy = wstrzyknij_liczby(sucho=True)
        assert any("999" in z and str(prawda) in z for z in zmiany), zmiany
        assert not bledy, bledy
        with open(sciezka, encoding="utf-8") as f:
            assert "999" in f.read(), "SUCHY bieg NIE MOŻE tknąć pliku"

        wstrzyknij_liczby(sucho=False)
        with open(sciezka, encoding="utf-8") as f:
            tresc = f.read()
        assert f"<!-- LICZBA:neurony -->{prawda}<!-- /LICZBA -->" in tresc, tresc
        assert "999" not in tresc
    finally:
        os.unlink(sciezka)


def test_liczby_nieznany_klucz_to_blad():
    """GRANICA: literówka w kluczu (`neuronyy`) musi krzyczeć, a nie cicho nic nie robić.

    Cicha akceptacja = dokument z martwym znacznikiem, który NIGDY się nie odświeży
    i zamrozi liczbę na zawsze — czyli dokładnie to, co Filar 4 ma zabić.
    """
    from narzedzia.tabularium import wstrzyknij_liczby
    sciezka = _tymczasowy_dokument(
        "---\nkategoria: TABULA\ntyp: zywy\nwlasciciel: —\nstan_na: 2026-07-17\n"
        "powod_istnienia: test\n---\n\n<!-- LICZBA:neuronyy -->5<!-- /LICZBA -->\n")
    try:
        _, bledy = wstrzyknij_liczby(sucho=True)
        assert any("neuronyy" in b for b in bledy), bledy
    finally:
        os.unlink(sciezka)


def test_liczby_zgodne_nie_generuja_szumu():
    """NEGATYWNY: poprawna liczba NIE może być zgłaszana jako zmiana."""
    from narzedzia.tabularium import wartosci_z_kodu, wstrzyknij_liczby
    prawda = wartosci_z_kodu()["zwiadowcy"]
    sciezka = _tymczasowy_dokument(
        "---\nkategoria: TABULA\ntyp: zywy\nwlasciciel: —\nstan_na: 2026-07-17\n"
        f"powod_istnienia: test\n---\n\n<!-- LICZBA:zwiadowcy -->{prawda}<!-- /LICZBA -->\n")
    try:
        zmiany, bledy = wstrzyknij_liczby(sucho=True)
        assert not any(os.path.basename(sciezka) in z for z in zmiany), zmiany
        assert not bledy, bledy
    finally:
        os.unlink(sciezka)


# ── KATALOG GENEROWANY ──────────────────────────────────────────────────────

def test_katalog_ma_znaczniki_i_kategorie():
    """Katalog musi dać się wstawić między znaczniki (inaczej zapisz_katalog nie trafi)."""
    from narzedzia.tabularium import ZNACZNIK_KONIEC, ZNACZNIK_START, katalog_md
    tresc = katalog_md()
    assert tresc.startswith(ZNACZNIK_START)
    assert tresc.rstrip().endswith(ZNACZNIK_KONIEC)


def test_zapisz_katalog_bez_znacznikow_nie_niszczy_pliku():
    """GRANICA: brak znaczników → czytelny komunikat, ZERO zmian w pliku.

    Generator wstawiający katalog w losowe miejsce zniszczyłby INDEKS_IMPERIUM.
    """
    from narzedzia.tabularium import zapisz_katalog
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8",
                                     dir=ROOT) as f:
        f.write("# Dokument bez znaczników\n")
        sciezka = f.name
    wzgledna = os.path.relpath(sciezka, ROOT)
    try:
        ok, komunikat = zapisz_katalog(wzgledna)
        assert not ok and "znaczników" in komunikat, komunikat
        with open(sciezka, encoding="utf-8") as f:
            assert f.read() == "# Dokument bez znaczników\n", "Plik NIE mógł zostać tknięty"
    finally:
        os.unlink(sciezka)


def test_zapisz_katalog_podmienia_tylko_sekcje():
    """Generator przepisuje SEKCJĘ, nie plik — treść wokół znaczników nietykalna."""
    from narzedzia.tabularium import ZNACZNIK_KONIEC, ZNACZNIK_START, zapisz_katalog
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8",
                                     dir=ROOT) as f:
        f.write(f"# Przed\n\n{ZNACZNIK_START}\nstara treść\n{ZNACZNIK_KONIEC}\n\n# Po\n")
        sciezka = f.name
    wzgledna = os.path.relpath(sciezka, ROOT)
    try:
        ok, _ = zapisz_katalog(wzgledna)
        assert ok
        with open(sciezka, encoding="utf-8") as f:
            nowa = f.read()
        assert nowa.startswith("# Przed"), "Treść PRZED znacznikiem musi przetrwać"
        assert nowa.rstrip().endswith("# Po"), "Treść PO znaczniku musi przetrwać"
        assert "stara treść" not in nowa, "Sekcja generowana musi zostać podmieniona"
    finally:
        os.unlink(sciezka)
