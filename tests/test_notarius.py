"""Testy NOTARIUSA (pisarz par nauczyciel→odpowiedź, surowiec TIRO) — z granicami.

Reguła Test-Granic (Prawo XXI): pisarz ma progi (LIMIT_ZNAKOW), stany (włączony/wyłączony)
i decyzje na pustce (None/""), więc każdą granicę sprawdzamy osobno. Najważniejsza granica
to ŻELAZNA ZASADA: awaria pisarza NIE MOŻE wywrócić wywołania nauczyciela.
"""

import sys
import os
import json
import functools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.notarius import (  # noqa: E402
    LIMIT_ZNAKOW,
    LIMIT_PROBEK_NA_PYTANIE,
    ENV_WYLACZNIK,
    PROGI_DATASETU,
    RODZAJ_KLASYFIKACJI,
    RODZAJ_PROZA,
    czytaj_pary,
    eksportuj_sft,
    odcisk,
    odcisk_pytania,
    policz_sft,
    postep_zbioru,
    raport,
    rodzaj_pary,
    statystyki,
    wlaczony,
    zapisz_pare,
)


def _bez_wylacznika(fn):
    """
    Uruchom z pisarzem WŁĄCZONYM, przywróć env po teście (izolacja od środowiska Cezara —
    gdyby miał ustawione TIRO_NOTARIUS=0, testy nie mogą przez to kłamać).

    `functools.wraps` jest tu OBOWIĄZKOWE, nie kosmetyczne: ustawia `__wrapped__`, za którym
    pytest podąża przy odczycie sygnatury — bez tego fixture `tmp_path` nie zostanie wstrzyknięty
    (goły `*a, **kw` zasłania parametry).
    """
    @functools.wraps(fn)
    def opakowane(*a, **kw):
        stare = os.environ.get(ENV_WYLACZNIK)
        os.environ.pop(ENV_WYLACZNIK, None)
        try:
            return fn(*a, **kw)
        finally:
            if stare is None:
                os.environ.pop(ENV_WYLACZNIK, None)
            else:
                os.environ[ENV_WYLACZNIK] = stare
    return opakowane


# ── zapis podstawowy ──────────────────────────────────────────────────────────

@_bez_wylacznika
def test_zapisuje_pare(tmp_path):
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("sys", "pytanie", "odpowiedź", "deepseek-v4-flash",
                       temperatura=0.7, zrodlo="test", sciezka=p) is True
    pary = list(czytaj_pary(p))
    assert len(pary) == 1
    assert pary[0]["prompt"] == "pytanie"
    assert pary[0]["odpowiedz"] == "odpowiedź"
    assert pary[0]["model"] == "deepseek-v4-flash"
    assert pary[0]["zrodlo"] == "test"
    assert "przyciety" not in pary[0]


@_bez_wylacznika
def test_tworzy_katalog_gdy_brak(tmp_path):
    p = tmp_path / "gleboko" / "jeszcze" / "pary.jsonl"
    assert zapisz_pare("s", "p", "o", "m", sciezka=p) is True
    assert p.exists()


@_bez_wylacznika
def test_zrodlo_wykrywane_automatycznie(tmp_path):
    """
    Wołający NIE przekazuje `zrodlo` — pisarz sam rozpoznaje, kto pyta (po stosie wywołań).
    To ono etykietuje dane treningowe (newsy vs zwiad vs lekcje) przy ważeniu zbioru w E4,
    więc musi działać bez współpracy wołającego.
    """
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is True
    assert list(czytaj_pary(p))[0]["zrodlo"] == "test_notarius"   # nazwa TEGO pliku


# ── GRANICA: pustka (None / "" / same spacje) ─────────────────────────────────

@_bez_wylacznika
def test_pusta_tresc_nie_zapisana(tmp_path):
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("sys", "", "odpowiedź", "m", sciezka=p) is False
    assert zapisz_pare("sys", "   ", "odpowiedź", "m", sciezka=p) is False
    assert list(czytaj_pary(p)) == []


@_bez_wylacznika
def test_pusta_odpowiedz_nie_zapisana(tmp_path):
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("sys", "pytanie", "", "m", sciezka=p) is False
    assert zapisz_pare("sys", "pytanie", "  \n ", "m", sciezka=p) is False
    assert list(czytaj_pary(p)) == []


@_bez_wylacznika
def test_none_nie_wywraca_pisarza(tmp_path):
    """None zamiast tekstu = brak przykładu, ale NIGDY wyjątek (żelazna zasada)."""
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("sys", None, "odp", "m", sciezka=p) is False        # type: ignore[arg-type]
    assert zapisz_pare("sys", "pyt", None, "m", sciezka=p) is False        # type: ignore[arg-type]
    assert list(czytaj_pary(p)) == []


@_bez_wylacznika
def test_pusty_system_prompt_jest_ok(tmp_path):
    """Pusty system prompt to legalny przypadek — liczy się pytanie i odpowiedź."""
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("", "pytanie", "odpowiedź", "m", sciezka=p) is True
    assert zapisz_pare(None, "pytanie2", "odpowiedź2", "m", sciezka=p) is True  # type: ignore[arg-type]
    assert len(list(czytaj_pary(p))) == 2


# ── GRANICA: dedup ────────────────────────────────────────────────────────────

@_bez_wylacznika
def test_identyczna_para_nie_dublowana(tmp_path):
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is True
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is False   # ten sam re-run
    assert len(list(czytaj_pary(p))) == 1


@_bez_wylacznika
def test_ten_sam_prompt_inna_odpowiedz_zapisany_do_limitu(tmp_path):
    """
    Kilka próbek tego samego wejścia MA wartość — pozwalają policzyć konsensus przy eksporcie
    (self-consistency). Dlatego do LIMIT_PROBEK_NA_PYTANIE wpuszczamy różne odpowiedzi.
    Powyżej limitu to już monokultura — patrz test granicy niżej.
    """
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("s", "pyt", "odpowiedź A", "m", sciezka=p) is True
    assert zapisz_pare("s", "pyt", "odpowiedź B", "m", sciezka=p) is True
    assert len(list(czytaj_pary(p))) == 2


# ── GRANICA: limit próbek na pytanie (anty-monokultura) ───────────────────────

@_bez_wylacznika
def test_limit_probek_na_pytanie_dokladnie_na_progu(tmp_path):
    """
    GRANICA `>=`: dokładnie LIMIT próbek wchodzi, LIMIT+1 już NIE.
    Dowód z realnych danych (2026-07-16): pętla live pytała o ten sam zestaw nagłówków 10×
    i dostała 10 SPRZECZNYCH odpowiedzi (sentyment +0.8 … -0.4). Dedup po całej parze tego
    nie łapał, bo odpowiedzi się różniły — model uczyłby się sprzecznych etykiet.
    """
    p = tmp_path / "pary.jsonl"
    for i in range(LIMIT_PROBEK_NA_PYTANIE):
        assert zapisz_pare("s", "te same nagłówki", f"odpowiedź {i}", "m", sciezka=p) is True
    # LIMIT+1 — inna odpowiedź, więc dedup pary NIE zadziała; ratuje wyłącznie limit.
    assert zapisz_pare("s", "te same nagłówki", "odpowiedź NADMIAROWA", "m", sciezka=p) is False
    assert len(list(czytaj_pary(p))) == LIMIT_PROBEK_NA_PYTANIE


@_bez_wylacznika
def test_limit_nie_dotyka_roznych_pytan(tmp_path):
    """Limit jest PER PYTANIE — różne wejścia nie mogą się nawzajem blokować."""
    p = tmp_path / "pary.jsonl"
    for i in range(LIMIT_PROBEK_NA_PYTANIE + 5):
        assert zapisz_pare("s", f"pytanie {i}", "odp", "m", sciezka=p) is True
    assert len(list(czytaj_pary(p))) == LIMIT_PROBEK_NA_PYTANIE + 5


@_bez_wylacznika
def test_limit_liczy_stare_wpisy_bez_odcisku_pytania(tmp_path):
    """
    Wsteczna zgodność: wpisy sprzed limitu nie mają pola `odcisk_pytania`. Limit MUSI je
    policzyć (odtwarzając odcisk z treści) — inaczej stary zalew ominąłby bezpiecznik.
    """
    p = tmp_path / "pary.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for i in range(LIMIT_PROBEK_NA_PYTANIE):
            f.write(json.dumps({"odcisk": f"stary{i}", "system": "s", "prompt": "te same nagłówki",
                                "odpowiedz": f"stara {i}"}, ensure_ascii=False) + "\n")
    assert zapisz_pare("s", "te same nagłówki", "nowa odpowiedź", "m", sciezka=p) is False


@_bez_wylacznika
def test_odcisk_pytania_zapisany_do_grupowania(tmp_path):
    """Eksport (E4) grupuje próbki po pytaniu — pole musi być w danych, nie liczone od nowa."""
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt", "odp A", "m", sciezka=p)
    zapisz_pare("s", "pyt", "odp B", "m", sciezka=p)
    pary = list(czytaj_pary(p))
    assert pary[0]["odcisk_pytania"] == pary[1]["odcisk_pytania"]   # to samo pytanie
    assert pary[0]["odcisk"] != pary[1]["odcisk"]                    # inne pary


def test_odcisk_pytania_ignoruje_odpowiedz():
    assert odcisk_pytania("s", "p") == odcisk_pytania("s", "p")
    assert odcisk_pytania("s", "p") != odcisk_pytania("s", "p2")
    assert odcisk_pytania("s", "p") != odcisk_pytania("s2", "p")


@_bez_wylacznika
def test_inny_system_prompt_to_inna_para(tmp_path):
    p = tmp_path / "pary.jsonl"
    assert zapisz_pare("sysA", "pyt", "odp", "m", sciezka=p) is True
    assert zapisz_pare("sysB", "pyt", "odp", "m", sciezka=p) is True
    assert len(list(czytaj_pary(p))) == 2


def test_odcisk_stabilny_i_rozroznia():
    assert odcisk("s", "p", "o") == odcisk("s", "p", "o")       # deterministyczny
    assert odcisk("s", "p", "o") != odcisk("s", "p", "o2")      # odpowiedź się liczy
    assert odcisk("s", "p", "o") != odcisk("s2", "p", "o")      # system się liczy
    # Granica: rozdzielacz \x00 broni przed sklejeniem pól ("ab"+"c" ≠ "a"+"bc").
    assert odcisk("a", "b", "c") != odcisk("ab", "", "c")


# ── GRANICA: dokładnie próg LIMIT_ZNAKOW (== vs +1) ───────────────────────────

@_bez_wylacznika
def test_dokladnie_limit_nie_przycina(tmp_path):
    p = tmp_path / "pary.jsonl"
    tekst = "x" * LIMIT_ZNAKOW
    assert zapisz_pare("s", tekst, "odp", "m", sciezka=p) is True
    wpis = list(czytaj_pary(p))[0]
    assert len(wpis["prompt"]) == LIMIT_ZNAKOW
    assert "przyciety" not in wpis          # == próg → jeszcze NIE przycięty


@_bez_wylacznika
def test_limit_plus_jeden_przycina_i_oznacza(tmp_path):
    p = tmp_path / "pary.jsonl"
    tekst = "x" * (LIMIT_ZNAKOW + 1)
    assert zapisz_pare("s", tekst, "odp", "m", sciezka=p) is True
    wpis = list(czytaj_pary(p))[0]
    assert len(wpis["prompt"]) == LIMIT_ZNAKOW
    assert wpis["przyciety"] is True                    # Prawo I: przycięcie jest jawne
    assert wpis["znakow_prompt"] == LIMIT_ZNAKOW + 1    # ale prawdziwa długość zapisana


# ── GRANICA: wyłącznik ────────────────────────────────────────────────────────

def test_wylacznik_zatrzymuje_zapis(tmp_path):
    p = tmp_path / "pary.jsonl"
    stare = os.environ.get(ENV_WYLACZNIK)
    try:
        for wartosc in ("0", "false", "nie", "off", "FALSE", "Off"):
            os.environ[ENV_WYLACZNIK] = wartosc
            assert wlaczony() is False, f"'{wartosc}' powinno wyłączać"
            assert zapisz_pare("s", "p", "o", "m", sciezka=p) is False
        assert list(czytaj_pary(p)) == []
    finally:
        if stare is None:
            os.environ.pop(ENV_WYLACZNIK, None)
        else:
            os.environ[ENV_WYLACZNIK] = stare


def test_domyslnie_wlaczony():
    """Zbieranie działa bez konfiguracji — inaczej zbiór nigdy by nie urósł."""
    stare = os.environ.get(ENV_WYLACZNIK)
    os.environ.pop(ENV_WYLACZNIK, None)
    try:
        assert wlaczony() is True
    finally:
        if stare is not None:
            os.environ[ENV_WYLACZNIK] = stare


# ── GRANICA: odporność na uszkodzony plik ─────────────────────────────────────

@_bez_wylacznika
def test_zepsuta_linia_nie_blokuje_reszty(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt1", "odp1", "m", sciezka=p)
    with p.open("a", encoding="utf-8") as f:
        f.write("{to nie jest json\n")
        f.write("\n")
        f.write(json.dumps("nie-slownik") + "\n")   # poprawny JSON, ale nie dict
    zapisz_pare("s", "pyt2", "odp2", "m", sciezka=p)
    pary = list(czytaj_pary(p))
    assert len(pary) == 2                            # zepsute pominięte, dobre czytane
    assert {x["prompt"] for x in pary} == {"pyt1", "pyt2"}


@_bez_wylacznika
def test_zapis_do_niemozliwej_sciezki_nie_rzuca(tmp_path):
    """ŻELAZNA ZASADA: gdy dysk odmawia, pisarz zwraca False — nigdy nie rzuca."""
    kolizja = tmp_path / "plik"
    kolizja.write_text("jestem plikiem, nie katalogiem", encoding="utf-8")
    p = kolizja / "pary.jsonl"          # katalog-który-jest-plikiem → OSError w środku
    assert zapisz_pare("s", "p", "o", "m", sciezka=p) is False


def test_czytaj_z_nieistniejacego_pliku_zwraca_pusto(tmp_path):
    assert list(czytaj_pary(tmp_path / "nie-ma-mnie.jsonl")) == []


# ── statystyki / eksport / raport ─────────────────────────────────────────────

@_bez_wylacznika
def test_statystyki_licza_zrodla_i_modele(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "p1", "odp", "flash", zrodlo="news_llm", sciezka=p)
    zapisz_pare("s", "p2", "odp", "flash", zrodlo="news_llm", sciezka=p)
    zapisz_pare("s", "p3", "odp", "pro", zrodlo="bibliotekarz", sciezka=p)
    s = statystyki(p)
    assert s["par"] == 3
    assert s["zrodla"] == {"news_llm": 2, "bibliotekarz": 1}
    assert s["modele"] == {"flash": 2, "pro": 1}
    assert s["pierwszy"] is not None and s["ostatni"] is not None


def test_statystyki_pustego_zbioru(tmp_path):
    s = statystyki(tmp_path / "brak.jsonl")
    assert s["par"] == 0
    assert s["zrodla"] == {} and s["znakow_odpowiedzi"] == 0
    assert s["pierwszy"] is None and s["ostatni"] is None


@_bez_wylacznika
def test_eksport_sft_format_i_filtr(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("jesteś analitykiem", "co z BTC?", "x" * 100, "m", sciezka=p)
    zapisz_pare("jesteś analitykiem", "a ETH?", "krótko", "m", sciezka=p)   # 6 znaków
    cel = tmp_path / "sft.jsonl"

    assert eksportuj_sft(cel, sciezka=p, min_znakow_odpowiedzi=50) == 1     # krótka odcięta
    wiersz = json.loads(cel.read_text(encoding="utf-8").strip())
    assert [m["role"] for m in wiersz["messages"]] == ["system", "user", "assistant"]
    assert wiersz["messages"][1]["content"] == "co z BTC?"

    assert eksportuj_sft(cel, sciezka=p, min_znakow_odpowiedzi=0) == 2      # bez filtra: obie


@_bez_wylacznika
def test_eksport_pomija_przyciete_odpowiedzi(tmp_path):
    """
    🚨 Przycięta odpowiedź urywa się w pół słowa — podana jako wzorzec uczy ucznia urywania.
    Domyślnie MUSI wypaść z eksportu (recenzja 2026-07-16).
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "krótkie pytanie", "x" * (LIMIT_ZNAKOW + 1), "m", sciezka=p)   # przycięta
    zapisz_pare("s", "drugie pytanie", "y" * 100, "m", sciezka=p)                   # zdrowa
    cel = tmp_path / "sft.jsonl"

    assert eksportuj_sft(cel, sciezka=p) == 1                      # domyślnie: tylko zdrowa
    wiersz = json.loads(cel.read_text(encoding="utf-8").strip())
    assert wiersz["messages"][-1]["content"].startswith("y")

    # Świadome wyłączenie filtra (inspekcja) — obie wracają.
    assert eksportuj_sft(cel, sciezka=p, pomin_przyciete=False) == 2


@_bez_wylacznika
def test_przyciety_prompt_ale_pelna_odpowiedz_tez_pomijany(tmp_path):
    """Granica: przycięcie ZNACZNIKUJE cały wpis — nie zgadujemy, które pole ucierpiało."""
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "x" * (LIMIT_ZNAKOW + 1), "pełna odpowiedź " * 10, "m", sciezka=p)
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=p) == 0


@_bez_wylacznika
def test_statystyki_licza_przyciete(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt", "x" * (LIMIT_ZNAKOW + 1), "m", sciezka=p)
    zapisz_pare("s", "pyt2", "zdrowa", "m", sciezka=p)
    s = statystyki(p)
    assert s["par"] == 2 and s["przyciete"] == 1


# ── cache odcisków (poprawka wydajności — musi zostać POPRAWNY) ───────────────

@_bez_wylacznika
def test_cache_nie_gubi_dedupu_przy_wielu_zapisach(tmp_path):
    """Cache ma przyspieszać, nie zmieniać zachowania: dedup dalej działa po serii zapisów."""
    p = tmp_path / "pary.jsonl"
    for i in range(5):
        assert zapisz_pare("s", f"pyt{i}", f"odp{i}", "m", sciezka=p) is True
    for i in range(5):
        assert zapisz_pare("s", f"pyt{i}", f"odp{i}", "m", sciezka=p) is False   # wszystkie dupy
    assert len(list(czytaj_pary(p))) == 5


@_bez_wylacznika
def test_cache_wykrywa_zmiane_pliku_z_zewnatrz(tmp_path):
    """
    GRANICA poprawności cache: gdy plik zmieni ktoś SPOZA procesu (inny bieg, ręczna edycja),
    stat() musi to wykryć i przeładować — inaczej dopisalibyśmy duplikat.
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt", "odp", "m", sciezka=p)          # cache rozgrzany
    tresc = p.read_text(encoding="utf-8")
    p.write_text("", encoding="utf-8")                       # ktoś wyczyścił plik
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is True   # nie ma już duplikatu
    p.write_text(tresc, encoding="utf-8")                    # ktoś przywrócił
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is False  # znów duplikat → wykryty


@_bez_wylacznika
def test_cache_znika_gdy_plik_skasowany(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt", "odp", "m", sciezka=p)
    p.unlink()
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=p) is True   # czysty start, nie duplikat
    assert len(list(czytaj_pary(p))) == 1


@_bez_wylacznika
def test_cache_izoluje_pliki(tmp_path):
    """Dwa zbiory nie mogą się widzieć nawzajem przez wspólny cache."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=a) is True
    assert zapisz_pare("s", "pyt", "odp", "m", sciezka=b) is True   # ten sam odcisk, inny plik
    assert len(list(czytaj_pary(a))) == 1 and len(list(czytaj_pary(b))) == 1


@_bez_wylacznika
def test_eksport_kolapsuje_probki_tego_samego_pytania(tmp_path):
    """
    🚨 Nauczyciel bywa NIESPÓJNY (zmierzone: te same nagłówki → +0.8 i -0.4). Eksport obu
    uczy sprzecznych etykiet dla identycznego wejścia. Domyślnie: jedna próbka per pytanie.
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "te same nagłówki", '{"sentyment": 0.8}', "m", sciezka=p)
    zapisz_pare("s", "te same nagłówki", '{"sentyment": -0.4}', "m", sciezka=p)
    zapisz_pare("s", "inne nagłówki", '{"sentyment": 0.1}', "m", sciezka=p)
    cel = tmp_path / "sft.jsonl"

    assert eksportuj_sft(cel, sciezka=p) == 2            # 2 pytania, nie 3 próbki
    tresci = [json.loads(w)["messages"][-1]["content"]
              for w in cel.read_text(encoding="utf-8").splitlines()]
    assert '{"sentyment": 0.8}' in tresci                # pierwsza próbka wygrywa (deterministycznie)
    assert '{"sentyment": -0.4}' not in tresci           # sprzeczna NIE wchodzi

    # Świadome wyłączenie (np. pod przyszły konsensus/self-consistency w E4).
    assert eksportuj_sft(cel, sciezka=p, jedna_probka_na_pytanie=False) == 3


@_bez_wylacznika
def test_eksport_kolaps_dziala_na_starych_wpisach_bez_pola(tmp_path):
    """Wsteczna zgodność: wpisy sprzed limitu nie mają `odcisk_pytania` — kolaps i tak działa."""
    p = tmp_path / "pary.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for i in range(3):
            f.write(json.dumps({"odcisk": f"s{i}", "system": "s", "prompt": "to samo",
                                "odpowiedz": f"sprzeczna {i}"}, ensure_ascii=False) + "\n")
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=p) == 1


@_bez_wylacznika
def test_eksport_bez_system_promptu_pomija_role_system(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("", "pytanie", "odpowiedź", "m", sciezka=p)
    cel = tmp_path / "sft.jsonl"
    assert eksportuj_sft(cel, sciezka=p) == 1
    wiersz = json.loads(cel.read_text(encoding="utf-8").strip())
    assert [m["role"] for m in wiersz["messages"]] == ["user", "assistant"]


# ─────────────────────────────────────────────────────────────────────────────
# RODZAJ ZADANIA: proza vs klasyfikacja (2026-07-27)
# Wada, którą te testy zamrażają: jeden próg długości dla dwóch różnych rodzajów zadań
# skasował 100% par klasyfikacji (102 pary `news_llm` → 0 użytecznych), a meldunek
# nazywał ten martwy strumień postępem Szkoły.
# ─────────────────────────────────────────────────────────────────────────────

def test_rodzaj_pary_odtwarza_ze_zrodla_gdy_brak_pola():
    """Wpisy sprzed wprowadzenia pola `rodzaj` — rodzaj odtwarzamy ze źródła."""
    assert rodzaj_pary({"zrodlo": "news_llm"}) == RODZAJ_KLASYFIKACJI
    assert rodzaj_pary({"zrodlo": "bibliotekarz"}) == RODZAJ_PROZA
    assert rodzaj_pary({}) == RODZAJ_PROZA            # brak wiedzy → proza (próg obowiązuje)


def test_rodzaj_jawny_wygrywa_ze_zrodlem():
    """Pole `rodzaj` to deklaracja wołającego — ma pierwszeństwo nad zgadywaniem ze źródła."""
    assert rodzaj_pary({"rodzaj": "proza", "zrodlo": "news_llm"}) == RODZAJ_PROZA
    assert rodzaj_pary({"rodzaj": "KLASYFIKACJA", "zrodlo": "bibliotekarz"}) == RODZAJ_KLASYFIKACJI
    assert rodzaj_pary({"rodzaj": "bzdura", "zrodlo": "news_llm"}) == RODZAJ_KLASYFIKACJI


@_bez_wylacznika
def test_prog_dlugosci_nie_obowiazuje_klasyfikacji(tmp_path):
    """
    🚨 GRANICA GŁÓWNA: poprawny werdykt klasyfikatora ma ~35 znaków, próg prozy to 200.
    Przed naprawą ta para NIE ISTNIAŁA dla treningu; po naprawie decyduje struktura.
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "nagłówki", '{"sentyment": 0.6, "pewnosc": 0.7}', "m",
                zrodlo="news_llm", sciezka=p)
    zapisz_pare("s", "rozwiń temat", "krótka proza", "m", zrodlo="bibliotekarz", sciezka=p)

    assert policz_sft(p, min_znakow_odpowiedzi=200) == 1     # klasyfikacja przechodzi…
    assert policz_sft(p, min_znakow_odpowiedzi=0) == 2       # …a proza dopiero bez progu


@_bez_wylacznika
def test_konsensus_bierze_mediane_a_nie_pierwsza_probke(tmp_path):
    """
    🚨 NAJOSTRZEJSZY PRZYPADEK (zmierzony na żywym ledgerze 2026-07-27, 3 z 32 pytań):
    pierwsza próbka ma ZNAK PRZECIWNY do mediany — reguła „pierwsza wygrywa" uczyłaby
    ucznia byka tam, gdzie nauczyciel przeważnie widział niedźwiedzia.
    """
    p = tmp_path / "pary.jsonl"
    for s in (0.2, -0.3, -0.2):
        zapisz_pare("s", "te same nagłówki", json.dumps({"sentyment": s, "pewnosc": 0.5}),
                    "m", zrodlo="news_llm", sciezka=p)
    cel = tmp_path / "sft.jsonl"

    assert eksportuj_sft(cel, sciezka=p) == 1                # trzy próbki → jeden przykład
    odp = json.loads(json.loads(cel.read_text(encoding="utf-8").strip())["messages"][-1]["content"])
    assert odp["sentyment"] == -0.2                          # mediana, NIE pierwsza (+0.2)
    assert odp["pewnosc"] == 0.5                             # zgodne próbki → wartość bez zmian


@_bez_wylacznika
def test_konsensus_parzysta_liczba_probek_usrednia_srodek(tmp_path):
    """Granica mediany: przy parzystej liczbie próbek `statistics.median` uśrednia dwie środkowe."""
    p = tmp_path / "pary.jsonl"
    for s in (0.1, 0.3):
        zapisz_pare("s", "pytanie", json.dumps({"sentyment": s}), "m",
                    zrodlo="news_llm", sciezka=p)
    cel = tmp_path / "sft.jsonl"
    eksportuj_sft(cel, sciezka=p)
    odp = json.loads(json.loads(cel.read_text(encoding="utf-8").strip())["messages"][-1]["content"])
    assert abs(odp["sentyment"] - 0.2) < 1e-9


@_bez_wylacznika
def test_zepsuty_json_odsiany_przed_zwijaniem(tmp_path):
    """
    🚨 KOLEJNOŚĆ ≠ JAKOŚĆ: gdyby walidacja szła PO zwinięciu, wadliwa pierwsza próbka
    wygrałaby z poprawnymi i uczeń uczyłby się produkować wyjście nie do sparsowania.
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie", "{sentyment: 0.9", "m", zrodlo="news_llm", sciezka=p)
    for s in (-0.4, -0.6):
        zapisz_pare("s", "pytanie", json.dumps({"sentyment": s}), "m",
                    zrodlo="news_llm", sciezka=p)
    cel = tmp_path / "sft.jsonl"

    assert eksportuj_sft(cel, sciezka=p) == 1
    odp = json.loads(json.loads(cel.read_text(encoding="utf-8").strip())["messages"][-1]["content"])
    assert abs(odp["sentyment"] - (-0.5)) < 1e-9             # mediana z DWÓCH poprawnych


@_bez_wylacznika
def test_same_zepsute_probki_nie_daja_przykladu(tmp_path):
    """Granica pustki: pytanie bez ANI JEDNEJ poprawnej próbki nie ma czego uczyć."""
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie", "nie wiem", "m", zrodlo="news_llm", sciezka=p)
    zapisz_pare("s", "pytanie", "[1, 2, 3]", "m", zrodlo="news_llm", sciezka=p)  # JSON, ale nie obiekt
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=p) == 0


@_bez_wylacznika
def test_jedna_probka_klasyfikacji_zostaje_kanonicznie(tmp_path):
    """Granica jednej próbki: konsensus z jednego strzału = ten strzał, w formacie kanonicznym."""
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie", '{\n  "sentyment": -0.2,\n  "pewnosc": 0.6\n}', "m",
                zrodlo="news_llm", sciezka=p)
    cel = tmp_path / "sft.jsonl"
    assert eksportuj_sft(cel, sciezka=p) == 1
    tresc = json.loads(cel.read_text(encoding="utf-8").strip())["messages"][-1]["content"]
    assert tresc == '{"sentyment": -0.2, "pewnosc": 0.6}'    # jeden format wyjścia dla ucznia


@_bez_wylacznika
def test_wylaczony_kolaps_daje_klasyfikacje_bez_konsensusu(tmp_path):
    """`jedna_probka_na_pytanie=False` — próbki surowe, bez zwijania (tryb inspekcji)."""
    p = tmp_path / "pary.jsonl"
    for s in (0.2, -0.3):
        zapisz_pare("s", "pytanie", json.dumps({"sentyment": s}), "m",
                    zrodlo="news_llm", sciezka=p)
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=p, jedna_probka_na_pytanie=False) == 2


@_bez_wylacznika
def test_zepsuty_json_nie_wychodzi_takze_bez_zwijania(tmp_path):
    """
    🚨 LUKA ZŁAPANA MUTACJĄ (2026-07-27): usunięcie bramki poprawności z `pary_sft` NIE
    wywracało żadnego testu, bo na ścieżce zwijania broni jeszcze konsensus. Broniona jest
    dopiero ścieżka BEZ zwijania — i to ona potrzebuje własnego testu, inaczej wadliwe
    wyjście trafiłoby na trening w trybie inspekcji.
    """
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie", "{sentyment: 0.9", "m", zrodlo="news_llm", sciezka=p)
    zapisz_pare("s", "pytanie", '{"sentyment": 0.9}', "m", zrodlo="news_llm", sciezka=p)
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=p, jedna_probka_na_pytanie=False) == 1


@_bez_wylacznika
def test_prog_dlugosci_nadal_dziala_na_prozie(tmp_path):
    """REGRESJA: naprawa klasyfikacji nie ma prawa rozbroić progu tam, gdzie ma sens."""
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie A", "nie wiem", "m", zrodlo="bibliotekarz", sciezka=p)
    zapisz_pare("s", "pytanie B", "x" * 250, "m", zrodlo="bibliotekarz", sciezka=p)
    assert policz_sft(p, min_znakow_odpowiedzi=200) == 1


def test_eksport_pustego_zbioru_daje_zero(tmp_path):
    assert eksportuj_sft(tmp_path / "sft.jsonl", sciezka=tmp_path / "brak.jsonl") == 0


def test_raport_nie_wywraca_sie_na_pustce(tmp_path):
    tekst = raport(tmp_path / "brak.jsonl")
    assert "NOTARIUS" in tekst and "0" in tekst


# ── GRANICE progu datasetu (== próg vs próg±1) ────────────────────────────────

def test_postep_zero_par():
    p = postep_zbioru(0)
    assert p["cel"] == PROGI_DATASETU[0][0] and p["procent"] == 0.0
    assert p["brakuje"] == PROGI_DATASETU[0][0]


def test_postep_ponizej_progu():
    p = postep_zbioru(499)
    assert p["cel"] == 500 and p["brakuje"] == 1
    assert p["procent"] == 99.8


def test_postep_dokladnie_na_progu_przeskakuje_dalej():
    """GRANICA `==`: 500 par to próg OSIĄGNIĘTY → celem staje się następny (1000), nie 500."""
    p = postep_zbioru(500)
    assert p["cel"] == 1_000
    assert p["brakuje"] == 500
    assert p["procent"] == 50.0


def test_postep_powyzej_ostatniego_progu():
    """Poza skalą: nie dzielimy przez nic, nie przekraczamy 100% — pasek ma zostać sensowny."""
    p = postep_zbioru(999_999)
    assert p["cel"] == PROGI_DATASETU[-1][0]
    assert p["procent"] == 100.0 and p["brakuje"] == 0


def test_postep_dokladnie_ostatni_prog():
    p = postep_zbioru(PROGI_DATASETU[-1][0])
    assert p["procent"] == 100.0 and p["brakuje"] == 0


def test_progi_rosnace():
    """Kolejność progów jest założeniem `postep_zbioru` (pierwszy większy wygrywa)."""
    wartosci = [prog for prog, _ in PROGI_DATASETU]
    assert wartosci == sorted(wartosci) and len(set(wartosci)) == len(wartosci)


@_bez_wylacznika
def test_pasek_postepu_w_raporcie(tmp_path):
    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pyt", "odp", "m", sciezka=p)
    tekst = raport(p)
    assert "█" in tekst or "░" in tekst      # pasek narysowany (Prawo XXIV)
    assert "1/500" in tekst


# ── ŻELAZNA ZASADA na moście: awaria pisarza ≠ awaria nauczyciela ─────────────

def test_most_zwraca_odpowiedz_gdy_pisarz_pada(monkeypatch):
    """
    Najważniejszy test tego modułu: gdyby NOTARIUS eksplodował, `zapytaj()` MUSI i tak
    zwrócić odpowiedź nauczyciela. Protokół jest dodatkiem do mowy, nigdy jej warunkiem.
    """
    import imperium.biblioteki.notarius as notarius
    from imperium.cesarz.deepseek_glos import GlosImperium

    def wybuch(*a, **kw):
        raise RuntimeError("dysk spłonął")

    monkeypatch.setattr(notarius, "zapisz_pare", wybuch)

    glos = GlosImperium.__new__(GlosImperium)      # bez __init__ → bez potrzeby klucza API
    glos.model = "deepseek-v4-flash"
    glos._protokoluj("s", "p", "o", 0.7)           # nie może rzucić


# ── JEDEN FILTR, DWÓCH KONSUMENTÓW (recenzja 2026-07-26) ─────────────────────

@_bez_wylacznika
def test_licznik_i_eksport_zawsze_zgodne(tmp_path):
    """`policz_sft` MUSI dać dokładnie tyle, ile `eksportuj_sft` zapisze — co do sztuki.

    To niezmiennik, dla którego filtr został wydzielony do `pary_sft`. Meldunek BREVIARIUM
    podaje Cezarowi postęp Szkoły TIRO właśnie z licznika; gdyby liczył innym filtrem niż
    eksport, procent gotowości opisywałby zbiór, który nigdy nie pojedzie na trening.
    """
    from imperium.biblioteki.notarius import policz_sft

    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie A", "x" * 300, "m", sciezka=p)
    zapisz_pare("s", "pytanie A", "y" * 300, "m", sciezka=p)   # duplikat pytania → kolaps
    zapisz_pare("s", "pytanie B", "krotka", "m", sciezka=p)    # za krótka → odsiew
    zapisz_pare("s", "pytanie C", "z" * 300, "m", sciezka=p)

    cel = tmp_path / "sft.jsonl"
    zapisane = eksportuj_sft(cel, p, min_znakow_odpowiedzi=200)
    policzone = policz_sft(p, min_znakow_odpowiedzi=200)
    linie = [l for l in cel.read_text(encoding="utf-8").splitlines() if l.strip()]

    assert policzone == zapisane == len(linie) == 2


@_bez_wylacznika
def test_licznik_nie_dotyka_dysku(tmp_path, monkeypatch):
    """Licznik biegnie na OBU końcach każdej sesji — nie ma prawa nic zapisywać.

    Wcześniej BREVIARIUM serializował cały zbiór do pliku tymczasowego tylko po to, by
    poznać liczbę; koszt rósł z każdą zebraną parą (recenzja 2026-07-26).
    """
    from imperium.biblioteki import notarius

    p = tmp_path / "pary.jsonl"
    zapisz_pare("s", "pytanie", "x" * 300, "m", sciezka=p)

    prawdziwe_open = notarius.Path.open

    def tylko_do_odczytu(self, mode="r", *a, **kw):
        if any(z in mode for z in ("w", "a", "x", "+")):
            raise AssertionError(f"licznik otworzył {self} w trybie zapisu ({mode})")
        return prawdziwe_open(self, mode, *a, **kw)

    monkeypatch.setattr(notarius.Path, "open", tylko_do_odczytu)
    assert notarius.policz_sft(p, min_znakow_odpowiedzi=200) == 1
