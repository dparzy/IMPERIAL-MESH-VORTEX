# 📂 PROTOKÓŁ ARCHIWUM KRÓLESTWA PIXEL — v2

> **Wersja:** v2 (poprawiona po audycie Trybunału Cara) | **Data:** 24 maja 2026 | **Autor:** Jack
>
> **⚠️ KOREKTA KRYTYCZNA:** Poprzednia wersja tego pliku (v1) zawierała fałszywe stwierdzenie, że nowsze kamienie milowe zawierają wszystko z poprzednich — w rzeczywistości pliki v1.5–v2.2 zawierały placeholdery odsyłające do wcześniejszych wersji. Komendant, który zaufał tej radzie i usunął wersje pośrednie, ryzykował utratą danych. Niniejsza wersja v2 wycofuje to zalecenie i wprowadza twardą zasadę zachowania pełnego archiwum.

---

Komendancie Pixel, melduję poprawiony Protokół Archiwum. Pliki w jednym folderze bez struktury to jak książki rzucone na stos. Trzeba je uporządkować, ale **nigdy nie usuwać**.

---

## 📂 Struktura Archiwum (wszystkie wersje zachowane)

```
C:\Kingdom Pixel\Archiwum\
│
├── Raport_Audytu_Trybunalu_Cara_2026-05-24.docx   # Raport pierwszego audytu zewnętrznego
│
├── Pliki_v3.0\                                     # Wersja konsolidacyjna (nowy punkt startowy)
│   ├── ZASADY_FUNDAMENTALNE_v2.md (75 zasad, naprawione)
│   ├── KSIEGA_IMPERIUM_v3.0.md
│   ├── MASTER_BAZA_WIEDZY_v3.0.md
│   ├── ZBADANE_v3.0.md (322 wpisy, bez placeholderów)
│   └── BAZA_SESJI_v3.0.md
│
├── Archiwum_Historyczne\                           # Pełen łańcuch wersji v1.0 → v2.2
│   ├── Milestone_v1.0\
│   │   ├── KSIEGA_IMPERIUM_v1.0.md
│   │   ├── MASTER_BAZA_WIEDZY_v1.0.md
│   │   └── ZBADANE_v1.0.md
│   ├── Milestone_v1.1\
│   │   ├── KSIEGA_IMPERIUM_v1.1.md
│   │   ├── MASTER_BAZA_WIEDZY_v1.1.md
│   │   └── ZBADANE_v1.1.md
│   ├── Milestone_v1.2\
│   ├── Milestone_v1.3\
│   ├── Milestone_v1.4\
│   ├── Milestone_v1.5\
│   ├── Milestone_v1.6\
│   ├── Milestone_v1.7\
│   ├── Milestone_v1.8\
│   ├── Milestone_v1.9\
│   ├── Milestone_v2.0\
│   ├── Milestone_v2.1\
│   └── Milestone_v2.2\
│
└── DOKUMENTACJA_TECHNICZNA\                        # Pliki kodu modułów
    ├── 201_NexGenHub.py
    ├── 202_MetaCortex.py
    └── ... (więcej w miarę realizacji Fazy 2)
```

---

## 🛡️ ŻELAZNA ZASADA ARCHIWUM (Zasada 3 + Zasada 23 — Data Lineage)

| Co | Status | Powód |
|:---|:---|:---|
| **Wersje v1.0 – v2.2** | **ZACHOWAĆ WSZYSTKIE** | Pliki v1.3–v2.2 zawierają placeholdery — pełna treść jest rozproszona w łańcuchu wersji. Usunięcie jednej = bezpowrotna utrata części katalogu. |
| **Pliki v3.0** (po konsolidacji) | **Główny folder roboczy** | Punkt startowy dla bieżącej pracy. Kompletne, bez placeholderów. |
| **Czat źródłowy** (Stan_Królestwa_i_rozkazy_cara…md, 45 553 linie) | **ZACHOWAĆ NA TRWAŁE** | Jedyne źródło danych dla wpisów #299–#310 oraz wielu decyzji historycznych. |
| **Raport audytu Trybunału Cara** | **ZACHOWAĆ WIECZNIE** | Pierwszy dokument audytu zewnętrznego — fundament Zasady 33. |

---

## ⛔ CO BYŁO BŁĘDEM W POPRZEDNIEJ WERSJI

Wersja v1 tego pliku zawierała trzy stwierdzenia, które były **nieprawdziwe** i prowadziły do ryzyka utraty danych:

1. *„Każdy nowszy kamień milowy zawiera wszystko, co było w poprzednich"* — **fałsz**. Pliki v1.3+ zawierają placeholdery typu *„Wpisy #11–#200 zachowane w całości — pełna lista w ZBADANE.md v1.2"*. Nie zawierają fizycznie tych wpisów.

2. *„v1.5 zawiera wszystko z v1.1–v1.4"* — **fałsz**. ZBADANE_v1.5 ma fizycznie 2 wiersze tabeli z deklarowanych 247.

3. *„Wersje pośrednie możesz usunąć (…) nie są niezbędne do pracy"* — **niebezpieczna rada**. Usunięcie którejkolwiek wersji v1.1–v2.1 skutkuje utratą części katalogu ZBADANE i części modułów Imperial Guard.

---

## 🛠️ Komendy CMD do uporządkowania Archiwum (poprawione)

```cmd
cd "C:\Kingdom Pixel\Archiwum"

:: Utwórz strukturę archiwum historycznego (wszystkie wersje zachowane)
mkdir "Archiwum_Historyczne"
mkdir "Archiwum_Historyczne\Milestone_v1.0"
mkdir "Archiwum_Historyczne\Milestone_v1.1"
mkdir "Archiwum_Historyczne\Milestone_v1.2"
mkdir "Archiwum_Historyczne\Milestone_v1.3"
mkdir "Archiwum_Historyczne\Milestone_v1.4"
mkdir "Archiwum_Historyczne\Milestone_v1.5"
mkdir "Archiwum_Historyczne\Milestone_v1.6"
mkdir "Archiwum_Historyczne\Milestone_v1.7"
mkdir "Archiwum_Historyczne\Milestone_v1.8"
mkdir "Archiwum_Historyczne\Milestone_v1.9"
mkdir "Archiwum_Historyczne\Milestone_v2.0"
mkdir "Archiwum_Historyczne\Milestone_v2.1"
mkdir "Archiwum_Historyczne\Milestone_v2.2"

:: Główny folder roboczy dla wersji v3.0
mkdir "..\Pliki_v3.0"
mkdir "..\DOKUMENTACJA_TECHNICZNA"

:: UWAGA: Nie uruchamiaj komend "del" ani "rmdir" na wersjach pośrednich.
:: Wszystkie wersje od v1.0 do v2.2 muszą zostać zachowane jako dowód genezy
:: i źródło rekonstrukcji do czasu zakończenia Fazy 2 planu naprawczego.
```

---

## 📋 CHANGELOG (Zasada 49 pkt 2)

| Wersja | Data | Zmiany |
|:---|:---|:---|
| **v2** | 2026-05-24 | **Korekta po audycie.** Usunięte fałszywe stwierdzenia o samowystarczalności kamieni milowych. Wprowadzona twarda zasada zachowania wszystkich wersji v1.0–v2.2. Dodana sekcja „Co było błędem w poprzedniej wersji". Komendy CMD wzbogacone o wszystkie 13 wersji archiwum + ostrzeżenie przed `del`/`rmdir`. |
| **v1** | wcześniejsza data | **Stan wyjściowy.** Zawierał trzy nieprawdziwe stwierdzenia o tym, że nowsze wersje zawierają pełną treść starszych. Sugerował usuwanie wersji pośrednich, co groziło utratą danych. |

---

*Autor: Jack — Wizjoner, Architekt, Wynalazca, Magik. Kingdom Pixel.*
*Korekta v2 zgodna z Raportem Audytu Trybunału Cara z 24 maja 2026 (sekcja 5.1 Faza 1, Krok 1.5).*
