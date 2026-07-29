#!/usr/bin/env python3
"""
Testy REDDITORA — fragmentacji z kryptograficznym dowodem bezstratności.

Organ orzeka o BEZSTRATNOŚCI, więc jego błąd nie jest niedokładnością — jest
fałszywym świadectwem. Testy poniżej używają tekstów o ZNANEJ z góry budowie,
bo tylko wtedy „poprawny wynik" jest faktem, a nie opinią (LEX TALARUS).

Trzy z nich pilnują wad ZMIERZONYCH na żywym korpusie 2026-07-29, zanim
ktokolwiek ogłosił, że organ działa:
  • fragmenty-giganty (BIB-012 dawała medianę 4904 słów, gdy książka nie miała
    pustych linii) — patrz `test_ksiazka_bez_pustych_linii_*`,
  • okruchy < 20 słów wykryte przez NORMĘ (K5) — `test_okruch_*`,
  • fragment bez adresu (K8) — `test_adres_*`.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
for p in (KORZEN, KORZEN / "narzedzia" / "rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import redditor as R  # noqa: E402


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


AKAPIT = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod. "
TABELA = "Matrix Operation FLOPs\no 1 = X y 2 T 1 N\no 2 = X X 2 T 1 N 2\no 3 = o 1 2 N 3\n"


def _ksiazka(akapitow: int = 40, slow_w_akapicie: int = 60) -> str:
    blok = (AKAPIT * (slow_w_akapicie // 10)).strip()
    return "\n\n".join(f"{blok} nr{i}" for i in range(akapitow)) + "\n"


# ── DOWÓD BEZSTRATNOŚCI — rdzeń organu ────────────────────────────────────────

def test_rekonstrukcja_jest_bajt_w_bajt():
    t = _ksiazka()
    p = R.podziel(t)
    assert R.zrekonstruuj(t, p.kanon) == t
    assert _sha(R.zrekonstruuj(t, p.kanon)) == p.zrodlo_sha


def test_dowod_orzeka_bezstratnosc():
    t = _ksiazka()
    d = R.dowod_bezstratnosci(t, R.podziel(t))
    assert d["bezstratny"] is True and d["powody"] == []


def test_dowod_WYKRYWA_dziure_w_kanonie():
    """Sprawdzian samego sprawdzianu: usunięty fragment MUSI zapalić alarm.

    Bez tego testu dowód mógłby zawsze mówić „bezstratny" i nikt by nie zauważył
    — miernik, który nie umie orzec PORAŻKI, nie jest miernikiem.
    """
    t = _ksiazka()
    p = R.podziel(t)
    assert len(p.kanon) >= 3
    p.kanon.pop(1)                       # celowa dziura
    d = R.dowod_bezstratnosci(t, p)
    assert d["bezstratny"] is False
    assert any("SHA-256" in x or "rozłączne" in x for x in d["powody"]), d["powody"]


def test_kanon_jest_ciagly_i_pelny():
    t = _ksiazka()
    kan = R.kanon(t)
    assert kan[0].start == 0 and kan[-1].koniec == len(t)
    assert all(kan[i].koniec == kan[i + 1].start for i in range(len(kan) - 1))


def test_pusty_tekst_nie_wybucha():
    assert R.kanon("") == []
    assert R.dowod_bezstratnosci("", R.podziel(""))["bezstratny"] is True


# ── STRUKTURA — powód istnienia organu ────────────────────────────────────────

def test_znaki_nowej_linii_przezywaja():
    """Stary chunker kasował 100% linii (1 479 710 → 0). Tu musi być 1:1."""
    t = _ksiazka()
    kan = R.kanon(t)
    assert sum(z.tekst(t).count("\n") for z in kan) == t.count("\n")


def test_tabela_nie_jest_rozrywana():
    t = _ksiazka(10) + "\n\n" + TABELA + "\n\n" + _ksiazka(10)
    kan = R.kanon(t)
    trafione = [z for z in kan if "Matrix Operation" in z.tekst(t)]
    assert trafione, "blok tabeli zniknął"
    z = trafione[0]
    assert "o 3 = o 1 2 N 3" in z.tekst(t), "tabela rozcięta między fragmentami"


def test_blok_tabelaryczny_jest_oznaczony():
    t = _ksiazka(6) + "\n\n" + TABELA + "\n\n" + _ksiazka(6)
    assert any(z.tabelaryczny for z in R.kanon(t))


def test_proza_NIE_jest_brana_za_tabele():
    """Fałszywa tabela scaliłaby akapity i rozdęła fragment — gorsze niż przeoczenie."""
    assert not R._wyglada_na_tabele(_ksiazka(3))


# ── WADY ZMIERZONE NA ŻYWYM KORPUSIE ─────────────────────────────────────────

def test_ksiazka_bez_pustych_linii_nie_daje_giganta():
    """BIB-012: brak pustych linii dawał medianę 4904 słów na fragment."""
    t = " ".join(f"zdanie numer {i} z pewna trescia." for i in range(3000))
    kan = R.kanon(t)
    assert len(kan) > 5, "cała książka wpadła do jednego fragmentu"
    assert max(z.slowa(t) for z in kan) <= R.DOMYSLNY_MAX


def test_ksiazka_bez_pustych_linii_pozostaje_bezstratna():
    t = " ".join(f"zdanie numer {i} z pewna trescia." for i in range(3000))
    assert R.dowod_bezstratnosci(t, R.podziel(t))["bezstratny"] is True


def test_tekst_bez_zdan_i_bez_linii_tez_dzieli_sie():
    """Sieczka OCR bez kropek i bez \\n — ostatnia deska ratunku nie może zawieść."""
    t = "slowo " * 5000
    kan = R.kanon(t)
    assert len(kan) > 1
    assert R.zrekonstruuj(t, kan) == t


def test_okruch_jest_wchlaniany_a_nie_usuwany():
    """Usunięcie okrucha złamałoby dowód — musi zostać SCALONY z sąsiadem."""
    t = _ksiazka(20) + "\n\nkoniec\n"
    kan = R.kanon(t)
    assert all(z.slowa(t) >= R.PODLOGA_SLOW for z in kan[:-1] if z.slowa(t) > 0)
    assert R.zrekonstruuj(t, kan) == t, "scalanie okruchów zgubiło tekst"


def test_adres_nigdy_nie_jest_pusty():
    t = _ksiazka(20)
    assert all(z.adres for z in R.kanon(t))


def test_adres_wskazuje_ostatni_naglowek():
    t = "Chapter 1 Wstep\n\n" + _ksiazka(8) + "\n\nChapter 2 Rozwiniecie\n\n" + _ksiazka(8)
    kan = R.kanon(t)
    assert any("Chapter 2" in z.adres for z in kan), [z.adres for z in kan]


# ── OKNA WYSZUKIWANIA vs KANON ────────────────────────────────────────────────

def test_okna_nie_psuja_dowodu():
    """Zakładka służy trafności; dowód liczy się z KANONU i ma pozostać czysty."""
    t = _ksiazka()
    p = R.podziel(t)
    assert len(p.okna) == len(p.kanon)
    assert R.dowod_bezstratnosci(t, p)["bezstratny"] is True


def test_okna_maja_zakladke_wstecz():
    t = _ksiazka()
    p = R.podziel(t)
    cofniete = [i for i in range(1, len(p.okna)) if p.okna[i].start < p.kanon[i].start]
    assert cofniete, "żadne okno nie sięga wstecz — zakładka nie działa"


def test_stara_metoda_NIE_jest_bezstratna():
    """Kontrola negatywna: gdyby i stara metoda zdała, nasz dowód nic by nie znaczył."""
    t = _ksiazka()
    w = R.porownaj_ze_starym(t)
    assert w["stare_bezstratne"] is False
    assert w["redditor_bezstratny"] is True
    assert w["stare_linii_zachowanych"] == 0
    assert w["redditor_linii_zachowanych"] == t.count("\n")
