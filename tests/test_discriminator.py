"""Testy DISCRIMINATORA — organu orzekającego, czy skupisko to naprawdę redundancja.

Rdzeń jest czysty (serie to DANE, nie źródła), więc każdy werdykt da się sprawdzić bez
świec, bez Bramy i bez dysku. Granice utrwalone tu pochodzą z PIERWSZEGO biegu na żywych
danych (BTCUSDT 4h, 2026-07-31), nie z wyobraźni.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.legiony import discriminator as d  # noqa: E402


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
