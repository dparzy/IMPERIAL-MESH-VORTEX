"""
Testy SynapsyRezimowe W-299 — Regime-Aware Decorrelated Coalition Graph.

Reguła Test-Granic (Prawo XXI):
  - zero sygnałów / jeden sygnał (brak par)
  - dokładnie MIN_WYMAGAN_TRAD aktualizacji
  - korelacja 0 vs korelacja 1 (kara dekorelacji)
  - max_wzmocnienie / max_redukcja cap
  - decay / zapomnienie
"""

import tempfile
import os

from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe, _klucz_pary


# ── helpers ───────────────────────────────────────────────────────────────────

class _S:
    """Minimalny mock SygnalNeuronu."""
    def __init__(self, nid, kierunek="LONG"):
        self.neuron_id = nid
        self.kierunek = kierunek


def _synapsy(**kw):
    return SynapsyRezimowe(min_trad=1, **kw)   # min_trad=1 dla szybkich testów


# ── klucz pary ────────────────────────────────────────────────────────────────

def test_klucz_pary_sorted():
    assert _klucz_pary("XII-04", "X-01", "RANGING") == _klucz_pary("X-01", "XII-04", "RANGING")


def test_klucz_pary_rozny_rezim():
    assert _klucz_pary("X-01", "X-02", "RANGING") != _klucz_pary("X-01", "X-02", "TREND_STRONG")


# ── uczenie (aktualizuj) ──────────────────────────────────────────────────────

def test_brak_sygnałów_nie_zmienia_silo():
    s = _synapsy()
    s.aktualizuj([], "LONG", 2.0, "RANGING")
    assert s.ile_par() == 0


def test_jeden_sygnal_nie_tworzy_pary():
    s = _synapsy()
    s.aktualizuj([_S("X-01")], "LONG", 2.0, "RANGING")
    assert s.ile_par() == 0


def test_zysk_wzmacnia_synapsy():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02")]
    s.aktualizuj(sig, "LONG", 3.0, "TREND_STRONG")
    k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
    assert s._silo[k] > 0.0


def test_strata_oslabia_synapsy():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02")]
    s.aktualizuj(sig, "LONG", -2.0, "TREND_STRONG")
    k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
    assert s._silo[k] < 0.0


def test_korelacja_spowalnia_uczenie():
    """Para ze skorelowanymi neuronami uczy się wolniej niż niezależna."""
    s_niezalezna = _synapsy()
    s_skorelowana = _synapsy()
    sig = [_S("X-01"), _S("X-02")]

    s_niezalezna.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG", korelacje={})
    s_skorelowana.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG",
                              korelacje={("X-01", "X-02"): 0.9})

    k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
    assert s_niezalezna._silo[k] > s_skorelowana._silo[k]


def test_sila_clamped_minus1_plus1():
    s = _synapsy(eta=0.5)
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(30):  # dużo zysków → powinno nasycić do +1
        s.aktualizuj(sig, "LONG", 5.0, "TREND_STRONG")
    k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
    assert s._silo[k] == 1.0


def test_neutral_kierunek_pomijany():
    s = _synapsy()
    s.aktualizuj([_S("X-01"), _S("X-02")], "NEUTRAL", 1.0, "RANGING")
    assert s.ile_par() == 0


# ── wzmacnianie pewności ──────────────────────────────────────────────────────

def test_brak_par_pewnosc_bez_zmian():
    s = _synapsy()
    assert s.wzmocnij_pewnosc(0.7, [_S("X-01")], "RANGING") == 0.7


def test_min_trad_blokuje_zbyt_mala_historia():
    s = SynapsyRezimowe(min_trad=5)  # wymaga 5 aktualizacji
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(4):   # tylko 4 — za mało
        s.aktualizuj(sig, "LONG", 2.0, "RANGING")
    wynik = s.wzmocnij_pewnosc(0.7, sig, "RANGING")
    assert wynik == 0.7   # bez zmiany — za mało historii


def test_pozytywne_synapsy_wzmacniaja():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(5):
        s.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG")
    bazowa = 0.6
    wynik = s.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG")
    assert wynik > bazowa


def test_negatywne_synapsy_redukuja():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(5):
        s.aktualizuj(sig, "LONG", -2.0, "TREND_STRONG")
    bazowa = 0.7
    wynik = s.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG")
    assert wynik < bazowa


def test_wzmocnienie_nie_przekracza_max():
    s = _synapsy(eta=0.5, max_wzmocnienie=0.15)
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(30):
        s.aktualizuj(sig, "LONG", 5.0, "TREND_STRONG")
    bazowa = 0.70
    wynik = s.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG")
    assert wynik <= bazowa + 0.15 + 1e-6


def test_redukcja_nie_przekracza_max():
    s = _synapsy(eta=0.5, max_redukcja=0.12)
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(30):
        s.aktualizuj(sig, "LONG", -5.0, "TREND_STRONG")
    bazowa = 0.70
    wynik = s.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG")
    assert wynik >= bazowa - 0.12 - 1e-6


def test_pewnosc_clamped_0_1():
    """Wynik wzmocnij_pewnosc zawsze w [0, 1]."""
    s = _synapsy(eta=0.5, max_wzmocnienie=0.5)
    sig = [_S("X-01"), _S("X-02")]
    for _ in range(50):
        s.aktualizuj(sig, "LONG", 5.0, "TREND_STRONG")
    wynik = s.wzmocnij_pewnosc(0.98, sig, "TREND_STRONG")
    assert 0.0 <= wynik <= 1.0


def test_dekorelacja_amplifikuje_wzmocnienie():
    """Dekorelowana para (corr=0) wzmacnia bardziej niż skorelowana (corr=0.9)."""
    s_niz = _synapsy()
    s_kor = _synapsy()
    sig = [_S("X-01"), _S("X-02")]

    for _ in range(5):
        s_niz.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG")
        s_kor.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG", {("X-01", "X-02"): 0.9})

    bazowa = 0.6
    wz_niz = s_niz.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG", {})
    wz_kor = s_kor.wzmocnij_pewnosc(bazowa, sig, "TREND_STRONG", {("X-01", "X-02"): 0.9})
    assert wz_niz >= wz_kor


# ── decay / zapomnienie ───────────────────────────────────────────────────────

def test_zapomnij_redukuje_sile():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02")]
    s.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG")
    k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
    przed = s._silo[k]
    s.zapomnij()
    po = s._silo.get(k, 0.0)
    assert po < przed


def test_zapomnij_usuwa_male_synapsy():
    s = SynapsyRezimowe(eta=0.001, alpha_decay=1.0, min_trad=1)  # szybki decay
    s.aktualizuj([_S("X-01"), _S("X-02")], "LONG", 1.0, "RANGING")
    s.zapomnij()
    assert s.ile_par() == 0


# ── statystyki ────────────────────────────────────────────────────────────────

def test_statystyki_puste_silo():
    s = _synapsy()
    st = s.statystyki()
    assert st.n_par_razem == 0
    assert st.n_par_aktywnych == 0


def test_statystyki_po_uczeniu():
    s = _synapsy()
    sig = [_S("X-01"), _S("X-02"), _S("X-03")]
    for _ in range(3):
        s.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG")
    st = s.statystyki()
    assert st.n_par_razem == 3      # 3 pary: (01,02),(01,03),(02,03)
    assert st.n_rezimow >= 1
    assert len(st.top3) <= 3


# ── persystencja ──────────────────────────────────────────────────────────────

def test_zapisz_wczytaj():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        s = _synapsy()
        sig = [_S("X-01"), _S("X-02")]
        s.aktualizuj(sig, "LONG", 2.0, "TREND_STRONG")
        s.zapisz(path)

        s2 = SynapsyRezimowe(min_trad=1)
        s2._wczytaj(path)
        k = _klucz_pary("X-01", "X-02", "TREND_STRONG")
        assert abs(s2._silo[k] - s._silo[k]) < 1e-6
    finally:
        os.unlink(path)


def test_wczytaj_brak_pliku_nie_rzuca():
    s = _synapsy()
    s._wczytaj("/tmp/niema_takiego_pliku_12345.json")   # nie rzuca
    assert s.ile_par() == 0
