"""
🏛️ Testy Areny Trzech Bram (W-035) — potrójna bariera, sprawiedliwy scoring Igrzysk.
"""

from imperium.biblioteki.arena_trzech_bram import oznacz_bariera, RaportAreny, WynikBariery


# ─── Pomocnicze ──────────────────────────────────────────────────────────────

def _bary(highs, lows, closes=None):
    """Buduje uproszczone bary dla testów."""
    n = len(highs)
    if closes is None:
        closes = [(h + l) / 2 for h, l in zip(highs, lows)]
    return [{"high": h, "low": l, "close": c}
            for h, l, c in zip(highs, lows, closes)]


def _flat_bary(n=30, price=100.0):
    """Bary płaskie — nic się nie dzieje → bariera czasowa."""
    return _bary([price * 1.005] * n, [price * 0.995] * n)


# ─── Testy podstawowe ─────────────────────────────────────────────────────────

def test_tp_long_trafiony():
    """LONG: cena rośnie powyżej TP (102) i nigdy nie spada do SL (99) → bariera TP."""
    # low=100.5 > sl=99, high na barze 3 = 102.5 > tp=102
    bary = _bary(highs=[100.8, 101.5, 102.5], lows=[100.2, 100.5, 100.8])
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    assert wynik.bariera == "TP", f"Oczekiwano TP, dostałem {wynik.bariera}"
    assert wynik.contribution == 1.0
    assert wynik.timeliness > 0


def test_sl_long_trafiony():
    """LONG: cena spada poniżej SL (99) i nigdy nie rośnie do TP (102) → bariera SL."""
    # high=100.3 < tp=102, low na barze 2 = 98.5 < sl=99
    bary = _bary(highs=[100.3, 100.2, 100.1], lows=[99.5, 98.5, 98.0])
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    assert wynik.bariera == "SL", f"Oczekiwano SL, dostałem {wynik.bariera}"
    assert wynik.contribution == -1.0


def test_tp_short_trafiony():
    """SHORT: cena spada poniżej TP (98) i nigdy nie rośnie do SL (101) → bariera TP."""
    # high=100.5 < sl=101, low na barze 2 = 97.5 < tp_short=98
    bary = _bary(highs=[100.5, 100.3, 100.2], lows=[99.5, 97.5, 97.0])
    wynik = oznacz_bariera("SHORT", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    assert wynik.bariera == "TP", f"Oczekiwano TP, dostałem {wynik.bariera}"
    assert wynik.contribution == 1.0


def test_sl_short_trafiony():
    """SHORT: cena rośnie powyżej SL (101) i nigdy nie spada do TP (98) → bariera SL."""
    # low=99.5 > tp_short=98, high na barze 3 = 101.5 > sl_short=101
    bary = _bary(highs=[100.5, 100.8, 101.5], lows=[99.5, 99.8, 100.0])
    wynik = oznacz_bariera("SHORT", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    assert wynik.bariera == "SL", f"Oczekiwano SL, dostałem {wynik.bariera}"
    assert wynik.contribution == -1.0


def test_bariera_czasowa():
    """Żadna bariera nie pada → bariera CZAS, contribution 0."""
    bary = _flat_bary(25, 100.0)
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.05, sl_pct=0.05, max_bary=20)
    assert wynik.bariera == "CZAS"
    assert wynik.contribution == 0.0
    assert wynik.timeliness == 0.0


def test_timeliness_wczesnie_wyzsza():
    """TP szybszy daje wyższą timeliness niż TP późniejszy."""
    # TP na barze 1: high=103 > tp=102, low=100.5 > sl=99
    bary_szybkie = _bary([103.0] * 5, [100.5] * 5)
    # TP na barze 9: pierwsze 8 barów neutralne, potem high=103
    bary_wolne = _bary([100.5] * 8 + [103.0], [100.2] * 8 + [100.5])

    w_szybki = oznacz_bariera("LONG", 100.0, bary_szybkie, tp_pct=0.02, sl_pct=0.01, max_bary=20)
    w_wolny  = oznacz_bariera("LONG", 100.0, bary_wolne,  tp_pct=0.02, sl_pct=0.01, max_bary=20)

    assert w_szybki.bariera == "TP", f"Szybkie: {w_szybki.bariera}"
    assert w_wolny.bariera == "TP", f"Wolne: {w_wolny.bariera}"
    assert w_szybki.timeliness > w_wolny.timeliness, (
        f"Szybki={w_szybki.timeliness} powinien być > wolny={w_wolny.timeliness}")


def test_oba_tp_i_sl_w_tym_samym_barze_sl_wygrywa():
    """Jeśli TP i SL trafione w tym samym barze → SL wygrywa (ostrożność)."""
    bary = _bary(highs=[103.0], lows=[98.5])  # TP=102, SL=99 — oba w jednym barze
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=5)
    assert wynik.bariera == "SL", "Oba bariery → SL wygrywa (ostrożność)"
    assert wynik.contribution == -1.0


def test_brak_barow_zwraca_czas():
    """Pusta lista barów → bariera CZAS, graceful fallback."""
    wynik = oznacz_bariera("LONG", 100.0, [], max_bary=10)
    assert wynik.bariera == "CZAS"
    assert wynik.contribution == 0.0


def test_zerowa_cena_wejscia_fallback():
    """Cena wejścia <= 0 → graceful fallback."""
    wynik = oznacz_bariera("LONG", 0.0, _flat_bary(5))
    assert wynik.bariera == "CZAS"


def test_bary_do_wyniku_poprawne():
    """bary_do_wyniku = numer baru (1-indeksowany) kiedy bariera padła."""
    # Bar 1 i 2: neutralne (high < tp=102, low > sl=99)
    # Bar 3: high=102.5 > tp=102, low=100.5 > sl → TP
    bary = _bary(
        highs=[100.5, 101.0, 102.5],
        lows=[100.2, 100.3, 100.5],
    )
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    assert wynik.bariera == "TP", f"Oczekiwano TP, dostałem {wynik.bariera}"
    assert wynik.bary_do_wyniku == 3


# ─── Testy RaportAreny ───────────────────────────────────────────────────────

def test_raport_rejestruje_tp():
    """RaportAreny poprawnie zlicza TP."""
    raport = RaportAreny()
    # high=105 > tp=102, low=100.5 > sl=99
    bary = _bary([105.0] * 3, [100.5] * 3)
    wynik = oznacz_bariera("LONG", 100.0, bary, tp_pct=0.02, sl_pct=0.01, max_bary=10)
    raport.zarejestruj(wynik)
    assert raport.sygnaly_tp == 1
    assert raport.sygnaly_sl == 0
    assert raport.win_rate_tp == 1.0


def test_raport_lacznie_i_win_rate():
    """RaportAreny: win_rate_tp = TP / łącznie."""
    raport = RaportAreny()
    # 2× TP: high=105 > tp=102, low=100.5 > sl=99
    bary_tp = _bary([105.0] * 3, [100.5] * 3)
    # 1× SL: high=100.5 < tp=102, low=98.5 < sl=99
    bary_sl = _bary([100.5] * 3, [98.5] * 3)
    for _ in range(2):
        raport.zarejestruj(oznacz_bariera("LONG", 100.0, bary_tp, 0.02, 0.01, 10))
    raport.zarejestruj(oznacz_bariera("LONG", 100.0, bary_sl, 0.02, 0.01, 10))

    assert raport.sygnaly_tp == 2
    assert raport.sygnaly_sl == 1
    assert raport.lacznie == 3
    assert abs(raport.win_rate_tp - 2/3) < 0.01


def test_raport_kontryb_neuronow():
    """RaportAreny.zarejestruj z sygnaly_json → słownik kontrybucji neuronów."""
    raport = RaportAreny()
    bary = _bary([105.0] * 3, [100.5] * 3)
    wynik = oznacz_bariera("LONG", 100.0, bary, 0.02, 0.01, 10)
    sygnaly = [{"k": "X-01", "d": "LONG"}, {"k": "X-02", "d": "LONG"}]
    raport.zarejestruj(wynik, sygnaly)

    assert "X-01" in raport.kontryb_neuronow
    assert raport.kontryb_neuronow["X-01"]["contribution"] == 1.0
    assert raport.kontryb_neuronow["X-02"]["n"] == 1


def test_raport_drukuj_nie_rzuca():
    """RaportAreny.drukuj() nie rzuca wyjątku."""
    raport = RaportAreny()
    bary = _bary([105.0] * 3, [100.5] * 3)
    raport.zarejestruj(oznacz_bariera("LONG", 100.0, bary, 0.02, 0.01, 10))
    raport.drukuj()  # nie rzuca


def test_wynik_bariery_opis():
    """WynikBariery.opis jest czytelny dla każdego wariantu."""
    bary_tp = _bary([105.0] * 2, [100.5] * 2)
    bary_sl = _bary([100.5] * 2, [98.5] * 2)
    bary_czas = _flat_bary(25, 100.0)

    w_tp = oznacz_bariera("LONG", 100.0, bary_tp, 0.02, 0.01, 10)
    w_sl = oznacz_bariera("LONG", 100.0, bary_sl, 0.02, 0.01, 10)
    w_cz = oznacz_bariera("LONG", 100.0, bary_czas, 0.05, 0.05, 20)

    assert "TP" in w_tp.opis
    assert "SL" in w_sl.opis
    assert "CZAS" in w_cz.opis
