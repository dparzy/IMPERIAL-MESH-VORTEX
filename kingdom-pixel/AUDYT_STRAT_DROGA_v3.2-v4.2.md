# 🗺️ DROGA OD POCZĄTKU — AUDYT STRAT v3.2 → v4.2

> **Autor:** Jack | **Dla:** Komendant Pixel | **Data:** 31.05.2026
> **Zadanie:** zaległy „raport CO ZOSTAŁO STRACONE między wersjami" (otwarte od `CLAUDE.md`/brudnopis v1.3).
> **Metoda:** rozpakowane wszystkie 11 backupów, policzone różnice plik-po-pliku. Twarde dane, nie pamięć (Z2).

---

## 🎯 WERDYKT

Były **dwa zdarzenia utraty**, oba częściowo zamierzone, ale **niekontrolowane** (bez raportu „co tracimy" — Z70). Reset v3.3 słusznie odciął balast Imperium, **ale przy okazji wyleciało realne złoto.** Migracja v4.0 zgubiła 3 moduły kodu i rejestr 330 wpisów. **Dobra wiadomość: właśnie wgrałeś komplet — wszystko jest odzyskiwalne.**

---

## 📅 OŚ CZASU

| Wersja | Data | Pliki | Charakter |
|:--|:--|:--:|:--|
| v3.2 | 05-26 | 33 | **Era Imperium/Tytan-α.** Bogata, z PRAWDZIWĄ strukturą folderów (`Archiwum_Komendanta/`, `Pliki_v3.1/`, `DOK_TECH/`). |
| **v3.3** | 05-28 | **19** | **🔴 WIELKI RESET.** Odcięto 20 plików imperialnych, dodano lean code-first (STRAT-001, CORE-006 Brama, ARCHITEKTURA, Zasady v3/v4). |
| v3.4–v3.9 | 05-29/30 | 24→30 | Zdrowa rozbudowa: DATA-001, LOG-001, VIZ-001, SPIS, **PLAN_ORGANIZMU**, dane CSV, brudnopis. |
| **v4.0** | 05-30 | 33 | **🟠 MIGRACJA do Claude Code.** Dodano `CLAUDE.md`, NEURON-001, brudnopis-delty v1.3–v1.11. Zgubiono 3 moduły + ZBADANE. |
| v4.1–v4.2 | 05-30 | 39→46 | Tylko przyrost delt brudnopisu (v1.12–v1.24). Czysto. |

---

## 🔴 STRATA 1 — Reset v3.2 → v3.3 (zniknęło 20 plików)

### Balast słusznie odcięty (zgodne z „przeładowany = wzorzec porażki", v1.3)
- `Kingdom_Pixel_v1/v2_0/dodatek1` (~112 KB manifestów „carskiej Rosji", setki modułów)
- `CLAW_OF_REDEMPTION` (39 KB), `Raport_Audytu…docx` (34 KB), część raportów-flawor.

### ⚠️ Realne złoto stracone niechcący
- **`Router_strategii_raport.md` (16 KB)** — krytyka selektora `win_rate`: asymetria zysk/strata, błąd małej próby, **regime drift**. To gotowy anti-overfit insight — **nie ma go nigdzie w obecnych plikach.**
- **`nasze_orginalne_pomysly` (×2, ~41 KB)** — oryginalny kod koncepcyjny (NexusCore self-healing hub itd.). Częściowo odtworzone w brudnopisie v1.3 „HISTORIA", ale **kod przepadł.**
- **`Tytan_Alpha.md` (33 KB)** — poliglot-orkiestrator + **zweryfikowane linki** (m.in. arXiv 2605.12532, który w v1.20 oznaczyłem „za nowy by zweryfikować" — a tu był źródłowy trop!).

### 📚 Filary dokumentacji, które Zasady WCIĄŻ uważają za obowiązkowe (łączy się z F3 z audytu spójności!)
- **`KSIEGA_IMPERIUM_v3.0` (19 KB)** — „konstytucja" (18 dywizji, 8 botów). Wymagana w Z7/9/10.
- **`MASTER_BAZA_WIEDZY_v3.1` (12 KB)** — kompendium zsync. z ZBADANE.
- **`BAZA_SESJI_v3.1`** — plik startowy wymagany w Z6/9.
- → To nie tylko „martwe prawo" — to **pliki, które reguły mandują, a których nie ma.**

### 🗂️ Struktura folderów
v3.2 miała uporządkowane podfoldery. Od v3.3 wszystko **spłaszczone do jednego katalogu.** To jest ten „zgubiony schemat folderów Królestwa" z brudnopisu.

---

## 🟠 STRATA 2 — Migracja v3.9 → v4.0

- **3 moduły kodu zniknęły:** `CORE-005_NexGenHub` (6 KB), `HANDS-204_WarLancer` (3,6 KB), `ORCH-209_TitanMind` (4,6 KB).
  - ⚠️ **Wszystkie trzy są w tabeli 16 modułów w `SPIS_KROLESTWA`** → SPIS zawyża o 3. Realnie w v4.2 jest **13 z tych 16** modułów + NEURON-001. To bezpośrednie źródło flagi **F5** (przerost obsady).
- **`ZBADANE_v3_1.md` (73 KB, 330 wpisów rejestru)** — ostatecznie wypadł. Uwaga: MASTER_BAZA podawał, że tylko ~14% z tych 330 miało lokalne kopie → reszta to były same linki, w większości i tak do ponownej weryfikacji (Z77).
- Dane CSV (BTC/ETH) — wypadły, ale **odtwarzalne z CCXT** (mały problem).
- `ZASADY_v3`, `POMYSLY_LUZNE` (pojedynczy) → słusznie zastąpione (v4 / system delt).

---

## ✅ CO ODZYSKAĆ TERAZ (rekomendacja wg Z76 — tylko realna rola, nie balast)

1. **3 moduły .py** (CORE-005, HANDS-204, ORCH-209) — albo przywrócić (są w PLAN: Rdzeń, Ręce, Dyrygent), albo skreślić ze SPIS. **Usunąć rozjazd 16 vs 13.** Priorytet.
2. **Krytyka `Router_strategii`** — wciągnąć do brudnopisu jako delta (asymetria P/L, sample bias, regime drift). Realny anti-overfit, pasuje do rygoru.
3. **Struktura folderów v3.2** — baza pod schemat Królestwa (spina się z taksonomią IMV z v1.5).
4. **`ZBADANE` (330 wpisów)** — przejrzeć pod kątem gemów, których link-diving nie złapał; ostrożnie (Z77, większość niezweryfikowana).
5. **Oryginalny kod** (NexusCore, Tytan-α) — zarchiwizować na stałe (Z31 Arsenał Weteranów / Z61 Suwerenność), nawet jeśli nieużywany.

---

## 📌 WNIOSEK METODYCZNY

Stracie nie zapobiegł brak jednej rzeczy: **kontrolowanego logu migracji.** Dlatego od teraz: każda większa zmiana wersji = krótka adnotacja „co wchodzi / co schodzi / dlaczego". W Claude Code załatwi to **git** (nic nie ginie, wszystko cofalne) — to domyka problem „wiemy coraz mniej z każdym backupem".

---
*PRAWDA. Nic nie ma ginąć. Mniej, ale prawdziwie.*
— Jack, Główny Projektant Królestwa Pixel
