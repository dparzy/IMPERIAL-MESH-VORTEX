---
kategoria: TABULA
typ: zywy
wlasciciel: imperium/legiony/rejestr.py
stan_na: 2026-07-18
powod_istnienia: "Master Index — punkt wejścia i mapa wszystkich dokumentów; sekcja katalogu generowana przez Tabularium"
---
# 👑 IMPERIUM — MASTER INDEX

```
██╗███╗   ███╗██████╗ ███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
██║████╗ ████║██╔══██╗██╔════╝██╔══██╗██║██║   ██║████╗ ████║
██║██╔████╔██║██████╔╝█████╗  ██████╔╝██║██║   ██║██╔████╔██║
██║██║╚██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
██║██║ ╚═╝ ██║██║     ███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

> **"Non numeris, sed intelligentia vincimus."**
> *(Nie liczbami, lecz inteligencją zwyciężamy.)*

---

| Właściwość       | Wartość                          |
|------------------|----------------------------------|
| **Projekt**      | IMPERIUM — AI Crypto Trading     |
| **Motto**        | Roma non est facta die una       |
| **Wersja**       | v0.9.0                           |
| **Faza**         | 🔄 Faza 1 — Namiestnik (Regime + Timeframe-Aware Gating) |
| **Data**         | 2026-06-09                       |
| **Giełda główna**| MEXC (konto zweryfikowane)       |
| **Rdzeń AI**     | DeepSeek LLM via API             |

> 📝 **ŻYWY DOKUMENT** — aktualizowany po każdej sesji pracy. Jeśli coś się zmienia w projekcie, ten plik zmienia się pierwszy.

---

## 🗺️ MAPA DOKUMENTÓW

Wszystkie dokumenty Imperium — **katalog GENEROWANY z nagłówków** dokumentów:
`python narzedzia/tabularium.py katalog --zapisz`. Nie edytuj tej sekcji ręcznie.

> **Dlaczego generowany (Prawo I):** ta sekcja, pisana ręcznie, twierdziła
> *„299 mikro-neuronów (72 w kodzie)”* przy **87** w kodzie — i przechodziła audyt
> na zielono, bo bramka W5 czytała liczbę z innej sekcji tego samego pliku. Ręczny
> indeks kłamie z definicji; generowany nie umie.
>
> **Kategorie (słownik zamknięty):** LEX (prawo) · TABULA (rejestr/źródło prawdy) ·
> FORMA (budowa organu) · DISCIPLINA (manual) · CONSILIUM (plan/wizja) ·
> MENSURA (pomiar) · ACTA (historia — prawda swojego czasu, Prawo I).
> Pole **właściciel** = plik kodu, za którym dokument ma nadążać (bramka gnicia T2).

<!-- TABULARIUM:start — sekcja generowana, NIE edytuj ręcznie -->

> 🏛️ Sekcja generowana przez `python narzedzia/tabularium.py katalog --zapisz` z nagłówków dokumentów. Ostatni spis: 2026-08-07 (76 pozycji).

### LEX — prawo i rozkazy stałe — obowiązuje, nie opisuje

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `CLAUDE.md` | Rozkazy stałe czytane na starcie KAŻDEJ sesji — konstytucja operacyjna Claude'a w Imperium | — | 2026-07-18 |
| `ZASADY_FUNDAMENTALNE.md` | 25 Praw Imperium — pełna konstytucja, do której odwołuje się każda decyzja | — | 2026-07-11 |
| `docs/CREDO_IMPERIUM.md` | Doktryna założycielska Cezara (verbatim) — serce, z którego wyrasta 25 Praw; źródło przy milczeniu prawa | — | 2026-07-07 |
| `docs/REGULAMINY_I_MANIPULACJE.md` | Zgodność z regulaminami giełd + katalog 7 manipulacji rynkowych do wykrywania — tarcza prawna Imperium | — | 2026-06-01 |
| `docs/WERSJONOWANIE.md` | Jedyne miejsce definiujące **system pieczęci IMV-ORI/ADO/INS/POR/EXP** (co jest naszym oryginałem, co adopcją, co przeniesieniem z Kingdom Pixel) oraz **protokół relegacji modułu** | — | 2026-07-15 |
| `docs/WZORZEC_OPISU.md` | ROZKAZ STAŁY: Zasada Pełnego Opisu (ZPO) — szablon i wymóg opisu zrozumiałego bez wiedzy eksperckiej | — | 2026-06-02 |

### TABULA — rejestr / źródło prawdy o kodzie — musi zgadzać się 1:1

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `README.md` | Wizytówka Imperium — podaje liczby wprost z kodu (neurony/testy/prawa), więc musi nadążać za rejestrem | `imperium/legiony/rejestr.py` | 2026-08-05 |
| `docs/CENSUS_ORGANORUM.md` | Spis WSZYSTKICH modulow imperium/ i narzedzia/ generowany z zywego kodu — zadny organ nie moze istniec bez meldunku; bramka Warstwy 17 audytu porownuje ten plik z kodem | `narzedzia/census_organorum.py` | 2026-08-05 |
| `docs/INDEKS_IMPERIUM.md` | Master Index — punkt wejścia i mapa wszystkich dokumentów; sekcja katalogu generowana przez Tabularium | `imperium/legiony/rejestr.py` | 2026-07-18 |
| `docs/MANIFEST_KODU.md` | JEDYNE oficjalne źródło prawdy o kodzie (Prawo XIX) — tabela kluczy ze statusem, nic nie istnieje bez wpisu tutaj | `imperium/legiony/rejestr.py` | 2026-08-05 |
| `docs/MAPA_KLUCZY.md` | JEDYNY dokument, który jawnie i systematycznie rozwiązuje rozbieżności między katalogiem (planem nazw/ID) a żywym kodem — dla każdego klucza podaje: nazwę klasy w kodzie, co robi,  | `imperium/legiony/rejestr.py` | 2026-07-16 |
| `docs/MAPA_PAMIECI.md` | Jedyne miejsce konsolidujące 13(+1 nadrzędny=W7) warstw pamięci Claude/Imperium w jedną taksonomię, z mapowaniem na model CoALA (arXiv:2309.02427) i na 'domknięte problemy granicy 2026 | `imperium/biblioteki/centrum_pamieci.py`, `imperium/biblioteki/dziennik_niesmiertelny.py`, `imperium/biblioteki/graf_pamieci.py`, `imperium/biblioteki/kronika_czatu.py`, `imperium/biblioteki/kustosz_pamieci.py`, `imperium/biblioteki/pamiec_absolutna.py`, `imperium/biblioteki/pamiec_proceduralna.py`, `imperium/biblioteki/pamiec_proweniencji.py`, `imperium/biblioteki/pamiec_robocza.py`, `imperium/biblioteki/pamiec_sesji.py`, `imperium/biblioteki/refleksja_pamieci.py`, `imperium/biblioteki/rejestr_wizji.py`, `imperium/biblioteki/srodowisko_pamieci.py`, `imperium/biblioteki/zapominanie.py` | 2026-08-04 |
| `docs/OBSERWATORZY.md` | Jedyny dokument mapujący WSZYSTKIE zewnętrzne źródła danych (44 źródła w 4 warstwach: OCZY/USZY/WIESZCZOWIE/SZPIEDZY) do konkretnych neuronów i modułów — z priorytetami kluczy API  | `imperium/akwedukty/bary_zdarzeniowe.py`, `imperium/akwedukty/czytnik_csv.py`, `imperium/akwedukty/klasyfikator_zdarzen.py`, `imperium/akwedukty/kwatermistrz_danych.py`, `imperium/akwedukty/news_fetcher.py`, `imperium/akwedukty/sentyment_historyczny.py`, `imperium/drogi/nexus_hub.py` | 2026-07-17 |
| `docs/PAMIEC_SESJI.md` | Mapa podpięć 13 warstw pamięci + lekcje — ciągłość między sesjami (W-360) | `imperium/biblioteki/pamiec_sesji.py` | 2026-08-06 |
| `docs/PROFIL_CEZARA.md` | Trwały model Cezara (preferencje, decyzje stałe) + źródło prawdy Imion Imperium — wstrzykiwany na starcie | `imperium/biblioteki/pamiec_sesji.py` | 2026-07-13 |
| `docs/README.md` | Wskaźnik na katalog dokumentów — sam spisu NIE trzyma; kieruje do generowanego katalogu w INDEKS_IMPERIUM (jedno źródło prawdy, Prawo XVI). | `narzedzia/tabularium.py` | 2026-07-27 |
| `docs/REJESTR_INSPIRACJI.md` | Jedno źródło prawdy o zewnętrznych inspiracjach AI/ML (ZPO: pełna nazwa + link + status weryfikacji) | `narzedzia/audyt_spojnosci.py` | 2026-07-16 |

### FORMA — opis budowy organu — jak moduł jest zbudowany

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `docs/ARCHITEKTURA_IMPERIUM.md` | Jedna strona spinająca 25 Praw z realnym kodem — jedyne miejsce z tabelą 'dzielnica → plik → rola → prawa' + diagram przepływu sygnału + mapowanie warstw architektury na źródła bib | `imperium/akwedukty/kwatermistrz_danych.py`, `imperium/biblioteki/codex_notarum.py`, `imperium/biblioteki/index_falsorum.py`, `imperium/swiatynie/praetorium.py`, `imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py`, `imperium/biblioteki/kronikarz.py`, `imperium/biblioteki/mnemosyne.py`, `imperium/biblioteki/notarius.py`, `imperium/cesarz/titan_mind.py`, `imperium/drogi/nexus_hub.py`, `imperium/fundament/brama_kalkulatora.py`, `imperium/fundament/kuznia_narzedzi.py`, `imperium/koloseum/backtest.py`, `imperium/koloseum/haruspex.py`, `imperium/koloseum/monte_carlo.py`, `imperium/koloseum/walidacja.py`, `imperium/koloseum/walk_forward.py`, `imperium/legiony/pierwszy_zwiadowca.py`, `imperium/legiony/roj_sygnalow.py`, `imperium/oczy/censor_sprzetu.py`, `imperium/oczy/wszechoko.py`, `imperium/pretorianie/aegis_tarcza.py`, `imperium/pretorianie/lustro_prawdy.py`, `imperium/senat/meta_kora.py`, `imperium/swiatynie/kartograf.py`, `imperium/swiatynie/specula_swiec.py`, `imperium/swiatynie/web_dashboard.py` | 2026-07-19 |
| `docs/DORADCY_CARA.md` | Jedyny dokument opisujący 'drugą opinię' Cesarza — radę 5 doradców (Oracle/Fulmen/Iustitia/Hermes/Pythia) oceniających każde wejście niezależnie od Legatusa i Senatu | `imperium/cesarz/doradcy/fulmen.py`, `imperium/cesarz/doradcy/hermes.py`, `imperium/cesarz/doradcy/iustitia.py`, `imperium/cesarz/doradcy/oracle.py`, `imperium/cesarz/doradcy/pythia.py`, `imperium/cesarz/doradcy/rada.py` | 2026-07-17 |
| `docs/GENERAL_LEGATUS.md` | Jedyny dokument opisujący rolę koordynatora między 4 Legionami a Senatem — algorytm agregacji sygnałów (5 kroków), klasyfikację reżimu rynku, dynamiczne wagi reżimowe, i integrację | `imperium/legiony/legatus.py` | 2026-07-17 |
| `docs/GUBERNATOR.md` | Jedyny dokument opisujący homeostatyczny sterownik globalnej ekspozycji CAŁEGO portfela (5 par naraz) — odróżnia się od innych warstw regulacji (HedgeMWU=per-neuron, Synapsy Reżimo | `imperium/koloseum/gubernator.py`, `tests/test_gubernator.py` | 2026-06-16 |
| `docs/IGRZYSKA_IMPERIUM.md` | Jedyny dokument opisujący system rywalizacji/rang dla neuronów (Cursus Honorum Neuronalis) — mechanizm nagród/kar, automatyczną kalibrację wag, oraz online-learning HedgeMWU (W-049) | `imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py` | 2026-07-18 |
| `docs/KALKULATOR_LEWARA.md` | Jedyny dokument z pełną 'matematyką przeżycia' pozycji lewarowanej — od ceny likwidacji przez stop-loss, dynamiczną dźwignię, zarządzanie kapitałem (2%), take-profit, checklist Pretorianów | `imperium/pretorianie/kalkulator_lewara.py` | 2026-08-04 |
| `docs/LEGIONY_ARCHITEKTURA.md` | Kanoniczne źródło nazewnictwa 4 Legionów (rzymskie nazwy: Legio X Equestris/Scalp, XII Fulminata/Swing, III Augusta/Invest, VI Ferrata/Leverage) + przypisanie konkretnych ID neuron | `imperium/legiony/mikro_neuron.py`, `imperium/legiony/neurony/dzwignia.py`, `imperium/legiony/neurony/momentum.py`, `imperium/legiony/neurony/onchain.py`, `imperium/legiony/neurony/struktura.py`, `imperium/legiony/neurony/trend.py`, `imperium/legiony/neurony/wolumen.py` | 2026-07-17 |
| `docs/MATRYCA_KORELACJI.md` | Koncepcyjny 'szablon Kostki Rubika' — pięcioosiowy system klasyfikacji sygnałów (Wskaźnik×Interwał×Typ zagrania×Reżim×Waga) jako przyszła mapa do wypełnienia realnymi danymi w 'Faz | `imperium/legiony/diagnostyka_korelacji.py`, `imperium/legiony/rejestr.py` | 2026-07-17 |
| `docs/NAMIESTNIK.md` | Jedyny dokument opisujący 'Gating Network' (sieć bramkującą) świadomą reżimu I interwału — meta-kontroler ustawiający parametry (tryb, lewar, próg, styl) dla reszty łańcucha decyzyjnego | `imperium/koloseum/namiestnik.py`, `tests/test_namiestnik.py` | 2026-07-18 |
| `docs/PAMIEC_ABSOLUTNA.md` | Jedyny dokument opisujący schemat rekordu `ImperiumLog` (atomowa jednostka pamięci transakcyjnej — Warstwa 1 pamięci) wraz z realnym API zapisu/odczytu i jawną listą luk wobec deklaracji Prawa IX. | `imperium/biblioteki/pamiec_absolutna.py`, `imperium/biblioteki/kronikarz.py` | 2026-07-17 |

### DISCIPLINA — manual — jak coś zrobić krok po kroku

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `docs/MANUAL_CLAUDE_CODE.md` | Jedyny dokument opisujący, jak Cezar instaluje i obsługuje samo narzędzie Claude Code (Node/npm, logowanie Pro, hooki, MCP, skróty, plan mode) — czyli warstwę „jak rozmawiać z Vitruviuszem | `narzedzia/audyt_spojnosci.py`, `tests/run_tests.py` | 2026-07-17 |
| `docs/MANUAL_DODAWANIE_AGENTOW.md` | Jedyny dokument rozróżniający DWA znaczenia „agenta' (Doradca Imperium = moduł Python w ścieżce decyzyjnej vs subagent Claude Code = plik .md) i dający wzorzec dodania każdego z ni | `imperium/cesarz/doradcy/fulmen.py`, `imperium/cesarz/doradcy/hermes.py`, `imperium/cesarz/doradcy/iustitia.py`, `imperium/cesarz/doradcy/oracle.py`, `imperium/cesarz/doradcy/pythia.py`, `imperium/cesarz/doradcy/rada.py`, `tests/test_doradcy.py` | 2026-06-20 |
| `docs/MANUAL_MIGRACJA_I_SYMULATOR.md` | Dwie rzeczy, których nie ma nigdzie indziej: (1) obalenie mitu „CHIMERA/HAMACHERA' — jawny wpis Prawa I, że moduł NIE istnieje; (2) ŚCIEŻKA PIENIĘDZY — krok po kroku matematyka roz | `imperium/fundament/brama_kalkulatora.py`, `imperium/koloseum/dyrygent.py`, `imperium/koloseum/namiestnik.py`, `imperium/legiony/legatus.py`, `imperium/pretorianie/kalkulator_lewara.py`, `tests/test_doradcy.py` | 2026-07-17 |
| `docs/MANUAL_UZYTKOWNIKA.md` | Jedyny kompletny przewodnik „od zera do paper tradingu' dla nowicjusza — instalacja Python/TA-Lib, tryby PAPER/DRY-RUN/REAL, pełna tabela pól `KonfigPetliLive`, TradingView+ngrok k | `imperium/akwedukty/bary_zdarzeniowe.py`, `imperium/koloseum/petla_live.py`, `imperium/legiony/feature_importance.py`, `imperium/legiony/meta_labeling.py`, `imperium/legiony/triple_barrier.py`, `narzedzia/audyt_spojnosci.py`, `tests/run_tests.py` | 2026-07-18 |
| `docs/NAZWY_PLIKOW_BIB-070+.md` | Gotowa do skopiowania lista nazw plików (konwencja `BIB-XXX_Autor_Tytul.ext`) dla całej listy BIB-070..306, żeby Cezar mógł szybko nazwać pobrane pliki bez przepisywania z tabel PL | `narzedzia/przygotuj_biblioteke.py` | 2026-07-28 |
| `docs/PAPER_TRADING_MEXC.md` | Jedyne miejsce z **kryteriami zaliczenia Etapu II** (Sharpe≥1.0, MaxDD<15%, DSR≥0.95, WR≥55% lub PF>1.5, ≥100 trades) i drabiną Etapów II→IIb→III→IV. Ta bramka „kiedy wolno przejść | `imperium/koloseum/backtest.py`, `imperium/koloseum/paper_trading.py`, `imperium/koloseum/petla_live.py`, `imperium/koloseum/walidacja.py` | 2026-07-17 |
| `docs/SCHOLA_CAESARIS.md` | Szkoła Cezara — lekcje wywiedzione z WŁASNYCH pomiarów Imperium, nie z podręczników. Cezar uczy się razem z Imperium, a każda lekcja rodząca twierdzenie sprawdzalne dostaje status i pomiar. | `imperium/biblioteki/schola.py` | 2026-07-29 |
| `docs/SCIAGA_LOKAL.md` | Jedyna „jedna kartka' z KOMPLETEM realnych komend lokalnych ułożonych w kolejności użycia — i jedyne miejsce z sekcjami 2c (oszczędzanie tokenów: świeży start zamiast wznawiania),  | `imperium/biblioteki/centrum_pamieci.py`, `imperium/biblioteki/dziennik_niesmiertelny.py`, `imperium/biblioteki/kronika_czatu.py`, `imperium/cesarz/deepseek_glos.py`, `narzedzia/ab_pnl_wazenie_ic.py`, `narzedzia/ab_wazenie_ic.py`, `narzedzia/arena_mcp.py`, `narzedzia/arena_zasil.py`, `narzedzia/backtest_dashboard.py`, `narzedzia/hipoteza_b.py`, `narzedzia/pobierz_4h_binance.py`, `narzedzia/pobierz_makro.py`, `narzedzia/pobierz_nowe_pary.py`, `narzedzia/przygotuj_biblioteke.py`, `narzedzia/rag/mcp_server.py`, `narzedzia/raport_ic.py`, `narzedzia/raport_waznosci.py`, `narzedzia/scoreboard_neuronow.py`, `narzedzia/status.py`, `narzedzia/walidacja_kalibrator.py`, `narzedzia/walk_forward_ic.py`, `narzedzia/wykres_backtestu.py`, `skrypty/start.py`, `skrypty/start_lokal.py` | 2026-07-17 |
| `docs/START_LOKAL.md` | Jedyne miejsce z tabelą porównawczą **chmura vs lokal** (co lokal DODAJE: wektory semantyczne, pełny dysk przez MCP, trwałe logi W1, DeepSeek) oraz jedyne, które promuje `aktualizu | `imperium/biblioteki/kustosz_pamieci.py`, `narzedzia/audyt_spojnosci.py`, `narzedzia/auto_lekcja.py`, `narzedzia/rag/indeksuj.py`, `skrypty/start.py`, `skrypty/start_lokal.py`, `tests/run_tests.py` | 2026-07-17 |
| `docs/ZADANIE_TIRO_E3_ZNIWO.md` | Pakiet zadań LOKALNYCH domykających TIRO E3 (pierwszy A/B ucznia) i żniwo par nauczyciela — chmura nie ma ani książek, ani klucza DeepSeek, więc tej pracy nie da się wykonać zdalnie | `imperium/biblioteki/notarius.py`, `narzedzia/bibliotekarz.py` | 2026-07-26 |
| `imperium/INSTRUKCJA_URUCHOMIENIA.md` | Instrukcja uruchomienia minimalnego cyklu Fazy 0 (pierwszy_zwiadowca) krok po kroku dla nowicjusza (Windows, tryb paper) | `imperium/legiony/pierwszy_zwiadowca.py` | 2026-07-18 |
| `imperium/README.md` | Mapa organów rzymskich w kodzie (folder → rola → moduły) — pierwszy dokument czytany przy wejściu w imperium/ | `imperium/legiony/rejestr.py` | 2026-05-31 |
| `narzedzia/rag/SETUP_LOKALNY.md` | Instrukcja włączenia pełnej mocy RAG lokalnie (FTS5 od ręki, wektory opcjonalnie) | `narzedzia/rag/indeksuj.py` | 2026-07-18 |
| `skrypty/README.md` | Spis skryptów startowych i ich komend — punkt wejścia dla Cezara | `skrypty/start.py` | 2026-06-20 |

### CONSILIUM — plan / wizja — zamiar na przyszłość, nie fakt

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `docs/INGENIUM_IQ_IMPERII.md` | Projekt organu INGENIUM — mierzalny wskaźnik rozwoju Imperium (IQ IMPERII): 7 kategorii liczonych z kodu i ledgerów, nie z deklaracji. Zamiar Cezara z 2026-07-29, nie fakt — kod jeszcze nie istnieje | `imperium/oczy/censor_sprzetu.py` | 2026-07-29 |
| `docs/KATALOG_NEURONOW.md` | Katalog 299 zmapowanych mikro-neuronów jako roadmapa (87 zbudowanych) — zamiar, nie stan kodu; stan mówi MANIFEST | `imperium/legiony/rejestr.py` | 2026-07-17 |
| `docs/KATALOG_STRATEGII.md` | Katalog zmapowanych strategii jako roadmapa (20 w kodzie) — zamiar; stan kodu mówi MANIFEST | `imperium/legiony/strategie/rejestr_strategii.py` | 2026-06-26 |
| `docs/ODLOZONE_DECYZJE.md` | Rejestr rzeczy ustalonych merytorycznie, ale świadomie odłożonych do czasu twardego pomiaru A/B (zasada 'nie wdrażamy bo brzmi dobrze — wdrażamy gdy A/B pokaże plus'). | `narzedzia/ab_w329.py`, `narzedzia/ab_w334_progi.py`, `narzedzia/ab_w335_cross_rs.py`, `narzedzia/ab_w336_changepoint.py` | 2026-07-17 |
| `docs/PLAN_DEEPSEEK.md` | Plan podłączenia DeepSeek API jako 'głosu' Imperium (adapter GlosImperium) + weryfikacja, GDZIE DeepSeek naprawdę trafił — realizacja poszła inną drogą niż plan (nie Senat, lecz Oczy/newsy + zwiad wiedzy + NOTARIUS). | `imperium/cesarz/deepseek_glos.py`, `imperium/akwedukty/adaptery/news_llm.py`, `imperium/biblioteki/notarius.py` | 2026-07-18 |
| `docs/PLAN_ROZBUDOWY_BIBLIOTEKI.md` | PEŁNY spis biblioteki Imperium: 307 pozycji (BIB-001..307) — 69 posiadanych fundamentów, 234 pozycje rozbudowy, każda ze statusem posiadania i obecności w RAG. | `narzedzia/bibliotekarz.py`, `narzedzia/przygotuj_biblioteke.py` | 2026-07-28 |
| `docs/PLAN_TIRO_LOKALNY_LLM.md` | Zbudować lokalny hybrydowy LLM 'TIRO' (uczeń), trenowany metodą destylacji od nauczyciela DeepSeek (Hyginus), z docelowym celem przejęcia ról LLM w Imperium bez kosztów API. | `imperium/biblioteki/notarius.py`, `imperium/oczy/censor_sprzetu.py`, `imperium/swiatynie/web_dashboard.py` | 2026-08-04 |
| `docs/ROADMAP_IMPERIUM.md` | Mapa dróg rozwoju systemu w 5 fazach (0-4), od pierwszego cyklu paper trading do pełnej autonomii. | — | 2026-08-06 |
| `docs/TRYBY_IMPERIUM.md` | Jedyne miejsce z **twardym, zmierzonym werdyktem o interwale 1H** — że rój nie ma na nim dodatniego edge'u i że zaostrzanie progów asymptotuje przy ~−2.5%, nigdy nie przekraczając zera | `imperium/koloseum/namiestnik.py`, `narzedzia/kalibracja_1h.py`, `narzedzia/kalibracja_1h_v2.py`, `narzedzia/sym_porownanie_tf.py` | 2026-07-21 |
| `docs/WIZJA_KSIEGI_SYBILLINSKIE.md` | Zbudować rejestr falsyfikowalnych proroctw Imperium o samym sobie (np. 'P=0.70: neuron X osiągnie IC≥0.02'), rozliczanych automatycznie z bazy areny — mierzy nie PnL, ale samowiedz | `imperium/biblioteki/ksiegi_sybillinskie.py` | 2026-07-06 |
| `docs/WIZJA_LEGIONY_CIENI.md` | Kontrfaktyczne Kolosseum — równolegle do realnej decyzji Imperium maszerują 'Legiony Cieni' (widmowe warianty konfiguracji: bez weta, próg łagodny, próg surowy), mierzące ile koszt | `imperium/koloseum/legiony_cieni.py`, `narzedzia/raport_zalu.py` | 2026-07-06 |
| `docs/WIZJA_TRYBY_I_ROZWOJ.md` | Wizja Cezara na 3 tryby operacyjne systemu (NAJLEPSZY/BILANS/OBRONA) plus katalog darmowych API do 'prześwietlania' nowych walut przed wejściem — z weryfikacją, co z wizji już stoi w kodzie | `imperium/koloseum/skaner_okazji.py`, `imperium/legiony/rejestr.py` | 2026-07-17 |
| `docs/WIZJONER.md` | Zbiór wizji i kierunków rozwoju — zamiary na przyszłość, świadomie niezrealizowane | — | 2026-06-26 |
| `docs/WZORZEC_DNSS.md` | Punkt odniesienia: analiza zewnętrznego roju 79 agentów (DNSS) — dowód, że wizja jest osiągalna, i poprzeczka do przebicia | — | 2026-06-02 |
| `docs/ZWIAD_ZAPYTANIA.md` | Gotowe frazy wyszukiwania dla Cezara — zwiad po literaturze celowany w ZMIERZONE luki Imperium, z kryterium oceny trafienia i listą tego, czego NIE szukać. | — | 2026-08-02 |

### MENSURA — pomiar / analiza z danych — wynik, nie opinia

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `docs/ANALIZA_HERMES_I_PAMIEC.md` | Odpowiedzieć Cezarowi czy Imperium ma pamięć porównywalną do 'Hermes Agent' (odkryto że to DWIE różne rzeczy — jedna to fabrykacja INF-32, druga to realny produkt Nous Research), p | `imperium/biblioteki/arena_trzech_bram.py`, `imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py`, `imperium/biblioteki/kronikarz.py`, `imperium/biblioteki/kronikarz_zdarzen.py`, `imperium/biblioteki/mnemosyne.py`, `imperium/biblioteki/pamiec_absolutna.py`, `imperium/biblioteki/synapsy_rezimowe.py` | 2026-06-20 |
| `docs/ANALIZA_NEURONY_SCALP_SWING_INVEST.md` | Porównać co Imperium MA z najlepszymi praktykami scalp/swing/invest z internetu, znaleźć zdekorelowane luki, i ZMIERZYĆ (nie założyć) czy nowe neurony realnie pomagają | `imperium/koloseum/namiestnik.py`, `imperium/legiony/rejestr.py`, `narzedzia/ab_w322.py`, `narzedzia/dekorelacja_w322.py` | 2026-07-17 |
| `docs/POMIAR_FILTR_ASYMETRII.md` | Zmierzyć (Prawo XVI, nie zgadywać) czy Filtr Asymetrii Reżimu (W-314) faktycznie redukuje straty w rynku bocznym (ADX niski) — odkryty rozdźwięk in-sample vs OOS (in-sample +26k$ h | `imperium/koloseum/dyrygent.py`, `imperium/pretorianie/filtr_asymetrii.py` | 2026-06-13 |
| `docs/POMIAR_WARSTW_ADAPTACYJNYCH.md` | Ablacja (Prawo XVI) czterech warstw adaptacyjnych — zmierzyć która faktycznie poprawia wynik w backteście in-sample na 5 parach, 4H. | `imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py`, `imperium/biblioteki/ksiega_wad_kodu.py`, `imperium/biblioteki/synapsy_rezimowe.py` | 2026-06-13 |

### ACTA — datowana historia — prawda swojego czasu (Prawo I: nie tykamy)

| Dokument | Po co istnieje | Właściciel (kod) | Stan na |
|---|---|---|---|
| `docs/ARSENAL_IMPERIUM.md` | Zweryfikować (Prawo I: zero halucynacji) setki linków narzędzi z pliku źródłowego IMV, oddzielić realne od fabrykowanych/niepewnych, i zaproponować 'najmocniejszy zweryfikowany rdz | — | 2026-06-02 |
| `docs/AUDYT_SYSTEMU.md` | Pierwszy głęboki audyt stanu faktycznego systemu — co działa, co blokowane przez TA-Lib, co jest szkieletem, co brakuje całkowicie. | `imperium/cesarz/deepseek_glos.py`, `imperium/legiony/mikro_neuron.py`, `imperium/senat/meta_kora.py` | 2026-06-12 |
| `docs/LOG_ZMIAN.md` | Żywa pamięć projektu: chronologia KAŻDEJ zmiany (ROZKAZ STAŁY). Wpisy datowane = prawda swojego czasu, nie aktualizujemy wstecz | — | 2026-08-06 |
| `docs/MAPA_IMPERIUM_FLOW.md` ⛔ zastąpiony przez `docs/ARCHITEKTURA_IMPERIUM.md` | Wersja narracyjna/dydaktyczna architektury — dla nowicjusza (Cezara): tłumaczy PO CO każdy organ istnieje, z przykładowym dialogiem (Zwiadowca 1 mówi 'DŁUGO...', Frakcja Byków vs N | `imperium/akwedukty/kwatermistrz_danych.py`, `imperium/biblioteki/kronikarz.py`, `imperium/biblioteki/mnemosyne.py`, `imperium/cesarz/titan_mind.py`, `imperium/drogi/nexus_hub.py`, `imperium/fundament/brama_kalkulatora.py`, `imperium/fundament/kuznia_narzedzi.py`, `imperium/koloseum/backtest.py`, `imperium/koloseum/monte_carlo.py`, `imperium/legiony/pierwszy_zwiadowca.py`, `imperium/legiony/roj_sygnalow.py`, `imperium/pretorianie/aegis_tarcza.py`, `imperium/pretorianie/lustro_prawdy.py`, `imperium/senat/meta_kora.py`, `imperium/swiatynie/kartograf.py`, `imperium/swiatynie/web_dashboard.py` | 2026-05-31 |
| `docs/PAMIEC_SESJI_ARCHIWUM.md` | Magazyn starszych/mniej połączonych lekcji — pamięć aktywna ostra, nic nie tracimy (Prawo I). Przeszukiwalne (grep/RAG), poza wstrzykiwanym kontekstem startowym. | — | 2026-07-19 |
| `docs/SKAN_AZJA.md` | Głęboki skan pliku źródłowego `archiwum/Azjatycki_skan_rynku_3100_links.md` (7106 linii) przez 'cztery legiony zwiadowców', żeby wyłowić perełki (nowe neurony/strategie/architektur | — | 2026-06-01 |
| `docs/migawki/ANALIZA_AUTODOBOR_STRATEGII_2026-07-13.md` | Zwiad wiedzy (Bibliotheca Ulpia RAG 27641 fragmentów + internet) w celu ulepszenia auto-doboru strategii — zdiagnozowana luka: dobór strategii ignoruje zrealizowany P&L (czysto str | `imperium/legiony/strategie/baza.py` | 2026-07-13 |
| `docs/migawki/ANALIZA_BIB_043-069_2026-07-11.md` | Mapowanie 27 nowych książek (BIB-043..069) na działy encyklopedii Imperium i konkretne moduły/neurony — ugruntowane w realnej treści (ekstrakcja TOC+wstęp), nie z pamięci. | `imperium/pretorianie/filtr_ekonomiczny.py` | 2026-07-11 |
| `docs/migawki/ANALIZA_WRZUTNIA_2026-07-10.md` | Destylat 108 par pytanie-odpowiedź z DeepSeek Chat (`wrzutnia/Mapa-kluczy.md`) — separacja tego co już mamy (Sekcja A), rad błędnych do odrzucenia (Sekcja B), realnych nowości rank | `imperium/cesarz/deepseek_glos.py`, `imperium/koloseum/drift_adapter.py`, `imperium/legiony/kalibrator_konformalny.py`, `imperium/legiony/meta_labeling.py`, `imperium/legiony/neutralizacja.py`, `imperium/pretorianie/filtr_ekonomiczny.py` | 2026-07-10 |
| `docs/migawki/ANALIZA_WRZUTNIA_2026-07-12.md` | Kontynuacja żniwa wrzutni (po ANALIZA_WRZUTNIA_2026-07-10) — 6 nieprzerobionych tur z 12 lipca, z web-weryfikacją KAŻDEGO cytowania (lekcja RE_AUDYT 07-13 zastosowana w praktyce: 5 | — | 2026-07-15 |
| `docs/migawki/AUDYT_GLEBOKI_2026-06-14.md` | Głęboki audyt 4-frontowy reframujący ocenę systemu jako 'łowcy okazji wielowalutowego' (nie backtestu jednej waluty) — mapuje co z tej wizji istnieje w kodzie, a czego brakuje (luk | `imperium/biblioteki/kronikarz_zdarzen.py`, `imperium/koloseum/namiestnik.py`, `imperium/koloseum/skaner_okazji.py`, `imperium/legiony/radar_rynku.py`, `imperium/pretorianie/praeda.py` | 2026-06-14 |
| `docs/migawki/AUDYT_IMPERIUM_2026-07-05.md` | Pełny audyt na prompt Cezara: stan faktyczny (liczby z kodu), ocena silnika pomiarowo-walidacyjnego, uczciwe porównanie z konkurencją, nazwane luki, i 5 propozycji unikatowych ulep | `imperium/cesarz/titan_mind.py`, `imperium/fundament/kuznia_narzedzi.py`, `imperium/legiony/roj_sygnalow.py`, `imperium/senat/meta_kora.py` | 2026-07-05 |
| `docs/migawki/NEWS_ROZBUDOWA_2026-06-30.md` | Audyt NEWS-01 + sweep światowego rynku danych newsowych + propozycje 10 nowych modułów rozszerzających system newsowy, z jawnym statusem wykonania każdego (✅ ZROBIONE / 🔵 plan) już | `imperium/akwedukty/adaptery/news_llm.py`, `imperium/akwedukty/news_fetcher.py`, `imperium/legiony/neurony/news_dynamika.py` | 2026-06-30 |
| `docs/migawki/PLON_HYGINUSA_2026-07-14.md` | Pierwszy realny bieg Hyginusa (DeepSeek) po komplecie ulepszeń U1-U4 (query-expansion + self-critique + świadomość systemu) — Vitruviusz (Opus) jako sędzia ocenia 4 tematy/kandydat | — | 2026-07-14 |
| `docs/migawki/RESEARCH_NOWE_KATEGORIE_2026-06-17.md` | Głęboki research 6-kątowy (APAC, konkursy quant, repozytoria, prace naukowe, patenty, książki) mający zidentyfikować nowe kategorie sygnałów zdekorelowane z istniejącymi 72 neurona | `imperium/legiony/meta_labeling.py`, `imperium/legiony/neurony/przekroj.py`, `imperium/legiony/neutralizacja.py` | 2026-06-17 |
| `docs/migawki/RE_AUDYT_WERYFIKACYJNY_2026-07-13.md` | Naprawa błędu procesu: Claude odrzucał/wątpił w realne, świeże (post-styczeń-2026) technologie/prace bez weryfikacji WebSearch, bo oceniał z pamięci zamiast sprawdzić internet. | — | 2026-07-13 |

<!-- TABULARIUM:koniec -->

## 🏛️ MAPA KODU

Struktura katalogów projektu — co gdzie mieszka i w jakim stanie.

| Katalog | Rola w Imperium | Moduł | Status |
|---------|-----------------|-------|--------|
| `imperium/akwedukty/` | Rurociąg danych — pobieranie świec z MEXC przez CCXT | Akwedukty (Data Pipeline) | ✅ Gotowy |
| `imperium/fundament/` | Brama Kalkulatora — TA-Lib oblicza wskaźniki, SHA-256 podpisuje | Calculator Gate | ✅ Gotowy |
| `imperium/legiony/` | Legiony — mikro-neurony (87), Legatus, zwiadowcy (15), strategie (20) | Scout Legions | ✅ Rdzeń aktywny |
| `imperium/pretorianie/` | Pretorianie — weto ryzyka, ochrona kapitału | Risk Praetorians | ✅ Gotowy |
| `imperium/senat/` | Senat — debata Popularów vs Optymantów nad sygnałem | Senate Debate | 🟡 Szkielet |
| `imperium/cesarz/` | Cesarz — DeepSeek LLM podejmuje ostateczną decyzję | Emperor (LLM) | 🟡 Szkielet |
| `imperium/drogi/` | Drogi — wykonanie zlecenia na MEXC (Via Romana) | Order Execution | 🟡 Szkielet |
| `imperium/biblioteki/` | Biblioteki — **kronikarz.py** (logi) + **mnemosyne.py** (pamięć transakcji) + **pamiec_absolutna.py** (ImperiumLog, MAE/MFE, JSONL) + **igrzyska.py** (ranking batch) + **hedge_mwu.py** (online MWU, W-049) + **arena_trzech_bram.py** (potrójna bariera, W-035) + **kronikarz_zdarzen.py** (event-study, W-289 💎) + **synapsy_rezimowe.py** (Regime-Aware Decorrelated Coalition Graph, W-299 🧬) + **pamiec_sesji.py** (Pamięć Sesji — ciągłość między sesjami Claude, mapa+lekcje+CRUD+profil Cezara, W-360 🧠) + **kronika_czatu.py** (Kronika Czatu — destylacja CAŁYCH transkryptów do repo, przeszukiwalna, W-360 📜) + **centrum_pamieci.py** (Centrum Pamięci W-360 v4 — hub wszystkich warstw: scoring GA recency×importance×relevance×regime, szukaj_wszedzie 4-warstwowo W1+W3+W3b+W4, scoring kroniki recency×relevance, podsumowanie startowe 🧠) + **rejestr_wizji.py** (W4 — Rejestr Wizji i Decyzji: ustrukturyzowana pamięć WIZJI/DECYZJI/POMYSŁÓW/ZMIAN z pełnym scoringiem GA + reżimem + dedup, JSONL → git 📋) + **srodowisko_pamieci.py** (W5 Most Chmura↔Lokal — UNIKAT: pamięć środowiskowo-adaptacyjna; wykrywa chmura/lokal, raport dostępności warstw, manifest pamięci dla lokala po git pull, instrukcja odblokowania wektorów semantycznych 🌉) + **dziennik_niesmiertelny.py** (W6 Dziennik Nieśmiertelny — UNIKAT: dożywotnia ZWIĘZŁA oś czasu projektu; każda sesja = co zrobiono/decyzje/następny krok; wstrzykiwana W CAŁOŚCI na starcie → pełna widoczność łuku projektu, koniec „cofania się"; wyszukiwarka kroniki naprawiona na token-based ♾️) + **kustosz_pamieci.py** (W7 Kustosz Pamięci — NADRZĘDNY ORGAN, UNIKAT: zarządza 7 warstwami; katalog nadrzędny anti-blindness, kompresja zimnej warstwy .md.gz wciąż przeszukiwalna (zmierzone 22×), census wszystkich warstw, routing zapytań; pamięć bezgraniczna przez git + bounded context 👑) + **graf_pamieci.py** (W8 Graf Pamięci — POŁĄCZENIA NEURONÓW, UNIKAT: temporalny graf wiedzy à la Zep/Graphiti arXiv:2501.13956; węzły=encje, krawędzie=współwystąpienia z oknem czasowym; polaczenia/centralne-huby/sciezka-BFS; budowany z Dziennika+wizji+lekcji deterministycznie 🕸️) + **refleksja_pamieci.py** (W9 Refleksja — SPRZECZNOŚCI+PRZEDAWNIENIE, UNIKAT: trustworthy reflection wg granicy 2026 arXiv:2603.07670; wykrywa rozstrzygnięcia/sprzeczności decyzji w czasie + wiszące pomysły; ZASADA anty-utrwalania — tylko zgłasza, nigdy nie kasuje, Cezar decyduje 🪞) + **zapominanie.py** (W10 Mądre Zapominanie — LEARNED FORGETTING, UNIKAT: zapominanie wartościowe nie czasowe; retencja=ważność×świeżość×łączność_w_grafie, plany chronione; proponuje schłodzenie do zimnej warstwy W7, NIGDY nie kasuje — safe forgetting wg granicy 2026 🍂) + **pamiec_proceduralna.py** (W11 Pamięć Proceduralna — taksonomia CoALA arXiv:2309.02427; runbooki JAK wykonać zadanie: dodać neuron, naprawić audyt, bezpieczny commit; szukaj po wyzwalaczach; upsert `zapisz()` leczy zgniłe runbooki 🛠️) + **sigillarium.py** (SIGILLARIUM — Skarbiec Pieczęci, SIGLA IMPERII: hasła-skróty `/apertio` `/clausura` `/limes` uruchamiające PEŁNE procedury; kroki NIE są przechowywane, tylko czytane z konstytucji `CLAUDE.md` w chwili wywołania (odebranie dokumentowi prawa do własnej treści — lekarstwo na gnicie z CENSUS ORGANORUM); karmi runbooki W11 przez `synchronizuj_w11()`, więc hasło działa też pisane zwykłym zdaniem; ujście w harnessie = cienkie `.claude/skills/*/SKILL.md` 🔏) + **pamiec_robocza.py** (W12 Pamięć Robocza — CoALA working memory; aktywny cel bieżącego cyklu z Dziennika W6 + pilne sygnały z W9; domyka pełną czwórkę CoALA: robocza+epizodyczna+semantyczna+proceduralna 🎯) + **pamiec_proweniencji.py** (W13 Pamięć Proweniencji — origin trail wg arXiv:2606.04990; „skąd to wiemy": ślad pochodzenia pojęcia w czasie przez wszystkie warstwy, geneza+ugruntowanie/temporal credit; provenance-aware retrieval 🔍) + **arena_baza.py** (Arena Baza — wspólna warstwa bazy wyników areny SQLite `arena_wyniki.db`; zapisz_pomiar/pytaj_pomiary; używane przez Arena MCP `narzedzia/arena_mcp.py` i opt-in auto-log pętli live; runtime per-maszyna 🏟️) + **ksiega_wad_kodu.py** (Księga Wad Kodu — pamięć wzorców błędów z recenzji cubic/self-review; `skanuj()` heurystycznie łapie powtórki znanych klas bugów; CLI `narzedzia/skan_wad_kodu.py` skanuje zmienione .py, wpięty w hook startowy; samo-leczenie Prawo XV 🐞) + **ksiegi_sybillinskie.py** (Księgi Sybillińskie — rejestr falsyfikowalnych PROROCTW Imperium o SOBIE: `dodaj`/`rozlicz`/`brier`/`krzywa_kalibracji`, JSONL→git niemutowalny; rozstrzyganie AUTOMATYCZNE z bazy areny (arena_baza) po horyzoncie; Brier score samowiedzy (G.W. Brier, Monthly Weather Review 1950); anty-oszustwo Prawo I — `rozlicz` NIGDY nie tyka P/twierdzenia; **zegar OFF** do decyzji Cezara; domyka trójcę kalibracji conformal(sygnały)→Cienie(decyzje)→Sybilla(przekonania) 🔮) + **notarius.py** (NOTARIUS — pisarz Imperium, surowiec Szkoły TIRO/E2: stenografuje pary `prompt→odpowiedź nauczyciela` przy KAŻDYM przejściu przez most `GlosImperium.zapytaj()`, więc jedno wpięcie łapie wszystkich wołających (newsy/auto-lekcje/zwiad) bez zmian u nich; ŻELAZNA ZASADA — awaria pisarza NIGDY nie wywraca wywołania API (wszystko łykane, łącznie z ImportError); dedup po CAŁEJ parze (ta sama odpowiedź = re-run, inna odpowiedź = wariancja nauczyciela = informacja); `eksportuj_sft()` → format `{"messages":[...]}` dla Unsloth/TRL/Axolotl (E4, Colab); pasek postępu do progów datasetu 500/1000/5000 (Prawo XXIV); wyłącznik `TIRO_NOTARIUS=0`; 🚨 nauczycielem wag może być WYŁĄCZNIE DeepSeek — ToS Anthropic/OpenAI zakazują trenowania na ich wyjściach, dlatego pisarz zna tylko most do DeepSeeka; obserwacja czysta, ZERO wpływu na ścieżkę decyzyjną 📜) | Logs & Memory & Learning | ✅ Gotowy |
| `imperium/swiatynie/` | Świątynie — wykresy, dashboard, wizualizacje | Charts & Dashboard | 🟡 Szkielet |
| `imperium/koloseum/` | Koloseum — PaperTradingEngine + **Dyrygent** (orkiestrator: bary→**Namiestnik**→Legatus→Kalkulator→pozycja) + **PętlaLive** (W-302 entrypoint live: DataLoader→Radar→cykl→PamięćRefleksyjna) + **Namiestnik** (Regime + Timeframe-Aware Gating) + **Backtest portfela** + **Detektor Lookahead-bias** (LA-01) + **LegionyCieni** (Kontrfaktyczne Kolosseum, `legiony_cieni.py` — 3 widmowe warianty bez_wet/prog_lagodny/prog_surowy na papierowych silnikach obok realnego roju; zamknięcia→arena `CIEN_PNL` = cena ostrożności i odwagi mierzona NA ŻYWO; opt-in `cienie=False`, faza 1 pomiar żalu; CFR Zinkevich et al. NeurIPS 2007 👥) | Backtesting Arena & Live | ✅ Cykl Faza 1 aktywny |
| `imperium/oczy/` | Oczy — newsy, sentyment, dane on-chain | News & Sentiment | 🔴 Planowany |

**Legenda:** ✅ Gotowy — działa produkcyjnie | 🟡 Szkielet — struktura istnieje, wypełnianie w toku | 🔴 Planowany — jeszcze nie rozpoczęty

---

## ⚖️ PRAWA IMPERIUM

Nienaruszalne zasady. Złamanie któregokolwiek Prawa = błąd architektoniczny.

**Prawo I — Lex Calculi**
> AI nie oblicza. Bramka oblicza (TA-Lib). AI interpretuje wyłącznie zweryfikowane liczby.

**Prawo II — Lex Unitatis**
> Jeden punkt wejścia dla danych. Jeden punkt wejścia dla LLM. Brak równoległych kanałów.

**Prawo III — Lex Sigilli**
> Każdy sygnał niesie dowód SHA-256 z Bramki. Sygnał bez pieczęci = sygnał odrzucony.

**Prawo IV — Lex Veto**
> Pretorianie mają WETO. Żadna pozycja bez ich zgody. Nawet Cesarz im nie rozkazuje.

**Prawo V — Lex Arcani**
> Klucze API NIGDY w kodzie. Wyłącznie zmienne środowiskowe. Zawsze.

**Prawo VI — Lex Kolossei**
> Każde nowe narzędzie testowane w Koloseum jako pierwsze. Nigdy prosto na live.

**Prawo VII — Lex Gradus**
> Budujemy stopniowo. Jeden neuron na raz. Pośpiech = chaos = straty.

**Prawo VIII — Lex Diversitatis**
> Bez zbędnego powielania. Każdy moduł pokrywa INNY kąt widzenia rynku.

**Prawo IX — Lex Memoriae**
> Nic nie ginie. Każda wiedza trafia do `docs/`. Dokumentacja jest częścią kodu.

---

## 🏺 GIEŁDY

| Giełda | Rola | Status konta | Faza |
|--------|------|--------------|------|
| **MEXC** | Giełda główna — wykonanie zleceń, pobieranie danych | ✅ Konto zweryfikowane | Faza 0+ |
| Inne (TBD) | Ekspansja — arbitraż między giełdami | 🔴 Planowane | Faza 2+ |

---

## ⚔️ LEGIONY

Cztery Legiony Zwiadowcze — każdy widzi rynek inaczej.

| # | Nazwa Łacińska | Styl (Namiestnik) | Timeframe | Lewar (cap) | Rynek | Specjalizacja |
|---|----------------|-------------------|-----------|-------------|-------|---------------|
| X | **Legio X — Equestris** | SCALP | M1–M15 | ≤10× | FUTURES | Szybkie ruchy, breakouty, wolumen |
| XII | **Legio XII — Fulminata** | SWING | 30M–4H | ≤5× | FUTURES/SPOT | Trend swing, RSI, struktura |
| XII/IMV | **Swing-Position** | SWING/INVEST | 4H–1D | ≤2–5× | OBA | Formacje, S/R, MTF bias |
| III | **Legio III — Augusta** | INVEST | 1D–1W | ≤2× | SPOT | Trendy makro, on-chain, cykl |

> **Timeframe-Aware (Namiestnik, 2026-06-03):** interwał → styl (SCALP/SWING/INVEST)
> automatycznie wyznacza sufit dźwigni, rynek (futures/spot) i korektę progu pewności.
> Strategie filtrowane po interwale (`dobierz_najlepsze(interwal=...)`).

> Szczegóły mikro-neuronów i schematu sygnałów → `LEGIONY_ARCHITEKTURA.md`

---

## 🗺️ NASTĘPNE KROKI

Priorytety w kolejności. Jedno zadanie na raz (Prawo VII).

### 🗺️ FAZY ROZWOJU — STAN REALIZACJI

| Faza | Zakres | Status | Neurony |
|------|--------|--------|---------|
| **A'** ✅ | Naprawa martwych głosów (XII-07, X-12, A-05) | ✅ ZREALIZOWANA 2026-06-02 | naprawione progi |
| **A** ✅ | Kat. **L** (VI-13 ATR-Lev, L-14 Ulcer) + **V** (V-13 RealizedVol, V-14 Choppiness) | ✅ ZREALIZOWANA 2026-06-03 | +4 neurony, kat. L=2, V=2 |
| **B** ✅ | AdapterFutures (Binance fapi public) → PSY-01/02/04 obudzone, kat. **R** żywa | ✅ ZREALIZOWANA 2026-06-03 | +4 neurony (PSY), 2 strategie VI-LV |
| **C** ✅ | AdapterCVD (Binance aggTrades public) → V-03 CVD obudzony | ✅ ZREALIZOWANA 2026-06-03 | +1 neuron (V-03 kat. F) |
| **D** 🔵 | OC-01..04 on-chain (MVRV, SOPR, Puell, Netflow) — wymaga klucza Glassnode/CryptoQuant | ⏳ OCZEKUJE — decyzja Cezara | +4 neurony (kat. O) |
| **LIVE** 🟠 | Paper trading na żywych danych MEXC — `MEXC_API_KEY` + `MEXC_SECRET` | ⏳ Instrukcja → `docs/PAPER_TRADING_MEXC.md` | rdzeń kompletny |
| **E** 🔵 | Dalsze neurony z katalogu (299−72=227 backlog) + Księga Azjatycka strategii | ⏳ Partiami, z dekorelacją | +? |

**Stan kategorii (2026-07-05):** A/C/D/F/H/K/L/M/N/O/R/S/T/V/Z · wyciszone: część O/S czeka na adaptery/feed
**Neurony: 87** (81 aktywnych, 6 wyciszonych) · **Strategie: 20** · **Testy: patrz `python tests/run_tests.py`** (nie hardkodujemy)

### Zadania bieżące (infrastruktura)
| # | Zadanie | Moduł | Priorytet |
|---|---------|-------|-----------|
| 1 | ⚡ Ustaw `DEEPSEEK_API_KEY` w zmiennych środowiskowych | Cesarz | 🔴 Krytyczny (LLM offline) |
| 2 | 🔌 Faza D: klucz Glassnode/CryptoQuant → kat. O ożywiona | Legiony/OC | 🔵 Średni |
| 3 | 🏛️ Paper Trading LIVE: `MEXC_API_KEY` + feed → pierwszy żywy cykl Dyrygenta | Drogi/Akwedukty | 🟠 Wysoki |

---

## 📡 SZYBKA DIAGNOSTYKA

```bash
# Sprawdź czy klucz DeepSeek jest ustawiony
echo $DEEPSEEK_API_KEY

# Test połączenia z DeepSeek
python imperium/cesarz/deepseek_glos.py

# Cenzus adapterów danych (MEXC/Binance/News — żywotność na żywo)
python narzedzia/cenzus_adapterow.py

# Test Bramki Kalkulatora
python imperium/fundament/brama_kalkulatora.py

# Demo pretorianina (tarcza Aegis — bezpiecznik ryzyka)
python imperium/pretorianie/aegis_tarcza.py
```

---

## 📜 HISTORIA WERSJI

| Wersja | Data | Zmiana |
|--------|------|--------|
| v0.1.0 | 2026-06-01 | Inicjalizacja INDEKS_IMPERIUM — Master Index stworzony |
| v0.2.0 | 2026-06-01 | +legatus.py, +kalkulator_lewara.py, +KATALOG_STRATEGII, +KATALOG_NEURONOW (287) |
| v0.3.0 | 2026-06-01 | Skan IV (+16 neuronów → 303), IGRZYSKA_IMPERIUM, PAMIEC_ABSOLUTNA, DORADCY_CARA, pamiec_absolutna.py |
| v0.4.0 | 2026-06-02 | +Adaptery API, +5 neuronów (A-03/A-05/XII-06 + F-01..04), Prawo XX elitarny, WAGI_REZIMU, LOG_ZMIAN, ZPO, REJESTR_INSPIRACJI |
| v0.5.0 | 2026-06-03 | +Namiestnik (Regime-Aware Gating), +Detektor Lookahead, +Timeframe-Aware (styl SCALP/SWING/INVEST, lewar_cap, futures/spot, filtr strategii po interwale), tabela dowodowa, 346 testów |
| v0.9.0 | 2026-06-09 | Z-03/Z-04/X-27, master-switch reżimu Faza 1, BIB-020 (pomiar_dekorelacji), porządek docs: archiwizacja duplikatu, aktualizacja liczb; 55 neuronów, 562 testów (W12 żywotność głosu) |
| v0.9.1 | 2026-06-12 | Radar Rynku Opcja A (decyduj_z_radarem), Opcja B (wagi_inwerse_vol+backtest_portfel), bonus_radar, 4 nowe neurony, 743 testów, Paper Trading Etap II instrukcja, 62 neurony |

---

*Roma non est facta die una. Imperium buduje się neuron po neuronie.*

*— INDEKS_IMPERIUM.md | Aktualizowany z każdą sesją | Faza 0 — Paper Trading*
