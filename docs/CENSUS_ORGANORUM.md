---
kategoria: TABULA
typ: zywy
wlasciciel: narzedzia/census_organorum.py
stan_na: 2026-08-02
powod_istnienia: "Spis WSZYSTKICH modulow imperium/ i narzedzia/ generowany z zywego kodu — zadny organ nie moze istniec bez meldunku; bramka Warstwy 17 audytu porownuje ten plik z kodem"
---
# 🏛️ CENSUS ORGANORUM — spis organów i narzędzi Imperium

> **Dokument GENEROWANY.** Nie edytuj ręcznie — treść jest przepisywana z żywego
> kodu przez `narzedzia/census_organorum.py`. Rola każdego modułu to pierwsza linia
> jego docstringu, więc opis nie może rozjechać się z kodem: żeby zmienić opis,
> zmieniasz docstring.
>
> **Po co to istnieje (dla nowicjusza):** wcześniej moduł mógł powstać, działać
> i nigdzie się nie zameldować — `imperium/cesarz/dispensator.py` przeżył tak całą
> sesję, a audyt i tak meldował „pełna harmonia", bo pilnował tylko jednego
> katalogu z jedenastu. Teraz **Warstwa 17** audytu porównuje ten plik z tym, co
> kod wygenerowałby w tej chwili — rozjazd zapala czerwień i blokuje commit.
>
> **Dodałeś moduł?** `python narzedzia/census_organorum.py --zapisz` i commituj
> razem ze zmianą (ZASADA PEŁNEJ SYMBIOZY).

<!-- CENSUS:start — sekcja generowana, NIE edytuj ręcznie -->

**Modułów w cenzusie: 258** w 18 katalogach (generowane z żywego kodu — `python narzedzia/census_organorum.py --zapisz`).

### `imperium/akwedukty/` — AQUAEDUCTUS — przepływ danych (świece, adaptery zewnętrzne)

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `bary_zdarzeniowe.py` | W-356 / Bary Zdarzeniowe: Tick / Volume / Dollar / Imbalance Bars (AFML Ch. 2) |
| `czytnik_csv.py` | 📜 CZYTNIK CSV — wczytuje historyczne dane rynkowe do barów Imperium |
| `klasyfikator_zdarzen.py` | 🏷️ Klasyfikator Zdarzeń Newsowych — taksonomia + KIERUNEK per typ (dla NEWS-02) |
| `kwatermistrz_danych.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `news_fetcher.py` | 📡 FetcherNewsRSS — pobieracz nagłówków rynkowych dla NEWS-01 (UNLOCK adaptera) |
| `sentyment_historyczny.py` | 📡 Sentyment historyczny — most między historią futures (funding/OI/LS) a osią barów |

### `imperium/akwedukty/adaptery/` — AQUAEDUCTUS — przepływ danych (świece, adaptery zewnętrzne)

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `baza.py` | 🔌 AdapterDanych — bazowy most: zewnętrzne API → dict `wskazniki` → rój budzi neurony |
| `cvd.py` | 📊 AdapterCVD — most danych trade-feed: Binance aggTrades PUBLICZNE → V-03 |
| `dvol.py` | 😱 AdapterDVOL — indeks strachu opcji (PSY-05, Deribit DVOL) |
| `feargreed.py` | 😱 AdapterFearGreed — PIERWSZY prawdziwy adapter API (PSY-03) |
| `futures.py` | 🔥 AdapterFutures — most danych futures: Binance fapi PUBLICZNE → PSY-01/02/04 |
| `mexc_futures.py` | 🔥 AdapterMEXCFutures — most danych futures z MEXC (PUBLICZNE contract API) → PSY-01/04 |
| `news_llm.py` | 📰 AdapterNewsLLM — most do NEWS-01 (sentyment nagłówków rynkowych) |
| `stablecoin.py` | 🏛️ AdapterStablecoin — podaż stablecoinów (K-03, DefiLlama) |
| `testowy.py` | 🧪 Adaptery TESTOWE (mock) — dane syntetyczne dla 3 domen API, działają offline |
| `usd_sila.py` | 🪙 AdapterUSD — siła dolara (K-04 MONETA, Frankfurter FX) |

### `imperium/biblioteki/` — BIBLIOTHECA — pamięć, kroniki, rejestry, uczenie

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `arena_baza.py` | 🏟️ ARENA BAZA — wspólna warstwa bazy wyników areny (SQLite, stdlib) |
| `arena_trzech_bram.py` | 🏛️ IMV / Arena Trzech Bram — potrójna bariera (W-035) |
| `centrum_pamieci.py` | 🧠 Centrum Pamięci Imperium (W-360 v5) — zunifikowany hub wszystkich warstw pamięci |
| `codex_notarum.py` | CODEX NOTARUM — Księga Not Cenzorskich (LEX TALIONIS IMPERII) |
| `dziennik_niesmiertelny.py` | ♾️ Dziennik Nieśmiertelny — W6 Centrum Pamięci W-360 v6 (UNIKAT IMPERIUM) |
| `graf_pamieci.py` | 🕸️ Graf Pamięci — W8 Centrum Pamięci W-360 v8: POŁĄCZENIA NEURONÓW (UNIKAT IMPERIUM) |
| `hedge_mwu.py` | HedgeMWU — Multiplicative Weights Update / algorytm Hedge (wizja W-049) |
| `igrzyska.py` | Igrzyska — silnik rywalizacji neuronów (W-002) |
| `index_falsorum.py` | INDEX FALSORUM — Spis Twierdzeń Obalonych (organ pamięci Imperium) |
| `kronika_czatu.py` | 📜 Kronika Czatu (W-360) — trwała pamięć CAŁEJ rozmowy między sesjami |
| `kronikarz.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `kronikarz_zdarzen.py` | 📜💎 KRONIKARZ ZDARZEŃ (Augur Imperium) — unikat W-289 (v2 rozbudowany 2026-06-10) |
| `ksiega_wad_kodu.py` | 🐞 KSIĘGA WAD KODU — pamięć wzorców błędów (samo-leczenie, Prawo XV/XVI) |
| `ksiegi_sybillinskie.py` | 🔮 KSIĘGI SYBILLIŃSKIE — rejestr falsyfikowalnych proroctw Imperium o SOBIE |
| `kustosz_pamieci.py` | 👑 Kustosz Pamięci — W7 Centrum Pamięci W-360 v7: NADRZĘDNY ORGAN (UNIKAT IMPERIUM) |
| `mnemosyne.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `notarius.py` | 📜 NOTARIUS — pisarz Imperium: stenografuje słowa Nauczyciela (Filar 2 TIRO, distylacja) |
| `pamiec_absolutna.py` | Pamięć Absolutna — centralny system logowania Imperium |
| `pamiec_proceduralna.py` | 🛠️ Pamięć Proceduralna — W11 Centrum Pamięci W-360 v11 (taksonomia CoALA — UNIKAT) |
| `pamiec_proweniencji.py` | 🔍 Pamięć Proweniencji — W13 Centrum Pamięci W-360 v13 (origin trail — UNIKAT) |
| `pamiec_robocza.py` | 🎯 Pamięć Robocza — W12 Centrum Pamięci W-360 v12 (taksonomia CoALA — domknięcie) |
| `pamiec_sesji.py` | 🧠 Pamięć Sesji (W-360) — ciągłość między sesjami Claude Code |
| `refleksja_pamieci.py` | 🪞 Refleksja Pamięci — W9 Centrum Pamięci W-360 v9: SPRZECZNOŚCI + PRZEDAWNIENIE (UNIKAT) |
| `rejestr_wizji.py` | 📋 Rejestr Wizji i Decyzji — W4 Centrum Pamięci W-360 v4 |
| `schola.py` | 🏛️ SCHOLA — organ Szkoły Cezara: czyta lekcje z ŻYWEGO dokumentu i pilnuje, |
| `sigillarium.py` | 🔏 SIGILLARIUM — Skarbiec Pieczęci Imperium (SIGLA IMPERII) |
| `srodowisko_pamieci.py` | 🌉 Most Chmura↔Lokal — W5 Centrum Pamięci W-360 v5 (UNIKAT IMPERIUM) |
| `synapsy_rezimowe.py` | 🧬 IMV-ORI / Synapsy Reżimowe — Regime-Aware Decorrelated Coalition Graph (W-299) |
| `zapominanie.py` | 🍂 Mądre Zapominanie — W10 Centrum Pamięci W-360 v10: LEARNED FORGETTING (UNIKAT) |

### `imperium/cesarz/` — CAESAR — rdzeń decyzji (most LLM, refleksja)

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `aerarium.py` | 🏦 AERARIUM — skarbiec Imperium: waga kontekstu startowego i stopnie wysiłku |
| `deepseek_glos.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `dispensator.py` | DISPENSATOR — Szafarz Imperium: ile myślenia KUPUJEMY do danego zadania |
| `ksiega_wad.py` | 📕 KSIĘGA WAD — prewencyjny filtr powtarzalnych błędów (W-309) |
| `pamiec_refleksyjna.py` | 🧠 PAMIĘĆ REFLEKSYJNA — zamknięta pętla uczenia narracyjnego Brain (W-295) |
| `titan_mind.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |

### `imperium/cesarz/doradcy/` — CAESAR — rdzeń decyzji (most LLM, refleksja)

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `fulmen.py` | 🏛️ IMV-ORI / FULMEN — Regime Validator |
| `hermes.py` | 🏛️ IMV-ORI / HERMES — Information Auditor |
| `iustitia.py` | 🏛️ IMV-ORI / IUSTITIA — Risk Auditor |
| `oracle.py` | 🏛️ IMV-ORI / ORACLE — Sharpe Auditor |
| `pythia.py` | 🏛️ IMV-ORI / PYTHIA — Probabilistic Advisor |
| `rada.py` | 🏛️ IMV-ORI / RadaDoradcow — Orchestrator Rady Pięciu Doradców |

### `imperium/drogi/` — VIA — routing i egzekucja zleceń

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `nexus_hub.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `oms.py` | W-344 — OMS (Order Management System) — Zarządca Zleceń Imperium |
| `real_order_router.py` | W-331 — RealOrderRouter: Most do realnych zleceń MEXC (paper=False) |
| `scheduler.py` | 🏛️ IMV-ORI / Scheduler — cykliczne uruchamianie pętli Imperium |

### `imperium/fundament/` — FUNDAMENTUM — Brama Kalkulatora, narzędzia bazowe

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `brama_kalkulatora.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `faber.py` | 🔨 FABER — Kowal Imperium: odnajduje zewnętrzne narzędzia i głośno melduje ich brak |
| `kuznia_narzedzi.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |

### `imperium/koloseum/` — COLOSSEUM — walidacja, backtest, kontrfaktyki

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `backtest.py` | 🏟️ BACKTEST — przejazd Dyrygenta po prawdziwej historii rynku |
| `drift_adapter.py` | 🌊 DRIFT ADAPTER — antycypacyjna adaptacja do zmiany reżimu (W-296) |
| `dyrygent.py` | 🏛️ DYRYGENT — orkiestrator pełnego cyklu decyzyjnego Imperium (Faza 1) |
| `gubernator.py` | 🧭 IMV-ORI / GUBERNATOR — Homeostatyczny Sterownik Portfela (W-325) |
| `haruspex.py` | 🔮 HARUSPEX — Predykcyjny Namiestnik (kandydat #20, żniwo wrzutni 2026-07-12) |
| `legiony_cieni.py` | 👥 LEGIONY CIENI — Kontrfaktyczne Kolosseum (perełka końca wachty → KOD, Prawo XIX) |
| `lookahead.py` | 🔍 DETEKTOR LOOKAHEAD-BIAS — strażnik uczciwości backtestu |
| `monte_carlo.py` | 🎲 MONTE CARLO ROBUSTNESS — walidacja odporności przewagi (W-293) |
| `namiestnik.py` | 🏛️ NAMIESTNIK — Regime-Aware Gating Network (Meta-Controller) |
| `optymalizator.py` | 🔬 OPTYMALIZATOR HIPERPARAMETRÓW — DSR-guided parameter search (W-294) |
| `paper_trading.py` | 🏛️ IMV-ORI / Paper Trading Engine — symulator bez realnych pieniędzy |
| `petla_live.py` | 🔴 PĘTLA LIVE — W-302 / Główny entrypoint systemu tradingowego |
| `selektor_par.py` | 🎯 SELEKTOR PAR (W-330) — automatyczny dobór par do handlu LIVE na MEXC |
| `skaner_okazji.py` | Skaner Okazji (W-316) — łowca najlepszych setupów w CAŁYM koszyku |
| `walidacja.py` | 🛡️ WALIDACJA KOLOSEUM — bramka anty-overfittingu (W-282, BIB-007) |
| `walk_forward.py` | 🔄 WALK-FORWARD — kroczące okna In-Sample/Out-of-Sample (W-345) |

### `imperium/legiony/` — LEGIONES — neurony, zwiadowcy, strategie, Legatus

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `_jit.py` | ⚡ Wspólny most JIT (Numba) — opcjonalne przyspieszenie gorących pętli numerycznych |
| `bocpd.py` | W-338 / BOCPD — Bayesian Online Change-Point Detection |
| `budowniczy_wskaznikow.py` | 🔧 Budowniczy Wskaźników — spina Bramę v2 z serią barów w komplet dict dla neuronów |
| `denoising_macierzy.py` | 🧬 IMV-LDP / Denoising + Clustering macierzy korelacji (López de Prado, MLAM 2020) |
| `diagnostyka_korelacji.py` | 📊 IMV-DIAG / Diagnostyka Dekorelacji — macierz korelacji sygnałów modułów |
| `discriminator.py` | 🔍 DISCRIMINATOR — orzeka, czy SKUPISKO neuronów to naprawdę redundancja |
| `feature_importance.py` | W-355 / Feature Importance: MDA + SFI (López de Prado, AFML Ch. 8) |
| `frac_diff.py` | W-339 / Fractional Differentiation — stacjonaryzacja z zachowaną pamięcią długiego zasięgu |
| `jump_model.py` | 🗿 STATISTICAL JUMP MODEL — detektor reżimu z karą za skok (W-281) |
| `kalibrator_konformalny.py` | 🎯 KALIBRATOR KONFORMALNY — twarda gwarancja pokrycia dla pewności roju (Prawo XXV) |
| `legatus.py` | Generał Legatus — koordynator między Legionami a Senatem |
| `meta_labeling.py` | W-337 / B-01 Meta-labeling — bet-sizing layer nad Legatusem |
| `metryki_ic.py` | W-369..371: Information Coefficient, breadth i IR (Grinold & Kahn Fundamental Law) |
| `mikro_neuron.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `mikrostruktura.py` | 🔬 IMV-OHARA / Mikrostruktura informacyjna (O'Hara, BIB-032, INF-44) |
| `mtf_konfluencja.py` | 🕐 IMV-MTF / Konfluencja Multi-Timeframe na poziomie ROJU (W-384) |
| `neutralizacja.py` | W-337 / B-02 Feature Neutralization — Prawo XVI w runtime |
| `pierwszy_zwiadowca.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `progi_adaptacyjne.py` | W-334 — Progi adaptacyjne (P3): kameleon progów RSI/ADX wg reżimu i zmienności |
| `przekroj_koszyka.py` | W-335 C-01 / Cross-sectional Relative Strength — liczony na poziomie KOSZYKA |
| `radar_btc.py` | 🛰️💎 RADAR BTC — strażnik lidera rynku (W-291, lead-lag) |
| `radar_rynku.py` | 🛰️🌐💎 RADAR RYNKU — wielowymiarowy strażnik kontekstu (W-292, rozwój W-291) |
| `rejestr.py` | 📒 Rejestr Legionu — fabryka pełnego Legatusa z wszystkimi neuronami i zwiadowcami |
| `rezim_zmiennosci.py` | W-340 / Detektor reżimu zmienności — lekka, online wersja Jump Modelu (vol-gate) |
| `roj_sygnalow.py` | ╔══════════════════════════════════════════════════════════════════╗ |
| `triple_barrier.py` | W-357 / Triple-Barrier Method + CUSUM Filter (AFML Ch. 3, §3.4 + Ch. 17, §17.2) |
| `zmiana_rezimu.py` | W-336 / CUSUM change-point detector — wykrywa, że REŻIM właśnie się zmienił |

### `imperium/legiony/neurony/` — LEGIONES — neurony, zwiadowcy, strategie, Legatus

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `dzwignia.py` | ⚔️ IMV-INS / Neurony Dźwigni i Zmienności — kategorie L i V |
| `entropia.py` | ⚔️ IMV-INS / Neurony Entropii/Pamięci — kategoria N (Entropia / Informacja) |
| `fraktal.py` | ⚔️ IMV-INS / Neurony Fraktalne — kategoria H (Hurst / pamięć długiego zasięgu) |
| `geometria.py` | ⚔️ IMV-INS / Neurony Geometrii Ścieżki — kategoria D (Dynamika ścieżkowa) |
| `makro.py` | 🌐 W-350/K / Neurony Makro — Dywizja Intermarket (Murphy, Technical Analysis rozdz. 15) |
| `momentum.py` | ⚔️ IMV-INS / Neurony Momentum — Legion X Equestris (Scalp) |
| `news_dynamika.py` | 🏛️ IMV-ORI / Neurony Dynamiki Newsów — Dywizja Wyrocznia (NEWS) |
| `onchain.py` | ⚔️ IMV-INS / Neurony On-Chain — Dywizja Wieszczowie |
| `przekroj.py` | ⚔️ IMV-INS / Neurony Przekrojowe — kategoria C (Cross-sectional / Relative Strength) |
| `psychologia.py` | 🏛️ IMV-ORI / Neurony Psychologii — Dywizja Wyrocznia (PSY) |
| `rezim_zmiana.py` | ⚔️ IMV-INS / Neurony Zmiany Reżimu — kategoria R (Regime) |
| `sentyment.py` | 🏛️ IMV-ORI / Neurony Sentymentu Newsów — Dywizja Wyrocznia (NEWS) |
| `sesje.py` | ⏰ IMV-SES / Neurony Zegarów Rynku — sesje, rytm fundingu, sezonowość (Faza C, W-286) |
| `straz.py` | 🛡️ IMV-INS / Neurony Straży — Dywizja Anty-Manipulacji (KATEGORIA A) |
| `struktura.py` | ⚔️ IMV-INS / Neurony Struktury Rynku — SMC/ICT/VSA |
| `trend.py` | ⚔️ IMV-INS / Neurony Trendu — Legion XII Fulminata (Swing) |
| `wolumen.py` | ⚔️ IMV-INS / Neurony Wolumenu — OBV, CVD, VWAP, Volume Profile |
| `zagrozenie.py` | 🚨 IMV-INS / Neurony Zagrożenia — kategoria Z (Zagrożenie / Threat) |
| `zdarzenia.py` | 🏛️ IMV-ORI / Neuron Taksonomii Zdarzeń — Dywizja Wyrocznia (NEWS) |

### `imperium/legiony/strategie/` — LEGIONES — neurony, zwiadowcy, strategie, Legatus

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `baza.py` | 🗺️ IMV / Dywizja Strategii — bazowy model + silnik dopasowania |
| `rejestr_strategii.py` | 🗺️ IMV / Rejestr Strategii — strategie z bazy ludzi, zmapowane na ŻYWE neurony |

### `imperium/legiony/zwiadowcy/` — LEGIONES — neurony, zwiadowcy, strategie, Legatus

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `baza.py` | 🏛️ IMV-ORI / ZwiadowcaElitarny — bazowa klasa Dywizji Exploratores |
| `exp_atmabhan.py` | 🔱 IMV-ADO / EXP-12 Atmabhan — mikrostruktura L2 orderbook (AP-Mode) |
| `exp_displacement.py` | 🔱 IMV-ADO / EXP-10 Displacement Scalper — impuls strukturalny (Gold Scalper engine) |
| `exp_dynamic.py` | 🔱 IMV-ADO / EXP-11 Dynamic Scalper — cross MA z bramką jakości egzekucji |
| `exp_garch.py` | W-376: GARCH(1,1) + GJR-GARCH — zmienność warunkowa (Tsay, BIB-031, rozdz. 3) |
| `exp_ha_scalper.py` | 🔱 IMV-ADO / EXP-02 HA Scalper Full — pełna implementacja MSX Hybrid Heiken Scalper |
| `exp_higuchi.py` | 🔬 IMV-EXP / EXP-01 Higuchi Fractal Dimension — detektor reżimu rynkowego |
| `exp_hurst.py` | 📐 IMV-EXP / EXP-03 Hurst Exponent — detektor persystencji szeregu czasowego |
| `exp_kalman.py` | 🎯 IMV-EXP / EXP-04 Kalman Filter ATR — adaptacyjny filtr trendu |
| `exp_katana.py` | 🔱 IMV-ADO / EXP-06 Katana Scalper Pro — zaawansowany skalpel z redukcją szumu |
| `exp_kyle_lambda.py` | W-380: Kyle's Lambda — price impact per unit net order flow (O'Hara BIB-032, rozdz. 4) |
| `exp_night.py` | 🔱 IMV-ADO / EXP-08 Night Turbo Scalper — kontrarianski scalper nocny (mean-reversion) |
| `exp_pin.py` | W-383: PIN (Probability of Informed Trading) jako zwiadowca (O'Hara BIB-032, INF-44) |
| `exp_smc.py` | 🏗️ IMV-EXP / EXP-05 ZwiadowcaSMC — wykrywacz struktur Smart Money |
| `exp_sweep.py` | 🔱 IMV-ADO / EXP-09 Liquidity Sweep — stop-hunt fade scalper (Hit & Run) |
| `exp_tlp.py` | 🔱 IMV-ADO / EXP-07 A-TLP Scalper — breakout z kanału zmienności (Donchian + ATR) |
| `igrzyska_exploratores.py` | 🏛️ IMV-ORI / Igrzyska Exploratores — osobna skala oceniania dla Zwiadowców |

### `imperium/oczy/` — OCULI — percepcja (sprzęt, zmysły zewnętrzne)

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `breviarium.py` | 📋 BREVIARIUM — Zwięzły Spis Sług Imperium (meldunek na otwarcie wachty) |
| `censor_sprzetu.py` | 🏛️ CENSOR SPRZĘTU — organ „oczu" mierzący majątek maszyny (Prawo XV) |
| `wszechoko.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |

### `imperium/pretorianie/` — PRAETORIANI — bezpieczniki, weto ryzyka, straż u wrót

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `aegis_tarcza.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `custos_liminis.py` | 🚧 CUSTOS LIMINIS — Strażnik Progu: bariera PRZED zadziałaniem narzędzia (PreToolUse) |
| `exactor.py` | 🪙 EXACTOR RENUNTIATIONIS — egzekwuje, czy MELDUNEK KOŃCOWY spłaca checklistę |
| `filtr_asymetrii.py` | Filtr Asymetrii Reżimu (W-314) — brama wejścia oparta na trendzie i jego sile |
| `filtr_ekonomiczny.py` | Filtr Ekonomiczny (ECON — market price of risk) — brama „zbyt dobre, by było prawdziwe" |
| `kalkulator_lewara.py` | Kalkulator Lewara — matematyka przeżycia |
| `lustro_prawdy.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `nomenclator.py` | 🏷️ NOMENCLATOR — Strażnik Imion Imperium (warstwa 2 anty-redundancyjna Hyginusa) |
| `portitor.py` | 🏛️ PORTITOR — celnik u wrót: pre-flight gotowości środowiska na starcie sesji (Prawo XV/XVII) |
| `praeda.py` | 🗡️💎 PRAEDA (Łupieżca) — TRYB ŁOWCY: kontrolowana, AUTO-skalowana chciwość (W-291) |
| `probator.py` | 🛡️ PROBATOR — Strażnik Cytatów Imperium (warstwa 1 anty-halucynacyjna Hyginusa) |
| `recognitor.py` | 🔎 RECOGNITOR — poświadcza, czy RECENZJA POKRYWA DZISIEJSZY STAN kodu |
| `sizing_przekonania.py` | Sizing Przekonania (W-318) — większa stawka na mocniejszej okazji |
| `straznik_przewagi.py` | 🛡️💎 STRAŻNIK PRZEWAGI — unikat Imperium (W-287, Faza C) |
| `vigil.py` | 🔦 VIGIL — Straż Nocna: skan KAŻDEGO zapisanego pliku .py natychmiast (PostToolUse) |
| `vindex.py` | ⚖️ VINDEX — obrońca zapisu: czy ktoś zmienił to, co miało zostać niezmienne |

### `imperium/senat/` — SENATUS — meta-decyzje, debata

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `debata_senatu.py` | Debata Senatu (W-343) — jawna debata Byk / Niedźwiedź / Cenzor-Ryzyka |
| `meta_kora.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |

### `imperium/swiatynie/` — TEMPLA — wiedza, mapy, panele, wizualizacje

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `godlo.py` | Godło Imperium (W-342) — generator znaku rozpoznawczego |
| `kartograf.py` | ╔══════════════════════════════════════════════════════════════════════════════╗ |
| `live_monitor.py` | LiveMonitor — TUI dashboard na żywo (W-341, Prawo XXIV: Widoczność Operacyjna) |
| `praetorium.py` | 🏛️ PRAETORIUM — Kwatera Główna Imperatora (Centrum Dowodzenia) |
| `specula_swiec.py` | 🗼 SPECULA — Wieża Obserwacyjna (świece OHLC w terminalu, W-361, Prawo XXIV) |
| `web_dashboard.py` | 🌐 WEB DASHBOARD — Panel Kapitolu (W-346 + W-354, realizuje W-004 + W-031) |
| `webhook_tradingview.py` | W-354 — TradingView Webhook Receiver (Prawo XV — potencjał na żywo) |

### `narzedzia/` — OFFICINA — warsztat: pomiary, audyty, generatory, raporty

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `ab_dvol.py` | 😱 A/B DVOL (PSY-05) — czy zwalidowany IC +0.16@7d przekłada się na realny PnL? (Prawo I) |
| `ab_plon_hyginusa.py` | ⚖️ LIBRA MESSIS — Waga Plonu: A/B jakości zwiadu Hyginusa |
| `ab_pnl_wazenie_ic.py` | 💰 A/B NA P&L — ważenie głosów IC w PEŁNEJ ścieżce decyzyjnej (W-361, hipoteza B) |
| `ab_stablecoin.py` | 🏛️ A/B STABLECOIN (K-03) — czy IC +0.05..0.10 przekłada się na PnL? (Prawo I) |
| `ab_strategy_mwu.py` | 🎯 A/B strategy-MWU (W-362) — czy ważenie strategii realnym P&L poprawia P&L routingu |
| `ab_tryb_strategii.py` | 🎯 A/B WARSTWY STRATEGII — czy 20 szkiców (SZKIC) dokłada wartość w ścieżce decyzyjnej |
| `ab_ucz_mwu.py` | 🎓 DISCIPULUS — A/B ZAMKNIĘTEJ PĘTLI UCZENIA (`ucz_mwu`, W-049/W-280/W-285.1) |
| `ab_usd.py` | 🪙 A/B USD (K-04 MONETA) — czy IC -0.27@30d przekłada się na PnL? (Prawo I) |
| `ab_w322.py` | A/B impakt 5 nowych neuronów W-322 na TRYB NAJLEPSZY (4h, to samo okno 2022→2026) |
| `ab_w323.py` | A/B W-323 — profil stylu vs pełny rój na TRYB NAJLEPSZY (4h, okno 2022→2026) |
| `ab_w324.py` | A/B W-324 — Brama Momentum Bezwzględnego (TS Gate) vs brak bramy |
| `ab_w325.py` | A/B W-325 — GUBERNATOR (homeostatyczny sterownik portfela) vs baseline |
| `ab_w329.py` | A/B W-329 — ktore mechanizmy uczenia online warto wlaczyc w LIVE (Prawo I) |
| `ab_w330_radar.py` | A/B W-330 — czy glosy radaru RADAR-04 (kaskada) + RADAR-05 (lead-lag) POMAGAJA (Prawo I) |
| `ab_w334_progi.py` | A/B W-334 — czy progi adaptacyjne RSI/ADX POMAGAJA (Prawo I) |
| `ab_w335_cross_rs.py` | A/B W-335 — czy neuron C-01 (cross-sectional RS) POMAGA (Prawo I/XVI) |
| `ab_w336_changepoint.py` | A/B W-336 — czy neuron CP-01 (CUSUM change-point) POMAGA (Prawo I/XVI) |
| `ab_wazenie_ic.py` | ⚖️ A/B NA ŻYWO — ważenie głosów IC w REALNYM Legatusie (W-361, hipoteza B) |
| `agreguj_bary.py` | 🧱 CONFLATOR TEMPORUM (Zlewacz Interwałów) — AGREGATOR BARÓW: buduje wyższy interwał z niższego (1m→5m/15m, 1h→4h) |
| `arena_mcp.py` | Arena MCP Server — wystawia stan i wyniki ROJU dla Claude Code (nauka areny na żywo) |
| `arena_zasil.py` | 🏟️ ARENA ZASIL — domyka pętlę „graj → mierz → ucz się" (Prawo XVI/XXV) |
| `audyt_danych.py` | 🔬 VERITAS ANNALIUM (Prawda Roczników) — AUDYT DANYCH ŚWIECOWYCH: czy nasze OHLCV mówi prawdę? |
| `audyt_spojnosci.py` | 🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0) |
| `auto_lekcja.py` | 🤖 Auto-Lekcja (Opcja C — W-360 v4) — DeepSeek ekstrahuje lekcje i wizje z sesji |
| `backfill_sentyment.py` | 📡 Backfill sentymentu — pobiera historię funding/OI/L-S z Binance public → CSV |
| `backtest_ab_mtf.py` | 🕐⚔️ BACKTEST A/B — Konfluencja Multi-Timeframe (W-384) jako arbiter pieniężny |
| `backtest_ab_mtf_rezimy.py` | 🕐⚔️📊 BACKTEST A/B MTF PER REŻIM (W-384) — czy brama pomaga w TRENDZIE, szkodzi w RANGE? |
| `backtest_dashboard.py` | 📊 BACKTEST DASHBOARD — uruchamia backtest i renderuje wynik w przeglądarce |
| `backtest_nowe_pary.py` | Backtest nowych par — porownuje rozszerzony koszyk z baseline |
| `bibliotekarz.py` | 📚 HYGINUS — BIBLIOTEKARZ-ZWIADOWCA Imperium. DeepSeek skanuje bibliotekę i proponuje KANDYDATÓW |
| `census_organorum.py` | CENSUS ORGANORUM — spis wszystkich organów i narzędzi Imperium, GENEROWANY z kodu |
| `cenzus_adapterow.py` | 📋 CENZUS ADAPTERÓW (Prawo XV) — spis żywych modułów adapterowych na REALNYCH danych |
| `codex_probationum.py` | 📜 CODEX PROBATIONUM — żywy rejestr testów Imperium w Excelu |
| `dekorelacja_w322.py` | Pomiar dekorelacji neuronów W-322 (V-06/V-07/VP-01/Z-06/Z-07) na BTCUSDT 4h |
| `hipoteza_b.py` | 🧪 HIPOTEZA B — czy WAŻENIE GŁOSÓW IC leczy wąskie gardło agregacji (Prawo XV/XVI) |
| `install_hooks.py` | Instalator git hooków Imperium |
| `kalibracja_1h.py` | Kalibracja progów wejścia pod 1h (W-321c). Cel: znaleźć konfigurację, która |
| `kalibracja_1h_v2.py` | Kalibracja progów wejścia pod 1h (W-321c). Cel: znaleźć konfigurację, która |
| `kapitol_podglad.py` | 🏛️ KAPITOL PODGLĄD (Speculum Probationis) — zero-tokenowy podgląd testu w przeglądarce |
| `najlepszy_tryb.py` | 🏆 NAJLEPSZY TRYB IMPERIUM — Skaner Okazji + Gubernator + Regime-Aware + Compounding |
| `pobierz_4h_binance.py` | Pobiera dane 4h bezpośrednio z publicznego API Binance (bez klucza) |
| `pobierz_binance.py` | ⬇️ NUNTIUS MERCATUS (Posłaniec Rynku) — POBIERACZ BINANCE: świece dowolnego interwału z publicznego API (bez klucza) |
| `pobierz_makro.py` | 🌐 Pobieranie danych makro z Yahoo Finance (DXY, XAUUSD, SPX) |
| `pobierz_nowe_pary.py` | Pobierz nowe pary — skrypt do uruchomienia LOKALNIE przez Cezara |
| `pomiar_dekorelacji_bib020.py` | 📊 Pomiar dekorelacji wizji BIB-020 (Prawo XVI — spłata długu „do zmierzenia") |
| `pomiar_dvol_ic.py` | 😱 PAVOR — pomiar IC indeksu strachu DVOL (Prawo I + XXIV). Walidacja Tier-1 alt-danych |
| `pomiar_funding_ic.py` | 🧪 PROBATIO FUNDING (Prawo I + XXIV) — walidacja TIER A: czy FUNDING_RATE ma IC? |
| `pomiar_haruspex.py` | 🔮 POMIAR HARUSPEXA — trafność predykcji reżimu na REALNYCH świecach (Prawo I + XXIV) |
| `pomiar_jump_model.py` | 📊 POMIAR JUMP MODEL (W-281) — tabela dowodowa przed Fazą 3 master-switcha |
| `pomiar_namiestnik.py` | 📊 POMIAR NAMIESTNIKA — tabela dowodowa przed/po (Prawo XVI) |
| `pomiar_nowe_moduly.py` | 🔬 POMIAR NOWYCH MODUŁÓW (Prawo XVI) — EXP-13/14/15 + OC-06/08 |
| `pomiar_portfela.py` | 📊💎 POMIAR PORTFELA (W-290) — czy dywersyfikacja 5 par przekracza próg Sharpe? |
| `pomiar_stablecoin_ic.py` | 🏛️ AERARIUM — pomiar IC podaży stablecoinów (Prawo I + XXIV). Walidacja Tier-1 alt-danych |
| `pomiar_usd_ic.py` | 🪙 MONETA — walidacja Tier-1: siła USD (DXY-proxy) vs zwroty BTC (Prawo I + XXIV) |
| `przygotuj_biblioteke.py` | Przygotuj Bibliotekę LOKALNIE — jedna komenda, ZERO tokenów Claude |
| `raport_etykiet.py` | 🏷️ RAPORT ETYKIET — Triple-Barrier + CUSUM (López de Prado, W-357, AFML Ch.3-4) |
| `raport_ic.py` | 📊 RAPORT IC ROJU — który neuron ma REALNY skill predykcyjny (Prawo XVI/XXV) |
| `raport_waznosci.py` | 🎯 RAPORT WAŻNOŚCI NEURONÓW — Feature Importance MDA+SFI (López de Prado, W-355) |
| `raport_wfo.py` | 🔄 RAPORT WFO — Walk-Forward Optimization parametrów (W-345, Pardo) |
| `raport_zalu.py` | 👥 RAPORT ŻALU — Kronika Żyć Nieprzeżytych (Legiony Cieni, krok 3 wizji) |
| `scoreboard_neuronow.py` | W-323c — SCOREBOARD KONTRYBUCJI NEURONÓW (mierzona baza do strojenia profili) |
| `scriba_codex.py` | 🖋️ SCRIBA CODEX PROBATIONUM — skryba, który dopisuje wyniki testów do ledgera |
| `skan_wad_kodu.py` | 🐞 SKAN WAD KODU — heurystyczny łowca powtórek błędów (Księga Wad Kodu) |
| `status.py` | 📊 STATUS IMPERIUM — pulpit jednego spojrzenia (Prawo XVII) |
| `sym_1h.py` | Runner symulacji TRYB NAJLEPSZY (pełny stack W-317..W-321) na danych 1h |
| `sym_porownanie_tf.py` | Porównanie TF na TYM SAMYM oknie czasowym (izolacja: interwał vs okno) |
| `tabularium.py` | 🏛️ TABULARIUM — archiwum państwowe Imperium: rejestr wszystkich żywych dokumentów |
| `walidacja_kalibrator.py` | 🔬 WALIDACJA KALIBRATORA — A/B progu pewności: baza vs bramka konformalna (ML-36) |
| `waliduj_zmysly.py` | 👁️ WALIDACJA ZMYSŁÓW — czy adaptery faktycznie BUDZĄ neurony na ŻYWYCH danych (Prawo XV) |
| `walk_forward_ic.py` | 🔬 WALK-FORWARD IC — czy skill neuronu jest STABILNY w czasie (Prawo XVI, OOS) |
| `wfo_chunked.py` | 🧩 WFO CHUNKED (Cursus Fenestrarum) — walk-forward CZĄSTKOWY i WZNAWIALNY |
| `wykres_backtestu.py` | 🖼️ WYKRES BACKTESTU — oczy Cezara (Prawo XV: Kartograf był niewpięty = utrata potencjału) |
| `wykres_kalibracja_1h.py` | Wykresy kalibracji 1h (W-321c) — wizualizacja zamiast samych tabel |
| `wykres_tryb_najlepszy.py` | Wykres „Tryb Najlepszy" (W-317..W-319) — jak wygląda pełny stack |

### `narzedzia/rag/` — OFFICINA — warsztat: pomiary, audyty, generatory, raporty

| Moduł | Rola (docstring modułu) |
|-------|--------------------------|
| `aestimator.py` | ⚖️ AESTIMATOR — Szacownik Wierności Biblioteki: mierzy, ILE GINIE po drodze |
| `ekstraktor.py` | Ekstraktor tekstu z formatów biblioteki (epub, pdf, azw3, mobi, djvu, md) |
| `indeksuj.py` | Bibliotheca-RAG: indeksacja ksiazek + encyklopedii + (opcjonalnie) dokumentow Imperium |
| `katalog.py` | Katalog książek jako SOCZEWKA nad RAG — wzbogaca wyniki wyszukiwania o metadane |
| `konwerter.py` | Konwerter/cache tekstu książek — auto-convert problematycznych formatów, raz, z zapisem |
| `mcp_server.py` | Bibliotheca-RAG MCP Server — wystawia narzedzie `biblioteka_szukaj` dla Claude Code |
| `metadane_ksiag.py` | Metadane Ksiąg (Bibliotheca Ulpia) — strukturalny katalog książek dla RAG i katalogu |
| `norma.py` | 📐 NORMA — Węgielnica Bibliotekarza: bramka 10 kryteriów, którą MUSI przejść |
| `quaesitor.py` | 🔎 QUAESITOR — Śledczy Biblioteki: mierzy JAKOŚĆ WYSZUKIWANIA w Bibliotheca-RAG |
| `redditor.py` | 🧩 REDDITOR — Zwracający Całość: fragmentacja z KRYPTOGRAFICZNYM DOWODEM bezstratności |
| `szukaj.py` | Bibliotheca-RAG: wyszukiwanie semantyczne + FTS |

<!-- CENSUS:koniec -->
