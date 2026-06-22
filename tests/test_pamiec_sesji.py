"""
Testy Pamięci Sesji (W-360) — ciągłość między sesjami Claude Code.

Weryfikuje:
  • lekcje() parsuje sekcję LEKCJE Z SESJI (data, tytuł, treść),
  • dopisz_lekcje() wstawia na GÓRZE (najnowsza pierwsza) + aktualizuje datę,
  • szukaj() filtruje po tytule i treści,
  • mapa_podpiec() wycina sekcję mapy,
  • podsumowanie_startowe() dla hooka,
  • granice: pusty plik, brak sekcji, dopisanie do nieistniejącej sekcji,
  • roundtrip: dopisz → odczyt zwraca dokładnie tę lekcję na pozycji 0.
"""

import tempfile
from pathlib import Path

from imperium.biblioteki import pamiec_sesji as ps

_WZOR = """# PAMIĘĆ SESJI — W-360

## Ostatnia aktualizacja: 2026-01-01

## 🗺️ PEŁNA MAPA PODPIĘĆ DO LOKALA

### A. MCP Servers
Treść mapy A.

## 📚 LEKCJE Z SESJI

### 2026-06-21 — Pierwsza lekcja
Treść pierwszej lekcji z GARCH.

### 2026-06-20 — Druga lekcja
Treść drugiej.

## 🔄 STAN BIEŻĄCY
Stan.
"""


def _plik(tekst: str = _WZOR) -> Path:
    d = tempfile.mkdtemp()
    p = Path(d) / "PAMIEC_SESJI.md"
    p.write_text(tekst, encoding="utf-8")
    return p


def test_lekcje_parsuje():
    p = _plik()
    lek = ps.lekcje(p)
    assert len(lek) == 2
    assert lek[0]["data"] == "2026-06-21"
    assert lek[0]["tytul"] == "Pierwsza lekcja"
    assert "GARCH" in lek[0]["tresc"]


def test_lekcje_limit():
    p = _plik()
    assert len(ps.lekcje(p, limit=1)) == 1


def test_lekcje_pusty_plik():
    p = _plik("# Pusto\n\nBez sekcji lekcji.\n")
    assert ps.lekcje(p) == []


def test_lekcje_nieistniejacy_plik():
    assert ps.lekcje(Path("/nieistnieje/x.md")) == []


def test_dopisz_na_gorze():
    """Nowa lekcja trafia na pozycję 0 (najnowsza pierwsza)."""
    p = _plik()
    ps.dopisz_lekcje("Nowa rzecz", "Treść nowej.", data="2026-06-22", plik=p)
    lek = ps.lekcje(p)
    assert len(lek) == 3
    assert lek[0]["tytul"] == "Nowa rzecz"
    assert lek[0]["data"] == "2026-06-22"
    # Stare lekcje zachowane
    assert lek[1]["tytul"] == "Pierwsza lekcja"


def test_dopisz_aktualizuje_date():
    p = _plik()
    ps.dopisz_lekcje("X", "Y", data="2026-12-31", plik=p)
    assert "## Ostatnia aktualizacja: 2026-12-31" in ps.wczytaj(p)


def test_dopisz_roundtrip():
    """dopisz → odczyt zwraca dokładnie tę treść."""
    p = _plik()
    ps.dopisz_lekcje("Tytuł testowy", "Linia 1\nLinia 2", data="2026-06-25", plik=p)
    lek = ps.lekcje(p)[0]
    assert lek["tytul"] == "Tytuł testowy"
    assert "Linia 1" in lek["tresc"] and "Linia 2" in lek["tresc"]


def test_dopisz_do_pliku_bez_sekcji():
    """Granica: plik bez sekcji LEKCJE → sekcja tworzona, lekcja dodana."""
    p = _plik("# Tylko nagłówek\n\n## Ostatnia aktualizacja: 2026-01-01\n")
    ps.dopisz_lekcje("Pierwsza", "Treść", data="2026-06-22", plik=p)
    lek = ps.lekcje(p)
    assert len(lek) == 1
    assert lek[0]["tytul"] == "Pierwsza"


def test_szukaj_tytul_i_tresc():
    p = _plik()
    assert len(ps.szukaj("GARCH", p)) == 1          # w treści
    assert len(ps.szukaj("Druga", p)) == 1          # w tytule
    assert ps.szukaj("nieistniejace", p) == []


def test_mapa_podpiec():
    p = _plik()
    mapa = ps.mapa_podpiec(p)
    assert "MCP Servers" in mapa
    assert "Treść mapy A" in mapa
    # Nie zawiera sekcji lekcji
    assert "Pierwsza lekcja" not in mapa


def test_podsumowanie_startowe():
    p = _plik()
    out = ps.podsumowanie_startowe(p, n_lekcji=2)
    assert "PAMIĘĆ SESJI" in out
    assert "Pierwsza lekcja" in out
    assert "PAMIEC_SESJI.md" in out


def test_podsumowanie_startowe_brak_pliku():
    assert ps.podsumowanie_startowe(Path("/nieistnieje/x.md")) == ""


# ── Regresja: bugi z adversarial review (markdown w treści) ──────────────────

def test_tresc_z_zagniezdzonym_h3_nie_tworzy_fantomow():
    """BUG 1: '### ' w treści lekcji NIE może rozbić jej na fantomowe lekcje."""
    p = _plik("# P\n\n## Ostatnia aktualizacja: 2026-01-01\n\n## 📚 LEKCJE Z SESJI\n")
    ps.dopisz_lekcje("Realna", "Detale:\n### Podtytuł w treści\nopis pod nim",
                     data="2026-06-22", plik=p)
    lek = ps.lekcje(p)
    assert len(lek) == 1                      # JEDNA lekcja, nie dwie
    assert lek[0]["tytul"] == "Realna"
    assert "Podtytuł w treści" in lek[0]["tresc"]
    assert "opis pod nim" in lek[0]["tresc"]


def test_tresc_z_h2_nie_ucina_kolejnych_lekcji():
    """BUG 2: linia '## ' w treści NIE może zgubić lekcji poniżej."""
    p = _plik("# P\n\n## Ostatnia aktualizacja: 2026-01-01\n\n## 📚 LEKCJE Z SESJI\n")
    ps.dopisz_lekcje("Starsza", "zwykła treść", data="2026-06-20", plik=p)
    ps.dopisz_lekcje("Nowsza", "Wniosek poniżej:\n## Sekcja w treści\ndalej",
                     data="2026-06-22", plik=p)
    lek = ps.lekcje(p)
    # Obie lekcje muszą być widoczne (nowsza pierwsza)
    tytuly = [x["tytul"] for x in lek]
    assert "Nowsza" in tytuly and "Starsza" in tytuly


def test_dopisz_wstawia_date_gdy_brak():
    """BUG 4: brak linii 'Ostatnia aktualizacja' → wstawiona, nie cichy no-op."""
    p = _plik("# Tytuł pliku\n\n## 📚 LEKCJE Z SESJI\n")
    ps.dopisz_lekcje("X", "Y", data="2026-06-30", plik=p)
    assert "## Ostatnia aktualizacja: 2026-06-30" in ps.wczytaj(p)


def test_wielokrotny_dopisz_nie_psuje_parsowania():
    """Round-trip: 5× dopisz → wszystkie 5 lekcji parsowalne, kolejność zachowana."""
    p = _plik("# P\n\n## Ostatnia aktualizacja: 2026-01-01\n\n## 📚 LEKCJE Z SESJI\n")
    for i in range(5):
        ps.dopisz_lekcje(f"Lekcja {i}", f"- punkt {i}\n- drugi {i}",
                         data=f"2026-06-{20+i:02d}", plik=p)
    lek = ps.lekcje(p)
    assert len(lek) == 5
    assert lek[0]["tytul"] == "Lekcja 4"   # ostatnia dopisana na górze
    assert lek[-1]["tytul"] == "Lekcja 0"


# ── CRUD pamięci (inspiracja Hermes memory tool: add/replace/remove) ──────────

def test_usun_lekcje():
    """remove: lekcja po tytule znika, reszta zostaje, kolejność zachowana."""
    p = _plik()
    assert ps.usun_lekcje("Pierwsza lekcja", p) is True
    lek = ps.lekcje(p)
    assert len(lek) == 1
    assert lek[0]["tytul"] == "Druga lekcja"


def test_usun_lekcje_nieistniejaca():
    p = _plik()
    assert ps.usun_lekcje("Nie ma takiej", p) is False
    assert len(ps.lekcje(p)) == 2          # nic nie tknięte


def test_usun_zachowuje_ogon_stan_biezacy():
    """remove nie może zjeść sekcji STAN BIEŻĄCY pod lekcjami."""
    p = _plik()
    ps.usun_lekcje("Druga lekcja", p)
    assert "## 🔄 STAN BIEŻĄCY" in ps.wczytaj(p)
    assert "Stan." in ps.wczytaj(p)


def test_aktualizuj_lekcje():
    """replace: podmiana treści zachowuje pozycję i datę."""
    p = _plik()
    assert ps.aktualizuj_lekcje("Druga lekcja", "Zupełnie nowa treść", p) is True
    lek = [x for x in ps.lekcje(p) if x["tytul"] == "Druga lekcja"][0]
    assert "Zupełnie nowa treść" in lek["tresc"]
    assert "Treść drugiej" not in lek["tresc"]


def test_aktualizuj_z_nowym_tytulem():
    p = _plik()
    ps.aktualizuj_lekcje("Druga lekcja", "T", p, nowy_tytul="Przemianowana")
    tytuly = [x["tytul"] for x in ps.lekcje(p)]
    assert "Przemianowana" in tytuly and "Druga lekcja" not in tytuly


def test_aktualizuj_nieistniejaca():
    p = _plik()
    assert ps.aktualizuj_lekcje("Brak", "x", p) is False


def test_usun_nie_duplikuje_przy_h2_w_tresci():
    """Regresja: linia '## ' w treści lekcji NIE może zduplikować lekcji ani zjeść ogona."""
    p = _plik("# P\n\n## 📚 LEKCJE Z SESJI\n\n"
              "### 2026-06-22 — Nowa\nopis\n## wtrącenie w treści\ndalej\n\n"
              "### 2026-06-20 — Stara\ntreść stara\n\n"
              "## 🔄 STAN BIEŻĄCY\nstan\n")
    assert ps.usun_lekcje("Stara", p) is True
    tekst = ps.wczytaj(p)
    # STAN BIEŻĄCY zachowany dokładnie raz, brak duplikatu "Nowa"
    assert tekst.count("## 🔄 STAN BIEŻĄCY") == 1
    assert tekst.count("### 2026-06-22 — Nowa") == 1
    assert "### 2026-06-20 — Stara" not in tekst


def test_limit_pojedynczej_lekcji_blokuje():
    """Hermes-style: lekcja > limit → twardy błąd, nie ciche ucięcie."""
    import pytest
    p = _plik()
    dluga = "x" * (ps.LIMIT_ZNAKOW_LEKCJA + 10)
    with pytest.raises(ValueError):
        ps.dopisz_lekcje("Za długa", dluga, plik=p)


def test_alarm_przepelnienia_gdy_male_ok():
    p = _plik()
    assert ps.alarm_przepelnienia(p) is None


def test_alarm_przepelnienia_gdy_duze():
    """Sekcja ponad limit → alarm Prawa XV (string z 🚨)."""
    p = _plik("# P\n\n## 📚 LEKCJE Z SESJI\n\n## 🔄 STAN\nx\n")
    for i in range(40):
        ps.dopisz_lekcje(f"L{i}", "t" * (ps.LIMIT_ZNAKOW_LEKCJA - 50),
                         data=f"2026-01-{(i % 28) + 1:02d}", plik=p)
    alarm = ps.alarm_przepelnienia(p)
    assert alarm is not None and "🚨" in alarm


# ── Profil Cezara (odpowiednik USER.md Hermesa) ──────────────────────────────

def test_profil_cezara_czyta():
    d = tempfile.mkdtemp()
    pf = Path(d) / "PROFIL.md"
    pf.write_text("# Profil\n\n- Lubi krótko\n- Tryb autonomiczny\n", encoding="utf-8")
    assert "Lubi krótko" in ps.profil_cezara(pf)


def test_profil_skrot_zwraca_punkty():
    d = tempfile.mkdtemp()
    pf = Path(d) / "PROFIL.md"
    pf.write_text("# H\n\n- A\n- B\nopis\n- C\n", encoding="utf-8")
    skrot = ps.profil_skrot(pf, maks_linii=2)
    assert skrot == ["- A", "- B"]


def test_profil_brak_pliku():
    assert ps.profil_cezara(Path("/nieistnieje/p.md")) == ""
