"""Testy redakcji KATALOGU DOMOWEGO w kronice — granice wzorca, nie jego istnienie.

Wada, której bronią te testy, przeszła bramkę i weszła do `main` bez recenzji zewnętrznej
(PR #134 zmergowany po jedynym przebiegu recenzenta). Była niewidoczna na laptopie Cezara,
bo `C:\\Users\\Ian` ma trzy segmenty — degenerowała się dopiero na PŁYTKIM katalogu domowym,
czyli w środowisku chmurowym. Dlatego testy sprawdzają nie „czy redaguje", ale „czy nie
niszczy", i robią to na domach, których na tej maszynie nie ma.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.biblioteki import kronika_czatu as kc  # noqa: E402

# Cytat kodu, jaki NAPRAWDĘ trafia do transkryptu — zawiera słowo „root" w trzech rolach.
PROBKA = 'ROOT = Path(__file__).parent  # root katalogu; zobacz /root/dane oraz /rootkit'


def test_dom_windows_redaguje_sciezke():
    rx = kc._wzorzec_domu(r"C:\Users\Ian")
    assert rx.sub("~", r"plik C:\Users\Ian\AppData\Local") == r"plik ~\AppData\Local"


def test_dom_windows_lapie_wszystkie_formy_separatora():
    """Ta sama ścieżka żyje w transkrypcie jako proza, JSON i POSIX — redakcja jednej
    formy meldowałaby sukces przy dwóch wyciekających."""
    rx = kc._wzorzec_domu(r"C:\Users\Ian")
    for forma in (r"C:\Users\Ian", r"C:\\Users\\Ian", "C:/Users/Ian", "c:/users/ian"):
        assert rx.sub("~", forma) == "~", f"forma nie zredagowana: {forma!r}"


def test_plytki_dom_kontenera_NIE_niszczy_slowa_root():
    """SEDNO WADY: `/root` degenerował wzorzec do gołego słowa `root` z IGNORECASE, więc
    cytat `ROOT = Path(...)` zapisywał się do wersjonowanej kroniki jako `~ = Path(...)`.
    Kronika jest pamięcią — korupcja byłaby trwała i cicha."""
    rx = kc._wzorzec_domu("/root")
    wynik = rx.sub("~", PROBKA)
    assert wynik.startswith("ROOT = Path"), f"zniszczony cytat kodu: {wynik!r}"
    assert "root katalogu" in wynik, "zniszczona proza"
    assert "/rootkit" in wynik, "dopasowanie weszło w środek dłuższego słowa"
    assert "~/dane" in wynik, "prawdziwa ścieżka domowa NIE została zredagowana"


def test_dom_glowny_nie_rozsadza_tekstu_na_znaki():
    """Dom `/` dawał wzorzec PUSTY, a `re.sub` pustym wzorcem wstawia `~` między KAŻDY znak.
    Tu redakcja ma się WYŁĄCZYĆ i powiedzieć o tym wprost, nie zniszczyć transkrypt."""
    rx = kc._wzorzec_domu("/")
    assert rx.sub("~", PROBKA) == PROBKA
    assert rx is kc._NIGDY


def test_jednoczlonowy_dom_wzglendy_jest_odrzucony():
    """`Ian` bez separatora dopasowywałby imię w dowolnym zdaniu — granica po obu stronach."""
    assert kc._wzorzec_domu("Ian") is kc._NIGDY


def test_dom_posix_dwuczlonowy_dziala_normalnie():
    rx = kc._wzorzec_domu("/home/ubuntu")
    assert rx.sub("~", "plik /home/ubuntu/projekt") == "plik ~/projekt"


def test_flaga_mowi_wprost_kiedy_redakcji_NIE_MA():
    """Milczenie o wyłączonej redakcji byłoby gorsze niż jej brak (Prawo I)."""
    assert kc.redakcja_domu_dziala() is (kc._WZORZEC_DOMU is not kc._NIGDY)


def test_redaguj_najpierw_sekrety_potem_sciezki():
    """Kolejność jest zadeklarowana w docstringu `_redaguj` — test trzyma ją przy życiu,
    bo odwrócenie skróciłoby kontekst, w którym wzorzec klucza jeszcze pasuje."""
    tekst = "klucz sk-" + "a" * 32 + " w pliku"
    assert "[ZREDAGOWANO]" in kc._redaguj(tekst)
