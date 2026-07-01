"""
⚡ Wspólny most JIT (Numba) — opcjonalne przyspieszenie gorących pętli numerycznych.

ZASADA (Prawo I — testy bez zależności): Numba jest OPCJONALNA. Gdy zainstalowana,
gorące pętle (Viterbi Jump Model, frac-diff itd.) kompilują się do kodu maszynowego
(~3-10× szybciej). Gdy NIE ma jej w środowisku — `njit` staje się no-op dekoratorem,
funkcja działa jako czysty Python/numpy (wolniej, ale identyczny wynik).

Użycie:
    from imperium.legiony._jit import njit, NUMBA_DOSTEPNA

    @njit(cache=True)
    def _hot_loop(x):
        ...

Dzięki temu kod numeryczny piszemy raz (jawne pętle — numba je uwielbia), a środowisko
decyduje o tempie. Lokalnie Cezar ma pełną moc; w chmurze fallback gwarantuje poprawność.

WYNIK MUSI BYĆ IDENTYCZNY jit vs fallback — to weryfikują testy (Reguła Test-Granic).
"""

from __future__ import annotations

try:
    from numba import njit as _numba_njit  # type: ignore
    NUMBA_DOSTEPNA = True
except Exception:   # ImportError lub błąd ładowania (np. brak libllvmlite)
    NUMBA_DOSTEPNA = False


def njit(*args, **kwargs):
    """
    Dekorator JIT. Z numbą → kompilacja (njit). Bez → no-op (czysty Python).

    Obsługuje obie formy:
      @njit                      (bez nawiasów)
      @njit(cache=True, ...)     (z opcjami)
    """
    # forma bez nawiasów: @njit nakłada się bezpośrednio na funkcję
    if len(args) == 1 and callable(args[0]) and not kwargs:
        fn = args[0]
        if NUMBA_DOSTEPNA:
            return _numba_njit(cache=True)(fn)
        return fn

    # forma z opcjami: @njit(...) → zwraca dekorator.
    # Domyślnie cache=True (spójnie z formą bez nawiasów) — @njit i @njit() zachowują się
    # identycznie; jawne cache=... w kwargs ma pierwszeństwo.
    opcje = {"cache": True, **kwargs}

    def _dekorator(fn):
        if NUMBA_DOSTEPNA:
            return _numba_njit(*args, **opcje)(fn)
        return fn
    return _dekorator
