"""
Testy PROBATORA — Strażnika Cytatów (warstwa 1 anty-halucynacyjna Hyginusa).

Weryfikuje:
  • wyodrębnianie cytatów we WSZYSTKICH wariantach składni + test NEGATYWNY
    (Księga Wad #53: detektor pokrywający jedną formę zapisu to ślepa plama),
  • rdzeń: cytat spoza PODANYCH fragmentów = halucynacja, nawet gdy książka istnieje,
  • abstencja jako wynik POPRAWNY (karanie milczenia uczy konfabulacji),
  • granice: brak fragmentów, pusta odpowiedź, chunk bez wiedzy o numeracji,
    numer chunku odległy od cytatu, BIB-6 vs BIB-006.
"""

from imperium.pretorianie import probator as pb


class _Wynik:
    """Atrapa wyniku RAG (ma .zrodlo i .nr_chunk jak obiekty z szukaj())."""

    def __init__(self, zrodlo: str, nr_chunk: int):
        self.zrodlo = zrodlo
        self.nr_chunk = nr_chunk


def _fragmenty():
    return [
        _Wynik("BIB-006_Carson_High-Probability-Scalping.epub", 8),
        _Wynik("BIB-006_Carson_High-Probability-Scalping.epub", 7),
        _Wynik("BIB-047_Kaufman_Trading-Systems-and-Methods.pdf", 1),
    ]


# ── Wyodrębnianie cytatów: warianty składni + test negatywny ────────────────────

def test_wyodrebnia_wszystkie_warianty_zapisu():
    """Detektor MUSI pokryć każdą formę zapisu celu, nie tylko tę zaobserwowaną."""
    tekst = ("Kandydat 1 (BIB-006), kandydat 2 [BIB 047], kandydat 3 bib-6, "
             "kandydat 4 BIB_012, kandydat 5 z BIB-047_Kaufman_Trading.pdf")
    biby = [c.bib for c in pb.wyodrebnij_cytaty(tekst)]
    assert biby == ["BIB-006", "BIB-047", "BIB-006", "BIB-012", "BIB-047"]


def test_negatywny_nie_lapie_czego_nie_powinien():
    """Test NEGATYWNY: napisy podobne do cytatu nie mogą uchodzić za cytat."""
    tekst = "BIBLIOTEKA ma 115 pozycji, ATTRIB-006 to nie cytat, a BIBBIB-006 tym bardziej."
    assert pb.wyodrebnij_cytaty(tekst) == []


def test_bib_6_i_bib_006_to_ten_sam_identyfikator():
    """Granica normalizacji: zapis skrócony nie może udawać innego źródła."""
    assert pb.id_bib("BIB-6") == pb.id_bib("BIB-006") == "BIB-006"


def test_chunk_przyklejony_tylko_z_bliska():
    """Odległy numer chunku NIE może przykleić się do cytatu (fałszywy alarm)."""
    blisko = pb.wyodrebnij_cytaty("wg BIB-006 chunk 8 mamy przewagę")
    assert blisko[0].chunk == 8
    daleko = pb.wyodrebnij_cytaty("wg BIB-006 " + "x" * 120 + " chunk 8")
    assert daleko[0].chunk is None


# ── Rdzeń: grounding wobec PODANYCH fragmentów ──────────────────────────────────

def test_czysty_gdy_cytaty_z_podanych_zrodel():
    w = pb.sprawdz("Kandydat A wg BIB-006 chunk 8; kandydat B wg BIB-047.", _fragmenty())
    assert w.status == pb.CZYSTY and w.czysty is True
    assert w.obce_zrodla == () and w.obce_chunki == ()


def test_cytat_ksiazki_ktorej_NIE_podano_to_halucynacja():
    """RDZEŃ ORGANU: liczy się zgodność ze źródłem POKAZANYM, nie z korpusem.
    BIB-047 istnieje w bibliotece, ale gdy go nie podano — powołanie się jest konfabulacją."""
    tylko_006 = [_Wynik("BIB-006_Carson.epub", 8)]
    w = pb.sprawdz("Kandydat wg BIB-047 Kaufman.", tylko_006)
    assert w.status == pb.PODEJRZANY and w.czysty is False
    assert w.obce_zrodla == ("BIB-047",)


def test_chunk_spoza_podanych_lapany():
    """Źródło podane, ale numer chunku wymyślony — też halucynacja citation."""
    w = pb.sprawdz("Zgodnie z BIB-006 chunk 99 rynek wraca do średniej.", _fragmenty())
    assert w.status == pb.PODEJRZANY
    assert w.obce_chunki == (("BIB-006", 99),)
    assert w.obce_zrodla == ()


def test_chunk_z_podanych_nie_alarmuje():
    """Granica: chunk 7 ORAZ 8 były podane — oba muszą przejść."""
    for nr in (7, 8):
        w = pb.sprawdz(f"Teza wg BIB-006 chunk {nr}.", _fragmenty())
        assert w.status == pb.CZYSTY, nr


def test_brak_wiedzy_o_chunkach_nie_oskarza():
    """Gdy nie znamy numeracji chunków źródła, cytat chunku NIE jest dowodem winy
    (brak wiedzy ≠ wina — inaczej detektor produkowałby fałszywe alarmy)."""
    bez_numeru = [_Wynik("BIB-006_Carson.epub", None)]
    w = pb.sprawdz("Teza wg BIB-006 chunk 99.", bez_numeru)
    assert w.status == pb.CZYSTY


def test_wiele_obcych_zrodel_bez_duplikatow():
    """To samo obce źródło cytowane kilka razy = jeden wpis, nie trzy."""
    w = pb.sprawdz("BIB-099 raz, BIB-099 dwa, BIB-099 trzy.", _fragmenty())
    assert w.obce_zrodla == ("BIB-099",)


# ── Abstencja i granice ─────────────────────────────────────────────────────────

def test_abstencja_jest_poprawnym_wynikiem():
    """Model odmawiający kandydatów zachował się WZOROWO — karanie go uczyłoby konfabulacji."""
    w = pb.sprawdz("Podane fragmenty nie niosą nic wartościowego dla roju.", _fragmenty())
    assert w.status == pb.ABSTENCJA and w.czysty is True


def test_abstencja_wygrywa_z_cytatem_w_tresci():
    """Kolejność rozstrzygania: odmowa POWOŁUJĄCA SIĘ na źródło to wciąż odmowa,
    a nie konfabulacja (fragment BYŁ podany, więc cytat jest legalny)."""
    w = pb.sprawdz("Fragmenty (BIB-006) nie niosą nic wartościowego.", _fragmenty())
    assert w.czysty is True


def test_kandydaci_bez_zadnego_cytatu_to_alarm():
    """Są tezy, zero powołań na źródło → grounding niesprawdzalny = podejrzane."""
    w = pb.sprawdz("Kandydat 1: neuron momentum. Kandydat 2: filtr zmienności.", _fragmenty())
    assert w.status == pb.BEZ_CYTATU and w.czysty is False


def test_brak_fragmentow_nic_do_sprawdzenia():
    """Granica: nie podano nic → nie ma czego weryfikować (nie oskarżamy)."""
    assert pb.sprawdz("Cokolwiek wg BIB-006.", []).status == pb.NIC_DO_SPRAWDZENIA


def test_pusta_odpowiedz_nic_do_sprawdzenia():
    """Granica: pusty/None plon → brak werdyktu, nie fałszywy alarm."""
    assert pb.sprawdz("", _fragmenty()).status == pb.NIC_DO_SPRAWDZENIA
    assert pb.sprawdz(None, _fragmenty()).status == pb.NIC_DO_SPRAWDZENIA
    assert pb.sprawdz("   \n  ", _fragmenty()).status == pb.NIC_DO_SPRAWDZENIA


def test_fragmenty_bez_identyfikatora_bib_ignorowane():
    """Fragment spoza biblioteki (np. z docs) nie wnosi źródła do mapy."""
    assert pb.podane_zrodla([_Wynik("docs/NOTATKA.md", 1)]) == {}


def test_podane_zrodla_przyjmuje_slowniki_i_krotki():
    """Cząstka z JSONL nie ma obiektów RAG — organ musi czytać też dane surowe."""
    ze_slownika = pb.podane_zrodla([{"zrodlo": "BIB-006_x.pdf", "nr_chunk": 3}])
    z_krotki = pb.podane_zrodla([("BIB-006_x.pdf", 3)])
    assert ze_slownika == {"BIB-006": {3}} == z_krotki


def test_nieparsowalny_numer_chunku_nie_wywala():
    """Odporność: śmieć w numerze chunku = brak wiedzy o chunku, nie wyjątek."""
    assert pb.podane_zrodla([{"zrodlo": "BIB-006_x.pdf", "nr_chunk": "abc"}]) == {"BIB-006": set()}


def test_do_slownika_serializowalny():
    """Werdykt musi dać się zapisać do kolejki JSONL (bez obiektów niestandardowych)."""
    import json
    w = pb.sprawdz("Teza wg BIB-099 chunk 5.", _fragmenty())
    d = pb.do_slownika(w)
    assert json.loads(json.dumps(d, ensure_ascii=False))["status"] == pb.PODEJRZANY
    assert d["obce_zrodla"] == ["BIB-099"]


def test_opis_alarmu_wymienia_winowajce():
    """Meldunek zero-tokenowy musi nazywać konkretne źródło, nie mówić 'coś nie gra'."""
    w = pb.sprawdz("Teza wg BIB-099.", _fragmenty())
    assert "BIB-099" in w.opis() and "🚨" in w.opis()


# ── Cytowanie NAZWISKIEM autora (zmierzone na realnym plonie 2026-07-21) ────────

def test_cytat_nazwiskiem_autora_nie_jest_falszywym_alarmem():
    """Plon „Źródła: Hull chunk 560" był ugruntowany, a detektor krzyczał BEZ_CYTATU.
    Fałszywy alarm jest groźniejszy niż brak alarmu — uczy ignorować organ."""
    frag = [_Wynik("BIB-037_Hull_Options-Futures-and-Other-Derivatives.epub", 560)]
    w = pb.sprawdz("Hipoteza: dealerzy hedgingują gamma. Źródła: Hull chunk 560.", frag)
    assert w.status == pb.CZYSTY and w.czysty is True
    assert w.uwagi and "NAZWISKIEM" in w.uwagi[0]


def test_nazwisko_spoza_podanych_zrodel_nie_ratuje_przed_alarmem():
    """Alias działa TYLKO na korzyść źródeł faktycznie podanych — obce nazwisko nie liczy się."""
    w = pb.sprawdz("Hipoteza wg Kaufmana i Schwagera.", [_Wynik("BIB-006_Carson_x.epub", 8)])
    assert w.status == pb.BEZ_CYTATU


def test_alias_wymaga_calego_slowa():
    """Test NEGATYWNY aliasu: fragment nazwiska w innym słowie to nie cytat."""
    frag = [_Wynik("BIB-037_Hull_Options.epub", 1)]
    assert pb.sprawdz("Kandydat oparty o hulling i hullabaloo.", frag).status == pb.BEZ_CYTATU


def test_alias_pomija_zbyt_krotkie_nazwiska():
    """Nazwiska <4 znaków („Lo", „Ng") trafiałyby w zwykłą prozę — świadomie odrzucane."""
    assert pb.aliasy_zrodel([_Wynik("BIB-050_Lo_Adaptive-Markets.pdf", 1)]) == {}


def test_alias_mapuje_nazwisko_na_bib():
    assert pb.aliasy_zrodel(_fragmenty()) == {"carson": "BIB-006", "kaufman": "BIB-047"}


def test_bib_wygrywa_z_aliasem_gdy_oba_obecne():
    """Gdy jest identyfikator BIB, alias nie może przykryć obcego źródła."""
    w = pb.sprawdz("Wg Carson, ale też wg BIB-099.", _fragmenty())
    assert w.status == pb.PODEJRZANY and w.obce_zrodla == ("BIB-099",)
