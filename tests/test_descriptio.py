"""Testy DESCRIPTIO IMPERII — podziału Imperium na filary.

Ten organ ma JEDNO zadanie, którego nie wolno mu zawalić po cichu: **żaden moduł nie może
wypaść z obrazu**. Dlatego najważniejsze testy to nie te sprawdzające ładny wydruk, lecz te
pilnujące, że nowy katalog w repo **wywraca organ na czerwono**, zamiast zniknąć z mapy —
na tym poległ MATURITAS (52 wiersze ROADMAP poza pomiarem) i to była jedna z trzech dziur,
które kazały Cezarowi zamrozić rozwój 2026-08-04.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.oczy import descriptio as D  # noqa: E402


# ── 1. PODZIAŁ NA ŻYWYM REPO — kompletny i domknięty ────────────────────────────

def test_zywe_repo_bez_sierot():
    p = D.podzial()
    assert p["nieprzypisane"] == [], f"moduły poza filarami: {p['nieprzypisane'][:5]}"


def test_suma_filarow_rowna_liczbie_modulow():
    """Dowód kompletności: podział NIE MOŻE gubić modułów po drodze."""
    p = D.podzial()
    suma = sum(len(d["moduly"]) for d in p["filary"].values())
    assert suma == p["modulow_razem"]


def test_lista_odniesienia_pochodzi_z_osobnego_przejscia():
    """`moduly_zrodlowe` to lista Z PRODUCENTA, zdjęta PRZED przypisywaniem do filarów.

    Bez niej kontrola kompletności porównywałaby wynik pętli z liczbą policzoną w TEJ SAMEJ
    pętli — czyli sama ze sobą (wada z recenzji 2026-08-05: bezpiecznik, który nie mógł się
    zapalić). Ten test pilnuje, żeby lista odniesienia nie zniknęła po cichu przy refaktorze.
    """
    p = D.podzial()
    assert p["moduly_zrodlowe"], "brak listy odniesienia = nie ma czym sprawdzić kompletności"
    assert len(p["moduly_zrodlowe"]) == p["modulow_razem"]


def test_zywe_repo_zgodne():
    assert D.zgodny() is True, D.bledy()


def test_kazdy_filar_ma_powod_i_straznika():
    for filar, dane in D.podzial()["filary"].items():
        assert dane["po_co"].strip(), f"{filar} nie mówi, po co istnieje"
        assert dane["straznik"].strip(), f"{filar} nie ma strażnika"


# ── 2. GRANICA: NOWY KATALOG MUSI KRZYCZEĆ, NIE ZNIKAĆ ──────────────────────────

def _podzial_z(spis, monkeypatch):
    import narzedzia.census_organorum as C
    monkeypatch.setattr(C, "spisz_moduly", lambda: spis)
    return D.podzial()


def test_nowy_katalog_poza_filarami_to_alarm(monkeypatch):
    """Klasa K2: moduł, którego nikt nie przypisał, NIE MOŻE po cichu wypaść z obrazu."""
    p = _podzial_z({"imperium/nowy_organ": [("cos.py", "rola")]}, monkeypatch)
    assert p["nieprzypisane"] == ["imperium/nowy_organ/cos.py"]
    assert D.zgodny(p) is False
    assert any("POZA filarami" in b for b in D.bledy(p))


def test_znany_katalog_nie_alarmuje(monkeypatch):
    """Druga strona granicy — bramka, która alarmuje zawsze, jest bezużyteczna."""
    p = _podzial_z({"imperium/legiony": [("rejestr.py", "rola")]}, monkeypatch)
    assert p["nieprzypisane"] == []
    assert D.zgodny(p) is True


def test_straznik_widmo_to_alarm(monkeypatch):
    """Filar nie może wskazywać strażnika, którego nie ma w kodzie (klasa API-widm, W16)."""
    monkeypatch.setattr(D, "FILARY", [
        ("imperium/legiony", "IV. RÓJ", "liczy sygnały", "imperium/legiony/NIE_MA_MNIE.py"),
    ])
    p = _podzial_z({"imperium/legiony": [("rejestr.py", "rola")]}, monkeypatch)
    assert D.zgodny(p) is False
    assert any("NIE MA w kodzie" in b for b in D.bledy(p))


# ── 2b. GRANICA: CELOWO PSUJĘ PODZIAŁ — KONTROLA MUSI SIĘ ZAPALIĆ ───────────────
# Wada z recenzji 2026-08-05: poprzednia kontrola kompletności („suma ≠ razem") była
# TAUTOLOGIĄ — obie liczby wychodziły z tej samej pętli, więc nie mogła zapalić się nigdy.
# Poniższe cztery testy psują podział na cztery różne sposoby; każdy MUSI dać alarm.

def test_zgubiony_modul_w_podziale_to_alarm():
    """Moduł, który wypadł między producentem a filarem — sumy tego nie widziały."""
    p = D.podzial()
    filar = next(iter(p["filary"]))
    p["filary"][filar]["moduly"].pop()          # celowo psuję producenta podziału
    assert D.zgodny(p) is False
    assert any("GUBI" in b for b in D.bledy(p)), D.bledy(p)


def test_wymyslony_modul_w_podziale_to_alarm():
    """Odwrotny kierunek: filar zawiera coś, czego CENSUS nie zna (literówka, duch)."""
    p = D.podzial()
    filar = next(iter(p["filary"]))
    p["filary"][filar]["moduly"].append("imperium/widmo/nie_ma_mnie.py")
    assert D.zgodny(p) is False
    assert any("WYMYŚLA" in b for b in D.bledy(p)), D.bledy(p)


def test_modul_w_dwoch_filarach_to_alarm():
    """Nakładające się filary zawyżałyby każdą liczbę współpracy — sumy i tak by się zgodziły."""
    p = D.podzial()
    dwa = list(p["filary"])[:2]
    p["filary"][dwa[1]]["moduly"].append(p["filary"][dwa[0]]["moduly"][0])
    assert D.zgodny(p) is False
    assert any("DWA RAZY" in b for b in D.bledy(p)), D.bledy(p)


def test_brak_listy_odniesienia_to_alarm_nie_zielen():
    """K2: bez czego porównać — mówimy „nie ma czym sprawdzić", nie „w porządku"."""
    p = D.podzial()
    p.pop("moduly_zrodlowe")
    assert D.zgodny(p) is False
    assert any("NIE MA CZYM sprawdzić" in b for b in D.bledy(p)), D.bledy(p)


# ── 3. DOPASOWANIE PO NAJDŁUŻSZYM PREFIKSIE ─────────────────────────────────────

def test_rag_idzie_do_wiedzy_a_reszta_narzedzi_do_pomiaru():
    """`narzedzia/rag` musi wygrać z `narzedzia` — inaczej RAG wypadłby z filara WIEDZY."""
    assert D._filar_dla("narzedzia/rag")[0].startswith("I.")
    assert D._filar_dla("narzedzia")[0].startswith("XI.")


def test_podkatalog_dziedziczy_po_rodzicu():
    assert D._filar_dla("imperium/cesarz/doradcy")[0] == D._filar_dla("imperium/cesarz")[0]


def test_katalog_spoza_mapy_nie_ma_filara():
    assert D._filar_dla("cokolwiek/innego") is None


# ── 4. WSPÓŁPRACA — tylko MIĘDZY filarami ───────────────────────────────────────

def test_wspolpraca_pomija_krawedzie_wewnatrz_filara():
    """Import w obrębie jednego filara nie jest współpracą filarów — inaczej duży filar
    wyglądałby na najbardziej zintegrowany tylko dlatego, że jest duży."""
    for (a, b) in D.wspolpraca().keys():
        assert a != b


def test_wspolpraca_ma_krawedzie_na_zywym_repo():
    assert len(D.wspolpraca()) > 0, "zero krawędzi na żywym repo = licznik przestał liczyć"


# ── 4b. KOLIZJA NAZW — NIE ZGADUJEMY, DO KTÓREGO FILARA NALEŻY `baza.py` ────────
# Wada z recenzji 2026-08-05: mapa `stem → filar` była zwykłym słownikiem, więc przy trzech
# plikach `baza.py` z DWÓCH filarów wygrywał ostatni wpis, a importy szły do przypadkowego
# filara. Zmierzony skutek naprawy na żywym repo: DANE woła 23→14, RÓJ wołany 93→82 —
# jedenaście krawędzi było raportowanych Cezarowi pod złym filarem.

def _p_testowy(filary, zrodlowe=None):
    zrodlowe = zrodlowe if zrodlowe is not None else [m for d in filary.values() for m in d["moduly"]]
    return {"filary": {f: {"po_co": "", "straznik": "", "katalogi": [], **d}
                       for f, d in filary.items()},
            "nieprzypisane": [], "moduly_zrodlowe": zrodlowe, "modulow_razem": len(zrodlowe)}


def test_kolizja_nazw_wykryta_na_zywym_repo():
    """`baza.py` faktycznie żyje w dwóch filarach — jeśli ten test zgaśnie, sprawdź DLACZEGO."""
    kol = D.kolizje_nazw()
    assert "baza" in kol, f"spodziewana kolizja `baza` zniknęła; widziane: {list(kol)}"
    assert len(kol["baza"]) >= 2


def test_import_niejednoznacznej_nazwy_NIE_TRAFIA_do_zadnego_filara(tmp_path, monkeypatch):
    """GRANICA — celowo podsuwam kolizję: ta sama nazwa w dwóch filarach + moduł, który ją
    importuje. Przed naprawą powstawała krawędź do LOSOWEGO filara; teraz nie powstaje żadna."""
    for k in ("a", "b", "c"):
        (tmp_path / k).mkdir()
    (tmp_path / "a" / "baza.py").write_text("X = 1\n", encoding="utf-8")
    (tmp_path / "b" / "baza.py").write_text("X = 2\n", encoding="utf-8")
    (tmp_path / "c" / "klient.py").write_text("from a.baza import X\n", encoding="utf-8")
    monkeypatch.setattr(D, "KORZEN", tmp_path)

    p = _p_testowy({"A": {"moduly": ["a/baza.py"]},
                    "B": {"moduly": ["b/baza.py"]},
                    "C": {"moduly": ["c/klient.py"]}})
    assert D.kolizje_nazw(p) == {"baza": ["A", "B"]}
    assert D.wspolpraca(p) == {}, "nazwa niejednoznaczna nie może dostać krawędzi z losowania"


def test_nazwa_jednoznaczna_nadal_daje_krawedz(tmp_path, monkeypatch):
    """Druga strona granicy: filtr kolizji nie może wyciszyć CAŁEGO licznika."""
    for k in ("a", "c"):
        (tmp_path / k).mkdir()
    (tmp_path / "a" / "unikat.py").write_text("X = 1\n", encoding="utf-8")
    (tmp_path / "c" / "klient.py").write_text("from a.unikat import X\n", encoding="utf-8")
    monkeypatch.setattr(D, "KORZEN", tmp_path)

    p = _p_testowy({"A": {"moduly": ["a/unikat.py"]}, "C": {"moduly": ["c/klient.py"]}})
    assert D.wspolpraca(p) == {("C", "A"): 1}


def test_raport_mowi_o_pominietych_nazwach():
    """Zaniżenie miary musi być WIDOCZNE — miara milcząca o ślepej plamce kłamie."""
    assert "POMINIĘTE" in D.raport_tekst()


# ── 5. RAPORT I BRAMKA ──────────────────────────────────────────────────────────

def test_raport_mowi_o_kompletnosci():
    t = D.raport_tekst()
    assert "RAZEM" in t and "zero pominięć" in t


def test_bramka_zwraca_zero_gdy_zgodne():
    assert D.main(["--bramka"]) == 0
