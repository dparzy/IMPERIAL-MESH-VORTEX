"""Testy DESCRIPTIO IMPERII — podziału Imperium na filary.

Ten organ ma JEDNO zadanie, którego nie wolno mu zawalić po cichu: **żaden moduł nie może
wypaść z obrazu**. Dlatego najważniejsze testy to nie te sprawdzające ładny wydruk, lecz te
pilnujące, że nowy katalog w repo **wywraca organ na czerwono**, zamiast zniknąć z mapy —
na tym poległ MATURITAS (52 wiersze ROADMAP poza pomiarem) i to była jedna z trzech dziur,
które kazały Cezarowi zamrozić rozwój 2026-08-04.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.oczy import descriptio as D  # noqa: E402


# ── 1. PODZIAŁ NA ŻYWYM REPO — kompletny i domknięty ────────────────────────────

def test_zywe_repo_bez_sierot():
    p = D.podzial()
    assert p["nieprzypisane"] == [], f"moduły poza filarami: {p['nieprzypisane'][:5]}"


def test_suma_filarow_rowna_liczbie_modulow():
    """Dowód kompletności: podział NIE MOŻE gubić modułów po drodze."""
    p = D.podzial()
    suma = sum(len(d["moduly"]) for d in p["filary"].values())
    assert suma == p["modulow_razem"]


def test_zywe_repo_zgodne():
    assert D.zgodny() is True, D.bledy()


def test_kazdy_filar_ma_powod_i_straznika():
    for filar, dane in D.podzial()["filary"].items():
        assert dane["po_co"].strip(), f"{filar} nie mówi, po co istnieje"
        assert dane["straznik"].strip(), f"{filar} nie ma strażnika"


# ── 2. GRANICA: NOWY KATALOG MUSI KRZYCZEĆ, NIE ZNIKAĆ ──────────────────────────

def _podzial_z(spis, monkeypatch):
    import narzedzia.census_organorum as C
    monkeypatch.setattr(C, "spisz_moduly", lambda: spis)
    return D.podzial()


def test_nowy_katalog_poza_filarami_to_alarm(monkeypatch):
    """Klasa K2: moduł, którego nikt nie przypisał, NIE MOŻE po cichu wypaść z obrazu."""
    p = _podzial_z({"imperium/nowy_organ": [("cos.py", "rola")]}, monkeypatch)
    assert p["nieprzypisane"] == ["imperium/nowy_organ/cos.py"]
    assert D.zgodny(p) is False
    assert any("POZA filarami" in b for b in D.bledy(p))


def test_znany_katalog_nie_alarmuje(monkeypatch):
    """Druga strona granicy — bramka, która alarmuje zawsze, jest bezużyteczna."""
    p = _podzial_z({"imperium/legiony": [("rejestr.py", "rola")]}, monkeypatch)
    assert p["nieprzypisane"] == []
    assert D.zgodny(p) is True


def test_straznik_widmo_to_alarm(monkeypatch):
    """Filar nie może wskazywać strażnika, którego nie ma w kodzie (klasa API-widm, W16)."""
    monkeypatch.setattr(D, "FILARY", [
        ("imperium/legiony", "IV. RÓJ", "liczy sygnały", "imperium/legiony/NIE_MA_MNIE.py"),
    ])
    p = _podzial_z({"imperium/legiony": [("rejestr.py", "rola")]}, monkeypatch)
    assert D.zgodny(p) is False
    assert any("NIE MA w kodzie" in b for b in D.bledy(p))


# ── 3. DOPASOWANIE PO NAJDŁUŻSZYM PREFIKSIE ─────────────────────────────────────

def test_rag_idzie_do_wiedzy_a_reszta_narzedzi_do_pomiaru():
    """`narzedzia/rag` musi wygrać z `narzedzia` — inaczej RAG wypadłby z filara WIEDZY."""
    assert D._filar_dla("narzedzia/rag")[0].startswith("I.")
    assert D._filar_dla("narzedzia")[0].startswith("XI.")


def test_podkatalog_dziedziczy_po_rodzicu():
    assert D._filar_dla("imperium/cesarz/doradcy")[0] == D._filar_dla("imperium/cesarz")[0]


def test_katalog_spoza_mapy_nie_ma_filara():
    assert D._filar_dla("cokolwiek/innego") is None


# ── 4. WSPÓŁPRACA — tylko MIĘDZY filarami ───────────────────────────────────────

def test_wspolpraca_pomija_krawedzie_wewnatrz_filara():
    """Import w obrębie jednego filara nie jest współpracą filarów — inaczej duży filar
    wyglądałby na najbardziej zintegrowany tylko dlatego, że jest duży."""
    for (a, b) in D.wspolpraca().keys():
        assert a != b


def test_wspolpraca_ma_krawedzie_na_zywym_repo():
    assert len(D.wspolpraca()) > 0, "zero krawędzi na żywym repo = licznik przestał liczyć"


# ── 5. RAPORT I BRAMKA ──────────────────────────────────────────────────────────

def test_raport_mowi_o_kompletnosci():
    t = D.raport_tekst()
    assert "RAZEM" in t and "zero pominięć" in t


def test_bramka_zwraca_zero_gdy_zgodne():
    assert D.main(["--bramka"]) == 0
