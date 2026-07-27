"""Testy Bibliotekarza-Zwiadowcy (narzedzia/bibliotekarz.py) — dyscyplina i cząstki.

Nie dotykamy DeepSeek API (koszt) — testujemy pure logic + ścieżkę dry-run (glos=None)."""
import sys
import os
import json
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "narzedzia", "rag"))

import narzedzia.bibliotekarz as bib
from narzedzia.bibliotekarz import (
    _fragmenty_tekst, scout_temat, _SYSTEM, _topk_arg, _tematy_ukonczone,
    _fts_bezpieczne, rozwin_zapytanie, krytyka_kandydatow,
)

_FakeWynik = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")


def test_fragmenty_tekst_cytuje_zrodlo_i_przycina():
    w = _FakeWynik("BIB-010", "Chan", 122, "x" * 2000, -1.0, "biblioteka")
    txt = _fragmenty_tekst([w])
    assert "BIB-010" in txt and "Chan" in txt and "chunk 122" in txt
    # tekst przycięty do 900 znaków (ochrona kontekstu/tokenów)
    assert txt.count("x") == 900


def test_system_prompt_wymusza_dyscypline():
    # ŻELAZNE ZASADY: hipoteza nie fakt, cytuj źródło, jak zmierzyć, nie konfabuluj
    for fraza in ["HIPOTEZA", "BIB-xxx", "ZMIERZYĆ", "konfabuluj"]:
        assert fraza in _SYSTEM


def test_scout_dry_run_nie_wola_api():
    # glos=None → ścieżka dry-run: zwraca dict bez wywołania DeepSeek (RAG realny, szybki FTS)
    czastka = scout_temat(None, "mean reversion", topk=3, tryb="fts")
    assert czastka["temat"] == "mean reversion"
    assert "kandydaci" in czastka and "ts" in czastka
    assert czastka["kandydaci"] in ("(dry-run — DeepSeek pominięty)", "(brak fragmentów RAG)")


def test_czastka_jest_json_serializowalna():
    czastka = {"temat": "x", "zrodla": ["BIB-001"], "kandydaci": "⚠️ kandydat", "ts": 1.0}
    odczyt = json.loads(json.dumps(czastka, ensure_ascii=False))
    assert odczyt["kandydaci"] == "⚠️ kandydat" and odczyt["zrodla"] == ["BIB-001"]


def test_topk_arg_odrzuca_poza_zakresem():
    # Cubic P2: --topk poza [1, _TOPK_MAX] → błąd zanim ruszy RAG/płatne API (granice).
    import argparse
    import pytest
    assert _topk_arg("6") == 6 and _topk_arg("1") == 1 and _topk_arg("20") == 20
    for zly in ("0", "-3", "21", "9999"):
        with pytest.raises(argparse.ArgumentTypeError):
            _topk_arg(zly)


def test_scout_domyslnie_korpus_biblioteka(monkeypatch):
    # U1 (anty-echo, Prawo XVI): scout domyślnie czyta TYLKO korpus 'biblioteka' (książki),
    # nie 'dane'/'docs'. Sprawdzamy, że korpus jest forwardowany do RAG i domyślnie = biblioteka.
    import szukaj as szukaj_mod
    zebrane = {}

    def fake_szukaj(temat, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zebrane["korpus"] = korpus
        return []

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    scout_temat(None, "mean reversion", topk=3, tryb="fts")
    assert zebrane["korpus"] == "biblioteka"          # domyślnie tylko książki
    scout_temat(None, "mean reversion", topk=3, tryb="fts", korpus=None)
    assert zebrane["korpus"] is None                  # override: None = bez filtra (dawne zachowanie)


def test_tematy_ukonczone_pomija_dry(tmp_path, monkeypatch):
    # Cubic P2: dedup liczy realny zwiad (ok/pusto, stare bez statusu), ale NIE dry-run.
    kol = tmp_path / "kolejka.jsonl"
    kol.write_text(
        json.dumps({"temat": "realny", "status": "ok"}) + "\n"
        + json.dumps({"temat": "podglad", "status": "dry"}) + "\n"
        + json.dumps({"temat": "stary_bez_statusu"}) + "\n",
        encoding="utf-8")
    monkeypatch.setattr(bib, "KOLEJKA", kol)
    done = _tematy_ukonczone()
    assert "realny" in done and "stary_bez_statusu" in done
    assert "podglad" not in done          # dry-run nie blokuje realnego zwiadu


class _FakeGlos:
    """Atrapa GlosImperium — nie dotyka API. Zwraca ustaloną odpowiedź lub rzuca błąd."""
    def __init__(self, odp=None, blad=False):
        self._odp, self._blad = odp, blad

    def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
        # Sygnatura MUSI nadążać za mostem (GlosImperium.zapytaj). Atrapa węższa niż
        # oryginał przepuszcza kod, który w produkcji poleci na TypeError — i odwrotnie:
        # test byłby zielony na innym kontrakcie niż ten, który naprawdę biegnie.
        # Pilnuje tego test_atrapa_glosu_zgodna_z_mostem (parytet sygnatur).
        if self._blad:
            raise RuntimeError("API down")
        return self._odp


def test_fts_bezpieczne_sanityzuje_i_nie_wywala():
    # U2: myślniki/słowa-klucze FTS5 nie mogą wywalić MATCH — sanityzacja do słów złączonych OR.
    assert _fts_bezpieczne("momentum trend-following breakout") == "momentum OR trend OR following OR breakout"
    assert _fts_bezpieczne("mean reversion") == "mean OR reversion"
    assert _fts_bezpieczne("!!!") == "!!!"      # brak słów → oryginał (nie tworzymy pustego MATCH)


def test_rozwin_zapytanie_sanityzuje_i_fallback():
    # U2: rozszerzenie zwraca same słowa; pusta/błędna odpowiedź → fallback na temat (Prawo XV).
    g = _FakeGlos(odp="mean-reversion, bands! overextension zscore")
    assert rozwin_zapytanie(g, "mean reversion") == "mean reversion bands overextension zscore"
    assert rozwin_zapytanie(_FakeGlos(odp="   "), "temat X") == "temat X"    # pusto → temat
    assert rozwin_zapytanie(_FakeGlos(blad=True), "temat Y") == "temat Y"    # błąd API → temat


def test_scout_rozwin_uzywa_rozszerzonego_zapytania(monkeypatch):
    # U2: gdy rozwin=True i jest glos — RAG idzie na ROZSZERZONYM (sanityzowanym) zapytaniu, nie surowym.
    import szukaj as szukaj_mod
    zebrane = {}

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zebrane["q"] = q
        return []

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    cz = scout_temat(_FakeGlos(odp="momentum breakout volatility"), "momentum", topk=3, rozwin=True)
    assert cz["zapytanie"] == "momentum breakout volatility"      # rozszerzone zachowane w rekordzie
    assert zebrane["q"] == "momentum OR breakout OR volatility"   # do FTS poszło sanityzowane OR


def test_krytyka_kandydatow_fallback_na_blad():
    # U3: błąd API krytyki nie może przekreślić cząstki — zwraca komunikat, nie wyjątek (Prawo XV).
    out = krytyka_kandydatow(_FakeGlos(blad=True), "jakiś kandydat", [])
    assert "niedostępna" in out


def test_scout_krytyka_dodaje_dowody_przeciw(monkeypatch):
    # U3: krytyka=True → drugie retrieval (dowody PRZECIW) + pole 'krytyka' w cząstce.
    from collections import namedtuple
    import szukaj as szukaj_mod
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    zapytania = []

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zapytania.append(q)
        return [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")]

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    cz = scout_temat(_FakeGlos(odp="ocena hipotez"), "momentum", topk=3, krytyka=True)
    assert cz["status"] == "ok"
    assert cz.get("krytyka") == "ocena hipotez"          # pole krytyki obecne
    assert len(zapytania) == 2                           # główne + kontra (osobne retrieval)
    assert "risk" in zapytania[1] and "failure" in zapytania[1]   # kontra-sufiks w drugim zapytaniu


def test_czastka_zapisuje_profil_krytyki_ktory_naprawde_biegl(monkeypatch):
    """
    🚨 DECYZJA, KTÓRA KOSZTUJE, MA BYĆ WIDOCZNA W POMIARZE (2026-07-27).
    Cezar przeniósł KRYTYKĘ na droższy profil `osad` (v4-pro) 07-21, ale cząstka niosła
    wyłącznie `profil` GENERACJI — z ledgera nie dało się udowodnić, czym biegła krytyka;
    wiedzieliśmy to tylko z kodu (pamięć zamiast pomiaru). Test pilnuje, że zapisany profil
    to DOKŁADNIE ten, który poszedł do mostu — inaczej zapis byłby deklaracją, nie dowodem.
    """
    from collections import namedtuple
    import szukaj as szukaj_mod
    from narzedzia.bibliotekarz import _PROFIL_KRYTYKA, _PROFIL_ZWIAD
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda q, **kw: [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])

    uzyte = []

    class _Szpieg(_FakeGlos):
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            uzyte.append(profil)
            return "ocena"

    cz = scout_temat(_Szpieg(odp="ocena"), "momentum", topk=3, krytyka=True)
    assert uzyte == [_PROFIL_ZWIAD, _PROFIL_KRYTYKA]      # generacja tania, krytyka droga
    assert cz["profil"] == _PROFIL_ZWIAD
    assert cz["profil_krytyki"] == uzyte[1], "ledger opisuje inny profil niż ten, który biegł"


def test_raport_alarmuje_o_skazonej_krytyce(tmp_path, monkeypatch):
    """
    🚨 LUKA ZŁAPANA MUTACJĄ (2026-07-27): zawężenie raportu z powrotem do samych kandydatów
    NIE wywracało żadnego testu — bronione było wyłącznie BREVIARIUM. Raport bibliotekarza
    to jednak pierwsze miejsce, gdzie sędzia widzi plon, więc musi krzyczeć o skażonej
    KRYTYCE tak samo jak o skażonym kandydacie (obrona bywa skażona częściej niż propozycja:
    zmierzone 07-26 — kandydaci 0/10 skażonych, krytyka 2/10).
    """
    import szukaj as szukaj_mod
    monkeypatch.setattr(bib, "KOLEJKA", tmp_path / "kolejka.jsonl")
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda q, **kw: [_FakeWynik("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    monkeypatch.setattr(bib, "scout_temat", lambda *a, **kw: {
        "temat": "momentum", "zrodla": ["BIB-001"], "kandydaci": "kandydat wg BIB-001 chunk 1",
        "status": "ok", "krytyka": "zarzut wg BIB-999 chunk 7",
        "probator": {"czysty": True, "opis": "🛡️ PROBATOR: CZYSTY"},
        "probator_krytyka": {"czysty": False, "opis": "🚨 PROBATOR: obce źródło BIB-999"},
    })
    tekst = bib.raport(["momentum"], topk=3, dry_run=True, krytyka=True)
    assert "BIB-999" in tekst, "skażona krytyka przemilczana w raporcie"
    assert "1/1 tematów" in tekst          # sekcja alarmowa PROBATORA odpalona


def test_bez_krytyki_nie_ma_profilu_krytyki(monkeypatch):
    """Granica: bieg bez `--krytyka` nie ma prawa zapisać profilu fazy, która się nie odbyła."""
    from collections import namedtuple
    import szukaj as szukaj_mod
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda q, **kw: [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    cz = scout_temat(_FakeGlos(odp="kandydaci"), "momentum", topk=3, krytyka=False)
    assert "profil_krytyki" not in cz


def test_kontekst_systemu_ma_luki_i_antydup():
    # U4: blok świadomości zawiera instrukcję anty-duplikatów (Prawo XVI) i sekcję luk —
    # albo pusty string, gdy rejestr niedostępny (graceful, Prawo XV). Bez brittle na konkretny klucz.
    from narzedzia.bibliotekarz import _kontekst_systemu
    blok = _kontekst_systemu()
    assert blok == "" or ("Prawo XVI" in blok and "LUKI" in blok and "ISTNIEJĄCE" in blok)


def test_scout_swiadomosc_wstrzykuje_kontekst(monkeypatch):
    # U4: swiadomosc=True dokłada blok świadomości do treści dla DeepSeeka; OFF → nie dokłada.
    from collections import namedtuple
    import szukaj as szukaj_mod
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    monkeypatch.setattr(bib, "_kontekst_systemu", lambda: "\nSENTINEL_KTX")
    zebrane = {}

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            zebrane["tresc"] = tresc
            return "kand"

    scout_temat(G(), "momentum", topk=3, swiadomosc=True)
    assert "SENTINEL_KTX" in zebrane["tresc"]              # ON → kontekst dołączony
    scout_temat(G(), "momentum", topk=3, swiadomosc=False)
    assert "SENTINEL_KTX" not in zebrane["tresc"]          # OFF → bez kontekstu


# ── PROBATOR wpięty w plon (warstwa 1 anty-halucynacyjna, 0 tokenów) ────────────

def _fake_szukaj_bib006(monkeypatch, zrodlo="BIB-006_Carson_Scalping.epub", chunk=8):
    """Podstawia RAG zwracający JEDEN znany fragment — wiemy dokładnie, co model 'dostał'."""
    import szukaj as szukaj_mod

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        return [_FakeWynik(zrodlo, "Carson — Scalping", chunk, "tekst", -1.0, "biblioteka")]

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)


def test_probator_czysty_gdy_model_cytuje_podane_zrodlo(monkeypatch):
    """Cytat zgodny z tym, co podano → werdykt CZYSTY, cząstka bez alarmu."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat 1 wg BIB-006 chunk 8."), "momentum", topk=3)
    assert cz["probator"]["status"] == "CZYSTY" and cz["probator"]["czysty"] is True


def test_probator_lapie_zrodlo_ktorego_nie_podano(monkeypatch):
    """RDZEŃ: model powołuje się na książkę, której NIE dostał → halucynacja citation.
    Cząstka niesie ostrzeżenie do kolejki, którą czyta sędzia-Opus."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-047 Kaufman."), "momentum", topk=3)
    assert cz["probator"]["status"] == "PODEJRZANY"
    assert cz["probator"]["obce_zrodla"] == ["BIB-047"]


def test_probator_domyslnie_wlaczony_i_wylaczalny(monkeypatch):
    """Domyślnie ON (deterministyczny, bez kosztu); da się wyłączyć bez zmiany reszty plonu."""
    _fake_szukaj_bib006(monkeypatch)
    zap = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006."), "momentum", topk=3)
    bez = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006."), "momentum", topk=3, probator=False)
    assert "probator" in zap and "probator" not in bez
    assert zap["kandydaci"] == bez["kandydaci"]         # plon identyczny — organ tylko OPISUJE


def test_probator_nie_zmienia_kandydatow_ani_statusu(monkeypatch):
    """ZASADA WPIĘCIA: organ jest monotonicznie ostrożny — dokłada werdykt, nic nie odrzuca."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-999 (wymyślony)."), "momentum", topk=3)
    assert cz["status"] == "ok"                         # cząstka NADAL trafia do kolejki
    assert cz["kandydaci"] == "Kandydat wg BIB-999 (wymyślony)."


def test_probator_bada_takze_krytyke(monkeypatch):
    """Krytyka to też plon modelu — bada się ją wobec WŁASNYCH fragmentów kontra."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Ocena wg BIB-777."), "momentum", topk=3, krytyka=True)
    assert cz["probator_krytyka"]["obce_zrodla"] == ["BIB-777"]


def test_czastka_z_probatorem_jest_json_serializowalna(monkeypatch):
    """Cząstka idzie do JSONL — werdykt nie może wnieść obiektu nieserializowalnego."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006 chunk 8."), "momentum", topk=3)
    assert json.loads(json.dumps(cz, ensure_ascii=False))["probator"]["status"] == "CZYSTY"


def test_dry_run_nie_dostaje_werdyktu(monkeypatch):
    """Granica: bez odpowiedzi modelu nie ma czego badać — brak pola, nie fałszywy alarm."""
    _fake_szukaj_bib006(monkeypatch)
    assert "probator" not in scout_temat(None, "momentum", topk=3)


# ── DISPENSATOR wpięty: która faza kupuje ile myślenia ──────────────────────────

class _GlosProfilujacy:
    """Atrapa mostu zapamiętująca profil KAŻDEGO wywołania (bez dotykania API)."""

    def __init__(self, odp="odpowiedź"):
        self.odp = odp
        self.wywolania = []

    def zapytaj(self, system_prompt, tresc, temperatura=0.7, profil=None, **kw):
        self.wywolania.append(profil)
        return self.odp


def test_generacja_kandydatow_uzywa_profilu_zwiad(monkeypatch):
    """Objętość ważniejsza od głębi — najtańszy sensowny profil."""
    _fake_szukaj_bib006(monkeypatch)
    g = _GlosProfilujacy("Kandydat wg BIB-006.")
    cz = scout_temat(g, "momentum", topk=3)
    assert g.wywolania == ["zwiad"]
    assert cz["profil"] == "zwiad"


def test_rozwiniecie_zapytania_kupuje_najtaniej(monkeypatch):
    """Rozwijanie tematu w synonimy to ekstrakcja, nie rozważanie → thinking off."""
    _fake_szukaj_bib006(monkeypatch)
    g = _GlosProfilujacy("momentum breakout volatility")
    scout_temat(g, "momentum", topk=3, rozwin=True)
    assert g.wywolania[0] == "klasyfikacja"          # najpierw rozwinięcie
    assert g.wywolania[1] == "zwiad"                 # potem generacja


def test_krytyka_kupuje_glebokosc(monkeypatch):
    """Sceptyk płytszy od proponenta byłby bezużyteczny — krytyka kupuje NAJWIĘCEJ myślenia.

    Od 2026-07-21 (decyzja Cezara po A/B LIBRA MESSIS) krytyka idzie na profil `osad`
    (v4-pro), nie `krytyka` (flash). Test pilnuje RELACJI, nie nazwy: faza krytyki nie może
    być tańsza od fazy zwiadu, bo krytyk słabszy od proponenta zatwierdza własne hipotezy."""
    from imperium.cesarz.dispensator import CENNIK, dobierz
    _fake_szukaj_bib006(monkeypatch)
    g = _GlosProfilujacy("ocena")
    scout_temat(g, "momentum", topk=3, krytyka=True)
    assert g.wywolania == [bib._PROFIL_ZWIAD, bib._PROFIL_KRYTYKA]

    cena = lambda profil: CENNIK[dobierz(profil)["model"]]["wyjscie"]  # noqa: E731
    assert cena(bib._PROFIL_KRYTYKA) >= cena(bib._PROFIL_ZWIAD), \
        "faza krytyki tańsza niż zwiad — sceptyk płytszy od proponenta"


def test_hyginus_nie_sadzi_wlasnego_plonu(monkeypatch):
    """ZASADA ZWIADOWCY WIEDZY: sędzią kandydatów jest Opus, nie DeepSeek.

    NIEZMIENNIK PRZEPISANY 2026-07-21: wcześniej pilnowaliśmy go zakazem NAZWY profilu
    („osad" nie może paść"), co myliło dwie różne rzeczy — *ile myślenia kupujemy* z *jaką
    rolę pełnimy*. Gdy Cezar przeniósł krytykę na profil `osad`, test padł, choć rola się
    nie zmieniła: krytyka wciąż PRODUKUJE kontrargumenty, a werdykt o wejściu do roju wydaje
    Architekt. Teraz pilnujemy tego, o co naprawdę chodziło: Hyginus wykonuje wyłącznie fazy
    zwiadu (rozwinięcie → generacja → krytyka) i ani jednego przejścia więcej."""
    _fake_szukaj_bib006(monkeypatch)
    g = _GlosProfilujacy("x")
    scout_temat(g, "momentum", topk=3, rozwin=True, krytyka=True)
    assert g.wywolania == [bib._PROFIL_ROZWIN, bib._PROFIL_ZWIAD, bib._PROFIL_KRYTYKA], \
        "Hyginus wykonał fazę spoza zwiadu — proponent nie może sądzić własnego plonu"


def test_wszystkie_profile_hyginusa_istnieja_w_dispensatorze():
    """Parytet: literówka w nazwie profilu cicho spadłaby na domyślny (dobierz nie rzuca),
    więc płacilibyśmy inaczej niż sądzimy. Test pilnuje, że nazwy są REALNE."""
    from imperium.cesarz.dispensator import PROFILE
    for profil in (bib._PROFIL_ROZWIN, bib._PROFIL_ZWIAD, bib._PROFIL_KRYTYKA):
        assert profil in PROFILE, profil


def test_atrapa_glosu_zgodna_z_mostem():
    """UODPORNIENIE KLASY: atrapa węższa niż prawdziwy most daje testy zielone na kontrakcie,
    który w produkcji nie istnieje. Każdy parametr `zapytaj` musi dać się podać atrapie."""
    import inspect
    from imperium.cesarz.deepseek_glos import GlosImperium
    prawdziwe = set(inspect.signature(GlosImperium.zapytaj).parameters) - {"self"}
    atrapa = inspect.signature(_FakeGlos.zapytaj)
    ma_kwargs = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in atrapa.parameters.values())
    brakuje = prawdziwe - set(atrapa.parameters)
    assert ma_kwargs or not brakuje, f"atrapa nie przyjmie: {sorted(brakuje)}"


def test_swiadomosc_jest_DOMYSLNIE_wylaczona(monkeypatch):
    """U4 domyślnie OFF od 2026-07-27 (DECYZJA CEZARA po replikacji A/B).

    POWÓD, dla którego to jest test, a nie tylko wartość domyślna: domyślna wartość sama
    z siebie nie broni się przed cichym powrotem. Rozkaz z 07-21 („ON") opierał się na
    tezie −12.1 pp p=0.016, którą przeliczenie naprawionym detektorem OBALIŁO (OFF 39.3%
    vs ON 41.0%, p=0.766 — stary detektor nie widział dubletów WIELKIE_Z_PODKRESLENIEM).
    Replikacja na 256 biegach: −0.7 pp, CI [−7.3, +6.0], p=0.888, moc na −12 pp = 94.2%.
    Koszt zmierzony 1.49×. Powrót do ON bez NOWEGO pomiaru byłby powrotem do płacenia
    połowy więcej za efekt nieodróżnialny od zera.

    Test celowo NIE twierdzi, że U4 szkodzi — moc na 5 pp to tylko 31%, więc małego
    efektu nie wykluczyliśmy. Broniona jest DOMYŚLNOŚĆ, nie teza o szkodliwości."""
    import szukaj as szukaj_mod
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [_FakeWynik("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    monkeypatch.setattr(bib, "_kontekst_systemu", lambda: "\nSENTINEL_KTX")
    zebrane = {}

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            zebrane["tresc"] = tresc
            return "kand"

    scout_temat(G(), "momentum", topk=3)          # BEZ jawnego swiadomosc=
    assert "SENTINEL_KTX" not in zebrane["tresc"]


def test_raport_nie_wstrzykuje_swiadomosci_domyslnie():
    """GRANICA DOMYŚLNOŚCI NA DRUGIM POZIOMIE: `raport()` ma własny parametr `swiadomosc`
    i to ON, a nie `scout_temat`, jest tym, co widzi CLI. Gdyby ktoś przełączył tylko
    jedną z dwóch wartości, decyzja Cezara obowiązywałaby w połowie ścieżek wywołania —
    dokładnie ta klasa wady, którą złapaliśmy przy deprecjonowaniu miary (07-26: objęliśmy
    meldunek, nie deltę). Pytamy sygnatury, więc test nie kosztuje ani jednego calla API."""
    import inspect
    assert inspect.signature(bib.raport).parameters["swiadomosc"].default is False
    assert inspect.signature(scout_temat).parameters["swiadomosc"].default is False


def test_nomenclator_jest_OPT_IN_wylaczony(monkeypatch):
    """ZASADA WPIĘCIA: NOMENCLATOR wchodzi w ścieżkę zwiadu jako opt-in OFF i włącza się
    dopiero po zielonym A/B. Domyślność sprawdzana na OBU poziomach — `raport()` ma własny
    parametr i to JEGO widzi CLI, więc przełączenie jednego z dwóch dałoby decyzję
    obowiązującą w połowie ścieżek wywołania (klasa złapana 07-26 przy delcie BREVIARIUM)."""
    import inspect
    assert inspect.signature(scout_temat).parameters["nomenclator"].default is False
    assert inspect.signature(bib.raport).parameters["nomenclator"].default is False

    import szukaj as szukaj_mod
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [_FakeWynik("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            return "1. Kandydat: VPIN_TOKSYCZNOSC\n- opis\n"

    rec = scout_temat(G(), "momentum", topk=3, probator=False)   # BEZ jawnego nomenclator=
    assert "nomenclator" not in rec, "organ dołożył się do cząstki mimo opt-in OFF"


def test_nomenclator_wlaczony_oznacza_znane_imie(monkeypatch):
    """Gdy WŁĄCZONY — dokłada adnotację, ale wyłącznie DOKŁADA (monotonicznie ostrożny):
    kandydaci w cząstce zostają nietknięci, więc nic, co przeszłoby bez organu, nie ginie."""
    import szukaj as szukaj_mod
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [_FakeWynik("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    plon = "1. Kandydat: VPIN_TOKSYCZNOSC\n- opis\n2. Kandydat: NOWE_POJECIE_XYZ\n- opis\n"

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            return plon

    rec = scout_temat(G(), "momentum", topk=3, probator=False, nomenclator=True)
    assert rec["nomenclator"]["status"] == "podejrzany"
    assert rec["nomenclator"]["podejrzanych"] == 1
    assert rec["nomenclator"]["kandydatow"] == 2
    # `.strip()` robi sam scout_temat od zawsze — porównujemy z tym, co bez organu też by wyszło.
    assert rec["kandydaci"] == plon.strip(), "organ zmienił plon — ma tylko adnotować"


def test_blok_swiadomosci_zawiera_zakaz_duplikatow():
    """Sedno U4: blok musi NAZWAĆ istniejące klucze i zakazać ich powielania.
    Sam fakt wstrzyknięcia czegokolwiek nie wystarczy — treść jest tu mechanizmem."""
    blok = bib._kontekst_systemu()
    if not blok:
        return                                     # brak rejestru → zwiad działa dalej (Prawo XV)
    assert "NIE proponuj duplikatów" in blok
    assert "LUKI" in blok


def test_bez_swiadomosci_da_sie_wylaczyc(monkeypatch):
    """Wyłącznik musi zostać: bieg porównawczy (A/B jakości plonu) wymaga obu ramion."""
    import szukaj as szukaj_mod
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [_FakeWynik("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    monkeypatch.setattr(bib, "_kontekst_systemu", lambda: "\nSENTINEL_KTX")
    zebrane = {}

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7, profil=None, **kw):
            zebrane["tresc"] = tresc
            return "kand"

    scout_temat(G(), "momentum", topk=3, swiadomosc=False)
    assert "SENTINEL_KTX" not in zebrane["tresc"]


# ── WYROK SĘDZIEGO — domknięcie cząstki (2026-07-27) ─────────────────────────

def _kolejka_tymczasowa(monkeypatch, tmp_path):
    import narzedzia.bibliotekarz as b
    plik = tmp_path / "KOLEJKA.jsonl"
    monkeypatch.setattr(b, "KOLEJKA", plik)
    b.osadzone_ts.cache_clear()
    b._znaczniki.cache_clear()   # migawka kolejki jest wspólna dla obu zbiorów znaczników
    return b, plik


def test_wyrok_bez_adresata_jest_ODRZUCONY(monkeypatch, tmp_path):
    """Literówka w `dot_ts` nie może wyglądać jak wydany wyrok (cubic PR #134, P2).

    Sądzona cząstka zostawałaby wtedy w kolejce, a ledger niósłby orzeczenie wskazujące
    w próżnię. Przy 35 cząstkach na wachtę to jedno przestawienie cyfry, nie hipoteza.
    """
    import pytest
    b, _ = _kolejka_tymczasowa(monkeypatch, tmp_path)
    b.zapisz_czastke({"temat": "t", "ts": 100.0, "status": "ok", "kandydaci": "x"})
    with pytest.raises(ValueError, match="nie wskazuje"):
        b.zapisz_wyrok(dot_ts=100.1, temat="t", werdykt="PRZYJETY", uzasadnienie="literówka")
    # GRANICA DRUGIEJ STRONY: poprawny znacznik nadal przechodzi — zawężanie na oślep
    # byłoby równie złe jak brak walidacji (sędzia straciłby możliwość orzekania).
    assert b.zapisz_wyrok(dot_ts=100.0, temat="t", werdykt="PRZYJETY",
                          uzasadnienie="właściwy znacznik") is True


def test_swiezo_zapisana_czastka_jest_od_razu_sadzalna(monkeypatch, tmp_path):
    """Błąd własny 2026-07-27: cache znaczników bez unieważnienia przy zapisie sprawiał,
    że sędzia nie mógł osądzić cząstki, którą sam przed chwilą zapisał."""
    b, _ = _kolejka_tymczasowa(monkeypatch, tmp_path)
    b.osadzone_ts()                      # rozgrzewamy cache PRZED zapisem
    b.zapisz_czastke({"temat": "swieza", "ts": 777.0, "status": "ok", "kandydaci": "x"})
    assert b.zapisz_wyrok(dot_ts=777.0, temat="swieza", werdykt="ODRZUCONY",
                          uzasadnienie="dublet") is True


def test_probator_liczy_TEMATY_nie_plony(monkeypatch, tmp_path):
    """Nagłówek mówi „X/N tematów", więc X musi liczyć TEMATY (cubic PR #134, P3).

    PROBATOR bada oba plony (kandydaci + krytyka), więc jeden temat dokłada do listy dwa
    wpisy. Przy obu skażonych licznik potrafił ogłosić więcej tematów skażonych, niż
    w ogóle skanowano — klasa „licznik, który kłamie".
    """
    import narzedzia.bibliotekarz as b
    oba_plony_jednego_tematu = ["temat A [kandydaci] → cytat spoza",
                                "temat A [krytyka] → cytat spoza"]
    assert b.ile_tematow(oba_plony_jednego_tematu) == 1, "jeden temat policzony dwa razy"
    assert b.ile_tematow(["A [kandydaci] → x", "B [krytyka] → y"]) == 2, "różne tematy sklejone"
    assert b.ile_tematow([]) == 0


def test_wyrok_domyka_czastke(monkeypatch, tmp_path):
    """Cząstka po wyroku przestaje czekać na sędziego — inaczej kolejka rośnie w nieskończoność.

    Powód powstania mechanizmu: kolejka rosła od 2026-07-14 do 43 cząstek NIE dlatego, że
    sędzia zwlekał, tylko dlatego, że nie miał gdzie orzec (brakujący krok procesu wygląda
    identycznie jak zaniedbanie).
    """
    b, _ = _kolejka_tymczasowa(monkeypatch, tmp_path)
    b.zapisz_czastke({"temat": "t", "ts": 111.0, "status": "ok", "kandydaci": "x"})
    assert b.osadzone_ts() == frozenset()
    assert b.zapisz_wyrok(dot_ts=111.0, temat="t", werdykt="ODRZUCONY",
                          uzasadnienie="dubluje Z-01") is True
    assert b.osadzone_ts() == frozenset({111.0})


def test_wyrok_jest_idempotentny(monkeypatch, tmp_path):
    """Drugi wyrok na tę samą cząstkę nie zapada — ledger nie może mnożyć orzeczeń."""
    b, plik = _kolejka_tymczasowa(monkeypatch, tmp_path)
    b.zapisz_czastke({"temat": "t", "ts": 222.0, "status": "ok", "kandydaci": "x"})
    assert b.zapisz_wyrok(dot_ts=222.0, temat="t", werdykt="PRZYJETY", uzasadnienie="nowe") is True
    assert b.zapisz_wyrok(dot_ts=222.0, temat="t", werdykt="ODRZUCONY", uzasadnienie="inne") is False
    linie = [x for x in plik.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert sum(1 for x in linie if '"status": "wyrok"' in x) == 1


def test_wyrok_nie_nadpisuje_plonu_zwiadowcy(monkeypatch, tmp_path):
    """Prawo I: meldunek zwiadowcy zostaje nietknięty; wyrok to OSOBNY rekord."""
    import json
    b, plik = _kolejka_tymczasowa(monkeypatch, tmp_path)
    b.zapisz_czastke({"temat": "t", "ts": 333.0, "status": "ok", "kandydaci": "PLON"})
    b.zapisz_wyrok(dot_ts=333.0, temat="t", werdykt="CZESCIOWO", uzasadnienie="1 z 3")
    rek = [json.loads(x) for x in plik.read_text(encoding="utf-8").splitlines() if x.strip()]
    plon = [r for r in rek if r.get("status") == "ok"]
    assert len(plon) == 1 and plon[0]["kandydaci"] == "PLON" and "werdykt" not in plon[0]


def test_wyrok_odrzuca_nieznany_werdykt_i_puste_uzasadnienie(monkeypatch, tmp_path):
    """GRANICA: wyrok bez powodu albo z wymyśloną etykietą to nie wyrok."""
    import pytest
    b, _ = _kolejka_tymczasowa(monkeypatch, tmp_path)
    with pytest.raises(ValueError):
        b.zapisz_wyrok(dot_ts=1.0, temat="t", werdykt="MOZE", uzasadnienie="bo tak")
    with pytest.raises(ValueError):
        b.zapisz_wyrok(dot_ts=1.0, temat="t", werdykt="PRZYJETY", uzasadnienie="   ")


def test_breviarium_odejmuje_osadzone(monkeypatch, tmp_path):
    """Sąd ma SPŁACAĆ dług przeglądu, nie podnosić go: wyrok wypada z obu liczników."""
    import imperium.oczy.breviarium as br
    plik = tmp_path / "KOLEJKA.jsonl"
    import json
    with plik.open("w", encoding="utf-8") as f:
        for r in ({"temat": "a", "ts": 1.0, "status": "ok"},
                  {"temat": "b", "ts": 2.0, "status": "ok"},
                  {"status": "wyrok", "dot_ts": 1.0, "temat": "a", "werdykt": "ODRZUCONY",
                   "uzasadnienie": "dublet", "ts": 9.0}):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    monkeypatch.setattr(br, "KOLEJKA_HIPOTEZ", plik)
    s = br.stan_hyginusa()
    assert s["czeka_na_sedziego"] == 1, "osądzona cząstka nadal liczona jako dług"
    assert s["czastek"] == 2, "wyrok policzony jako nowa cząstka plonu"
    assert s["osadzonych"] == 1
