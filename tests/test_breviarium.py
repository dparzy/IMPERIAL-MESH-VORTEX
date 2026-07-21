"""
Testy BREVIARIUM — Zwięzłego Spisu Sług Imperium (meldunek otwarcia wachty).

Weryfikuje:
  • liczby GENEROWANE z żywego stanu (nigdy przechowywane — jak SIGILLARIUM/CENSUS),
  • wykrycie martwego potencjału: organ istnieje, ale nikt go nie woła (DISPENSATOR),
  • uczciwość wobec niewiedzy: model Architekta NIE jest zmyślany, tylko żądany (Prawo I),
  • granice: brak plików, uszkodzona linia JSONL, brak katalogu TIRO, pusty ledger.
"""

import json

from imperium.oczy import breviarium as bv


def _jsonl(sciezka, rekordy):
    sciezka.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rekordy) + "\n",
                       encoding="utf-8")


# ── Odporność na brak i na śmieci ───────────────────────────────────────────────

def test_brak_plikow_nie_wywala_meldunku(monkeypatch, tmp_path):
    """Świeży klon repo nie ma kolejki ani par — meldunek ma działać, nie krzyczeć wyjątkiem."""
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", tmp_path / "nie_ma.jsonl")
    monkeypatch.setattr(bv, "PARY_TIRO", tmp_path / "tez_nie.jsonl")
    monkeypatch.setattr(bv, "KATALOG_TIRO", tmp_path / "brak_tiro")
    assert bv.stan_hyginusa()["czastek"] == 0
    assert bv.stan_tiro() == {"pary_nauczyciela": 0, "modele": [], "silnik": False,
                              "klasa_sprzetu": bv.stan_tiro()["klasa_sprzetu"],
                              "zakres_modelu": bv.stan_tiro()["zakres_modelu"]}
    assert "BREVIARIUM" in bv.banner()


def test_uszkodzona_linia_jsonl_pomijana_nie_zabija(monkeypatch, tmp_path):
    """Jedna zepsuta linia nie może wyzerować całego meldunku (ani go wywalić)."""
    p = tmp_path / "kolejka.jsonl"
    p.write_text('{"status": "ok"}\n{ to nie jest json\n{"status": "ok"}\n', encoding="utf-8")
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    assert bv.stan_hyginusa()["czeka_na_sedziego"] == 2


def test_puste_linie_ignorowane(monkeypatch, tmp_path):
    p = tmp_path / "k.jsonl"
    p.write_text('\n\n{"status": "ok"}\n\n', encoding="utf-8")
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    assert bv.stan_hyginusa()["czastek"] == 1


# ── Rdzeń: co meldunek ma pokazać ───────────────────────────────────────────────

def test_liczy_plon_czekajacy_na_sedziego(monkeypatch, tmp_path):
    """DŁUG PRZEGLĄDU: cząstki 'ok' to plon, za który zapłacono i którego nikt nie ocenił."""
    p = tmp_path / "k.jsonl"
    _jsonl(p, [{"status": "ok"}, {"status": "ok"}, {"status": "dry"}, {"status": "pusto"}])
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    s = bv.stan_hyginusa()
    assert s["czastek"] == 4 and s["czeka_na_sedziego"] == 2


def test_liczy_werdykty_probatora(monkeypatch, tmp_path):
    """Podejrzane cząstki muszą być widoczne na otwarciu, nie dopiero po ręcznym grepie."""
    p = tmp_path / "k.jsonl"
    _jsonl(p, [
        {"status": "ok", "probator": {"czysty": True}},
        {"status": "ok", "probator": {"czysty": False}},
        {"status": "ok"},                                   # sprzed wpięcia PROBATORA
    ])
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    s = bv.stan_hyginusa()
    assert s["zbadane_probatorem"] == 2 and s["podejrzane"] == 1


def test_stary_rekord_bez_probatora_nie_liczy_sie_jako_podejrzany(monkeypatch, tmp_path):
    """Granica: brak pola ≠ wina. Inaczej cała historia kolejki stałaby się 'podejrzana'."""
    p = tmp_path / "k.jsonl"
    _jsonl(p, [{"status": "ok"} for _ in range(5)])
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    assert bv.stan_hyginusa()["podejrzane"] == 0


def test_ostatni_zwiad_bierze_najnowszy_znacznik(monkeypatch, tmp_path):
    p = tmp_path / "k.jsonl"
    _jsonl(p, [{"status": "ok", "ts": 1000}, {"status": "ok", "ts": 900_000_000}])
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    assert bv.stan_hyginusa()["ostatni_zwiad"] != "—"


def test_znacznik_nieliczbowy_nie_wywala(monkeypatch, tmp_path):
    """Granica: śmieć w polu ts → '—', nie TypeError na max()."""
    p = tmp_path / "k.jsonl"
    _jsonl(p, [{"status": "ok", "ts": "wczoraj"}])
    monkeypatch.setattr(bv, "KOLEJKA_HIPOTEZ", p)
    assert bv.stan_hyginusa()["ostatni_zwiad"] == "—"


def test_wykrywa_martwy_potencjal_dispensatora(monkeypatch, tmp_path):
    """Organ w repo, ale NIEWOŁANY, to martwy potencjał (Prawo XV) — meldunek musi to widzieć.
    Dokładnie przypadek DISPENSATORA, który przeżył całą erę niezameldowany."""
    (tmp_path / "narzedzia").mkdir()
    (tmp_path / "narzedzia" / "bibliotekarz.py").write_text(
        "# Hyginus, który nikogo nie pyta o model\n", encoding="utf-8")
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is False


def test_wykrywa_dispensator_wpiety(monkeypatch, tmp_path):
    """Kontrola POZYTYWNA: detektor musi umieć powiedzieć też „tak".
    Sam test negatywny dałby zielone światło detektorowi, który zawsze mówi „nie"."""
    (tmp_path / "narzedzia").mkdir()
    (tmp_path / "narzedzia" / "bibliotekarz.py").write_text(
        "from imperium.cesarz import dispensator\n", encoding="utf-8")
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is True


def test_brak_bibliotekarza_to_nie_wpiecie(monkeypatch, tmp_path):
    """Granica: nie ma pliku → False, nie wyjątek i nie fałszywe „wpięty"."""
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is False


def test_tiro_widzi_modele_gguf(monkeypatch, tmp_path):
    dom = tmp_path / "TIRO"
    (dom / "modele").mkdir(parents=True)
    (dom / "silnik").mkdir()
    (dom / "modele" / "Qwen3-1.7B-Q4_K_M.gguf").write_text("x", encoding="utf-8")
    (dom / "modele" / "notatka.txt").write_text("x", encoding="utf-8")
    monkeypatch.setattr(bv, "KATALOG_TIRO", dom)
    s = bv.stan_tiro()
    assert s["modele"] == ["Qwen3-1.7B-Q4_K_M.gguf"]         # tylko .gguf, nie śmieci
    assert s["silnik"] is True


def test_brak_silnika_tiro_jest_alarmem(monkeypatch, tmp_path):
    dom = tmp_path / "TIRO"
    (dom / "modele").mkdir(parents=True)
    monkeypatch.setattr(bv, "KATALOG_TIRO", dom)
    assert bv.stan_tiro()["silnik"] is False
    assert "brak silnika" in bv.banner()


# ── Uczciwość wobec niewiedzy (Prawo I) ─────────────────────────────────────────

def test_model_architekta_nie_jest_zmyslany(monkeypatch):
    """Środowisko NIE niesie identyfikatora modelu. Meldunek ma tego ŻĄDAĆ, nie zgadywać —
    prawdopodobna nazwa udająca pomiar zestarzeje się jak każda ręczna liczba."""
    monkeypatch.delenv("CLAUDE_EFFORT", raising=False)
    tekst = bv.banner()
    assert "niemierzalny" in tekst and "deklaruje" in tekst


def test_podany_model_architekta_jest_drukowany():
    """Gdy wołający WIE (Architekt deklaruje sam) — meldunek pokazuje fakt, nie żądanie."""
    tekst = bv.banner("claude-opus-4-8, effort high")
    assert "claude-opus-4-8" in tekst and "niemierzalny" not in tekst


def test_banner_jest_zwiezly():
    """Meldunek dzieli hook z 10 innymi organami — nie może go zdominować."""
    assert len(bv.banner().splitlines()) <= 10
