"""
Testy Prawa XXI — Protokół Spójności.
Silnik audytu (narzedzia/audyt_spojnosci.py) MUSI być zielony w każdej sesji.
"""

import os
import pathlib
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def test_audyt_spojnosci_zielony():
    """Prawo XXI: pełny audyt spójności kodu z dokumentacją bez rozbieżności."""
    from narzedzia.audyt_spojnosci import audyt
    wynik = audyt()
    bledy, _info = wynik if isinstance(wynik, tuple) else (wynik, [])
    assert not bledy, "Audyt spójności (Prawo XXI) wykrył rozbieżności:\n" + "\n".join(bledy)


def test_audyt_wykrywa_rozbieznosc():
    """Audyt MUSI faktycznie łapać błąd — inaczej jest bezużyteczny (negatywny test)."""
    import narzedzia.audyt_spojnosci as a
    orig = a._czytaj

    def fake(p):
        t = orig(p)
        if p == "README.md":
            # README podaje liczbę neuronów w bloku W15 (<!-- LICZBA:neurony -->N<!-- /LICZBA -->);
            # podmieniamy N w bloku, by W3 (tolerujący oba formaty) wykrył rozbieżność.
            return re.sub(r"(LICZBA:neurony -->)\d+", r"\g<1>999", t)
        return t

    a._czytaj = fake
    try:
        bledy, _ = a.audyt()
        assert any("README" in b for b in bledy), "Audyt NIE wykrył wstrzykniętej rozbieżności"
    finally:
        a._czytaj = orig


def test_audyt_wykrywa_brak_stan_na():
    """W6: brak pola 'Stan na:' w README MUSI być błędem (nie ciche przejście)."""
    import narzedzia.audyt_spojnosci as a
    orig = a._czytaj

    def fake(p):
        t = orig(p)
        if p == "README.md":
            return t.replace("Stan na:", "Pole usuniete:")
        return t

    a._czytaj = fake
    try:
        bledy, _ = a.audyt()
        assert any("W6" in b and "README" in b and "Stan na" in b for b in bledy), \
            "Audyt NIE wykrył braku pola 'Stan na:'"
    finally:
        a._czytaj = orig


def test_audyt_akceptuje_stan_na_w_markdown():
    """W6: 'Stan na:' otoczone markdown (**...**) musi być rozpoznane (nie fałszywy alarm)."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a.audyt()
    w6_daty = [b for b in bledy if "W6" in b and "Stan na" in b]
    assert not w6_daty, f"Fałszywy alarm W6 mimo poprawnej daty: {w6_daty}"


def test_audyt_w9_wykrywa_obcy_klucz_strategii():
    """W9: klucz neuronu cytowany w katalogu, którego strategia nie ma w kodzie = błąd."""
    import narzedzia.audyt_spojnosci as a
    orig = a._czytaj

    def fake(p):
        t = orig(p)
        if p == "docs/KATALOG_STRATEGII.md":
            # wstrzyknij obcy klucz w blok zaimplementowanej strategii
            return t.replace("### XII-TR-001",
                             "### XII-TR-001\n- `OC-99` obcy klucz testowy", 1)
        return t

    a._czytaj = fake
    try:
        bledy, _ = a.audyt()
        assert any("W9" in b and "OC-99" in b for b in bledy), \
            "W9 nie wykrył obcego klucza w katalogu strategii"
    finally:
        a._czytaj = orig


def test_audyt_w9_zielony_na_realnym_katalogu():
    """W9: realny katalog NIE może mieć obcych kluczy w zaimplementowanych strategiach."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a.audyt()
    w9 = [b for b in bledy if "W9" in b]
    assert not w9, f"Rozjazd katalog↔kod w strategiach: {w9}"


def test_audyt_w7_ignoruje_zewnetrzne_url():
    """W7: zewnętrzne URL-e (np. www.mdpi.com zawierający '.md' w domenie) NIE są martwymi linkami."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a.audyt()
    # WIZJONER.md zawiera realne linki http(s) z '.md' w domenie (mdpi.com itd.)
    w7_url = [b for b in bledy if "W7" in b and "Martwe linki" in b
              and ("http" in b or "mdpi" in b)]
    assert not w7_url, f"W7 fałszywie oznaczył zewnętrzne URL-e jako martwe linki: {w7_url}"


def test_audyt_w12_zywotnosc_glosu_zielona():
    """W12 (Prawo XV): żaden aktywny neuron spoza allowlisty adapterowej nie milczy."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a.audyt()
    w12 = [b for b in bledy if "W12" in b]
    assert not w12, f"W12 wykrył martwy głos (regresja Prawa XV): {w12}"


def test_audyt_w12_raportuje_neurony_adapterowe():
    """W12: 5 neuronów zależnych od adapterów raportowanych jako ⚠️ info (nie błąd)."""
    import narzedzia.audyt_spojnosci as a
    _bledy, info = a.audyt()
    adaptery = [i for i in info if "Prawo XV" in i and "adaptery" in i]
    assert adaptery, "W12 nie zaraportował neuronów czekających na adaptery"
    # PSY-01..04 + V-03 muszą być wymienione
    tekst = " ".join(adaptery)
    for k in ("PSY-01", "PSY-02", "PSY-03", "PSY-04", "V-03"):
        assert k in tekst, f"W12 info nie wymienia {k}"


def test_audyt_w12_dowod_allowlisty():
    """W12 (Prawo I): każdy neuron adapterowy OŻYWA, gdy nakarmić go danymi adaptera."""
    import narzedzia.audyt_spojnosci as a
    from imperium.legiony.rejestr import wszystkie_neurony
    by = {n.KLUCZ: n for n in wszystkie_neurony()}
    for klucz, trigger in a.WERYFIKACJA_ADAPTEROW.items():
        n = by.get(klucz)
        assert n is not None, f"Neuron {klucz} z WERYFIKACJA_ADAPTEROW nie istnieje"
        sig = n.interpretuj(dict(trigger))
        zywy = (sig.kierunek != "NEUTRAL" or sig.pewnosc > 0
                or getattr(sig, "pewnosc_przeciwnika", 0) > 0)
        assert zywy, f"{klucz} milczy MIMO danych adaptera {trigger} — realny bug"


def test_audyt_w12_wykrywa_martwy_glos():
    """W12 negatywny: usunięcie neuronu z allowlisty adapterowej → błąd blokujący."""
    import narzedzia.audyt_spojnosci as a
    orig = dict(a.NEURONY_ZALEZNE_OD_ADAPTEROW)
    try:
        # PSY-01 milczy bez adaptera; bez wpisu w allowliście MUSI dać błąd W12
        a.NEURONY_ZALEZNE_OD_ADAPTEROW.pop("PSY-01", None)
        bledy, _ = a.audyt()
        assert any("W12" in b and "PSY-01" in b for b in bledy), \
            "W12 nie wykrył martwego głosu po usunięciu z allowlisty"
    finally:
        a.NEURONY_ZALEZNE_OD_ADAPTEROW.clear()
        a.NEURONY_ZALEZNE_OD_ADAPTEROW.update(orig)


def test_audyt_w14_mapa_kluczy_kompletna():
    """W14 (rozkaz Cezara): MAPA_KLUCZY zawiera wszystkie klucze z żywego kodu."""
    import narzedzia.audyt_spojnosci as a
    from imperium.legiony.rejestr import wszystkie_neurony
    bledy, info = a._warstwa_14_wszystkie_dokumenty(wszystkie_neurony())
    w14 = [b for b in bledy if "W14" in b]
    assert not w14, f"W14 wykrył dryf dokumentacji: {w14}"
    assert any("kluczy kodu pokryte" in i for i in info)
    assert any("plików .md" in i for i in info)


def test_audyt_w14_wykrywa_brakujacy_klucz():
    """W14 negatywny: neuron, którego klucza nie ma w MAPA_KLUCZY → błąd blokujący."""
    import narzedzia.audyt_spojnosci as a

    class _FakeNeuron:
        KLUCZ = "ZZZ-99"  # klucz nieistniejący w MAPA_KLUCZY

    bledy, _ = a._warstwa_14_wszystkie_dokumenty([_FakeNeuron()])
    assert any("W14" in b and "ZZZ-99" in b for b in bledy), \
        "W14 nie wykrył braku klucza w MAPA_KLUCZY"


# ── WARSTWA 16: API-WIDMA (łowca ścieżek do nieistniejących plików) ──────────
_W16_REAL = {"imperium/istnieje.py", "narzedzia/audyt_spojnosci.py"}


def test_audyt_w16_zielony_na_realnym_korpusie():
    """W16 na żywym repo: każda ścieżka .py w żywych docs istnieje (po naprawie INDEKS)."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_16_api_widma()
    assert not bledy, f"W16 wykrył API-widma w żywych dokumentach: {bledy}"
    assert any("W16" in i for i in info)


def test_audyt_w16_wykrywa_widmo_w_prozie():
    """Granica: ścieżka do NIEISTNIEJĄCEGO pliku w zwykłej linii = widmo."""
    import narzedzia.audyt_spojnosci as a
    tresc = "Uruchom `imperium/koloseum/valhalla.py` aby wystartować.\n"
    w = a._w16_widma_w_tresci(tresc, _W16_REAL)
    assert w == [("imperium/koloseum/valhalla.py", 1)], w


def test_audyt_w16_plik_istniejacy_nie_jest_widmem():
    """Granica: ścieżka do REALNEGO pliku = brak alarmu."""
    import narzedzia.audyt_spojnosci as a
    tresc = "Silnik: `imperium/istnieje.py` — działa.\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_cudze_repo_nie_jest_widmem():
    """Granica: `↗` oznacza plik z CUDZEGO repozytorium — istnieje, tylko nie u nas.

    Dodane po trzecim talarze Cezara (2026-07-29). Meldunki zwiadu cytują ścieżki
    obcych projektów; bez tego pojęcia audyt zmuszał do wyboru między fałszywym
    alarmem a oznaczeniem cudzego KODU jako „plan", czyli fałszywym opisem.
    """
    import narzedzia.audyt_spojnosci as a
    tresc = "↗ `ml4t/backtest` → `tests/contracts/test_ledger_invariants.py` `[KOD]`\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_marker_cudzego_repo_NIE_zacisza_calej_linii():
    """Granica: `↗` cichnie SWÓJ segment, nie cały wiersz.

    Wada znaleziona recenzją tego samego dnia: wersja liniowa ukrywała realne widmo
    NASZEGO pliku stojące obok ścieżki obcej, a porównanie „u nich vs u nas"
    w jednym wierszu to naturalny styl meldunków zwiadu.
    """
    import narzedzia.audyt_spojnosci as a
    tresc = "↗ `skfolio/_hrp.py` — a u nas robi to `imperium/nie_istnieje_wcale.py`\n"
    znalezione = a._w16_widma_w_tresci(tresc, _W16_REAL)
    assert [s for s, _ in znalezione] == ["imperium/nie_istnieje_wcale.py"], znalezione


def test_audyt_w16_marker_w_komorce_tabeli_zacisza_tylko_ja():
    """Granica: cudza ścieżka w komórce tabeli cichnie, wiersz nie zapala alarmu."""
    import narzedzia.audyt_spojnosci as a
    tresc = "| 🥇 | testy | ↗ `ml4t/backtest` → `tests/contracts/x.py` `[KOD]` | daje |\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_bez_markera_cudze_repo_JEST_widmem():
    """Kontrola negatywna: ta sama ścieżka BEZ `↗` musi nadal zapalić alarm.

    Gdyby marker był zbędny, supresja tłumiłaby wszystko i W16 przestałaby chronić.
    """
    import narzedzia.audyt_spojnosci as a
    tresc = "`ml4t/backtest` → `tests/contracts/test_ledger_invariants.py`\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) != []


def test_audyt_w16_blok_python_jest_przykladem():
    """Granica: ścieżka w bloku ```python (kod przykładowy) NIE jest twierdzeniem."""
    import narzedzia.audyt_spojnosci as a
    tresc = "```python\n# imperium/cesarz/doradcy/vulcan.py\nclass X: ...\n```\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_blok_bash_nie_jest_przykladem():
    """Granica dopełniająca: ta sama ścieżka w bloku ```bash = twierdzenie → widmo."""
    import narzedzia.audyt_spojnosci as a
    tresc = "```bash\npython imperium/koloseum/valhalla.py\n```\n"
    w = a._w16_widma_w_tresci(tresc, _W16_REAL)
    assert w == [("imperium/koloseum/valhalla.py", 2)], w


def test_audyt_w16_marker_planu_cisza():
    """Granica: 'do zbudowania' w linii → plan, nie widmo (bez fałszywego alarmu)."""
    import narzedzia.audyt_spojnosci as a
    tresc = "A/B: `narzedzia/ab_widmo.py` (do zbudowania).\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_negacja_cisza():
    """Granica: negacja 'NIGDY nie istniał' → nie widmo (przypadek paper_trading_live)."""
    import narzedzia.audyt_spojnosci as a
    tresc = "`narzedzia/paper_trading_live.py` — pliku, który NIGDY nie istniał.\n"
    assert a._w16_widma_w_tresci(tresc, _W16_REAL) == []


def test_audyt_w16_marker_nie_lapie_wewnatrz_slowa():
    """Granica (recenzja 2026-07-18): 'todo' w 'metodologia' i 'wizja' w 'dywizja'
    NIE mogą uciszać — inaczej prawdziwe widmo na takiej linii ginie (false-negative)."""
    import narzedzia.audyt_spojnosci as a
    t1 = "Metodologia w `imperium/koloseum/valhalla.py` opisana niżej.\n"
    assert a._w16_widma_w_tresci(t1, _W16_REAL) == [("imperium/koloseum/valhalla.py", 1)], t1
    t2 = "Dywizja III uruchamia `imperium/koloseum/valhalla.py`.\n"
    assert a._w16_widma_w_tresci(t2, _W16_REAL) == [("imperium/koloseum/valhalla.py", 1)], t2


# ── Warstwa 18: LEX TALIONIS — dług honorowy zatrzymuje commit (bramka TWARDA) ──

def test_w18_dlug_honorowy_gryzie(tmp_path):
    """DOWÓD, ŻE BRAMKA GRYZIE: sztuczny dług → czerwień, po CORONIE → zieleń.

    Bez tego testu Warstwa 18 byłaby deklaracją. Pierwsza wersja dowodu podmieniała
    stałą `codex_notarum.LEDGER` i po cichu czytała PRAWDZIWY ledger — bo `bilans(sciezka=LEDGER)`
    wiąże domyślny argument w chwili definicji. Meldowała zieleń dla sztucznego długu,
    czyli sam dowód był mechanizmem, który przy awarii wygląda na sprawny. Stąd jawna ścieżka.
    """
    from imperium.biblioteki import codex_notarum as cn
    from narzedzia.audyt_spojnosci import _warstwa_18_dlug_honorowy as w18

    ledger = tmp_path / "notarum.jsonl"

    assert w18(ledger)[0] == []                      # pusty ledger — brak długu

    nota = cn.dodaj_nota(opis="Sztuczny błąd", kategoria="test",
                         zatwierdzenie="dowód, że bramka gryzie", sesja="test",
                         sciezka=ledger)
    bledy, info = w18(ledger)
    assert len(bledy) == 1 and "DŁUG HONOROWY" in bledy[0]   # NOTA bez CORONY → czerwień
    assert info == []

    cn.dodaj_corona(opis="Sztuczny unikat", kategoria="test",
                    zatwierdzenie="dowód spłaty", sesja="test",
                    splaca=nota, sciezka=ledger)
    bledy, info = w18(ledger)
    assert bledy == [] and info                       # spłacone → zieleń


def test_w18_corona_nie_splacajaca_nie_zamyka_dlugu(tmp_path):
    """Granica LEX TALIONIS: „oko za oko musi mieć oko" — CORONA bez `splaca`
    NIE zamyka długu, inaczej dowolny laur kasowałby dowolny błąd."""
    from imperium.biblioteki import codex_notarum as cn
    from narzedzia.audyt_spojnosci import _warstwa_18_dlug_honorowy as w18

    ledger = tmp_path / "notarum.jsonl"
    cn.dodaj_nota(opis="Błąd nierozliczony", kategoria="test",
                  zatwierdzenie="dowód", sesja="test", sciezka=ledger)
    cn.dodaj_corona(opis="Laur nie wskazujący noty", kategoria="test",
                    zatwierdzenie="dowód", sesja="test", sciezka=ledger)
    assert len(w18(ledger)[0]) == 1                   # dług NADAL otwarty


def test_w18_awaria_ledgera_nie_wywraca_audytu(tmp_path):
    """Uszkodzony ledger → błąd warstwy, nie wyjątek walący cały audyt."""
    from narzedzia.audyt_spojnosci import _warstwa_18_dlug_honorowy as w18
    zly = tmp_path / "zepsuty.jsonl"
    zly.write_text("{to nie json\n", encoding="utf-8")
    bledy, _ = w18(zly)
    assert isinstance(bledy, list)                    # kontrakt zachowany, brak wyjątku


# ── WARSTWA 19: PARYTET DAT (frontmatter vs nagłówek) ────────────────────────

def test_audyt_w19_zielony_na_realnym_korpusie():
    """W19 na żywym repo: żaden dokument nie deklaruje dwóch różnych dat 'stan na'."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_19_parytet_dat()
    assert not bledy, f"W19 wykrył rozjazd dat: {bledy}"
    assert any("W19" in i for i in info)


def test_audyt_w19_lapie_rozjazd_dwoch_dat(monkeypatch, tmp_path):
    """GRANICA: frontmatter mówi jedno, nagłówek drugie → alarm.

    Dokładnie przypadek z recenzji 2026-07-26: README miał `stan_na: 2026-07-19`
    i „Stan na: 2026-07-26". Warstwa 6 czytała tylko nagłówek, Tabularium tylko
    frontmatter, więc audyt meldował harmonię przy jawnej sprzeczności.
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia import tabularium as tab
    plik = tmp_path / "DOK.md"
    plik.write_text("---\nstan_na: 2026-07-19\n---\n> **Stan na:** 2026-07-26\ntreść\n",
                    encoding="utf-8")
    monkeypatch.setattr(tab, "ROOT", str(tmp_path))
    monkeypatch.setattr(tab, "zbierz_dokumenty", lambda: [("DOK.md", {"stan_na": "2026-07-19"})])
    bledy, _ = a._warstwa_19_parytet_dat()
    assert len(bledy) == 1 and "DOK.md" in bledy[0]


def test_audyt_w19_data_w_prozie_nie_jest_deklaracja(monkeypatch, tmp_path):
    """GRANICA (fałszywy alarm złapany w samo-recenzji przed commitem): fraza „Stan na:"
    zacytowana GŁĘBOKO w treści to nie deklaracja dokumentu.

    Pierwsza wersja W19 skanowała cały plik i oskarżyła LOG_ZMIAN o rozjazd, bo w jednym
    wpisie changelogu cytowano cudzą datę. Warstwa pilnująca prawdy nie ma prawa
    produkować nieprawdy — zasięg to nagłówek dokumentu.
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia import tabularium as tab
    plik = tmp_path / "LOG.md"
    plik.write_text("---\nstan_na: 2026-07-26\n---\n"
                    + "wypełniacz\n" * 40
                    + "Naprawiono: README ze „Stan na: 2026-07-15\" było nieaktualne.\n",
                    encoding="utf-8")
    monkeypatch.setattr(tab, "ROOT", str(tmp_path))
    monkeypatch.setattr(tab, "zbierz_dokumenty", lambda: [("LOG.md", {"stan_na": "2026-07-26"})])
    bledy, _ = a._warstwa_19_parytet_dat()
    assert bledy == [], f"cytat w prozie nie może być alarmem: {bledy}"


# ── WARSTWA 20: KATALOG INDEKS NIETKNIĘTY RĘKĄ ───────────────────────────────

def test_audyt_w20_zielony_na_realnym_indeksie():
    """W20 na żywym repo: katalog w INDEKS = to, co wypluwa Tabularium."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_20_katalog_nietkniety()
    assert not bledy, f"W20 wykrył ręczną edycję katalogu: {bledy}"
    assert any("W20" in i for i in info)


def test_audyt_w20_lapie_ZDUBLOWANY_znacznik(monkeypatch, tmp_path):
    """Zdublowany znacznik START zostawia sekcję poza kontrolą, a bramka mówiła „zgodne ✅".

    Zarzut cubica (PR #134, P2) potwierdzony na kodzie: sprawdzana była OBECNOŚĆ znaczników,
    a porównanie bierze treść między PIERWSZĄ parą (`split(..., 1)[1]`). Drugi blok był
    niewidzialny — klasa „wąski zasięg bramki produkujący fałszywy spokój".
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia.tabularium import ZNACZNIK_KONIEC, ZNACZNIK_START
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "INDEKS_IMPERIUM.md").write_text(
        f"# Indeks\n{ZNACZNIK_START}\n| a |\n{ZNACZNIK_KONIEC}\n"
        f"{ZNACZNIK_START}\n| duplikat poza kontrolą |\n{ZNACZNIK_KONIEC}\n",
        encoding="utf-8")
    # W20 bierze korzeń z `tabularium.ROOT` w chwili wywołania — podmieniamy źródło, nie kopię.
    import narzedzia.tabularium as t
    monkeypatch.setattr(t, "ROOT", str(tmp_path))
    bledy, _ = a._warstwa_20_katalog_nietkniety()
    assert bledy, "zdublowany znacznik przeszedł bez alarmu"
    assert "2×" in bledy[0] and "W20" in bledy[0]


def test_audyt_w20_lapie_wiersz_dopisany_recznie(monkeypatch):
    """GRANICA: jeden wiersz dopisany ręcznie do sekcji generowanej → alarm.

    Przypadek z recenzji 2026-07-26: wpis o kategorii DISCIPLINA wstawiono do sekcji
    CONSILIUM. Warstwa 7 pilnowała samej OBECNOŚCI dokumentu w INDEKS, nigdy MIEJSCA,
    więc ręczna edycja żyła aż do pierwszej regeneracji.
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia import tabularium as tab
    prawdziwy = tab.katalog_md()
    monkeypatch.setattr(tab, "katalog_md",
                        lambda: prawdziwy.replace("### DISCIPLINA",
                                                  "| `docs/PODRZUCONY.md` | widmo | — | 2026-01-01 |\n### DISCIPLINA",
                                                  1))
    bledy, _ = a._warstwa_20_katalog_nietkniety()
    assert len(bledy) == 1 and "rozjechał się z generatorem" in bledy[0]


def test_audyt_w20_data_spisu_nie_wywoluje_alarmu(monkeypatch):
    """GRANICA: linia „Ostatni spis: <data>" zmienia się CODZIENNIE i musi być pomijana.

    Bez tego wyłączenia audyt żądałby przepisania katalogu każdego dnia — dokładnie
    ten fałszywy alarm naprawiliśmy już raz w Warstwie 6 (porównanie z `date.today()`).
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia import tabularium as tab
    prawdziwy = tab.katalog_md()
    monkeypatch.setattr(tab, "katalog_md",
                        lambda: prawdziwy.replace("Ostatni spis: ", "Ostatni spis: 1999-01-01 zamiast "))
    bledy, _ = a._warstwa_20_katalog_nietkniety()
    assert bledy == [], "zmiana samej daty spisu nie jest rozjazdem katalogu"


# ── WARSTWA 21: WYZWALACZE ROZKAZOW OSIAGALNE ────────────────────────────────

def test_audyt_w21_zielony_na_realnej_konstytucji():
    """W21 na żywym repo: każdy `/skill` cytowany w CLAUDE.md istnieje na dysku."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_21_wyzwalacze_rozkazow()
    assert not bledy, f"W21 wykrył nieosiągalne rozkazy: {bledy}"
    assert any("W21" in i for i in info)


def test_audyt_w21_lapie_rozkaz_bez_skilla(monkeypatch, tmp_path):
    """GRANICA: konstytucja obiecuje `/widmo`, katalog skilli go nie ma → alarm.

    Po odchudzeniu konstytucji (787→253 linie) rozkaz odesłany do nieistniejącego skilla
    jest NIEOSIĄGALNY — gorzej niż gruby CLAUDE.md, bo Architekt nie wie, że go zgubił.
    """
    import narzedzia.audyt_spojnosci as a
    (tmp_path / ".claude" / "skills" / "realny").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "realny" / "SKILL.md").write_text("x", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(
        "- rozkaz A: **`/realny`**\n- rozkaz B: **`/widmo`**\n", encoding="utf-8")
    monkeypatch.setattr(a, "ROOT", str(tmp_path))
    bledy, _ = a._warstwa_21_wyzwalacze_rozkazow()
    assert len(bledy) == 1 and "widmo" in bledy[0] and "realny" not in bledy[0]


def test_audyt_w21_ukosnik_w_prozie_nie_jest_obietnica(monkeypatch, tmp_path):
    """GRANICA (ta sama pułapka co w W19): `/cos` w zwykłym zdaniu to nie wyzwalacz.

    Konstytucja pisze m.in. „wejście/wyjście z pozycji" i ścieżki plików. Gdyby warstwa
    liczyła każdy ukośnik, produkowałaby własne fałszywe alarmy.
    """
    import narzedzia.audyt_spojnosci as a
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text(
        "zmiana wejścia/wyjścia z pozycji; plik narzedzia/audyt_spojnosci.py; `/goly`\n",
        encoding="utf-8")
    monkeypatch.setattr(a, "ROOT", str(tmp_path))
    bledy, _ = a._warstwa_21_wyzwalacze_rozkazow()
    assert bledy == [], f"proza nie może być alarmem: {bledy}"


# ── WARSTWA 22: JEDEN KATALOG DOKUMENTOW ─────────────────────────────────────

def _dok(katalog, nazwa, ile_wierszy):
    """Dokument z tabelą o `ile_wierszy` pozycjach wskazujących na inne dokumenty."""
    wiersze = ["| Plik | Temat |", "|---|---|"]
    wiersze += [f"| [D{i}.md](D{i}.md) | opis {i} |" for i in range(ile_wierszy)]
    (katalog / nazwa).write_text("\n".join(wiersze) + "\n", encoding="utf-8")


def test_audyt_w22_zielony_na_realnym_korpusie():
    """W22 na żywym repo: po decyzji C żaden dokument nie konkuruje z INDEKSEM."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_22_jeden_katalog()
    assert not bledy, f"W22 wykrył drugi katalog: {bledy}"
    assert any("W22" in i or "Jeden katalog" in i for i in info)


def test_audyt_w22_lapie_odrodzony_reczny_spis(tmp_path):
    """GRANICA: dokument urósł do 5 wierszy katalogu → alarm (próg zmierzony)."""
    import narzedzia.audyt_spojnosci as a
    _dok(tmp_path, "README.md", 5)
    bledy, _ = a._warstwa_22_jeden_katalog(katalog_docs=str(tmp_path))
    assert len(bledy) == 1 and "README.md" in bledy[0] and "W22" in bledy[0]


def test_audyt_w22_kilka_odnosnikow_to_nie_katalog(tmp_path):
    """GRANICA DRUGA STRONA: 4 wiersze (tuż pod progiem) to nawigacja, nie spis.

    Zero byłoby fałszywym alarmem — README ma prawo wskazać INDEKS, konstytucję i ZASADY.
    """
    import narzedzia.audyt_spojnosci as a
    _dok(tmp_path, "README.md", 4)
    bledy, _ = a._warstwa_22_jeden_katalog(katalog_docs=str(tmp_path))
    assert bledy == [], f"kilka odnośników nie może być alarmem: {bledy}"


def test_audyt_w22_indeks_jest_zwolniony(tmp_path):
    """INDEKS_IMPERIUM to JEDYNY prawowity katalog — pilnuje go W20, nie W22."""
    import narzedzia.audyt_spojnosci as a
    _dok(tmp_path, "INDEKS_IMPERIUM.md", 73)
    bledy, _ = a._warstwa_22_jeden_katalog(katalog_docs=str(tmp_path))
    assert bledy == [], f"generowany katalog nie może wywoływać alarmu: {bledy}"


def test_audyt_w22_wzmianka_w_dalszej_kolumnie_to_opis(tmp_path):
    """GRANICA: `.md` w kolumnie OPISU nie czyni z wiersza pozycji spisu.

    Ta sama pułapka co w W19 (zasięg): warstwa pilnująca cudzej prawdy nie ma prawa
    liczyć każdej wzmianki o pliku jako wpisu katalogowego.
    """
    import narzedzia.audyt_spojnosci as a
    wiersze = ["| Warstwa | Co robi |", "|---|---|"]
    wiersze += [f"| W{i} | porównuje z `INDEKS_IMPERIUM.md` |" for i in range(9)]
    (tmp_path / "OPIS.md").write_text("\n".join(wiersze) + "\n", encoding="utf-8")
    bledy, _ = a._warstwa_22_jeden_katalog(katalog_docs=str(tmp_path))
    assert bledy == [], f"opis w drugiej kolumnie to nie katalog: {bledy}"


def test_audyt_w22_zasieg_obejmuje_dokumenty_spoza_docs():
    """ZASIĘG (pytanie osobne od logiki): warstwa widzi też żywe dokumenty spoza `docs/`.

    Nawracająca klasa Imperium: bramka o wąskim zasięgu daje fałszywy spokój (W11 pilnowała
    1 katalogu z 11). Katalog może odrodzić się w `imperium/README.md` tak samo jak w `docs/`.
    """
    import narzedzia.audyt_spojnosci as a
    from narzedzia.tabularium import zbierz_dokumenty
    zadeklarowane = [w for w, _ in zbierz_dokumenty()]
    poza = [w for w in zadeklarowane if pathlib.PurePath(w).parts[0] != "docs"]
    assert poza, "Tabularium przestało widzieć dokumenty spoza docs/ — zasięg W22 by się zawęził"
    oczekiwane = len([w for w in zadeklarowane
                      if os.path.basename(w) != "INDEKS_IMPERIUM.md"])
    _, info = a._warstwa_22_jeden_katalog()
    zbadane = int(re.search(r"\(W22\): (\d+) dokument", info[0]).group(1))
    assert zbadane == oczekiwane, (
        f"W22 zbadała {zbadane} z {oczekiwane} zadeklarowanych dokumentów — zasięg zawężony "
        f"(pierwsza wersja tego testu miała luźny próg i PRZEŻYŁA mutację zawężenia do docs/)")


# ── W23: liczba o CAŁOŚCI roju pisana prozą (luka znaleziona mutacją 2026-07-29) ──

def test_w23_zywe_repo_bez_falszywych_sum():
    """W23 na żywym repo: żaden żywy dokument nie twierdzi prozą nieprawdy o rozmiarze roju."""
    from narzedzia.audyt_spojnosci import _warstwa_23_liczby_w_prozie

    bledy, info = _warstwa_23_liczby_w_prozie()
    assert not bledy, f"W23 wykrył fałszywe sumy w prozie: {bledy}"
    assert any("W23" in i or "prozie" in i for i in info)


def test_w23_lapie_falszywa_sume_w_prozie(monkeypatch, tmp_path=None):
    """
    MUTACJA — dowód, że warstwa broni. Przed jej dodaniem to samo zdanie dawało exit 0,
    a identyczna liczba w znaczniku LICZBA zapalała czerwień: W15 broniła POLA, nie prawdy.
    """
    import narzedzia.audyt_spojnosci as a
    import narzedzia.tabularium as t

    tresc = "kategoria: TABULA\n\nImperium ma 421 neuronow.\n"
    # Podmieniamy źródła: jeden dokument o znanej treści + znana prawda z kodu.
    monkeypatch.setattr(t, "zbierz_dokumenty", lambda: [("fikcja.md", {})])
    monkeypatch.setattr(t, "wartosci_z_kodu", lambda: {"neurony": 87, "zwiadowcy": 15})
    monkeypatch.setattr(a.os.path, "join", lambda *cz: "fikcja.md")

    import builtins
    prawdziwy_open = builtins.open

    def fake_open(plik, *a_, **kw):
        if plik == "fikcja.md":
            import io
            return io.StringIO(tresc)
        return prawdziwy_open(plik, *a_, **kw)

    monkeypatch.setattr(builtins, "open", fake_open)
    bledy, info = a._warstwa_23_liczby_w_prozie()
    assert len(bledy) == 1 and "421" in bledy[0] and "87" in bledy[0]
    assert not info


def test_w23_milczy_na_liczbach_czastkowych(monkeypatch):
    """GRANICA: „11 neuronów kategorii M" to PRAWDA cząstkowa — alarm byłby tapetą."""
    import builtins
    import io

    import narzedzia.audyt_spojnosci as a
    import narzedzia.tabularium as t

    tresc = "kategoria: TABULA\n\nW kategorii M pracuje 11 neuronow, a w R — 5 zwiadowcow.\n"
    monkeypatch.setattr(t, "zbierz_dokumenty", lambda: [("fikcja.md", {})])
    monkeypatch.setattr(t, "wartosci_z_kodu", lambda: {"neurony": 87, "zwiadowcy": 15})
    monkeypatch.setattr(a.os.path, "join", lambda *cz: "fikcja.md")
    prawdziwy_open = builtins.open
    monkeypatch.setattr(builtins, "open",
                        lambda p, *a_, **kw: io.StringIO(tresc) if p == "fikcja.md"
                        else prawdziwy_open(p, *a_, **kw))
    bledy, _ = a._warstwa_23_liczby_w_prozie()
    assert bledy == []


def test_w23_pomija_dokumenty_acta(monkeypatch):
    """Historii NIE przepisujemy (Prawo I): ACTA mają prawo do liczb swojego czasu."""
    import builtins
    import io

    import narzedzia.audyt_spojnosci as a
    import narzedzia.tabularium as t

    tresc = "kategoria: ACTA\ntyp: acta\n\nImperium ma 421 neuronow.\n"
    monkeypatch.setattr(t, "zbierz_dokumenty", lambda: [("kronika.md", {})])
    monkeypatch.setattr(t, "wartosci_z_kodu", lambda: {"neurony": 87})
    monkeypatch.setattr(a.os.path, "join", lambda *cz: "kronika.md")
    prawdziwy_open = builtins.open
    monkeypatch.setattr(builtins, "open",
                        lambda p, *a_, **kw: io.StringIO(tresc) if p == "kronika.md"
                        else prawdziwy_open(p, *a_, **kw))
    bledy, _ = a._warstwa_23_liczby_w_prozie()
    assert bledy == []


# ── WARSTWA 24: hooki wykonywalne (recenzja cubic PR #138, S1) ──────────────────

def _settings(tmp_path, komenda):
    import json
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": komenda}]}]}}), encoding="utf-8")
    return str(p)


def test_audyt_w24_brak_settings_to_BLAD_nie_zielone(tmp_path):
    """Brak `.claude/settings.json` to WYŁĄCZONA OBRONA, nie „nie ma czego pilnować".

    Naprawa P1 z recenzji cubic PR #139. Poprzednia wersja zwracała na tej ścieżce
    `([], [info])`, czyli **zero błędów** — audyt świecił zielono dla repozytorium,
    w którym skasowano plik rejestrujący CUSTOS LIMINIS, VIGIL, EXACTOR i sync pamięci.
    Bramka zatwierdzałaby wtedy stan bez żadnego strażnika. To ta sama klasa, którą
    W24 miała ścigać: hooki martwe, a nikt nie krzyczy. Cisza o braku obrony JEST alarmem.
    """
    import narzedzia.audyt_spojnosci as a

    bledy, info = a._warstwa_24_hooki_wykonywalne(
        sciezka_settings=str(tmp_path / "nie-ma-takiego-pliku.json"))
    assert bledy, "brak settings.json MUSI być błędem audytu"
    assert "W24" in bledy[0]
    assert not info, "to nie jest informacja, to jest zarzut"


def test_audyt_w24_zielony_na_realnych_hookach():
    """Stan faktyczny repozytorium — wszystkie hooki z settings.json mają 100755."""
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_24_hooki_wykonywalne()
    assert bledy == [], bledy
    assert info and "W24" in info[0]


def test_audyt_w24_lapie_hook_bez_bitu(tmp_path):
    """Sedno: hook bez +x konczy sie na Unixie 'Permission denied' PRZED wejsciem do
    organu, wiec milczy nieodroznialnie od hooka, ktory przepuscil."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a._warstwa_24_hooki_wykonywalne(
        sciezka_settings=_settings(tmp_path, "$CLAUDE_PROJECT_DIR/.claude/hooks/stop.sh"),
        tryby_gita={".claude/hooks/stop.sh": "100644"})
    assert len(bledy) == 1 and "bitu wykonywalnosci" in bledy[0].replace("ś", "s")


def test_audyt_w24_bit_obecny_to_cisza(tmp_path):
    import narzedzia.audyt_spojnosci as a
    bledy, info = a._warstwa_24_hooki_wykonywalne(
        sciezka_settings=_settings(tmp_path, "$CLAUDE_PROJECT_DIR/.claude/hooks/stop.sh"),
        tryby_gita={".claude/hooks/stop.sh": "100755"})
    assert bledy == [] and info


def test_audyt_w24_hook_niesledzony_przez_git_to_blad(tmp_path):
    """Plik spoza gita nie pojawi sie na innej maszynie — cisza byłaby fałszywym spokojem."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a._warstwa_24_hooki_wykonywalne(
        sciezka_settings=_settings(tmp_path, "$CLAUDE_PROJECT_DIR/.claude/hooks/duch.sh"),
        tryby_gita={".claude/hooks/stop.sh": "100755"})
    assert len(bledy) == 1 and "NIESLEDZONE" in bledy[0].replace("Ś", "S")


def test_audyt_w24_hook_wolany_przez_bash_nie_wymaga_bitu(tmp_path):
    """`bash skrypt.sh` uruchamia interpreter — bit skryptu nie ma tam znaczenia.
    Alarm bylby falszywy, a falszywy alarm uczy ignorowania straznika."""
    import narzedzia.audyt_spojnosci as a
    bledy, _ = a._warstwa_24_hooki_wykonywalne(
        sciezka_settings=_settings(tmp_path, "bash .claude/hooks/stop.sh"),
        tryby_gita={".claude/hooks/stop.sh": "100644"})
    assert bledy == [], bledy


# ── WARSTWA 19: alias „Ostatnia aktualizacja" (recenzja cubic PR #138, M1) ──────

def _dokument_z_data(monkeypatch, tmp_path, tresc, stan_na):
    """Podstawia JEDEN dokument o zadanej treści pod parser Tabularium."""
    import narzedzia.audyt_spojnosci as a  # noqa: F401
    import narzedzia.tabularium as t
    plik = tmp_path / "probny.md"
    plik.write_text(tresc, encoding="utf-8")
    monkeypatch.setattr(t, "zbierz_dokumenty", lambda: [("probny.md", {"stan_na": stan_na})])
    monkeypatch.setattr(t, "ROOT", str(tmp_path))
    return plik


def test_audyt_w19_alias_lapie_naglowek_ostatnia_aktualizacja(monkeypatch, tmp_path):
    """PAMIEC_SESJI glosila '## Ostatnia aktualizacja: 2026-07-27' przy stan_na 2026-07-18
    i lekcjach do 2026-08-01 — trzy daty, zadnej nie pilnowala zadna warstwa."""
    import narzedzia.audyt_spojnosci as a
    _dokument_z_data(monkeypatch, tmp_path,
                     "---\nkategoria: TABULA\n---\n## Ostatnia aktualizacja: 2026-07-27\n",
                     "2026-07-18")
    bledy, _ = a._warstwa_19_parytet_dat()
    assert len(bledy) == 1 and "Ostatnia aktualizacja" in bledy[0]


def test_audyt_w19_alias_zgodny_to_cisza(monkeypatch, tmp_path):
    import narzedzia.audyt_spojnosci as a
    _dokument_z_data(monkeypatch, tmp_path,
                     "---\nkategoria: TABULA\n---\n## Ostatnia aktualizacja: 2026-07-13\n",
                     "2026-07-13")
    bledy, _ = a._warstwa_19_parytet_dat()
    assert bledy == [], bledy


def test_audyt_w19_data_zdarzenia_w_prozie_nie_jest_deklaracja_swiezosci(monkeypatch, tmp_path):
    """KATALOG_NEURONOW ma '> Ostatnia aktualizacja: 2026-06-01 (CALA baza przeskanowana)' —
    to data ZDARZENIA w cytacie, nie deklaracja swiezosci pliku. Dopasowanie frazy gdziekolwiek
    dawaloby tam falszywy alarm, a warstwa pilnujaca prawdy nie moze produkowac nieprawdy."""
    import narzedzia.audyt_spojnosci as a
    _dokument_z_data(monkeypatch, tmp_path,
                     "---\nkategoria: TABULA\n---\n"
                     "> Ostatnia aktualizacja: 2026-06-01 (CALA baza przeskanowana)\n",
                     "2026-07-17")
    bledy, _ = a._warstwa_19_parytet_dat()
    assert bledy == [], bledy


# ── W20: komunikat MUSI pokazywać miejsce różnicy, nie wspólny początek ──────────
# Wada zmierzona 2026-08-05: wiersze katalogu różniły się OSTATNIĄ kolumną („Stan na"),
# a komunikat ucinał je po 90 znakach — ta sama linia stała jednocześnie jako „dopisana
# ręcznie" i „brakująca". Alarm był prawdziwy, lecz nieczytelny: przyrząd raportujący
# realny rozjazd w sposób, który go ukrywa, uczy operatora ignorować siebie.

_WIERSZ_A = ("| `docs/X.md` | bardzo dlugi opis ktory jest identyczny po obu stronach "
             "i zjada caly limit znakow | `imperium/legiony/rejestr.py` | 2026-08-02 |")
_WIERSZ_B = _WIERSZ_A.replace("2026-08-02", "2026-08-04")


def test_audyt_w20_para_najblizsza_laczy_ten_sam_wiersz():
    import narzedzia.audyt_spojnosci as a
    assert a._para_najblizsza([_WIERSZ_A], [_WIERSZ_B]) == (_WIERSZ_A, _WIERSZ_B)


def test_audyt_w20_para_bez_wspolnego_poczatku_to_nie_para():
    """GRANICA: zero wspólnych znaków = dwie różne pozycje, nie jeden wiersz w dwóch wersjach."""
    import narzedzia.audyt_spojnosci as a
    assert a._para_najblizsza(["### Sekcja"], ["| `docs/Y.md` |"]) is None


def test_audyt_w20_fragment_pokazuje_roznice_a_nie_poczatek():
    import narzedzia.audyt_spojnosci as a
    frag_a, frag_b = a._fragmenty_roznicy(_WIERSZ_A, _WIERSZ_B)
    assert "2026-08-02" in frag_a and "2026-08-04" in frag_b
    assert frag_a != frag_b, "dwa identyczne fragmenty to dokładnie ta wada, którą naprawiamy"


def test_audyt_w20_fragment_gdy_roznica_na_poczatku():
    """Druga strona granicy: różnica w pierwszym znaku nie może wyjść poza zakres."""
    import narzedzia.audyt_spojnosci as a
    frag_a, frag_b = a._fragmenty_roznicy("Aaa", "Baa")
    assert frag_a == "Aaa" and frag_b == "Baa"


# ── W6: odniesieniem jest commit TEGO pliku, nie ostatni commit repozytorium ─────
# Powód zmierzony 2026-08-05: hook końca sesji commituje `auto: sync pamięci sesji`
# (kronika, wizje). To przesuwało odniesienie dla MANIFEST i README, których nikt nie
# ruszał — bramka czerwieniła się od pracy własnego hooka i uczyła lekceważyć czerwień.

def test_audyt_w6_data_commitu_pliku_dziala_na_zywym_repo():
    import narzedzia.audyt_spojnosci as a
    from datetime import date
    d = a._data_commitu_pliku("README.md")
    assert d is None or isinstance(d, date)


def test_audyt_w6_nieistniejacy_plik_nie_wywraca_audytu():
    """Brak historii → None → warstwa spada na `date.today()`, a nie na wyjątek."""
    import narzedzia.audyt_spojnosci as a
    assert a._data_commitu_pliku("nie_ma_takiego_pliku_w_repo.md") is None
