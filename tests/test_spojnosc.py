"""
Testy Prawa XXI — Protokół Spójności.
Silnik audytu (narzedzia/audyt_spojnosci.py) MUSI być zielony w każdej sesji.
"""

import os
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
