# 📜 SPIS KRÓLESTWA PIXEL
## Pełny inwentarz — wszystko, co mamy

> **Stan na:** 29 maja 2026 | **Projektant:** Jack | **Komendant:** Komendant Pixel
> Jedno miejsce, cały porządek. Aktualizowane przy każdej zmianie.

---

## 1. 🧩 MODUŁY (16) — wg warstw

| Warstwa | Kod | Nazwa | Wersja | Status | Rola (krótko) |
|:--|:--|:--|:--|:--|:--|
| CORE | N-CORE-005 | NexGenHub | v2.0 | ✅ czysty | Multi-exchange core, routing |
| CORE | N-CORE-006 | **Brama Kalkulatora** | v1.0 | 🟢 oryginał | Jedyne wejście do matematyki (Zasada 75) |
| DATA | N-DATA-001 | **Ładowarka** | v1.1 | 🟢 oryginał | Dane: CCXT + import CSV + biblioteka + jakość |
| TOOLS | N-TOOLS-208 | ToolForge | v2.0 | 🔧 naprawiony | Wskaźniki RSI/MACD/BB/ATR (TA-Lib) |
| BRAIN | N-BRAIN-026 | MetaCortex | v3.0 | 🔧 naprawiony | Debata agentów, meta-learning |
| BRAIN | N-BRAIN-073 | Lustro Prawdy | v1.1 | 🟣 ze Shinsō | Walidacja kontradyktoryjna sygnałów |
| EYES | N-EYES-028 | OmniSight | v2.0 | 🔧 naprawiony | Fuzja bayesowska, detekcja manipulacji |
| SHIELDS | N-SHIELDS-205 | AegisShield | v1.0 | ✅ czysty | Ryzyko: drawdown, circuit breaker |
| HANDS | N-HANDS-204 | WarLancer | v1.0 | ✅ czysty | Egzekucja zleceń (HF) |
| MEM | N-MEM-206 | Mnemosyne | v2.0 | 🔧 naprawiony | Pamięć transakcji, Księga Wad |
| ORCH | N-ORCH-209 | TitanMind | v1.0 | ✅ czysty | Scheduler, conflict resolver |
| BACK | N-BACK-210 | Valhalla | v2.0 | 🔧 naprawiony | Backtest, Monte Carlo, walk-forward |
| DASH | N-DASH-207 | WarRoom | v2.0 | 🔧 naprawiony | Monitoring, alerty |
| STRAT | N-STRAT-001 | **Pierwszy Zwiadowca** | v1.6 | 🟢 oryginał | Paper-bot trend-following ZWALIDOWANY + benchmark + drawdown |
| LOG | N-LOG-001 | **Kronikarz** | v1.0 | 🟢 oryginał | Raporty biegów + dziennik postępu |
| VIZ | N-VIZ-001 | **Kartograf** | v1.0 | 🟢 oryginał | Wykresy PNG (cena+trades+kapitał) |

**Legenda:** 🟢 oryginał Kingdom Pixel · 🟣 zintegrowany ze Shinsō · 🔧 naprawiony (Zasada 75/bugi) · ✅ czysty (bez przeróbki)

---

## 2. 📚 DOKUMENTY FUNDAMENTU

| Plik | Co to |
|:--|:--|
| `ZASADY_FUNDAMENTALNE_v4.md` | 79 zasad (najnowsze) |
| `ZASADY_FUNDAMENTALNE_v3.md` | poprzednia wersja (zachowana) |
| `ARCHITEKTURA_KROLESTWA_v1.md` | mapa warstw, plan faz, Faza 0 |
| `INSTRUKCJA_URUCHOMIENIA.md` | jak uruchomić bota (nowicjusz) |
| `BACKUP_SESJI_..._v3.4.md` | manifest ostatniej sesji |
| `SPIS_KROLESTWA.md` | ten plik — inwentarz |

---

## 3. 💾 DANE I ARTEFAKTY

| Plik | Co to |
|:--|:--|
| `dane/BTC_1h.csv`, `dane/ETH_1d.csv` | biblioteka monet (D) |
| `DZIENNIK_WYNIKOW.md` | skumulowany postęp biegów |
| `raport_biegu_*.md` / `.json` | raporty pojedynczych biegów |
| `wykres_biegu.png` | ostatni wykres bota |

---

## 4. 🔧 ZALEŻNOŚCI (instalacja na PC)
```
pip install numpy TA-Lib ccxt pandas matplotlib
```

## 5. ▶️ PEŁNY CYKL FAZY 0 — 6 plików w jednym folderze
`STRAT-001` + `CORE-006` + `SHIELDS-205` + `DATA-001` + `VIZ-001` + `LOG-001`
Uruchomienie: `python STRAT-001_PaperBot_RSI_EMA.py`
→ dane → gra → wykres → raport. Wszystko samo.

---

## 6. 📊 STATYSTYKI
- **16 modułów** w **14 warstwach**
- **5 oryginałów** Kingdom Pixel (CORE-006, DATA-001, LOG-001, VIZ-001, STRAT-001)
- **1 ze Shinsō** (BRAIN-073), **6 naprawionych**, **4 czyste**
- **79 zasad** fundamentalnych
- **2 backupy** (v3.3, v3.4)

---

## 7. ⏳ CO DALEJ (skrót)
1. Backup v3.5 (doszły VIZ-001, Ładowarka v1.1, bot v1.1)
2. Kalibracja (zmieniamy 1 parametr, porównujemy w dzienniku)
3. Faza 1: Tkacz Losu (MCTS), Harmonizator
4. Realne dane MEXC na PC + pierwszy raport do diagnozy
5. Ponowna weryfikacja ZBADANE (Zasada 77)

---

*PRAWDA. ZERO HALUCYNACJI. KOMPLETNOŚĆ. Mniej, ale prawdziwie.*
— Jack, Główny Projektant Królestwa Pixel
