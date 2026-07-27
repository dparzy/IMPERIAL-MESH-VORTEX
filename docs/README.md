---
kategoria: TABULA
typ: zywy
wlasciciel: —
stan_na: 2026-07-27
powod_istnienia: "Wskaźnik na katalog dokumentów — sam spisu NIE trzyma; kieruje do generowanego katalogu w INDEKS_IMPERIUM (jedno źródło prawdy, Prawo XVI)."
---
# 📚 Dokumentacja Imperium

Tu trafia **uporządkowana wiedza** wyciągnięta z surowej wizji (`archiwum/`).
Każdy temat = osobny, czytelny plik. To jest trwała pamięć projektu.

## 🧭 Spis dokumentów → [`INDEKS_IMPERIUM.md`](INDEKS_IMPERIUM.md)

**Pełny katalog wszystkich dokumentów** (plik → temat → opisywany kod → data stanu)
mieszka w jednym miejscu: sekcja `TABULARIUM` w
[`INDEKS_IMPERIUM.md`](INDEKS_IMPERIUM.md). Jest **generowana z nagłówków samych
dokumentów**:

```bash
python narzedzia/tabularium.py katalog --zapisz
```

Dzięki temu nie umie się zestarzeć: nowy dokument z poprawnym nagłówkiem wchodzi do
katalogu sam, a Warstwa 20 audytu pilnuje, żeby nikt nie dopisał tam wiersza ręką.

## ❌ Dlaczego tego spisu tu NIE MA (decyzja 2026-07-27)

Ten plik trzymał **drugi, ręczny spis** tych samych dokumentów. Zmierzone przed
usunięciem: wymieniał **22 z 56** plików `docs/*.md` — **33 dokumenty (59% korpusu)
były dla niego niewidzialne**, w tym `MANIFEST_KODU`, `LOG_ZMIAN`, `PROFIL_CEZARA`,
`START_LOKAL` i wszystkie trzy `WIZJA_*`. Katalog generowany widział je wszystkie.

To klasyczne **drugie źródło prawdy** (Prawo XVI): dwa spisy tej samej rzeczy rozjadą
się co do sztuki, a gnije zawsze ten pisany ręką. Lekarstwem — jak w CENSUS ORGANORUM
(W17) i w SIGLA IMPERII — jest **odebranie dokumentowi prawa do własnej treści**.

Rozważaliśmy też *generowanie* tego spisu z Tabularium. Odrzucone: dawałoby dwie
generowane kopie tej samej tabeli, czyli redundancję bez nowej informacji (Prawo XVI) —
dwa artefakty do regeneracji i dwie bramki zamiast jednej. Wskaźnik kosztuje zero.

**Bramka:** Warstwa 22 audytu (`narzedzia/audyt_spojnosci.py`) blokuje odrodzenie się
ręcznego katalogu w jakimkolwiek dokumencie poza `INDEKS_IMPERIUM.md`.

## Pozostałe punkty wejścia

| Dokąd | Po co |
|-------|-------|
| [`../README.md`](../README.md) | Wizytówka Imperium — liczby wprost z kodu (neurony, testy, prawa) |
| [`../CLAUDE.md`](../CLAUDE.md) | Konstytucja — rozkazy stałe dla Architekta |
| [`../ZASADY_FUNDAMENTALNE.md`](../ZASADY_FUNDAMENTALNE.md) | 25 Praw Imperium |
