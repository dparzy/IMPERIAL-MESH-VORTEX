"""Testy MATURITAS — organu mierzącego piętro inżynierii (prompt / loop / graph).

Organ powstał z rozkazu Cezara „pilnujmy i weryfikujmy stany prompt/loop/graph" i jest
pierwszą ŻYWĄ kategorią projektu INGENIUM. Testy pilnują jego zasad nienaruszalnych —
bo miernik bez nich zamienia się w laurkę.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.oczy import maturitas as m  # noqa: E402


# ── Skala poziomów ──────────────────────────────────────────────────────────────

def test_poziom_nie_przeskakuje_progu():
    """Kolejność progów jest ISTOTĄ: graf z tysiącem węzłów, którego nikt nie czyta przy
    decyzji, NIE jest dojrzalszy od małego grafu, który decyduje."""
    assert m._poziom([True, True, True, True]) == 4
    assert m._poziom([True, False, True, True]) == 1, "przeskoczył niespełniony próg"
    assert m._poziom([False, True, True, True]) == 0


def test_kazdy_poziom_ma_nazwe():
    for i in range(5):
        assert m.POZIOMY[i]


# ── Zasady nienaruszalne z projektu INGENIUM ────────────────────────────────────

def test_kazde_pietro_ma_antywskaznik():
    """ZASADA INGENIUM: każda kategoria musi mieć zapisane, JAK można ją oszukać.
    Miernik bez antywskaźnika to zaproszenie do grania pod miarę (Goodhart)."""
    for p in m.zmierz()["pietra"]:
        assert p["antywskaznik"].strip(), f"{p['pietro']} bez antywskaźnika"
        assert len(p["antywskaznik"]) > 40, f"{p['pietro']}: antywskaźnik bez treści"


def test_nie_ma_jednej_oceny_imperium():
    """Uśrednienie trzech pięter ukryłoby to, co najważniejsze — można mieć doskonały
    LOOP przy zerowym GRAPH. Organ świadomie NIE liczy jednej liczby."""
    w = m.zmierz()
    assert "ocena" not in w and "iq" not in w and "wynik" not in w
    assert len(w["poziomy"]) == 3


def test_raport_przypomina_o_goodharcie():
    """Lustro, nie kierownica — i ma to być napisane tam, gdzie Cezar patrzy."""
    tekst = m.raport()
    assert "Goodhart" in tekst
    assert "NIE steruje" in tekst


def test_organ_nie_jest_wpiety_w_sciezke_decyzyjna():
    """Twarda granica z projektu INGENIUM: wynik NIGDY nie steruje decyzją handlową.
    Test pilnuje, że żaden moduł ścieżki decyzyjnej nie importuje tego organu."""
    import subprocess
    korzen = Path(__file__).resolve().parent.parent
    p = subprocess.run(["git", "grep", "-l", "maturitas", "--", "imperium/"],
                       cwd=korzen, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    czytelnicy = [x for x in p.stdout.split() if not x.endswith("maturitas.py")]
    zakazane = [c for c in czytelnicy if any(s in c for s in m.SCIEZKA_DECYZJI)]
    assert not zakazane, f"MATURITAS wpięty w ścieżkę decyzyjną: {zakazane}"


# ── Brak pomiaru to NIEZNANE, nie zero ──────────────────────────────────────────

def test_brak_odczytu_grafu_daje_NIEZNANE_a_nie_zero(monkeypatch):
    """Prawo I: rzecz niezmierzona nie jest zerem. Zero znaczyłoby „graf jest pusty",
    a to zupełnie inna wiadomość niż „nie umiem odczytać"."""
    monkeypatch.setattr(m, "_git", lambda *a: "")
    import imperium.biblioteki.graf_pamieci as g
    monkeypatch.setattr(g, "_wczytaj", lambda *a, **k: (_ for _ in ()).throw(OSError("brak")))
    w = m.zmierz_graph()
    assert w["wskazniki"]["wezly"] == m.NIEZNANE
    assert w["poziom"] == 0


def test_uszkodzony_wiersz_ledgera_nie_oslepia_organu(tmp_path, monkeypatch):
    """Jedna zepsuta linia JSONL nie może wywrócić całego pomiaru — inaczej organ
    milczy dokładnie wtedy, gdy dane są w złym stanie."""
    plik = tmp_path / "x.jsonl"
    plik.write_text('{"a": 1}\nNIE-JSON\n{"b": 2}\n', encoding="utf-8")
    monkeypatch.setattr(m, "DANE", tmp_path)
    assert len(m._jsonl("x.jsonl")) == 2


# ── Regresja realnego błędu pomiaru (2026-08-02) ────────────────────────────────

def test_status_zamkniecia_liczony_po_OSTATNIM_rekordzie_elementu(tmp_path, monkeypatch):
    """REGRESJA: skaner filtrował status `ZAMKNIETA` (żeńska końcówka), a ledger zapisuje
    `ZAMKNIETE` — dało to fałszywy alarm „55 sugestii, ZERO zamkniętych".

    Ledger jest append-only, więc zamknięcie to OSOBNY rekord tego samego elementu.
    Liczenie rekordów zamiast elementów zawyża otwarte — i tak właśnie się pomyliłem.
    """
    (tmp_path / "rejestr_testow.jsonl").write_text(
        '{"typ":"SUGESTIA","element":"A","status":"KANDYDAT"}\n'
        '{"typ":"SUGESTIA","element":"A","status":"ZAMKNIETE"}\n'
        '{"typ":"SUGESTIA","element":"B","status":"KANDYDAT"}\n'
        '{"typ":"SUGESTIA","element":"C","status":"ZREALIZOWANE"}\n', encoding="utf-8")
    for nazwa in ("wizje_i_decyzje.jsonl", "codex_notarum.jsonl"):
        (tmp_path / nazwa).write_text("", encoding="utf-8")
    monkeypatch.setattr(m, "DANE", tmp_path)
    w = m.zmierz_loop()["wskazniki"]
    assert w["sugestie_zamkniete"] == 2, "zamknięcie w drugim rekordzie nie zostało policzone"
    assert w["sugestie_otwarte"] == 1, "liczy rekordy zamiast elementów"


def test_warstwy_liczone_po_znacznikach_a_nie_nazwach_funkcji():
    """REGRESJA: `def _warstwa_\\d+` dawało 15 przy realnych 24 — część warstw żyje
    w helperach. Miara ma liczyć to, co audyt EGZEKWUJE (znaczniki `[W..]`)."""
    w = m.zmierz_loop()["wskazniki"]
    assert w["warstwy_audytu"] >= 20, f"warstwy zaniżone: {w['warstwy_audytu']}"


# ── Pomiar na żywym repo ────────────────────────────────────────────────────────

def test_pomiar_na_zywym_repo_daje_trzy_pietra():
    w = m.zmierz()
    assert [p["pietro"] for p in w["pietra"]] == ["PROMPT", "LOOP", "GRAPH"]
    for p in w["pietra"]:
        assert 0 <= p["poziom"] <= 4
        assert p["wskazniki"], f"{p['pietro']} bez ani jednego wskaźnika"


def test_wask_gardlo_nazywa_przyczyne_a_nie_tylko_fakt():
    """Alarm bez przyczyny jest tapetą — Cezar ma wiedzieć, CO naprawić."""
    for p in m.zmierz()["pietra"]:
        if p["wask"]:
            assert len(p["wask"]) > 30, f"{p['pietro']}: wąskie gardło bez wyjaśnienia"
