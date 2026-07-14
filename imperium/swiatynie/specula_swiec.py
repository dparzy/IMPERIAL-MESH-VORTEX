"""
🗼 SPECULA — Wieża Obserwacyjna (świece OHLC w terminalu, W-361, Prawo XXIV).

Dokłada wykres ŚWIECOWY do podglądu live w terminalu — świece jak na MEXC, ale
bez przeglądarki. Komplementarne (Prawo XVI, nie redundancja) wobec dwóch istniejących
kanałów obserwacji:
  • web_dashboard.py — świece w PRZEGLĄDARCE (TradingView Lightweight Charts),
  • live_monitor.py  — TUI w TERMINALU, ale tylko liczby/tabele (bez świec).
SPECULA wypełnia lukę: świece OHLC bezpośrednio w oknie terminala.

RENDERER OPCJONALNY (filozofia „runner bez deps"): używa `plotext` (PyPI, MIT, ZERO
obowiązkowych zależności). Gdy plotext NIEzainstalowany → degraduje się elegancko
(komunikat-podpowiedź, nigdy crash) — rdzeń Imperium i testy zostają bez zależności,
dokładnie jak matplotlib w kartografie czy calibre/rapidocr w bibliotece.
  Włączenie:  pip install plotext

Karmiona TYM SAMYM feedem OHLC co reszta roju (bary z DataLoader/petla_live):
    bar = {"timestamp": ms, "open", "high", "low", "close", "volume", "symbol", "interwal"}

Znaczniki wejść/wyjść bota (opcjonalne) rysują ▲ (wejście) / ▼ (wyjście) na świecach,
zielone dla LONG, czerwone dla SHORT — Cezar widzi GDZIE rój wchodzi i wychodzi.

Nazwa rzymska (ZASADA NOMENKLATURY IMPERIALNEJ): SPECULA = rzymska wieża strażnicza /
punkt obserwacyjny, z którego legiony obserwowały teren. Tu Cezar obserwuje rynek.

Uwaga Windows: plotext wymaga formy daty z pełną datą ("d/m/Y H:M") + lokalnego
`fromtimestamp` — sama "H:M" wywraca się na `fromtimestamp` (OSError 22) po odjęciu
time0 (zweryfikowane w runtime na Windows 10).
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, Optional, Sequence

try:
    import plotext as _plt
    PLOTEXT_DOSTEPNY = True
except ImportError:  # pragma: no cover — zależy od środowiska
    _plt = None
    PLOTEXT_DOSTEPNY = False

# candlestick plotext potrzebuje ≥2 świec (rysuje knoty/ciała względem sąsiadów)
MIN_BARY = 2
# Forma daty z PEŁNĄ datą — bez niej plotext pada na Windows (patrz docstring)
_DATE_FORM = "d/m/Y H:M"
# Domyślna szerokość = szerokość ramki TUI live_monitor (spójny widok)
_SZEROKOSC_DOMYSLNA = 72


def komunikat_braku_plotext() -> str:
    """Podpowiedź gdy plotext niezainstalowany — panel wyłączony, nie crash."""
    return (
        "🗼 SPECULA: wykres świec wyłączony — brak biblioteki `plotext`.\n"
        "   Włącz (opcjonalny dodatek, MIT, zero zależności): pip install plotext"
    )


def _ts_na_string(ts_ms: int) -> str:
    """Timestamp (ms) → string daty w formie plotext. Lokalny czas (Windows-safe)."""
    return _plt.datetime_to_string(_dt.datetime.fromtimestamp(ts_ms / 1000))


def render_swiece(
    bary: Sequence[Dict],
    *,
    wysokosc: int = 15,
    szerokosc: int = 0,
    tytul: Optional[str] = None,
    znaczniki: Optional[Sequence[Dict]] = None,
    motyw: str = "pro",
) -> str:
    """
    Zbuduj świecowy wykres OHLC jako STRING (do wypisania w terminalu).

    Parametry:
      bary       — lista dictów z kluczami open/high/low/close/timestamp (format Imperium).
      wysokosc   — wysokość wykresu w liniach terminala.
      szerokosc  — szerokość w kolumnach; 0 → domyślna (szerokość ramki TUI = 72).
      tytul      — opcjonalny tytuł nad wykresem (np. "BTCUSDT 1H").
      znaczniki  — opcjonalne wejścia/wyjścia bota, lista dictów:
                     {"timestamp": ms, "cena": float,
                      "kierunek": "LONG"/"SHORT", "typ": "wejscie"/"wyjscie"}
      motyw      — motyw plotext (domyślnie "pro").

    Zwraca gotowy string wykresu. NIGDY nie rzuca wyjątku: przy braku plotext,
    zbyt małej liczbie barów lub błędzie renderu zwraca komunikat-podpowiedź.
    """
    if not PLOTEXT_DOSTEPNY:
        return komunikat_braku_plotext()

    n = len(bary) if bary else 0
    if n < MIN_BARY:
        return f"🗼 SPECULA: za mało barów na świece ({n}/{MIN_BARY} minimum)."

    try:
        _plt.clf()
        _plt.date_form(_DATE_FORM)  # MUSI być po clf() — clf resetuje formę
        dates = [_ts_na_string(int(b["timestamp"])) for b in bary]
        data = {
            "Open":  [float(b["open"])  for b in bary],
            "High":  [float(b["high"])  for b in bary],
            "Low":   [float(b["low"])   for b in bary],
            "Close": [float(b["close"]) for b in bary],
        }
        _plt.candlestick(dates, data)

        # Znaczniki wejść/wyjść bota — ▲ wejście / ▼ wyjście, zielone LONG / czerwone SHORT
        if znaczniki:
            for zn in znaczniki:
                try:
                    d = _ts_na_string(int(zn["timestamp"]))
                    marker = "▼" if zn.get("typ") == "wyjscie" else "▲"
                    kolor = "red" if zn.get("kierunek") == "SHORT" else "green"
                    _plt.scatter([d], [float(zn["cena"])], marker=marker, color=kolor)
                except (KeyError, ValueError, TypeError):
                    continue  # pojedynczy zły znacznik nie psuje całego wykresu

        _plt.plotsize(szerokosc or _SZEROKOSC_DOMYSLNA, wysokosc)
        if tytul:
            _plt.title(tytul)
        try:
            _plt.theme(motyw)
        except Exception:  # nieznany motyw nie może wywrócić wykresu
            pass
        return _plt.build()
    except Exception as e:  # ostatnia linia obrony — podgląd nigdy nie ubija pętli
        return f"🗼 SPECULA: błąd renderu świec ({type(e).__name__}: {e})."
