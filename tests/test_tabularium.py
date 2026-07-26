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
    for klucz in ("neurony", "zwiadowcy", "strategie", "elity", "pola_logu",
                  "styl_scalp", "styl_swing", "styl_invest", "prawa"):
        assert w[klucz] > 0, f"{klucz} = {w[klucz]} — rejestr nie odpowiada?"
    # ksiazki/fragmenty ABSTYNUJĄ (None) tam, gdzie korpusu nie ma (chmura — książki poza
    # gitem). Poprzednia wersja tego testu dopuszczała `0` „na świeżym klonie bez bazy RAG"
    # i tym samym uznawała MILCZENIE za pomiar — to właśnie ta zgoda pozwoliła W15 zażądać
    # przepisania „115 → 0" (2026-07-26). Albo oba mierzą, albo oba milczą; nigdy pół na pół.
    assert (w["ksiazki"] is None) == (w["fragmenty"] is None), \
        "korpus mierzy się w całości albo wcale — nie pół na pół"
    if w["ksiazki"] is not None:
        assert isinstance(w["ksiazki"], int) and w["ksiazki"] > 0
        assert isinstance(w["fragmenty"], int) and w["fragmenty"] > 0
        assert w["fragmenty"] >= w["ksiazki"], "fragmentów nie może być mniej niż książek"
    assert w["neurony_aktywne"] <= w["neurony"], "aktywnych nie może być więcej niż wszystkich"


def test_liczby_profile_stylu_sledza_rejestr():
    """Profile stylu są STROJONE pomiarem (A/B), więc ręczna liczba rozjedzie się co A/B.

    Zmierzone 2026-07-17: ANALIZA_NEURONY podawała rozmiary profili kolejno jako 41/59/35,
    65/65/70 i 75/75/87 — każda prawdziwa w dniu zapisu. Dlatego są wstrzykiwane.
    """
    from imperium.legiony.rejestr import neurony_dla_trybu
    from narzedzia.tabularium import wartosci_z_kodu
    w = wartosci_z_kodu()
    for styl, klucz in (("SCALP", "styl_scalp"), ("SWING", "styl_swing"), ("INVEST", "styl_invest")):
        assert w[klucz] == len(neurony_dla_trybu(styl))
        assert w[klucz] <= w["neurony"], f"{styl}: profil nie może być większy niż rój"


def test_prawa_jeden_parser_dla_calego_imperium():
    """Prawo XVI: jeden format = jeden parser. Audyt (W10) MUSI liczyć praw tak samo.

    Historia: bramka W10 miała liczbę praw ZASZYTĄ i żądała „21", gdy praw było 25 —
    egzekwowała kłamstwo. Potem regex żył w dwóch plikach; dwa parsery tego samego
    formatu rozjadą się co do znaku, a bramka pilnująca prawdy nie może zgadywać.
    """
    from narzedzia.tabularium import policz_prawa, wartosci_z_kodu
    n = policz_prawa()
    assert n > 0, "ZASADY_FUNDAMENTALNE.md nie oddaje żadnego prawa — parser padł?"
    assert wartosci_z_kodu()["prawa"] == n

    # Audyt musi używać TEJ SAMEJ funkcji, nie własnej kopii regexu.
    import narzedzia.audyt_spojnosci as audyt
    zrodlo_audytu = open(audyt.__file__, encoding="utf-8").read()
    assert "policz_prawa" in zrodlo_audytu, \
        "audyt zgubił import policz_prawa — wrócił do własnego regexu (Prawo XVI)"

    # Audyt owija ten import w try/except → cykl importów CICHO wyłączyłby bramkę W10
    # (klasa „bramka cichnie na głucho" z Księgi Wad). Tabularium nie może importować audytu.
    # Szukamy realnego IMPORTU, nie samego słowa: pierwsza wersja tego testu oblała się na
    # własnym KOMENTARZU wspominającym audyt — ta sama klasa, przez którą odrzuciliśmy
    # kandydata `xpath(...)[0]` (wzorzec trafiał we własne komentarze o bugu).
    import re as _re

    import narzedzia.tabularium as tab
    zrodlo_tabularium = open(tab.__file__, encoding="utf-8").read()
    import_audytu = _re.search(r"^\s*(?:from|import)\s+\S*audyt_spojnosci", zrodlo_tabularium, _re.M)
    assert not import_audytu, \
        ("tabularium importuje audyt → cykl → `except` w audycie połknie ImportError "
         "i bramka praw (W10) zamilknie bez śladu")


def test_liczby_pola_logu_sledza_dataclass():
    """PAMIEC_ABSOLUTNA podaje rozmiar schematu ImperiumLog — musi iść za kodem.

    Dokument twierdził „~80 pól" przy 68 w kodzie (zmierzone 2026-07-17). Liczba
    wpisana ręcznie rozjeżdża się z każdym dodanym polem — dlatego jest wstrzykiwana.
    """
    import dataclasses

    from imperium.biblioteki.pamiec_absolutna import ImperiumLog
    from narzedzia.tabularium import wartosci_z_kodu
    assert wartosci_z_kodu()["pola_logu"] == len(dataclasses.fields(ImperiumLog))


def test_liczby_niedomkniety_znacznik_nie_zjada_tekstu():
    """GRANICA (realny incydent 2026-07-17): otwarcie BEZ domknięcia zjadło 44 linie historii.

    Regex z DOTALL i `(.*?)` sklejał osierocone otwarcie z domknięciem NASTĘPNEGO bloku i
    `sub()` kasował całą treść pomiędzy — w tym cudze wpisy. Blok musi kończyć się na własnej
    granicy albo nie dopasować się wcale.
    """
    from narzedzia.tabularium import wartosci_z_kodu, wstrzyknij_liczby
    prawda = wartosci_z_kodu()["neurony"]
    miedzy = "TEKST KTORY MUSI PRZEZYC"
    sciezka = _tymczasowy_dokument(
        "---\nkategoria: TABULA\ntyp: zywy\nwlasciciel: —\nstan_na: 2026-07-17\n"
        "powod_istnienia: test\n---\n\n"
        "Cytat bez domknięcia: <!-- LICZBA:neurony -->\n\n"
        f"{miedzy}\n\n"
        "Prawdziwy blok: <!-- LICZBA:neurony -->999<!-- /LICZBA -->\n")
    try:
        wstrzyknij_liczby(sucho=False)
        with open(sciezka, encoding="utf-8") as f:
            tresc = f.read()
        assert miedzy in tresc, "treść między znacznikami ZJEDZONA — regex przekroczył granicę bloku"
        assert f"<!-- LICZBA:neurony -->{prawda}<!-- /LICZBA -->" in tresc, "domknięty blok ma się odświeżyć"
    finally:
        os.unlink(sciezka)


def test_liczby_nie_dotykaja_historii_acta():
    """Prawo I: wpis datowany cytuje liczbę z DNIA ZAPISU — narzędzie nie może jej podmienić.

    LOG_ZMIAN cytuje `<!-- LICZBA:neurony -->87<!-- /LICZBA -->` w opisie z 2026-07-17. Gdy rój
    urośnie, przepisanie zamieniłoby historyczne 87 na nową liczbę = falsyfikacja historii.
    """
    from narzedzia.tabularium import wstrzyknij_liczby
    sciezka = _tymczasowy_dokument(
        "---\nkategoria: ACTA\ntyp: acta\npowod_acta: test\nwlasciciel: —\n"
        "stan_na: 2026-07-17\npowod_istnienia: test\n---\n\n"
        "Wpis z przeszłości: <!-- LICZBA:neurony -->1<!-- /LICZBA --> neuron.\n")
    try:
        zmiany, bledy = wstrzyknij_liczby(sucho=True)
        assert not any(os.path.basename(sciezka) in z for z in zmiany), \
            f"ACTA nie może być przepisywana: {zmiany}"
        wstrzyknij_liczby(sucho=False)
        with open(sciezka, encoding="utf-8") as f:
            assert "-->1<!-- /LICZBA -->" in f.read(), "historia sfalsyfikowana przez wstrzykiwacz"
    finally:
        os.unlink(sciezka)


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


# ── DROGOWSKAZY_Z_LICZBAMI: README biblioteki wpięty w warstwę liczb (2026-07-21) ──

def test_readme_biblioteki_objety_liczbami_mimo_poza_rejestrem():
    """bibliotheca_ulpia jest w POZA_REJESTREM (T1/T2), ale README biblioteki podaje liczbę
    ksiąg, która gniła niezauważona (69 przy 115, wstyd Cezara). DROGOWSKAZY_Z_LICZBAMI
    wpina go w warstwę liczb — tabularium MUSI wykryć rozjazd bloku LICZBA:ksiazki."""
    import narzedzia.tabularium as tab
    assert "bibliotheca_ulpia/README.md" in tab.DROGOWSKAZY_Z_LICZBAMI
    # README biblioteki realnie ma blok LICZBA:ksiazki i jest zgodny (audyt W15 zielony).
    zmiany, bledy = tab.wstrzyknij_liczby(sucho=True)
    # sucho=True nie zapisuje; brak zmian = zgodność, ale README MUSI być w polu widzenia:
    dokumenty = list(tab.zbierz_dokumenty())
    for wzgl in tab.DROGOWSKAZY_Z_LICZBAMI:
        if __import__("os").path.exists(__import__("os").path.join(tab.ROOT, wzgl)):
            dokumenty.append((wzgl, {}))
    assert any(s == "bibliotheca_ulpia/README.md" for s, _ in dokumenty)
    assert not bledy, f"nieznane klucze liczb: {bledy}"


def test_drogowskaz_nie_wchodzi_do_t1_t2():
    """Drogowskaz bez frontmatter NIE może trafić do T1/T2 (wymagają nagłówka) — tylko liczby.
    zbierz_dokumenty (baza T1/T2) pomija bibliotheca_ulpia całkowicie."""
    import narzedzia.tabularium as tab
    bazowe = [s for s, _ in tab.zbierz_dokumenty()]
    assert not any(s.startswith("bibliotheca_ulpia/") for s in bazowe), \
        "bibliotheca_ulpia nie może wejść do bazy T1/T2 (POZA_REJESTREM)"


# ── ABSTYNENCJA ZAMIAST ZERA: środowisko bez korpusu nie ma głosu (2026-07-26) ──

def test_klucz_abstynujacy_nie_nadpisuje_dokumentu():
    """Klucz o wartości None (środowisko nie mierzy zasobu) MUSI zostawić blok nietknięty.

    Klasa wady zmierzona 2026-07-26 w chmurze: książki są świadomie poza gitem, więc
    `ksiazki_w_bazie()` zwracało 0 nieodróżnialne od zmierzonego zera, a Warstwa 15
    żądała przepisania „115 → 0" w sześciu dokumentach — narzędzie OD PRAWDY namawiało
    do skasowania prawdziwej liczby lokalnej. Granica: None ≠ 0.
    """
    import os
    import tempfile

    import narzedzia.tabularium as tab

    with tempfile.NamedTemporaryFile("w", suffix=".md", dir=tab.ROOT,
                                     delete=False, encoding="utf-8") as f:
        f.write("# Próba\n\nKsiąg: <!-- LICZBA:ksiazki -->115<!-- /LICZBA -->\n")
        sciezka = f.name
    wzgledna = os.path.relpath(sciezka, tab.ROOT)
    oryginal_wartosci = tab.wartosci_z_kodu
    oryginal_drogowskazy = tab.DROGOWSKAZY_Z_LICZBAMI
    oryginal_zbierz = tab.zbierz_dokumenty
    try:
        # IZOLACJA OD PRODUKCJI (naprawa mojego własnego błędu, 2026-07-26): pierwsza
        # wersja tego testu DOPISYWAŁA plik tymczasowy do prawdziwej listy i wołała
        # `wstrzyknij_liczby(sucho=False)`, więc faza „zmierzone zero" przepisała ZERAMI
        # sześć produkcyjnych dokumentów (MAPA_PAMIECI, ARCHITEKTURA, README biblioteki…).
        # Dokładnie klasa złapana 07-21 („tryb testowy mutujący trwały rejestr") — test
        # pisze WYŁĄCZNIE do swojego pliku, nigdy do repozytorium.
        tab.zbierz_dokumenty = lambda: []
        tab.DROGOWSKAZY_Z_LICZBAMI = [wzgledna]

        # 1) ABSTYNENCJA (None) — dokument nietknięty, zero zgłoszonych zmian.
        tab.wartosci_z_kodu = lambda: {**oryginal_wartosci(), "ksiazki": None}
        zmiany, bledy = tab.wstrzyknij_liczby(sucho=False)
        with open(sciezka, encoding="utf-8") as f:
            assert "-->115<!--" in f.read(), "abstynencja skasowała zmierzoną liczbę"
        assert not any(wzgledna in z for z in zmiany), "abstynencja zgłoszona jako rozjazd"
        assert not bledy

        # 2) ZMIERZONE ZERO (0) — nadal MUSI nadpisać: to prawdziwy pomiar, nie milczenie.
        tab.wartosci_z_kodu = lambda: {**oryginal_wartosci(), "ksiazki": 0}
        zmiany, _ = tab.wstrzyknij_liczby(sucho=False)
        with open(sciezka, encoding="utf-8") as f:
            assert "-->0<!--" in f.read(), "zmierzone 0 musi nadpisać (to pomiar)"
        assert any(wzgledna in z for z in zmiany)
    finally:
        tab.wartosci_z_kodu = oryginal_wartosci
        tab.DROGOWSKAZY_Z_LICZBAMI = oryginal_drogowskazy
        tab.zbierz_dokumenty = oryginal_zbierz
        os.unlink(sciezka)


def test_korpus_ksiazek_obecny_zgodny_z_liczba():
    """`korpus_ksiazek_obecny()` musi być spójny z `ksiazki_w_bazie()` w KAŻDYM środowisku
    (chmura: brak korpusu → False; lokal: 115 ksiąg → True). Jedno źródło prawdy."""
    from imperium.biblioteki.srodowisko_pamieci import (
        korpus_ksiazek_obecny, ksiazki_w_bazie,
    )
    assert korpus_ksiazek_obecny() == (ksiazki_w_bazie() > 0)
