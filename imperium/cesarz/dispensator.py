"""DISPENSATOR — Szafarz Imperium: ile myślenia KUPUJEMY do danego zadania.

W Rzymie *dispensator* był zarządcą kasy domu — decydował, na co wydać, a na czym
oszczędzić. Ten organ robi to samo z tokenami: dobiera MODEL i GŁĘBOKOŚĆ ROZUMOWANIA
do rodzaju zadania, zamiast płacić najwyższą stawkę za wszystko.

POWÓD POWSTANIA (zmierzone 2026-07-20 na żywym API — ta sama odpowiedź „391"):

    flash + thinking:disabled   0 tokenów rozumowania   $0.0000028   ← 1×
    flash (nasze DZISIEJSZE)  106 tokenów rozumowania   $0.0000328   ← 11.7×
    v4-pro                     69 tokenów rozumowania   $0.0000696   ← 24.9×

Imperium używa DZIŚ jednego ustawienia domyślnego dla wszystkiego: `deepseek-v4-flash`
z rozumowaniem włączonym, którego treści (`reasoning_content`) nigdzie nie czytamy.
Czyli płacimy ~12× za coś, czego przy klasyfikacji newsa nie potrzebujemy — a przy
osądzie kandydatów na neurony nie kupujemy modelu premium, choć jest w zasięgu.

CO ZMIERZONE, A CO NIE (Prawo I):
  • ceny — dokumentacja api-docs.deepseek.com/quick_start/pricing, odczyt 2026-07-20
  • `thinking:{"type":"disabled"}` wyłącza rozumowanie — POTWIERDZONE pomiarem
  • `reasoning_effort` ∈ {low, medium, high, max, xhigh} — lista wydobyta z komunikatu
    błędu API (dokumentacja podaje tylko przykład „high")
  • wpływ profilu na JAKOŚĆ odpowiedzi — NIEZMIERZONY. Profile poniżej to HIPOTEZY
    kosztowe, nie dowiedziona jakość. Dlatego organ jest OPT-IN (ZASADA WPIĘCIA).

CZEGO ORGAN NIE ROBI: nie decyduje o wejściu/wyjściu z pozycji, nie dotyka ścieżki
decyzyjnej tradingu. Dobiera wyłącznie parametry wywołania LLM.
"""
from __future__ import annotations

from typing import Any, Dict

# ── Cennik ($/1M tokenów) — api-docs.deepseek.com/quick_start/pricing, 2026-07-20 ──
# Trzymamy w kodzie, bo bez ceny nie da się policzyć kosztu biegu. Gdy dostawca zmieni
# cennik, ta stała skłamie — dlatego `raport_kosztu` podaje datę odczytu razem z liczbą.
CENNIK_DATA = "2026-07-20"
CENNIK: Dict[str, Dict[str, float]] = {
    "deepseek-v4-flash": {"wejscie": 0.14, "wejscie_cache": 0.0028, "wyjscie": 0.28},
    "deepseek-v4-pro":   {"wejscie": 0.435, "wejscie_cache": 0.003625, "wyjscie": 0.87},
}

POZIOMY_ROZUMOWANIA = ("low", "medium", "high", "max", "xhigh")

# ── Profile: rodzaj zadania → co kupujemy ────────────────────────────────────────
# Zasada doboru ta sama co w tabeli „model wg trudności" dla modeli Claude (CLAUDE.md):
# mechaniczne — najtaniej; osąd o konsekwencjach — najdroższe. Różnica: tam wybieramy
# model sesji, tu parametry pojedynczego wywołania.
PROFILE: Dict[str, Dict[str, Any]] = {
    # Klasyfikacja/ekstrakcja: model ma wybrać etykietę, nie rozważać. Rozumowanie to
    # czysty koszt — zmierzone: 106 tokenów na policzenie 17×23.
    "klasyfikacja": {
        "model": "deepseek-v4-flash", "thinking": {"type": "disabled"},
        "po_co": "sentyment newsa, tagowanie, ekstrakcja pól — jedna etykieta, zero rozważań",
    },
    # Zwiad objętościowy: dużo fragmentów, płytka analiza każdego. Rozumowanie pomaga
    # trzymać spójność, ale nie musi być głębokie.
    "zwiad": {
        "model": "deepseek-v4-flash", "reasoning_effort": "low",
        "po_co": "Hyginus czytający fragmenty RAG — objętość ważniejsza od głębi",
    },
    # Krytyka: szukanie dowodów PRZECIW własnym kandydatom wymaga realnego rozważania.
    "krytyka": {
        "model": "deepseek-v4-flash", "reasoning_effort": "high",
        "po_co": "self-critique Hyginusa — druga perspektywa, dowody przeciw",
    },
    # Osąd: konsekwencje długoterminowe (co wchodzi do roju). Tu stać nas na premium.
    "osad": {
        "model": "deepseek-v4-pro", "reasoning_effort": "high",
        "po_co": "ocena kandydatów na neurony/strategie — decyzja o konsekwencjach",
    },
}
PROFIL_DOMYSLNY = "zwiad"


def dobierz(zadanie: str = PROFIL_DOMYSLNY) -> Dict[str, Any]:
    """Parametry wywołania API dla rodzaju zadania. Nieznany rodzaj → profil domyślny.

    Nieznana nazwa NIE rzuca wyjątkiem: dobór parametrów jest optymalizacją kosztu, a nie
    warunkiem mowy — most ma się odezwać nawet przy literówce w nazwie profilu (ta sama
    filozofia co NOTARIUS: dodatek do mowy, nigdy jej warunek).
    """
    p = dict(PROFILE.get(zadanie, PROFILE[PROFIL_DOMYSLNY]))
    p.pop("po_co", None)
    return p


def koszt_usd(usage: Any, model: str) -> float | None:
    """Koszt wywołania z FAKTYCZNEGO zużycia. None gdy brak cennika dla modelu.

    Tokeny rozumowania są częścią `completion_tokens` (zmierzone), więc liczą się po
    stawce wyjściowej — nie ma osobnej, tańszej taryfy za myślenie.
    """
    c = CENNIK.get(model)
    if not c or usage is None:
        return None

    def _pole(nazwa: str, domyslnie: int = 0) -> int:
        if isinstance(usage, dict):
            return int(usage.get(nazwa) or domyslnie)
        return int(getattr(usage, nazwa, domyslnie) or domyslnie)

    wejscie = _pole("prompt_tokens")
    wyjscie = _pole("completion_tokens")
    trafienia = _pole("prompt_cache_hit_tokens")
    swieze = max(0, wejscie - trafienia)
    return (swieze * c["wejscie"] + trafienia * c["wejscie_cache"]
            + wyjscie * c["wyjscie"]) / 1_000_000


def tokeny_rozumowania(usage: Any) -> int:
    """Ile tokenów poszło na rozumowanie (0 gdy brak danych)."""
    if usage is None:
        return 0
    det = (usage.get("completion_tokens_details") if isinstance(usage, dict)
           else getattr(usage, "completion_tokens_details", None))
    if det is None:
        return 0
    return int((det.get("reasoning_tokens") if isinstance(det, dict)
                else getattr(det, "reasoning_tokens", 0)) or 0)


def diagnoza_pustej(tresc: str | None, usage: Any = None) -> str | None:
    """Zwraca OPIS problemu, gdy odpowiedź jest pusta. None = treść jest.

    PUŁAPKA ZMIERZONA 2026-07-20: przy `max_tokens=300` model spalił 300 tokenów na
    rozumowanie i zwrócił content = "" — z kodem HTTP 200. Wywołanie WYGLĄDA na udane,
    a wyniku nie ma; wołający dostanie pusty string i uzna go za odpowiedź.
    Rozróżniamy DWA powody pustki, bo prowadzą do różnych napraw:
      • rozumowanie zjadło budżet  → podnieś max_tokens albo obniż reasoning_effort
      • pustka bez rozumowania     → problem po stronie promptu/modelu, nie budżetu
    """
    if tresc and tresc.strip():
        return None
    rozum = tokeny_rozumowania(usage)
    if rozum > 0:
        return (f"pusta treść przy {rozum} tokenach rozumowania — rozumowanie zjadło budżet "
                "wyjścia; podnieś max_tokens albo obniż reasoning_effort")
    return "pusta treść bez rozumowania — przyczyna po stronie promptu lub modelu"


def opis_profili() -> str:
    """Zero-tokenowy przegląd: co który profil kupuje i po co."""
    linie = [f"💰 DISPENSATOR — profile doboru (cennik z {CENNIK_DATA})"]
    for nazwa, p in PROFILE.items():
        mysli = ("WYŁĄCZONE" if p.get("thinking", {}).get("type") == "disabled"
                 else f"effort={p.get('reasoning_effort', 'domyślny')}")
        linie.append(f"   {nazwa:14} {p['model']:20} rozumowanie: {mysli:18} — {p['po_co']}")
    return "\n".join(linie)


if __name__ == "__main__":
    print(opis_profili())
