"""Testy Strażnika Przewagi (W-287) — maszyna stanów AKTYWNY/HALT/SONDA."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imperium.pretorianie.straznik_przewagi import StraznikPrzewagi


def test_aktywny_dopoki_edge_dodatni():
    sp = StraznikPrzewagi(okno=3, bary_halt=5)
    for pnl in (10, -2, 8, 5, -1):
        sp.zarejestruj_zamkniecie(pnl)
    assert sp.stan == sp.AKTYWNY and sp.wolno_wejsc()


def test_halt_gdy_expectancy_ujemna():
    sp = StraznikPrzewagi(okno=3, bary_halt=5)
    for pnl in (-10, -5, -8):
        sp.zarejestruj_zamkniecie(pnl)
    assert sp.stan == sp.HALT and not sp.wolno_wejsc()


def test_granica_expectancy_zero_nie_halt():
    """Dokładnie 0 → NIE halt (próg ostro < 0; Reguła Test-Granic)."""
    sp = StraznikPrzewagi(okno=3, bary_halt=5)
    for pnl in (-5, 0, 5):
        sp.zarejestruj_zamkniecie(pnl)
    assert sp.stan == sp.AKTYWNY


def test_halt_odlicza_do_sondy():
    sp = StraznikPrzewagi(okno=3, bary_halt=4)
    for pnl in (-1, -1, -1):
        sp.zarejestruj_zamkniecie(pnl)
    for _ in range(3):
        sp.tyknij_bar()
        assert sp.stan == sp.HALT and not sp.wolno_wejsc()
    sp.tyknij_bar()
    assert sp.stan == sp.SONDA and sp.wolno_wejsc()


def test_sonda_jedna_pozycja_naraz():
    sp = StraznikPrzewagi(okno=3, bary_halt=1)
    for pnl in (-1, -1, -1):
        sp.zarejestruj_zamkniecie(pnl)
    sp.tyknij_bar()
    assert sp.wolno_wejsc()
    sp.zarejestruj_wejscie()
    assert not sp.wolno_wejsc(), "druga pozycja w SONDZIE zabroniona"


def test_sonda_wygrana_wraca_do_aktywnego_z_resetem():
    sp = StraznikPrzewagi(okno=3, bary_halt=1)
    for pnl in (-9, -9, -9):
        sp.zarejestruj_zamkniecie(pnl)
    sp.tyknij_bar(); sp.zarejestruj_wejscie()
    sp.zarejestruj_zamkniecie(+5)
    assert sp.stan == sp.AKTYWNY
    assert sp.raport()["n_w_oknie"] == 1, "wygrana sonda resetuje pomiar (świeży start)"


def test_sonda_przegrana_ponowny_halt():
    sp = StraznikPrzewagi(okno=3, bary_halt=2)
    for pnl in (-9, -9, -9):
        sp.zarejestruj_zamkniecie(pnl)
    sp.tyknij_bar(); sp.tyknij_bar()
    sp.zarejestruj_wejscie()
    sp.zarejestruj_zamkniecie(-3)
    assert sp.stan == sp.HALT


def test_sonda_pnl_zero_to_przegrana():
    """Granica: sonda z PnL == 0 = przegrana (edge ma być DODATNI)."""
    sp = StraznikPrzewagi(okno=3, bary_halt=1)
    for pnl in (-9, -9, -9):
        sp.zarejestruj_zamkniecie(pnl)
    sp.tyknij_bar(); sp.zarejestruj_wejscie()
    sp.zarejestruj_zamkniecie(0.0)
    assert sp.stan == sp.HALT


def test_parametry_graniczne():
    for zle in (2, 0, -1):
        try:
            StraznikPrzewagi(okno=zle); raise AssertionError("okno<3 ma rzucić")
        except ValueError:
            pass
    try:
        StraznikPrzewagi(bary_halt=0); raise AssertionError("bary_halt<1 ma rzucić")
    except ValueError:
        pass


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    bl = 0
    for n, f in fn:
        try:
            f(); print(f"  ✅ {n}")
        except Exception as e:
            bl += 1; print(f"  ❌ {n}: {e}")
    sys.exit(1 if bl else 0)
