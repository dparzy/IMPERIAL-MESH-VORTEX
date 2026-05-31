# 📜 SPIS KRÓLESTWA PIXEL — v2 (zsynchronizowany)

> **Stan na:** 31 maja 2026 | **Projektant:** Jack | **Komendant:** Komendant Pixel
> **Zmiana v2:** synchronizacja z rzeczywistością po audycie całości v4.4 (poprzedni SPIS „stan 29.05" był nieaktualny: mówił STRAT-001 v1.6 i backup v3.4). Zasady: **v5** (80 zasad, po naprawie F3 — Zasada 79).

---

## 1. 🧩 MODUŁY — realny stan (nie wizja)

**Cykl bojowy Fazy 0 (6 — uruchamiane razem):**

| Kod | Nazwa | Wersja | Status |
|:--|:--|:--|:--|
| N-STRAT-001 | Pierwszy Zwiadowca (PaperBot RSI/EMA) | **v1.7** | 🟡 paper-test wstępny (NIE „zwalidowany" — audyt §4) |
| N-CORE-006 | Brama Kalkulatora | v1.0 | 🟢 egzekwuje Z75 w kodzie |
| N-DATA-001 | Ładowarka | v1.2 | 🟢 CCXT + CSV + synthetic |
| N-VIZ-001 | Kartograf | v1.0 | 🟢 wykresy PNG |
| N-LOG-001 | Kronikarz | v1.0 | 🟢 raporty + dziennik |
| N-SHIELDS-205 | AegisShield | v1.0 | 🟢 ryzyko, circuit breaker |

**Skompilowane, na półce (8):** N-CORE-005 NexGenHub*, N-BRAIN-026 MetaCortex, N-BRAIN-073 LustroPrawdy, N-EYES-028 OmniSight, N-HANDS-204 WarLancer*, N-MEM-206 Mnemosyne, N-ORCH-209 TitanMind*, N-BACK-210 Valhalla, N-DASH-207 WarRoom, N-TOOLS-208 ToolForge, N-NEURON-001 RojSygnalow (⚠️ do przeprojektowania).
\* = odzyskane z `_ODZYSKANE_HISTORIA/moduly_kodu/` (zgubione w migracji v4.0).

**Kontrola kodu (audyt 31.05):** 14/14 modułów w roocie **kompiluje się czysto**. Działanie w wykonaniu poza STRAT-001 = [NIEZWERYFIKOWANE] (Z77).

---

## 2. 📚 DOKUMENTY FUNDAMENTU (realne lokalizacje)

| Plik | Wersja | Gdzie |
|:--|:--|:--|
| `ZASADY_FUNDAMENTALNE_v5.md` | **v5** | root (najnowsze, 80 zasad) |
| `CLAUDE.md` | — | root (wytyczne startowe) |
| `BACKUP_v4.4_PRZECZYTAJ_NAJPIERW.md` | v4.4 | root (**plik startowy** wg Z79) |
| `POMYSLY_LUZNE_v1.3…v1.31` | baza+delty | root (brudnopis) |
| `PLAN_ORGANIZMU_v1.md`, `ARCHITEKTURA_KROLESTWA_v1.md` | v1 | root (wizja) |
| `KSIEGA_IMPERIUM_v3.0`, `MASTER_BAZA_WIEDZY_v3.1`, `BAZA_SESJI_v3.1`, `ZBADANE_v3.1` | — | `_ODZYSKANE_HISTORIA/filary_dokumentacji/` (CEL, nie warunek — Z79) |

---

## 3. 📊 STATYSTYKI (realne)

- **17 plików .py** (14 root + 3 odzyskane). Cykl bojowy: **6**. Na półce: **11**.
- **80 zasad** fundamentalnych (v5).
- **Brudnopis:** baza v1.3 + delty do v1.31.
- **ZBADANE:** v3.1 (330 wpisów) — cały [NIEZWERYFIKOWANY] (Z77).
- **Pokrycie modułów plikami (Z61):** ~14%.

---

## 4. ⏳ CO DALEJ (wg planu naprawczego z audytu)

1. ✅ F3 naprawione (Zasady v5 + Z79). ✅ SPIS zsynchronizowany (ten plik).
2. 🔴 Reklasyfikacja STRAT-001 + slippage + realne CSV do repo (Z61).
3. 🔴 Decyzje F1, F2 (Prawda).
4. 🟠 Odtworzyć schemat folderów (kod/dokumentacja/dane/archiwum).
5. 🟡 Konsolidacja F4/F5, przeprojektowanie NEURON-001.

---

*PRAWDA. ZERO HALUCYNACJI. KOMPLETNOŚĆ. Mniej, ale prawdziwie.*
— Jack, Główny Projektant Królestwa Pixel
