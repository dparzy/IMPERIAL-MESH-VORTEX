"""
🛡️ ZAPORA TESTÓW — testy Imperium NIGDY nie dotykają płatnego API ani sieci.

Pytest ładuje ten plik automatycznie; `tests/run_tests.py` woła tę samą zaporę jawnie.

DLACZEGO ISTNIEJE (dowód, nie przezorność — Prawo I):
NOTARIUS (pisarz stenografujący każde przejście przez most `GlosImperium.zapytaj()`)
złapał **2026-07-17 o 05:41 pięć płatnych wywołań DeepSeeka ze źródła `news_llm`**
podczas zwykłego biegu `python tests/run_tests.py`. Przyczyna: `handluj_live`
(`petla_live.py:193`) buduje BEZWARUNKOWO `AdapterNewsLLM(fetcher=FetcherNewsRSS())`,
a adapter ma `uzyj_llm=True` domyślnie i `glos=None` → **lazy-init z klucza w środowisku**.
`tests/test_petla_live.py` woła `handluj_live` pięć razy.

Klasa była już ZAPISANA w Księdze Wad 2026-07-16 („testy palą pieniądze": zmierzone
8 wywołań i 4 min 42 s) — ale **zapisana, nie naprawiona**. Wróciła tego samego dnia.
Księga, która tylko notuje, jest pamiętnikiem, nie systemem samo-leczenia.

TRZY SZKODY NARAZ (dlatego zapora, nie łatka w jednym teście):
  1. **koszt** — każdy bieg bramki płaci za tokeny,
  2. **niedeterminizm** — wynik zależy od tego, co akurat piszą w newsach,
  3. **czas** — bramka wolna, więc rzadziej uruchamiana.

ZASADA: zamiast łatać każde wywołanie z osobna, ODBIERAMY TESTOM KLUCZE. Kod produkcyjny
zachowuje się identycznie (lazy-init po prostu nie znajduje klucza → fallback słownikowy,
ścieżka i tak wymagana przez Prawo XV). Test, który CHCE sprawdzić zachowanie LLM,
wstrzykuje atrapę (`glos=_FakeGlos(...)` — patrz `test_sentyment_news.py`) i działa dalej.
"""
import os

# Klucze odbierane testom. Lazy-init każdego mostu sprawdza `os.getenv(...)` — bez klucza
# schodzi na deterministyczny fallback zamiast wołać sieć.
KLUCZE_ODEBRANE_TESTOM = (
    "DEEPSEEK_API_KEY",   # most LLM (news_llm, auto-lekcje, Senat, zwiad)
    "MEXC_API_KEY",       # egzekucja — test NIGDY nie może złożyć zlecenia
    "MEXC_SECRET",
)


def zaloz_zapore():
    """Usuwa klucze ze środowiska procesu testowego. Idempotentne. → lista odebranych."""
    odebrane = []
    for klucz in KLUCZE_ODEBRANE_TESTOM:
        if os.environ.pop(klucz, None) is not None:
            odebrane.append(klucz)
    return odebrane


# Zakładamy zaporę przy IMPORCIE — zanim pytest zbierze i zaimportuje moduły testowe
# (import modułu potrafi już zbudować adapter). Później = za późno.
_ODEBRANE = zaloz_zapore()
