"""Testy sprzężenia Dziennik ↔ INDEX FALSORUM — obalone twierdzenie nie wraca samo.

POWÓD (zmierzone 2026-07-27, pytanie Cezara „co znaczy 4 z 9"): Dziennik Nieśmiertelny jest
wstrzykiwany W CAŁOŚCI do kontekstu na starcie KAŻDEJ sesji, a INDEX FALSORUM świadomie pomija
katalogi kronik — w tym `bibliotheca_ulpia/dane`, gdzie Dziennik leży. Jedyny korpus czytany
na pewno co rano był jedynym, którego strażnik fałszów nie skanował. Skutek zmierzony na
żywym Dzienniku: **5 wpisów ze 130** głosiło twierdzenia już obalone (3× „backtest kwadratowy",
1× nieistniejąca właściwość `rules`, 1× „~9 zdarzeń hooka") i wracało jako fakt.

Historii NIE przepisujemy (Prawo I) — testy pilnują, że wpis zostaje słowo w słowo,
a zmienia się wyłącznie to, co mu TOWARZYSZY.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.biblioteki import dziennik_niesmiertelny as dz  # noqa: E402
from imperium.biblioteki import index_falsorum as idf  # noqa: E402

WPIS_Z_FALSZEM = [{"fraza": r"ziemia jest plaska", "poprawna_teza": "Ziemia jest kulą",
                   "obalone_przez": "pomiar", "data": "2026-07-27"}]


def test_tekst_glaszacy_obalone_twierdzenie_jest_wykryty():
    traf = idf.trafienia_w_tekscie("Jak wiadomo ziemia jest plaska i tyle.", wpisy=WPIS_Z_FALSZEM)
    assert len(traf) == 1
    assert traf[0]["poprawna_teza"] == "Ziemia jest kulą"


def test_negacja_PRZY_frazie_ucisza_alarm():
    """„nie jest płaska" to sprostowanie, nie głoszenie — inaczej karalibyśmy za korektę.

    PIERWSZA WERSJA TEGO TESTU BYŁA ATRAPĄ i wykryła to dopiero MUTACJA (2026-07-27).
    Używała frazy dosłownej `ziemia jest plaska`, która do zdania „ziemia NIE jest plaska"
    po prostu NIE PASUJE — test przechodził, bo regex nie trafiał, a nie dlatego, że
    negacja go uciszała. Usunięcie `_negacja_przy` z kodu niczego nie psuło. Właściwa
    próba wymaga frazy, która trafia MIMO wstawionego „NIE" — dopiero wtedy sprawdzamy
    to, co deklarujemy (lekcja: gdy mutacja przeżyje, ustal KTO naprawdę broni).
    """
    # `.{0,12}`, NIE `\W{0,12}` — druga wersja też była atrapą i też złapała ją mutacja:
    # `\W` nie obejmuje liter, więc wstawione „NIE" rozrywało wzorzec i regex znowu nie
    # trafiał. Fraza musi PRZEKRACZAĆ negację, żeby test w ogóle dotknął `_negacja_przy`.
    rozciagliwa = [{"fraza": r"ziemia.{0,12}plaska", "poprawna_teza": "Ziemia jest kulą",
                    "obalone_przez": "pomiar", "data": "2026-07-27"}]
    assert idf.trafienia_w_tekscie("Wiemy, ze ziemia NIE plaska.", wpisy=rozciagliwa) == [], \
        "negacja przy frazie przestała uciszać — sprostowanie byłoby karane jak głoszenie"
    # GRANICA DRUGIEJ STRONY: bez negacji ta sama fraza MUSI dać alarm, inaczej test
    # udowadniałby tylko, że wzorzec nie działa.
    assert len(idf.trafienia_w_tekscie("Wiemy, ze ziemia plaska.", wpisy=rozciagliwa)) == 1


def test_OKNO_prostujace_jest_DOMYSLNIE_WYLACZONE():
    """SEDNO WADY ZŁAPANEJ PRZY BUDOWIE: pierwsza wersja nie wykryła NICZEGO.

    Wpis Dziennika to nie proza — jedna „linia" niesie cały akapit o wielu tematach. We wpisie
    `nomen27` linia z „OBALON" dotyczyła U4, a uciszała fałszywą liczbę zdarzeń hooka stojącą
    linię wyżej. Sprostowanie musi stać PRZY frazie, nie gdziekolwiek w sąsiedztwie tematu.
    """
    tekst = "ziemia jest plaska\ncos zupelnie innego zostalo OBALONE w tej wachcie"
    assert len(idf.trafienia_w_tekscie(tekst, wpisy=WPIS_Z_FALSZEM)) == 1, \
        "okno prostujące znowu ucisza fałsz sąsiedztwem o INNYM temacie"
    assert idf.trafienia_w_tekscie(tekst, wpisy=WPIS_Z_FALSZEM, okno_prostujace=True) == [], \
        "tryb okna przestał działać — `przeszukaj` polega na tej samej heurystyce"


def test_jedno_ostrzezenie_na_twierdzenie_nie_na_wystapienie():
    """Wpis powtarzający frazę pięć razy ma dostać JEDNO sprostowanie, nie pięć."""
    tekst = "ziemia jest plaska. " * 5
    assert len(idf.trafienia_w_tekscie(tekst, wpisy=WPIS_Z_FALSZEM)) == 1


def test_wpis_dziennika_dostaje_adnotacje_a_TRESC_zostaje_nietknieta(monkeypatch):
    """Prawo I: historii nie falsyfikujemy. Zmienia się TOWARZYSTWO wpisu, nie wpis."""
    monkeypatch.setattr(idf, "aktywne", lambda *a, **k: WPIS_Z_FALSZEM)
    wpis = {"data": "2026-01-01", "sesja": "test", "co": ["ustalono, ze ziemia jest plaska"],
            "decyzje": [], "nastepny": "dalej"}
    blok = dz._formatuj_wpis(wpis)
    assert "ustalono, ze ziemia jest plaska" in blok, "treść historyczna została zmieniona!"
    assert "OBALONE (INDEX FALSORUM): Ziemia jest kulą" in blok
    assert blok.index("ustalono") < blok.index("OBALONE"), "sprostowanie ma iść PO wpisie"


def test_czysty_wpis_nie_dostaje_zadnej_adnotacji(monkeypatch):
    """CISZA GDY ZIELONE — inaczej 130 wpisów utopiłoby prawdziwe ostrzeżenia w szumie."""
    monkeypatch.setattr(idf, "aktywne", lambda *a, **k: WPIS_Z_FALSZEM)
    wpis = {"data": "2026-01-01", "sesja": "test", "co": ["zwykla praca"], "decyzje": []}
    assert "OBALONE" not in dz._formatuj_wpis(wpis)


def test_awaria_straznika_NIE_wywala_Dziennika(monkeypatch):
    """Bez osi czasu Architekt traci ciągłość całego projektu — to koszt nieporównanie
    większy niż brak jednej adnotacji. Strażnik ma prawo zamilknąć, nie zabić Dziennika."""
    def wybuch(*a, **k):
        raise RuntimeError("ledger uszkodzony")
    monkeypatch.setattr(idf, "trafienia_w_tekscie", wybuch)
    wpis = {"data": "2026-01-01", "sesja": "test", "co": ["ziemia jest plaska"], "decyzje": []}
    blok = dz._formatuj_wpis(wpis)
    assert "ziemia jest plaska" in blok and "OBALONE" not in blok


def test_zywy_dziennik_prostuje_realne_falsze():
    """Test na ŻYWYM korpusie: zmierzone 5 wpisów ze 130 głosiło obalone twierdzenia.

    Asercja jest na „>= 1", nie na dokładnej liczbie — spis obalonych rośnie, a test ma
    bronić MECHANIZMU, nie utrwalać stanu ledgera z jednego dnia."""
    osx = dz.os_czasu()
    assert "OBALONE (INDEX FALSORUM)" in osx, \
        "żywy Dziennik przestał być prostowany — obalone twierdzenia wracają jako fakt"
