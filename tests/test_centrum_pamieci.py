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
    # Dziś = 1.0 niezależnie od ważności (decay^0 == 1)
    assert cp._recency(dzis, 0.3) == 1.0
    assert cp._recency(dzis, 1.0) == 1.0


# ── Zanik warstwowy (FinMem layered decay, 2311.13743) ────────────────────────

def test_decay_warstwowy_krytyczne_wolniej():
    """Lekcja krytyczna (i=1.0) ma wolniejszy zanik niż rutynowa (i=0.3)."""
    assert cp._decay_dla_waznosci(1.0) > cp._decay_dla_waznosci(0.3)


def test_decay_warstwowy_granice():
    """Clamp: importance poza [0.3,1.0] nie wychodzi poza warstwy."""
    assert cp._decay_dla_waznosci(0.0) == cp._decay_dla_waznosci(0.3)
    assert cp._decay_dla_waznosci(2.0) == cp._decay_dla_waznosci(1.0)
    assert cp._decay_dla_waznosci(0.3) == cp._DECAY_SHALLOW
    assert cp._decay_dla_waznosci(1.0) == cp._DECAY_DEEP


def test_recency_krytyczna_przetrwa_dluzej():
    """Po 200 dniach lekcja krytyczna zachowuje wyższy recency niż rutynowa."""
    from datetime import date as _d
    data_str = _d.fromordinal(date.today().toordinal() - 200).isoformat()
    assert cp._recency(data_str, 1.0) > cp._recency(data_str, 0.3)


def test_score_krytyczna_wyprzedza_rutyne_po_czasie():
    """
    Regresja UTRATA POTENCJAŁU (Prawo XV): stara lekcja krytyczna ('utrata
    potencjału') po czasie bije świeższą rutynową dzięki wolniejszemu zanikowi.
    """
    from datetime import date as _d
    stara_data = _d.fromordinal(date.today().toordinal() - 150).isoformat()
    swieza_data = _d.fromordinal(date.today().toordinal() - 30).isoformat()
    kryt = {"data": stara_data, "tytul": "utrata potencjału w GARCH",
            "tresc": "krytyczny błąd"}
    rut = {"data": swieza_data, "tytul": "profil drobiazg", "tresc": "notatka"}
    assert cp.score_lekcji(kryt) > cp.score_lekcji(rut)


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


# ── PAMIĘĆ REŻIMOWA (unikat — 4. wymiar scoringu) ──────────────────────────────

def test_wykryj_rezim_token():
    assert cp._wykryj_rezim("lekcja w reżimie TREND_STRONG działa") == "TREND_STRONG"
    assert cp._wykryj_rezim("rynek VOLATILE — uważaj") == "VOLATILE"
    assert cp._wykryj_rezim("ogólna lekcja bez reżimu") is None


def test_regime_match_zgodny_pelna_waga():
    """Granica: ten sam reżim → 1.0."""
    assert cp._regime_match("TREND_STRONG", "TREND_STRONG") == 1.0


def test_regime_match_inny_tlumiony():
    """Granica: inny reżim → _DAMPEN_REZIM (<1.0)."""
    assert cp._regime_match("BULL", "BEAR") == cp._DAMPEN_REZIM
    assert cp._DAMPEN_REZIM < 1.0


def test_regime_match_brak_tagu_neutralny():
    """Granica: wspomnienie bez tagu reżimu → 1.0 (nie karzemy lekcji ogólnych)."""
    assert cp._regime_match(None, "BEAR") == 1.0


def test_regime_match_brak_biezacego_wylaczone():
    """Granica: brak bieżącego reżimu ('') → 1.0 (funkcja wyłączona, wstecznie kompat.)."""
    assert cp._regime_match("BULL", "") == 1.0


def test_regime_match_case_insensitive():
    assert cp._regime_match("bull", "BULL") == 1.0


def test_score_lekcji_rezim_tlumi_inny():
    """Lekcja z innego reżimu ma niższy score niż ta sama bez warunkowania."""
    lek = {"data": date.today().isoformat(), "tytul": "BULL kupuj dołki", "tresc": "działa w hossie"}
    bez = cp.score_lekcji(lek, "kupuj")
    w_bessie = cp.score_lekcji(lek, "kupuj", rezim_biezacy="BEAR")
    assert w_bessie < bez
    assert abs(w_bessie - bez * cp._DAMPEN_REZIM) < 1e-9


def test_score_lekcji_rezim_zgodny_bez_zmian():
    """Lekcja z bieżącego reżimu — score jak bez warunkowania (×1.0)."""
    lek = {"data": date.today().isoformat(), "tytul": "BULL kupuj dołki", "tresc": "działa w hossie"}
    bez = cp.score_lekcji(lek, "kupuj")
    w_hossie = cp.score_lekcji(lek, "kupuj", rezim_biezacy="BULL")
    assert abs(w_hossie - bez) < 1e-9


def test_szukaj_logi_rezim_tlumi(monkeypatch, tmp_path):
    """W1: log z innego reżimu dostaje niższy score przy warunkowaniu reżimem."""
    from imperium.biblioteki import pamiec_absolutna as pa
    monkeypatch.setattr(pa, "LOG_DIR", tmp_path)
    _zapisz_log_close(tmp_path, rezim="BULL", notatka="GARCH spike")
    p = _plik_z_lekcjami()
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    bez = cp.szukaj_wszedzie("GARCH", cel_kronika=tmp_path)
    w_bessie = cp.szukaj_wszedzie("GARCH", cel_kronika=tmp_path, rezim_biezacy="BEAR")
    s_bez = next(w["score"] for w in bez if w["warstwa"] == "logi")
    s_bessie = next(w["score"] for w in w_bessie if w["warstwa"] == "logi")
    assert s_bessie < s_bez


# ── szukaj_wszedzie() — warstwa W1 (logi pamiec_absolutna) ─────────────────────

def _zapisz_log_close(katalog, symbol="BTCUSDT", rezim="BULL", notatka="GARCH spike"):
    from imperium.biblioteki import pamiec_absolutna as pa
    from datetime import datetime, timezone
    log = pa.ImperiumLog(
        log_typ=pa.TypLogu.TRADE_CLOSE, sesja_id="s1", symbol=symbol, interwal="1h",
        rezim=rezim, kierunek_pozycji="LONG", pnl_pct=2.5, mae_pct=1.0, mfe_pct=3.0,
        powod_zamkniecia="take_profit", notatka=notatka,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )
    pa.PamiecAbsolutna(katalog).zapisz(log)


def test_szukaj_zawiera_warstwe_logi(monkeypatch, tmp_path):
    """W1: logi TRADE_CLOSE pojawiają się w cross-layer search (naprawa Prawa XV)."""
    from imperium.biblioteki import pamiec_absolutna as pa
    monkeypatch.setattr(pa, "LOG_DIR", tmp_path)
    _zapisz_log_close(tmp_path, notatka="GARCH spike reżim")
    p = _plik_z_lekcjami()
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    wyniki = cp.szukaj_wszedzie("GARCH", limit=10, cel_kronika=tmp_path)
    warstwy = {w["warstwa"] for w in wyniki}
    assert "logi" in warstwy
    log_wynik = next(w for w in wyniki if w["warstwa"] == "logi")
    assert "PnL=" in log_wynik["tresc"]
    assert log_wynik["rezim"] == "BULL"


def test_szukaj_logi_brak_dopasowania_odfiltrowany(monkeypatch, tmp_path):
    """Granica: log niepasujący do zapytania (relevance<0.05) nie wchodzi."""
    from imperium.biblioteki import pamiec_absolutna as pa
    monkeypatch.setattr(pa, "LOG_DIR", tmp_path)
    _zapisz_log_close(tmp_path, symbol="ETHUSDT", notatka="zwykłe zamknięcie")
    p = _plik_z_lekcjami()
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    wyniki = cp.szukaj_wszedzie("kompletnie inne zapytanie xyz", cel_kronika=tmp_path)
    assert not any(w["warstwa"] == "logi" for w in wyniki)


def test_szukaj_logi_brak_katalogu_nie_wybucha(monkeypatch, tmp_path):
    """Granica: brak katalogu logów → [] (resilient, nie wyjątek)."""
    from imperium.biblioteki import pamiec_absolutna as pa
    monkeypatch.setattr(pa, "LOG_DIR", tmp_path / "nieistnieje")
    p = _plik_z_lekcjami()
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", p)
    wyniki = cp.szukaj_wszedzie("cokolwiek", cel_kronika=tmp_path)
    assert isinstance(wyniki, list)  # nie wybucha


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


# ── W4 Rejestr Wizji i Decyzji ────────────────────────────────────────────────

def test_rejestr_wizji_dodaj_i_czytaj(tmp_path):
    """Dodany wpis pojawia się w wszystkie()."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "wizje.jsonl"
    rw.dodaj("WIZJA", "Portfel 20 par", "Multiasset docelowo", plik=plik)
    wpisy = rw.wszystkie(plik=plik)
    assert len(wpisy) == 1
    assert wpisy[0]["typ"] == "WIZJA"
    assert wpisy[0]["tytul"] == "Portfel 20 par"
    assert wpisy[0]["status"] == "POMYSŁ"


def test_rejestr_wizji_zmien_status(tmp_path):
    """zmien_status() aktualizuje pole status."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "wizje.jsonl"
    rw.dodaj("ZMIANA", "Dodano X-28", "MTF neuron", status="WDROŻONA", plik=plik)
    ok = rw.zmien_status("Dodano X-28", "ZAMKNIĘTA", plik=plik)
    assert ok
    assert rw.wszystkie(plik=plik)[0]["status"] == "ZAMKNIĘTA"


def test_rejestr_wizji_zmien_status_nie_istnieje(tmp_path):
    """zmien_status() zwraca False gdy tytuł nie znaleziony."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "wizje.jsonl"
    rw.dodaj("POMYSŁ", "Coś", "opis", plik=plik)
    assert not rw.zmien_status("Nieistniejący", "WDROŻONA", plik=plik)


def test_rejestr_wizji_scored_search(tmp_path):
    """szukaj_scored() zwraca wyniki z 'warstwa'='wizje'."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "wizje.jsonl"
    from datetime import date
    rw.dodaj("WIZJA", "portfel multiasset", "20 par krypto", plik=plik, data=date.today().isoformat())
    wyniki = rw.szukaj_scored("portfel", plik=plik)
    assert wyniki, "Brak wyników dla 'portfel'"
    assert wyniki[0]["warstwa"] == "wizje"
    assert wyniki[0]["score"] > 0


def test_rejestr_wizji_scored_pusty_plik(tmp_path):
    """szukaj_scored() na pustym pliku zwraca []."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "wizje_empty.jsonl"
    assert rw.szukaj_scored("cokolwiek", plik=plik) == []


def test_rejestr_wizji_bledny_typ_rzuca(tmp_path):
    """dodaj() z błędnym typem rzuca ValueError."""
    import pytest
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    with pytest.raises(ValueError):
        rw.dodaj("NIEZNANY_TYP", "tytuł", "treść", plik=plik)


def test_szukaj_wszedzie_zawiera_wizje(monkeypatch, tmp_path):
    """szukaj_wszedzie() po wdrożeniu W4 zwraca wyniki z warstwy 'wizje'."""
    from datetime import date
    from imperium.biblioteki import rejestr_wizji as rw
    from imperium.biblioteki import centrum_pamieci as cp

    plik_wizje = tmp_path / "wizje.jsonl"
    rw.dodaj("WIZJA", "portfel multiasset", "20 par krypto long-term",
             plik=plik_wizje, data=date.today().isoformat())

    # podmień domyślny plik rejestr_wizji w obu miejscach (moduł + alias w cp)
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik_wizje)
    monkeypatch.setattr(cp._rw, "PLIK_DOMYSLNY", plik_wizje)
    # podmień lekcje na puste
    plik_lekcji = tmp_path / "PAMIEC.md"
    plik_lekcji.write_text("# P\n\n## 📚 LEKCJE Z SESJI\n\n", encoding="utf-8")
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", plik_lekcji)
    # pusta kronika
    monkeypatch.setattr(cp._kc, "CEL_DOMYSLNY", tmp_path / "brak_kroniki")

    wyniki = cp.szukaj_wszedzie("portfel", limit=5)
    warstwy = {w["warstwa"] for w in wyniki}
    assert "wizje" in warstwy, f"Brak warstwy 'wizje' w wynikach: {warstwy}"


# ── Scoring kroniki (Opcja B) ─────────────────────────────────────────────────

def test_kronika_score_nie_jest_flat(monkeypatch, tmp_path):
    """Kronika ma zróżnicowany score — nie flat 0.3."""
    from imperium.biblioteki import centrum_pamieci as cp
    from imperium.biblioteki import kronika_czatu as kc

    # utwórz dwa pliki kroniki: jeden nowy, jeden stary
    kronika_dir = tmp_path / "kronika"
    kronika_dir.mkdir()
    import time

    plik_nowy = kronika_dir / "sesja_aaa111.md"
    plik_nowy.write_text("## 🧑 Cezar\nportfel multiasset krypto\n", encoding="utf-8")

    plik_stary = kronika_dir / "sesja_bbb222.md"
    plik_stary.write_text("## 🧑 Cezar\nportfel multiasset krypto\n", encoding="utf-8")
    # sztucznie "zestarzeć" plik — ustawiamy mtime na 2 lata temu
    stary_mtime = time.time() - 2 * 365 * 24 * 3600
    import os
    os.utime(str(plik_stary), (stary_mtime, stary_mtime))

    monkeypatch.setattr(kc, "CEL_DOMYSLNY", kronika_dir)
    monkeypatch.setattr(cp._kc, "CEL_DOMYSLNY", kronika_dir)

    plik_lekcji = tmp_path / "PAMIEC.md"
    plik_lekcji.write_text("# P\n\n## 📚 LEKCJE Z SESJI\n\n", encoding="utf-8")
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", plik_lekcji)

    wyniki = cp.szukaj_wszedzie("portfel", cel_kronika=kronika_dir, limit=10)
    kroniki = [w for w in wyniki if w["warstwa"] == "kronika"]
    assert len(kroniki) == 2
    scores = {w["sesja"]: w["score"] for w in kroniki}
    # nowy plik powinien mieć wyższy score niż stary
    assert scores["aaa111"] > scores["bbb222"], (
        f"Oczekiwano nowy > stary, got aaa111={scores['aaa111']:.3f} bbb222={scores['bbb222']:.3f}"
    )
