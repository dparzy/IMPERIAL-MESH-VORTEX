"""Testy DISCRIMINATORA — organu orzekającego, czy skupisko to naprawdę redundancja.

Rdzeń jest czysty (serie to DANE, nie źródła), więc każdy werdykt da się sprawdzić bez
świec, bez Bramy i bez dysku. Granice utrwalone tu pochodzą z PIERWSZEGO biegu na żywych
danych (BTCUSDT 4h, 2026-07-31), nie z wyobraźni.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.legiony import discriminator as d  # noqa: E402

KORZEN = Path(__file__).resolve().parent.parent


class _Sygnal:
    def __init__(self, kierunek="NEUTRAL", pewnosc=0.0, pewnosc_przeciwnika=0.0):
        self.kierunek = kierunek
        self.pewnosc = pewnosc
        self.pewnosc_przeciwnika = pewnosc_przeciwnika


# ── Zamiana głosu na liczbę ──────────────────────────────────────────────────────

def test_long_dodatni_short_ujemny():
    assert d.sygnal_na_liczbe(_Sygnal("LONG", 0.7)) == 0.7
    assert d.sygnal_na_liczbe(_Sygnal("SHORT", 0.7)) == -0.7
    assert d.sygnal_na_liczbe(_Sygnal("NEUTRAL", 0.0)) == 0.0


def test_neuron_defensywny_nie_jest_niemy():
    """Granica: NEUTRAL z pewnością przeciwnika to TŁUMIENIE, nie brak głosu.

    Bez tego neurony defensywne (Amihud) miałyby stałą serię zer i organ ogłaszałby
    ciszę tam, gdzie moduł pracuje.
    """
    assert d.sygnal_na_liczbe(_Sygnal("NEUTRAL", 0.0, pewnosc_przeciwnika=0.6)) == -0.6


def test_brak_pol_nie_wywraca_odczytu():
    assert d.sygnal_na_liczbe(object()) == 0.0


# ── Werdykt pary — progi Prawa XVI ───────────────────────────────────────────────

def test_pary_idealnie_zgodne_to_kandydat_do_scalenia():
    w = d.ocen_pare("A", "B", [1.0, -1.0, 0.5, -0.5], [1.0, -1.0, 0.5, -0.5])
    assert w["werdykt"] == "KANDYDAT_DO_SCALENIA"
    assert w["korelacja"] == 1.0


def test_pary_przeciwstawne_tez_sa_kandydatem():
    """|r| — antykorelacja niesie tę samą informację z odwróconym znakiem."""
    w = d.ocen_pare("A", "B", [1.0, -1.0, 0.5, -0.5], [-1.0, 1.0, -0.5, 0.5])
    assert w["werdykt"] == "KANDYDAT_DO_SCALENIA"
    assert w["korelacja"] == -1.0


def test_para_nieskorelowana_to_filar():
    w = d.ocen_pare("A", "B", [1.0, -1.0, 1.0, -1.0], [1.0, 1.0, -1.0, -1.0])
    assert w["werdykt"] == "FILAR_DYWERSYFIKACJI"


def test_strefa_posrednia_nie_udaje_werdyktu():
    w = d.ocen_pare("A", "B", [1.0, 0.9, -1.0, -0.2, 0.3], [1.0, 0.1, -0.6, 0.4, 0.2])
    assert w["werdykt"] in {"POSREDNIE", "FILAR_DYWERSYFIKACJI", "KANDYDAT_DO_SCALENIA"}
    assert w["korelacja"] is not None


def test_granica_progu_redundancji_jest_ostra():
    """Próg jest OSTRY (>0.80), więc dokładnie 0.80 NIE jest jeszcze kandydatem."""
    assert d.PROG_REDUNDANCJI == 0.80
    assert d.PROG_DYWERSYFIKACJI == 0.20


# ── Cisza: stan faktyczny, nie oskarżenie ───────────────────────────────────────

def test_staly_glos_daje_cisze_a_nie_zerowa_korelacje():
    """Sedno: Pearson na stałej serii jest niezdefiniowany. Gdyby organ wpisał tam 0.0,
    milczący neuron udawałby filar dywersyfikacji — czyli cisza czytana jako zaleta."""
    w = d.ocen_pare("MILCZEK", "B", [0.0, 0.0, 0.0, 0.0], [1.0, -1.0, 0.5, -0.5])
    assert w["werdykt"] == "CISZA_W_POMIARZE"
    assert w["korelacja"] is None
    assert w["martwe"] == ["MILCZEK"]


def test_cisza_wykrywa_kazda_stala_wartosc_nie_tylko_zero():
    w = d.ocen_pare("A", "B", [0.4, 0.4, 0.4], [1.0, -1.0, 0.5])
    assert w["werdykt"] == "CISZA_W_POMIARZE"


def test_obaj_milczacy_sa_wymienieni():
    w = d.ocen_pare("A", "B", [0.0, 0.0], [0.0, 0.0])
    assert sorted(w["martwe"]) == ["A", "B"]


def test_jedna_probka_nie_dowodzi_stalego_glosu():
    """D1 (cubic PR #138): przy 0 lub 1 obserwacji „stały głos" jest artefaktem DŁUGOŚCI
    serii, nie własnością neuronu — a organ dopisywał go do martwych głosów.

    Skutek był realny: przy `limit <= od` (za mało barów po rozgrzewce) KAŻDA para
    wracała jako CISZA_W_POMIARZE i cały rój wyglądał na niemy.
    """
    for seria in ([], [0.5]):
        w = d.ocen_pare("A", "B", list(seria), list(seria))
        assert w["werdykt"] == "NIEROZSTRZYGNIETE", w
        assert w["martwe"] == [], w


def test_awaria_nie_udaje_glosu_neutral():
    """D3 (cubic PR #138): wyjątek z `interpretuj` lądował w serii jako 0.0 — identycznie
    jak uczciwy NEUTRAL. Tu bary z awarią są usuwane PARAMI i nie ruszają korelacji."""
    # Dane dobrane tak, by MUTACJA BYŁA WIDOCZNA: na wspólnych czterech barach neurony są
    # identyczne (r=1,0 → KANDYDAT), ale gdyby awarie policzyć jako 0.0, dwa mocne głosy
    # partnera rozcieńczyłyby korelację do ~0,27, czyli do strefy pośredniej. Bez tego
    # doboru test przechodzi także dla WADLIWEJ wersji — sprawdzone mutacją.
    a = [None, None, 1.0, -1.0, 1.0, -1.0]
    b = [5.0, -5.0, 1.0, -1.0, 1.0, -1.0]
    w = d.ocen_pare("ZEPSUTY", "B", a, b)
    assert w["werdykt"] == "KANDYDAT_DO_SCALENIA", w
    assert w["korelacja"] == 1.0, w
    assert w["martwe"] == []


def test_neuron_stale_awaryjny_nie_jest_nazwany_cichym():
    """Granica rozłączności: awaria trwała dawała stałą serię zer, więc organ ogłaszał
    CISZĘ — czyli neuron ZEPSUTY wyglądał dokładnie jak neuron bez wejścia. To ta sama
    para pojęć, dla której rozróżnienia ten organ powstał."""
    w = d.ocen_pare("ZEPSUTY", "B", [None, None, None, None], [1.0, -1.0, 1.0, -1.0])
    assert w["werdykt"] == "NIEROZSTRZYGNIETE", w
    assert w["martwe"] == [], w


def test_awarie_ida_do_wyniku_osobno_od_ciszy():
    w = d.ocen_skupisko("T/trend",
                        {"X-01": [1.0, -1.0, 1.0], "X-02": [0.0, 0.0, 0.0]},
                        {"X-01": 5, "X-02": 0})
    assert w["awaryjne"] == {"X-01": 5}
    assert w["martwe_glosy"] == ["X-02"]


def test_raport_oskarza_awarie_choc_nie_oskarza_ciszy():
    """Jedyne OSKARŻENIE w tym raporcie: awaria. Cisza pozostaje stanem faktycznym."""
    tekst = d.raport([d.ocen_skupisko(
        "T/trend", {"X-01": [1.0, -1.0, 1.0], "X-02": [0.0, 0.0, 0.0]}, {"X-01": 5})])
    assert "AWARYJNE" in tekst
    assert "X-01×5" in tekst


def test_serie_roznej_dlugosci_sa_bledem_a_nie_cichym_ucieciem():
    """`zip` bez `strict` cicho ucinał dłuższą serię — rozjazd długości to wada danych,
    nie rzecz do przemilczenia (ta sama zasada, co zip(strict) w Bramie)."""
    try:
        d.ocen_pare("A", "B", [1.0, -1.0, 1.0], [1.0, -1.0])
        raise AssertionError("rozjazd długości serii przeszedł bez słowa")
    except ValueError:
        pass


def test_cisza_nie_jest_liczona_jako_filar():
    """Granica z PIERWSZEGO biegu: 27 z 66 neuronów milczało (brak alt-danych w CSV).
    Gdyby cisza wpadała do filarów, skupisko K/macro raportowałoby dywersyfikację
    zbudowaną wyłącznie z niemych modułów."""
    w = d.ocen_skupisko("K/macro", {"K-03": [0.0, 0.0, 0.0], "K-04": [0.0, 0.0, 0.0]})
    assert w["filarow"] == 0
    assert w["kandydatow_do_scalenia"] == 0
    assert w["martwe_glosy"] == ["K-03", "K-04"]


# ── Skupisko ────────────────────────────────────────────────────────────────────

def test_skupisko_liczy_wszystkie_pary():
    serie = {"A": [1.0, -1.0, 0.5], "B": [1.0, -1.0, 0.4], "C": [-1.0, 1.0, -0.5]}
    w = d.ocen_skupisko("T/trend", serie)
    assert w["par"] == 3            # 3 neurony → 3 pary
    assert w["neurony"] == ["A", "B", "C"]
    assert sum(w["licznik"].values()) == 3


def test_skupisko_jednoelementowe_nie_ma_par():
    w = d.ocen_skupisko("X/y", {"A": [1.0, -1.0]})
    assert w["par"] == 0
    assert w["kandydatow_do_scalenia"] == 0


def test_skupiska_pochodza_z_zywego_rejestru():
    """Organ NIE trzyma własnej listy skupisk — czyta ją z rejestru (jedno źródło prawdy)."""
    s = d.skupiska()
    assert isinstance(s, dict) and s, "rejestr nie zwrócił żadnego skupiska"
    assert all(len(v) >= 2 for v in s.values()), "skupisko z <2 neuronami nie ma sensu"


# ── Zbieranie serii: okno pomiaru i rozgrzewka ──────────────────────────────────
#
# `zbierz_serie` nie miała dotąd ANI JEDNEGO testu — cały organ był sprawdzany od strony
# czystego rdzenia (`ocen_pare`/`ocen_skupisko`), a wady D2 i D4 siedziały właśnie w tej
# jedynej funkcji, która dotyka barów. To sama w sobie lekcja o zasięgu bramki.

class _NeuronAtrapa:
    """Neuron, którego głos MÓWI, ile barów zobaczył — dzięki temu okno pomiaru jest
    widoczne w samej serii, a nie tylko w liczniku postępu."""

    def __init__(self, klucz="X-01"):
        self.KLUCZ = klucz

    def interpretuj(self, wskazniki):
        return _Sygnal("LONG", wskazniki["ile_barow"])


class _BudowniczyAtrapa:
    def zbuduj(self, bary):
        return {"ile_barow": len(bary)}


def _zbierz(bary, od, klucz="X-01", postep=None):
    """Uruchamia `zbierz_serie` na atrapach — bez świec, bez dysku, bez Bramy."""
    oryginal = d.wszystkie_neurony
    d.wszystkie_neurony = lambda: [_NeuronAtrapa(klucz)]
    try:
        return d.zbierz_serie(bary, [klucz], _BudowniczyAtrapa(), od=od, postep=postep)
    finally:
        d.wszystkie_neurony = oryginal


def test_ostatni_zamkniety_bar_wchodzi_do_pomiaru():
    """D2 (cubic PR #138): `range(od, len(bary))` nigdy nie wołało `zbuduj` z PEŁNYM
    wycinkiem, więc najświeższy bar — ten, na którym rój głosowałby w produkcji —
    nie był badany ani razu.

    Test jest tak dobrany, by MUTACJA BYŁA WIDOCZNA: głos niesie długość wycinka, więc
    brak ostatniego bara widać wprost w ostatniej wartości serii, a nie tylko w liczbie
    obserwacji (którą łatwo przeoczyć).
    """
    serie, _ = _zbierz(list(range(10)), od=8)
    assert serie["X-01"] == [8.0, 9.0, 10.0], serie
    assert max(serie["X-01"]) == 10, "ostatni bar nie wszedł do pomiaru"


def test_rozgrzewka_rowna_dlugosci_danych_daje_jeden_glos():
    """Granica dolna: przy `len(bary) == od` jest dokładnie jedno pełne okno."""
    serie, _ = _zbierz(list(range(5)), od=5)
    assert serie["X-01"] == [5.0], serie


def test_za_krotkie_dane_nie_daja_glosu_ani_wyjatku():
    """Rozgrzewka dłuższa niż dane to brak pomiaru — nie błąd i nie zmyślony głos."""
    serie, awarie = _zbierz(list(range(3)), od=10)
    assert serie["X-01"] == [], serie
    assert awarie["X-01"] == 0


def test_puste_dane_nie_daja_glosu_z_pustego_okna():
    """Granica, którą `+1` mogłoby otworzyć: przy `od=0` i braku barów naiwny zakres
    dałby JEDEN krok z pustym wycinkiem, czyli głos policzony z niczego."""
    serie, _ = _zbierz([], od=0)
    assert serie["X-01"] == [], serie


def test_licznik_postepu_zapowiada_tyle_krokow_ile_wykonano():
    """Rozjazd „ile kroków zapowiadam" vs „ile wykonuję" BYŁ tu źródłem wady D2 —
    dlatego zakres i licznik liczą się teraz z jednej wielkości."""
    widziane = []
    serie, _ = _zbierz(list(range(30)), od=4, postep=lambda i, ile: widziane.append((i, ile)))
    assert widziane, "pasek postępu nie odezwał się ani razu"
    ostatni_krok, zapowiedziane = widziane[-1]
    assert ostatni_krok == zapowiedziane == len(serie["X-01"]), widziane


def test_ujemna_rozgrzewka_jest_bledem_a_nie_pomiarem():
    """D4 (cubic PR #138): `od=-5` dawało wycinki `bary[:-5]` i `bary[:0]` — wynik, który
    wygląda jak pomiar, a mierzy co innego, niż deklaruje."""
    try:
        _zbierz(list(range(10)), od=-1)
        raise AssertionError("ujemna rozgrzewka przeszła bez słowa")
    except ValueError:
        pass


def test_ujemne_wejscie_odrzucane_PRZED_wczytaniem_danych():
    """Recenzja żąda odrzucenia „before entering zbierz_serie" — więc dowodem jest to,
    że przy ŚCIEŻCE NIEISTNIEJĄCEJ dostajemy zarzut o `od`, a nie błąd czytania pliku.
    Gdyby walidacja siedziała tylko w środku, najpierw poleciałby dysk."""
    for kwargs in ({"od": -1}, {"od": 360, "limit": -5}):
        try:
            d.zbadaj("nie/ma/takiego/pliku.csv", "4h", **kwargs)
            raise AssertionError(f"ujemne wejście przeszło bez słowa: {kwargs}")
        except ValueError as e:
            assert "ujemn" in str(e).lower(), (kwargs, e)


def test_json_z_cli_da_sie_wczytac():
    """Złapane przy powtórce pomiaru D2 (2026-08-02): pasek postępu szedł na STDOUT
    razem z wynikiem, więc `--json` zwracał strumień, którego `json.load` nie wczyta —
    organ psuł własny wydruk. Strumień diagnostyczny nie ma prawa mieszać się z danymi.

    Okno jest minimalne z rozmysłu: sprawdzamy KONTRAKT WYDRUKU, nie wartości korelacji.
    """
    dane = KORZEN / "dane" / "4h" / "Binance_BTCUSDT_4h.csv"
    if not dane.exists():
        return  # dane historyczne bywają poza repo — brak pliku to nie wada organu
    p = subprocess.run([sys.executable, "-m", "imperium.legiony.discriminator",
                        "--dane", str(dane), "--limit", "363", "--od", "360", "--json"],
                       cwd=KORZEN, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    assert p.returncode == 0, p.stderr[-2000:]
    wynik = json.loads(p.stdout)          # sedno testu: MUSI się wczytać
    assert isinstance(wynik, list) and wynik, p.stdout[:500]
    assert "barów" in p.stderr, "pasek postępu zniknął zamiast przenieść się na stderr"


def test_cli_odrzuca_ujemne_okno():
    """D4 od strony CLI: komunikat argparse, nie traceback (recenzja żąda obu ścieżek)."""
    p = subprocess.run([sys.executable, "-m", "imperium.legiony.discriminator",
                        "--od", "-1", "--lista"],
                       cwd=KORZEN, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    assert p.returncode != 0
    assert "ujemna" in p.stderr.lower(), p.stderr[-500:]
    assert "Traceback" not in p.stderr, p.stderr[-500:]


# ── Raport ──────────────────────────────────────────────────────────────────────

def test_raport_nie_oskarza_ciszy():
    """Wydruk MUSI mówić, że cisza w tym pomiarze nie jest jeszcze zarzutem — inaczej
    ograniczenie przyrządu (brak alt-danych) czytałoby się jak alarm Prawa XV."""
    w = [d.ocen_skupisko("K/macro", {"K-03": [0.0, 0.0], "K-04": [0.0, 0.0]})]
    tekst = d.raport(w)
    assert "CISZA W TYM POMIARZE" in tekst
    assert "NIE jest jeszcze zarzut" in tekst
    assert "adapterami" in tekst


def test_raport_mowi_ze_kandydat_to_nie_wyrok():
    """Prawo XVI: odrzucamy za brak nowej informacji, nie za podobieństwo."""
    w = [d.ocen_skupisko("T/trend", {"A": [1.0, -1.0, 0.5], "B": [1.0, -1.0, 0.5]})]
    tekst = d.raport(w)
    assert "KANDYDAT ≠ WYROK" in tekst
    assert "Decyzja należy do Cezara" in tekst
