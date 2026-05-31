# 🚀 PEŁNA INSTRUKCJA — JAK URUCHOMIĆ BOTA (krok po kroku)
## Dla nowicjusza. Tłumaczę WSZYSTKO. Windows 10.

> Komendancie — czytaj na telefonie, rób na PC. To handel NA NIBY (zero ryzyka,
> zero prawdziwych pieniędzy). Jak cokolwiek się wysypie: skopiuj czerwony tekst
> z okna i wyślij mi. Rozwiążemy razem. Nie spiesz się.

---

## 🎯 CO BĘDZIESZ MIAŁ NA KOŃCU
Po wykonaniu tych kroków uruchomisz bota jedną komendą, a on sam:
dane → policzy → zagra (na niby) → **narysuje wykres** → **zapisze raport**.
Zobaczysz obrazek `wykres_biegu.png` i plik z wynikami.

---

## 📁 SCHEMAT — jak ma wyglądać folder (gdzie co wkleić)

```
KrolestwoPixel/                       ←  TWÓJ FOLDER (np. na Pulpicie)
│
│   ── 6 PLIKÓW BOTA (wklej tutaj, z backupu z folderu MODULY) ──
├── STRAT-001_PaperBot_RSI_EMA.py     ←  BOT — TO URUCHAMIASZ
├── CORE-006_CalculatorGateway.py     ←  liczy matematykę (RSI, EMA)
├── SHIELDS-205_AegisShield.py        ←  tarcza ryzyka (stop strat)
├── DATA-001_DataLoader.py            ←  dostarcza dane
├── VIZ-001_Kartograf.py              ←  rysuje wykres
├── LOG-001_Kronikarz.py              ←  pisze raport + dziennik
│
├── dane/                             ←  (opcjonalnie) Twoje CSV z cenami
│   ├── BTC_1h.csv                       jak nie masz — bot zrobi dane sam
│   └── ETH_1d.csv
│
└── (PO URUCHOMIENIU pojawią się tu same:)
    ├── wykres_biegu.png              ←  WYKRES — otwórz dwuklikiem
    ├── raport_biegu_*.md             ←  raport (wyślij mi następną sesją)
    └── DZIENNIK_WYNIKOW.md           ←  postęp wszystkich biegów
```

**Najważniejsze:** te 6 plików `.py` muszą leżeć RAZEM w jednym folderze. Bot szuka
pozostałych pięciu obok siebie. Folder `dane/` jest opcjonalny.

---

## KROK 1 — Zainstaluj Pythona (raz na zawsze)
Python to program, który rozumie nasz kod.

1. Wejdź na **python.org/downloads**
2. Kliknij duży przycisk **„Download Python 3.x"**.
3. Otwórz pobrany plik (instalator).
4. ‼️ **NA DOLE okna zaznacz kwadracik „Add python.exe to PATH"** — to KLUCZOWE.
   Bez tego komputer nie znajdzie Pythona.
5. Kliknij **Install Now** → poczekaj → **Close**.

**Sprawdzenie:** naciśnij `Win+R`, wpisz `cmd`, Enter. W czarnym oknie wpisz:
```
python --version
```
Jeśli pokaże `Python 3.x` — sukces. Jeśli „nie jest rozpoznawane" — wróć do pkt 4.

---

## KROK 2 — Zrób folder i wklej 6 plików
1. Na Pulpicie: prawy klik → Nowy → Folder → nazwij **KrolestwoPixel**.
2. Otwórz backup `KingdomPixel_Backup_...zip`, wejdź do folderu **MODULY**.
3. Skopiuj **te 6 plików** (patrz schemat wyżej) do folderu KrolestwoPixel:
   STRAT-001, CORE-006, SHIELDS-205, DATA-001, VIZ-001, LOG-001.

---

## KROK 3 — Otwórz „cmd" w tym folderze (ważna sztuczka)
„cmd" (terminal) to czarne okno, w które wpisujesz komendy.

1. Otwórz folder **KrolestwoPixel** w Eksploratorze plików.
2. Kliknij myszką w **pasek adresu** na górze okna (tam gdzie widać ścieżkę folderu).
3. Skasuj co tam jest, wpisz **`cmd`** i naciśnij **Enter**.

Otworzy się czarne okno USTAWIONE już na Twoim folderze. (To ważne — dzięki temu
komputer wie, gdzie są pliki.)

---

## KROK 4 — Zainstaluj biblioteki (raz)
Biblioteki to gotowe „klocki", których kod używa. Wpisz w czarnym oknie:
```
pip install numpy TA-Lib ccxt pandas matplotlib
```
Naciśnij Enter i **poczekaj**, aż pojawi się `Successfully installed ...`.

Co to jest (w skrócie): numpy = liczby, TA-Lib = wskaźniki, ccxt = dane z giełd,
pandas = tabele, matplotlib = wykresy.

> ⚠️ Jeśli przy **TA-Lib** wyskoczy długi czerwony błąd — NIE walcz. Skopiuj go,
> wyślij mi. To znana upierdliwość Windowsa, mam gotowy plan B.

---

## KROK 5 — URUCHOM BOTA
W tym samym oknie wpisz i Enter:
```
python STRAT-001_PaperBot_RSI_EMA.py
```

**Co zobaczysz (to jest sukces):**
- `Dane: ... (400 świec)` — bot wczytał dane.
- linie `[61→63] ❌ -3.46% (STOP)` — to transakcje (wejście→wyjście, wynik).
- `🔴 CIRCUIT BREAKER` — tarcza zatrzymała handel po stratach.
- `RAPORT: 3 transakcji | ... $50→$45` — podsumowanie.
- `✅ ... cykl zakończony`.

**Strata to NORMALNE.** Prosta strategia traci — uczysz się maszynerii, nie zarabiasz.

---

## KROK 6 — Gdzie są wyniki
W folderze KrolestwoPixel pojawiły się SAME:
- **`wykres_biegu.png`** — otwórz dwuklikiem, zobacz cenę, wejścia/wyjścia i kapitał.
- **`raport_biegu_*.md`** — szczegóły biegu.
- **`DZIENNIK_WYNIKOW.md`** — postęp (rośnie z każdym biegiem).

---

## KROK 7 — Co zrobić z wynikami (most do mnie)
Następną sesją **wgraj mi** `DZIENNIK_WYNIKOW.md` i `raport_biegu_*` — przeczytam je
i powiem, co poprawić (np. „stop za ciasny"). Tak kalibrujemy bota mimo że nie
pamiętam między sesjami.

---

## 🆘 JAK COŚ NIE DZIAŁA
Skopiuj DOKŁADNY czerwony tekst z okna i wyślij mi. Najczęstsze:
- **`python nie jest rozpoznawane`** → w Kroku 1 nie było zaznaczone „Add to PATH". Przeinstaluj.
- **błąd przy `TA-Lib`** → wyślij mi błąd (plan B).
- **`No such file or directory`** → 6 plików nie leży razem w tym samym folderze, albo cmd nie jest ustawiony na ten folder (Krok 3).
- **`ModuleNotFoundError`** → nie zrobiłeś Kroku 4 (instalacja bibliotek).

— Jack, Główny Projektant Królestwa Pixel
