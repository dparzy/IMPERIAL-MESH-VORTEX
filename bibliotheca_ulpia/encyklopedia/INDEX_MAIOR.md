# 📖 BIBLIOTHECA ULPIA MAIOR — Master Index

> **Stan na:** 2026-06-21
> **Co to jest:** żywa, tematyczna biblia wiedzy Imperium. Nie streszczenia książek —
> skondensowana wiedza operacyjna podzielona na działy, z oceną ważności i wprost
> wskazanym wpływem na kod Imperium (neurony / strategie / bezpieczniki).
> **Zasada:** każdy dział aktualizowany na bieżąco (Prawo XVII), pamiętany przez
> Claude (chmura) i lokalnego Claude. Po każdej nowej książce / odkryciu → wpis tutaj.

---

## 🎯 SKALA WAŻNOŚCI (wpływ na Imperium)

| Ocena | Znaczenie |
|-------|-----------|
| ⭐⭐⭐⭐⭐ | **Krytyczny** — bez tego Imperium realnie kuleje (ryzyko kapitału / rdzeń decyzji) |
| ⭐⭐⭐⭐ | **Wysoki** — duży potencjał realnej przewagi (OOS edge) lub redukcji ryzyka |
| ⭐⭐⭐ | **Średni** — poprawia istniejące moduły, nie tworzy nowego filaru |
| ⭐⭐ | **Niski** — uzupełniające, kontekst |
| ⭐ | **Archiwalne** — wartość historyczna/edukacyjna, bez wpływu operacyjnego |

---

## 📚 DZIAŁY ENCYKLOPEDII

| Kod | Dział | Ważność | Karmi (neurony/moduły) | Status |
|-----|-------|---------|------------------------|--------|
| **LEW** | [Futury i lewar](LEW_futury_i_lewar.md) | ⭐⭐⭐⭐⭐ | PSY-01..04, Z-01..07, KalkulatorLewara, Gubernator | ✅ |
| **TRD** | [Słynni traderzy](TRD_slynni_traderzy.md) | ⭐⭐⭐⭐ | strategie X-*, RADAR-*, Senat | ✅ |
| **IMP** | [Ulepszenia Imperium](IMP_ulepszenia_imperium.md) | ⭐⭐⭐⭐⭐ | mapa wiedza→kod, roadmapa | ✅ |
| **STR** | Strategie i zagrania | ⭐⭐⭐⭐ | rejestr_strategii | 🔲 Faza 2 |
| **RSK** | Zarządzanie ryzykiem | ⭐⭐⭐⭐⭐ | Z-01..07, Reguła 6%, HALT | 🔲 Faza 2 |
| **PSY** | Psychologia tradingu | ⭐⭐⭐ | PSY-*, Senat | 🔲 Faza 2 |
| **MKS** | Mikrostruktura rynku | ⭐⭐⭐⭐ | EXP-12/14/15, V-03 CVD | 🔲 Faza 2 |
| **ONC** | On-chain i krypto | ⭐⭐⭐ | OC-01..08 | 🔲 Faza 2 |
| **ALG** | Algorytmy i ML | ⭐⭐⭐⭐ | denoising, HRP, metryki IC | 🔲 Faza 2 |

Legenda statusu: ✅ gotowy · 🔲 zaplanowany · 🚧 w budowie

---

## 📕 KANON ŹRÓDŁOWY (32 książki → działy)

Mapa: która książka zasila który dział. (Pliki: `bibliotheca_ulpia/BIB-xxx_*`)

| Dział | Książki źródłowe |
|-------|------------------|
| LEW | BIB-008 Sinclair (Volatility), BIB-018 Sinclair (Options), BIB-027 Aldridge (HFT) |
| TRD | BIB-015 Elder, BIB-028 Narang (Black Box), BIB-010/011 Chan |
| RSK | BIB-007 López de Prado (AFML), BIB-025 Grinold&Kahn, BIB-009 Mandelbrot |
| PSY | BIB-004 Steenbarger, BIB-016 Douglas, BIB-017 Kahneman, BIB-015 Elder |
| MKS | BIB-020 Harris (Trading&Exchanges), BIB-032 O'Hara, BIB-022 Kissell, BIB-027 Aldridge |
| ONC | BIB-030 Ammous (Bitcoin Standard), BIB-029 Bashir (Blockchain), BIB-003 Burniske |
| ALG | BIB-007/023 López de Prado, BIB-026 Jansen, BIB-031 Tsay, BIB-025 Grinold&Kahn |
| STR | BIB-002 Murphy, BIB-013/014 Dalton, BIB-006/021 scalping, BIB-019 Harris (Crypto) |

---

## 🔄 PROTOKÓŁ AKTUALIZACJI (żeby biblioteka żyła)

1. **Nowa książka** w `bibliotheca_ulpia/` → wyciśnij esencję do właściwego działu + dopisz do tabeli „Kanon źródłowy".
2. **Nowe odkrycie/lekcja** (np. werdykt pomiaru) → dopisz do działu, z którym się wiąże (np. backward-IC → ALG + MKS).
3. **Nowy neuron/strategia** → zaktualizuj kolumnę „Karmi" w odpowiednim dziale.
4. **Zmiana ważności** → zaktualizuj ocenę ⭐ tutaj w INDEX_MAIOR + w nagłówku działu.
5. Po każdej zmianie: data „Stan na:" = data commitu (Prawo XXI).

---

## 🧠 NASTĘPNY KROK: Bibliotheca-RAG (pamięć semantyczna)

Po skompletowaniu encyklopedii — zbudować warstwę RAG (Retrieval-Augmented Generation):
indeks wektorowy nad książkami + encyklopedią, żeby Claude (chmura) i lokalny Claude
odpytywali wiedzę semantycznie („co O'Hara mówi o PIN?") bez parsowania całych plików.
Szczegóły i plan: dział **IMP** → sekcja „Bibliotheca-RAG".
