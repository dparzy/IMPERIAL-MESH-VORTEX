"""Testy NOMENCLATORA — strażnika imion (warstwa 2 anty-redundancyjna Hyginusa).

Organ powstał 2026-07-27 z PRZENIESIENIA działającego detektora, nie z nowego pomysłu.
Dlatego testy pilnują dwóch rzeczy naraz: że detektor działa, ORAZ że nie istnieje
w dwóch egzemplarzach — bo rozjazd kopii byłby cichy i zepsułby A/B, które ma go walidować.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.pretorianie import nomenclator as nom  # noqa: E402


def test_lapie_kandydata_ktory_dublowal_Z01():
    """Przypadek Z HISTORII, nie wymyślony: VPIN_TOKSYCZNOSC przeszedł przez A/B jako „nowy",
    choć dublował Z-01 (NeuronToxicFlow, wskaźnik VPIN_50). Ślepota `\\bvpin\\b` na podkreślenie
    przekręciła cały werdykt U4 — to jest ten kandydat, który obalił tezę −12 pp."""
    w = nom.sprawdz("1. **Kandydat: VPIN_TOKSYCZNOSC**\n- opis\n")
    assert w["czysty"] is False
    assert w["podejrzanych"] == 1
    assert r"\bvpin\b" in w["podejrzani"][0]["pojecia"]


def test_nazwa_bez_dubletu_nie_jest_oskarzana():
    """Fałszywe oskarżenie jest droższe niż przeoczenie: sędzia, który raz odrzuci dobrego
    kandydata przez szumiący detektor, przestanie ufać całemu organowi."""
    w = nom.sprawdz("1. **Kandydat: LEJEK_PLYNNOSCI_MIEDZYGIELDOWEJ**\n- opis\n")
    assert w["czysty"] is True
    assert w["podejrzanych"] == 0


def test_zaprzeczenie_w_ciele_NIE_oskarza():
    """SEDNO MIARY (błąd pomiarowy zmierzony 2026-07-21): kandydat, który uczciwie pisze
    „istnieje V-03 CVD, ale to co innego", wymienia nasz moduł W CIELE. Liczenie wzmianek
    karałoby go za znajomość Imperium — czyli dokładnie za to, czego od niego chcemy."""
    tekst = ("1. **Kandydat: NIERÓWNOWAGA_KSIĄŻKI_ZLECEŃ**\n"
             "- nie dubluje: istnieje CVD oraz kelly, ale to inne pojęcia\n")
    w = nom.sprawdz(tekst)
    assert w["czysty"] is True, "detektor przeczytał ciało bloku zamiast nazwy"


def test_liczy_kazdego_kandydata_osobno():
    tekst = ("1. Kandydat: HURST_REZIMOWY\n- opis\n"
             "2. Kandydat: NOWE_POJECIE_XYZ\n- opis\n"
             "3. Kandydat: ICHIMOKU_ADAPTACYJNY\n- opis\n")
    w = nom.sprawdz(tekst)
    assert w["kandydatow"] == 3
    assert w["podejrzanych"] == 2


def test_do_slownika_ma_ksztalt_probatora():
    """Ten sam kształt co PROBATOR — BREVIARIUM i raporty liczą podejrzanych bez zaglądania
    do wnętrza organu. Rozjazd kształtu zepsułby meldunki po cichu."""
    d = nom.do_slownika(nom.sprawdz("1. Kandydat: KELLY_ULAMKOWY\n- opis\n"))
    assert d["status"] == "podejrzany"
    assert d["kandydatow"] == 1 and d["podejrzanych"] == 1
    assert d["pojecia"] == [r"\bkelly\b"]
    assert all(not isinstance(v, (list, dict)) for k, v in d.items() if k != "pojecia")


def test_pusty_plon_nie_wywala_organu():
    """Zwiad bywa pusty (status 'pusto'/'dry'). Strażnik nie ma prawa przewrócić cząstki."""
    for pusty in ("", "   \n  ", None):
        w = nom.sprawdz(pusty or "")
        assert w["czysty"] is True and w["kandydatow"] == 0


def test_leksykon_nie_klamie_o_kodzie():
    """Prawo I: każdy wpis musi mieć DOWÓD w żywym kodzie. Niepusta lista = wpis
    przeterminowany, czyli detektor oskarżałby o posiadanie czegoś, czego nie mamy."""
    assert nom.niezweryfikowane() == [], "leksykon wskazuje moduły nieobecne w kodzie"
    assert len(nom.leksykon_roju()) >= 30


def test_samodowod_leksykonu_jest_wykluczony():
    """MUTACJA NA STRAŻNIKU SAMO-DOWODU. Weryfikacja czytająca własną deklarację jako dowód
    to bramka, która przy awarii wygląda na sprawną (zmierzone 2026-07-21). Po przeniesieniu
    do organu ryzyko NIE ZNIKŁO, tylko się przeprowadziło: gdyby korpus objął stanowisko
    pomiarowe, proza o mierzonych pojęciach („kandydat VPIN_TOKSYCZNOSC dublował Z-01")
    dowodziłaby ich istnienia zamiast kodu.

    Test podaje pojęcie-widmo, którego dowód pada WYŁĄCZNIE w wykluczonych plikach."""
    widmo = r"\bpojecie-widmo-nomenclatora\b"
    nom.KONCEPTY_IMPERIUM[widmo] = "pojecie_widmo_ktorego_nie_ma_w_kodzie"
    nom._korpus_kodu.cache_clear()
    nom.leksykon_roju.cache_clear()
    try:
        assert widmo in nom.niezweryfikowane(), "weryfikacja przepuszcza pojęcie-widmo"
        assert widmo not in [w for w, _ in nom.leksykon_roju()], "widmo weszło do leksykonu"
    finally:
        del nom.KONCEPTY_IMPERIUM[widmo]
        nom._korpus_kodu.cache_clear()
        nom.leksykon_roju.cache_clear()


def test_wykluczone_pliki_naprawde_sa_pomijane():
    """GRANICA WYKLUCZENIA liczona ze ŹRÓDŁA, nie luźnym progiem. Lekcja z 07-27: asercja
    „zbadane >= N+40" przeżyła mutację zawężenia zasięgu 73→65, bo mierzyła własną wygodę.
    Tu żądamy RÓWNOŚCI z liczbą policzoną z dysku."""
    nom._korpus_kodu.cache_clear()
    wszystkie = [s for k in ("imperium", "narzedzia")
                 for s in (ROOT / k).rglob("*.py") if "__pycache__" not in str(s)]
    oczekiwane = len([s for s in wszystkie if s.name not in nom._POZA_KORPUSEM])
    assert len(wszystkie) - oczekiwane == len(nom._POZA_KORPUSEM), \
        "wykluczone pliki nie istnieją albo są policzone podwójnie"
    # Treść wykluczonych NIE MOŻE być w korpusie — sprawdzamy po unikalnym znaczniku.
    korpus = nom._korpus_kodu()
    assert "nomenclator — strażnik imion imperium" not in korpus
    assert "libra messis — waga plonu" not in korpus


def test_detektor_ISTNIEJE_W_JEDNYM_EGZEMPLARZU():
    """ANTY-ROZJAZD (Prawo XVI) — najważniejszy test tego pliku.

    Detektor jest jednocześnie NARZĘDZIEM POMIARU (A/B, które waliduje wpięcie) i CZĘŚCIĄ
    ZWIADU (adnotacja dla sędziego). Gdyby istniał w dwóch kopiach, A/B mierzyłoby inny
    detektor niż ten wpięty w produkcję, a rozjazd byłby CICHY: obie kopie przechodziłyby
    własne testy. Dlatego żądamy TOŻSAMOŚCI obiektów, nie równości zachowań.
    """
    import narzedzia.ab_plon_hyginusa as lm
    for nazwa in ("policz_duplikaty", "podziel_kandydatow", "leksykon_roju",
                  "niezweryfikowane", "_korpus_kodu", "_do_dopasowania", "_naglowek_bloku"):
        assert getattr(lm, nazwa) is getattr(nom, nazwa), \
            f"{nazwa} istnieje w dwóch egzemplarzach — pomiar rozjedzie się z produkcją"
    assert lm.KONCEPTY_IMPERIUM is nom.KONCEPTY_IMPERIUM


def test_sprawdz_zgadza_sie_z_policz_duplikaty():
    """Werdykt dla sędziego i liczba dla A/B muszą pochodzić z tej samej prawdy — inaczej
    raport mówiłby sędziemu co innego niż pomiar pokazuje Cezarowi."""
    tekst = ("1. Kandydat: VWAP_KROCZACY\n- opis\n"
             "2. Kandydat: COS_ZUPELNIE_INNEGO\n- opis\n")
    lex = nom.leksykon_roju()
    dubel, bloki, _ = nom.policz_duplikaty(tekst, lex)
    w = nom.sprawdz(tekst)
    assert (w["podejrzanych"], w["kandydatow"]) == (dubel, bloki)


def test_etykieta_naglowka_nie_lapie_polskiej_odmiany():
    """Recenzja cubic PR #134, zweryfikowana pomiarem: `kandydat\\w*` wpuszczał odmianę
    z prozy jako nowy nagłówek, zawyżając licznik kandydatów i mianownik odsetka duplikatów.

    Test trzyma OBIE strony granicy — wspierane formy muszą dalej działać, bo zawężenie
    wzorca „na wszelki wypadek" zepsułoby miarę w drugą stronę (klasa z Księgi Wad:
    lekarstwem na zły próg nie jest jego przesunięcie, tylko test właściwy rodzajowi)."""
    for dobre in ("Kandydat: X", "Kandydat A: X", "Kandydat 1: X",
                  "### Kandydat A: X", "- **Kandydat: X**"):
        assert nom._NAGLOWEK.match(dobre), f"wspierany format przestał działać: {dobre!r}"
    for proza in ("Kandydatura: opis", "Kandydatem jest VPIN: tak",
                  "Kandydaci: lista", "Kandydata nie ma: pusto"):
        assert not nom._NAGLOWEK.match(proza), f"proza uznana za nagłówek: {proza!r}"


def test_wzorce_leksykonu_sie_kompiluja():
    """Literówka w regexie leksykonu wywaliłaby zwiad PO zapłaceniu za skan DeepSeekiem."""
    for wzor in nom.KONCEPTY_IMPERIUM:
        re.compile(wzor)
