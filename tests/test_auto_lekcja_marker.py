"""
Testy markera przetworzonych kronik (auto_lekcja) — recenzja cubic PR #118.

Rdzeń buga: hasz treści i sesja_id trafiały do JEDNEGO zbioru, więc kronika dopisana
po przetworzeniu (nowy hasz) była nadal pomijana po starym ID. Hasz przestawał cokolwiek
unieważniać. Tu pilnujemy obu kierunków: pomijamy niezmienione, przetwarzamy zmienione.
"""

import tempfile
from pathlib import Path

import narzedzia.auto_lekcja as al


def _srodowisko():
    d = Path(tempfile.mkdtemp())
    al.PRZETWORZONE_PLIK = d / "auto_lekcja_przetworzone.txt"
    al.STARY_MARKER = d / ".auto_lekcja_przetworzone.txt"
    return d


def test_hasz_rozstrzyga_a_zmigrowane_id_nie_blokuje():
    d = _srodowisko()
    kron = d / "sesja_abc.md"
    kron.write_text("treść pierwotna", encoding="utf-8")
    h1 = al._klucz_kroniki(kron)
    al.PRZETWORZONE_PLIK.write_text(f"# nagłówek\n{h1}  abc\n", encoding="utf-8")
    al.STARY_MARKER.write_text("abc\ninna_sesja\n", encoding="utf-8")

    hasze, stare = al._wczytaj_przetworzone()
    assert h1 in hasze                      # hasz rozstrzyga
    assert "abc" not in stare               # zmigrowane ID nie blokuje unieważnienia
    assert "inna_sesja" in stare            # niezmigrowane ID nadal działa (zgodność wstecz)


def test_zmieniona_kronika_jest_przetwarzana_ponownie():
    d = _srodowisko()
    kron = d / "sesja_abc.md"
    kron.write_text("treść pierwotna", encoding="utf-8")
    h1 = al._klucz_kroniki(kron)
    al.PRZETWORZONE_PLIK.write_text(f"{h1}  abc\n", encoding="utf-8")
    al.STARY_MARKER.write_text("", encoding="utf-8")

    hasze, stare = al._wczytaj_przetworzone()
    assert h1 in hasze and "abc" not in stare      # niezmieniona → pomijana

    kron.write_text("treść pierwotna + DOPISEK", encoding="utf-8")
    h2 = al._klucz_kroniki(kron)
    assert h2 != h1
    hasze, stare = al._wczytaj_przetworzone()
    assert h2 not in hasze and "abc" not in stare  # zmieniona → przetwarzana ponownie


def test_komentarze_i_puste_linie_pomijane():
    _srodowisko()
    al.PRZETWORZONE_PLIK.write_text("# komentarz\n\nabc123def456  sesja\n", encoding="utf-8")
    hasze, stare = al._wczytaj_przetworzone()
    assert hasze == {"abc123def456"} and stare == set()


def test_brak_obu_markerow_daje_puste_zbiory():
    _srodowisko()
    assert al._wczytaj_przetworzone() == (set(), set())
