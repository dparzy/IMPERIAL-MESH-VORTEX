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

### 3. A/B nowych neuronów z deep researchu (W-335/336) — zmierzyć ON vs OFF
- **C-01 Cross-sectional RS** → `python narzedzia/ab_w335_cross_rs.py`
- **CP-01 CUSUM change-point** → `python narzedzia/ab_w336_changepoint.py`
- Kod ma fallback (abstynują bez danych), więc bezpieczne; werdykt „pomaga?" po A/B.
- META-01 (VI/informacja wzajemna) to narzędzie diagnostyczne — uruchom na zebranych
  sygnałach paper-tradingu, by znaleźć ukrytą redundancję w roju 76 neuronów.

---

## 🛠️ KOLEJKA BUDOWY z deep researchu (RESEARCH_NOWE_KATEGORIE_2026-06-17.md)

Decyzja Cezara (2026-06-17): „wszystko po kolei, decyduj sam". Kolejność: reżimowe →
meta B → L2. **Zrobione:** META-01 (VI), C-01 (kat. C), CP-01 (CUSUM, kat. R), B-01+B-02 (W-337).

**Następne (każde: kod+test+A/B, Prawo I/XIX/XXI):**
1. ✅ **B-02 Neutralization** + **B-01 Meta-labeling** — WDROŻONE W-337 (2026-06-18).
   Pliki: `neutralizacja.py`, `meta_labeling.py`. A/B: `narzedzia/ab_w337_meta.py` (do zbudowania).
2. ✅/⏳ **Jump Model / BOCPD** — BOCPD wdrożony (W-338). JumpModel: kierunkowy ZMIERZONY
   jako niespójny (BTC+/ETH−, Prawo I → NIE wpinamy kierunku). Vol-reżim WDROŻONY jako
   brama opt-in (W-340): turbo→VOLATILE, zmierzone 1.22–1.56× |zwrot| t+1 na 4 aktywach.
   **A/B PENDING:** `Legatus.uzyj_vol_regime=True` vs OFF na pełnym P&L (domyślnie OFF).
   Gdy A/B delta>0 → flip domyślnej na ON + test + LOG_ZMIAN.
3. **U (mikrostruktura L2)** + **P (Hawkes)** — wymaga wpięcia feedu order-book depth
   z MEXC (nowy pipeline danych — decyzja o koszcie/feedzie przed startem).
4. **IV (options DVOL z Deribit)** — darmowy feed, forecast realized vol (nie kierunek).

---

## 📌 PROTOKÓŁ
Po dokończeniu A/B: zaktualizuj ten plik (przenieś do „ZAMKNIĘTE" z wynikiem),
wpisz LOG_ZMIAN, zaktualizuj MANIFEST/README jeśli zmienia się zachowanie domyślne.

*Stan na: 2026-06-18*
