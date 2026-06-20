"""
Testy W-355..W-359 — AFML (López de Prado) implementacje.
Prawo XXI: granice, znaki, progi, None — każdy moduł przetestowany osobno.
"""

# ─── W-355 Feature Importance ─────────────────────────────────────────────────

def test_sfi_wszystkie_poprawne():
    from imperium.legiony.feature_importance import _sfi_neuronu
    sygnaly = ["LONG"] * 10 + ["SHORT"] * 10
    wyniki = [1] * 10 + [-1] * 10
    sl, ss, nl, ns, nn = _sfi_neuronu(sygnaly, wyniki)
    assert sl == 1.0
    assert ss == 1.0
    assert nl == 10 and ns == 10


def test_sfi_wszystkie_zle():
    from imperium.legiony.feature_importance import _sfi_neuronu
    sygnaly = ["LONG"] * 5 + ["SHORT"] * 5
    wyniki = [-1] * 5 + [1] * 5
    sl, ss, nl, ns, _ = _sfi_neuronu(sygnaly, wyniki)
    assert sl == 0.0 and ss == 0.0


def test_sfi_brak_sygnalow_fallback():
    from imperium.legiony.feature_importance import _sfi_neuronu
    sl, ss, nl, ns, nn = _sfi_neuronu(["NEUTRAL"] * 10, [1] * 10)
    assert sl == 0.5 and ss == 0.5
    assert nl == 0 and ns == 0 and nn == 10


def test_raport_waznosci_za_malo_danych():
    from imperium.legiony.feature_importance import raport_waznosci
    r = raport_waznosci([], [], )
    assert r.n_obserwacji == 0
    assert r.rankowanie == []


def test_raport_waznosci_pelny():
    from imperium.legiony.feature_importance import raport_waznosci
    import random
    rng = random.Random(42)
    n = 60
    # Neuron A: dobry (LONG gdy cena rośnie)
    # Neuron B: losowy (szum)
    historia = []
    wyniki = []
    for i in range(n):
        wzrost = rng.random() > 0.4
        wyniki.append(1 if wzrost else -1)
        historia.append({
            "A": "LONG" if wzrost else "SHORT",   # dobry
            "B": rng.choice(["LONG", "SHORT", "NEUTRAL"]),  # szum
        })
    r = raport_waznosci(historia, wyniki, n_permutacji=5)
    assert r.n_obserwacji == n
    assert len(r.rankowanie) == 2
    # A powinien mieć wyższe MDA niż B (nie zawsze, ale statystycznie)
    klucze = [w.klucz for w in r.rankowanie]
    assert "A" in klucze and "B" in klucze


def test_raport_waznosci_martwy_glos():
    from imperium.legiony.feature_importance import raport_waznosci
    import random
    rng = random.Random(99)
    n = 50
    historia = [{"MARTWY": "NEUTRAL"} for _ in range(n)]
    wyniki = [rng.choice([1, -1]) for _ in range(n)]
    r = raport_waznosci(historia, wyniki, n_permutacji=3)
    # MARTWY daje tylko NEUTRAL → 0 sygnałów → pominięty lub w martwych
    assert r.n_obserwacji == n


# ─── W-356 Bary Zdarzeniowe ───────────────────────────────────────────────────

def _ticki_testowe(n=100, cena_start=50000.0, wolumen_per=0.1):
    from imperium.akwedukty.bary_zdarzeniowe import Tick
    return [
        Tick(timestamp=i * 1000, cena=cena_start + i * 10, wolumen=wolumen_per)
        for i in range(n)
    ]


def test_tick_bars_podstawowy():
    from imperium.akwedukty.bary_zdarzeniowe import tick_bars_z_tickow
    ticki = _ticki_testowe(50)
    bary = tick_bars_z_tickow(ticki, n=10)
    assert len(bary) == 5   # 50 ticków / 10 = 5 barów
    for b in bary:
        assert b.n_ticks == 10
        assert b.open > 0
        assert b.high >= b.low


def test_volume_bars_podstawowy():
    from imperium.akwedukty.bary_zdarzeniowe import volume_bars_z_tickow, Tick
    ticki = [Tick(i * 1000, 50000.0, 1.0) for i in range(20)]
    bary = volume_bars_z_tickow(ticki, prog=5.0)
    assert len(bary) == 4   # 20 BTC / 5 = 4 bary
    for b in bary:
        assert b.volume >= 5.0


def test_dollar_bars_podstawowy():
    from imperium.akwedukty.bary_zdarzeniowe import dollar_bars_z_tickow, Tick
    ticki = [Tick(i * 1000, 10_000.0, 1.0) for i in range(30)]
    bary = dollar_bars_z_tickow(ticki, prog=50_000.0)
    assert len(bary) == 6   # 30 × 10K = 300K / 50K = 6 barów
    for b in bary:
        assert b.dollar_volume >= 50_000.0


def test_dollar_bars_z_ohlcv():
    from imperium.akwedukty.bary_zdarzeniowe import dollar_bars
    ohlcv = [
        {"timestamp": i * 3600000, "open": 50000.0, "high": 50500.0,
         "low": 49500.0, "close": 50000.0, "volume": 100.0}
        for i in range(20)
    ]
    bary = dollar_bars(ohlcv, prog_dolarow=5_000_000.0)
    assert len(bary) >= 1
    for b in bary:
        assert b.close > 0
        assert b.high >= b.low


def test_bar_jako_dict():
    from imperium.akwedukty.bary_zdarzeniowe import Tick, dollar_bars_z_tickow
    ticki = [Tick(i * 1000, 1000.0, 1.0) for i in range(10)]
    bary = dollar_bars_z_tickow(ticki, prog=5000.0)
    assert len(bary) >= 1
    d = bary[0].jako_dict()
    assert "open" in d and "close" in d and "volume" in d
    assert d["typ_bara"] == "dollar"


def test_statystyki_barow():
    from imperium.akwedukty.bary_zdarzeniowe import Tick, dollar_bars_z_tickow, statystyki_barow
    ticki = [Tick(i * 1000, 50000.0, 1.0) for i in range(100)]
    bary = dollar_bars_z_tickow(ticki, prog=100_000.0)
    st = statystyki_barow(bary)
    assert "n_barow" in st
    assert st["cv_dollar_volume"] >= 0


def test_imbalance_bars_nie_crashuje():
    from imperium.akwedukty.bary_zdarzeniowe import Tick, imbalance_bars_z_tickow
    import random
    rng = random.Random(7)
    ticki = [Tick(i * 1000, 50000.0 + rng.gauss(0, 100), 1.0,
                  strona=rng.choice([1, -1])) for i in range(200)]
    bary = imbalance_bars_z_tickow(ticki, oczekiwana_dl_inicjalna=20)
    # Nie powinien crashować; liczba barów zmiennicza (adaptacyjna)
    assert isinstance(bary, list)


# ─── W-357 Triple-Barrier ─────────────────────────────────────────────────────

def _close_testowe(n=100, drift=0.001):
    c = [50000.0]
    for i in range(n - 1):
        c.append(c[-1] * (1 + drift + (0.01 if i % 10 < 5 else -0.008)))
    return c


def test_filtr_cusum_emituje_zdarzenia():
    from imperium.legiony.triple_barrier import filtr_cusum
    close = _close_testowe(100)
    zdarzenia = filtr_cusum(close, h=0.02)
    assert isinstance(zdarzenia, list)
    # Przy trendzie wzrostowym z h=2% powinno być kilka zdarzeń
    assert len(zdarzenia) >= 1
    assert all(0 <= i < len(close) for i in zdarzenia)


def test_filtr_cusum_pusta_seria():
    from imperium.legiony.triple_barrier import filtr_cusum
    assert filtr_cusum([], h=0.01) == []


def test_triple_barrier_etykiety():
    from imperium.legiony.triple_barrier import triple_barrier, filtr_cusum
    close = _close_testowe(200, drift=0.002)
    zdarzenia = filtr_cusum(close, h=0.01)[:10]
    bariery = triple_barrier(close, zdarzenia, k_tp=1.5, k_sl=1.0, max_hold=20)
    assert len(bariery) == len(zdarzenia)
    for b in bariery:
        assert b.etykieta in (-1, 0, 1)
        assert b.bariera_gorna > b.cena_wejscia
        assert b.bariera_dolna < b.cena_wejscia


def test_triple_barrier_puste_zdarzenia():
    from imperium.legiony.triple_barrier import triple_barrier
    close = _close_testowe(50)
    bariery = triple_barrier(close, [], k_tp=2.0, k_sl=1.0)
    assert bariery == []


def test_triple_barrier_granica_max_hold():
    from imperium.legiony.triple_barrier import triple_barrier
    # Płaski rynek → wszystkie time-out
    close = [50000.0] * 100
    zdarzenia = [0, 10, 20]
    bariery = triple_barrier(close, zdarzenia, k_tp=0.1, k_sl=0.1, max_hold=5)
    for b in bariery:
        assert b.etykieta == 0  # brak ruchu → time-out


def test_etykiety_z_barier_dict():
    from imperium.legiony.triple_barrier import triple_barrier, etykiety_z_barier
    close = _close_testowe(100)
    bariery = triple_barrier(close, [0, 20, 40], k_tp=2.0, k_sl=1.0, max_hold=15)
    et = etykiety_z_barier(bariery)
    assert isinstance(et, dict)
    for k, v in et.items():
        assert v in (-1, 0, 1)


def test_statystyki_barier():
    from imperium.legiony.triple_barrier import triple_barrier, statystyki_barier
    close = _close_testowe(200)
    bariery = triple_barrier(close, list(range(0, 150, 10)), k_tp=2.0, k_sl=1.0, max_hold=15)
    st = statystyki_barier(bariery)
    assert "tp_pct" in st and "sl_pct" in st
    assert abs(st["tp_pct"] + st["sl_pct"] + st["timeout_pct"] - 100.0) < 0.1


def test_sample_uniqueness():
    from imperium.legiony.triple_barrier import triple_barrier, sample_uniqueness
    close = _close_testowe(100)
    bariery = triple_barrier(close, [0, 5, 10, 15], k_tp=2.0, k_sl=1.0, max_hold=20)
    wagi = sample_uniqueness(bariery, n_close=len(close))
    assert len(wagi) == len(bariery)
    for w in wagi:
        assert 0.0 < w <= 1.0


# ─── W-358 Purged K-Fold ──────────────────────────────────────────────────────

def test_purged_kfold_podstawowy():
    from imperium.koloseum.walidacja import purged_kfold_podzialy
    podzialy = purged_kfold_podzialy(100, k=5)
    assert len(podzialy) == 5
    for train, test in podzialy:
        assert len(train) > 0 and len(test) > 0
        # Train i test rozłączne
        assert set(train).isdisjoint(set(test))


def test_purged_kfold_z_t1():
    from imperium.koloseum.walidacja import purged_kfold_podzialy
    # t1[i] = i + 10 (etykieta trwa 10 barów)
    n = 100
    t1 = [min(i + 10, n - 1) for i in range(n)]
    podzialy = purged_kfold_podzialy(n, k=5, t1=t1, embargo_pct=0.01)
    assert len(podzialy) >= 1
    for train, test in podzialy:
        assert set(train).isdisjoint(set(test))


def test_purged_kfold_embargo_dziala():
    from imperium.koloseum.walidacja import purged_kfold_podzialy
    # Bez purgingu ale z embargo — obserwacje tuż po teście usunięte
    podzialy = purged_kfold_podzialy(50, k=5, t1=None, embargo_pct=0.1)
    for train, test in podzialy:
        test_end = max(test)
        for ti in train:
            # Żaden train nie powinien być tuż po teście (embargo = 10% × 50 = 5)
            if ti > test_end:
                assert ti > test_end + 5 - 1  # >= embargo_end


def test_cross_val_score_purged_dziala():
    from imperium.koloseum.walidacja import cross_val_score_purged

    # Model dummy: zawsze przewiduje 1, accuracy = %jedynek w y_test
    def ucz(X, y, w):
        pass

    def ocen(X, y):
        return sum(1 for yi in y if yi == 1) / len(y) if y else 0.5

    X = list(range(100))
    y = [1 if i % 2 == 0 else 0 for i in range(100)]
    wynik = cross_val_score_purged(ucz, ocen, X, y, k=5)
    assert wynik["ok"] is True
    assert 0.0 <= wynik["mean"] <= 1.0
    assert wynik["n_foldow"] == 5


# ─── W-359 Bet Sizing LdP ─────────────────────────────────────────────────────

def test_bet_size_ldp_sredni():
    from imperium.legiony.meta_labeling import bet_size_ldp
    # p=0.5 → m powinien być 0.0 (przy K=2: z=(0.5-0.5)/sqrt(0.25)=0 → Φ(0)=0.5 → 2*0.5-1=0)
    m = bet_size_ldp(0.5, k=2, dyskretyzacja=0.0)
    assert m == 0.0


def test_bet_size_ldp_pewny():
    from imperium.legiony.meta_labeling import bet_size_ldp
    m = bet_size_ldp(1.0, k=2, dyskretyzacja=0.0)
    assert m == 1.0


def test_bet_size_ldp_niepewny():
    from imperium.legiony.meta_labeling import bet_size_ldp
    m = bet_size_ldp(0.0, k=2, dyskretyzacja=0.0)
    assert m == 0.0


def test_bet_size_ldp_monotonicznosc():
    from imperium.legiony.meta_labeling import bet_size_ldp
    # Wyższe p → wyższy bet_size (monotoniczność)
    prev = 0.0
    for p in [0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]:
        m = bet_size_ldp(p, k=2, dyskretyzacja=0.0)
        assert m >= prev, f"p={p}: m={m} < prev={prev}"
        prev = m


def test_bet_size_ldp_dyskretyzacja():
    from imperium.legiony.meta_labeling import bet_size_ldp
    m = bet_size_ldp(0.72, k=2, dyskretyzacja=0.1)
    # Musi być wielokrotnością 0.1
    assert abs(m * 10 - round(m * 10)) < 1e-9, f"m={m} nie jest wielokrotnością 0.1"


def test_bet_size_ldp_zakres():
    from imperium.legiony.meta_labeling import bet_size_ldp
    for p in [0.0, 0.3, 0.5, 0.7, 0.85, 1.0]:
        m = bet_size_ldp(p)
        assert 0.0 <= m <= 1.0, f"p={p}: m={m} poza [0,1]"


def test_bufor_aktywnych_srednia():
    from imperium.legiony.meta_labeling import BuforAktywnych
    b = BuforAktywnych()
    b.dodaj("BTCUSDT", 0.8)
    b.dodaj("ETHUSDT", 0.4)
    assert abs(b.srednia() - 0.6) < 1e-9


def test_bufor_aktywnych_zamknij():
    from imperium.legiony.meta_labeling import BuforAktywnych
    b = BuforAktywnych()
    b.dodaj("BTCUSDT", 0.8)
    b.zamknij("BTCUSDT")
    assert b.srednia() == 0.0


def test_bufor_aktywnych_pusty():
    from imperium.legiony.meta_labeling import BuforAktywnych
    b = BuforAktywnych()
    assert b.srednia() == 0.0


def test_bufor_aktywnych_aktualizacja():
    from imperium.legiony.meta_labeling import BuforAktywnych
    b = BuforAktywnych()
    b.dodaj("X", 0.5)
    b.dodaj("X", 0.9)   # aktualizacja
    assert b.bet_dla("X") == 0.9
    assert b.srednia() == 0.9
