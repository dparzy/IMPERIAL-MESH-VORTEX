# 🔮 KSIĘGI SYBILLIŃSKIE — Rejestr Falsyfikowalnych Proroctw (perełka II, 2026-07-05)

> **Status: WIZJA/PROJEKT (Prawo XIX: to NIE jest kod).** Druga perełka końca wachty,
> siostra Legionów Cieni: Cienie mierzą decyzje nieprzeżyte — Sybilla mierzy SAMOWIEDZĘ.
> Zgodność: Prawo I (falsyfikowalność!), XV, XVI, XXV, ZPO, ZASADA WPIĘCIA.

---

## Idea w jednym zdaniu

**Imperium spisuje o SOBIE falsyfikowalne proroctwa z prawdopodobieństwem i terminem —
a przyszłe sesje bezlitośnie je rozliczają. Po roku wiemy nie tylko, czy system zarabia,
ale czy system WIE, CO O SOBIE WIE.**

## Rzym i my

Rzym w kryzysie otwierał Księgi Sybillińskie — proroctwa strzeżone przez kapłanów.
Nikt nigdy nie sprawdzał, czy Sybilla miała rację. **My będziemy pierwszym Imperium,
które swoją Sybillę rozlicza z każdego proroctwa.**

## Problem, którego nikt nie mierzy

Każdy quant ma przekonania o własnym systemie: „NEWS ożyje po podpięciu feedu",
„weto pomaga w PANIC", „ten neuron to perła". Te przekonania sterują decyzjami
rozwojowymi (co budować, co wyciszyć) — a NIKT nie mierzy ich trafności. Kalibrujemy
sygnały (conformal ML-36), ale nie kalibrujemy PRZEKONAŃ instytucji o sobie samej.
Miskalibrowana samowiedza = źle alokowany wysiłek całego projektu.

## Mechanizm (prosty, deterministyczny, na tym co mamy)

1. **Proroctwo** — wpis JSONL w git (niemutowalny przez historię commitów):
   `{id, data, twierdzenie, metryka, prog, horyzont, P, zrodlo}`
   Przykłady z DZIŚ:
   - „P=0.70: po podpięciu RSS, NEWS-01 osiągnie |IC warunkowy| ≥ 0.02 na 200 barach 4h"
   - „P=0.60: bramka konformalna (kalibruj_prog) przejdzie walidację (win-rate↑, DD nie gorszy)"
   - „P=0.55: MTF-weto zgeneralizuje na bessę 2018 (test W-384)"
2. **Rozliczenie** — przy starcie sesji Kustosz sprawdza proroctwa, którym minął horyzont,
   i rozstrzyga je AUTOMATYCZNIE z bazy areny / wyników walidacji (zero opinii — Prawo I).
   Nierozstrzygalne → jawnie „NIEROZSTRZYGNIĘTE" (nie znikają cicho).
3. **Wynik: Brier score Imperium** — per domena (neurony/bezpieczniki/adaptery/strategie).
   Krzywa kalibracji instytucji: gdy mówimy „70%", jak często mamy rację?
4. **Sprzężenie:** domeny z najgorszym Brierem = tam nasza intuicja kłamie = tam decyzje
   rozwojowe wymagają twardszych pomiarów PRZED budową. Samowiedza steruje roadmapą.

## Fundament naukowy (ZPO)

- **Brier score** — Glenn W. Brier, „Verification of Forecasts Expressed in Terms of
  Probability", Monthly Weather Review, 1950. ⚠️ link do weryfikacji przy wdrożeniu.
- **Proper scoring rules** — Gneiting & Raftery, JASA 2007 (reguły punktacji, których nie
  da się oszukać asekuranctwem). ⚠️ do weryfikacji.
- **Superforecasting** — Tetlock & Gardner, 2015: trafność prognoz rośnie od samego
  prowadzenia rozliczanego rejestru. My robimy to instytucji-AI, nie ludziom.

## Dlaczego to lata świetlne (i dlaczego tylko my)

1. **Nikt nie prowadzi rozliczanego rejestru przekonań systemu o sobie.** Boty raportują
   PnL; fundusze mają postmortemy pisane przez ludzi. Samo-kalibrująca się instytucja AI
   z Brierem w git — nie istnieje na rynku.
2. **Wymaga dokładnie naszych organów:** pamięci wieloletniej w git (13 warstw — proroctwa
   przeżywają sesje), bazy pomiarów do automatycznego rozstrzygania (arena), kultury
   Prawa I (zero udawanej weryfikacji). Konkurencja nie ma żadnego z trzech.
3. **Domyka trójcę kalibracji:** conformal kalibruje SYGNAŁY → Cienie kalibrują DECYZJE →
   Sybilla kalibruje PRZEKONANIA. Trzy piętra samowiedzy — kompletna epistemologia Imperium.
4. Efekt uboczny bezcenny dla Cezara-nowicjusza: każda obietnica Claude („to pomoże")
   staje się proroctwem z numerem — **asystent też jest rozliczany**. Koniec obietnic bez
   pokrycia, na zawsze, strukturalnie.

## Plan wdrożenia (przyszła sesja, przy laptopie)

1. `imperium/biblioteki/ksiegi_sybillinskie.py` — rejestr JSONL (dodaj/rozlicz/brier)
   + testy granic (horyzont minął/nie minął, nierozstrzygalne, P∈{0,1}, puste).
2. Hook startowy: „⚖️ Proroctwa do rozliczenia: N" (informacyjnie, non-blocking).
3. Pierwsze 5 proroctw: 3 przykłady z tego dokumentu + 2 od Cezara.
4. Po 10 rozliczeniach — pierwszy Brier Imperium i krzywa kalibracji w raporcie.
5. Rytuał: każda WIZJA i każde „to da przewagę" w LOG_ZMIAN dostaje proroctwo z P.

---
*Rzym pytał Sybillę, gdy płonął Kapitol. Imperium pyta Sybillę codziennie — i codziennie
sprawdza, czy Sybilla mówiła prawdę.* 🔮🏛️
