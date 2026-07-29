#!/usr/bin/env python3
"""
Testy SCHOLI — organu Szkoły Cezara.

Organ istnieje po to, żeby dokument z lekcjami NIE ZGNIŁ. Jego jedyna groźna wada to
milcząca zgoda: parser, który przy zmianie formatu przestaje widzieć lekcje i melduje
„0 lekcji, wszystko w porządku". Dlatego rdzeniem testów są przypadki, w których organ
MUSI KRZYCZEĆ — brak statusu, brak własnego dowodu, brak sprawdzianu.

Testy `test_zywy_dokument_*` pilnują, że realny `docs/SCHOLA_CAESARIS.md` pozostaje
parsowalny — bo lekcje pisane ręcznie łatwo rozjeżdżają się z formatem (klasa wady,
którą znamy z W11 i CENSUS ORGANORUM).
"""

from __future__ import annotations

import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
if str(KORZEN) not in sys.path:
    sys.path.insert(0, str(KORZEN))

from imperium.biblioteki import schola as S  # noqa: E402

SZKIELET = """## LEKCJA {n} — {tytul}

### 🎯 Pytanie
Coś tam?

### 🔬 Nasz własny dowód
Zmierzone 2026-07-29: liczba.

### 🎓 Sprawdzian
Pytanie kontrolne.

### 📊 Status
**{status}** — uzasadnienie.

---
"""


def _dok(tmp_path: Path, *lekcje: str) -> Path:
    p = tmp_path / "SCHOLA.md"
    p.write_text("# Szkoła\n\n" + "\n".join(lekcje), encoding="utf-8")
    return p


# ── Parsowanie ────────────────────────────────────────────────────────────────

def test_czyta_lekcje_i_statusy(tmp_path: Path):
    p = _dok(tmp_path,
             SZKIELET.format(n=1, tytul="Pierwsza", status="✅ POTWIERDZONE"),
             SZKIELET.format(n=2, tytul="Druga", status="⏳ HIPOTEZA"))
    lek = S.wczytaj(p)
    assert [x.numer for x in lek] == [1, 2]
    assert [x.status for x in lek] == ["POTWIERDZONE", "HIPOTEZA"]


def test_tytul_jest_odczytany(tmp_path: Path):
    p = _dok(tmp_path, SZKIELET.format(n=7, tytul="NIEZMIENNIK", status="✅ POTWIERDZONE"))
    assert S.wczytaj(p)[0].tytul == "NIEZMIENNIK"


def test_brak_pliku_nie_wybucha(tmp_path: Path):
    assert S.wczytaj(tmp_path / "nie-ma.md") == []


# ── Organ MUSI krzyczeć, gdy lekcja jest niedokończona ────────────────────────

def test_brak_statusu_jest_brakiem(tmp_path: Path):
    p = _dok(tmp_path, "## LEKCJA 1 — Bez statusu\n\n### 🔬 Nasz własny dowód\nx\n\n### 🎓 Sprawdzian\ny\n")
    lek = S.wczytaj(p)
    assert lek[0].status == "BRAK"
    assert any("BRAK STATUSU" in b for b in S.braki(lek))


def test_brak_wlasnego_dowodu_jest_brakiem(tmp_path: Path):
    """Lekcja bez naszego pomiaru to CUDZA TEORIA — cały sens szkoły odwrotny."""
    p = _dok(tmp_path, "## LEKCJA 1 — Cudza teoria\n\n### 🎓 Sprawdzian\nx\n\n### 📊 Status\n\n**✅ POTWIERDZONE** — bla.\n")
    assert any("brak własnego dowodu" in b for b in S.braki(S.wczytaj(p)))


def test_brak_sprawdzianu_jest_brakiem(tmp_path: Path):
    p = _dok(tmp_path, "## LEKCJA 1 — Bez pytania\n\n### 🔬 Nasz własny dowód\nx\n\n### 📊 Status\n\n**✅ POTWIERDZONE** — bla.\n")
    assert any("brak sprawdzianu" in b for b in S.braki(S.wczytaj(p)))


def test_komplet_nie_daje_zadnych_brakow(tmp_path: Path):
    p = _dok(tmp_path, SZKIELET.format(n=1, tytul="Pelna", status="✅ POTWIERDZONE"))
    assert S.braki(S.wczytaj(p)) == []


# ── Hipotezy: tędy nauka wraca do Imperium jako zadanie ───────────────────────

def test_hipoteza_czeka_na_pomiar(tmp_path: Path):
    p = _dok(tmp_path,
             SZKIELET.format(n=1, tytul="Domknieta", status="✅ POTWIERDZONE"),
             SZKIELET.format(n=2, tytul="Otwarta", status="⏳ HIPOTEZA"))
    hip = S.hipotezy(S.wczytaj(p))
    assert [x.numer for x in hip] == [2]


def test_obalona_lekcja_NIE_czeka_juz_na_pomiar(tmp_path: Path):
    """OBALONE to wynik domknięty — sprawdziliśmy i wiemy, że nieprawda."""
    p = _dok(tmp_path, SZKIELET.format(n=1, tytul="Obalona", status="❌ OBALONE"))
    assert S.hipotezy(S.wczytaj(p)) == []


def test_zmierzone_wciaz_czeka_na_werdykt(tmp_path: Path):
    p = _dok(tmp_path, SZKIELET.format(n=1, tytul="W toku", status="📊 ZMIERZONE"))
    assert len(S.hipotezy(S.wczytaj(p))) == 1


# ── Linia startowa: postęp LICZONY, nie wpisany ───────────────────────────────

def test_linia_startowa_liczy_z_pliku(tmp_path: Path):
    p = _dok(tmp_path,
             SZKIELET.format(n=1, tytul="A", status="✅ POTWIERDZONE"),
             SZKIELET.format(n=2, tytul="B", status="✅ POTWIERDZONE"),
             SZKIELET.format(n=3, tytul="C", status="⏳ HIPOTEZA"))
    linia = S.linia_startowa(S.wczytaj(p))
    assert "3 lekcji" in linia and "pomiarem 2" in linia and "do sprawdzenia 1" in linia


def test_linia_startowa_alarmuje_o_niedokonczonych(tmp_path: Path):
    p = _dok(tmp_path, "## LEKCJA 1 — Kaleka\n\ntresc bez niczego\n")
    assert "🚨" in S.linia_startowa(S.wczytaj(p))


def test_raport_pustej_szkoly_nie_wybucha():
    assert "brak lekcji" in S.raport([])


# ── Żywy dokument musi pozostać parsowalny ────────────────────────────────────

def test_zywy_dokument_ma_lekcje():
    lek = S.wczytaj()
    assert lek, "docs/SCHOLA_CAESARIS.md nie parsuje się — format lekcji się rozjechał"


def test_zywy_dokument_nie_ma_lekcji_niedokonczonych():
    """Szkoła nie może uczyć niechlujstwa, którego sama zakazuje."""
    assert S.braki(S.wczytaj()) == []


def test_zywy_dokument_kazda_lekcja_ma_wlasny_dowod():
    assert all(x.ma_dowod for x in S.wczytaj())
