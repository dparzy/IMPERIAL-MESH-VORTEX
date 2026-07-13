"""Testy W-361 — ważenie głosów IC w Legatusie (hipoteza B, Grinold&Kahn, opt-in OFF).

Reguła Test-Granic (Prawo XXI): moduł zmienia AGREGAT na ZNAKU/PROGU → testujemy granice,
nie tylko happy-path. Kluczowe niebezpieczeństwa ważenia IC:
  • OFF domyślnie MUSI być byte-identyczne ze starym zachowaniem (ZASADA WPIĘCIA).
  • IC<0 ODWRACA kierunek (neuron mylący się systematycznie) — bucket flip.
  • IC=0 / brak pomiaru → neuron NIE waży (nie może wpaść w przeciwny kierunek przez pomyłkę).
  • Jednorodne skalowanie IC nie może zmienić kierunku (normalizacja je znosi).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.legatus import Legatus, oblicz_wagi_ic
from imperium.legiony.mikro_neuron import SygnalNeuronu


def _syg(nid, kier, finalna, waga=5, kat="M"):
    """Sygnał z zadaną pewnością finalną (bezpośrednio — pomijamy policz_finalna)."""
    s = SygnalNeuronu(neuron_id=nid, legion="SWING", wskaznik="X", wartosc=1.0,
                      kierunek=kier, waga=waga, kategoria=kat)
    s.pewnosc_finalna = finalna
    return s


def _leg():
    return Legatus(neurony=[], min_neuronow=1, min_przewaga=0.1)


# ── Domyślnie OFF: brak zmiany ścieżki decyzyjnej (ZASADA WPIĘCIA) ──────────────

def test_domyslnie_wazenie_off():
    leg = _leg()
    assert leg.wazenie_ic is False
    assert leg.wagi_ic == {}


def test_off_identyczne_ze_starym_zachowaniem():
    # 2×LONG (0.4×5=2.0 każdy) vs 1×SHORT (0.3×5=1.5) → LONG, prev = 4.0/5.5
    leg = _leg()
    syg = [_syg("A", "LONG", 0.4), _syg("B", "LONG", 0.4), _syg("C", "SHORT", 0.3)]
    r = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    assert r.kierunek == "LONG"
    assert abs(r.pewnosc_agregatu - (4.0 / 5.5)) < 1e-3
    assert r.zgodnych_neuronow == 2


# ── ON: własności skalowania (nie mogą zmienić kierunku) ───────────────────────

def test_on_jednorodne_ic_nie_zmienia_kierunku():
    # wszystkie IC = 1.0 → |ic|=1 → wkłady bez zmian → identyczny agregat jak OFF
    syg = [_syg("A", "LONG", 0.4), _syg("B", "LONG", 0.4), _syg("C", "SHORT", 0.3)]
    leg = _leg()
    off = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    leg.ustaw_wagi_ic({"A": 1.0, "B": 1.0, "C": 1.0}, wlacz=True)
    on = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    assert on.kierunek == off.kierunek
    assert abs(on.pewnosc_agregatu - off.pewnosc_agregatu) < 1e-9


def test_on_stale_ic_znosi_sie_w_normalizacji():
    # wszystkie IC = 0.5 → sila_l i sila_s ×0.5 → prev bez zmian (normalizacja)
    syg = [_syg("A", "LONG", 0.4), _syg("B", "SHORT", 0.3)]
    leg = _leg()
    off = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    leg.ustaw_wagi_ic({"A": 0.5, "B": 0.5}, wlacz=True)
    on = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    assert on.kierunek == off.kierunek
    assert abs(on.pewnosc_agregatu - off.pewnosc_agregatu) < 1e-6


# ── ON: odwracanie znaku (rdzeń hipotezy B) ────────────────────────────────────

def test_on_ic_ujemny_odwraca_kierunek_agregatu():
    # A: LONG mocny (0.5×5=2.5) ale IC=-1 → efektywnie SHORT; B: SHORT słaby IC=+1
    # OFF → LONG wygrywa; ON → A odwrócony na SHORT, agregat SHORT
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.2)]
    leg = _leg()
    off = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    assert off.kierunek == "LONG"
    leg.ustaw_wagi_ic({"A": -1.0, "B": 1.0}, wlacz=True)
    on = leg._agreguj("SYM", "FOKUS", "NORMAL", syg)
    assert on.kierunek == "SHORT"
    # buckety odzwierciedlają kierunek EFEKTYWNY: oba głosy po stronie SHORT
    assert on.zgodnych_neuronow == 2


# ── ON: IC=0 i brak pomiaru → neuron milczy (nie fałszuje agregatu) ────────────

def test_on_ic_zero_wycisza_neuron():
    # A: LONG mocny ale IC=0 → wkład 0; B: SHORT z IC=1 → agregat SHORT (A milczy)
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.3)]
    leg = _leg()
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "LONG"  # OFF
    leg.ustaw_wagi_ic({"A": 0.0, "B": 1.0}, wlacz=True)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "SHORT"


def test_on_brak_pomiaru_domyslny_zero_wycisza():
    # jedyny głos A (LONG) nie ma pomiaru; domyslny_ic=0 → wkład 0 → brak decyzji (NEUTRAL)
    syg = [_syg("A", "LONG", 0.5)]
    leg = _leg()
    leg.ustaw_wagi_ic({"INNY": 1.0}, wlacz=True, domyslny_ic=0.0)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "NEUTRAL"


def test_on_brak_pomiaru_domyslny_dodatni_zachowuje_glos():
    # ten sam przypadek, ale domyslny_ic=0.5 → A zachowuje minimalny głos → LONG
    syg = [_syg("A", "LONG", 0.5)]
    leg = _leg()
    leg.ustaw_wagi_ic({"INNY": 1.0}, wlacz=True, domyslny_ic=0.5)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "LONG"


# ── Guardy setterów ────────────────────────────────────────────────────────────

def test_ustaw_wagi_ic_wlacz_false_zapisuje_ale_nie_wazy():
    leg = _leg()
    leg.ustaw_wagi_ic({"A": -1.0}, wlacz=False)
    assert leg.wagi_ic == {"A": -1.0}
    assert leg.wazenie_ic is False


def test_ustaw_wagi_ic_puste_nie_wlacza():
    # pusty słownik nie może włączyć ważenia (brak czym ważyć — guard)
    leg = _leg()
    leg.ustaw_wagi_ic({}, wlacz=True)
    assert leg.wazenie_ic is False


def test_resetuj_wazenie_ic_wylacza():
    leg = _leg()
    leg.ustaw_wagi_ic({"A": 1.0}, wlacz=True)
    assert leg.wazenie_ic is True
    leg.resetuj_wazenie_ic()
    assert leg.wazenie_ic is False


def test_pusty_guard_w_wkladach_gdy_wagi_puste():
    # wazenie_ic True ale wagi puste (obejście settera) → traktuj jak OFF
    leg = _leg()
    leg.wazenie_ic = True
    leg.wagi_ic = {}
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.2)]
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "LONG"


# ── W-361b SHRINKAGE: próg istotności |IC| + tryb tylko-znak ──────────────────

def test_shrinkage_ponizej_progu_neuron_zostaje_baseline():
    # A: LONG mocny, ale IC=-0.01 (szum) < prog 0.03 → NIE odwraca, zostaje LONG na baseline.
    # B: SHORT słaby. OFF→LONG; z shrinkage nadal LONG (szum nie flipuje).
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.2)]
    leg = _leg()
    leg.ustaw_wagi_ic({"A": -0.01, "B": 0.5}, wlacz=True, prog_ic=0.03)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "LONG"


def test_shrinkage_powyzej_progu_odwraca():
    # A: IC=-0.1 (istotny) ≥ prog 0.03 → odwrócony na SHORT; efekt jak w pełnym W-361.
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.2)]
    leg = _leg()
    leg.ustaw_wagi_ic({"A": -0.1, "B": 0.1}, wlacz=True, prog_ic=0.03)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "SHORT"


def test_shrinkage_prog_dokladnie_na_granicy_koryguje():
    # |IC| == prog → warunek >=, więc korekta DZIAŁA (granica inkluzywna).
    syg = [_syg("A", "LONG", 0.5)]
    leg = _leg()
    leg.ustaw_wagi_ic({"A": -0.03}, wlacz=True, prog_ic=0.03, skaluj_ic=False)
    # flip na SHORT z baseline → kierunek SHORT
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "SHORT"


def test_tryb_tylko_znak_ignoruje_magnitude():
    # A bazowo mocniejszy (2.5) niż B (2.0). Ze skalą: A×0.5=1.25 < B×1.0=2.0 → SHORT.
    # Bez skali: baseline A=2.5 > B=2.0 → LONG. Dowodzi, że skaluj_ic ignoruje magnitude |IC|.
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.4)]
    leg = _leg()
    leg.ustaw_wagi_ic({"A": 0.5, "B": 1.0}, wlacz=True, skaluj_ic=True)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "SHORT"   # ze skalą magnitudy
    leg.ustaw_wagi_ic({"A": 0.5, "B": 1.0}, wlacz=True, skaluj_ic=False)
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "LONG"    # bez skali → baseline


def test_shrinkage_prog_zero_zachowuje_stare_w361():
    # prog=0 + skaluj=True (domyślne) → identyczne z pierwotnym W-361 (flip przy IC<0).
    syg = [_syg("A", "LONG", 0.5), _syg("B", "SHORT", 0.2)]
    leg = _leg()
    leg.ustaw_wagi_ic({"A": -1.0, "B": 1.0}, wlacz=True)   # prog_ic=0.0, skaluj_ic=True domyślnie
    assert leg._agreguj("SYM", "FOKUS", "NORMAL", syg).kierunek == "SHORT"


# ── Kanoniczna oblicz_wagi_ic (jedno źródło prawdy z hipoteza_b) ───────────────

def test_oblicz_wagi_ic_dodatni_gdy_trafia():
    syg = [{"A": "LONG"}, {"A": "LONG"}, {"A": "LONG"}]
    assert oblicz_wagi_ic(syg, [1, 1, 1]) == {"A": 1.0}


def test_oblicz_wagi_ic_ujemny_gdy_myli():
    assert oblicz_wagi_ic([{"A": "LONG"}, {"A": "LONG"}], [-1, -1]) == {"A": -1.0}


def test_oblicz_wagi_ic_pomija_abstynencje():
    # NEUTRAL/"" nie liczą się do IC (brak głosu ≠ zerowa trafność)
    w = oblicz_wagi_ic([{"A": "NEUTRAL"}, {"A": "LONG"}], [1, 1])
    assert w == {"A": 1.0}


def test_oblicz_wagi_ic_min_glosow_odcina():
    # A głosuje raz → przy min_glosow=2 pomijany (za mało danych na wiarygodne IC)
    assert oblicz_wagi_ic([{"A": "LONG"}], [1], min_glosow=2) == {}


def test_oblicz_wagi_ic_pusty_nie_wybucha():
    assert oblicz_wagi_ic([], []) == {}
