"""Testy SIGILLARIUM (SIGLA IMPERII) + naprawionego upsertu pamięci proceduralnej.

Perspektywa recenzenta, nie autora (Reguła Test-Granic): pieczęć ma paść GŁOŚNO,
gdy sekcja konstytucji zniknie, gdy skill zgubi swoją pieczęć albo gdy komenda
bramki wskaże nieistniejący plik. Cicha pusta procedura to dokładnie klasa
„mechanizm, który przy awarii wygląda na sprawny".
"""
from pathlib import Path
from unittest import mock

from imperium.biblioteki import pamiec_proceduralna as pp
from imperium.biblioteki import sigillarium as sg

KORZEN = Path(__file__).resolve().parents[1]
SKILLE = KORZEN / ".claude" / "skills"


# ── PARSER KONSTYTUCJI: granice ───────────────────────────────────────────────

_PROBKA = """## 🧪 SEKCJA PROBNA (ROZKAZ STAŁY — ogon nagłówka bywa zmieniany)

Proza wstępu, która NIE jest krokiem.

1. **Pierwszy krok** z kontynuacją
   dopisaną w drugiej linii.
2. Drugi krok.
5b. Krok dopisany później (sufiks literowy).

**Złamanie:** to jest kara, nie krok — parser musi się tu zatrzymać.

## 🔚 NASTĘPNA SEKCJA
1. Krok obcej sekcji, którego nie wolno doliczyć.
"""


def test_parser_sklada_kontynuacje_i_zatrzymuje_sie_na_zlamaniu():
    kroki = sg.kroki_z_konstytucji("## 🧪 SEKCJA PROBNA", _PROBKA)
    assert len(kroki) == 3, kroki
    assert kroki[0] == "1. **Pierwszy krok** z kontynuacją dopisaną w drugiej linii."
    assert not any("kara" in k for k in kroki)          # klauzula karna odcięta
    assert not any("obcej sekcji" in k for k in kroki)  # następna sekcja odcięta


def test_parser_lapie_numeracje_z_sufiksem():
    kroki = sg.kroki_z_konstytucji("## 🧪 SEKCJA PROBNA", _PROBKA)
    assert kroki[-1].startswith("5b. "), kroki[-1]


def test_parser_nie_gubi_niewcietej_kontynuacji():
    """Zawinięta linia bez wcięcia (typowa przy ręcznej edycji CLAUDE.md) była CICHO
    gubiona — numeracja zostawała ciągła, a treść kroku ucięta (zmierzone 2026-07-20).
    Test ciągłości numeracji tego NIE łapał, bo numery były w porządku."""
    probka = ("## 🧪 S\n"
              "1. Krok jeden.\n"
              "2. Krok dwa z długim opisem\n"
              "kontynuacja bez wcięcia MUSI przetrwać\n"
              "   i wcięta też.\n"
              "3. Krok trzeci.\n")
    kroki = sg.kroki_z_konstytucji("## 🧪 S", probka)
    assert len(kroki) == 3, kroki
    assert "kontynuacja bez wcięcia MUSI przetrwać" in kroki[1]
    assert "i wcięta też" in kroki[1]


def test_parser_widzi_DOKLADNIE_tyle_krokow_ile_jest_w_konstytucji():
    """Regresja na PRAWDZIWYM CLAUDE.md — bez ręcznie wpisanej liczby.

    Pierwsza wersja twierdziła `== 7 / 10 / 5`. To była RĘCZNA LICZBA o systemie, czyli
    dokładnie klasa, którą zwalcza Warstwa 15 audytu: pierwszy rozkaz Cezara dopisany do
    checklisty wywracał test, a „naprawa" polegałaby na podbiciu stałej — czyli na uczeniu
    się ignorowania własnej bramki. Zdarzyło się to przy dodaniu kroku 4b (raport sług na
    domknięciu, 2026-07-21).

    Prawdziwym niezmiennikiem NIE jest liczba kroków, tylko to, że parser widzi ICH TYLE,
    ILE NAPRAWDĘ JEST — policzone niezależnie z pliku. Konstytucja może rosnąć; parser nie
    ma prawa gubić ani doklejać.
    """
    import re

    sprawdzone = 0
    for s in sg.wszystkie():
        if not s.sekcja:
            continue          # LIMES trzyma komendy w rejestrze, nie w sekcji konstytucji
        sekcja = sg._tresc_sekcji(s.sekcja)
        # Niezależny licznik: linie otwierające krok — „1. ", „4b. ", „5b. ".
        oczekiwane = len(re.findall(r"^\d+[a-z]?\.\s", sekcja, re.M))
        assert oczekiwane > 0, f"{s.nazwa}: sekcja w CLAUDE.md nie ma ani jednego kroku"
        assert len(sg.kroki(s.nazwa)) == oczekiwane, (
            f"{s.nazwa}: parser widzi {len(sg.kroki(s.nazwa))}, w CLAUDE.md jest {oczekiwane}")
        sprawdzone += 1
    assert sprawdzone >= 2, "test przestał cokolwiek sprawdzać — sekcje zniknęły z rejestru"


def test_kazdy_krok_ma_niepusta_tresc():
    """Krok policzony, ale pusty, to gorzej niż krok zgubiony — pieczęć wyglądałaby
    na kompletną, a operator nie wiedziałby, co zrobić (klasa: mechanizm, który przy
    awarii wygląda na sprawny)."""
    for sigil in ("apertio", "clausura", "limes"):
        for i, krok in enumerate(sg.kroki(sigil)):
            assert krok.strip(), f"{sigil}: krok {i} pusty"
            assert len(krok.strip()) > 20, f"{sigil}: krok {i} podejrzanie krótki: {krok!r}"


def test_parser_dopasowuje_naglowek_po_prefiksie():
    """Ogon nagłówka („(ROZKAZ STAŁY — Cezar zatwierdził ...)") bywa aktualizowany.

    Sam prefiks wystarcza, więc zmiana daty w ogonie nie zabija pieczęci — ale
    prefiks MUSI być prawdziwym początkiem nagłówka, nie luźnym podciągiem
    (klasa wady: „detektor na podciągu zamiast granicy", Księga Wad).
    """
    assert len(sg.kroki_z_konstytucji("## 🧪 SEKCJA PROBNA", _PROBKA)) == 3
    assert len(sg.kroki_z_konstytucji("## 🧪 SEKCJA PROBNA (ROZKAZ", _PROBKA)) == 3
    assert sg.kroki_z_konstytucji("SEKCJA PROBNA", _PROBKA) == []
    assert sg.kroki_z_konstytucji("## 🧪 SEKCJA PROBNA X", _PROBKA) == []


def test_brak_sekcji_daje_pusto_a_nie_wyjatek():
    assert sg.kroki_z_konstytucji("## NIE MA TAKIEJ SEKCJI", _PROBKA) == []
    assert sg._tresc_sekcji("## NIE MA TAKIEJ SEKCJI", _PROBKA) == ""


# ── REJESTR SIGLI ─────────────────────────────────────────────────────────────

def test_kazde_sigillum_ma_zywe_kroki():
    """Pusta pieczęć = sekcja zniknęła z CLAUDE.md. Musi paść tu, nie w trakcie sesji."""
    for s in sg.wszystkie():
        assert sg.kroki(s.nazwa), f"PIECZĘĆ PUSTA: {s.nazwa} (sekcja: {s.sekcja!r})"


def test_kroki_maja_ciagla_numeracje_bez_dziur():
    """Dziura w numeracji = krok zgubiony po cichu (np. ktoś usunął wcięcie kontynuacji).

    Liczba kroków celowo NIE jest przybita na sztywno — checklisty rosną. Ale numeracja
    musi zaczynać się od 1 i iść bez przeskoków; sufiks (`5b`) dokłada się do swojej
    liczby, nie tworzy nowej.
    """
    import re as _re
    for s in sg.wszystkie():
        if not s.sekcja:
            continue
        numery = []
        for krok in sg.kroki(s.nazwa):
            m = _re.match(r"^(\d+)([a-z]?)\.", krok)
            assert m, f"{s.nazwa}: krok bez numeru — {krok[:60]}"
            numery.append(int(m.group(1)))
        assert numery[0] == 1, f"{s.nazwa}: checklista nie zaczyna się od 1 ({numery})"
        for poprz, nast in zip(numery, numery[1:]):
            assert nast in (poprz, poprz + 1), f"{s.nazwa}: dziura w numeracji {poprz}→{nast}"


def test_sigillum_po_nazwie_aliasie_i_wielkosci_liter():
    assert sg.sigillum("APERTIO").nazwa == "APERTIO"
    assert sg.sigillum("apertio").nazwa == "APERTIO"
    assert sg.sigillum("koniec sesji").nazwa == "CLAUSURA"
    assert sg.sigillum("  Bramka  ") is None or sg.sigillum("bramka").nazwa == "LIMES"
    assert sg.sigillum("bramka").nazwa == "LIMES"


def test_sigillum_nieznane_i_puste_nie_wybucha():
    assert sg.sigillum("nie ma takiej") is None
    assert sg.sigillum("") is None
    assert sg.sigillum(None) is None
    assert sg.kroki("nie ma takiej") == []
    assert "❌" in sg.raport("nie ma takiej")
    assert sg._main(["x", "nie ma takiej"]) == 1
    assert sg._main(["x", "apertio"]) == 0


def test_limes_nie_wola_nieistniejacych_skryptow():
    """Bramka wołająca zniknięty skrypt udawałaby sprawną (Warstwa 16, API-widma)."""
    assert sg.brakujace_komendy("LIMES") == []
    for s in sg.wszystkie():
        assert sg.brakujace_komendy(s.nazwa) == []


def test_brakujace_komendy_wykrywa_martwy_modul_dash_m():
    """Przypadek NEGATYWNY: komenda `python -m ...` na nieistniejący moduł MUSI zostać
    wykryta. Wcześniej regex `\\S+\\.py` jej nie widział — martwa komenda LEX TALIONIS
    (krok 5b, forma `-m`) przeszłaby cicho (zmierzone 2026-07-20)."""
    widmo = sg.Sigillum(nazwa="WIDMO_M", tytul="W", opis="", wyzwalacze=["widmo_m"],
                        komendy=["python -m imperium.biblioteki.nie_ma_takiego_modulu bilans"])
    sg.SIGLA["WIDMO_M"] = widmo
    try:
        assert sg.brakujace_komendy("WIDMO_M") == [widmo.komendy[0]]
    finally:
        sg.SIGLA.pop("WIDMO_M", None)


def test_cel_komendy_rozpoznaje_zywy_modul_i_plik():
    assert sg._cel_komendy_istnieje("python -m imperium.biblioteki.codex_notarum bilans") is True
    assert sg._cel_komendy_istnieje("python narzedzia/audyt_spojnosci.py") is True
    assert sg._cel_komendy_istnieje("python -m imperium.biblioteki.brak_xyz") is False
    assert sg._cel_komendy_istnieje("echo bez celu") is None


def test_raport_pustej_pieczeci_krzyczy_zamiast_milczec():
    """Bez `monkeypatch` — runner Imperium ma własny, minimalny shim (brak `setitem`).

    Pytest świecił zielono, a bramka projektu padała: zielone w narzędziu, które NIE
    jest bramką, to fałszywy spokój. Sprzątanie w `finally`, żeby rejestr wrócił do
    stanu sprzed testu nawet po asercji.
    """
    widmo = sg.Sigillum(nazwa="WIDMO", tytul="WIDMO", opis="", wyzwalacze=["widmo"],
                        sekcja="## SEKCJA KTOREJ NIE MA")
    sg.SIGLA["WIDMO"] = widmo
    try:
        tekst = sg.raport("widmo")
        assert "PIECZĘĆ PUSTA" in tekst and "🚨" in tekst
    finally:
        sg.SIGLA.pop("WIDMO", None)
    assert sg.sigillum("widmo") is None, "rejestr sigli nie wrócił do stanu sprzed testu"


def test_raport_startowy_podaje_liczby_kroków():
    linia = sg.raport_startowy()
    assert "SIGLA IMPERII" in linia
    for s in sg.wszystkie():
        assert f"/{s.nazwa.lower()}" in linia


# ── UJŚCIE W HARNESSIE: skille ────────────────────────────────────────────────

def test_kazde_sigillum_ma_skill():
    """Pieczęć bez ukośnika = hasło, którego Cezar nie moze wywolac. Kierunek TWARDY."""
    z_kodu = {s.nazwa.lower() for s in sg.wszystkie()}
    z_dysku = {p.parent.name for p in SKILLE.glob("*/SKILL.md")}
    assert not (z_kodu - z_dysku), f"pieczęcie bez skilla: {z_kodu - z_dysku}"


def test_skill_bez_pieczeci_jest_skillem_ROZKAZU_nie_sierota():
    """Drugi kierunek — POLUZOWANY ŚWIADOMIE 2026-07-27, ale NIE zniesiony.

    Do odchudzenia konstytucji istniały wyłącznie skille-pieczęcie, więc równość zbiorów
    była poprawnym niezmiennikiem. Od przeniesienia rozkazów stałych (787 → 253 linie)
    istnieje DRUGA, legalna klasa: skille niosące TREŚĆ rozkazu, ładowane na żądanie.
    Zamiast skasować test, zaostrzamy pytanie: skill bez pieczęci MUSI być rozkazem —
    czyli nieść treść przeniesioną z CLAUDE.md — a nie osieroconym śmieciem.

    Bez tego rozróżnienia każdy przypadkowy katalog w `.claude/skills/` przechodziłby
    jako „no przecież to rozkaz".
    """
    z_kodu = {s.nazwa.lower() for s in sg.wszystkie()}
    for p in SKILLE.glob("*/SKILL.md"):
        if p.parent.name in z_kodu:
            continue
        tresc = p.read_text(encoding="utf-8")
        assert "przeniesione z CLAUDE.md" in tresc, (
            f"{p.parent.name}: skill bez pieczęci i bez treści rozkazu — sierota")
        assert "ROZKAZ STAŁY" in tresc, (
            f"{p.parent.name}: skill-rozkaz musi cytować rozkaz stały, nie streszczać go")


def test_skille_wolaja_wlasna_pieczec_i_nie_kopiuja_krokow():
    for s in sg.wszystkie():
        tresc = (SKILLE / s.nazwa.lower() / "SKILL.md").read_text(encoding="utf-8")
        assert f"name: {s.nazwa.lower()}" in tresc
        assert f"sigillarium {s.nazwa.lower()}" in tresc, f"{s.nazwa}: skill nie woła pieczęci"


def test_skill_nie_kopiuje_komend_bramki():
    """Skill kopiujący komendy pieczęci = druga kopia, która zgnije (dokładnie klasa,
    którą organ ma eliminować). LIMES trzyma komendy w kodzie — żadna nie może wystąpić
    dosłownie w SKILL.md. Wcześniej limes/SKILL.md wypisywał wszystkie 5 (zmierzone)."""
    for s in sg.wszystkie():
        if not s.komendy:
            continue
        tresc = (SKILLE / s.nazwa.lower() / "SKILL.md").read_text(encoding="utf-8")
        skopiowane = [k for k in s.komendy if k in tresc]
        assert not skopiowane, f"{s.nazwa}/SKILL.md kopiuje komendy zamiast wołać pieczęć: {skopiowane}"


# ── W11: upsert (wada zmierzona 2026-07-20) ───────────────────────────────────

def test_zapisz_dodaje_aktualizuje_i_rozpoznaje_brak_zmian(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert pp.zapisz("Proba", ["a"], "x", "zrodlo", plik=plik) == "dodano"
    assert pp.zapisz("Proba", ["a"], "x", "zrodlo", plik=plik) == "bez zmian"
    assert pp.zapisz("Proba", ["a", "b"], "x", "zrodlo", plik=plik) == "zaktualizowano"
    wpisy = pp.wszystkie(plik)
    assert len(wpisy) == 1, "aktualizacja nie może mnożyć wpisów"
    assert wpisy[0]["kroki"] == ["a", "b"]


def test_zapisz_nie_kasuje_nieznanych_pol(tmp_path):
    """Aktualizacja nie może po cichu wycinać pól dopisanych przez inną warstwę pamięci."""
    import json
    plik = tmp_path / "p.jsonl"
    plik.write_text(json.dumps({"nazwa": "Proba", "kroki": ["a"], "wyzwalacz": [],
                                "zrodlo": "", "data": "2026-01-01",
                                "obce_pole": "nie kasuj mnie"}, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    assert pp.zapisz("Proba", ["a", "b"], plik=plik) == "zaktualizowano"
    assert pp.pobierz("Proba", plik)["obce_pole"] == "nie kasuj mnie"


def test_zapisz_jest_atomowy_nie_zostawia_tmp(tmp_path):
    """Aktualizacja przez `.tmp` + os.replace: po sukcesie nie ma pliku tymczasowego,
    a treść jest kompletna. Chroni przed obcięciem całego pliku runbooków przy crashu."""
    plik = tmp_path / "p.jsonl"
    pp.zapisz("A", ["a"], plik=plik)
    pp.zapisz("B", ["b"], plik=plik)
    pp.zapisz("A", ["a2"], plik=plik)  # aktualizacja = pełne przepisanie
    assert not (tmp_path / "p.jsonl.tmp").exists(), "plik tymczasowy nie został posprzątany"
    nazwy = [w["nazwa"] for w in pp.wszystkie(plik)]
    assert nazwy == ["A", "B"], nazwy
    assert pp.pobierz("A", plik)["kroki"] == ["a2"]


def test_zapisz_nie_gubi_sasiednich_procedur(tmp_path):
    plik = tmp_path / "p.jsonl"
    pp.zapisz("Pierwsza", ["a"], plik=plik)
    pp.zapisz("Druga", ["b"], plik=plik)
    pp.zapisz("Pierwsza", ["a2"], plik=plik)
    nazwy = [w["nazwa"] for w in pp.wszystkie(plik)]
    assert nazwy == ["Pierwsza", "Druga"], nazwy


def test_zasiej_leczy_zmienione_ziarno(tmp_path):
    """Dawniej `dodaj` cicho pomijał istniejącą nazwę — poprawka ziarna nigdy nie docierała."""
    plik = tmp_path / "p.jsonl"
    pp.zasiej(plik=plik)
    assert pp.zasiej(plik=plik) == 0                      # idempotentne
    pp.zapisz(pp._ZIARNO[0]["nazwa"], ["stara treść"], plik=plik)
    assert pp.zasiej(plik=plik) == 1                      # ziarno leczy zgniłą treść
    assert pp.pobierz(pp._ZIARNO[0]["nazwa"], plik)["kroki"] == pp._ZIARNO[0]["kroki"]


def test_zaden_runbook_nie_kaze_claude_pushowac():
    """Regresja: rozkaz 2026-07-11 — Claude NIGDY nie pushuje (runbook łamał go pół roku)."""
    for p in pp.wszystkie():
        for krok in p.get("kroki", []):
            if "git push" in krok.lower():
                assert ("nigdy nie pushuje" in krok.lower() or "cezar" in krok.lower()), \
                    f"{p['nazwa']}: krok każe pushować — {krok}"


def test_synchronizacja_w11_przepisuje_zywe_kroki(tmp_path):
    plik = tmp_path / "p.jsonl"
    stan = sg.synchronizuj_w11(plik=plik)
    assert set(stan) == {s.nazwa for s in sg.wszystkie()}
    assert all(v == "dodano" for v in stan.values()), stan
    assert all(v == "bez zmian" for v in sg.synchronizuj_w11(plik=plik).values())
    zapisane = {w["nazwa"]: w for w in pp.wszystkie(plik)}
    for s in sg.wszystkie():
        assert zapisane[s.tytul]["kroki"] == sg.kroki(s.nazwa)


# ── NADZÓR NAD TWARDĄ LISTĄ KOMEND (2026-08-06) ──────────────────────────────
# Powód: RECOGNITOR stał w kroku 3 domknięcia od 2026-07-28 i przez dziewięć dni
# nie był częścią LIMES. Bramka wyglądała na kompletną, bo istniejące testy pytały
# WYŁĄCZNIE, czy komendy pieczęci wskazują na żywe moduły — nigdy, czy nakazana
# komenda w ogóle do pieczęci trafiła. Testy niżej pilnują DRUGIEGO kierunku.

def test_limes_wola_recognitora():
    """Regresja instancji: bramka bez RECOGNITORA nie pyta, czy recenzent widział kod.

    Zmierzone 2026-08-06: 92 ze 141 PR repozytorium (65,2%) nie miało ANI JEDNEJ
    recenzji, a `/limes` — jedyna bramka wołana przed commitem — nie zawierała
    jedynego organu, który to mierzy.
    """
    komendy = sg.SIGLA["LIMES"].komendy
    assert any("recognitor" in k for k in komendy), \
        f"LIMES nie woła RECOGNITORA — bramka nie pyta o pokrycie recenzji: {komendy}"


def test_zadna_nakazana_komenda_nie_wypadla_z_pieczeci():
    """Regresja KLASY na ŻYWEJ konstytucji: każda komenda z nadzorowanych kroków
    CLAUDE.md musi być w `komendy` pieczęci. To ten test zaświeciłby na czerwono
    2026-07-28, gdyby istniał."""
    for s in sg.wszystkie():
        assert sg.komendy_konstytucji_poza_pieczecia(s.nazwa) == [], (
            f"{s.nazwa}: konstytucja nakazuje komendy, których pieczęć nie woła — "
            f"{sg.komendy_konstytucji_poza_pieczecia(s.nazwa)}")


def test_zadna_kotwica_nadzoru_nie_jest_osierocona():
    """Nadzór po NUMERACH kroków gnije przy przenumerowaniu checklisty — a gnije
    CICHO, wyglądając na spełniony. Ten test pilnuje samego przyrządu."""
    for s in sg.wszystkie():
        assert sg.kroki_nadzoru_osierocone(s.nazwa) == [], (
            f"{s.nazwa}: nadzoruje kroki nieistniejące w konstytucji — "
            f"{sg.kroki_nadzoru_osierocone(s.nazwa)}")


def test_wykrywa_komende_wypadla_z_pieczeci():
    """Mutacja: strażnik, którego nie widziano na CZERWONO, nie jest zmierzony."""
    from dataclasses import replace
    okrojony = replace(sg.SIGLA["LIMES"],
                       komendy=[k for k in sg.SIGLA["LIMES"].komendy if "recognitor" not in k])
    with mock.patch.dict(sg.SIGLA, {"LIMES": okrojony}):
        assert sg.komendy_konstytucji_poza_pieczecia("LIMES") == [
            "python -m imperium.pretorianie.recognitor --bramka"]


def test_wykrywa_kotwice_wskazujaca_w_prozne():
    """Mutacja: krok, którego w konstytucji nie ma, musi KRZYCZEĆ, nie milczeć."""
    from dataclasses import replace
    zgnily = replace(sg.SIGLA["LIMES"], kroki_komend=("1", "3", "5b", "9z"))
    with mock.patch.dict(sg.SIGLA, {"LIMES": zgnily}):
        assert sg.kroki_nadzoru_osierocone("LIMES") == ["9z"]


def test_nadmiar_komend_w_pieczeci_jest_dozwolony():
    """GRANICA reguły: jednokierunkowa. Bramce WOLNO być ostrzejszą od checklisty
    (LIMES woła `--falsa`, którego krok 3 nie wymienia), nie wolno łagodniejszą.
    Bez tego testu ktoś „naprawiłby" regułę w obie strony i wyciął INDEX FALSORUM."""
    assert any("--falsa" in k for k in sg.SIGLA["LIMES"].komendy)
    assert sg.komendy_konstytucji_poza_pieczecia("LIMES") == []


def test_nadzor_pol_skonfigurowany_NIE_MA_PRAWA_POWSTAC():
    """WADA 3 z własnej recenzji adversarialnej (2026-08-06 → naprawa 2026-08-07).

    `sekcja_komend` bez `kroki_komend` (i odwrotnie) dawało CICHY NADZÓR: obie funkcje
    strażnika zwracały pustą listę, raport nie drukował ani jednego alarmu, oba testy
    świeciły zielono. Czyli strażnik zbudowany PRZECIWKO cichemu przeoczeniu dawał się
    skonfigurować tak, by cicho przeoczyć — wada wracała pod przykrywką lekarstwa.

    Naprawa jest KLASOWA, nie punktowa: stan półskonfigurowany nie jest wykrywany po
    fakcie, tylko przestaje być możliwy do utworzenia."""
    from dataclasses import replace

    for pole, wartosc in (("kroki_komend", ()), ("sekcja_komend", "")):
        try:
            replace(sg.SIGLA["LIMES"], **{pole: wartosc})
        except ValueError as e:
            assert "PÓŁ-SKONFIGUROWANY" in str(e)
        else:
            raise AssertionError(f"pieczęć bez `{pole}` powstała po cichu — nadzór jest martwy")

    # GRANICA: komplet i całkowity brak nadzoru są nadal legalne (większość sigli go nie ma).
    assert replace(sg.SIGLA["LIMES"], sekcja_komend="", kroki_komend=()).kroki_komend == ()
    for s in sg.wszystkie():
        assert bool(s.sekcja_komend) == bool(s.kroki_komend), f"{s.nazwa}: nadzór półskonfigurowany"


def test_komendy_w_tekscie_pomija_to_co_nie_jest_poleceniem():
    """Krok 3 cytuje w grzbietach także `/code-review` (skill harnessa) i
    `ksiega_wad_kodu` (nazwa ledgera) — żadne z nich nie jest komendą powłoki."""
    krok = ("3. `/code-review` na diffie + `python narzedzia/skan_wad_kodu.py` na "
            "zmienionych plikach. Nowe wady → Księga Wad (`ksiega_wad_kodu`).")
    assert sg._komendy_w_tekscie(krok) == ["python narzedzia/skan_wad_kodu.py"]
