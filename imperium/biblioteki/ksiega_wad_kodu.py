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
    # ── cubic PR#122 (2026-07-13) — wzorce składniowe, które POPRAWNY kod omija ──
    {"kat": "cache", "regex": r'pytaj_pomiary\([^)]*neuron\s*=\s*nazwa\b',
     "opis": "Wznawianie z areny kluczowane samą nazwą pliku (bez podpisu konfiguracji)",
     "lekcja": "Klucz areny/cache MUSI nieść podpis konfiguracji (frac/okno/cap/interwał) — inaczej "
               "zmiana parametru cicho podstawia nieświeży wynik. Wpuść config w klucz `neuron=` "
               "albo zwaliduj parametry z noty przed pominięciem pary.",
     "zrodlo": "cubic PR#122 ab_* P1/P2 (2026-07-13)"},
    {"kat": "granice",
     "regex": r'add_argument\(\s*[\'"]--(?:topk|top-k|prog[_-]?ic)[\'"][^)]*type\s*=\s*(?:int|float)\b',
     "opis": "Argument liczbowy sterujący kosztem API / progiem bez walidacji zakresu",
     "lekcja": "Argument sterujący kosztem (topk → rozmiar korpusu do PŁATNEGO API) lub semantyką progu "
               "(prog_ic) waliduj przy parsowaniu — type=funkcja z zakresem/skończonością, nie gołe int/float.",
     "zrodlo": "cubic PR#122 bibliotekarz/ab_pnl P2/P3 (2026-07-13)"},
]

# ── CHECKLISTA REVIEW (bez regexu) — klasy SEMANTYCZNE, których forma składniowa jest
# identyczna z poprawnym kodem (flip znaku, nan, suma%, niezgodne długości). Regex dałby
# tu SZUM na naszym własnym poprawnym kodzie (zmierzone: „SHORT if ==LONG" = 11 trafień
# legalnego idiomu), więc NIE auto-skanujemy — pokazujemy jako checklistę przed pushem
# (obok /code-review). „Wszystko ma być łapane" (Prawo XV) dwiema warstwami: regex łapie
# formę, checklista łapie znaczenie.
CHECKLIST_STARTOWA = [
    {"kat": "kierunek",
     "opis": "Odwrócenie kierunku (flip znakiem) bez propagacji do WSZYSTKICH konsumentów",
     "lekcja": "Gdy odwracasz kierunek (np. ujemny IC → LONG↔SHORT), KAŻDY konsument w dół (dobór "
               "strategii, weto konfluencji, licznik zgodnych, synapsy) musi czytać kierunek EFEKTYWNY, "
               "nie surowy — inaczej wejdzie na przeciwną stronę niż skorygowany agregat. Surowe znaki "
               "zostaw wyłącznie do audytu/treningu.",
     "zrodlo": "cubic PR#122 legatus P1 (2026-07-13)"},
    {"kat": "granice",
     "opis": "Wartość nan/nieskończona przed zapisem cząstki, porównaniem lub agregatem",
     "lekcja": "Funkcja zwracająca nan (brak decyzji, pusty mianownik) — zanim wynik trafi do checkpointu "
               "areny lub porównania (nan>x=False cicho przekłamuje werdykt), sprawdź math.isfinite i "
               "pomiń/oznacz jako niekonkluzywne; kolejne jednostki mają liczyć się dalej.",
     "zrodlo": "cubic PR#122 ab_wazenie_ic P2 (2026-07-13)"},
    {"kat": "kontrakt",
     "opis": "Suma procentowych zwrotów per-jednostka prezentowana jako wynik portfela",
     "lekcja": "Suma % rośnie liniowo z liczbą par/jednostek — to nie P&L portfela. Uśrednij (sum/N) lub "
               "zważ przed prezentacją; werdykt oparty na sumie zawyża się z rozmiarem próby.",
     "zrodlo": "cubic PR#122 ab_strategy_mwu P2 (2026-07-13)"},
    {"kat": "werdykt",
     "opis": "Werdykt/większość liczona z jednostek bez realnego samplu",
     "lekcja": "Jednostki bez transakcji/decyzji (ret 0, brak głosów) nie mogą przechylać większości ani "
               "portfela — licz werdykt z par spełniających próg (np. ≥ MIN_TRADES) lub oznacz bieg niekonkluzywnym.",
     "zrodlo": "cubic PR#122 ab_tryb_strategii P2 (2026-07-13)"},
    {"kat": "kontrakt",
     "opis": "Niezgodne długości sparowanych serii (sygnał ↔ etykieta forward)",
     "lekcja": "Serie, które MUSZĄ być równoległe (sygnał i etykieta forward, cena i wynik), sprawdzaj na "
               "równość długości i odrzucaj rozjazd zanim policzysz — zip cicho ucina ogon i liczy z "
               "niezamierzonego podzbioru (look-ahead / skażone wagi).",
     "zrodlo": "cubic PR#122 legatus/hipoteza_b P2/P3 (2026-07-13)"},
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

    def dodaj_checklist(self, kat: str, opis: str, lekcja: str, zrodlo: str = "") -> bool:
        """Dodaje pozycję CHECKLISTY review (bez regexu — klasa semantyczna, nie auto-skan).
        Dedup po opisie (brak regexu jako klucza). Zwraca czy dodano."""
        if not opis or not lekcja:
            raise ValueError("opis i lekcja są wymagane")
        if any(not w.get("regex") and w["opis"] == opis for w in self.wpisy):
            return False
        self.wpisy.append({"kat": kat, "regex": "", "opis": opis,
                           "lekcja": lekcja, "zrodlo": zrodlo})
        return True

    def skanuj(self, tekst: str) -> list[dict]:
        """Zwraca trafienia: {wpis, linia} — które znane wzorce REGEX pasują do kodu (nudge).
        Pozycje checklisty (pusty regex) są pomijane — nie auto-skanują (byłby szum)."""
        trafienia = []
        for w in self.wpisy:
            if not w.get("regex"):        # checklista review — nie auto-skanujemy
                continue
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

    def wzorce(self) -> list[dict]:
        """Pozycje z regexem (auto-skanowalne)."""
        return [w for w in self.wpisy if w.get("regex")]

    def checklista(self) -> list[dict]:
        """Pozycje bez regexu — klasy semantyczne do ręcznego przeglądu przed pushem."""
        return [w for w in self.wpisy if not w.get("regex")]


def zasiej_startowe(sciezka: Path | str = DOMYSLNA) -> int:
    """Dosiewa brakujące wzorce REGEX i pozycje CHECKLISTY (idempotentnie). Zwraca liczbę dodanych."""
    k = KsiegaWadKodu(sciezka)
    dodane = 0
    for w in WZORCE_STARTOWE:
        if k.dodaj(w["kat"], w["regex"], w["opis"], w["lekcja"], w["zrodlo"]):
            dodane += 1
    for c in CHECKLIST_STARTOWA:
        if k.dodaj_checklist(c["kat"], c["opis"], c["lekcja"], c["zrodlo"]):
            dodane += 1
    if dodane:
        k.zapisz()
    return dodane
