"""Testy CONDITOR LUSTRI — bramki zdejmującej ZAMROŻENIE LUSTRATIO (U1).

Ta bramka orzeka o rzeczy nieodwracalnej (powrót do rozwoju), więc jej testy pilnują
przede wszystkim NIEZMIENNIKÓW, nie wyglądu raportu:

  1. **`NIE WIEM` blokuje tak samo jak `NIE`** (klasa K2). Gdyby przestało, najtańszą
     drogą do zielonej bramki byłoby dopisanie kryterium bez miernika — miernik
     zamieniłby się w pochlebcę. To jest jedyny test, którego złamanie wywraca sens organu.
  2. **Zero kryteriów ≠ sukces.** Pusta lista musi dawać czerwień; „nie miałem czego
     sprawdzić" to niewiedza, nie zgoda.
  3. **Awaria producenta = `NIE WIEM`.** Organ, który po wyjątku mówi OK, jest gorszy
     od organu, którego nie ma.
  4. **L4 poza oceną** — inaczej bramka żądałaby własnego domknięcia, żeby się domknąć.

Reguła Test-Granic: każdy próg ma test po OBU stronach.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.pretorianie import conditor_lustri as C  # noqa: E402
from imperium.oczy import maturitas as M  # noqa: E402


def _k(stan, klucz="X"):
    return C.Kryterium(klucz=klucz, pytanie="?", producent="test", stan=stan)


# ── 1. NIEZMIENNIK GŁÓWNY: trzy stany, dwa z nich blokują ───────────────────────

def test_blokuje_trzy_stany():
    assert _k(C.SPELNIONE).blokuje is False
    assert _k(C.NIESPELNIONE).blokuje is True
    assert _k(C.NIE_WIEM).blokuje is True, "NIE WIEM musi blokować — to cała klasa K2"


def test_nie_wiem_blokuje_zdjecie_zamrozenia():
    """GRANICA: komplet spełnionych + JEDNO `NIE WIEM` = zamrożenie TRWA."""
    w = C.Werdykt(kryteria=[_k(C.SPELNIONE, "A"), _k(C.SPELNIONE, "B"), _k(C.NIE_WIEM, "C")])
    assert w.wolno_zdjac is False
    assert w.nieznane == 1 and w.spelnione == 2


def test_same_spelnione_pozwalaja_zdjac():
    """Druga strona granicy — bramka MUSI umieć zaświecić na zielono."""
    w = C.Werdykt(kryteria=[_k(C.SPELNIONE, "A"), _k(C.SPELNIONE, "B")])
    assert w.wolno_zdjac is True


def test_jedno_niespelnione_blokuje():
    w = C.Werdykt(kryteria=[_k(C.SPELNIONE, "A"), _k(C.NIESPELNIONE, "B")])
    assert w.wolno_zdjac is False and w.niespelnione == 1


def test_pusta_lista_nie_jest_sukcesem():
    """`all([])` to True — bez jawnego warunku pusta bramka przepuszczałaby wszystko."""
    assert C.Werdykt(kryteria=[]).wolno_zdjac is False


# ── 2. AWARIA PRODUCENTA NIE MOŻE DAWAĆ ZIELENI ─────────────────────────────────

def test_wyjatek_producenta_daje_nie_wiem():
    def k_pechowy():
        raise RuntimeError("producent padł")

    w = C.zmierz(kryteria=[k_pechowy])
    pechowe = [k for k in w.kryteria if "producent padł" in k.powod]
    assert len(pechowe) == 1
    assert pechowe[0].stan == C.NIE_WIEM
    assert w.wolno_zdjac is False


def test_kryteria_bez_producenta_zawsze_dolaczone():
    """Nawet przy jednym zdrowym kryterium bramka dokłada te, których nie umie zmierzyć."""
    w = C.zmierz(kryteria=[lambda: _k(C.SPELNIONE, "ZDROWE")])
    klucze = {k.klucz for k in w.kryteria}
    for brak in C.BRAK_PRODUCENTA:
        assert brak["klucz"] in klucze
    assert w.wolno_zdjac is False, "brak miernika nie może przepuścić bramki"


def test_kryteria_bez_producenta_niosa_instrukcje():
    """Kryterium bez miernika bez instrukcji byłoby tapetą, a nie zadaniem."""
    for k in C._kryteria_bez_producenta():
        assert k.stan == C.NIE_WIEM
        assert k.co_zrobic.strip(), f"{k.klucz} nie mówi, co zbudować"
        assert k.powod.strip()


# ── 3. ETAPY LUSTRATIO — L4 POZA OCENĄ, brak statusu = NIE WIEM ─────────────────

def _roadmap(monkeypatch, tmp_path, tresc):
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "ROADMAP_IMPERIUM.md").write_text(tresc, encoding="utf-8")
    monkeypatch.setattr(C, "KORZEN", tmp_path)


def test_etapy_l4_nie_wchodzi_do_oceny(monkeypatch, tmp_path):
    """L0 domknięte + L4 otwarte → SPEŁNIONE, bo L4 to właśnie ta bramka."""
    _roadmap(monkeypatch, tmp_path,
             "| # | Etap | Stan |\n|---|---|---|\n"
             "| L0 | LUSTRUM | ✅ |\n"
             "| L4 | Bramka wyjścia | 🔴 |\n")
    k = C.k_etapy()
    assert k.stan == C.SPELNIONE, "L4 nie może blokować samo siebie"


def test_etapy_otwarty_blokuje(monkeypatch, tmp_path):
    _roadmap(monkeypatch, tmp_path,
             "| # | Etap | Stan |\n|---|---|---|\n"
             "| L0 | LUSTRUM | ✅ |\n"
             "| L3c | Strażnik | 🔴 |\n")
    k = C.k_etapy()
    assert k.stan == C.NIESPELNIONE and "L3c" in k.powod


def test_etapy_bez_statusu_to_nie_wiem(monkeypatch, tmp_path):
    """Wiersz z opisem zamiast statusu — dokładnie to, co MATURITAS gubił po cichu."""
    _roadmap(monkeypatch, tmp_path,
             "| # | Etap | Stan |\n|---|---|---|\n"
             "| L0 | LUSTRUM | zrobione w zeszłym tygodniu |\n")
    assert C.k_etapy().stan == C.NIE_WIEM


def test_etapy_zerowy_odczyt_to_nie_wiem(monkeypatch, tmp_path):
    """Zmieniony format tabeli nie może udawać kompletu domknięć."""
    _roadmap(monkeypatch, tmp_path, "# ROADMAP bez tabeli etapów\n")
    assert C.k_etapy().stan == C.NIE_WIEM


def test_etapy_wariant_zlozony_rozpoznany(monkeypatch, tmp_path):
    """Etykiety typu `**L3a2**` (pogrubione, z cyfrą na końcu) też są etapami."""
    _roadmap(monkeypatch, tmp_path,
             "| # | Etap | Stan |\n|---|---|---|\n"
             "| **L3a2** | druga runda | ✅ |\n")
    k = C.k_etapy()
    assert k.stan == C.SPELNIONE and "1 domkniętych" in k.wartosc


# ── 4. JEDEN PARSER NA DWA PYTANIA (K1) ─────────────────────────────────────────

def test_parser_wierszy_pomija_naglowki_i_separatory():
    tekst = ("| # | Etap | Stan |\n|---|---|---|\n"
             "| L1 | coś | ✅ |\n"
             "zwykły akapit\n")
    wiersze = M.wiersze_stanu(tekst)
    assert wiersze == [("L1", "✅")]


def test_stan_domkniety_trzy_odpowiedzi():
    assert M.stan_domkniety("✅ zrobione") is True
    assert M.stan_domkniety("🔴") is False
    assert M.stan_domkniety("🟡 w toku") is False
    assert M.stan_domkniety("⏸️ odłożone") is False
    assert M.stan_domkniety("opis bez statusu") is None, "brak statusu ≠ otwarte ≠ domknięte"


# ── KONTRAKT MIĘDZY ORGANAMI JEST PUBLICZNY (wada z recenzji 2026-08-05) ─────────
# CONDITOR importował z MATURITASA prywatną `_stan_domkniety`. Zmiana nazwy w cudzym module
# dałaby `ImportError`, ten zaś wpada w `except` w `zmierz()` i zamienia kryterium ETAPY
# w ciche `NIE WIEM` — awaria wyglądająca jak niewiedza. Cały organ stoi na tym, że nie
# wolno milczeć; nie może się przewracać przez podkreślnik w cudzej nazwie.

def test_parser_etapow_jest_publicznym_api_maturitasa():
    """Kontrakt nazwany kontraktem: obie funkcje muszą istnieć BEZ podkreślnika."""
    assert callable(getattr(M, "stan_domkniety", None)), \
        "CONDITOR czyta stan etapów tą funkcją — kontrakt musi być publiczny"
    assert callable(getattr(M, "wiersze_stanu", None))


def test_conditor_nie_importuje_prywatnych_nazw():
    """GRANICA: żaden import z podkreślnikiem w tym pliku — inaczej wada wraca pod nową nazwą."""
    import re
    zrodlo = (C.KORZEN / "imperium" / "pretorianie" / "conditor_lustri.py").read_text(encoding="utf-8")
    podejrzane = [w.strip() for w in zrodlo.splitlines()
                  if re.search(r"^\s*(from|import)\s.*\bimport\b.*(^|[\s,])_[a-zA-Z]", w)]
    assert not podejrzane, f"import prywatnej nazwy = zakładnik cudzego refaktoru: {podejrzane}"


def test_kryterium_etapy_dziala_na_zywym_roadmapie():
    """Dowód empiryczny, że kontrakt naprawdę działa — nie tylko że się importuje.

    Gdyby import padł, `zmierz()` zamieniłby to w `NIE WIEM` z „awaria producenta"; ten test
    żąda ODPOWIEDZI producenta (dowolnego z trzech stanów), ale nie awarii.
    """
    k = C.k_etapy()
    assert k.klucz == "ETAPY"
    assert k.wartosc != "awaria producenta"
    assert "domkniętych" in k.wartosc or "brak ROADMAP" in k.wartosc


def test_maturitas_dlug_z_jednego_producenta():
    """K1: MATURITAS ma WOŁAĆ codex_notarum, nie liczyć drugiej arytmetyki."""
    from imperium.biblioteki import codex_notarum

    loop = M.zmierz_loop()
    assert loop["wskazniki"]["dlug_honorowy"] == len(codex_notarum.dlug_honorowy())
    assert loop["wskazniki"]["noty_odroczone"] == len(codex_notarum.odroczone())


# ── 5. RAPORT MÓWI PRAWDĘ O WERDYKCIE ───────────────────────────────────────────

def test_raport_czerwony_nie_oglasza_zgody():
    w = C.Werdykt(kryteria=[_k(C.NIE_WIEM, "A")])
    t = C.raport_tekst(w)
    assert "BRAMKA CZERWONA" in t and "SPEŁNIONE w komplecie" not in t


def test_raport_czerwony_mowi_o_dlugu_nie_o_zniesionym_zakazie():
    """Do 2026-08-05 raport pisał „⛔ ZAMROŻENIE TRWA". Cezar zdjął zamrożenie DECYZJĄ tego
    dnia, więc zdanie stało się nieprawdą o świecie — a miernik raportujący nieistniejący
    zakaz uczy czytelnika ignorować własne komunikaty. Zmienił się WYŁĄCZNIE opis stanu."""
    t = C.raport_tekst(C.Werdykt(kryteria=[_k(C.NIESPELNIONE, "A")]))
    assert "ZAMROŻENIE TRWA" not in t, "organ nie może ogłaszać zakazu, którego już nie ma"
    assert "DŁUG NIE ZNIKNĄŁ" in t, "…ale nie wolno mu też przemilczeć, że kryteria nie są spełnione"


def test_raport_zielony_oddaje_decyzje_cezarowi():
    w = C.Werdykt(kryteria=[_k(C.SPELNIONE, "A")])
    t = C.raport_tekst(w)
    assert "KRYTERIA SPEŁNIONE" in t
    assert "nie orzeka decyzji" in t, "organ mierzy stan, decyzja należy do Cezara"
