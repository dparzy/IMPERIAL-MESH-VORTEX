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


def test_profil_klasyfikacji_wylacza_rozumowanie():
    """Klasyfikacja to wybór etykiety — rozumowanie jest czystym kosztem (zmierzone 11.7×)."""
    p = dobierz("klasyfikacja")
    assert p["thinking"] == {"type": "disabled"}
    assert p["model"] == "deepseek-v4-flash"
    assert "reasoning_effort" not in p, "wyłączone myślenie nie potrzebuje poziomu głębokości"


def test_profil_osadu_bierze_model_premium():
    """Osąd o konsekwencjach (co wchodzi do roju) — tu stać nas na droższy model."""
    p = dobierz("osad")
    assert p["model"] == "deepseek-v4-pro"
    assert p["reasoning_effort"] == "high"


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
    assert abs(koszt_usd(u, "deepseek-v4-flash") - 0.42) < 1e-9


def test_koszt_uwzglednia_cache():
    """Trafienie w cache jest 50× tańsze — bez tego oszczędność byłaby niewidoczna."""
    bez = koszt_usd({"prompt_tokens": 1_000_000, "completion_tokens": 0}, "deepseek-v4-flash")
    z_cache = koszt_usd({"prompt_tokens": 1_000_000, "prompt_cache_hit_tokens": 1_000_000,
                         "completion_tokens": 0}, "deepseek-v4-flash")
    assert abs(bez - 0.14) < 1e-9
    assert abs(z_cache - 0.0028) < 1e-9
    assert z_cache < bez / 40, "cache musi być wyraźnie tańszy"


def test_koszt_pro_drozszy_od_flash():
    """Granica kierunku: ten sam rachunek na pro musi kosztować więcej niż na flashu."""
    u = {"prompt_tokens": 10_000, "completion_tokens": 10_000}
    assert koszt_usd(u, "deepseek-v4-pro") > koszt_usd(u, "deepseek-v4-flash")


def test_koszt_nieznanego_modelu_to_none_nie_zero():
    """Prawo I: brak cennika = NIE WIEM. Zero udawałoby, że wywołanie było darmowe."""
    assert koszt_usd({"prompt_tokens": 100, "completion_tokens": 100}, "model-widmo") is None
    assert koszt_usd(None, "deepseek-v4-flash") is None


def test_koszt_przyjmuje_obiekt_usage_nie_tylko_slownik():
    """SDK zwraca obiekt, nie dict — organ musi czytać oba (inaczej cicho policzy 0)."""
    class U:
        prompt_tokens = 1_000_000
        completion_tokens = 0
    assert abs(koszt_usd(U(), "deepseek-v4-flash") - 0.14) < 1e-9


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
