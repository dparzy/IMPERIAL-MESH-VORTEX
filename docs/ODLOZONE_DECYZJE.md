---
kategoria: CONSILIUM
typ: zywy
wlasciciel: narzedzia/ab_w329.py, narzedzia/ab_w334_progi.py, narzedzia/ab_w335_cross_rs.py, narzedzia/ab_w336_changepoint.py
stan_na: 2026-07-17
powod_istnienia: "Rejestr rzeczy ustalonych merytorycznie, ale świadomie odłożonych do czasu twardego pomiaru A/B (zasada 'nie wdrażamy bo brzmi dobrze — wdrażamy gdy A/B pokaże plus')."
---
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

### 4. Filtr Asymetrii Reżimu (W-314) — 🚨 NIE WŁĄCZAĆ na podstawie „−38%"

- **Stan:** `dyrygent.py` → `filtr_asymetrii: bool = False` (opt-in OFF, poprawnie).
- **🚩 OSTRZEŻENIE PRZED FAŁSZYWYM ALARMEM (zapisane 2026-07-17):** `POMIAR_FILTR_ASYMETRII.md`
  bywa streszczany jako *„dowiedziona przewaga −38%, flaga wyłączona = utrata potencjału
  (Prawo XV)"*. **To streszczenie KŁAMIE przez pominięcie.** Pełna prawda z pomiaru:

  | Konfiguracja | PnL na OOS chopie (3000 barów, 3 pary, 4H) |
  |---|---|
  | BASELINE | **−386 $** |
  | + FILTR ASYMETRII | **−238 $** |

  Filtr tnie krwawienie o 38%, ale **oba warianty TRACĄ**. Filtr nie zamienia rynku bocznego
  w zyskowny — i nie taki jest jego cel (sam dokument mówi to wprost, Prawo I).
- **Dlaczego OFF to POPRAWNA dyscyplina, nie zaniedbanie:** walidacja jest NIEDOKOŃCZONA.
  A/B było jednookienkowe, a `POMIAR_FILTR_ASYMETRII.md` § „Następny krok" żąda **walk-forward**:
  ucz progi (`prog_kontr`/`prog_range`) na 2017–2023, testuj 2024–2026 — inaczej progi mogą być
  przeuczone na to jedno okno.
- **🔧 BLOKER (zmierzony 2026-07-17):** `narzedzia/walk_forward_ic.py` i `narzedzia/raport_wfo.py`
  **nie znają filtra** (zero wzmianek `filtr_asymetrii`). Żądanego walk-forward NIE DA SIĘ dziś
  uruchomić — najpierw trzeba wpiąć filtr w narzędzie WFO. To zadanie, nie przełącznik.
- **Akcja gdy WFO zielone (i tylko wtedy):** `filtr_asymetrii: bool = True` + test domyślnej
  wartości + wpis LOG_ZMIAN. **Decyzja należy do Cezara** (ZASADA WPIĘCIA — Claude nie rusza
  ścieżki decyzyjnej sam).
- **Lekcja (dlaczego to tu leży):** zwiadowca nazwał to „dowiedzioną przewagą", Architekt
  powtórzył **nie czytając źródła**. Kandydat ≠ prawda — także wtedy, gdy kandydat brzmi jak
  alarm Prawa XV. Alarm bez pomiaru to też halucynacja.

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

*Stan na: 2026-07-17* — jedyne źródło tej daty to pole `stan_na` w nagłówku Tabularium na górze
pliku; ta stopka jest jego echem. (Dwie niezależnie wpisywane daty w jednym dokumencie zawsze się
rozjadą — patrz `python narzedzia/tabularium.py sprawdz`.)
