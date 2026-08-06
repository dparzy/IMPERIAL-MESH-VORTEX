"""Testy MATURITAS — organu mierzącego piętro inżynierii (prompt / loop / graph).

Organ powstał z rozkazu Cezara „pilnujmy i weryfikujmy stany prompt/loop/graph" i jest
pierwszą ŻYWĄ kategorią projektu INGENIUM. Testy pilnują jego zasad nienaruszalnych —
bo miernik bez nich zamienia się w laurkę.
"""
from unittest import mock
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
    """Uśrednienie pięter ukryłoby to, co najważniejsze — można mieć HARNESS 4/4
    przy GRAPH, którego nikt nie czyta. Organ świadomie NIE liczy jednej liczby."""
    w = m.zmierz()
    assert "ocena" not in w and "iq" not in w and "wynik" not in w
    assert len(w["poziomy"]) == 5


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

def test_pomiar_na_zywym_repo_daje_wszystkie_pietra():
    """Od 2026-08-06 pięter jest PIĘĆ — HARNESS i NEURO-SYM stały zbudowane i nieliczone
    (ROADMAP, CORONA D: „prawdopodobnie ZANIŻAMY własny stan")."""
    w = m.zmierz()
    assert [p["pietro"] for p in w["pietra"]] == [
        "PROMPT", "LOOP", "GRAPH", "HARNESS", "NEURO-SYM"]
    for p in w["pietra"]:
        assert 0 <= p["poziom"] <= 4
        assert p["wskazniki"], f"{p['pietro']} bez ani jednego wskaźnika"


def test_wask_gardlo_nazywa_przyczyne_a_nie_tylko_fakt():
    """Alarm bez przyczyny jest tapetą — Cezar ma wiedzieć, CO naprawić."""
    for p in m.zmierz()["pietra"]:
        if p["wask"]:
            assert len(p["wask"]) > 30, f"{p['pietro']}: wąskie gardło bez wyjaśnienia"


# ── PIĘTRA HARNESS i NEURO-SYM (dopisane 2026-08-06, rozkaz Cezara) ─────────────
# ROADMAP przy CORONIE D notował od 2026-08-03: MATURITAS mierzy 3 z 9, a HARNESS
# i NEURO-SYMBOLIC "JUŻ STOJĄ i nie są liczone" — czyli ZANIŻAMY własny stan.
# Testy pilnują, żeby naprawa nie zamieniła zaniżania w zawyżanie.

def test_mierzymy_piec_pieter_i_mowimy_ile_nie_mierzymy():
    """Miernik przemilczający własny zasięg sugeruje kompletność, której nie ma."""
    w = m.zmierz()
    assert w["mierzone_pieter"] == len(w["pietra"]) == 5
    assert w["znane_pieter"] == 6, (
        "zasięg liczy się od TAKSONOMII POTWIERDZONEJ (5 warstw + NEURO-SYM), "
        "nie od liczby 9 z materiału obalonego zwiadem 2026-08-06")
    assert w["niemierzone"], "CONTEXT ma zostać JAWNIE niemierzony"
    assert w["kandydaci"], "kandydaci spoza taksonomii mają być widoczni, nie przemilczani"
    assert "OBALONA" in w["taksonomia"], "źródło taksonomii ma nieść ślad korekty"
    assert w["mierzone_pieter"] + len(w["niemierzone"]) == w["znane_pieter"]


def test_kazde_pietro_ma_komplet_pol():
    """Nowe piętra muszą spełniać ten sam kontrakt co stare — inaczej raport się rozjedzie."""
    for p in m.zmierz()["pietra"]:
        for pole in ("pietro", "poziom", "nazwa", "wskazniki", "wask",
                     "antywskaznik", "organy", "luka_w_planie"):
            assert pole in p, f"{p.get('pietro')}: brak pola {pole}"
        assert 0 <= p["poziom"] <= 4
        assert p["antywskaznik"], f"{p['pietro']}: antywskaznik obowiązkowy (zasada INGENIUM)"


def test_zaden_organ_w_mapie_nie_jest_widmem():
    """GRANICA: mapa organów wpisana ręcznie gnije jak każda proza. Ścieżka, której nie ma
    na dysku, to API-widmo (klasa Warstwy 16) — w organie mierzącym dojrzałość szczególnie."""
    for pietro in m.ORGANY_PIETRA:
        widma = m.organy_pietra(pietro)["widma"]
        assert widma == [], f"{pietro}: organy-widma w mapie: {widma}"


def test_organy_pietra_wykrywa_widmo():
    """MUTACJA: strażnik, którego nie widziano na czerwono, nie jest zmierzony."""
    with mock.patch.dict(m.ORGANY_PIETRA, {"PROMPT": ["CLAUDE.md", "nie/ma/takiego.py"]}):
        wynik = m.organy_pietra("PROMPT")
        assert wynik["widma"] == ["nie/ma/takiego.py"]
        assert "CLAUDE.md" in wynik["zywe"]


def test_harness_rozroznia_zapobieganie_od_raportowania():
    """Sedno piętra HARNESS: hook, który tylko raportuje, NIE daje poziomu 3.
    Zmierzony powód: VINDEX wykrywał zabrudzenie po fakcie, a mimo to biegi ginęły —
    dopiero SILENTIUM (PreToolUse) odmawia zapisu ZANIM szkoda powstanie."""
    h = m.zmierz_harness()
    assert h["pietro"] == "HARNESS"
    w = h["wskazniki"]
    if h["poziom"] >= 3:
        assert w["zapobiegawcze_PreToolUse"] > 0, "poziom 3 bez hooka zapobiegawczego"
    if h["poziom"] >= 4:
        assert w["workflow_wolajace_bramke"] != "BRAK", (
            "poziom 4 wymaga egzekutora POZA maszyną Architekta (VALLUM)")


def test_harness_nie_liczy_workflow_ktory_nie_wola_bramki():
    """GRANICA + warunek nienaruszalny Cezara: CI, które nigdy nie czerwienieje, jest tapetą.
    Sama obecność pliku .yml nie ma prawa dać poziomu 4."""
    h = m.zmierz_harness()
    wolajace = h["wskazniki"]["workflow_wolajace_bramke"]
    if wolajace != "BRAK":
        for nazwa in wolajace:
            tresc = (m.KORZEN / ".github" / "workflows" / nazwa).read_text(
                encoding="utf-8", errors="replace")
            assert "run_tests.py" in tresc, f"{nazwa} policzone, choć nie woła bramki"


def test_neuro_sym_wymaga_kodu_wyjscia_a_nie_samego_wydruku():
    """Weryfikacja, która RAPORTUJE, ale nie zatrzymuje, to cisza udająca zgodę."""
    n = m.zmierz_neuro_symbolic()
    assert n["pietro"] == "NEURO-SYM"
    if n["poziom"] >= 3:
        assert n["wskazniki"]["bramka_ma_kod_wyjscia"] is True
    if n["poziom"] >= 4:
        assert n["wskazniki"]["weryfikacja_przed_zapisem"] > 0


def test_luka_w_planie_odrzuca_slowa_tlo():
    """GRANICA PROGU (Prawo XXI) — i regresja wady złapanej w godzinę po napisaniu:
    pierwsza wersja liczyła KAŻDE słowo >5 znaków, więc 'decyzji' i 'roadmap' dawały
    fałszywe „mamy to w planie". Słowo-tło nie ma prawa być dowodem."""
    tresc = (m.KORZEN / "docs" / "ROADMAP_IMPERIUM.md").read_text(
        encoding="utf-8", errors="replace").lower()
    # Zdanie zbudowane WYŁĄCZNIE ze słów-tła musi dać werdykt negatywny.
    samo_tlo = "decyzji roadmap kontekstu czytany"
    for slowo in samo_tlo.split():
        assert tresc.count(slowo) >= m.PROG_RZADKOSCI, (
            f"'{slowo}' przestało być tłem ({tresc.count(slowo)}x) — dobierz inne do testu")
    assert m.luka_w_planie(samo_tlo).startswith("🔴")


def test_luka_w_planie_milczy_bez_waskiego_gardla():
    """Piętro bez wąskiego gardła nie ma czego dopełniać — pusty werdykt, nie fałszywy alarm."""
    assert m.luka_w_planie("") == ""


def test_warstwy_audytu_jedno_zrodlo_dla_trzech_pieter():
    """LOOP, HARNESS i NEURO-SYM pytają o tę samą liczbę — trzy parsery rozjechałyby się."""
    ile = m._warstwy_audytu()
    assert ile >= 10, f"audyt ma {ile} warstw — poniżej progu realnego zasięgu"
    assert m.zmierz_loop()["wskazniki"]["warstwy_audytu"] == ile
    assert m.zmierz_harness()["wskazniki"]["warstwy_audytu"] == ile
    assert m.zmierz_neuro_symbolic()["wskazniki"]["warstwy_regul"] == ile


def test_raport_pokazuje_organy_i_zasieg():
    """Rozkaz Cezara: wydruk ma odpowiadać, JAKIE organy i CZEGO NIE mierzymy."""
    tekst = m.raport()
    assert "mierzone 5 z 6" in tekst
    assert "organy" in tekst
    assert "NIEMIERZONE" in tekst
    assert "Goodhart" in tekst, "nota o Goodharcie nie może zniknąć z wydruku"


def test_delta_przezywa_rozszerzenie_miernika(tmp_path):
    """REGRESJA 2026-08-07: `--delta` wywalił się `KeyError: 'HARNESS'` w tej samej minucie,
    w której dopisałem dwa piętra — bo wydruk czytał `poprzednie[p]` wprost, a migawka
    sprzed rozszerzenia ich nie zna.

    Klasa: miernik traktujący ROZSZERZENIE WŁASNEGO ZASIĘGU jak błąd danych. Piętro bez
    historii to `NIEZNANE` (nowy pomiar), nie awaria i nie „wzrost o 4"."""
    import json
    plik = tmp_path / "migawki.jsonl"
    plik.write_text(json.dumps({"data": "2026-08-06",
                                "poziomy": {"PROMPT": 3, "LOOP": 3, "GRAPH": 3}}) + "\n",
                    encoding="utf-8")
    d = m.delta(sciezka=plik)
    assert d["stan"] == "zmiana"
    # Rdzeń NIE MOŻE rzucić — brak piętra w historii jest legalny.
    assert "HARNESS" in d["zmiany_poziomow"]
    assert "HARNESS" not in d["poprzednie"]
    # I to jest kontrakt wydruku: sięgamy przez .get, nie przez [] — inaczej KeyError wraca.
    assert d["poprzednie"].get("HARNESS", m.NIEZNANE) == m.NIEZNANE
