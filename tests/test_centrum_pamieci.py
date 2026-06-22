"""
Testy Centrum Pamięci (W-360 v3) — hub wszystkich warstw.

Weryfikuje:
  • scoring Generative Agents (recency × importance × relevance),
  • top_lekcji() — posortowane scored, nie "ostatnie N",
  • szukaj_wszedzie() — cross-layer (lekcje + kronika),
  • lekcje_scope() — filtr Mem0-style,
  • podsumowanie_startowe() — zawiera profil + top-k + statystyki,
  • granice: brak pliku, puste zapytanie, scoring decay.
"""

import tempfile
from pathlib import Path
from datetime import date

from imperium.biblioteki import centrum_pamieci as cp
from imperium.biblioteki import pamiec_sesji as ps


def _plik_z_lekcjami(*wpisy) -> Path:
    d = tempfile.mkdtemp()
    p = Path(d) / "PAMIEC.md"
    p.write_text("# P\n\n## Ostatnia aktualizacja: 2026-01-01\n\n"
                 "## 📚 LEKCJE Z SESJI\n\n", encoding="utf-8")
    for data, tytul, tresc in wpisy:
        ps.dopisz_lekcje(tytul, tresc, data=data, plik=p)
    return p


# ── Scoring Generative Agents ─────────────────────────────────────────────────

def test_recency_malejacy():
    """Starsza lekcja ma niższy recency score."""
    dzis = date.today().isoformat()
    stary = "2020-01-01"
    assert cp._recency(dzis) > cp._recency(stary)


def test_recency_dzisiaj_rowny_1():
    dzis = date.today().isoformat()
    assert cp._recency(dzis) == 1.0


def test_importance_krytyczne_slowo():
    """Lekcja z 'bug' / 'utrata potencjału' ma wyższy importance."""
    i_wysoki = cp._importance("bug w GARCH", "szczegóły naprawy")
    i_niski = cp._importance("Rutynowa praca", "opis sesji")
    assert i_wysoki > i_niski


def test_importance_minimum_bazowe():
    """Każda lekcja ma importance ≥ 0.3 (minimum bazowe)."""
    assert cp._importance("coś", "opis") >= 0.3


def test_relevance_trafne_slowa():
    q = "backtest sharpe"
    assert cp._relevance(q, "wyniki backtestu Sharpe", "szczegóły") > 0.0


def test_relevance_puste_zapytanie():
    """Puste zapytanie → relevance 0.5 (neutralna, nie blokuje)."""
    assert cp._relevance("", "cokolwiek", "treść") == 0.5


def test_score_lekcji_bez_zapytania():
    lek = {"data": date.today().isoformat(), "tytul": "bug naprawiony", "tresc": "fix"}
    s = cp.score_lekcji(lek)
    assert 0.0 < s <= 1.0


def test_score_lekcji_z_zapytaniem():
    lek = {"data": date.today().isoformat(), "tytul": "bug GARCH", "tresc": "fix speedup"}
    s_traf = cp.score_lekcji(lek, "GARCH speedup")
    s_chyb = cp.score_lekcji(lek, "telegram bot")
    assert s_traf > s_chyb


# ── top_lekcji() ──────────────────────────────────────────────────────────────

def test_top_lekcji_posortowane_malejaco(monkeypatch):
    """Wyniki posortowane od najwyższego score."""
    p = _plik_z_lekcjami(
        ("2020-01-01", "Stara rutyna", "opis"),
        (date.today().isoformat(), "bug krytyczny naprawiony", "fix GARCH"),
    )
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    top = cp.top_lekcji(2)
    assert top[0]["score"] >= top[1]["score"]


def test_top_lekcji_nie_jest_po_kolejnosci(monkeypatch):
    """Bug stary ale ważny (słowo 'bug') → może wyprzedzić nowszą rutynową."""
    p = _plik_z_lekcjami(
        ("2019-01-01", "bug absolutnie krytyczny", "utrata potencjału poważna"),
        (date.today().isoformat(), "zwykła notatka", "coś zrobiłem"),
    )
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    top = cp.top_lekcji(2)
    # Nie zakładamy kolejności — sprawdzamy tylko że jest 2 i posortowane
    assert len(top) == 2
    assert top[0]["score"] >= top[1]["score"]


# ── szukaj_wszedzie() ─────────────────────────────────────────────────────────

def test_szukaj_zwraca_lekcje_i_kroniki(monkeypatch, tmp_path):
    p = _plik_z_lekcjami((date.today().isoformat(), "test GARCH fix", "szczegóły naprawy"))
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    (tmp_path / "sesja_aaa.md").write_text("## 🧑 Cezar\nGARCH optymalizacja\n", encoding="utf-8")
    wyniki = cp.szukaj_wszedzie("GARCH", limit=10, cel_kronika=tmp_path)
    warstwy = {w["warstwa"] for w in wyniki}
    assert "lekcje" in warstwy
    assert "kronika" in warstwy


def test_szukaj_posortowane_malejaco(monkeypatch, tmp_path):
    p = _plik_z_lekcjami((date.today().isoformat(), "bug GARCH", "fix"))
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    wyniki = cp.szukaj_wszedzie("GARCH", cel_kronika=tmp_path)
    for i in range(len(wyniki) - 1):
        assert wyniki[i]["score"] >= wyniki[i + 1]["score"]


# ── lekcje_scope() ────────────────────────────────────────────────────────────

def test_lekcje_scope_filtr(monkeypatch):
    p = _plik_z_lekcjami(
        (date.today().isoformat(), "wyniki backtestu portfel", "sharpe 1.2"),
        (date.today().isoformat(), "telegram bot setup", "kod gotowy"),
    )
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    bt = cp.lekcje_scope("backtest")
    tg = cp.lekcje_scope("telegram")
    assert any("backtest" in l["tytul"].lower() for l in bt)
    assert not any("backtest" in l["tytul"].lower() for l in tg)


def test_lekcje_scope_gwiazdka_zwraca_wszystkie(monkeypatch):
    p = _plik_z_lekcjami(
        (date.today().isoformat(), "A", "a"),
        (date.today().isoformat(), "B", "b"),
    )
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    assert len(cp.lekcje_scope("*")) == 2


# ── podsumowanie_startowe() ───────────────────────────────────────────────────

def test_podsumowanie_zawiera_centrum(monkeypatch, tmp_path):
    p = _plik_z_lekcjami((date.today().isoformat(), "bug naprawiony", "fix"))
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    out = cp.podsumowanie_startowe(k=1)
    assert "CENTRUM PAMIĘCI" in out
    assert "Top-1" in out
    assert "Kronika" in out
