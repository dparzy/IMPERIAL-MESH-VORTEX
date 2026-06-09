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
            return re.sub(r"\d+ zaimplementowane", "999 zaimplementowane", t)
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
