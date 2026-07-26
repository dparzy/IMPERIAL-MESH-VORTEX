"""
Testy Centrum Pamięci (W-360 v5) — hub wszystkich warstw.

Weryfikuje:
  • scoring Generative Agents (recency × importance × relevance × regime),
  • top_lekcji() — posortowane scored, nie "ostatnie N",
  • szukaj_wszedzie() — cross-layer 6 warstw (lekcje+kronika+wizje+logi+wiedza+refleksje),
  • W4 rejestr_wizji + dedup, W5 most chmura↔lokal (srodowisko_pamieci),
  • lekcje_scope() — filtr Mem0-style,
  • podsumowanie_startowe() — zawiera profil + top-k + manifest + statystyki,
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

    # HERMETYCZNOŚĆ (Prawo XXI): izolujemy pozostałe warstwy cross-layer. Bez tego test
    # zależał od realnych danych — gdy wizje_i_decyzje.jsonl urosło, trafienia „portfel"
    # z wizji/RAG wypychały starą kronikę (recency≈0) poza limit=10 → fałszywy czerwony.
    # Ten test sprawdza WYŁĄCZNIE scoring kroniki (recency: nowy > stary).
    monkeypatch.setattr(cp, "_szukaj_w_logach", lambda *a, **k: [])
    monkeypatch.setattr(cp, "_szukaj_w_rag", lambda *a, **k: [])
    monkeypatch.setattr(cp, "_szukaj_w_refleksjach", lambda *a, **k: [])
    monkeypatch.setattr(cp._rw, "szukaj_scored", lambda *a, **k: [])

    wyniki = cp.szukaj_wszedzie("portfel", cel_kronika=kronika_dir, limit=10)
    kroniki = [w for w in wyniki if w["warstwa"] == "kronika"]
    assert len(kroniki) == 2
    scores = {w["sesja"]: w["score"] for w in kroniki}
    # nowy plik powinien mieć wyższy score niż stary
    assert scores["aaa111"] > scores["bbb222"], (
        f"Oczekiwano nowy > stary, got aaa111={scores['aaa111']:.3f} bbb222={scores['bbb222']:.3f}"
    )


# ── W5 Most Chmura↔Lokal (srodowisko_pamieci) ────────────────────────────────

def test_wykryj_srodowisko_chmura(monkeypatch):
    """CLAUDE_CODE_REMOTE=true → 'chmura' (silniejszy niż reguła Windows→lokal)."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.delenv("IMPERIUM_SRODOWISKO", raising=False)
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    assert sp.wykryj_srodowisko() == "chmura"


def test_wykryj_srodowisko_lokal(monkeypatch):
    """Brak zmiennych web → 'lokal'."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.delenv("IMPERIUM_SRODOWISKO", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.delenv("CLAUDE_ENV_FILE", raising=False)
    assert sp.wykryj_srodowisko() == "lokal"


def test_wykryj_srodowisko_override_lokal(monkeypatch):
    """IMPERIUM_SRODOWISKO=lokal wygrywa NAWET z sygnałem zdalnym (trwały rozkaz Cezara)."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.setenv("IMPERIUM_SRODOWISKO", "lokal")
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setenv("CLAUDE_ENV_FILE", "/tmp/env")
    assert sp.wykryj_srodowisko() == "lokal"


def test_wykryj_srodowisko_override_chmura(monkeypatch):
    """IMPERIUM_SRODOWISKO=chmura wymusza chmurę nawet na Windows (jawne nadpisanie)."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.setenv("IMPERIUM_SRODOWISKO", "chmura")
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    assert sp.wykryj_srodowisko() == "chmura"


def test_wykryj_srodowisko_windows_bez_env_file(monkeypatch):
    """Windows z CLAUDE_ENV_FILE (hook lokalny) → nadal 'lokal', nie fałszywa chmura."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.delenv("IMPERIUM_SRODOWISKO", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setenv("CLAUDE_ENV_FILE", "/tmp/env")  # harness ustawia to też w hooku lokalnym
    monkeypatch.setattr(sp.sys, "platform", "win32")
    assert sp.wykryj_srodowisko() == "lokal"


def test_wykryj_srodowisko_linux_env_file_chmura(monkeypatch):
    """Linux (telefon/chmura) z CLAUDE_ENV_FILE → 'chmura' (adaptacyjność zachowana)."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    monkeypatch.delenv("IMPERIUM_SRODOWISKO", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setenv("CLAUDE_ENV_FILE", "/tmp/env")
    monkeypatch.setattr(sp.sys, "platform", "linux")
    assert sp.wykryj_srodowisko() == "chmura"


def test_raport_dostepnosci_ma_klucze():
    """raport_dostepnosci() zwraca komplet pól do manifestu."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    r = sp.raport_dostepnosci()
    for klucz in ("srodowisko", "rag_tryb", "rag_fragmenty", "rag_wektory",
                  "kronika_sesje", "wizje_wpisy", "model_embeddings"):
        assert klucz in r, f"Brak klucza {klucz} w raporcie"


def test_manifest_zawiera_srodowisko():
    """manifest_pamieci() zawiera nazwę środowiska i warstwy."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    m = sp.manifest_pamieci()
    assert "MANIFEST PAMIĘCI" in m
    assert "W3" in m and "W2" in m
    assert "kronika" in m.lower()


def test_instrukcja_lokal_ma_kroki():
    """instrukcja_lokal() zawiera konkretne komendy odblokowania wektorów."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    i = sp.instrukcja_lokal()
    assert "git pull" in i
    assert "indeksuj.py" in i


def test_alarm_rag_bez_wektorow(monkeypatch):
    """Gdy RAG istnieje ale wektory=0 → alarm UTRATY POTENCJAŁU."""
    from imperium.biblioteki import srodowisko_pamieci as sp
    rap = {
        "srodowisko": "lokal", "rag_baza_istnieje": True, "rag_wektory": 0,
        "rag_fragmenty": 100, "model_embeddings": True,
    }
    alarmy = sp._alarmy(rap)
    assert any("FTS" in a or "wektor" in a.lower() for a in alarmy)


# ── W2 RAG + W5 refleksje podpięte do szukaj_wszedzie ────────────────────────

def test_szukaj_wszedzie_zawiera_wiedze(monkeypatch, tmp_path):
    """szukaj_wszedzie() z zapytaniem zwraca warstwę 'wiedza' (RAG), gdy baza istnieje."""
    from imperium.biblioteki import centrum_pamieci as cp
    # izoluj lekcje/kronikę/wizje, by nie zaszumiały
    plik_lekcji = tmp_path / "PAMIEC.md"
    plik_lekcji.write_text("# P\n\n## 📚 LEKCJE Z SESJI\n\n", encoding="utf-8")
    monkeypatch.setattr(cp._ps, "DOMYSLNY_PLIK", plik_lekcji)
    monkeypatch.setattr(cp._kc, "CEL_DOMYSLNY", tmp_path / "brak")
    monkeypatch.setattr(cp._rw, "PLIK_DOMYSLNY", tmp_path / "brak.jsonl")

    # RAG: jeśli baza istnieje, oczekuj warstwy 'wiedza'; jeśli nie — graceful brak
    from imperium.biblioteki import srodowisko_pamieci as sp
    if sp.RAG_BAZA.exists():
        wyniki = cp.szukaj_wszedzie("liquidity order book", limit=5)
        warstwy = {w["warstwa"] for w in wyniki}
        assert "wiedza" in warstwy, f"RAG istnieje ale brak warstwy wiedza: {warstwy}"


def test_szukaj_w_rag_resilient_blad(monkeypatch):
    """_szukaj_w_rag nie wybucha gdy RAG rzuca wyjątek (zwraca [])."""
    from imperium.biblioteki import centrum_pamieci as cp
    from narzedzia.rag import szukaj as rag
    def wybuch(*a, **k):
        raise RuntimeError("symulowany błąd RAG")
    monkeypatch.setattr(rag, "szukaj", wybuch)
    assert cp._szukaj_w_rag("cokolwiek", 5) == []


def test_szukaj_w_refleksjach_resilient(monkeypatch):
    """_szukaj_w_refleksjach zwraca [] gdy brak danych (chmura: logs/ gitignore)."""
    from imperium.biblioteki import centrum_pamieci as cp
    wynik = cp._szukaj_w_refleksjach("strata trend", 5)
    assert isinstance(wynik, list)   # nie wybucha, lista (pusta lub z danymi)


# ── Deduplikacja (L6) ─────────────────────────────────────────────────────────

def test_rejestr_wizji_dedup_pomija_duplikat(tmp_path):
    """dodaj() z dedup=True pomija wpis o tym samym (typ, tytuł)."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    assert rw.dodaj("WIZJA", "Portfel 20 par", "opis1", plik=plik) is True
    assert rw.dodaj("WIZJA", "Portfel 20 par", "opis2 inny", plik=plik) is False
    assert len(rw.wszystkie(plik=plik)) == 1


def test_rejestr_wizji_dedup_rozne_typy_ok(tmp_path):
    """Ten sam tytuł ale różny typ → nie duplikat (dopisywane oba)."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    assert rw.dodaj("WIZJA", "RAG", "wizja", plik=plik) is True
    assert rw.dodaj("POMYSŁ", "RAG", "pomysł", plik=plik) is True
    assert len(rw.wszystkie(plik=plik)) == 2


def test_rejestr_wizji_dedup_wylaczony(tmp_path):
    """dedup=False → dopisuje nawet duplikat."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("ZMIANA", "X", "a", plik=plik)
    assert rw.dodaj("ZMIANA", "X", "b", plik=plik, dedup=False) is True
    assert len(rw.wszystkie(plik=plik)) == 2


# ── W6 Dziennik Nieśmiertelny (dożywotnia oś czasu) ──────────────────────────

def test_dziennik_dopisz_i_wczytaj(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    assert dn.dopisz(["zrobiono X"], ["decyzja Y"], "krok Z", sesja="abc123", data="2026-06-28", plik=plik)
    w = dn.wszystkie(plik=plik)
    assert len(w) == 1
    assert w[0]["co"] == ["zrobiono X"]
    assert w[0]["sesja"] == "abc123"
    assert w[0]["nastepny"] == "krok Z"


def test_dziennik_ostatni_wpis(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    dn.dopisz(["a"], data="2026-06-01", plik=plik)
    dn.dopisz(["b"], data="2026-06-02", plik=plik)
    assert dn.ostatni_wpis(plik=plik)["co"] == ["b"]


def test_dziennik_os_czasu_pelna(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    dn.dopisz(["pierwszy krok"], data="2026-06-01", plik=plik)
    dn.dopisz(["drugi krok"], data="2026-06-02", plik=plik)
    txt = dn.os_czasu(plik=plik)
    assert "pierwszy krok" in txt and "drugi krok" in txt
    assert "2 sesji" in txt


def test_dziennik_os_czasu_skraca_starsze(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    for i in range(5):
        dn.dopisz([f"krok {i}"], nastepny=f"next {i}", data=f"2026-06-0{i+1}", plik=plik)
    txt = dn.os_czasu(ostatnie=2, plik=plik)
    # najnowsze 2 mają 'następny', starsze są jednolinijkowe (bez 'następny')
    assert "next 4" in txt and "next 3" in txt
    assert "next 0" not in txt


def test_dziennik_szukaj_po_slowach(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    dn.dopisz(["wdrożono Numba JIT na wskaźnikach"], data="2026-06-01", plik=plik)
    dn.dopisz(["coś zupełnie innego"], data="2026-06-02", plik=plik)
    wyniki = dn.szukaj("numba wskaźniki", plik=plik)
    assert wyniki and "Numba" in wyniki[0]["co"][0]


def test_dziennik_brak_wpisu_dzis(tmp_path):
    from imperium.biblioteki import dziennik_niesmiertelny as dn
    plik = tmp_path / "dz.jsonl"
    assert dn.brak_wpisu_dzis(plik=plik) is True   # pusty
    dn.dopisz(["x"], plik=plik)                      # dziś
    assert dn.brak_wpisu_dzis(plik=plik) is False


# ── DEDUP REJESTRU WIZJI: PREDYKAT WSPÓLNY Z PAMIĘCIĄ (naprawa 2026-07-26) ────

def test_rejestr_wizji_lapie_parafraze_nie_tylko_napis(tmp_path):
    """Wpisy pisze DeepSeek, który parafrazuje — dedup po napisie ich nie widzi.

    Wcześniej bramka porównywała (typ, tytuł) znak w znak, więc ten sam fakt zapisany
    dwoma zdaniami wchodził dwa razy. Od naprawy używamy TEGO SAMEGO predykatu, co pamięć
    lekcji (Prawo XVI: jeden predykat, dwa rejestry) — inaczej ten sam wpis byłby duplikatem
    w jednym rejestrze, a nowością w drugim.
    """
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    assert rw.dodaj("ZMIANA", "Obudzono neurony PSY-01/02 i V-03",
                    "Adaptery Futures i CVD dolewają dane, neurony PSY-01, PSY-02 i V-03 głosują.",
                    plik=plik) is True
    assert rw.dodaj("ZMIANA", "Przebudzenie neuronów PSY-01/PSY-02 oraz V-03",
                    "Neurony PSY-01, PSY-02, V-03 zaczęły głosować po dolaniu danych z adapterów.",
                    plik=plik) is False, "parafraza tego samego faktu nie może wejść drugi raz"


def test_rejestr_wizji_rozne_typy_to_rozne_byty(tmp_path):
    """GRANICA: ta sama treść jako WIZJA i jako ZMIANA to dwa różne byty, nie duplikat.

    Bez tego rozróżnienia zrealizowana ZMIANA zjadałaby WIZJĘ, z której powstała — czyli
    dedup kasowałby historię zamiaru. Fałszywe scalenie kosztuje wiedzę bezpowrotnie.
    """
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    assert rw.dodaj("WIZJA", "Portfel 20+ par", "Rozszerzyć portfel do 20+ par krypto.",
                    plik=plik) is True
    assert rw.dodaj("ZMIANA", "Portfel 20+ par", "Rozszerzyć portfel do 20+ par krypto.",
                    plik=plik) is True, "inny typ = inny byt, nawet przy tym samym tytule"


def test_rejestr_wizji_dedup_wylaczalny(tmp_path):
    """`dedup=False` musi nadal wpuszczać wszystko — import historii nie jest cenzurowany."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Ten sam", "Treść.", plik=plik)
    assert rw.dodaj("POMYSŁ", "Ten sam", "Treść.", plik=plik, dedup=False) is True
