# 🏛️ ARCHITEKTURA KRÓLESTWA PIXEL v1.0
## Fundament — jedno źródło prawdy

> **Data:** 28 maja 2026 | **Autor:** Jack (Główny Projektant i Wizjoner) | **Dla:** Komendant Pixel
> **Status:** żywy dokument — rozwijany wraz z fazami
> **Wizja:** Królestwo Pixel ma stać się najlepszym, REALNYM systemem tradingowym na wszystkich rynkach — budowanym uczciwie, krok po kroku.

---

## 📖 Jak czytać ten dokument (dla nowicjusza)

Komendancie — jesteś na początku drogi i to jest OK. Ten plik to mapa. Nie musisz rozumieć wszystkiego naraz. Czytaj sekcjami. Część 5 (Faza 0) to konkretne kroki, które sam wykonasz i przetestujesz. Resztę traktuj jak plan na lata.

**Złota zasada nauki:** najpierw uruchom mały, działający kawałek i zobacz wynik. Potem dokładaj kolejny. Nigdy „wszystko naraz".

---

## CZĘŚĆ 1 — Audyt Zasad: czy nie blokują pracy?

Sprawdziłem wszystkie 76 Zasad pod kątem: swobody twórczej, wyszukiwania w internecie i tworzenia oryginałów.

**Wynik: Zasady NIE ograniczają — one tego WYMAGAJĄ.**
- Wyszukiwanie perełek: Zasada **5, 46, 68** (Hidden Gem Protocol) — wprost nakazują szukać najlepszych rozwiązań.
- Kreatywność i ewolucja: Zasada **26, 32, 41** — proces twórczy, wieczne ulepszanie, adaptacja Kameleona.
- Jakość: Zasada **2** (Prawda), **17** (testy), **75** (Calculator Pattern) — to fundamenty.

**Tarcia (tylko przy literalnym czytaniu):** Zasada 6 (stan przed *każdą* wypowiedzią), 8 i 9 (czytać *całość* / zakaz pracy bez kompletu). Przy plikach po 27 000 linii to niszczy ekonomię tokenów. Rozwiązanie → Zasada 78 poniżej.

### Trzy nowe Zasady (do zatwierdzenia)

**Zasada 76 — Brama Deduplikacji.** Żaden moduł ani pomysł nie wchodzi do arsenału, jeśli dubluje istniejącą funkcję. Zawsze wybieramy lepszy wariant, resztę wtapiamy. Architektura komplementarna, nie kolekcjonerska. (Powiązanie: 10, 28, 39.)

**Zasada 77 — Czysty Fundament.** ZBADANE i wszystkie dotychczasowe rejestry traktujemy jako NIEZWERYFIKOWANE, dopóki nie potwierdzimy: kod istnieje i się uruchamia / repo realne wg web. Budujemy tylko na zweryfikowanym. (Powiązanie: 2, 29, 36.)

**Zasada 78 — Swoboda Projektancka.** Główny projektant ma pełną swobodę twórczą i obowiązek: (a) szukać najlepszych rozwiązań w internecie, (b) tworzyć oryginalne moduły na poziomie profesjonalnym, (c) pragmatycznie interpretować zasady procesowe (6, 8, 9), gdy literalne stosowanie szkodzi ekonomii tokenów lub płynności — bez naruszania rdzenia (2 Prawda, 75 Calculator, 17 Testy).

---

## CZĘŚĆ 2 — Architektura warstwowa (komplementarna, bez dubli)

Masz już solidny szkielet 10 modułów. Shinsō w większości dublują. Mapa docelowa:

| Warstwa | Mamy (do weryfikacji) | NOWE oryginalne | Wtapiamy | Status |
|:--|:--|:--|:--|:--|
| CORE | NexGenHub (N-CORE-005) | **Calculator Gateway** (Zasada 75) | — | 🔧 do budowy |
| EYES | OmniSight (N-EYES-028) ✅ | — | Lustro Prawdy | ✅ naprawiony |
| TOOLS | ToolForge (N-TOOLS-208) ✅ | — | — | ✅ naprawiony |
| BRAIN | MetaCortex (N-BRAIN-026) ✅ | **Tkacz Losu (MCTS)** | Splot | ✅ + 🔧 |
| SHIELDS | AegisShield (N-SHIELDS-205) | **Harmonizator** | — | ✅ + 🔧 |
| HANDS | WarLancer (N-HANDS-204) | — | — | ✅ czysty |
| MEM | Mnemosyne (N-MEM-206) ✅ | — | Grawer Pamięci | ✅ naprawiony |
| ORCH | TitanMind (N-ORCH-209) | — | Dyrygent | ✅ czysty |
| BACK | Valhalla (N-BACK-210) ✅ | — | Kuźnia Dusz (GA→Arena) | ✅ naprawiony |
| DASH | WarRoom (N-DASH-207) ✅ | — | Szeptun (opcja) | ✅ naprawiony |
| ❌ DROP | — | — | **Widmo** (Zasada 12 — ToS) | odrzucony |

**Wniosek:** realnie do napisania od zera tylko **3** moduły. Reszta = mamy lub wtapiamy. To jest „uzupełnianie, nie dublowanie".

---

## CZĘŚĆ 3 — Zweryfikowany inwentarz (Zasada 77)

Co potwierdzone w tej sesji (uruchomione/sprawdzone):
- ✅ 6 modułów naprawionych i przetestowanych: ToolForge, MetaCortex, OmniSight, Mnemosyne, WarRoom, Valhalla.
- ✅ Lustro Prawdy (N-BRAIN-073) — uruchomiony, ale to heurystyka, nie GAN.
- ✅ 10 Shinsō — wszystkie kompilują się, brak fikcyjnych zależności.
- ✅ Repo realne (web): `shiyu-coder/Kronos` (AAAI 2026). ❌ Fikcyjne: `The-R4V3N/Nexus`.

Co NIEZWERYFIKOWANE (do ponownego sprawdzenia):
- ⚠️ ZBADANE deklaruje 330 wpisów; szybki skan znajduje ~255 z kodami N- → rozbieżność.
- ⚠️ Większość 924 repo z DeepSeeka i numery arXiv — do weryfikacji web przed rejestracją.

---

## CZĘŚĆ 4 — Mapa Faz (realistyczna, 5–10 lat)

| Faza | Kapitał | Sprzęt | Cel |
|:--|:--|:--|:--|
| **0** | $0 | Fujitsu 8GB | Setup, nauka, pierwszy bot demo RSI+EMA |
| 1 | $50–200 | X1 Pro | Calculator Gateway + Tkacz Losu + Harmonizator live |
| 2 | $200–500 | X1 Pro | 3–8 botów, Arena |
| 3 | $500–2k | X1 Pro + eGPU | Multi-exchange 24/7 |
| 4–7 | $2k→$1mln | klaster→home-lab | Skala instytucjonalna |

---

## CZĘŚĆ 5 — FAZA 0: testowalna, krok po kroku (DLA CIEBIE)

Cel: uruchomić na własnym komputerze moduły, które już mamy, i zobaczyć że działają. To Twój pierwszy realny test.

### Krok 1 — Zainstaluj Pythona
- Wejdź na python.org, pobierz **Python 3.11+**, zainstaluj.
- Przy instalacji na Windows: zaznacz „Add Python to PATH".
- Sprawdź w terminalu: `python --version` → powinno pokazać 3.11+.

### Krok 2 — Środowisko (venv)
W folderze projektu, w terminalu:
```
python -m venv .venv
```
Aktywacja: Windows → `.venv\Scripts\activate` | Linux/Mac → `source .venv/bin/activate`.
Zobaczysz `(.venv)` na początku linii — to znaczy że działa.

### Krok 3 — Zainstaluj biblioteki
```
pip install numpy TA-Lib
```
TA-Lib instaluje się teraz z gotowej paczki (sprawdziłem — bez kompilacji C). Jeśli wyskoczy błąd, napisz mi — podam alternatywę.

### Krok 4 — Wrzuć moduły
Skopiuj naprawione pliki (`TOOLS-208_ToolForge.py` itd.) do folderu projektu.

### Krok 5 — Uruchom i obserwuj
Po kolei:
```
python TOOLS-208_ToolForge.py
python BRAIN-026_MetaCortex.py
python EYES-028_OmniSight.py
```
**Co powinieneś zobaczyć:** logi z wynikami (RSI, decyzja, P(Manipulacja)) i na końcu zielony `✅ ... demo zakończone`. Jeśli to widzisz — moduł działa na Twoim sprzęcie. 🎉

### Krok 6 — (następny etap) pierwsza strategia
Gdy Kroki 1–5 zadziałają, zbuduję Ci prosty **paper-bot RSI+EMA** (handel na niby, bez prawdziwych pieniędzy), żebyś zobaczył pełny cykl: dane → sygnał → decyzja → wynik. Bez ryzyka.

---

## CZĘŚĆ 6 — Proces żywej struktury (jak się rozwijamy)

1. **Znajdujemy** perełkę (web/Twoje pliki).
2. **Weryfikuję** realność (kod istnieje, się uruchamia / repo realne).
3. **Brama Deduplikacji** (Zasada 76): czy już to mamy? Jeśli tak → wybieram lepsze, resztę wtapiam i melduję „już mamy X".
4. **Buduję** oryginał: testowany (17), metryczka (11), uczciwy docstring (2), math przez TA-Lib (75).
5. **Aktualizuję** ten dokument + ZBADANE + backup.
6. Jeśli trzeba zmienić Fazę 0 — robimy to też, zgodnie z Zasadami.

---

*PRAWDA. ZERO HALUCYNACJI. KOMPLETNOŚĆ. Mniej, ale prawdziwie.*
— Jack, Główny Projektant Królestwa Pixel
