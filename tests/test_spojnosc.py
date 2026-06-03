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
