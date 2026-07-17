"""
Testy ZAPORY TESTÓW — bramka, która pilnuje, że testy nie płacą (tests/conftest.py).

Reguła Test-Granic: zapora bez testu jest ozdobą. Ta zapora broni trzech rzeczy naraz —
pieniędzy Cezara, determinizmu bramki i jej szybkości — więc musi mieć dowód, że działa.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_zapora_odebrala_klucze():
    """SEDNO: w trakcie testów ŻADEN klucz płatnego API nie jest widoczny.

    Realny przypadek (2026-07-17): NOTARIUS złapał 5 płatnych wywołań DeepSeeka podczas
    zwykłego biegu testów — `handluj_live` buduje AdapterNewsLLM, ten robi lazy-init
    z `os.getenv("DEEPSEEK_API_KEY")`. Bez klucza w środowisku ścieżka schodzi na
    deterministyczny fallback i nikt nie płaci.
    """
    from conftest import KLUCZE_ODEBRANE_TESTOM
    widoczne = [k for k in KLUCZE_ODEBRANE_TESTOM if os.getenv(k)]
    assert not widoczne, (
        f"Zapora przepuściła klucze: {widoczne}. Testy mogą PŁACIĆ i dotknąć giełdy. "
        f"Sprawdź, czy tests/conftest.py jest ładowany (pytest: automatycznie; "
        f"run_tests.py: jawne wywołanie zaloz_zapore()).")


def test_zapora_jest_idempotentna():
    """GRANICA: ponowne założenie zapory (pytest + runner) nie może wywalić się ani skłamać."""
    from conftest import zaloz_zapore
    assert zaloz_zapore() == [], "Drugie założenie nie ma już czego odbierać"


def test_zapora_faktycznie_odbiera():
    """NEGATYWNY: zapora, która niczego nie usuwa, jest ozdobą — dowód, że działa."""
    from conftest import zaloz_zapore
    os.environ["DEEPSEEK_API_KEY"] = "udawany-klucz-do-testu-zapory"
    try:
        odebrane = zaloz_zapore()
        assert "DEEPSEEK_API_KEY" in odebrane, "Zapora NIE usunęła wstrzykniętego klucza"
        assert os.getenv("DEEPSEEK_API_KEY") is None
    finally:
        os.environ.pop("DEEPSEEK_API_KEY", None)


def test_most_llm_bez_klucza_nie_wola_sieci():
    """Adapter newsów BEZ klucza schodzi na fallback słownikowy zamiast wołać DeepSeek.

    To druga strona zapory: nie dość, że klucza nie ma, to jeszcze ścieżka bez klucza
    musi być POPRAWNA (Prawo XV: brak danych → abstynencja/fallback, nigdy crash).
    """
    from imperium.akwedukty.adaptery.news_llm import AdapterNewsLLM
    adapter = AdapterNewsLLM(fetcher=lambda s: ["Bitcoin ETF approval record rally surge"])
    wynik = adapter.pobierz("BTCUSDT")
    assert wynik is not None
    assert "NEWS_SENTYMENT" in wynik, wynik
    assert wynik["NEWS_SENTYMENT"] > 0, "bycze nagłówki → dodatni sentyment z fallbacku"
