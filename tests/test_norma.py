#!/usr/bin/env python3
"""
Testy NORMY — węgielnicy oceniającej metody fragmentacji.

NORMA jest przyrządem, który OCENIA INNE PRZYRZĄDY, więc jej błąd propaguje się
na każdy werdykt, jaki wyda. Najgroźniejszy byłby błąd „miękki": bramka, która
przepuszcza wszystko. Dlatego rdzeniem tych testów są KONTROLE NEGATYWNE —
metoda ewidentnie zła MUSI polec, a kryterium bez pomiaru MUSI zostać NIEZNANE.

Test `test_nierozstrzygniete_gdy_K10_nieznane` pilnuje najważniejszej własności
całego organu: dziewięć zielonych kryteriów NIE upoważnia do słowa „najlepsza".
Gdyby ten test kiedyś zniknął, NORMA zamieniłaby się w uzasadnienie (LEX TALARUS).
"""

from __future__ import annotations

import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
for p in (KORZEN, KORZEN / "narzedzia" / "rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import norma as N  # noqa: E402
import redditor as R  # noqa: E402

AKAPIT = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed eiusmod tempor. "


def _teksty(n: int = 3) -> dict[str, str]:
    blok = (AKAPIT * 6).strip()
    return {f"BIB-{i:03d}": "\n\n".join(f"{blok} nr{j}" for j in range(30)) + "\n"
            for i in range(n)}


# ── Kontrola pozytywna: REDDITOR przechodzi 9 z 10 ────────────────────────────

def test_redditor_zalicza_wiernosc():
    b = N.zbadaj_metode("REDDITOR", R.kanon, _teksty())
    for kod in ("K1", "K2", "K3"):
        assert b["kryteria"][kod] == N.ZALICZONE, (kod, b["szczegoly"][kod])


def test_redditor_zalicza_uzytecznosc():
    b = N.zbadaj_metode("REDDITOR", R.kanon, _teksty())
    for kod in ("K4", "K5", "K7", "K8"):
        assert b["kryteria"][kod] == N.ZALICZONE, (kod, b["szczegoly"][kod])


# ── Kontrola negatywna: metoda zwracająca napisy NIE MOŻE dowieść bezstratności ─

def test_metoda_napisowa_oblewa_bezstratnosc():
    from ekstraktor import podziel_na_chunki
    b = N.zbadaj_metode("stara", podziel_na_chunki, _teksty())
    assert b["kryteria"]["K1"] == N.PORAZKA
    assert b["kryteria"]["K2"] == N.PORAZKA
    assert b["kryteria"]["K3"] == N.PORAZKA, "stara metoda kasuje linie — musi oblać K3"
    assert N.werdykt(b) == "🔴 ODRZUCONA"


def test_gigant_oblewa_K4():
    """Metoda zwracająca jeden wielki fragment musi polec — inaczej bramka jest atrapą."""
    b = N.zbadaj_metode("gigant", lambda t: [R.Zakres(0, len(t), "x")], _teksty())
    assert b["kryteria"]["K4"] == N.PORAZKA, b["szczegoly"]["K4"]


def test_okruchy_oblewaja_K5():
    def tnij(t: str):
        krok = max(1, len(t) // 400)
        gr = list(range(0, len(t), krok)) + [len(t)]
        return [R.Zakres(gr[i], gr[i + 1], "x") for i in range(len(gr) - 1)]
    b = N.zbadaj_metode("okruchy", tnij, _teksty(1))
    assert b["kryteria"]["K5"] == N.PORAZKA, b["szczegoly"]["K5"]


def test_ciecie_w_pol_slowa_oblewa_K7():
    def tnij(t: str):
        srodek = len(t) // 2
        while srodek < len(t) and not (t[srodek - 1].isalnum() and t[srodek].isalnum()):
            srodek += 1
        return [R.Zakres(0, srodek, "x"), R.Zakres(srodek, len(t), "x")]
    b = N.zbadaj_metode("w-pol-slowa", tnij, _teksty(1))
    assert b["kryteria"]["K7"] == N.PORAZKA, b["szczegoly"]["K7"]


def test_brak_adresu_oblewa_K8():
    b = N.zbadaj_metode("bez-adresu", lambda t: [R.Zakres(0, len(t), "")], _teksty(1))
    assert b["kryteria"]["K8"] == N.PORAZKA


# ── Najważniejsze: NIEZNANE blokuje werdykt „najlepsza" ───────────────────────

def test_K10_zostaje_NIEZNANE_bez_pomiaru_trafnosci():
    b = N.zbadaj_metode("REDDITOR", R.kanon, _teksty())
    assert b["kryteria"]["K10"] == N.NIEZNANE, (
        "K10 policzone bez QUAESITORA znaczy, że bramkę da się przejść samą starannością"
    )


def test_nierozstrzygniete_gdy_K10_nieznane():
    b = N.zbadaj_metode("REDDITOR", R.kanon, _teksty())
    assert all(v != N.PORAZKA for k, v in b["kryteria"].items() if k != "K10")
    assert N.werdykt(b).startswith("⏳"), N.werdykt(b)


def test_porazka_bije_nieznane_w_werdykcie():
    b = {"kryteria": {"K1": N.PORAZKA, "K10": N.NIEZNANE}}
    assert N.werdykt(b) == "🔴 ODRZUCONA"


def test_wszystko_zielone_daje_przyjeta():
    b = {"kryteria": {f"K{i}": N.ZALICZONE for i in range(1, 11)}}
    assert N.werdykt(b) == "✅ PRZYJĘTA"


def test_raport_wypisuje_wszystkie_dziesiec_kryteriow():
    b = N.zbadaj_metode("REDDITOR", R.kanon, _teksty(1))
    txt = N.raport([b])
    for i in range(1, 11):
        assert f"K{i}" in txt
