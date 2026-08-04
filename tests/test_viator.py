"""
🐎 Testy VIATORA — posłańca dróg (wsadowy sąd nad linkami).

ZERO SIECI: każdy test wstrzykuje własny `otwieracz`, więc bramka jest szybka
i deterministyczna, a wynik nie zależy od tego, czy GitHub akurat żyje.

Reguła Test-Granic: każdy próg klasyfikacji ma test PO OBU stronach granicy
(199/200, 299/300, 499/500, 599/600) — bo próg bez testu granicy to próg,
o którym tylko WIERZYMY, że stoi tam, gdzie myślimy.

Osobno pilnowana lekcja zapłacona w wachcie G1: **pasek postępu nie może brudzić
stdout**. Tam pasek DISCRIMINATORA czynił `--json` niesparsowalnym, a testy tego
nie widziały, bo wołały funkcję zamiast CLI. Tu test woła CLI i parsuje wyjście.
"""

import json
import os
import subprocess
import sys
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.viator import (
    AWARIA_SERWERA,
    BLAD,
    MARTWY,
    POMINIETY,
    PRZEKIEROWANY,
    ZABLOKOWANY,
    ZYWY,
    Droga,
    _host_prywatny,
    _klasyfikuj,
    domena,
    podsumuj,
    przytnij_ogon,
    sprawdz_link,
    sprawdz_wsadowo,
    wczytaj_cache,
    wyciagnij_linki,
)


class _Odpowiedz:
    """Minimalny stub odpowiedzi HTTP (context manager, jak urlopen)."""

    def __init__(self, kod: int, url: str) -> None:
        self._kod, self._url = kod, url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def getcode(self):
        return self._kod

    def geturl(self):
        return self._url


def otwieracz_staly(kod: int, finalny: str | None = None, wywolania: list | None = None):
    """Otwieracz zwracający zawsze ten sam kod; opcjonalnie notuje metody wywołań."""

    def _o(zadanie, timeout=None):
        if wywolania is not None:
            wywolania.append(zadanie.get_method())
        url = finalny or zadanie.full_url
        if kod >= 400:
            raise urllib.error.HTTPError(url, kod, "błąd", {}, None)
        return _Odpowiedz(kod, url)

    return _o


# ── wyciąganie adresów ────────────────────────────────────────────────────────

def test_wyciaga_unikalne_zachowujac_kolejnosc():
    t = "a https://b.org/x b https://a.org/y c https://b.org/x"
    assert wyciagnij_linki(t) == ["https://b.org/x", "https://a.org/y"]


def test_pomija_interpunkcje_zdania():
    assert wyciagnij_linki("zob. https://arxiv.org/abs/1706.03762.") == [
        "https://arxiv.org/abs/1706.03762"
    ]
    assert wyciagnij_linki("(https://x.org/a), dalej") == ["https://x.org/a"]


def test_nawias_sparowany_zostaje_w_adresie():
    """Wikipedia: nawias JEST częścią adresu, gdy sparowany — inaczej psujemy link."""
    u = "https://en.wikipedia.org/wiki/Kelly_criterion_(betting)"
    assert wyciagnij_linki(f"tekst {u} dalej") == [u]


def test_niesparowany_nawias_obciety():
    assert przytnij_ogon("https://x.org/a)") == "https://x.org/a"


def test_pogrubienie_markdown_nie_zabija_repo():
    """REGRESJA z realnego biegu 2026-08-02 — wada złapana UŻYCIEM, nie testem.

    Pierwsza partia próbna na materiale z wrzutni zgłosiła 19/20 adresów jako MARTWE.
    Wszystkie kończyły się na `)**`, bo materiał zapisuje je jako `**[nazwa](url)**`.
    Repozytoria żyły — martwy był regex. Bez tego testu wada wróci przy pierwszej
    zmianie wzorca, a jej skutkiem jest KASOWANIE ŻYWYCH PROPOZYCJI.
    """
    t = "**[LightRAG](https://github.com/HKUDS/LightRAG)** oraz *[B](https://github.com/a/b)*"
    assert wyciagnij_linki(t) == [
        "https://github.com/HKUDS/LightRAG",
        "https://github.com/a/b",
    ]


def test_gwiazdka_nie_zjada_sparowanego_nawiasu():
    """Obie naprawy muszą współistnieć: zdjąć `**`, ale zachować `(betting)`."""
    t = "**[K](https://en.wikipedia.org/wiki/Kelly_criterion_(betting))**"
    assert wyciagnij_linki(t) == ["https://en.wikipedia.org/wiki/Kelly_criterion_(betting)"]


def test_znacznik_cytowania_deepseeka_odciety():
    """REGRESJA z drugiego biegu 2026-08-02: `url)[reference:8` — czat DeepSeeka dokleja
    znaczniki cytowań wprost do adresu. Ta sama klasa co `)**`."""
    t = "zob. https://huggingface.co/BinomialTechnologies)[reference:8] dalej"
    assert wyciagnij_linki(t) == ["https://huggingface.co/BinomialTechnologies"]


def test_backtick_nie_wchodzi_w_adres():
    """REGRESJA: `https://github.com/dparzy/IMPERIAL-MESH-VORTEX` w kodzie inline."""
    assert wyciagnij_linki("repo `https://github.com/a/b` tutaj") == ["https://github.com/a/b"]


def test_markdown_nie_wciaga_skladni():
    assert wyciagnij_linki("[tytuł](https://x.org/a) i [b](https://y.org/b)") == [
        "https://x.org/a",
        "https://y.org/b",
    ]


def test_brak_linkow_daje_pusta_liste():
    assert wyciagnij_linki("zwykły tekst bez adresów") == []


# ── granice klasyfikacji (Reguła Test-Granic: po obu stronach każdego progu) ──

def test_granice_klasyfikacji():
    """Pętla zamiast `parametrize` — runner Imperium (`tests/run_tests.py`) NIE jest
    pytestem i nie wstrzykuje parametrów; test z `parametrize` pada u niego na TypeError,
    będąc jednocześnie zielony pod `pytest`. Bramką jest runner, więc to on rozstrzyga."""
    przypadki = [
        (199, BLAD), (200, ZYWY), (204, ZYWY), (299, ZYWY), (300, BLAD),
        (404, MARTWY), (410, MARTWY), (403, ZABLOKOWANY), (429, ZABLOKOWANY),
        (401, ZABLOKOWANY), (499, BLAD), (500, AWARIA_SERWERA), (599, AWARIA_SERWERA),
        (600, BLAD),
    ]
    for kod, oczekiwany in przypadki:
        assert _klasyfikuj(kod) == oczekiwany, f"kod {kod} → {_klasyfikuj(kod)}, oczekiwano {oczekiwany}"


def test_403_nie_jest_martwy():
    """Prawo I: blokada bota to stan NASZEGO przyrządu, nie wyrok o cudzej treści."""
    assert _klasyfikuj(403) != MARTWY
    assert not Droga("https://x.org", ZABLOKOWANY).rozstrzygniety
    assert Droga("https://x.org", MARTWY).rozstrzygniety


# ── adresy prywatne (ochrona przed SSRF) ─────────────────────────────────────

def test_host_prywatny():
    for host, prywatny in [
        ("localhost:8000", True), ("127.0.0.1", True), ("10.0.0.5", True),
        ("192.168.1.1", True), ("172.16.0.1", True), ("mojhost.local", True),
        ("github.com", False), ("8.8.8.8", False), ("arxiv.org", False),
    ]:
        assert _host_prywatny(host) is prywatny, f"{host} → {_host_prywatny(host)}"


def test_localhost_pomijany_bez_pukania():
    wywolania: list = []
    d = sprawdz_link("http://localhost:8000/api", otwieracz=otwieracz_staly(200, wywolania=wywolania))
    assert d.status == POMINIETY
    assert wywolania == []  # ani jednego żądania — o to chodzi w ochronie


# ── pojedyncza droga ──────────────────────────────────────────────────────────

def test_zywy_link():
    d = sprawdz_link("https://arxiv.org/abs/1", otwieracz=otwieracz_staly(200))
    assert (d.status, d.kod) == (ZYWY, 200)


def test_martwy_link():
    d = sprawdz_link("https://github.com/nie/ma", otwieracz=otwieracz_staly(404))
    assert (d.status, d.kod) == (MARTWY, 404)


def test_przekierowanie_wykryte():
    d = sprawdz_link("https://x.org/stare", otwieracz=otwieracz_staly(200, finalny="https://x.org/nowe"))
    assert d.status == PRZEKIEROWANY
    assert d.finalny_url == "https://x.org/nowe"


def test_ukosnik_na_koncu_to_nie_przekierowanie():
    """`/a` → `/a/` to normalizacja serwera, nie przeprowadzka zasobu."""
    d = sprawdz_link("https://x.org/a", otwieracz=otwieracz_staly(200, finalny="https://x.org/a/"))
    assert d.status == ZYWY


def test_405_na_head_probuje_get():
    """Serwer nielubiący HEAD nie może być zapisany jako martwy."""
    metody: list = []

    def _o(zadanie, timeout=None):
        metody.append(zadanie.get_method())
        if zadanie.get_method() == "HEAD":
            raise urllib.error.HTTPError(zadanie.full_url, 405, "no HEAD", {}, None)
        return _Odpowiedz(200, zadanie.full_url)

    d = sprawdz_link("https://x.org/a", otwieracz=_o)
    assert metody == ["HEAD", "GET"]
    assert d.status == ZYWY


def test_403_na_head_probuje_get_i_zostaje_zablokowany():
    def _o(zadanie, timeout=None):
        raise urllib.error.HTTPError(zadanie.full_url, 403, "nie", {}, None)

    d = sprawdz_link("https://x.org/a", otwieracz=_o)
    assert d.status == ZABLOKOWANY


def test_timeout_to_blad_nie_martwy():
    def _o(zadanie, timeout=None):
        raise TimeoutError("za wolno")

    d = sprawdz_link("https://x.org/a", otwieracz=_o)
    assert d.status == BLAD
    assert not d.rozstrzygniety


def test_dziwny_wyjatek_nie_wywraca_biegu():
    def _o(zadanie, timeout=None):
        raise ValueError("cudzy serwer potrafi wszystko")

    assert sprawdz_link("https://x.org/a", otwieracz=_o).status == BLAD


# ── cache i wznawialność (Prawo XXIV) ────────────────────────────────────────

def test_cache_zapisuje_i_wznawia(tmp_path):
    cache = str(tmp_path / "c.jsonl")
    urls = ["https://a.org/1", "https://a.org/2"]
    sprawdz_wsadowo(urls, watki=2, cache_sciezka=cache, postep=False,
                    otwieracz=otwieracz_staly(200))
    assert len(wczytaj_cache(cache)) == 2

    # drugi bieg: nie może puknąć ANI RAZU — wszystko jest w cache
    wywolania: list = []
    wynik = sprawdz_wsadowo(urls, watki=2, cache_sciezka=cache, postep=False,
                            otwieracz=otwieracz_staly(200, wywolania=wywolania))
    assert wywolania == []
    assert len(wynik) == 2


def test_odswiez_ignoruje_cache(tmp_path):
    cache = str(tmp_path / "c.jsonl")
    urls = ["https://a.org/1"]
    sprawdz_wsadowo(urls, cache_sciezka=cache, postep=False, otwieracz=otwieracz_staly(200))
    wywolania: list = []
    sprawdz_wsadowo(urls, cache_sciezka=cache, odswiez=True, postep=False,
                    otwieracz=otwieracz_staly(404, wywolania=wywolania))
    assert wywolania  # puknął ponownie


def test_cache_jest_append_only(tmp_path):
    """VINDEX pilnuje kontraktu append-only — plik ma ROSNĄĆ, nie być nadpisywany."""
    cache = str(tmp_path / "c.jsonl")
    sprawdz_wsadowo(["https://a.org/1"], cache_sciezka=cache, postep=False,
                    otwieracz=otwieracz_staly(200))
    po_pierwszym = open(cache, encoding="utf-8").read()
    sprawdz_wsadowo(["https://a.org/2"], cache_sciezka=cache, postep=False,
                    otwieracz=otwieracz_staly(200))
    po_drugim = open(cache, encoding="utf-8").read()
    assert po_drugim.startswith(po_pierwszym)
    assert len(po_drugim.splitlines()) == 2


def test_uszkodzona_linia_cache_nie_zabija_wznowienia(tmp_path):
    cache = tmp_path / "c.jsonl"
    cache.write_text(
        '{"url": "https://a.org/1", "status": "ZYWY"}\n'
        "to nie jest json\n"
        '{"brak_pola_url": 1}\n',
        encoding="utf-8",
    )
    znane = wczytaj_cache(str(cache))
    assert list(znane) == ["https://a.org/1"]


def test_ostatni_wpis_o_tym_samym_url_wygrywa(tmp_path):
    cache = tmp_path / "c.jsonl"
    cache.write_text(
        '{"url": "https://a.org/1", "status": "BLAD"}\n'
        '{"url": "https://a.org/1", "status": "ZYWY"}\n',
        encoding="utf-8",
    )
    assert wczytaj_cache(str(cache))["https://a.org/1"].status == ZYWY


def test_bez_cache_nie_tworzy_pliku(tmp_path):
    sprawdz_wsadowo(["https://a.org/1"], cache_sciezka=None, postep=False,
                    otwieracz=otwieracz_staly(200))
    assert list(tmp_path.iterdir()) == []


def test_kolejnosc_wynikow_stabilna(tmp_path):
    urls = [f"https://a.org/{i}" for i in range(10)]
    w = sprawdz_wsadowo(urls, watki=4, cache_sciezka=str(tmp_path / "c.jsonl"),
                        postep=False, otwieracz=otwieracz_staly(200))
    assert [d.url for d in w] == urls  # wielowątkowość nie miesza kolejności


# ── pasek postępu: lekcja z wachty G1 ────────────────────────────────────────

def test_pasek_idzie_na_stderr_nie_na_stdout(tmp_path):
    """Bez fixture `capsys` — runner Imperium jej nie wstrzykuje. Przechwytujemy sami."""
    import contextlib
    import io as _io

    buf_out, buf_err = _io.StringIO(), _io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        sprawdz_wsadowo(["https://a.org/1"], cache_sciezka=str(tmp_path / "c.jsonl"),
                        postep=True, otwieracz=otwieracz_staly(200))
    assert buf_out.getvalue() == ""            # ANI JEDNEGO znaku na stdout
    assert "[1/1]" in buf_err.getvalue()       # pasek jednak był


def test_cli_json_jest_parsowalny(tmp_path):
    """Test CLI, nie funkcji — dokładnie ta luka przepuściła wadę w G1."""
    plik = tmp_path / "m.md"
    plik.write_text("zob. http://localhost:8000/a oraz http://127.0.0.1/b", encoding="utf-8")
    wynik = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "..", "narzedzia", "viator.py"),
         "--plik", str(plik), "--json", "--cache", str(tmp_path / "c.jsonl")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
    )
    assert wynik.returncode == 0, wynik.stderr
    dane = json.loads(wynik.stdout)  # sparsuje się albo test padnie
    assert dane["podsumowanie"]["lacznie"] == 2
    assert dane["podsumowanie"]["wg_statusu"][POMINIETY] == 2


def test_cli_brak_pliku_zwraca_2(tmp_path):
    wynik = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "..", "narzedzia", "viator.py"),
         "--plik", str(tmp_path / "nie-ma.md")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    assert wynik.returncode == 2


# ── podsumowanie ──────────────────────────────────────────────────────────────

def test_podsumowanie_oddziela_rozstrzygniete():
    drogi = [
        Droga("https://a/1", ZYWY, 200), Droga("https://a/2", MARTWY, 404),
        Droga("https://b/3", ZABLOKOWANY, 403), Droga("https://b/4", BLAD),
    ]
    p = podsumuj(drogi)
    assert p["lacznie"] == 4
    assert p["martwe"] == 1
    assert p["rozstrzygniete"] == 2     # ZYWY + MARTWY
    assert p["nierozstrzygniete"] == 2  # ZABLOKOWANY + BLAD


def test_podsumowanie_pustej_listy():
    p = podsumuj([])
    assert p["lacznie"] == 0 and p["martwe"] == 0


def test_kontekst_ssl_ma_zaufane_certyfikaty():
    """REGRESJA: bez tego 83 adresy arxiv.org szły jako BŁĄD (`cafile` = None na Windowsie)."""
    from narzedzia.viator import kontekst_ssl

    ctx = kontekst_ssl()
    assert ctx.get_ca_certs(), "kontekst bez ani jednego zaufanego certyfikatu"
    assert ctx.verify_mode == __import__("ssl").CERT_REQUIRED, "weryfikacji NIE WOLNO wyłączać"


def test_domena_z_adresu():
    assert domena("https://GitHub.com/a/b") == "github.com"


def test_blad_sieci_nie_utrwala_sie_jako_wynik(tmp_path):
    """Chwilowy timeout NIE MOŻE stać się trwałym werdyktem o adresie.

    Wada znaleziona recenzją tej wachty: `BLAD` i `ZABLOKOWANY` lądowały w cache tak
    samo jak wyroki, więc jeden zły moment sieci zamrażał adres na zawsze — a jedynym
    lekarstwem był `--odswiez`, kasujący też setki poprawnych wyników.
    """
    cache = str(tmp_path / "c.jsonl")
    url = ["https://a.org/1"]

    def _timeout(zadanie, timeout=None):
        raise TimeoutError("chwilowa awaria")

    w1 = sprawdz_wsadowo(url, cache_sciezka=cache, postep=False, otwieracz=_timeout)
    assert w1[0].status == BLAD

    # drugi bieg BEZ --odswiez: musi puknąć ponownie, bo poprzedni wynik nie był wyrokiem
    wywolania: list = []
    w2 = sprawdz_wsadowo(url, cache_sciezka=cache, postep=False,
                         otwieracz=otwieracz_staly(200, wywolania=wywolania))
    assert wywolania, "nierozstrzygnięty wynik z cache zablokował ponowną próbę"
    assert w2[0].status == ZYWY


def test_rozstrzygniety_wynik_nadal_wraca_z_cache(tmp_path):
    """Granica z drugiej strony: 404 to WYROK i ma oszczędzić nam pukania."""
    cache = str(tmp_path / "c.jsonl")
    url = ["https://a.org/1"]
    sprawdz_wsadowo(url, cache_sciezka=cache, postep=False, otwieracz=otwieracz_staly(404))
    wywolania: list = []
    w = sprawdz_wsadowo(url, cache_sciezka=cache, postep=False,
                        otwieracz=otwieracz_staly(200, wywolania=wywolania))
    assert wywolania == [], "rozstrzygnięty wyrok powinien wrócić z cache"
    assert w[0].status == MARTWY


def test_pozniejszy_blad_uniewaznia_wczesniejszy_wyrok(tmp_path):
    """Append-only: jeśli OSTATNIM słowem o adresie jest BLAD, wcześniejszy wyrok nie
    może cicho obowiązywać — adres wraca do sprawdzenia."""
    cache = tmp_path / "c.jsonl"
    cache.write_text(
        '{"url": "https://a.org/1", "status": "ZYWY", "kod": 200}\n'
        '{"url": "https://a.org/1", "status": "BLAD"}\n',
        encoding="utf-8",
    )
    assert wczytaj_cache(str(cache)) == {}
    assert len(wczytaj_cache(str(cache), tylko_rozstrzygniete=False)) == 1
