"""
🐞 KSIĘGA WAD KODU — pamięć wzorców błędów (samo-leczenie, Prawo XV/XVI).

Odpowiednik `ksiega_wad` (wady setupu tradingowego), ale dla KODU. Zapamiętuje
klasy błędów, które łapie recenzja (cubic / `/code-review`), żeby NIE powtarzać ich
w przyszłości: przy pisaniu/recenzji kodu Claude sprawdza księgę NAJPIERW.

Dwie zdolności:
  • pamięć (JSONL, wersjonowana w git — wiedza uniwersalna, nie per-maszyna),
  • heurystyczny skan: `skanuj(tekst)` dopasowuje znane wzorce (regex) do kodu i
    zwraca trafienia z lekcją. To NUDGE, nie dowód (Prawo I) — sygnalizuje „sprawdź to".

DLA NOWICJUSZA: cubic (zewnętrzny bot) łapał błędy, których my sami nie sprawdzaliśmy —
bo pisaliśmy „happy path". Ta księga to pamięć „co MOŻE pójść źle", zbierana z każdej
recenzji, więc z czasem sami łapiemy to, co wcześniej łapał tylko cubic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOMYSLNA = ROOT / "bibliotheca_ulpia" / "dane" / "ksiega_wad_kodu.jsonl"

# Wzorce startowe — destylat realnych uwag cubic (2026-07). Wysokosygnałowe, niskofałszywe.
WZORCE_STARTOWE = [
    {"kat": "odpornosc", "regex": r'req\s*\[\s*[\'"]params[\'"]\s*\]\s*\[',
     "opis": "Dostęp do pól requestu POZA try",
     "lekcja": "Parsuj pola żądania WEWNĄTRZ try — malformed request → JSON-RPC error, nie crash procesu.",
     "zrodlo": "cubic arena_mcp P1 (2026-07-05)"},
    {"kat": "kontrakt", "regex": r'ORDER BY id\b',
     "opis": "Sortowanie po id zamiast po czasie zdarzenia",
     "lekcja": "Dla danych z timestampem sortuj ORDER BY ts (id jako tie-breaker) — backfill nie udaje najnowszego.",
     "zrodlo": "cubic arena_baza P2 (2026-07-05)"},
    {"kat": "kontrakt", "regex": r'int\(\s*\w+\.get\(\s*[\'"]limit[\'"]',
     "opis": "limit z requestu bez clampu do reklamowanego zakresu",
     "lekcja": "Reklamujesz zakres (np. 1-100) → wymuś go: min(max, max(min, wartosc)).",
     "zrodlo": "cubic arena_mcp P2 (2026-07-05)"},
    {"kat": "granice", "regex": r'pytest\.raises\(ValueError\)',
     "opis": "Test progu bez przypadku None",
     "lekcja": "Reguła Test-Granic: None w progu daje TypeError, nie ValueError — dodaj jawny przypadek None.",
     "zrodlo": "cubic test_kalibrator P2 (2026-07-05)"},
    {"kat": "odpornosc", "regex": r'for .+ in .+:\s*(#.*)?\n\s+.*(connect|_polacz)\(',
     "opis": "Połączenie do bazy w pętli (I/O per iteracja)",
     "lekcja": "Batchuj zapisy — jedno połączenie na partię, nie per-element (latencja w pętli live).",
     "zrodlo": "cubic petla_live P2 (2026-07-05)"},
]


class KsiegaWadKodu:
    """Pamięć wzorców błędów kodu + heurystyczny skaner."""

    def __init__(self, sciezka: Path | str = DOMYSLNA):
        self.sciezka = Path(sciezka)
        self.wpisy: list[dict] = []
        self._wczytaj()

    def _wczytaj(self) -> None:
        if not self.sciezka.exists():
            return
        for linia in self.sciezka.read_text(encoding="utf-8").splitlines():
            linia = linia.strip()
            if linia:
                try:
                    self.wpisy.append(json.loads(linia))
                except json.JSONDecodeError:
                    continue

    def zapisz(self) -> None:
        self.sciezka.parent.mkdir(parents=True, exist_ok=True)
        with self.sciezka.open("w", encoding="utf-8") as f:
            for w in self.wpisy:
                f.write(json.dumps(w, ensure_ascii=False) + "\n")

    def dodaj(self, kat: str, regex: str, opis: str, lekcja: str, zrodlo: str = "") -> bool:
        """Dodaje wzorzec. Odrzuca duplikat regex i błędny regex. Zwraca czy dodano."""
        if not regex or not opis:
            raise ValueError("regex i opis są wymagane")
        try:
            re.compile(regex)
        except re.error as e:
            raise ValueError(f"niepoprawny regex: {e}") from e
        if any(w["regex"] == regex for w in self.wpisy):
            return False   # już znany wzorzec — nie dubluj (Prawo XVI)
        self.wpisy.append({"kat": kat, "regex": regex, "opis": opis,
                           "lekcja": lekcja, "zrodlo": zrodlo})
        return True

    def skanuj(self, tekst: str) -> list[dict]:
        """Zwraca trafienia: {wpis, linia} — które znane wzorce pasują do kodu (nudge)."""
        trafienia = []
        for w in self.wpisy:
            try:
                wzor = re.compile(w["regex"], re.MULTILINE)
            except re.error:
                continue
            m = wzor.search(tekst)
            if m:
                linia = tekst.count("\n", 0, m.start()) + 1
                trafienia.append({"kat": w["kat"], "opis": w["opis"],
                                  "lekcja": w["lekcja"], "linia": linia})
        return trafienia

    def wszystkie(self) -> list[dict]:
        return list(self.wpisy)


def zasiej_startowe(sciezka: Path | str = DOMYSLNA) -> int:
    """Tworzy księgę z wzorcami startowymi jeśli pusta. Zwraca liczbę dodanych."""
    k = KsiegaWadKodu(sciezka)
    dodane = 0
    for w in WZORCE_STARTOWE:
        if k.dodaj(w["kat"], w["regex"], w["opis"], w["lekcja"], w["zrodlo"]):
            dodane += 1
    if dodane:
        k.zapisz()
    return dodane
