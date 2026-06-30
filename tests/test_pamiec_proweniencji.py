"""Testy Pamięci Proweniencji (W13 — origin trail, W-360 v13)."""

from imperium.biblioteki import pamiec_proweniencji as pw


def _patch_zrodla(monkeypatch, dziennik=None, wizje=None, lekcje=None, kronika=None):
    import imperium.biblioteki.dziennik_niesmiertelny as dn
    import imperium.biblioteki.rejestr_wizji as rw
    import imperium.biblioteki.pamiec_sesji as ps
    import imperium.biblioteki.kronika_czatu as kc
    monkeypatch.setattr(dn, "wszystkie", lambda *a, **k: dziennik or [])
    monkeypatch.setattr(rw, "wszystkie", lambda *a, **k: wizje or [])
    monkeypatch.setattr(ps, "lekcje", lambda *a, **k: lekcje or [])
    monkeypatch.setattr(kc, "szukaj", lambda *a, **k: kronika or [])


def test_slad_chronologiczny(monkeypatch):
    _patch_zrodla(monkeypatch,
        dziennik=[{"data": "2026-06-28", "sesja": "abc", "co": ["numba wdrożona"], "decyzje": []}],
        lekcje=[{"data": "2026-06-21", "tytul": "numba pomysł", "tresc": "speedup"}])
    s = pw.slad("numba")
    assert len(s) == 2
    assert s[0]["data"] == "2026-06-21"   # najstarsze pierwsze (geneza)
    assert s[-1]["data"] == "2026-06-28"


def test_geneza_najstarsza(monkeypatch):
    _patch_zrodla(monkeypatch,
        lekcje=[{"data": "2026-06-21", "tytul": "kustosz idea", "tresc": "organ"}],
        dziennik=[{"data": "2026-06-28", "sesja": "x", "co": ["kustosz wdrożony"], "decyzje": []}])
    g = pw.geneza("kustosz")
    assert g["data"] == "2026-06-21"
    assert g["warstwa"] == "lekcje"


def test_raport_ugruntowanie(monkeypatch):
    _patch_zrodla(monkeypatch,
        kronika=[{"data": "2026-06-22", "sesja": "s1aaaaaa", "fragment": "numba szybki"},
                 {"data": "2026-06-23", "sesja": "s2bbbbbb", "fragment": "numba jit"}])
    r = pw.raport("numba")
    assert r["wystapien"] == 2
    assert r["sesje_unikalne"] == 2
    assert "kronika" in r["warstwy"]


def test_brak_sladu(monkeypatch):
    _patch_zrodla(monkeypatch)
    assert pw.slad("nieistniejacypojeciexyz") == []
    assert pw.geneza("nieistniejacypojeciexyz") is None


def test_puste_zapytanie(monkeypatch):
    _patch_zrodla(monkeypatch, lekcje=[{"data": "2026-06-01", "tytul": "x", "tresc": "y"}])
    assert pw.slad("") == []


def test_dopasowanie_po_slowie(monkeypatch):
    _patch_zrodla(monkeypatch,
        wizje=[{"data": "2026-06-01", "tytul": "Most Chmura Lokal", "tresc": "srodowisko"},
               {"data": "2026-06-02", "tytul": "Coś innego", "tresc": "nic"}])
    s = pw.slad("chmura")
    assert len(s) == 1
    assert "Chmura" in s[0]["fragment"]
