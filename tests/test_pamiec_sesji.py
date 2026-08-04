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

import re
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


def test_konsoliduj_ponizej_celu_nic_nie_rusza():
    """Granica: sekcja mniejsza niż cel → 0 zarchiwizowanych, plik nietknięty."""
    p = _plik()
    r = ps.konsoliduj_lekcje(cel_znakow=99999, plik=p, sucho=True)
    assert r["zarchiwizowanych"] == 0 and r["po"] == r["przed"]


def test_konsoliduj_sucho_nie_zapisuje(tmp_path):
    """Granica: sucho=True liczy, ale NIE zmienia pliku ani nie tworzy archiwum."""
    p = _plik()
    przed = p.read_text(encoding="utf-8")
    arch = tmp_path / "ARCH.md"
    r = ps.konsoliduj_lekcje(cel_znakow=10, plik=p, archiwum=arch, sucho=True)
    assert r["zarchiwizowanych"] >= 1                 # coś BY poszło do archiwum
    assert p.read_text(encoding="utf-8") == przed     # ale plik nietknięty
    assert not arch.exists()                          # archiwum nie powstało


def test_konsoliduj_przenosi_nic_nie_kasuje(tmp_path):
    """Rdzeń: aktywne + archiwum = wszystkie lekcje (nic nie ginie, Prawo I)."""
    p = _plik()
    arch = tmp_path / "ARCH.md"
    n0 = len(ps.lekcje(p))
    r = ps.konsoliduj_lekcje(cel_znakow=60, plik=p, archiwum=arch, sucho=False)
    assert r["po"] + r["zarchiwizowanych"] == n0      # bilans się zgadza
    assert r["po"] >= 1 and r["zarchiwizowanych"] >= 1
    assert arch.exists()
    tekst_arch = arch.read_text(encoding="utf-8")
    for tytul in r["archiwum"]:
        assert tytul in tekst_arch                    # każda schłodzona JEST w archiwum
    # STAN BIEŻĄCY (ogon) przetrwał operację na pliku aktywnym
    assert "🔄 STAN BIEŻĄCY" in p.read_text(encoding="utf-8")


def test_konsoliduj_zostawia_najwartosciowsze(tmp_path, monkeypatch):
    """Kryterium retencji: przy remisie/wartości nowsza+ważniejsza lekcja zostaje w gorącym."""
    monkeypatch.setattr(ps, "_dzis", lambda: "2026-07-01")
    p = _plik()
    # dodaj świeżą, ważną lekcję — powinna zostać, a stare wypaść przy ciasnym celu
    ps.dopisz_lekcje("KRYTYCZNA zasada Cezara najważniejsza", "Treść.", data="2026-07-01", plik=p)
    arch = tmp_path / "ARCH.md"
    ps.konsoliduj_lekcje(cel_znakow=70, plik=p, archiwum=arch, sucho=False)
    aktywne_tytuly = [lek["tytul"] for lek in ps.lekcje(p)]
    assert any("KRYTYCZNA" in t for t in aktywne_tytuly)


def test_dopisz_archiwum_idempotentny(tmp_path):
    """Granica: kolejne konsolidacje DOPISUJĄ do archiwum (nie nadpisują, jeden nagłówek)."""
    arch = tmp_path / "ARCH.md"
    ps._dopisz_archiwum([{"data": "2026-06-01", "tytul": "Pierwsza", "tresc": "T1"}], arch)
    ps._dopisz_archiwum([{"data": "2026-06-02", "tytul": "Druga", "tresc": "T2"}], arch)
    txt = arch.read_text(encoding="utf-8")
    assert "Pierwsza" in txt and "Druga" in txt                 # nic nie zgubione
    assert txt.count(ps._NAGLOWEK_ARCHIWUM) == 1                # jeden nagłówek sekcji
    assert txt.count("kategoria: ACTA") == 1                    # jeden frontmatter


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


def test_dopisz_aktualizuje_OBIE_daty_w_tym_samym_ruchu():
    """Nagłówek i frontmatter to JEDNA prawda w dwóch miejscach (recenzja cubic PR #138).

    Zmierzone przed naprawą: ten zapis ruszał wyłącznie „## Ostatnia aktualizacja", więc
    `stan_na` zostawał w tyle po KAŻDEJ sesji. Dokument miał trzy różne daty naraz
    (stan_na 2026-07-18, nagłówek 2026-07-27, lekcje do 2026-08-01) i przez pięć dni mówił
    Cezarowi nieprawdę o własnej świeżości. Ręczne przestawienie daty nie było naprawą —
    automat pisze po każdej sesji, człowiek nie.
    """
    p = _plik()
    p.write_text("---\nkategoria: TABULA\nstan_na: 2026-01-01\n---\n"
                 + p.read_text(encoding="utf-8"), encoding="utf-8")
    ps.dopisz_lekcje("X", "Y", data="2026-12-31", plik=p)
    tresc = ps.wczytaj(p)
    assert "## Ostatnia aktualizacja: 2026-12-31" in tresc
    assert "stan_na: 2026-12-31" in tresc, "frontmatter został w tyle za nagłówkiem"


def test_dopisz_NIE_COFA_dat_gdy_lekcja_jest_starsza():
    """Świeżość dokumentu idzie tylko W PRZÓD (audyt W20 na czerwono, 2026-08-03).

    Zmierzone: `auto_lekcja` woła z datą ANALIZOWANEJ SESJI, nie dnia zapisu. Hook
    przemielił zaległe transkrypty z 27 lipca i cofnął obie daty PAMIEC_SESJI.md
    z 2026-07-30 na 2026-07-27 — dokument ogłosił się starszym, niż był, a katalog
    Tabularium (czytany z `stan_na`) rozjechał się z INDEKS_IMPERIUM.md.
    Data samej lekcji zostaje prawdziwa — cofa się tylko to, czego cofać nie wolno.
    """
    p = _plik()
    p.write_text("---\nkategoria: TABULA\nstan_na: 2026-07-30\n---\n"
                 + re.sub(r"## Ostatnia aktualizacja:.*",
                          "## Ostatnia aktualizacja: 2026-07-30",
                          p.read_text(encoding="utf-8"), count=1),
                 encoding="utf-8")
    assert "## Ostatnia aktualizacja: 2026-07-30" in ps.wczytaj(p), "fixture nie ustawił nagłówka"
    ps.dopisz_lekcje("Zaległa", "Z przemielonego transkryptu.", data="2026-07-27", plik=p)
    tresc = ps.wczytaj(p)
    assert "## Ostatnia aktualizacja: 2026-07-30" in tresc, "nagłówek cofnął się wstecz"
    assert "stan_na: 2026-07-30" in tresc, "frontmatter cofnął się wstecz"
    assert ps.lekcje(p)[0]["data"] == "2026-07-27", "data lekcji ma zostać prawdziwa"


def test_dopisz_data_rowna_nie_psuje_pola():
    """GRANICA: ten sam dzień to nie cofnięcie — pole zostaje poprawne, nie puste."""
    p = _plik()
    p.write_text("---\nstan_na: 2026-07-30\n---\n" + p.read_text(encoding="utf-8"),
                 encoding="utf-8")
    ps.dopisz_lekcje("Dzisiejsza", "Treść.", data="2026-07-30", plik=p)
    assert "stan_na: 2026-07-30" in ps.wczytaj(p)


def test_dopisz_data_niepasowalna_nie_blokuje_zapisu():
    """GRANICA: śmieć w polu nie może zamrozić dokumentu — nowa data wygrywa."""
    p = _plik()
    p.write_text("---\nstan_na: wkrótce\n---\n" + p.read_text(encoding="utf-8"),
                 encoding="utf-8")
    ps.dopisz_lekcje("X", "Y", data="2026-07-30", plik=p)
    assert "stan_na: 2026-07-30" in ps.wczytaj(p)


def test_nowsza_znosi_none_i_pustke():
    """GRANICA (Reguła Test-Granic): None w polu daje TypeError, jeśli go nie przewidzieć."""
    assert ps._nowsza(None, "2026-07-30") == "2026-07-30"
    assert ps._nowsza("2026-07-30", None) == "2026-07-30"
    assert ps._nowsza("", "2026-07-30") == "2026-07-30"
    assert ps._nowsza(None, None) == ""


def test_dopisz_nie_tworzy_frontmatteru_gdy_go_nie_bylo():
    """Zasięg wąski: uzupełniamy istniejące pole, nigdy nie dorabiamy bloku — od tego
    jest Tabularium, a dwa organy piszące ten sam nagłówek rozjechałyby się (Prawo XVI)."""
    p = _plik()
    ps.dopisz_lekcje("X", "Y", data="2026-12-31", plik=p)
    assert "stan_na:" not in ps.wczytaj(p)


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
    """Sekcja ponad limit → alarm Prawa XV (string z 🚨).

    `chlodz=False` świadomie: od 2026-07-21 zapis SAM chłodzi sekcję, więc przy
    domyślnym zapisie ten stan jest nieosiągalny. Test bada DETEKTOR, nie chłodzenie —
    mieszanie obu dawałoby zielone światło mechanizmowi, którego nikt nie sprawdził.
    """
    p = _plik("# P\n\n## 📚 LEKCJE Z SESJI\n\n## 🔄 STAN\nx\n")
    for i in range(40):
        ps.dopisz_lekcje(f"L{i}", "t" * (ps.LIMIT_ZNAKOW_LEKCJA - 50),
                         data=f"2026-01-{(i % 28) + 1:02d}", plik=p, chlodz=False)
    alarm = ps.alarm_przepelnienia(p)
    assert alarm is not None and "🚨" in alarm


def test_zapis_domyslny_nie_dopuszcza_do_przepelnienia():
    """Bliźniak powyższego: przy DOMYŚLNYM zapisie 40 długich lekcji sekcja nigdy
    nie przekracza progu — alarm nie ma jak wrócić w kolejnej sesji."""
    p = _plik("# P\n\n## 📚 LEKCJE Z SESJI\n\n## 🔄 STAN\nx\n")
    for i in range(40):
        ps.dopisz_lekcje(f"L{i}", "t" * (ps.LIMIT_ZNAKOW_LEKCJA - 50),
                         data=f"2026-01-{(i % 28) + 1:02d}", plik=p)
    assert ps.alarm_przepelnienia(p) is None
    assert ps.rozmiar_sekcji_lekcji(p) <= ps.LIMIT_ZNAKOW_SEKCJA


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


# ─────────────────────────────────────────────────────────────────────────────
# DEDUP SEMANTYCZNY (naprawa duplikatów, recenzja cubic PR #118)
# Reguła Test-Granic (Prawo XXI): każdy próg ma test wartości granicznej.
# ─────────────────────────────────────────────────────────────────────────────

def test_sygnatura_wyciaga_identyfikatory():
    s = ps.sygnatura_lekcji("Martwy głos ATR_MULT w EXP-07",
                            "EXP-07 miał ATR_MULT=1.5 zamiast 0.15.")
    assert "ATR_MULT" in s and "EXP-07" in s


def test_sygnatura_pomija_tokeny_puste():
    assert "NEUTRAL" not in ps.sygnatura_lekcji("Neuron zwraca NEUTRAL", "")


def test_dedup_lapie_parafraze_dwujezyczna():
    """Rdzeń buga: 'Martwy głos' vs 'Dead voice bug' — żaden nie jest podciągiem drugiego.
    Treści dosłownie z docs/PAMIEC_SESJI.md sprzed scalenia (przypadek regresyjny)."""
    assert ps.czy_duplikaty(
        "Martwy głos ATR_MULT w EXP-07",
        "EXP-07 miał ATR_MULT=1.5 ale ATR nie był używany w logice. "
        "Poprawiono na ATR_MULT=0.15 i faktyczne użycie ATR.",
        "Dead voice bug: ATR_MULT w EXP-07",
        "EXP-07 (TLP) miał ATR_MULT=1.5 w kodzie zamiast 0.15 z dokumentacji "
        "— martwy głos naprawiony.")


def test_dedup_nie_scala_roznych_modulow():
    """ATR w EXP-07 (TLP) i ATR w EXP-08 (Night Turbo) to RÓŻNE lekcje — fałszywe
    scalenie kasuje wiedzę bezpowrotnie, więc to najważniejszy test negatywny."""
    assert not ps.czy_duplikaty(
        "Martwy głos ATR_MULT w EXP-07", "EXP-07 miał ATR_MULT=1.5 zamiast 0.15.",
        "Martwy głos ATR w Night Turbo", "EXP-08 miał PROG_ATR_MULT nieużywany.")


def test_dedup_sito_rdzeni_dla_prozy():
    """Lekcje bez identyfikatorów (sygnatura pusta) — łapie je worek rdzeni tytułu."""
    assert ps.czy_duplikaty("True Range - poprawna definicja", "max(H-L, |H-prevC|).",
                            "Poprawiona definicja True Range", "max(H-L, |H-prevC|).")


def test_dedup_rdzenie_nie_myla_roznych_tytulow():
    assert not ps.czy_duplikaty("RSI Div threshold 2.0 zbyt wysoki", "opis",
                                "BB Squeeze threshold 4% zbyt restrykcyjny", "opis")


def test_dedup_lapie_parafraze_tytulu_pr122():
    """Cubic PR #122: parafrazy tego samego tytułu (DeepSeek co przebieg formułuje inaczej)
    scalają się dzięki progowi Jaccarda rdzeni <1.0 — bez tego rosły duplikaty w PAMIEC_SESJI."""
    # tresc pusta izoluje Sito 3 (sam tytuł); realne lekcje dodatkowo dzielą identyfikatory.
    assert ps.czy_duplikaty(
        "Mieszanie zasad Kingdom Pixel z Imperium = chaos", "",
        "Mieszanie zasad Kingdom Pixel z Imperium źródłem chaosu", "")
    assert ps.czy_duplikaty(
        "OpenAlice i Hermes Agent zweryfikowane jako realne narzędzia", "",
        "OpenAlice i Hermes Agent to realne narzędzia", "")
    assert ps.czy_duplikaty(
        "TA-Lib blokerem dla 9 modułów", "",
        "TA-Lib blokerem 9 modułów", "")


def test_dedup_negacja_mimo_wysokiego_podobienstwa_tytulu():
    """Strażnik polarności: nawet gdy Jaccard rdzeni ≥ próg, różnica na 'nie'/'bez' = lekcja
    OBALAJĄCA, nie duplikat (relaksacja progu z PR #122 nie może scalić zaprzeczeń)."""
    assert not ps.czy_duplikaty("Numba przyspiesza wskazniki", "szybciej",
                                "Numba nie przyspiesza wskaznikow", "wolniej")
    assert not ps.czy_duplikaty("Sizing bez cappingu bezpieczny", "opis",
                                "Sizing cappingu bezpieczny", "opis")


def test_granica_prog_rdzeni_tytulu():
    """Próg rdzeni dobrany POMIAREM (Prawo XVI) — istnieje, w (0,1], luźniejszy niż exact-match."""
    assert 0.0 < ps.PROG_RDZENI_TYTULU < 1.0


def test_granica_progu_podobienstwa_dokladnie_na_progu():
    """Jaccard == PROG_PODOBIENSTWA musi być DUPLIKATEM (>=, nie >)."""
    a, b = frozenset("ABC"), frozenset("ABD")   # |∩|=2, |∪|=4 → 0.5
    assert ps._jaccard(a, b) == 0.5
    trzy_z_piatki = ps._jaccard(frozenset("ABC"), frozenset("ABCDE"))  # 3/5 = 0.60
    assert trzy_z_piatki == ps.PROG_PODOBIENSTWA
    assert trzy_z_piatki >= ps.PROG_PODOBIENSTWA   # granica: włącznie


def test_granica_min_tokenow_sygnatury():
    """Sygnatura 1-tokenowa NIE deduplikuje (za uboga), 2-tokenowa już tak."""
    assert not ps.czy_duplikaty("Problem z ATR", "opis", "Inny problem z ATR", "opis")
    assert ps.czy_duplikaty("ATR_MULT w EXP-07", "x", "Bug ATR_MULT dotyczy EXP-07", "x")


def test_jaccard_dwa_puste_zbiory():
    assert ps._jaccard(frozenset(), frozenset()) == 0.0


def test_duplikat_lekcji_zwraca_istniejaca_lub_none():
    p = _plik()
    ps.dopisz_lekcje("Martwy głos ATR_MULT w EXP-07",
                     "EXP-07 miał ATR_MULT=1.5 ale ATR nie był używany w logice. "
                     "Poprawiono na ATR_MULT=0.15 i faktyczne użycie ATR.", plik=p)
    trafiona = ps.duplikat_lekcji(
        "Dead voice bug: ATR_MULT w EXP-07",
        "EXP-07 (TLP) miał ATR_MULT=1.5 w kodzie zamiast 0.15 z dokumentacji "
        "— martwy głos naprawiony.", plik=p)
    assert trafiona is not None and trafiona["tytul"] == "Martwy głos ATR_MULT w EXP-07"
    assert ps.duplikat_lekcji("Zupełnie inna rzecz o VPIN_50", "Toxic flow rośnie.", plik=p) is None


def test_duplikat_lekcji_pusty_plik_zwraca_none():
    p = _plik("# Pusto\n")
    assert ps.duplikat_lekcji("Cokolwiek ATR_MULT EXP-07", "treść", plik=p) is None


def test_duplikat_identyczny_tytul_rozna_wielkosc_liter():
    p = _plik()
    assert ps.duplikat_lekcji("PIERWSZA LEKCJA", "", plik=p) is not None


def test_sygnatura_czysto_liczbowa_nie_scala():
    """Bug złapany w samo-recenzji przed pushem: `\d{2,}` łapie daty i progi, więc
    sygnatura {14, 30} zlewałaby dwie zupełnie różne lekcje (Jaccard 1.0).
    Wymagamy co najmniej jednego tokenu z literą."""
    assert not ps.czy_duplikaty(
        "Stop-loss 14 pipsow przy 30 barach", "Zupełnie inny temat: stop 14, okno 30.",
        "Cooldown 14 barow po 30 stratach", "Inna rzecz: cooldown 14, limit 30.")
    assert not ps._sygnatura_rozstrzygajaca(frozenset({"14", "30"}))
    assert ps._sygnatura_rozstrzygajaca(frozenset({"RSI", "14"}))


def test_sygnatura_rozstrzygajaca_granica_jednego_tokenu():
    """Granica MIN_TOKENOW_SYGNATURY: 1 token nie wystarcza, 2 (z literą) już tak."""
    assert not ps._sygnatura_rozstrzygajaca(frozenset({"ATR_MULT"}))
    assert ps._sygnatura_rozstrzygajaca(frozenset({"ATR_MULT", "EXP"}))


# ── Regresja: bugi złapane w adversarial samo-recenzji przed pushem ───────────

def test_klucz_numer_jest_jednym_tokenem():
    """Kolejność alternatyw w _WZOR_TOKENU: 'EXP-07' to JEDEN token, nie 'EXP' + '07'.
    Inaczej osierocona liczba zawyża Jaccarda i scala różne lekcje na progu."""
    assert "EXP-07" in ps.sygnatura_lekcji("EXP-07 ATR 14", "")
    assert "07" not in ps.sygnatura_lekcji("EXP-07", "")


def test_ten_sam_modul_rozne_wskazniki_nie_scala():
    """'EXP-07 ATR 14' vs 'EXP-07 RSI 14' — ten sam moduł i okno, RÓŻNE bugi.
    Przed naprawą regexu dawało Jaccard dokładnie 0.60 → fałszywe scalenie."""
    assert not ps.czy_duplikaty("EXP-07 ATR 14 za niski", "opis",
                                "EXP-07 RSI 14 dywergencja", "opis")


def test_negacja_w_tytule_nie_jest_duplikatem():
    """Sito 3 patrzy tylko na tytuł — 'nie' NIE może być stopwordem, bo lekcja
    obalająca poprzednią zostałaby odrzucona jako duplikat (utrata wiedzy)."""
    assert not ps.czy_duplikaty("Numba przyspiesza wskazniki", "ok, szybciej",
                                "Numba NIE przyspiesza wskaznikow", "wolniej niestety")


def test_dwa_puste_tytuly_nie_sa_duplikatem():
    """Granica: '' == '' nie może orzekać o tożsamości lekcji."""
    assert not ps.czy_duplikaty("", "treść a", "", "treść b")


# ── Regresja: recenzja cubic na PR #118 (drugi przebieg) ─────────────────────

def test_daty_nie_wchodza_do_sygnatury():
    """Data mówi KIEDY, nie O CZYM. Dwie różne lekcje z tego samego dnia miały
    wspólne tokeny {2026, 06, 30} → Jaccard 0.60 → fałszywe scalenie."""
    s = ps.sygnatura_lekcji("X-01", "sesja 2026-06-30, 30.06.2026, rok 2026")
    assert s == frozenset({"X-01"})
    assert not ps.czy_duplikaty(
        "Neuron X-01 zwraca NEUTRAL", "Wykryto 2026-06-30, naprawiono.",
        "Zwiadowca EXP-13 milczy", "Wykryto 2026-06-30, inna sprawa.")


def test_proza_nie_nadpisuje_rozlacznych_sygnatur():
    """Sito 3 (worek rdzeni tytułu) nie może scalać lekcji o RÓŻNYCH modułach,
    nawet gdy tytuły mają identyczny worek rdzeni."""
    assert not ps.czy_duplikaty("Bug w EXP-07", "ATR_MULT zly",
                                "Bug w EXP-13", "GARCH zly")


def test_proza_nadal_dziala_gdy_sygnatury_slabe():
    """Kontrola: ograniczenie sita 3 nie może zabić jego pierwotnego celu."""
    assert ps.czy_duplikaty("True Range - poprawna definicja", "max(H-L).",
                            "Poprawiona definicja True Range", "max(H-L).")


# ── Automatyczne chłodzenie sekcji (Prawo XV: przyrost automatyczny = chłodzenie
#    automatyczne). Klasa wady: ręczna konsolidacja przeciw automatycznemu przyrostowi —
#    alarm wracał nazajutrz po każdym ręcznym schłodzeniu (zmierzone 2026-07-21). ──

def _plik_z_lekcjami(n: int, dlugosc: int = 400) -> Path:
    """Plik pamięci z n lekcjami po ~dlugosc znaków treści (do testów limitu)."""
    bloki = "\n".join(
        f"### 2026-06-{(i % 28) + 1:02d} — Lekcja numer {i}\n{'x' * dlugosc}\n"
        for i in range(n)
    )
    return _plik(f"# PAMIĘĆ\n\n## Ostatnia aktualizacja: 2026-01-01\n\n"
                 f"{ps._NAGLOWEK_LEKCJE}\n\n{bloki}\n## 🔄 STAN BIEŻĄCY\nStan.\n")


def test_rozmiar_sekcji_zgodny_z_faktycznym_zapisem():
    """Rdzeń: `_rozmiar_sekcji` musi zwracać DOKŁADNIE tyle, ile renderuje zapis.
    Rozjazd tej miary z miarą alarmu był źródłem 'schłodzone, a alarm dalej krzyczy'."""
    p = _plik_z_lekcjami(5)
    ls = ps.lekcje(p)
    ps._zapisz_lekcje(ls, p)
    tekst = p.read_text(encoding="utf-8")
    sekcja = tekst.split(ps._NAGLOWEK_LEKCJE, 1)[1]
    sekcja = sekcja[:sekcja.index("\n## 🔄")]
    assert ps._rozmiar_sekcji(ls) == len(sekcja)


def test_alarm_nie_ucina_sekcji_na_naglowku_w_tresci():
    """Fałszywy NEGATYW: lekcja z linią `## ` w treści ucinała pomiar surowego tekstu,
    więc alarm mógł MILCZEĆ przy przepełnionej pamięci."""
    p = _plik(f"# PAMIĘĆ\n\n{ps._NAGLOWEK_LEKCJE}\n\n"
              "### 2026-06-01 — Z nagłówkiem w środku\n"
              "## To jest linia w TREŚCI, nie nowa sekcja\n" + "y" * 200 + "\n")
    assert ps.rozmiar_sekcji_lekcji(p) > 200        # cała treść policzona, nie ucięta


def test_egzekwuj_limit_ponizej_progu_nic_nie_rusza(monkeypatch):
    """Granica: rozmiar < próg → zero chłodzenia, plik bit-w-bit ten sam."""
    p = _plik_z_lekcjami(3)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 99999)
    przed = p.read_text(encoding="utf-8")
    r = ps.egzekwuj_limit_sekcji(p)
    assert r["chlodzenie"] is False and r["zarchiwizowanych"] == 0
    assert p.read_text(encoding="utf-8") == przed


def test_egzekwuj_limit_dokladnie_na_progu_nie_chlodzi(monkeypatch):
    """Granica DOKŁADNIE == próg: alarm łapie dopiero `>`, więc chłodzenie też nie rusza."""
    p = _plik_z_lekcjami(3)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", ps.rozmiar_sekcji_lekcji(p))
    assert ps.alarm_przepelnienia(p) is None
    assert ps.egzekwuj_limit_sekcji(p)["chlodzenie"] is False


def test_egzekwuj_limit_o_jeden_znak_ponad_prog_chlodzi(monkeypatch):
    """Granica próg+1: minimalne przekroczenie MUSI odpalić chłodzenie."""
    p = _plik_z_lekcjami(6)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", ps.rozmiar_sekcji_lekcji(p) - 1)
    assert ps.egzekwuj_limit_sekcji(p)["chlodzenie"] is True


def test_dopisz_chlodzi_i_alarm_milknie(monkeypatch):
    """Rdzeń mechanizmu: po zapisie sekcja wraca pod próg, a alarm Prawa XV milczy.
    Regresja na klasę 'schłodzone wg jednej miary, alarm liczy drugą'."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    assert ps.alarm_przepelnienia(p) is not None          # przed: alarm krzyczy
    ps.dopisz_lekcje("Nowa lekcja", "Treść nowej lekcji.", data="2026-07-21", plik=p)
    assert ps.rozmiar_sekcji_lekcji(p) <= 4000
    assert ps.alarm_przepelnienia(p) is None              # po: milczy BEZ ręcznej ręki


def test_dopisz_chlodzenie_nic_nie_kasuje(monkeypatch):
    """Prawo I: schłodzone lekcje MUSZĄ być w archiwum — bilans aktywne+ACTA bez ubytku."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    tytuly_przed = {lek["tytul"] for lek in ps.lekcje(p)}
    ps.dopisz_lekcje("Nowa lekcja", "Treść.", data="2026-07-21", plik=p)
    arch = ps._archiwum_dla(p)
    tekst_arch = arch.read_text(encoding="utf-8") if arch.exists() else ""
    aktywne = {lek["tytul"] for lek in ps.lekcje(p)}
    for tytul in tytuly_przed:
        assert tytul in aktywne or tytul in tekst_arch


def test_dopisz_chlodz_false_zostawia_przepelnienie(monkeypatch):
    """Opt-out działa: chlodz=False → sekcja zostaje ponad progiem (świadomy wybór)."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    ps.dopisz_lekcje("Nowa", "Treść.", data="2026-07-21", plik=p, chlodz=False)
    assert ps.alarm_przepelnienia(p) is not None


def test_aktualizuj_tez_chlodzi(monkeypatch):
    """Parytet bliźniaków: podmiana treści też powiększa sekcję, więc też chłodzi."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    tytul = ps.lekcje(p)[0]["tytul"]
    assert ps.aktualizuj_lekcje(tytul, "Nowa treść.", plik=p) is True
    assert ps.alarm_przepelnienia(p) is None


def test_chlodzenie_nie_tyka_prawdziwego_archiwum_imperium(monkeypatch):
    """Piaskownica: chłodzenie pliku tymczasowego pisze OBOK niego, nigdy do
    docs/PAMIEC_SESJI_ARCHIWUM.md (mechanizm wychodzący poza własny zasięg)."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    assert ps._archiwum_dla(p) != ps.PLIK_ARCHIWUM
    assert ps._archiwum_dla(p).parent == p.parent
    ps.dopisz_lekcje("Nowa", "Treść.", data="2026-07-21", plik=p)
    assert ps._archiwum_dla(p).exists()


def test_cel_chlodzenia_liczony_z_progu(monkeypatch):
    """Sprzężenie: obniżenie progu MUSI obniżyć cel chłodzenia. Dwie niezależne
    liczby (24000 vs 22000) zamieniłyby chłodzenie w cichy no-op."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 3000)
    ps.egzekwuj_limit_sekcji(p)
    assert ps.rozmiar_sekcji_lekcji(p) <= 3000


def test_lekcje_czyta_takze_plik_acta(tmp_path):
    """Schłodzona lekcja NIE może być nieosiągalna dla własnego czytnika modułu.
    Archiwum ma inny nagłówek sekcji — parser musi go rozpoznać (zmierzone:
    113 bloków w ACTA, `lekcje()` widziało 0)."""
    arch = tmp_path / "ACTA.md"
    ps._dopisz_archiwum([{"naglowek": "### 2026-01-01 — Schłodzona",
                          "data": "2026-01-01", "tytul": "Schłodzona",
                          "tresc": "Treść o VWAP."}], arch)
    lek = ps.lekcje(arch)
    assert len(lek) == 1 and lek[0]["tytul"] == "Schłodzona"


def test_szukaj_z_archiwum_znajduje_schlodzona(monkeypatch):
    """Prawo I: po chłodzeniu wiedza dalej znajdywalna, tylko poza kontekstem startowym."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 4000)
    ps.dopisz_lekcje("Nowa", "Treść.", data="2026-07-21", plik=p)
    schlodzone = [lek["tytul"] for lek in ps.lekcje(ps._archiwum_dla(p))]
    assert schlodzone, "chłodzenie miało coś przenieść"
    cel = schlodzone[0]
    assert ps.szukaj(cel, p) == []                        # w gorącej pamięci już nie ma
    trafienia = ps.szukaj(cel, p, z_archiwum=True)
    assert trafienia and trafienia[0]["zrodlo"] == "ACTA"  # ale w ACTA jest


def test_szukaj_bez_archiwum_zachowuje_stary_kontrakt():
    """Wsteczna zgodność: domyślnie szukaj czyta TYLKO pamięć aktywną (bez klucza zrodlo)."""
    p = _plik()
    wyniki = ps.szukaj("GARCH", p)
    assert len(wyniki) == 1 and "zrodlo" not in wyniki[0]


def test_konsoliduj_cel_none_bierze_cel_z_progu(monkeypatch):
    """Granica None: cel_znakow=None (domyślny) MUSI wyliczyć cel z progu, nie
    wywalić się ani nie potraktować None jak zera/nieskończoności."""
    p = _plik_z_lekcjami(20)
    monkeypatch.setattr(ps, "LIMIT_ZNAKOW_SEKCJA", 3000)
    r = ps.konsoliduj_lekcje(cel_znakow=None, plik=p, archiwum=None, sucho=True)
    assert r["znakow_po"] <= int(3000 * ps.UDZIAL_CELU_SEKCJA)
    assert r["zarchiwizowanych"] >= 1


# ── ZASIĘG DEDUPU OBEJMUJE ARCHIWUM (naprawa 2026-07-26) ─────────────────────

def test_dedup_widzi_lekcje_schlodzona_do_archiwum(monkeypatch):
    """🚨 GRANICA ZASIĘGU: bliźniak w ACTA to NADAL duplikat.

    Wada (zmierzona 2026-07-26): `duplikat_lekcji` przeglądał wyłącznie plik aktywny —
    91 lekcji widzianych wobec 207 schłodzonych niewidzianych, czyli bramka pilnowała 31%
    korpusu. Mechanizm: chłodzenie przenosi lekcję do ACTA, jej bliźniak znika z pola
    widzenia i auto-lekcja zapisuje tę samą treść jako „nową". Tak powstały 4 kopie jednej
    lekcji — powtórka wady naprawianej po cubic PR #118, gdzie poprawiono PREDYKAT, ale
    nie ZASIĘG.
    """
    p = _plik()
    ps.dopisz_lekcje("Wskaźnik VWAP liczony na złym oknie",
                     "Okno VWAP było dobowe zamiast sesyjnego.",
                     data="2026-07-20", plik=p, chlodz=False)
    # Bliźniak leży WYŁĄCZNIE w ACTA — dokładnie stan po schłodzeniu. Treść musi być
    # rozłączna z lekcją aktywną, inaczej test mierzyłby czułość predykatu, nie zasięg.
    ps._dopisz_archiwum([{"naglowek": "### 2026-07-01 — Model GARCH nie zbiega na krótkiej próbce",
                          "data": "2026-07-01",
                          "tytul": "Model GARCH nie zbiega na krótkiej próbce",
                          "tresc": "Estymacja GARCH poniżej 500 obserwacji nie zbiega."}],
                        ps._archiwum_dla(p))

    tytul = "Model GARCH nie zbiega na krótkiej próbce"
    tresc = "Estymacja GARCH poniżej 500 obserwacji nie zbiega."
    assert ps.duplikat_lekcji(tytul, tresc, plik=p, z_archiwum=False) is None, (
        "to jest STARE zachowanie — gdyby łapało, test nie dowodziłby naprawy")
    znaleziona = ps.duplikat_lekcji(tytul, tresc, plik=p)
    assert znaleziona is not None, "bliźniak w archiwum MUSI zostać rozpoznany"
    assert znaleziona.get("schlodzona") is True, "wołający ma wiedzieć, że bliźniak jest w ACTA"


def test_dedup_bez_archiwum_nie_wywala_sie_gdy_acta_nie_istnieje():
    """GRANICA: brak pliku ACTA to normalny stan (świeża pamięć), nie awaria."""
    p = _plik()
    assert not ps._archiwum_dla(p).exists()
    assert ps.duplikat_lekcji("Zupełnie nowa lekcja o czymś innym", "Treść.", plik=p) is None
