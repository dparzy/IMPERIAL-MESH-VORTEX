"""Testy Pamięci Roboczej (W12 — CoALA working memory, W-360 v12)."""

from imperium.biblioteki import pamiec_robocza as pr


def test_aktywny_cel_z_dziennika(monkeypatch):
    import imperium.biblioteki.dziennik_niesmiertelny as dn
    monkeypatch.setattr(dn, "ostatni_wpis", lambda *a, **k: {"nastepny": "zrób Y"})
    assert pr.aktywny_cel() == "zrób Y"


def test_aktywny_cel_brak(monkeypatch):
    import imperium.biblioteki.dziennik_niesmiertelny as dn
    monkeypatch.setattr(dn, "ostatni_wpis", lambda *a, **k: None)
    assert pr.aktywny_cel() is None


def test_ognisko_struktura(monkeypatch):
    import imperium.biblioteki.dziennik_niesmiertelny as dn
    import imperium.biblioteki.refleksja_pamieci as rp
    monkeypatch.setattr(dn, "ostatni_wpis", lambda *a, **k: {"nastepny": "cel Z"})
    monkeypatch.setattr(rp, "raport", lambda *a, **k: {"sprzeczne": [], "przedawnione": []})
    o = pr.ognisko()
    assert o["aktywny_cel"] == "cel Z"
    assert o["pilne"] == []


def test_raport_startowy_pusty_bez_celu(monkeypatch):
    import imperium.biblioteki.dziennik_niesmiertelny as dn
    monkeypatch.setattr(dn, "ostatni_wpis", lambda *a, **k: None)
    assert pr.raport_startowy() == ""


def test_pilne_zglasza_sprzecznosci(monkeypatch):
    import imperium.biblioteki.refleksja_pamieci as rp
    monkeypatch.setattr(rp, "raport", lambda *a, **k: {
        "sprzeczne": [{"temat": ["portfel", "koszyk"]}], "przedawnione": [1, 2]})
    p = pr.pilne()
    assert any("sprzeczność" in x for x in p)
    assert any("wisi" in x for x in p)
