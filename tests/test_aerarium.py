"""Testy AERARIUM — skarbca kontekstu i stopni wysiłku.

Reguła Test-Granic: organ podejmuje decyzje na PROGU (200 linii) i na BRAKU DANYCH
(nieznany stopień, niewidoczna pamięć). Obie klasy mają tu testy wartości granicznych,
bo dokładnie na nich Imperium przewracało się wcześniej: „brak danych to abstynencja,
nie wynik" (lekcja 2026-07-26) oraz „ręczna liczba w teście rozjeżdża się z dokumentem"
(lekcja 2026-07-21 — dlatego parytet tabeli sprawdzamy NIEZMIENNIKIEM, nie liczbą).
"""

import json

import imperium.cesarz.aerarium as ae


def _konstytucja(monkeypatch, tmp_path, linie: int):
    """Podstawia CLAUDE.md o dokładnie zadanej liczbie linii."""
    plik = tmp_path / "CLAUDE.md"
    plik.write_text("\n".join(f"linia {i}" for i in range(linie)), encoding="utf-8")
    monkeypatch.setattr(ae, "KONSTYTUCJA", plik)
    return plik


def _bez_pamieci(monkeypatch, tmp_path):
    """Odcina indeks pamięci — inaczej test czytałby prawdziwy dysk Cezara."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "pusto"))


def test_prog_dokladnie_200_linii_nie_alarmuje(monkeypatch, tmp_path):
    """GRANICA: 200 == próg → brak alarmu (limit jest 'ponad 200', nie 'od 200')."""
    _konstytucja(monkeypatch, tmp_path, ae.PROG_LINII_KONSTYTUCJI)
    _bez_pamieci(monkeypatch, tmp_path)
    assert ae.alarmy() == [], "dokładnie na progu jeszcze nie ma długu"


def test_prog_przekroczony_o_jedna_linie_alarmuje(monkeypatch, tmp_path):
    """GRANICA: 201 linii → alarm. Jedna linia za dużo to już dług."""
    _konstytucja(monkeypatch, tmp_path, ae.PROG_LINII_KONSTYTUCJI + 1)
    _bez_pamieci(monkeypatch, tmp_path)
    lista = ae.alarmy()
    assert len(lista) == 1 and "DŁUG KONTEKSTU" in lista[0]


def test_brak_konstytucji_abstynuje_zamiast_zerowac(monkeypatch, tmp_path):
    """Brak pliku → None (nie wiem), NIGDY 0 linii — zero uruchomiłoby fałszywy spokój."""
    monkeypatch.setattr(ae, "KONSTYTUCJA", tmp_path / "nie-ma.md")
    _bez_pamieci(monkeypatch, tmp_path)
    w = ae.waga_kontekstu()
    assert w["linie_konstytucji"] is None
    assert w["skladniki"]["CLAUDE.md"] is None
    assert ae.alarmy(w) == [], "nie oskarżamy o dług pliku, którego nie widzimy"


def test_pusta_konstytucja_to_zmierzone_zero(monkeypatch, tmp_path):
    """GRANICA odwrotna: plik ISTNIEJE i jest pusty → 0 linii to POMIAR, nie None."""
    plik = tmp_path / "CLAUDE.md"
    plik.write_text("", encoding="utf-8")
    monkeypatch.setattr(ae, "KONSTYTUCJA", plik)
    _bez_pamieci(monkeypatch, tmp_path)
    w = ae.waga_kontekstu()
    assert w["linie_konstytucji"] == 0
    assert ae.alarmy(w) == []


def test_brak_zapisu_stopnia_to_none_a_nie_high(monkeypatch, tmp_path):
    """Brak konfiguracji → None. Wartość domyślna MODELU to nie decyzja CEZARA."""
    monkeypatch.delenv("CLAUDE_CODE_EFFORT_LEVEL", raising=False)
    monkeypatch.setattr(ae, "USTAWIENIA", tmp_path / "nie-ma.json")
    st = ae.stopien_domyslny()
    assert st["poziom"] is None and st["zrodlo"] is None


def test_settings_bez_klucza_effort_to_nadal_none(monkeypatch, tmp_path):
    """Plik jest, klucza nie ma → abstynencja. Obecność pliku nie jest odpowiedzią."""
    plik = tmp_path / "settings.json"
    plik.write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    monkeypatch.delenv("CLAUDE_CODE_EFFORT_LEVEL", raising=False)
    monkeypatch.setattr(ae, "USTAWIENIA", plik)
    assert ae.stopien_domyslny()["poziom"] is None


def test_zepsuty_json_nie_wywraca_organu(monkeypatch, tmp_path):
    """Uszkodzony config → abstynencja, nie wyjątek: skarbiec nie może zabić startu sesji."""
    plik = tmp_path / "settings.json"
    plik.write_text("{ to nie jest json", encoding="utf-8")
    monkeypatch.delenv("CLAUDE_CODE_EFFORT_LEVEL", raising=False)
    monkeypatch.setattr(ae, "USTAWIENIA", plik)
    assert ae.stopien_domyslny()["poziom"] is None


def test_poprawny_json_o_zlym_ksztalcie_abstynuje(monkeypatch, tmp_path):
    """GRANICA: JSON POPRAWNY, ale nie-obiekt (lista/napis/liczba) → abstynencja, nie wyjątek.

    Wada znaleziona recenzją 2026-07-26: łapaliśmy wyłącznie `JSONDecodeError`, więc `[]`
    przechodziło parsowanie i dopiero `.get` wywalało AttributeError — kładąc CAŁY baner
    startowy przez literówkę w lokalnej konfiguracji. Zły kształt = ten sam werdykt co zły
    JSON: nie wiem, jaki stopień, ale hook żyje dalej.
    """
    monkeypatch.delenv("CLAUDE_CODE_EFFORT_LEVEL", raising=False)
    for tresc in ("[]", '"high"', "42", "null"):
        plik = tmp_path / "settings.json"
        plik.write_text(tresc, encoding="utf-8")
        monkeypatch.setattr(ae, "USTAWIENIA", plik)
        assert ae.stopien_domyslny()["poziom"] is None, f"zły kształt {tresc} ma abstynować"


def test_obcy_katalog_projektu_nie_udaje_naszego(monkeypatch, tmp_path):
    """GRANICA: JEDEN katalog w ~/.claude/projects, ale CUDZY → pusto, nie „pewnie ten".

    Wcześniejszy fallback („jeden = nasz") podawał cudzą pamięć i cudzy koszt hooka jako
    pomiar TEGO projektu. Fałszywa liczba jest gorsza od jej braku — nie da się jej odróżnić
    od prawdziwej (Prawo I).
    """
    (tmp_path / "projects" / "C--Gdzies-inny-projekt" / "sesja" / "tool-results").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    assert ae._katalogi_projektu() == []
    assert ae.koszt_hooka() is None, "cudzy wydruk hooka nie jest naszym pomiarem"


def test_zmienna_srodowiskowa_bije_settings(monkeypatch, tmp_path):
    """Kolejność wg dokumentacji Claude Code: zmienna środowiskowa nadpisuje ustawienia."""
    plik = tmp_path / "settings.json"
    plik.write_text(json.dumps({"effortLevel": "low"}), encoding="utf-8")
    monkeypatch.setattr(ae, "USTAWIENIA", plik)
    monkeypatch.setenv("CLAUDE_CODE_EFFORT_LEVEL", "xhigh")
    st = ae.stopien_domyslny()
    assert st["poziom"] == "xhigh" and st["imie"] == "TRIBUNUS"


def test_nieznany_stopien_nie_wymysla_imienia(monkeypatch, tmp_path):
    """Nieznana nazwa poziomu → '?', nie zgadywanie ani wyjątek (Prawo I)."""
    monkeypatch.setenv("CLAUDE_CODE_EFFORT_LEVEL", "hiperultra")
    assert ae.stopien_domyslny()["imie"] == "?"


def test_pamiec_niewidoczna_abstynuje(monkeypatch, tmp_path):
    """Indeks pamięci leży POZA repo — nieobecny w tym środowisku ≠ nieistniejący."""
    _konstytucja(monkeypatch, tmp_path, 10)
    _bez_pamieci(monkeypatch, tmp_path)
    assert ae.waga_kontekstu()["skladniki"]["MEMORY.md"] is None


def test_kazde_imie_gradus_jest_w_konstytucji():
    """PARYTET kod↔dokument: tabela stopni w CLAUDE.md musi wymieniać każdy stopień z kodu —
    IMIENIEM **oraz** KLUCZEM WYSIŁKU.

    Sprawdzamy NIEZMIENNIK (obecność), nie liczbę wierszy — ręczna liczba w teście rozjechała
    się już raz (test_sigillarium, 07-21). Tabela może rosnąć; dokument nie ma prawa gubić
    stopnia.

    KLUCZ DOPISANY PO RECENZJI 2026-07-26: wcześniej test pilnował wyłącznie rzymskich imion,
    więc dokument mógł przypisać CENTURIO zły poziom (`medium` zamiast `high`) i parytet
    nadal świeciłby zielono — a to właśnie poziom, nie imię, decyduje o doborze zadań i
    koszcie wachty. Porównujemy sam klucz (pierwszy człon), bo `GRADUS` trzyma dla stopni
    sesyjnych opis w rodzaju „ultracode (ustawienie Claude Code)", którego dokument nie
    cytuje dosłownie — parytet ma pilnować treści, nie interpunkcji.
    """
    ŹRÓDŁO = ae.DOKUMENT_GRADUS          # od 2026-07-27 tabela żyje w skillu na żądanie
    assert ŹRÓDŁO.exists(), (
        "skill /gradus zniknął — konstytucja odsyła do dokumentu, którego nie ma. "
        "To gorsze niż gruby CLAUDE.md: rozkaz stałby się nieosiągalny")
    tekst = ŹRÓDŁO.read_text(encoding="utf-8")
    brak_imion = [g["imie"] for g in ae.GRADUS if g["imie"] not in tekst]
    assert not brak_imion, f"stopnie w kodzie, ale nie w /gradus: {brak_imion}"
    brak_kluczy = [g["effort"].split()[0] for g in ae.GRADUS
                   if g["effort"].split()[0] not in tekst]
    assert not brak_kluczy, f"poziomy wysiłku w kodzie, ale nie w /gradus: {brak_kluczy}"
    # Konstytucja musi ZOSTAWIĆ ślad: bez linii-wyzwalacza nikt nie trafi do skilla.
    konst = ae.KONSTYTUCJA.read_text(encoding="utf-8")
    assert "/gradus" in konst, "konstytucja zgubiła wyzwalacz do tabeli stopni"


def test_poziomy_trwale_sa_podzbiorem_gradus():
    """Spójność wewnętrzna: nie wolno deklarować jako trwałego stopnia, którego nie znamy."""
    znane = {g["effort"] for g in ae.GRADUS}
    assert set(ae.POZIOMY_TRWALE) <= znane


def test_zaden_stopien_sesyjny_nie_jest_trwaly():
    """Stopień SESYJNY (wygasa z wachtą) nie ma prawa trafić do settings.json.

    Wcześniej niezmiennik obejmował wyłącznie `max`, choć dokumentacja modułu od początku
    klasyfikuje jako nietrwałe OBA: `max` (DICTATOR — władza nadzwyczajna, wygasała z czasem)
    i `ultracode` (PRAEFECTUS FABRUM — ustawienie sesji Claude Code). Ochrona zastosowana
    wybiórczo jest ochroną pozorną — to nasza własna lekcja z 07-21, tu powtórzona przez
    recenzenta zewnętrznego. Lista sesyjnych czytana z KODU, nie wypisana ręcznie, żeby
    kolejny dodany stopień nie wypadł z niej po cichu.
    """
    sesyjne = [g["effort"].split()[0] for g in ae.GRADUS
               if g["effort"].split()[0] not in ae.POZIOMY_TRWALE]
    assert "max" in sesyjne and "ultracode" in sesyjne, (
        "oba stopnie nietrwałe muszą być rozpoznane jako sesyjne — inaczej test niczego nie broni")
    for stopien in sesyjne:
        assert stopien not in ae.POZIOMY_TRWALE, f"stopień sesyjny {stopien} nie może być trwały"


def test_nadzor_bez_zapisanego_wydruku_abstynuje(monkeypatch, tmp_path):
    """Brak zapisanych wydruków hooka → None (nie wiem), nie 0 znaków.

    Zero znaczyłoby „hook nic nie kosztuje" — fałsz groźniejszy od milczenia, bo
    uzasadniałby dokładanie kolejnych meldunków bez rachunku."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "pusto"))
    assert ae.koszt_hooka() is None


def test_nadzor_liczy_najciezszy_blok(monkeypatch, tmp_path):
    """Nadzór wskazuje blok dominujący — po to jest, żeby koszt nie rósł anonimowo."""
    kat = tmp_path / "projects" / "imperial-mesh-vortex" / "sesja" / "tool-results"
    kat.mkdir(parents=True)
    (kat / "hook-1-stdout.txt").write_text(
        "[hook] drobny\n♾️ CIEZKI BLOK\n" + ("x" * 500 + "\n") * 4,
        encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    kh = ae.koszt_hooka()
    assert kh is not None
    assert kh["najciezszy_blok"]["naglowek"].startswith("♾️")
    assert kh["najciezszy_blok"]["udzial_proc"] > 50


def test_nadzor_pusty_plik_nie_dzieli_przez_zero(monkeypatch, tmp_path):
    """GRANICA: pusty wydruk → 0 znaków i BRAK bloku, bez ZeroDivisionError."""
    kat = tmp_path / "projects" / "imperial-mesh-vortex" / "sesja" / "tool-results"
    kat.mkdir(parents=True)
    (kat / "hook-1-stdout.txt").write_text("", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    kh = ae.koszt_hooka()
    assert kh["znaki"] == 0 and kh["najciezszy_blok"] is None


def test_banner_nie_pada_bez_zadnych_danych(monkeypatch, tmp_path):
    """Baner MUSI się wydrukować nawet gdy nie ma nic — hook nie może paść na skarbcu."""
    monkeypatch.setattr(ae, "KONSTYTUCJA", tmp_path / "nie-ma.md")
    monkeypatch.setattr(ae, "USTAWIENIA", tmp_path / "nie-ma.json")
    monkeypatch.setattr(ae, "KATALOG_SKILLI", tmp_path / "nie-ma")
    monkeypatch.delenv("CLAUDE_CODE_EFFORT_LEVEL", raising=False)
    _bez_pamieci(monkeypatch, tmp_path)
    tekst = ae.banner()
    assert "AERARIUM" in tekst and "NIEZNANY" in tekst
