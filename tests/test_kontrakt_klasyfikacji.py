"""Testy kontraktu odpowiedzi klasyfikatora w zbiorze treningowym TIRO.

Zarzut cubica (PR #134, P2) osądzony 2026-07-27: bramka sprawdzała, czy odpowiedź jest
OBIEKTEM JSON, a nie czy jest WERDYKTEM. `{"error": "rate limited"}` spełniało pierwsze
i nie spełniało drugiego, a próg długości odpowiedzi klasyfikacji nie obowiązuje (werdykt
ma z definicji 34-41 znaków). Skutkiem byłaby awaria API zapisana jako ETYKIETA w zbiorze,
którego jedyną wartością jest to, że etykiety są prawdziwe.

Pomiar przed naprawą: 108 par klasyfikacji, 0 z takim kształtem — wada REALNA, ale UTAJONA.
Testy pilnują OBU stron granicy: awaria nie wchodzi, a poprawny werdykt nadal wchodzi.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.biblioteki import notarius as nt  # noqa: E402


def _para(odp: str, zrodlo: str = "news_llm") -> dict:
    return {"zrodlo": zrodlo, "rodzaj": nt.RODZAJ_KLASYFIKACJI,
            "system": "s", "prompt": "p", "odpowiedz": odp}


def _kontrakt(odp: str, zrodlo: str = "news_llm") -> bool:
    return nt._kontrakt_dotrzymany(_para(odp, zrodlo), nt._obiekt_json(odp) or {})


def test_prawdziwy_werdykt_przechodzi():
    """Kształt zmierzony na żywym ledgerze: 102 ze 108 par mają dokładnie te dwa pola."""
    assert _kontrakt('{"sentyment": -0.4, "pewnosc": 0.8}') is True
    assert _kontrakt('{"sentyment": 0, "pewnosc": 0.1}') is True


def test_komunikat_o_awarii_NIE_jest_etykieta():
    """Sedno zarzutu: poprawny JSON, który nie niesie oceny."""
    assert _kontrakt('{"error": "rate limited"}') is False
    assert _kontrakt('{"message": "server busy", "code": 429}') is False


def test_bool_nie_jest_ocena():
    """`bool` jest podklasą `int` — bez jawnego odrzucenia `true` udawałoby liczbę."""
    assert _kontrakt('{"sentyment": true}') is False


def test_sentyment_nieliczbowy_odrzucony():
    assert _kontrakt('{"sentyment": "negatywny"}') is False
    assert _kontrakt('{"sentyment": null}') is False


def test_zrodlo_bez_zadeklarowanego_kontraktu_przechodzi():
    """Zgadywanie kontraktu byłoby gorsze niż jego brak — nieznane źródło zachowuje się
    jak dotąd (Prawo I: nie udajemy wiedzy, której nie mamy)."""
    assert _kontrakt('{"cokolwiek": 1}', zrodlo="nowe_zrodlo") is True


def test_zniekstalcony_rodzaj_nie_wywraca_calego_eksportu():
    """Jeden zły rekord nie ma prawa skasować plonu całej sesji (cubic PR #134, P3).

    `rodzaj: 5` jest wartością prawdziwą, więc `or ""` go nie łapał, a `.strip()` na `int`
    rzucał AttributeError w środku generatora — ginął CAŁY eksport SFT i licznik par."""
    assert nt.rodzaj_pary({"rodzaj": 5, "zrodlo": "news_llm"}) == nt.RODZAJ_KLASYFIKACJI
    assert nt.rodzaj_pary({"rodzaj": ["lista"], "zrodlo": "inne"}) == nt.RODZAJ_PROZA
    assert nt.rodzaj_pary({"rodzaj": None, "zrodlo": "news_llm"}) == nt.RODZAJ_KLASYFIKACJI
    # GRANICA: jawny napis nadal wygrywa ze źródłem — walidacja nie może znieść kontraktu.
    assert nt.rodzaj_pary({"rodzaj": " PROZA ", "zrodlo": "news_llm"}) == nt.RODZAJ_PROZA


def test_eksport_odrzuca_awarie_a_zachowuje_werdykt(tmp_path):
    """Test ŚCIEŻKI, nie tylko predykatu — bramka musi działać w eksporcie SFT."""
    import json
    plik = tmp_path / "pary.jsonl"
    wiersze = [
        {**_para('{"sentyment": -0.5, "pewnosc": 0.9}'), "odcisk_pytania": "a"},
        {**_para('{"error": "rate limited"}'), "odcisk_pytania": "b"},
    ]
    plik.write_text("\n".join(json.dumps(w, ensure_ascii=False) for w in wiersze),
                    encoding="utf-8")
    wynik = list(nt.pary_sft(sciezka=plik, jedna_probka_na_pytanie=False))
    assert len(wynik) == 1, f"awaria API weszła do zbioru treningowego: {wynik}"
