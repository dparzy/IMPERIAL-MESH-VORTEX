---
kategoria: ACTA
typ: acta
wlasciciel: imperium/legiony/strategie/baza.py
stan_na: 2026-07-13
powod_istnienia: "Zwiad wiedzy (Bibliotheca Ulpia RAG 27641 fragmentów + internet) w celu ulepszenia auto-doboru strategii — zdiagnozowana luka: dobór strategii ignoruje zrealizowany P&L (czysto str"
---
# 🎯 ANALIZA: Auto-dobór strategii — zwiad wiedzy (biblioteka + internet)

> **Stan na:** 2026-07-13 · **Typ:** datowany snapshot (Prawo I — prawda swojego czasu, audyt pomija)
> **Zwiad:** Bibliotheca Ulpia (RAG/FTS, 27641 fragmentów) + głęboki skan internetu
> **Cel (Cezar):** ulepszyć auto-dobór strategii → wyższa skuteczność, auto-wygrywanie najlepszym zyskiem
> **Status wszystkich pozycji:** ⚠️ KANDYDAT/HIPOTEZA — prawdą staje się DOPIERO po arenie
> (Prawo I + ZASADA WPIĘCIA: każde wpięcie opt-in OFF → A/B na P&L → decyzja Cezara/Prawo XVIII).

---

## Kontekst — co już mamy (baseline, Prawo XVI: bez redundancji)

| Mechanizm | Plik | Co robi |
|-----------|------|---------|
| Dobór statyczny strategii | `imperium/legiony/strategie/baza.py::dobierz_najlepsze` | score = zgodność_wejść × (0.5+0.5·filtry) × bonus_reżimu(×1.15/×0.85) × bonus_radaru; top-1 do Dyrygenta |
| Reżim→tryb | `imperium/koloseum/namiestnik.py` | per reżim przydziela tryb agregat/filtr/strategia |
| MWU (online weights) | `imperium/biblioteki/hedge_mwu.py` | multiplicative weights (Freund-Schapire) — **na NEURONACH, nie strategiach** |
| RadarRynku | bonus per styl | dynamiczne tło rynkowe |

**Zdiagnozowana luka (rdzeń):** dobór strategii **ignoruje zrealizowany P&L** — jest czysto
strukturalny (zgodność sygnałów), bez pętli sprzężenia zwrotnego od wyników. A/B warstwy
(agregat/filtr/strategia, 2026-07-13) pokazuje, że statyczny routing często SZKODZI vs baseline.

---

## Kandydaci (ranking: wartość × niskie ryzyko przeuczenia × reużycie kodu)

### ① Strategy-level MWU — ważenie 20 strategii świeżym P&L ⭐ WYBRANY KIERUNEK
Każda z 20 strategii = „ekspert"; waga rośnie/maleje po każdym ZAMKNIĘTYM trade tej strategii
(multiplicative weights update). Dobór = score_strukturalny × waga_wynikowa_MWU.
- **Źródła:** `imperium/biblioteki/hedge_mwu.py` (KOD — reużycie na nowym obiekcie);
  NYU Stern „Online Quantitative Trading Strategies" (Aggregation Algorithm, Follow-the-Leading-History,
  Online Gradient Update) https://www.stern.nyu.edu/sites/default/files/2025-05/Glucksman_Lahanis.pdf ;
  Sutton & Barto *RL: An Introduction* 2nd ed (BIB-067).
- **Czemu najlepszy:** wprost „auto-wygrywanie najlepszym zyskiem"; online; mała nowość = małe ryzyko
  przeuczenia; opt-in trywialny; naprawia zdiagnozowaną lukę (brak sprzężenia P&L).
- **Wpięcie:** flaga opt-in OFF → A/B na P&L (infra `ab_pnl_wazenie_ic.py` / `ab_tryb_strategii.py`
  gotowa do adaptacji) → zielony wynik uzasadnia flagę (Prawo XVIII).

### ② Rolling-Sharpe selector (FinRL ensemble, Yang i in.)
Co N barów wybieraj strategię/tryb wg najlepszego Sharpe'a na oknie walidacyjnym.
- **Źródło:** Columbia OpenFin „Deep RL for Automated Stock Trading: An Ensemble Strategy"
  https://arxiv.org/pdf/2511.12120 . Prosty, odporny, „best profit" wprost. Tani wariant porównawczy dla ①.

### ③ Meta-labeling per strategia (López de Prado)
Wtórny model ML decyduje CZY brać sygnał strategii + jaki rozmiar („znasz stronę, mniej pewny rozmiaru").
- **Źródło (biblioteka!):** BIB-007 *Advances in Financial ML* rozdz. 3.6; BIB-023 *ML for Asset Managers* §5.5
  (López de Prado). Mamy fundament B-01 meta_labeling (⚠️ status w kodzie do weryfikacji).

### ④ Contextual bandit — wybór strategii wg kontekstu przewidującego reward
- **Źródło:** MetaPS „Adaptive Programmatic Strategy Selection" https://arxiv.org/html/2606.22385 ;
  CMAB+neuroevolution dla tradingu (GECCO 2024, dl.acm.org/doi/10.1145/3638530.3664145);
  Sutton & Barto (BIB-067, contextual bandits). Mocniejsze, wyższe ryzyko przeuczenia → fala późniejsza.

### ⑤ HMM / Markov regime allocation (Hamilton) — alokacja strategii wg posteriora reżimu
- **Źródło (biblioteka!):** BIB-023 López (Hamilton 1994, EM, macierz przejść); BIB-031 Tsay (MSA, ukryty
  Markov, oczekiwany czas trwania stanu 1/wᵢ); BIB-010 Chan (regime-conditional parameter optimization);
  BIB-027 Aldridge (Markov switching zmienności). Mamy detektory reżimu (CUSUM/BOCPD/vol-gate) —
  NOWE: warunkowanie DOBORU strategii posteriorem HMM.

---

## Rekomendacja i droga zgodna z zasadami

**Kierunek ①** (strategy-MWU) — najwyższa dźwignia, reużycie sprawdzonego kodu, wprost cel „najlepszy
zysk", online. Spina się z dowodem: skoro statyczny routing przegrywa, dodanie sprzężenia P&L jest
naturalną naprawą, nie zgadywaniem. ② jako tani komparator. ③–⑤ kolejne fale.

**Reżim wpięcia (NIENARUSZALNY):** opt-in domyślnie OFF → walidacja A/B na P&L (OOS, cząstkowana,
pasek postępu — Prawo XXIV) → flagę na sztywno przełącza Cezar po zielonym wyniku (Prawo XVIII,
ZASADA WPIĘCIA). Żaden kandydat nie jest „prawdą" przed pomiarem areny (Prawo I, ZASADA ZWIADOWCY WIEDZY).

## Źródła internetowe (pełne linki — ZPO)
- MetaPS: Adaptive Programmatic Strategy Selection — https://arxiv.org/html/2606.22385
- FinRL Ensemble (Deep RL, Yang i in.) — https://arxiv.org/pdf/2511.12120
- NYU Stern, Online Quantitative Trading Strategies — https://www.stern.nyu.edu/sites/default/files/2025-05/Glucksman_Lahanis.pdf
- Automate Strategy Finding with LLM in Quant Investment — https://arxiv.org/html/2409.06289v4
- CMAB + Neuroevolution for Stock Trading (GECCO 2024) — https://dl.acm.org/doi/10.1145/3638530.3664145

## Źródła z biblioteki (BIB-xxx)
- BIB-007 López de Prado — *Advances in Financial Machine Learning* (meta-labeling, rozdz. 3.6)
- BIB-023 López de Prado — *Machine Learning for Asset Managers* (meta-labeling §5.5; regime-switching Hamilton)
- BIB-010 Chan — *Quantitative Trading* 2nd ed (regime change & conditional parameter optimization)
- BIB-031 Tsay — *Analysis of Financial Time Series* (Markov Switching MSA, ukryty Markov)
- BIB-027 Aldridge — *High-Frequency Trading* (Markov switching zmienności)
- BIB-067 Sutton & Barto — *Reinforcement Learning: An Introduction* 2nd ed (bandyci kontekstowe)
