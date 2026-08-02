"""Testy DISPENSATORA — Szafarza doboru modelu/rozumowania (2026-07-20).

Reguła Test-Granic: organ liczy PIENIĄDZE i decyduje o kosztach, więc granice muszą być
sprawdzone — zwłaszcza tam, gdzie brak danych mógłby po cichu dać 0 zamiast „nie wiem".
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.cesarz.dispensator import (  # noqa: E402
    CENNIK, POZIOMY_ROZUMOWANIA, PROFILE, diagnoza_pustej, dobierz, koszt_usd,
    opis_profili, tokeny_rozumowania,
)


# CHWILA PRZYPIĘTA W KAŻDYM TEŚCIE KOSZTU (naprawa 2026-07-26). Od wprowadzenia taryfy
# szczytowej (07-21) `koszt_usd` liczy wg CHWILI WYWOŁANIA: w oknach 01–04 i 06–10 UTC
# stawka jest podwójna. Trzy testy kosztu przypięcia nie dostały i przez ~7 godzin na dobę
# oblewały cały pakiet (złapane 2026-07-26 o 01:57 UTC: oczekiwane 0.14, policzone 0.28).
# Test mierzący wielkość zależną od zegara MUSI zegar przypiąć — inaczej mierzy porę dnia.
def _utc(godzina, minuta=0):
    from datetime import datetime, timezone
    return datetime(2026, 7, 21, godzina, minuta, tzinfo=timezone.utc)


def test_profil_klasyfikacji_wylacza_rozumowanie():
    """Klasyfikacja to wybór etykiety — rozumowanie jest czystym kosztem (zmierzone 11.7×)."""
    p = dobierz("klasyfikacja")
    assert p["thinking"] == {"type": "disabled"}
    assert p["model"] == "deepseek-v4-flash"
    assert "reasoning_effort" not in p, "wyłączone myślenie nie potrzebuje poziomu głębokości"


def test_profil_osadu_bierze_model_najlepszy_nie_najdrozszy():
    """Osąd o konsekwencjach (co wchodzi do roju) — bierzemy NAJLEPSZY model, nie najdroższy.

    ZMIANA ZAŁOŻENIA 2026-08-03 (rozkaz Cezara, pomiar zewnętrzny ×2 źródła): stara nazwa
    tego testu brzmiała `..._bierze_model_premium`, a docstring mówił „stać nas na droższy" —
    czyli test kodował ZAŁOŻENIE, że cena jest miarą jakości. Wydanie `V4-Flash-0731`
    (31.07.2026) je obaliło: tańszy model bije droższego na wszystkich pięciu opublikowanych
    benchmarkach agentowych, przy 3,1× niższej cenie wyjścia.

    Test pilnuje teraz DWÓCH rzeczy, które pozostają prawdą niezależnie od cennika:
    profil osądu myśli GŁĘBOKO i nie schodzi na model wyłączonego rozumowania.
    """
    p = dobierz("osad")
    assert p["model"] == "deepseek-v4-flash"
    assert p["reasoning_effort"] == "high", "osąd bez głębokiego rozumowania to nie osąd"
    assert "thinking" not in p, "profil osądu nie może mieć wyłączonego myślenia"


def test_nieznany_profil_nie_wywraca_wywolania():
    """Literówka w nazwie profilu NIE może uciszyć mostu — dobór to optymalizacja, nie warunek."""
    assert dobierz("nie-ma-takiego") == dobierz("zwiad")
    assert dobierz() == dobierz("zwiad")


def test_profile_uzywaja_tylko_znanych_wartosci():
    """Prawo XXI: każdy profil musi wskazywać model z cennika i legalny poziom rozumowania."""
    for nazwa, p in PROFILE.items():
        assert p["model"] in CENNIK, f"profil {nazwa}: model spoza cennika"
        if "reasoning_effort" in p:
            assert p["reasoning_effort"] in POZIOMY_ROZUMOWANIA, f"profil {nazwa}: zły poziom"
        assert p.get("po_co"), f"profil {nazwa}: brak uzasadnienia (ZPO)"


def test_dobierz_nie_przekazuje_opisu_do_api():
    """Pole `po_co` jest dla ludzi — API dostałoby nieznany parametr i mogłoby odrzucić."""
    for nazwa in PROFILE:
        assert "po_co" not in dobierz(nazwa)


# ── Koszt ────────────────────────────────────────────────────────────────────────

def test_koszt_liczony_z_faktycznego_zuzycia():
    """1M tokenów wejścia + 1M wyjścia na flashu = 0.14 + 0.28 USD."""
    u = {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000}
    assert abs(koszt_usd(u, "deepseek-v4-flash", kiedy=_utc(12)) - 0.42) < 1e-9


def test_koszt_uwzglednia_cache():
    """Trafienie w cache jest 50× tańsze — bez tego oszczędność byłaby niewidoczna."""
    bez = koszt_usd({"prompt_tokens": 1_000_000, "completion_tokens": 0},
                    "deepseek-v4-flash", kiedy=_utc(12))
    z_cache = koszt_usd({"prompt_tokens": 1_000_000, "prompt_cache_hit_tokens": 1_000_000,
                         "completion_tokens": 0}, "deepseek-v4-flash", kiedy=_utc(12))
    assert abs(bez - 0.14) < 1e-9
    assert abs(z_cache - 0.0028) < 1e-9
    assert z_cache < bez / 40, "cache musi być wyraźnie tańszy"


def test_koszt_pro_drozszy_od_flash():
    """Granica kierunku: ten sam rachunek na pro musi kosztować więcej niż na flashu."""
    u = {"prompt_tokens": 10_000, "completion_tokens": 10_000}
    assert (koszt_usd(u, "deepseek-v4-pro", kiedy=_utc(12))
            > koszt_usd(u, "deepseek-v4-flash", kiedy=_utc(12)))


def test_koszt_nieznanego_modelu_to_none_nie_zero():
    """Prawo I: brak cennika = NIE WIEM. Zero udawałoby, że wywołanie było darmowe."""
    assert koszt_usd({"prompt_tokens": 100, "completion_tokens": 100}, "model-widmo") is None
    assert koszt_usd(None, "deepseek-v4-flash") is None


def test_koszt_przyjmuje_obiekt_usage_nie_tylko_slownik():
    """SDK zwraca obiekt, nie dict — organ musi czytać oba (inaczej cicho policzy 0)."""
    class U:
        prompt_tokens = 1_000_000
        completion_tokens = 0
    assert abs(koszt_usd(U(), "deepseek-v4-flash", kiedy=_utc(12)) - 0.14) < 1e-9


# ── Pułapka pustej odpowiedzi ────────────────────────────────────────────────────

def test_pelna_odpowiedz_bez_diagnozy():
    assert diagnoza_pustej("391", {"completion_tokens_details": {"reasoning_tokens": 90}}) is None


def test_pusta_przy_rozumowaniu_wskazuje_budzet():
    """REGRESJA 2026-07-20: max_tokens=300 → 300 tokenów rozumowania, content='' , HTTP 200."""
    d = diagnoza_pustej("", {"completion_tokens_details": {"reasoning_tokens": 300}})
    assert d and "budżet" in d and "max_tokens" in d


def test_pusta_bez_rozumowania_wskazuje_prompt():
    """Rozróżnienie ma sens tylko wtedy, gdy prowadzi do INNEJ naprawy."""
    d = diagnoza_pustej("", {"completion_tokens_details": {"reasoning_tokens": 0}})
    assert d and "promptu" in d


def test_biale_znaki_to_pustka():
    """Granica: sama spacja/nowa linia to nie jest odpowiedź."""
    assert diagnoza_pustej("   \n  ") is not None
    assert diagnoza_pustej(None) is not None


def test_tokeny_rozumowania_bez_danych_to_zero():
    assert tokeny_rozumowania(None) == 0
    assert tokeny_rozumowania({}) == 0
    assert tokeny_rozumowania({"completion_tokens_details": {}}) == 0


def test_opis_profili_wymienia_wszystkie():
    o = opis_profili()
    for nazwa in PROFILE:
        assert nazwa in o


# ── Most mowy: dobór głębokości per wywołanie (DISPENSATOR wpięty 2026-07-21) ────

class _KlientAtrapa:
    """Podstawiony klient OpenAI — zapamiętuje DOKŁADNIE, co poszłoby do API."""

    def __init__(self):
        self.zadania = []
        self.chat = self
        self.completions = self

    def create(self, **kw):
        self.zadania.append(kw)

        class _Odp:
            choices = [type("C", (), {"message": type("M", (), {"content": "ok"})()})()]
        return _Odp()


def _glos_z_atrapa(monkeypatch):
    from imperium.cesarz import deepseek_glos as dg
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-nie-jest-prawdziwy")
    monkeypatch.setattr(dg, "OpenAI", lambda **kw: _KlientAtrapa())
    g = dg.GlosImperium()
    monkeypatch.setattr(g, "_protokoluj", lambda *a, **k: None)   # bez zapisu do NOTARIUSA
    return g


def test_bez_profilu_zadanie_identyczne_jak_przed_zmiana(monkeypatch):
    """WSTECZNA ZGODNOŚĆ: wywołanie bez nowych argumentów NIE MOŻE dołożyć extra_body
    ani zmienić modelu — inaczej wszyscy dotychczasowi wołający zaczęliby płacić inaczej."""
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("system", "treść", temperatura=0.4)
    z = g.client.zadania[0]
    assert z["model"] == "deepseek-v4-flash"
    assert "extra_body" not in z
    assert z["temperature"] == 0.4


def test_profil_zwiad_kupuje_tanio(monkeypatch):
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("s", "t", profil="zwiad")
    z = g.client.zadania[0]
    assert z["model"] == "deepseek-v4-flash"
    assert z["extra_body"]["reasoning_effort"] == "low"


def test_profil_osad_idzie_na_flash_z_glebokim_rozumowaniem(monkeypatch):
    """Osąd o konsekwencjach → v4-flash + głębokie rozumowanie (rozkaz Cezara 2026-08-03)."""
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("s", "t", profil="osad")
    z = g.client.zadania[0]
    assert z["model"] == "deepseek-v4-flash"
    assert z["extra_body"]["reasoning_effort"] == "high"


def test_v4_pro_zostaje_w_cenniku_jako_ramie_porownawcze():
    """`v4-pro` NIE znika z cennika, choć żaden profil go już nie kupuje.

    Powód: A/B `flash/high vs pro/high` (ab_plon_hyginusa) jest zaplanowany i dotąd
    nieuruchomiony. Usunięcie ceny drugiego ramienia uniemożliwiłoby ZMIERZENIE decyzji,
    którą właśnie podjęliśmy na cudzym pomiarze — a nasz pomiar jest wyrokiem, cudzy
    tylko poszlaką. Cena, której nie ma, to eksperyment, którego nie da się rozliczyć.
    """
    from imperium.cesarz.dispensator import CENNIK, PROFILE

    assert "deepseek-v4-pro" in CENNIK
    assert all(p["model"] != "deepseek-v4-pro" for p in PROFILE.values()), \
        "żaden profil nie powinien już domyślnie kupować v4-pro"


def test_profil_klasyfikacja_wylacza_rozumowanie(monkeypatch):
    """Zmierzone 07-20: thinking disabled = 11.7× taniej. Etykietowanie nie wymaga rozważań."""
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("s", "t", profil="klasyfikacja")
    assert g.client.zadania[0]["extra_body"]["thinking"] == {"type": "disabled"}


def test_jawny_argument_nadpisuje_profil(monkeypatch):
    """Wołający wie więcej niż tabela — jawny model/effort ma pierwszeństwo przed profilem."""
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("s", "t", profil="zwiad", model="deepseek-v4-pro", reasoning_effort="max")
    z = g.client.zadania[0]
    assert z["model"] == "deepseek-v4-pro"
    assert z["extra_body"]["reasoning_effort"] == "max"


def test_nieznany_profil_spada_na_domyslny_nie_wywala(monkeypatch):
    """Literówka w nazwie profilu nie może uciszyć mostu (dobierz nie rzuca) —
    ale test_wszystkie_profile_hyginusa_istnieja_w_dispensatorze pilnuje, że ich nie ma."""
    g = _glos_z_atrapa(monkeypatch)
    g.zapytaj("s", "t", profil="nie-ma-takiego")
    assert g.client.zadania[0]["model"] == "deepseek-v4-flash"


def test_notarius_dostaje_model_FAKTYCZNIE_uzyty(monkeypatch):
    """Etykieta nauczyciela musi zgadzać się z tym, kto naprawdę mówił. Inaczej TIRO uczy
    się z par opisanych cudzą nazwą (v4-pro odpowiedział, a w pliku stoi flash)."""
    from imperium.cesarz import deepseek_glos as dg
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-nie-jest-prawdziwy")
    monkeypatch.setattr(dg, "OpenAI", lambda **kw: _KlientAtrapa())
    g = dg.GlosImperium()
    zapisane = {}
    monkeypatch.setattr(g, "_protokoluj",
                        lambda *a, **k: zapisane.update({"model": a[4] if len(a) > 4 else None}))
    # MOC ROZRÓŻNIAJĄCA ODZYSKANA 2026-08-03. Test opierał się na tym, że profil `osad`
    # kupował `v4-pro`, czyli COŚ INNEGO niż domyślny `flash` z `__init__` — i tylko dzięki
    # tej różnicy wykrywał podmianę etykiety. Gdy Cezar przestawił `osad` na `flash`,
    # obie wartości zrównały się i test świeciłby na zielono, NIE BADAJĄC JUŻ NICZEGO
    # (zdałby nawet wtedy, gdyby `_protokoluj` dostawał model z `__init__`). Dlatego
    # różnicę wstrzykujemy tu jawnie, zamiast polegać na tym, że akurat wynika z cennika.
    from imperium.cesarz import dispensator as _disp
    monkeypatch.setitem(_disp.PROFILE, "_test_inny_model",
                        {"model": "deepseek-v4-pro", "reasoning_effort": "high", "po_co": "test"})
    g.zapytaj("s", "t", profil="_test_inny_model")
    assert zapisane["model"] == "deepseek-v4-pro"       # NIE flash z __init__


# ── Taryfa szczytowa (zweryfikowana 2026-07-21) ──────────────────────────────────

def test_czy_szczyt_granice_okien():
    """REGUŁA TEST-GRANIC: początek okna WLICZONY, koniec WYŁĄCZONY.

    Okna UTC 01:00–04:00 i 06:00–10:00 (2× stawka). Pomyłka o jedną godzinę na krańcu
    to dwukrotny błąd rachunku dla całej godziny ruchu."""
    from imperium.cesarz.dispensator import czy_szczyt
    for h in (1, 2, 3, 6, 8, 9):
        assert czy_szczyt(_utc(h)), f"{h}:00 UTC powinno być szczytem"
    for h in (0, 4, 5, 10, 11, 15, 23):
        assert not czy_szczyt(_utc(h)), f"{h}:00 UTC NIE powinno być szczytem"
    # dokładne krańce
    assert czy_szczyt(_utc(1, 0)) and czy_szczyt(_utc(3, 59))
    assert not czy_szczyt(_utc(4, 0))
    assert czy_szczyt(_utc(6, 0)) and czy_szczyt(_utc(9, 59))
    assert not czy_szczyt(_utc(10, 0))


def test_czy_szczyt_data_naiwna_liczona_jako_utc():
    """Granica: data bez strefy nie może cicho wpaść w lokalną — traktujemy ją jako UTC."""
    from datetime import datetime
    from imperium.cesarz.dispensator import czy_szczyt
    assert czy_szczyt(datetime(2026, 7, 21, 8, 0))
    assert not czy_szczyt(datetime(2026, 7, 21, 14, 0))


def test_koszt_w_szczycie_jest_podwojny():
    """Ten sam `usage` w szczycie kosztuje dokładnie 2× tego, co poza szczytem."""
    from imperium.cesarz.dispensator import koszt_usd
    usage = {"prompt_tokens": 10_000, "completion_tokens": 2_000,
             "prompt_cache_hit_tokens": 0}
    poza = koszt_usd(usage, "deepseek-v4-flash", kiedy=_utc(12))
    w_szczycie = koszt_usd(usage, "deepseek-v4-flash", kiedy=_utc(8))
    assert poza is not None
    assert abs(w_szczycie - 2 * poza) < 1e-12


def test_koszt_poza_szczytem_zgodny_z_cennikiem_bazowym():
    """Stawka bazowa nie zmieniła się — CENNIK z dokumentacji pozostaje prawdziwy.

    Ważne rozróżnienie (2026-07-21): dokument, z którego przepisaliśmy CENNIK, nie był
    BŁĘDNY, tylko NIEPEŁNY — milczał o taryfie szczytowej. Ten test pilnuje, że naprawa
    dołożyła wymiar czasu, a nie podmieniła stawki bazowe."""
    from imperium.cesarz.dispensator import CENNIK, koszt_usd
    c = CENNIK["deepseek-v4-pro"]
    usage = {"prompt_tokens": 1_000_000, "completion_tokens": 0,
             "prompt_cache_hit_tokens": 0}
    assert abs(koszt_usd(usage, "deepseek-v4-pro", kiedy=_utc(13)) - c["wejscie"]) < 1e-9


def test_brak_cennika_dalej_zwraca_none_takze_w_szczycie():
    """Granica: nieznany model → None (nie wiemy), a nie 0.0 ani 2×0."""
    from imperium.cesarz.dispensator import koszt_usd
    assert koszt_usd({"prompt_tokens": 5}, "model-widmo", kiedy=_utc(8)) is None
