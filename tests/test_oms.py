"""Testy OMS (W-344) — maszyna stanów cyklu życia zlecenia, retry, reconciliacja.

Nacisk na GRANICE (Prawo XXI Test-Granic): nielegalne przejścia, 0/over-fill,
dokładne domknięcie, wyczerpanie retry, reconciliacja rozjazdu OMS↔giełda.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.drogi.oms import (
    ZarzadcaZlecen, StanZlecenia, Strona, TypZlecenia,
    NielegalnePrzejscie, STANY_KONCOWE,
)


# ── Tworzenie ──────────────────────────────────────────────────────────────

def test_utworz_zlecenie_nowe():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 0.5)
    assert z.stan == StanZlecenia.NOWE
    assert z.ilosc == 0.5
    assert z.ilosc_pozostala == 0.5
    assert not z.zakonczone


def test_utworz_zero_ilosc_blad():
    oms = ZarzadcaZlecen()
    try:
        oms.utworz("BTCUSDT", Strona.KUP, 0.0)
        assert False, "Zero ilości powinno rzucić ValueError"
    except ValueError:
        pass


def test_utworz_ujemna_ilosc_blad():
    oms = ZarzadcaZlecen()
    try:
        oms.utworz("BTCUSDT", Strona.SPRZEDAJ, -1.0)
        assert False
    except ValueError:
        pass


def test_limit_bez_ceny_blad():
    oms = ZarzadcaZlecen()
    try:
        oms.utworz("BTCUSDT", Strona.KUP, 1.0, typ=TypZlecenia.LIMIT)
        assert False, "LIMIT bez ceny powinien rzucić"
    except ValueError:
        pass


def test_duplikat_id_blad():
    oms = ZarzadcaZlecen()
    oms.utworz("BTCUSDT", Strona.KUP, 1.0, zlecenie_id="X1")
    try:
        oms.utworz("ETHUSDT", Strona.KUP, 1.0, zlecenie_id="X1")
        assert False
    except ValueError:
        pass


# ── Składanie paper ────────────────────────────────────────────────────────

def test_zloz_paper_od_razu_zlozone():
    oms = ZarzadcaZlecen()  # submit_fn=None → paper
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is True
    assert z.stan == StanZlecenia.ZLOZONE
    assert z.proby == 1


def test_zloz_dwa_razy_blad():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    try:
        oms.zloz(z)
        assert False, "Drugie zloz() na ZLOZONE powinno rzucić"
    except NielegalnePrzejscie:
        pass


# ── Składanie realne z retry ───────────────────────────────────────────────

def test_zloz_realny_sukces():
    wywolania = []
    def submit(z): wywolania.append(z.zlecenie_id); return {"ok": True}
    oms = ZarzadcaZlecen(submit_fn=submit)
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is True
    assert z.stan == StanZlecenia.ZLOZONE
    assert len(wywolania) == 1


def test_zloz_retry_potem_sukces():
    """Pierwsza próba pada, druga sukces — retry odzyskuje (Prawo XV)."""
    licznik = {"n": 0}
    def submit(z):
        licznik["n"] += 1
        if licznik["n"] < 2:
            raise ConnectionError("sieć padła")
        return {"ok": True}
    oms = ZarzadcaZlecen(submit_fn=submit, max_prob=3, backoff_bazowy_s=0.0)
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is True
    assert z.stan == StanZlecenia.ZLOZONE
    assert z.proby == 2


def test_zloz_wyczerpanie_retry_blad():
    """Wszystkie próby padają → stan BLAD, zwraca False (Prawo I — jawna porażka)."""
    def submit(z): raise ConnectionError("zawsze pada")
    oms = ZarzadcaZlecen(submit_fn=submit, max_prob=3, backoff_bazowy_s=0.0)
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is False
    assert z.stan == StanZlecenia.BLAD
    assert z.proby == 3
    assert "zawsze pada" in z.ostatni_blad


# ── Wypełnienia / partial-fill ─────────────────────────────────────────────

def test_pelne_wypelnienie_jednym():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 50000)
    assert z.stan == StanZlecenia.WYPELNIONE
    assert z.cena_srednia == 50000
    assert z.ilosc_pozostala == 0.0


def test_partial_potem_pelne():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.4, 50000)
    assert z.stan == StanZlecenia.CZESCIOWE
    assert z.ilosc_pozostala == 0.6
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.6, 51000)
    assert z.stan == StanZlecenia.WYPELNIONE
    # Cena średnia ważona: (0.4*50000 + 0.6*51000)/1.0 = 50600
    assert abs(z.cena_srednia - 50600) < 1e-6


def test_trzy_partiale_srednia_wazona():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 3.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 100)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 200)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 300)
    assert z.stan == StanZlecenia.WYPELNIONE
    assert abs(z.cena_srednia - 200) < 1e-6  # (100+200+300)/3


def test_over_fill_blad():
    """GRANICA: wypełnienie ponad zamówioną ilość → ValueError (Prawo XXI)."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    try:
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.5, 50000)
        assert False, "Over-fill powinno rzucić"
    except ValueError:
        pass


def test_wypelnienie_dokladnie_do_zera_to_wypelnione():
    """GRANICA: suma partiali dokładnie == ilość → WYPELNIONE, nie CZESCIOWE."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 0.3)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.1, 100)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.1, 100)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.1, 100)
    assert z.stan == StanZlecenia.WYPELNIONE


def test_wypelnienie_zero_ilosc_blad():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    try:
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.0, 50000)
        assert False
    except ValueError:
        pass


def test_wypelnienie_na_nowym_blad():
    """GRANICA: nie można wypełnić zlecenia jeszcze niezłożonego (NOWE)."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    try:
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.5, 50000)
        assert False, "Wypełnienie na NOWE powinno rzucić"
    except NielegalnePrzejscie:
        pass


# ── Odrzucenie / anulowanie ────────────────────────────────────────────────

def test_odrzucenie():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.odrzuc(z.zlecenie_id, "brak środków")
    assert z.stan == StanZlecenia.ODRZUCONE
    assert z.zakonczone


def test_anulowanie_z_nowego():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.anuluj(z.zlecenie_id)
    assert z.stan == StanZlecenia.ANULOWANE


def test_anulowanie_czesciowego():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.5, 50000)
    oms.anuluj(z.zlecenie_id, "ręczne wycofanie reszty")
    assert z.stan == StanZlecenia.ANULOWANE
    assert z.ilosc_wypelniona == 0.5  # częściowe wypełnienie zachowane


def test_nie_mozna_anulowac_wypelnionego():
    """GRANICA: stan końcowy WYPELNIONE → brak przejść."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 50000)
    try:
        oms.anuluj(z.zlecenie_id)
        assert False, "Anulowanie WYPELNIONE powinno rzucić"
    except NielegalnePrzejscie:
        pass


# ── Reconciliacja ──────────────────────────────────────────────────────────

def test_reconcile_doplyw_wypelnienia():
    """Giełda wie o wypełnieniu, którego OMS nie widział → dociągnij."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    skor = oms.reconcile({z.zlecenie_id: {"ilosc_wypelniona": 1.0, "cena_srednia": 50000}})
    assert z.zlecenie_id in skor
    assert z.stan == StanZlecenia.WYPELNIONE
    assert z.cena_srednia == 50000


def test_reconcile_anulowane_na_gieldzie():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    skor = oms.reconcile({z.zlecenie_id: {"stan": "CANCELED"}})
    assert z.zlecenie_id in skor
    assert z.stan == StanZlecenia.ANULOWANE


def test_reconcile_nie_cofa_koncowego():
    """GRANICA: reconcile nie rusza stanów końcowych (Prawo I — brak regresu)."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 1.0, 50000)
    skor = oms.reconcile({z.zlecenie_id: {"stan": "CANCELED"}})
    assert z.zlecenie_id not in skor
    assert z.stan == StanZlecenia.WYPELNIONE


def test_reconcile_zgodny_brak_korekty():
    """Gdy OMS i giełda zgodne → zero korekt."""
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.5, 50000)
    skor = oms.reconcile({z.zlecenie_id: {"ilosc_wypelniona": 0.5}})
    assert skor == []
    assert z.stan == StanZlecenia.CZESCIOWE


def test_reconcile_nieznane_zlecenie_ignorowane():
    oms = ZarzadcaZlecen()
    skor = oms.reconcile({"NIEZNANE": {"stan": "FILLED"}})
    assert skor == []


# ── Zapytania / raport ─────────────────────────────────────────────────────

def test_aktywne_zwraca_w_locie():
    oms = ZarzadcaZlecen()
    z1 = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    z2 = oms.utworz("ETHUSDT", Strona.KUP, 1.0)
    oms.zloz(z1)
    oms.zloz(z2)
    oms.zarejestruj_wypelnienie(z2.zlecenie_id, 1.0, 3000)  # z2 WYPELNIONE
    aktywne = oms.aktywne()
    assert z1 in aktywne and z2 not in aktywne


def test_raport_rozklad_stanow():
    oms = ZarzadcaZlecen()
    z1 = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    z2 = oms.utworz("ETHUSDT", Strona.KUP, 1.0)
    oms.zloz(z1)
    oms.zloz(z2)
    oms.zarejestruj_wypelnienie(z1.zlecenie_id, 1.0, 50000)
    r = oms.raport()
    assert r["lacznie"] == 2
    assert r["aktywne"] == 1
    assert r["rozklad_stanow"]["WYPELNIONE"] == 1
    assert r["rozklad_stanow"]["ZLOZONE"] == 1


def test_stany_koncowe_komplet():
    """Niezmiennik: stany końcowe to dokładnie te 4 (ochrona przed regresją)."""
    assert STANY_KONCOWE == frozenset({
        StanZlecenia.WYPELNIONE, StanZlecenia.ODRZUCONE,
        StanZlecenia.ANULOWANE, StanZlecenia.BLAD,
    })


def test_wymagaj_nieznane_blad():
    oms = ZarzadcaZlecen()
    try:
        oms.odrzuc("NIE-MA")
        assert False
    except KeyError:
        pass
