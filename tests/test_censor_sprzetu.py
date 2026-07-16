"""Testy CENSOR SPRZĘTU (Prawo XV, Prawo XXI) — bez sieci, bez zależności od
realnego żelaza maszyny testującej.

CENSOR podejmuje decyzje na PROGACH (RAM ≥12, VRAM ≥4/8/24 GB) i podnosi alarmy
potencjału przy awansie/degradacji klasy. Reguła Test-Granic (Prawo XXI) wymaga
testów wartości granicznych: dokładnie-próg, tuż-poniżej, None, oraz każdej
gałęzi alarmu (awans / degradacja / GPU pojawia się / GPU znika).
"""
from imperium.oczy import censor_sprzetu as cs


def _mig(ram=None, cuda=False, vram=0.0, cpu=4, nazwa="CPU", plat="Test 1"):
    return {
        "platforma": plat, "cpu_nazwa": nazwa, "cpu_logiczne": cpu,
        "ram_gb": ram, "gpu_cuda": cuda, "gpu_vram_gb": vram,
        "gpu_nazwa": "GPU" if cuda else None, "znacznik": "2026-01-01T00:00:00+00:00",
    }


# ── Klasy: monotoniczność rang i pokrycie ────────────────────────────────────
def test_rangi_rosnace_i_unikalne():
    rangi = [k["ranga"] for k in cs.KLASY]
    assert rangi == sorted(rangi), "rangi muszą rosnąć"
    assert len(set(rangi)) == len(rangi), "rangi muszą być unikalne"
    assert {k["klasa"] for k in cs.KLASY} == {
        "PROLETARIUS", "PEDES", "EQUES", "PRAETOR", "CONSUL"
    }


# ── Testy granic RAM (próg PEDES = 12 GB) ────────────────────────────────────
def test_ram_dokladnie_12gb_to_pedes():
    assert cs.sklasyfikuj(_mig(ram=12.0))["klasa"] == "PEDES"


def test_ram_tuz_ponizej_12gb_to_proletarius():
    assert cs.sklasyfikuj(_mig(ram=11.99))["klasa"] == "PROLETARIUS"


def test_ram_none_zachowawczo_proletarius():
    # Nieznany RAM NIE może zawyżać klasy (Prawo I) — traktowany jak najniższy.
    assert cs.sklasyfikuj(_mig(ram=None))["klasa"] == "PROLETARIUS"


def test_fujitsu_16gb_bez_gpu_to_pedes():
    assert cs.sklasyfikuj(_mig(ram=15.88))["klasa"] == "PEDES"


# ── Testy granic VRAM (progi EQUES=4, PRAETOR=8, CONSUL=24) ───────────────────
def test_vram_dokladnie_4gb_to_eques():
    assert cs.sklasyfikuj(_mig(ram=16, cuda=True, vram=4.0))["klasa"] == "EQUES"


def test_vram_dokladnie_8gb_to_praetor():
    assert cs.sklasyfikuj(_mig(ram=16, cuda=True, vram=8.0))["klasa"] == "PRAETOR"


def test_vram_dokladnie_24gb_to_consul():
    assert cs.sklasyfikuj(_mig(ram=32, cuda=True, vram=24.0))["klasa"] == "CONSUL"


def test_cuda_z_malym_vram_nie_awansuje_ponad_pedes():
    # GPU CUDA z <4 GB VRAM jest za słabe — RAM decyduje (PEDES), nie EQUES.
    assert cs.sklasyfikuj(_mig(ram=16, cuda=True, vram=2.0))["klasa"] == "PEDES"


# ── Wykrywanie zmian i alarmy potencjału (Prawo XV) ──────────────────────────
def test_awans_klasy_podnosi_alarm(monkeypatch):
    base = _mig(ram=16, cuda=False)                       # PEDES
    live = _mig(ram=32, cuda=True, vram=12.0)             # PRAETOR
    monkeypatch.setattr(cs, "wczytaj_baseline", lambda: base)
    monkeypatch.setattr(cs, "migawka_sprzetu", lambda: live)
    w = cs.wykryj_zmiane()
    assert any("AWANS KLASY" in a for a in w["alarmy"])
    assert any("GPU CUDA" in a for a in w["alarmy"])
    assert w["klasa_live"]["klasa"] == "PRAETOR"


def test_degradacja_klasy_podnosi_ostrzezenie(monkeypatch):
    base = _mig(ram=16, cuda=True, vram=12.0)             # PRAETOR
    live = _mig(ram=16, cuda=False)                       # PEDES
    monkeypatch.setattr(cs, "wczytaj_baseline", lambda: base)
    monkeypatch.setattr(cs, "migawka_sprzetu", lambda: live)
    w = cs.wykryj_zmiane()
    assert any("DEGRADACJA" in a for a in w["alarmy"])
    assert any("GPU CUDA ZNIK" in a for a in w["alarmy"])


def test_brak_zmian_brak_alarmow(monkeypatch):
    stan = _mig(ram=16, cuda=False)
    monkeypatch.setattr(cs, "wczytaj_baseline", lambda: dict(stan))
    monkeypatch.setattr(cs, "migawka_sprzetu", lambda: dict(stan))
    w = cs.wykryj_zmiane()
    assert w["alarmy"] == []
    assert w["zmiany"] == []


def test_pierwszy_cenzus_bez_baseline(monkeypatch):
    monkeypatch.setattr(cs, "wczytaj_baseline", lambda: None)
    monkeypatch.setattr(cs, "migawka_sprzetu", lambda: _mig(ram=16))
    w = cs.wykryj_zmiane()
    assert w["pierwszy_cenzus"] is True
    assert w["alarmy"] == []
    assert w["klasa_base"] is None


def test_wzrost_ram_bez_zmiany_klasy_daje_alarm_ram(monkeypatch):
    base = _mig(ram=16, cuda=False)                       # PEDES
    live = _mig(ram=24, cuda=False)                       # nadal PEDES, ale +8 GB
    monkeypatch.setattr(cs, "wczytaj_baseline", lambda: base)
    monkeypatch.setattr(cs, "migawka_sprzetu", lambda: live)
    w = cs.wykryj_zmiane()
    assert any("RAM WZR" in a for a in w["alarmy"])
    assert w["klasa_live"]["klasa"] == "PEDES"


# ── Baseline round-trip ──────────────────────────────────────────────────────
def test_baseline_zapis_odczyt(tmp_path, monkeypatch):
    plik = tmp_path / "censor_sprzet.json"
    monkeypatch.setattr(cs, "BAZA_BASELINE", plik)
    mig = _mig(ram=16, cuda=True, vram=8.0)
    cs.zapisz_baseline(mig)
    odczyt = cs.wczytaj_baseline()
    assert odczyt["ram_gb"] == 16
    assert odczyt["gpu_vram_gb"] == 8.0


# ── Smoke: żywy pomiar nie wywala się (jakikolwiek sprzęt CI/lokal) ───────────
def test_migawka_zywa_nie_wywala():
    mig = cs.migawka_sprzetu()
    assert "platforma" in mig and "ram_gb" in mig and "gpu_cuda" in mig
    assert isinstance(cs.sklasyfikuj(mig)["ranga"], int)
