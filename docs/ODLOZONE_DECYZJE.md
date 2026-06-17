# 🔖 ODŁOŻONE DECYZJE — czekają na pomiar (Prawo I)

> Rzeczy ustalone, ale **świadomie odłożone** do czasu twardego pomiaru A/B.
> Cezar i Claude wracają tu na początku sesji. Nic tu nie ginie.
> Zasada: nie wdrażamy „bo brzmi dobrze" — wdrażamy gdy A/B pokaże plus (Prawo I).

---

## ⏳ OCZEKUJE NA A/B (lokalnie, wymaga sieci/danych)

### 1. +Igrzyska jako domyślnie ON w `petla_live` ⭐ NAJBLIŻEJ
- **Stan:** A/B W-329 przerwane przez restart kontenera. Wynik częściowy:
  - BASELINE (synapsy) − 0.70%
  - +MWU − 1.47% (szkodzi → potwierdzone OFF)
  - **+Igrzyska + 0.89%** ← obiecujące, ale niepełne (1500 barów)
  - +KsięgaWad − 0.70% (neutralne)
  - brakuje: +Gubernator, WSZYSTKO
- **Decyzja Cezara (2026-06-17):** „czekamy aż dokończymy, później podepniemy".
- **Akcja gdy A/B dokończone i +Igrzyska potwierdzone:**
  w `imperium/koloseum/petla_live.py` → `KonfigPetliLive.igrzyska: bool = True`
  (obecnie domyślnie `False`). Dodać test domyślnej wartości + wpis LOG_ZMIAN.
- **Narzędzie:** `python narzedzia/ab_w329.py`

### 2. Progi adaptacyjne RSI/ADX (W-334) — weryfikacja czy POMAGAJĄ
- **Stan:** kod wdrożony z fallbackiem do progów bazowych (bezpieczny), ale
  werdykt „czy pomaga" należy do A/B — jeszcze niezmierzone.
- **Akcja:** `python narzedzia/ab_w334_progi.py` (adaptacyjne vs sztywne 30/70, 25).
  Jeśli delta ≤ 0 na pełnej historii → rozważyć cofnięcie/strojenie progów.

---

## 📌 PROTOKÓŁ
Po dokończeniu A/B: zaktualizuj ten plik (przenieś do „ZAMKNIĘTE" z wynikiem),
wpisz LOG_ZMIAN, zaktualizuj MANIFEST/README jeśli zmienia się zachowanie domyślne.

*Stan na: 2026-06-17*
