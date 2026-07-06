# 👥 LEGIONY CIENI — Kontrfaktyczne Kolosseum (perełka końca wachty, 2026-07-05)

> **Status: WDROŻONE — FAZA 1 (kod, 2026-07-06).** `imperium/koloseum/legiony_cieni.py`
> (`LegionyCieni` + `zbuduj_cienie_paper` — 3 cienie: bez_wet/prog_lagodny/prog_surowy) +
> 12 testów granic. Opt-in `cienie=False` w `KonfigPetliLive`, wpięte w `petla_live` (3c) —
> zamknięcia cieni → arena (rodzaj `CIEN_PNL`). Cienie to OBSERWATORZY (papierowe silniki
> obok głównego) — NIE dotykają realnych zleceń (ZASADA WPIĘCIA). **Faza 2 (żal→wagi MWU)
> NIEZBUDOWANA** — czeka na walidację ≥100 barów (raport_zalu.py, osobna decyzja Cezara).
> Zapisana na rozkaz Cezara jako „super perełka wyprzedzająca konkurencję o lata świetlne".
> Zgodność: Prawo XV (potencjał), XVI (reuse silników), XIX (kod), XXV (przewaga), ZASADA WPIĘCIA.

---

## Idea w jednym zdaniu

**Za każdym razem, gdy Imperium podejmuje decyzję, równolegle maszerują Legiony Cieni —
widmowe kopie roju, które podjęły decyzje INNE — i mierzymy, ile kosztowała nas każda
ostrożność i każda odwaga.**

## Problem, którego NIKT nie mierzy

Każdy system tradingowy zna wynik decyzji PODJĘTYCH. Nikt nie zna wyniku decyzji
NIEPODJĘTYCH: ile kosztowało weto Pretorianów? Ile zarobiłby próg 0.50 zamiast 0.55?
Ile zjadła bramka konformalna, a ile uratowała? Dziś na te pytania odpowiada się A/B
backtestem PO FAKCIE, na historii. My możemy odpowiadać NA ŻYWO, przy każdym barze.

To jest Prawo XV podniesione do potęgi: dziś alarmujemy o niewykorzystanych MODUŁACH —
Cienie alarmują o niewykorzystanych DECYZJACH.

## Dlaczego my możemy, a konkurencja nie (sedno przewagi)

**Nasz rój jest deterministyczny** (Brama liczy, kod głosuje, zero LLM w pętli decyzji).
Ten sam bar + ta sama konfiguracja = zawsze ta sama decyzja. Dlatego możemy tanio i
UCZCIWIE odtworzyć „co by było gdyby" — wystarczy przepuścić ten sam bar przez wariant
konfiguracji. Systemy agentowe na LLM (TradingAgents itp.) są niedeterministyczne — ich
kontrfaktyczne „gdyby" jest nieodtwarzalne. **Nasz determinizm, dotąd cecha inżynierska,
staje się bronią badawczą.** Tego się nie kopiuje doklejką — to architektura.

## Fundament naukowy (ZPO)

- **Counterfactual Regret Minimization (CFR)** — minimalizacja żalu kontrfaktycznego;
  Zinkevich, Johanson, Bowling, Piccione, „Regret Minimization in Games with Incomplete
  Information", NeurIPS 2007. ⚠️ link do zweryfikowania przy wdrożeniu.
- Rodzina CFR pokonała ludzi w pokerze no-limit (Libratus 2017, Pluribus 2019 — Brown &
  Sandholm, Science). ⚠️ do weryfikacji linków. Rynek, jak poker, to gra z niepełną
  informacją — żal (regret) jest tam naturalną miarą jakości polityki decyzyjnej.
- U nas w wersji 1: nie pełny CFR, lecz **pomiar żalu per mechanizm** (weto, próg, sizing)
  — uczciwy, prosty, mierzalny. Pełna aktualizacja polityk wg żalu = faza 2, po walidacji.

## Architektura (na tym, co JUŻ mamy — Prawo XVI reuse)

```
                    bar t
                      │
        ┌─────────────┼──────────────────────────────┐
        ▼             ▼                               ▼
   IMPERIUM      CIEŃ-1 (bez wet)               CIEŃ-2..N (próg 0.45/0.65,
   (realna       silnik papierowy               bez bramki ML-36, sizing×2…)
   decyzja)      równoległy                     silniki papierowe równoległe
        │             │                               │
        └──────►  arena_wyniki.db  ◄──────────────────┘
                 rodzaj='CIEN_PNL', neuron=nazwa_cienia
                      │
              KRONIKA ŻYĆ NIEPRZEŻYTYCH
        raport żalu: „weto kosztowało X% / uratowało Y%
         w reżimie Z — zmierzone na N barach live"
```

- Cienie to zwykłe `PaperTradingEngine` + `Dyrygent` z wariantem konfiguracji (wszystko
  istnieje). Koszt: ~N× czas cyklu paper (pomijalny przy barach 1H/4H).
- Wyniki lecą do bazy areny (istnieje) → Claude czyta MCP-em `arena_pytaj` (istnieje).
- Werdykty per REŻIM (Namiestnik istnieje) — „weto pomaga w PANIC, kosztuje w TREND"
  przestaje być opinią z backtestu, a staje się pomiarem z życia.

## Co z tego wynika (dlaczego to lata świetlne)

1. **Cena strachu i cena odwagi zmierzone na żywo.** Żaden retail ani open-source nie
   raportuje kosztu własnych bezpieczników w czasie rzeczywistym.
2. **Rada Cieni zamiast strojenia ręcznego:** po ≥100 barach żal per mechanizm wskazuje,
   który bezpiecznik dokręcić, a który poluzować — decyzja Cezara z POMIARU (Prawo I),
   wdrażana wg ZASADY WPIĘCIA (opt-in, A/B).
3. **Kompozycja z tym, co zbudowaliśmy tej wachty:** żal ↔ triada skilla (IC/MDA/WF) ↔
   kalibracja konformalna ↔ pamięć 13 warstw. Cienie domykają pętlę: graj → mierz →
   **żałuj mądrze** → ucz się.
4. Faza 2 (po walidacji): MWU karmione żalem kontrfaktycznym zamiast tylko wynikiem
   podjętych trade'ów — rój uczy się także z dróg, którymi nie poszedł.

## Plan wdrożenia (dla przyszłej sesji, przy laptopie)

1. `imperium/koloseum/legiony_cieni.py` — menedżer N wariantów (start: 3 cienie:
   `bez_wet`, `prog_lagodny`, `prog_surowy`) + zapis CIEN_PNL do areny. Testy granic.
2. Opt-in `cienie=False` w KonfigPetliLive (ZASADA WPIĘCIA — zero zmiany domyślnej).
3. `narzedzia/raport_zalu.py` — Kronika Żyć Nieprzeżytych: żal per mechanizm per reżim.
4. Walidacja: ≥100 barów paper z cieniami → pierwszy Raport Żalu dla Cezara.
5. Dopiero po nim ewentualna faza 2 (żal → wagi), osobna decyzja.

---
*„Prawdziwy łowca zna nie tylko ślady, którymi poszedł — zna też te, którymi nie poszedł,
i wie dokładnie, ile go to kosztowało."* 👥🏛️
