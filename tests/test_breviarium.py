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
    # KONTRAKT ZMIENIONY 2026-07-26: brak rejestru to NIE „zero cząstek", tylko „nie wiem".
    # Kolejka jest gitignorowana, więc w chmurze pliku nie ma, a meldunek ogłaszał wtedy
    # „kolejka 0 | czeka na sędziego 0" — dług przeglądu wyglądał na spłacony, choć na
    # lokalu leżały 34 cząstki. Poprzednia wersja tego testu WYMUSZAŁA to kłamstwo (`== 0`).
    stan = bv.stan_hyginusa()
    assert stan["rejestr_nieobecny"] is True
    assert stan["czastek"] is None and stan["czeka_na_sedziego"] is None, \
        "brak rejestru musi milczeć (None), nie meldować zera"
    assert stan["profile_dispensatora"], \
        "konfiguracja mowy jest w KODZIE — abstynencja o kolejce nie może jej wygaszać"
    assert "NIEZNANA" in bv.banner(), "meldunek ma nazwać brak wiedzy wprost (Prawo I)"
    # Sprawdzamy POLA, nie równość całego słownika: porównanie 1:1 pękało przy KAŻDYM
    # nowym wskaźniku meldunku (2026-07-26: doszły `pary_uzyteczne` i `dysk_tiro_widoczny`),
    # czyli test karał ROZBUDOWĘ organu zamiast pilnować jego zachowania.
    tiro = bv.stan_tiro()
    assert tiro["pary_nauczyciela"] == 0
    assert tiro["modele"] == []
    assert tiro["silnik"] is False, "tmp_path to widoczny dysk — brak silnika jest ZMIERZONY"
    assert tiro["dysk_tiro_widoczny"] is True
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


def test_wykrywa_wpiecie_przez_argument_profil(monkeypatch, tmp_path):
    """Realna droga wpięcia: Hyginus nie importuje Szafarza — oddaje mu decyzję przez
    `zapytaj(profil=...)`. Detektor szukający napisu przegapiał DOKŁADNIE ten przypadek."""
    (tmp_path / "narzedzia").mkdir()
    (tmp_path / "narzedzia" / "bibliotekarz.py").write_text(
        'odp = glos.zapytaj(SYS, tresc, temperatura=0.4, profil="zwiad")\n', encoding="utf-8")
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is True


def test_sam_komentarz_to_NIE_wpiecie(monkeypatch, tmp_path):
    """Fałszywy POZYTYW: „TODO: wpiąć DISPENSATORA" nie może uchodzić za wpięcie.
    Napis w pliku nigdy nie dowodzi, że coś się WYKONUJE."""
    (tmp_path / "narzedzia").mkdir()
    (tmp_path / "narzedzia" / "bibliotekarz.py").write_text(
        '# TODO: wpiąć DISPENSATORA (dispensator) — na razie nic\nx = 1\n', encoding="utf-8")
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is False


def test_niepoprawny_skladniowo_plik_nie_wywala(monkeypatch, tmp_path):
    """Granica: plik z błędem składni → False, nie SyntaxError w meldunku otwarcia."""
    (tmp_path / "narzedzia").mkdir()
    (tmp_path / "narzedzia" / "bibliotekarz.py").write_text("def (((\n", encoding="utf-8")
    monkeypatch.setattr(bv, "ROOT", tmp_path)
    assert bv._czy_dispensator_wpiety() is False


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


# ── SIGILLUM PROBATIONIS: aktualność wyniku testów (zwiad adwersarialny 07-21) ──

def _pieczec(monkeypatch, tmp_path, **pola):
    dane = {"zaliczone": 100, "oblane": 0, "odcisk_zrodel": bv.odcisk_zrodel(),
            "commit": "abc123", "drzewo_brudne": False, "kiedy": "2026-07-21T10:00:00"}
    dane.update(pola)
    p = tmp_path / "sigillum.json"
    p.write_text(json.dumps(dane), encoding="utf-8")
    monkeypatch.setattr(bv, "PIECZEC_TESTOW", p)
    return p


def test_brak_pieczeci_to_alarm_nie_cisza(monkeypatch, tmp_path):
    """Nikt nie odnotował biegu → 🚨, nie milczenie. Cichy optymizm jest gorszy niż niewiedza."""
    monkeypatch.setattr(bv, "PIECZEC_TESTOW", tmp_path / "nie_ma.json")
    assert bv.stan_testow()["status"] == "BRAK"


def test_pieczec_nieczytelna_to_alarm(monkeypatch, tmp_path):
    """Granica: uszkodzony JSON → BRAK, nie wyjątek w meldunku otwarcia."""
    p = tmp_path / "s.json"
    p.write_text("{to nie json", encoding="utf-8")
    monkeypatch.setattr(bv, "PIECZEC_TESTOW", p)
    assert bv.stan_testow()["status"] == "BRAK"


def test_oblane_testy_zawsze_czerwone(monkeypatch, tmp_path):
    """Oblane biją wszystko — nawet gdy odcisk źródeł się zgadza."""
    _pieczec(monkeypatch, tmp_path, oblane=3)
    w = bv.stan_testow()
    assert w["status"] == "CZERWONE" and "3 OBLANYCH" in w["opis"]


def test_wynik_dla_innego_kodu_to_NIEZNANY(monkeypatch, tmp_path):
    """RDZEŃ: zielone dla kodu, którego już nie ma, NIE jest zgodą — to niewiedza."""
    _pieczec(monkeypatch, tmp_path, odcisk_zrodel="odcisk-zupelnie-innego-kodu")
    w = bv.stan_testow()
    assert w["status"] == "NIEZNANY" and "INNEGO KODU" in w["opis"]


def test_pieczec_bez_odcisku_nie_udaje_wiedzy(monkeypatch, tmp_path):
    """Wsteczna zgodność: stara pieczęć (sprzed odcisku) → NIEZNANY, nie fałszywe ZIELONE."""
    dane = {"zaliczone": 100, "oblane": 0, "commit": "abc", "kiedy": "2026-07-20T10:00:00"}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(dane), encoding="utf-8")
    monkeypatch.setattr(bv, "PIECZEC_TESTOW", p)
    assert bv.stan_testow()["status"] == "NIEZNANY"


def test_zielone_dla_dokladnie_tego_kodu(monkeypatch, tmp_path):
    """Kontrola POZYTYWNA: detektor MUSI umieć powiedzieć „ZIELONE".
    Detektor alarmujący zawsze uczy operatora ignorować siebie — czyli psuje to, po co powstał.
    To była realna wada pierwszej wersji (porównanie z commitem: przy rytmie
    edytuj→testy→commit nigdy nie dałoby zielonego)."""
    _pieczec(monkeypatch, tmp_path)
    assert bv.stan_testow()["status"] == "ZIELONE"


def test_brudne_drzewo_nie_uniewaznia_wyniku(monkeypatch, tmp_path):
    """Bieg na brudnym drzewie jest NORMALNY (edytuj → testy → commit). Liczy się treść
    kodu, nie stan indeksu gita — inaczej pieczęć alarmowałaby przy każdej pracy."""
    _pieczec(monkeypatch, tmp_path, drzewo_brudne=True)
    assert bv.stan_testow()["status"] == "ZIELONE"


def test_odcisk_zrodel_jest_stabilny():
    """Dwa odczyty bez zmiany kodu muszą dać ten sam odcisk (inaczej alarm co start)."""
    assert bv.odcisk_zrodel() == bv.odcisk_zrodel()


def test_odcisk_zmienia_sie_po_zmianie_kodu(tmp_path):
    """Kontrola czułości: dopisanie linii do pliku .py MUSI zmienić odcisk."""
    (tmp_path / "imperium").mkdir()
    plik = tmp_path / "imperium" / "modul.py"
    plik.write_text("x = 1", encoding="utf-8")
    przed = bv.odcisk_zrodel(tmp_path)
    plik.write_text("x = 2", encoding="utf-8")
    assert bv.odcisk_zrodel(tmp_path) != przed


def test_odcisk_nie_reaguje_na_dokumenty(tmp_path):
    """Wpis do LOG_ZMIAN nie może gasić pieczęci — inaczej fałszywy alarm po każdej notatce."""
    (tmp_path / "imperium").mkdir()
    (tmp_path / "imperium" / "m.py").write_text("x = 1", encoding="utf-8")
    przed = bv.odcisk_zrodel(tmp_path)
    (tmp_path / "DOKUMENT.md").write_text("# zmiana dokumentu", encoding="utf-8")
    assert bv.odcisk_zrodel(tmp_path) == przed


def test_stan_testow_jest_pierwsza_linia_meldunku(monkeypatch, tmp_path):
    """Czerwony stan testów nie może być schowany pod stanem sług — idzie na górę."""
    monkeypatch.setattr(bv, "PIECZEC_TESTOW", tmp_path / "brak.json")
    assert "testy" in bv.banner().splitlines()[1]


def test_pieczec_zero_testow_to_alarm_nie_zielen(monkeypatch, tmp_path):
    """Bieg, który nie uruchomił ANI JEDNEGO testu, nie jest dowodem zdrowia.
    Wcześniej raportował „✅ 0/0 dla DOKŁADNIE tego kodu" — detektor mówił
    „wszystko dobrze" o biegu, który nic nie sprawdził (recenzja 2026-07-21)."""
    _pieczec(monkeypatch, tmp_path, zaliczone=0, oblane=0)
    w = bv.stan_testow()
    assert w["status"] == "BRAK" and "nic nie sprawdził" in w["opis"]


# ── Δ wachty: raport sług na OBU końcach sesji (rozkaz Cezara 2026-07-21) ───────

def test_migawka_ma_tylko_liczby_zmienne_w_czasie(monkeypatch, tmp_path):
    """Migawka celowo NIE zawiera modeli na dysku ani klasy sprzętu — te się w trakcie
    sesji nie zmieniają, więc ich delta byłaby szumem zagłuszającym realny dorobek."""
    m = bv.migawka()
    assert set(m) <= set(bv._POLA_DELTY)
    assert "modele" not in m and "klasa_sprzetu" not in m


def test_delta_bez_migawki_nie_zmysla_roznicy(tmp_path):
    """Prawo I: brak punktu odniesienia → mówimy wprost, że różnicy NIE ZNAMY,
    zamiast pokazywać zero i sugerować „nic się nie zmieniło"."""
    assert "nie znamy" in bv.delta(tmp_path / "brak.json")


def test_delta_uszkodzona_migawka_nie_wywala(tmp_path):
    """Granica: zepsuty JSON → uczciwy komunikat, nie wyjątek przy domykaniu wachty."""
    p = tmp_path / "m.json"
    p.write_text("{to nie json", encoding="utf-8")
    assert "nie znamy" in bv.delta(p)


def test_delta_pokazuje_kierunek_zmiany(tmp_path, monkeypatch):
    """Rdzeń: różnica ma nazwać, CO wachta zrobiła sługom — ze znakiem."""
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"czastek": 34, "czeka_na_sedziego": 33,
                             "pary_nauczyciela": 193}), encoding="utf-8")
    monkeypatch.setattr(bv, "migawka",
                        lambda: {"czastek": 41, "czeka_na_sedziego": 40,
                                 "pary_nauczyciela": 193})
    tekst = bv.delta(p)
    assert "czastek: 34 → 41 (+7)" in tekst
    assert "pary_nauczyciela" not in tekst          # bez zmiany → nie zaśmieca meldunku


def test_delta_bez_zmian_mowi_to_wprost(tmp_path, monkeypatch):
    """Kontrola pozytywna: „bez zmian" to poprawny wynik, nie brak wyniku."""
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"czastek": 5}), encoding="utf-8")
    monkeypatch.setattr(bv, "migawka", lambda: {"czastek": 5})
    assert "bez zmian" in bv.delta(p)


def test_zapisz_migawke_tworzy_odczytywalny_punkt(tmp_path, monkeypatch):
    """Roundtrip: to, co zapisze otwarcie, musi dać się porównać przy domknięciu."""
    p = tmp_path / "m.json"
    monkeypatch.setattr(bv, "migawka", lambda: {"czastek": 7})
    bv.zapisz_migawke(p)
    assert json.loads(p.read_text(encoding="utf-8")) == {"czastek": 7}


def test_zapisz_migawke_nie_wywala_na_zlej_sciezce():
    """Awaria zapisu ≠ awaria meldunku — hook startowy ma działać dalej (Prawo XV)."""
    from pathlib import Path
    bv.zapisz_migawke(Path("/nieistniejacy\x00katalog/m.json"))


# ── WIDOK NIE MOŻE KŁAMAĆ O FAZACH (2026-07-26) ──────────────────────────────

def test_profile_pokazuja_faze_a_nie_katalog():
    """Meldunek MUSI pokazywać FAZA→PROFIL faktycznie użyty, nie katalog możliwości.

    Zmierzone 2026-07-26 na otwarciu wachty: meldunek listował klucze słownika
    `dispensator.PROFILE`, więc drukował „krytyka→v4-flash" i czytało się to jako
    sprzeczność z decyzją z 07-21 (KRYTYKA przeniesiona na profil `osad`, v4-pro).
    Kod był poprawny — kłamał WIDOK. Katalog możliwości pokazany w miejscu stanu
    faktycznego jest fałszywym meldunkiem, a meldunek istnieje po to, żeby na nim polegać.
    """
    from imperium.cesarz import dispensator as dsp
    from imperium.oczy.breviarium import stan_hyginusa
    from narzedzia import bibliotekarz as bib

    profile = stan_hyginusa()["profile_dispensatora"]
    assert profile, "meldunek bez profili — awaria importu ukryta przez except"

    wpis_krytyki = [p for p in profile if p.startswith("krytyka→")]
    assert len(wpis_krytyki) == 1, profile
    # Nazwa profilu MUSI być tą, której naprawdę używa faza krytyki (dziś: `osad`).
    assert f"[{bib._PROFIL_KRYTYKA}]" in wpis_krytyki[0], (
        f"widok pokazuje inny profil niż _PROFIL_KRYTYKA={bib._PROFIL_KRYTYKA}: {wpis_krytyki[0]}")
    # ...a model MUSI być modelem TEGO profilu, policzonym z rejestru, nie wpisanym.
    oczekiwany = str(dsp.PROFILE[bib._PROFIL_KRYTYKA]["model"]).replace("deepseek-", "")
    assert oczekiwany in wpis_krytyki[0], wpis_krytyki[0]

    for faza, stala in (("klasyfikacja", bib._PROFIL_ROZWIN), ("zwiad", bib._PROFIL_ZWIAD)):
        wpis = [p for p in profile if p.startswith(f"{faza}→")]
        assert len(wpis) == 1 and f"[{stala}]" in wpis[0], (faza, wpis)


# ── TIRO: „nie widzę" ≠ „nie ma"; pary surowe ≠ pary użyteczne (2026-07-26) ──────

def test_dysk_tiro_z_innego_systemu_abstynuje(monkeypatch):
    """`C:\\TIRO` na Linuksie to NIEWIDOCZNOŚĆ, nie zmierzony brak silnika.

    Ten fałszywy alarm wprowadził w błąd samego Architekta (2026-07-26), który podał go
    Cezarowi jako „największa utrata potencjału" — podczas gdy llama.cpp stoi na laptopie
    od 07-16 (zmierzone: Qwen3-1.7B 9.64 t/s). Meldunek MUSI odróżniać jedno od drugiego.
    """
    import sys as _sys
    from pathlib import Path

    obca = Path("C:\\TIRO") if not _sys.platform.startswith("win") else Path("/home/tiro")
    monkeypatch.setattr(bv, "KATALOG_TIRO", obca)
    stan = bv.stan_tiro()
    assert stan["silnik"] is None, "obcy system plików → None (nie wiem), nigdy False"
    assert stan["dysk_tiro_widoczny"] is False
    baner = bv.banner()
    assert "niewidoczny stąd" in baner
    assert "brak silnika" not in baner, "nie wolno oskarżać o brak tego, czego nie widać"


def test_zmierzony_brak_silnika_nadal_krzyczy(monkeypatch, tmp_path):
    """GRANICA: katalog TEGO systemu, w którym silnika NIE MA → to pomiar, alarm zostaje.

    Abstynencja nie może uciszyć prawdziwego braku — inaczej wyciszylibyśmy organ zamiast
    go naprawić (dokładnie odwrotność celu).
    """
    monkeypatch.setattr(bv, "KATALOG_TIRO", tmp_path / "TIRO")
    stan = bv.stan_tiro()
    assert stan["silnik"] is False, "brak na widocznym dysku to zmierzony fakt, nie None"
    assert "brak silnika" in bv.banner()


def test_pary_uzyteczne_nie_przekraczaja_surowych():
    """Postęp Szkoły liczymy parami, które PRZEŻYJĄ eksport SFT (kolaps + filtr jakości).

    Zmierzone 2026-07-26: 329 surowych → 140 użytecznych. Meldunek podający wyłącznie
    liczbę surową zawyżał gotowość 2,35× (14% progu 1000 wyglądało jak 66% progu 500).
    """
    stan = bv.stan_tiro()
    assert stan["pary_uzyteczne"] is None or (
        0 <= stan["pary_uzyteczne"] <= stan["pary_nauczyciela"]), stan
    if stan["pary_uzyteczne"] is not None:
        assert f"{stan['pary_nauczyciela']} surowych" in bv.banner()
        assert f"{stan['pary_uzyteczne']} użytecznych" in bv.banner()
