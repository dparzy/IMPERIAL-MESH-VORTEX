"""Testy LIBRA MESSIS — wagi plonu Hyginusa (A/B jakości zwiadu).

Zero wywołań API: testujemy WYŁĄCZNIE deterministyczny rdzeń (dzielnik kandydatów,
leksykon, metryki, rejestr, agregacja). Reguła Test-Granic: pusty plon, proza bez
numeracji, warianty składni nagłówka, brak ramienia, wznawianie.
"""
import json
import logging
import os
import sys

logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia import ab_plon_hyginusa as lm  # noqa: E402


def test_leksykon_ma_dowod_w_kodzie():
    """Prawo I: każde pojęcie 'już mamy' musi mieć dowód w ŻYWYM kodzie.

    Bez tego miara duplikatów oskarżałaby zwiad o proponowanie czegoś, czego Imperium
    nie posiada — a wpis przeterminowany kłamałby cicho przez kolejne sesje."""
    assert lm.niezweryfikowane() == [], "leksykon wskazuje moduły nieobecne w kodzie"
    assert len(lm.leksykon_roju()) >= 30


def test_weryfikacja_leksykonu_zglasza_widmo(monkeypatch):
    """TEST NEGATYWNY — bez niego zielone 'wszystko potwierdzone' nic nie dowodzi.

    Zmierzone 2026-07-21: weryfikacja skanowała korpus RAZEM z plikiem deklarującym leksykon,
    więc każdy wpis znajdował dowód we własnej linijce i przechodziła ZAWSZE. Test pozytywny
    też był zielony — bo testował tę samą zatrutą funkcję. Tu wstrzykujemy pojęcie, którego
    w kodzie NIE MA: jeśli weryfikacja go nie zgłosi, znaczy że znów potwierdza samą siebie."""
    widmo = r"\bzupelnie[- ]nieistniejace[- ]pojecie\b"
    monkeypatch.setitem(lm.KONCEPTY_IMPERIUM, widmo, "zupelnie_nieistniejacy_modul_xyz")
    lm._korpus_kodu.cache_clear()
    lm.leksykon_roju.cache_clear()
    try:
        assert widmo in lm.niezweryfikowane(), "weryfikacja przepuszcza pojęcie-widmo"
        assert widmo not in [w for w, _ in lm.leksykon_roju()], "widmo weszło do leksykonu"
    finally:
        lm._korpus_kodu.cache_clear()
        lm.leksykon_roju.cache_clear()


def test_naglowek_nie_liczy_wzmianki_w_uzasadnieniu():
    """Wzmianka o naszym module w ZAPRZECZENIU nie jest propozycją duplikatu.

    Ramię U4=ON dostaje polecenie 'dopisz, czy kandydat NIE dubluje istniejącego modułu',
    więc z definicji wymienia nasze moduły. Licząc całe ciało bloku, miara karała ramię za
    wykonanie instrukcji i pokazywała wynik ODWROTNY do prawdy (31% vs 14%)."""
    lex = lm.leksykon_roju()
    zaprzeczenie = ("1. **Kandydat: Wskaznik glebokosci ksiegi zlecen**\n"
                    "- **Luka/nowosc:** wnosi NOWA informacje; istnieje V-03 CVD, "
                    "ale to wolumen transakcyjny, a nie ksiazkowy.")
    propozycja = "1. **Kandydat: CVD jako miara presji kupujacych**\n- opis mechanizmu"
    assert lm.policz_duplikaty(zaprzeczenie, lex)[0] == 0
    assert lm.policz_duplikaty(propozycja, lex)[0] == 1


def test_dzielnik_zna_warianty_skladni():
    """Granica zmierzona na realnym plonie: model numeruje na kilka sposobów.

    Pierwsza wersja znała tylko '1. ' i sklejała 21 z 33 cząstek w jeden blok
    (ślepa plama detektora na wariant składni — Księga Wad)."""
    warianty = [
        "1. **Kandydat A**\nopis\n2. **Kandydat B**\nopis",
        "### 1. **Kandydat A**\ntresc\n### 2. **Kandydat B**\ntresc",
        "1) Kandydat A\ntresc\n2) Kandydat B\ntresc",
        "**1.** Kandydat A\ntresc\n**2.** Kandydat B\ntresc",
    ]
    for tekst in warianty:
        assert len(lm.podziel_kandydatow(tekst)) == 2, f"nie rozbito: {tekst[:30]!r}"


def test_dzielnik_granice_pusto_i_proza():
    """Pusty plon → brak bloków; proza bez numeracji → JEDEN blok (nie zero)."""
    assert lm.podziel_kandydatow("") == []
    assert lm.podziel_kandydatow("   \n  ") == []
    assert len(lm.podziel_kandydatow("Sama proza bez numeracji, ale to nadal plon.")) == 1


def test_duplikaty_lapia_pojecie_ktore_juz_mamy():
    """Kandydat nazywający Kelly'ego/VPIN = duplikat; kandydat spoza leksykonu = nowość."""
    lex = lm.leksykon_roju()
    stary = "1. **Kryterium Kelly'ego** do sizingu\n2. **VPIN** jako miara toksyczności"
    nowy = "1. **Sezonowość księżycowa** wg fazy satelity\n2. **Indeks pogodowy** dla rolnictwa"
    assert lm.policz_duplikaty(stary, lex)[0] == 2
    assert lm.policz_duplikaty(nowy, lex)[0] == 0


def test_miara_nie_nasyca_sie_na_zywym_plonie():
    """REGRESJA na wadę zmierzoną 2026-07-21: pierwsza wersja flagowała 95% bloków.

    Miara nasycona nie odróżnia ramion, więc A/B zbudowane na niej byłoby bezwartościowe.
    Biegnie po PRAWDZIWEJ kolejce hipotez (jeśli istnieje) — nie po syntetyce."""
    from narzedzia.bibliotekarz import KOLEJKA
    if not KOLEJKA.exists():
        return
    lex = lm.leksykon_roju()
    bloki = dubel = 0
    for linia in KOLEJKA.read_text(encoding="utf-8").splitlines():
        if not linia.strip():
            continue
        rec = json.loads(linia)
        if rec.get("status") != "ok":
            continue
        d, k, _ = lm.policz_duplikaty(rec.get("kandydaci", ""), lex)
        dubel += d
        bloki += k
    if bloki < 20:          # za mało danych, by cokolwiek twierdzić (Prawo I)
        return
    udzial = dubel / bloki
    assert 0.02 < udzial < 0.80, f"miara nie różnicuje: {udzial:.0%} bloków oflagowanych"


def test_rejestr_nie_jest_produkcyjna_kolejka():
    """ŻELAZNA ZASADA organu: narzędzie mierzące NIE zmienia mierzonego stanu.

    Powód zmierzony 2026-07-21: bieg weryfikacyjny `--dry-run` zaśmiecił produkcyjną
    kolejkę hipotez. Waga plonu pisze wyłącznie do własnego rejestru."""
    from narzedzia.bibliotekarz import KOLEJKA
    assert lm.REJESTR.resolve() != KOLEJKA.resolve()
    zrodlo = (lm.ROOT / "narzedzia" / "ab_plon_hyginusa.py").read_text(encoding="utf-8")
    assert "zapisz_czastke" not in zrodlo, "waga plonu nie ma prawa pisać do kolejki hipotez"


def test_rejestr_zapis_odczyt_i_wznawianie(tmp_path):
    """Cząstka → zapis → następna: powtórzony bieg pomija to, co już zmierzone."""
    p = tmp_path / "ab.jsonl"
    assert lm.wczytaj(p) == []
    assert lm.zrobione("u4", p) == set()
    lm.zapisz({"bieg": "u4", "ramie": "on", "temat": "T1", "kandydatow": 3}, p)
    lm.zapisz({"bieg": "u4", "ramie": "off", "temat": "T1", "kandydatow": 5}, p)
    lm.zapisz({"bieg": "profile", "ramie": "osad", "temat": "T1"}, p)
    # Rekordy bez pola `runda` czytamy jako rundę 1 — wsteczna zgodność z pomiarami
    # sprzed wprowadzenia rund (nie unieważniamy ich).
    assert lm.zrobione("u4", p) == {("T1", "on", 1), ("T1", "off", 1)}
    assert lm.zrobione("profile", p) == {("T1", "osad", 1)}
    # Ta sama para w NOWEJ rundzie to nowa obserwacja — nie jest „już zrobiona".
    lm.zapisz({"bieg": "u4", "ramie": "on", "temat": "T1", "runda": 2, "kandydatow": 4}, p)
    assert ("T1", "on", 2) in lm.zrobione("u4", p)


def test_rejestr_pomija_uszkodzona_linie(tmp_path):
    """Granica: uszkodzony JSON nie zabija odczytu całego rejestru (Prawo I)."""
    p = tmp_path / "ab.jsonl"
    p.write_text('{"bieg":"u4","ramie":"on","temat":"A"}\n{ zepsute\n', encoding="utf-8")
    assert len(lm.wczytaj(p)) == 1


def test_blad_sieci_nie_utrwala_sie_jako_wynik(tmp_path):
    """Zerwane łącze → rekord 'blad', ale jednostka WRACA do kolejki przy wznowieniu.

    Zmierzone 2026-07-21: pierwszy pełny bieg padł na APITimeoutError przy 11 z 16
    pomiarów. Gdyby porażka liczyła się jako zrobiona, ramię zostałoby na zawsze
    niepełne, a agregat cicho porównywałby różne liczby tematów."""
    p = tmp_path / "ab.jsonl"
    lm.zapisz({"bieg": "u4", "ramie": "on", "temat": "T1", "status": "blad",
               "blad": "APITimeoutError"}, p)
    assert lm.zrobione("u4", p) == set()          # wraca do ponowienia
    assert lm.agreguj("u4", p) == {}              # nie wchodzi do wyniku


def test_ponowienie_oddaje_wynik_po_awarii(monkeypatch):
    """Chwilowy błąd sieci jest przeżywalny; trwały kończy się jawną porażką, nie ciszą."""
    monkeypatch.setattr(lm.time, "sleep", lambda *_: None)   # bez realnego czekania
    stan = {"n": 0}

    def chwiejny():
        stan["n"] += 1
        if stan["n"] < 3:
            raise TimeoutError("zryw")
        return "plon"

    wynik, blad = lm._z_ponowieniem(chwiejny, "test")
    assert wynik == "plon" and blad is None

    wynik2, blad2 = lm._z_ponowieniem(lambda: (_ for _ in ()).throw(TimeoutError("trwały")),
                                      "test")
    assert wynik2 is None and "TimeoutError" in blad2


def test_agreguj_sumuje_ramiona(tmp_path):
    """Agregacja liczy per ramię; brak pomiarów → puste (nie zera udające wynik)."""
    p = tmp_path / "ab.jsonl"
    assert lm.agreguj("u4", p) == {}
    for ramie, kand, dubel, koszt in (("on", 4, 1, 0.001), ("on", 6, 1, 0.002),
                                      ("off", 5, 4, 0.001)):
        lm.zapisz({"bieg": "u4", "ramie": ramie, "temat": f"t{kand}", "kandydatow": kand,
                   "duplikaty": dubel, "koszt_usd": koszt, "znakow": 100, "czas_s": 1.0,
                   "probator_czysty": True}, p)
    a = lm.agreguj("u4", p)
    assert a["on"]["kandydatow"] == 10 and a["on"]["duplikatow"] == 2
    assert a["on"]["duplikaty_pct"] == 20.0
    assert a["off"]["duplikaty_pct"] == 80.0
    assert a["on"]["koszt_usd"] == 0.003


def test_agreguj_bez_kosztu_nie_udaje_zera(tmp_path):
    """Granica: brak `usage` z API → koszt None ('nie wiem'), nie 0.0 ('za darmo')."""
    p = tmp_path / "ab.jsonl"
    lm.zapisz({"bieg": "u4", "ramie": "on", "temat": "t", "kandydatow": 1,
               "duplikaty": 0, "koszt_usd": None}, p)
    assert lm.agreguj("u4", p)["on"]["koszt_usd"] is None


def test_argumenty_kosztu_maja_granice():
    """Argument sterujący rozmiarem PŁATNEGO biegu musi być ograniczony przy parsowaniu.

    Bez granicy literówka ('--tematy 800') zamienia eksperyment za centy w rachunek —
    znana klasa z Księgi Wad, złapana przez skan_wad_kodu na tym właśnie pliku."""
    import argparse
    for zly in ("0", "-1", str(lm._TEMATY_MAX + 1)):
        try:
            lm._tematy_arg(zly)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError(f"--tematy przepuściło wartość {zly}")
    assert lm._tematy_arg("8") == 8


def test_raport_bez_danych_mowi_wprost(tmp_path):
    """Pusty rejestr → komunikat, nie tabela zer."""
    assert "brak pomiarów" in lm.raport_tekstowy("u4", tmp_path / "nie_ma.jsonl")


# ── ŚLEPA PLAMA DETEKTORA (nawrót klasy, 2026-07-27) ─────────────────────────

def test_naglowek_lapie_wszystkie_zmierzone_warianty():
    """GRANICA: 7 formatów nagłówka ZMIERZONYCH w kolejce musi dzielić plon.

    Poprzednia naprawa dołożyła JEDEN wariant zamiast domknąć klasę — 4 z 7 nadal
    sklejały cały plon w jeden blok, więc licznik kandydatów kłamał w dół.
    """
    from narzedzia.ab_plon_hyginusa import podziel_kandydatow
    warianty = [
        "1. **Kandydat: X**\n- opis\n2. **Kandydat: Y**\n- opis",
        "### 1. **X**\n- opis\n### 2. **Y**\n- opis",
        "### Kandydat A: X\n- opis\n### Kandydat B: Y\n- opis",
        "### Kandydat 1: X\n- opis\n### Kandydat 2: Y\n- opis",
        "1: X\n- opis\n2: Y\n- opis",
        "**1. Kandydat: X**\n- opis\n**2. Kandydat: Y**\n- opis",
        "- **Kandydat: X**\n- opis\n- **Kandydat: Y**\n- opis",
    ]
    for tekst in warianty:
        assert len(podziel_kandydatow(tekst)) == 2, f"nie rozdzielone: {tekst[:24]!r}"


def test_naglowek_nie_lapie_zagniezdzonych_krokow():
    """GRANICA DRUGA STRONA: wcięta lista kroków to TREŚĆ kandydata, nie kandydaci.

    Pierwsza wersja tej naprawy dopisała swobodne `\s*`, co zniosło limit wcięcia
    `^[ \t]{0,3}` i dołożyło 12 widmowych „kandydatów" w jednym rekordzie.
    """
    from narzedzia.ab_plon_hyginusa import podziel_kandydatow
    tekst = ("1. **Kandydat: DSR**\n"
             "   - **Jak zmierzyć**:\n"
             "     1. Oblicz surowy SR.\n"
             "     2. Zastosuj DSR.\n"
             "     3. Porównaj wyniki.\n"
             "2. **Kandydat: PBO**\n"
             "     1. Zbuduj foldy.\n")
    assert len(podziel_kandydatow(tekst)) == 2


def test_naglowek_nie_lapie_liczby_dziesietnej():
    """GRANICA: „2.5" nie jest nagłówkiem — po numerze wymagana spacja."""
    from narzedzia.ab_plon_hyginusa import podziel_kandydatow
    assert len(podziel_kandydatow("1. **Kandydat: X**\n2.5 raza wieksza wartosc\n")) == 1


def test_duplikat_wykryty_gdy_nazwa_ma_podkreslenie():
    """GRANICA: `VPIN_TOKSYCZNOSC` dubluje Z-01, choć `\bvpin\b` nie trafia w `_`.

    ZMIERZONE 2026-07-27: ramię U4 ON nazywało 34.7% kandydatów naszą konwencją
    WIELKIE_Z_PODKRESLENIEM, ramię OFF 0% — detektor był ślepy dokładnie tam, gdzie
    działał badany zabieg, i cały werdykt A/B U4 był artefaktem tej ślepoty.
    """
    import re

    from narzedzia.ab_plon_hyginusa import policz_duplikaty
    lek = ((r"\bvpin\b", re.compile(r"\bvpin\b", re.IGNORECASE)),)
    dubel, bloki, trafione = policz_duplikaty("1. **Kandydat: VPIN_TOKSYCZNOSC**\n- opis\n", lek)
    assert (dubel, bloki) == (1, 1) and trafione == [r"\bvpin\b"]


def test_duplikat_nadal_wykrywany_bez_podkreslenia():
    """Normalizacja `_`→spacja nie może zepsuć zwykłego dopasowania."""
    import re

    from narzedzia.ab_plon_hyginusa import policz_duplikaty
    lek = ((r"\bvpin\b", re.compile(r"\bvpin\b", re.IGNORECASE)),)
    dubel, _, _ = policz_duplikaty("1. **Kandydat: VPIN toksycznosc**\n- opis\n", lek)
    assert dubel == 1


def test_nazwa_bez_dubletu_nie_jest_oskarzana():
    """GRANICA: normalizacja nie może produkować trafień z niczego."""
    import re

    from narzedzia.ab_plon_hyginusa import policz_duplikaty
    lek = ((r"\bvpin\b", re.compile(r"\bvpin\b", re.IGNORECASE)),)
    dubel, _, _ = policz_duplikaty("1. **Kandydat: SKEW_PREMIA**\n- opis\n", lek)
    assert dubel == 0
