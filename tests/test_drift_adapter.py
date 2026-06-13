"""Testy Drift Adapter — antycypacyjna adaptacja reżimu (W-296)."""
from imperium.koloseum.drift_adapter import (
    DriftAdapter,
    PROG_DRYFU,
    _oblicz_momentum,
    _korekty_wag,
)
from collections import Counter


# ── inicjalizacja ─────────────────────────────────────────────────────────────

def test_zly_okno_rzuca():
    try:
        DriftAdapter(okno=2)
        assert False, "Powinien rzucić ValueError"
    except ValueError:
        pass


def test_za_malo_historii_brak_dryfu():
    a = DriftAdapter(okno=10)
    a.dodaj_rezim("NORMAL")
    a.dodaj_rezim("RANGING")
    s = a.skanuj()
    assert s.czy_drift is False
    assert s.entropia == 0.0


# ── entropia i stabilność ─────────────────────────────────────────────────────

def test_stabilny_rezim_niska_entropia():
    a = DriftAdapter(okno=20)
    for _ in range(20):
        a.dodaj_rezim("TRENDING_UP")
    s = a.skanuj()
    assert s.entropia == 0.0
    assert s.entropia_norm == 0.0
    assert s.czy_drift is False


def test_chaotyczny_rezim_wysoka_entropia():
    a = DriftAdapter(okno=20)
    rezimy = ["TRENDING_UP", "RANGING", "VOLATILE", "TRENDING_DOWN", "NORMAL"]
    for i in range(20):
        a.dodaj_rezim(rezimy[i % len(rezimy)])
    s = a.skanuj()
    assert s.entropia_norm > 0.5


def test_entropia_norm_maks_jeden():
    a = DriftAdapter(okno=20)
    rezimy = ["A", "B", "C", "D", "E", "F"]
    for i in range(20):
        a.dodaj_rezim(rezimy[i % len(rezimy)])
    s = a.skanuj()
    assert 0.0 <= s.entropia_norm <= 1.0


# ── prog dryfu ────────────────────────────────────────────────────────────────

def test_dryf_wykryty_pow_progu():
    a = DriftAdapter(okno=20)
    rezimy = ["TRENDING_UP", "RANGING", "VOLATILE", "TRENDING_DOWN"]
    for i in range(20):
        a.dodaj_rezim(rezimy[i % 4])
    s = a.skanuj()
    if s.entropia_norm > PROG_DRYFU:
        assert s.czy_drift is True
    else:
        assert s.czy_drift is False


# ── momentum reżimu ──────────────────────────────────────────────────────────

def test_momentum_trending():
    # 2. połówka zdominowana przez TRENDING
    stara = Counter({"RANGING": 10})
    nowa = Counter({"TRENDING_UP": 8, "TREND_WEAK": 2})
    assert _oblicz_momentum(stara, nowa, 10) == "TRENDING"


def test_momentum_ranging():
    stara = Counter({"TRENDING_UP": 10})
    nowa = Counter({"RANGING": 9, "NORMAL": 1})
    assert _oblicz_momentum(stara, nowa, 10) == "RANGING"


def test_momentum_neutral():
    stara = Counter({"NORMAL": 5, "RANGING": 5})
    nowa = Counter({"NORMAL": 5, "RANGING": 5})
    assert _oblicz_momentum(stara, nowa, 10) == "NEUTRAL"


# ── korekty wag ──────────────────────────────────────────────────────────────

def test_korekty_ranging_trend_w_dol():
    k = _korekty_wag(True, "RANGING", 0.2)
    assert k.get("M", 1.0) < 1.0
    assert k.get("T", 1.0) < 1.0
    assert k.get("S", 1.0) > 1.0


def test_korekty_trending_trend_w_gore():
    k = _korekty_wag(True, "TRENDING", 0.2)
    assert k.get("M", 1.0) > 1.0
    assert k.get("T", 1.0) > 1.0


def test_korekty_brak_dryfu_pusta_mapa():
    k = _korekty_wag(False, "RANGING", 0.8)
    assert k == {}


def test_korekty_max_sila_ograniczona():
    k = _korekty_wag(True, "RANGING", 0.99)  # wspolczynnik > MAX_SILA_KOREKTY
    # max korekta <= 30% → mnożnik >= 0.70
    for v in k.values():
        assert v >= 0.70
        assert v <= 1.30


# ── koryguj_wagi ──────────────────────────────────────────────────────────────

WAGI_TEST = {
    "NORMAL": {"M": 1.0, "T": 1.0, "V": 1.0, "_default": 1.0},
    "RANGING": {"M": 0.5, "T": 0.5, "S": 1.5, "_default": 1.0},
}


def test_brak_dryfu_zwraca_oryginalne_wagi():
    a = DriftAdapter(okno=20)
    for _ in range(20):
        a.dodaj_rezim("NORMAL")  # stabilny = brak dryfu
    s = a.skanuj()
    wynik = a.koryguj_wagi(WAGI_TEST, "NORMAL", s)
    # brak dryfu → identyczne wagi (ten sam obiekt lub równoważny)
    assert wynik is WAGI_TEST or wynik == WAGI_TEST


def test_dryf_nie_modyfikuje_oryginalu():
    a = DriftAdapter(okno=20)
    rezimy = ["TRENDING_UP", "RANGING", "VOLATILE", "TRENDING_DOWN", "NORMAL"]
    for i in range(20):
        a.dodaj_rezim(rezimy[i % 5])
    s = a.skanuj()
    original_m = WAGI_TEST["NORMAL"]["M"]
    a.koryguj_wagi(WAGI_TEST, "NORMAL", s)
    assert WAGI_TEST["NORMAL"]["M"] == original_m  # oryginał niezmieniony


def test_default_klucz_nie_zmieniany():
    a = DriftAdapter(okno=20)
    for i in range(20):
        a.dodaj_rezim(["TRENDING_UP", "RANGING", "VOLATILE"][i % 3])
    s = a.skanuj()
    if s.czy_drift:
        wynik = a.koryguj_wagi(WAGI_TEST, "NORMAL", s)
        assert wynik["NORMAL"]["_default"] == 1.0


# ── okno krocze ──────────────────────────────────────────────────────────────

def test_okno_krocze_ogranicza_historyje():
    a = DriftAdapter(okno=5)
    for rezim in ["A"] * 10 + ["B"] * 10:
        a.dodaj_rezim(rezim)
    # po 20 dodaniach historia ma max 5 elementów
    assert len(a._historia) == 5
