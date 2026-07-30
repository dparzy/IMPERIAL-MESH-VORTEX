---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/akwedukty/kwatermistrz_danych.py, imperium/biblioteki/codex_notarum.py, imperium/biblioteki/index_falsorum.py, imperium/swiatynie/praetorium.py, imperium/biblioteki/hedge_mwu.py, imperium/biblioteki/igrzyska.py, imperium/biblioteki/kronikarz.py, imperium/biblioteki/mnemosyne.py, imperium/biblioteki/notarius.py, imperium/cesarz/titan_mind.py, imperium/drogi/nexus_hub.py, imperium/fundament/brama_kalkulatora.py, imperium/fundament/kuznia_narzedzi.py, imperium/koloseum/backtest.py, imperium/koloseum/haruspex.py, imperium/koloseum/monte_carlo.py, imperium/koloseum/walidacja.py, imperium/koloseum/walk_forward.py, imperium/legiony/pierwszy_zwiadowca.py, imperium/legiony/roj_sygnalow.py, imperium/oczy/censor_sprzetu.py, imperium/oczy/wszechoko.py, imperium/pretorianie/aegis_tarcza.py, imperium/pretorianie/lustro_prawdy.py, imperium/senat/meta_kora.py, imperium/swiatynie/kartograf.py, imperium/swiatynie/specula_swiec.py, imperium/swiatynie/web_dashboard.py
stan_na: 2026-07-19
powod_istnienia: "Jedna strona spinająca 25 Praw z realnym kodem — jedyne miejsce z tabelą 'dzielnica → plik → rola → prawa' + diagram przepływu sygnału + mapowanie warstw architektury na źródła bib"
---
# 🏛️ ARCHITEKTURA IMPERIUM — pełna mapa

> **Po co:** Jedno miejsce, które spina **25 Praw** z **realnym kodem**
> (<!-- LICZBA:neurony -->87<!-- /LICZBA --> neuronów). Pokazuje, jak Cesarstwo jest zbudowane
> i którędy płynie sygnał. Liczby **policzone z kodu**, nie z pamięci (Prawo XXI reguła 8).

> **✅ Dług naprawiony 2026-07-18:** poprzednia wersja miała pole `dlug:` ostrzegające, że mapa
> opisuje **nieistniejący kod** (`drogi/war_lancer`, `swiatynie/sala_wojenna`, `koloseum/valhalla`
> — zweryfikowane: 0 plików). Zastąpione realnymi modułami: egzekucja → `oms.py`/`real_order_router.py`,
> dashboard → `web_dashboard.py`, backtest → `backtest.py`/`monte_carlo.py`.

---

## 🗺️ Mapa dzielnic (kod → rola → prawa)

```
👑 CESARZ          cesarz/        titan_mind            decyzja, harmonogram   [III, XIV]
🏛️ SENAT           senat/         meta_kora             debata agentów         [IX, XIII]
⚔️ LEGIONY          legiony/       pierwszy_zwiadowca    boty, pełny cykl       [IV, VI]
                                   roj_sygnalow          konsensus sygnałów     [X, IX]
🛡️ PRETORIANIE     pretorianie/   aegis_tarcza          ryzyko, circuit breaker[IX]
                                   lustro_prawdy         walidacja adwersarialna[I, IX]
                                   portitor              celnik u wrót: pre-flight środowiska startu[XV, XVII]
                                   probator              strażnik cytatów: plon Hyginusa vs podane fragmenty[I, XVI]
🚰 AKWEDUKTY        akwedukty/     kwatermistrz_danych   dane OHLCV (CCXT/CSV)  [II]
👁️ OCZY            oczy/          wszechoko             percepcja wielowarstwowa[XII]
                                   censor_sprzetu        cenzus majątku maszyny → klasa+alarm[XV]
                                   breviarium            spis sług: Hyginus/TIRO/modele na otwarciu[XV, XVII]
🛤️ DROGI            drogi/         nexus_hub             multi-exchange routing [III, XIII]
                                   oms + real_order_router egzekucja zleceń     [III]
🎨 ŚWIĄTYNIE       swiatynie/     kartograf             wykresy PNG            [V]
                                   web_dashboard         dashboard live         [V, XXIV]
                                   specula_swiec         świece OHLC w terminalu[V, XXIV]
📚 BIBLIOTEKI      biblioteki/    mnemosyne             pamięć transakcji      [VIII, XIII]
                                   kronikarz             logi, dziennik         [XIII]
                                   igrzyska              ranking batch + observer pattern [XV]
                                   hedge_mwu             MWU online learning (W-049)     [XV, XVI]
                                   notarius              stenograf słów Nauczyciela → pary
                                                         prompt→odpowiedź = surowiec Szkoły
                                                         TIRO (E2)              [I, XV, XXIV]
🧮 FUNDAMENT       fundament/     brama_kalkulatora     jedyne wejście do mat. [I, IX, XIII]
                                   kuznia_narzedzi       kanoniczne wskaźniki   [I]
                                   faber                 KOWAL: binaria spoza Pythona
                                                         (calibre/djvutxt/tesseract) — znajduje
                                                         poza PATH i KRZYCZY zamiast milczeć [XV]
🏟️ KOLOSEUM        koloseum/      backtest + monte_carlo backtest, Monte Carlo [VI, VII]
                                   haruspex              predykcja reżimu (Markow) — ⚠️ falsyfikowany pomiarem [I, XVI]
```

---

## 🧰 Narzędzia z nazwą rzymską (`narzedzia/`)

Organy pomocnicze POZA `imperium/` — dobór nazwy DO FUNKCJI (ZASADA NOMENKLATURY IMPERIALNEJ).
Źródło prawdy imion narzędzi (organy `imperium/` są w mapie dzielnic wyżej; agenci w `docs/PROFIL_CEZARA.md`).

> **Kwatera Główna w `imperium/swiatynie/`:** **PRAETORIUM** (`imperium/swiatynie/praetorium.py`) —
> Centrum Dowodzenia Imperatora: hybryda kwatery bojowej (kokpit) i castrum (kondycja organów).
> Renderer jest CZYSTĄ funkcją (`render_praetorium(stan) -> str`), więc `web_dashboard.py` może go
> podać bez stawiania drugiego serwera (Prawo XVI). Każdy panel niesie znacznik **ŻYWE / BRAK DANYCH**
> — kokpit nigdy nie maluje wypełniacza jako pomiaru (Prawo I). [I, XV, XVI]
>
> **Organ governance w `imperium/biblioteki/`:** **CODEX NOTARUM** (Księga Not Cenzorskich,
> `imperium/biblioteki/codex_notarum.py`) — ledger LEX TALIONIS „oko za oko": NOTA CENSORIA (−) za
> zatwierdzony błąd, CORONA (+) za zatwierdzony unikat spłacający dług honorowy. [I, XV, XXI]
>
> **INDEX FALSORUM** (Spis Twierdzeń Obalonych, `imperium/biblioteki/index_falsorum.py`) — twierdzenie
> obalone POMIAREM rejestruje się raz (fraza + poprawna teza + dowód), a sweep całego korpusu `.py`+`.md`
> pilnuje, by nie żyło dalej jako fakt. Klasa siostrzana Warstwy 15 (liczby) i 16 (API-widma) — tylko po
> stronie TWIERDZEŃ. Historia (ACTA/archiwum) i sprostowania poza zasięgiem; źle dobraną frazę zdejmuje
> `wycofaj()`. Sweep: `narzedzia/skan_wad_kodu.py --falsa`, w hooku startowym. [I, XV, XXI]
>
> **SIGILLARIUM** (Skarbiec Pieczęci, `imperium/biblioteki/sigillarium.py`) — **SIGLA IMPERII**:
> hasła-skróty Cezara `/apertio` (otwarcie wachty), `/clausura` (domknięcie), `/limes` (bramka
> Prawa XXI) uruchamiające PEŁNE procedury bez recytowania ich za każdym razem. Rdzeń: pieczęć
> **nie przechowuje kroków** — czyta je z konstytucji (`CLAUDE.md`) w chwili wywołania, więc
> rozjazd jest strukturalnie niemożliwy, a nie „pilnowany" (to samo lekarstwo co CENSUS ORGANORUM:
> odebranie dokumentowi prawa do własnej treści). Karmi runbooki W11 (`synchronizuj_w11()`), więc
> hasło działa też pisane zwykłym zdaniem; ujście w harnessie to cienkie `.claude/skills/*/SKILL.md`,
> które wołają pieczęć zamiast kopiować kroki (Prawo XVI). Pusta pieczęć albo martwa komenda bramki
> **krzyczy**, zamiast udawać sprawną. [I, XV, XVI, XXI]

| Nazwa rzymska | Plik | Rola | Prawa |
|---|---|---|---|
| **Speculum Probationis** (Zwierciadło Prób) | `narzedzia/kapitol_podglad.py` | zero-tokenowy podgląd testu w Kapitolu (HTML + inline-SVG, spec + wykres + link) | [V, XXIV] |
| **Cursus Fenestrarum** (Bieg Okien) | `narzedzia/wfo_chunked.py` | chunkowany, wznawialny walk-forward (checkpoint per-okno) | [I, XVI, XXIV] |
| **Scriba Codex** (Skryba Kodeksu) | `narzedzia/scriba_codex.py` | idempotentny appender wyników testów do rejestru CODEX | [I, XXI] |
| **Veritas Annalium** (Prawda Roczników) | `narzedzia/audyt_danych.py` | audyt świec w 3 warstwach: struktura · krzyżowa 1h↔4h · zgodność z giełdą; naprawa zmierzonych rozjazdów z kopią | [I, XVI, XXI] |
| **Conflator Temporum** (Zlewacz Interwałów) | `narzedzia/agreguj_bary.py` | buduje wyższy interwał z niższego (1m→5m/15m, 1h→4h); odrzuca niepełne okna, ostrzega przy nadpisaniu danych z giełdy | [I, XVI] |
| **Nuntius Mercatus** (Posłaniec Rynku) | `narzedzia/pobierz_binance.py` | pobiera świece dowolnego interwału z publicznego API Binance; checkpoint stronicowy = zabity bieg traci jedną stronę, nie postęp | [I, XXIV] |
| **Census Organorum** (Spis Organów) | `narzedzia/census_organorum.py` | spis WSZYSTKICH modułów `imperium/`+`narzedzia/` generowany z żywego kodu (rola = docstring); bramka Warstwy 17 audytu — moduł bez meldunku blokuje commit | [XV, XIX, XXI] |
| **Breviarium** (Spis Sług) | `imperium/oczy/breviarium.py` | meldunek otwarcia: **aktualność wyniku testów** (SIGILLUM PROBATIONIS — pieczęć przypięta do commitu; „zielone dla innego commitu" = NIEZNANY, nie zgoda), stan HYGINUSA (kolejka, plon czekający na sędziego, model, profile Dispensatora) i TIRO (pary nauczyciela, modele na dysku, klasa sprzętu). Liczby GENEROWANE z żywego stanu. Modelu Architekta świadomie NIE zgaduje — środowisko go nie niesie, więc żąda deklaracji (Prawo I) | [XV, XVII, XXI] |
| **Probator** (Strażnik Cytatów) | `imperium/pretorianie/probator.py` | warstwa 1 anty-halucynacyjna Hyginusa: deterministycznie (0 tokenów) sprawdza, czy każde cytowane źródło NAPRAWDĘ było modelowi podane — grounding wobec promptu, nie wobec korpusu. Abstencja = wynik poprawny. Monotonicznie ostrożny: dokłada werdykt do cząstki, nic nie odrzuca | [I, XVI, XXI] |
| **Nomenclator** (Strażnik Imion) | `imperium/pretorianie/nomenclator.py` | warstwa 2 anty-redundancyjna Hyginusa: deterministycznie (0 tokenów) sprawdza, czy NAZWA kandydata trafia w pojęcie żywe w kodzie — rzymski *nomenclator* szeptał panu imiona mijanych osób. Czyta wyłącznie nagłówek, nie ciało (zaprzeczenie „istnieje CVD, ale to co innego" nie może oskarżać). Głos wyłącznie POZYTYWNY: trafienie jest mocnym sygnałem, milczenie słabym — bo leksykon liczy 32 pojęcia. Powstał 2026-07-27 z PRZENIESIENIA detektora z Libra Messis, gdy pomiar pokazał, że mierzący miał przyrząd, a mierzony nie (Prawo XV). Opt-in OFF do zielonego A/B | [I, XV, XVI] |
| **Custos Liminis** (Strażnik Progu) | `imperium/pretorianie/custos_liminis.py` | hook **PreToolUse**: bariera ZANIM narzędzie zadziała. `git push` w dowolnej formie → **deny** (rozkaz nienaruszalny z 2026-07-11); zapis do `archiwum/` → **ask**, bo konstytucja oddaje tę decyzję Cezarowi, nie skryptowi; wszystko inne → cisza. Domyka lukę zmierzoną 2026-07-27: `permissions.deny` miało regułę wyłącznie `Bash(...)`, a reguły PowerShella to OSOBNA przestrzeń nazw — przy powłoce podstawowej PowerShell rozkaz był nieegzekwowany. Łapie też formy, których reguła wzorcowa nie widzi (`git -C /repo push`, cytowana ścieżka do `git.exe`). Awaria strażnika nie blokuje pracy, ale nie milczy | [I, XV, XXI] |
| **Vigil** (Straż Nocna) | `imperium/pretorianie/vigil.py` | hook **PostToolUse**: po KAŻDYM zapisie pliku `.py` uruchamia `ruff` + `skan_wad_kodu` i wstrzykuje zarzuty od razu, zamiast czekać na bramkę — rzymscy *vigiles* gasili ogień, póki był mały. Powód zmierzony: Księga Wad ma 126 klas i 16 wzorców regex (~13% automatu), a klasa nazwana 07-26 wróciła 07-27 w 277 egzemplarzach. Cisza gdy zielone (meldunek po każdym zapisie zamieniłby strażnika w tapetę). Koszt zmierzony: ~0.35 s na plik | [XV, XXI, XXIV] |
| **Recognitor** (Poświadczyciel Recenzji) | `imperium/pretorianie/recognitor.py` | pyta o JEDNO: czy commit, który widział recenzent zewnętrzny, to nadal ten, który mamy — rzymski *recognitor* poświadczał zgodność dokumentu ze stanem faktycznym. Powstał 2026-07-27 z pytania Cezara „czy cubic znalazł nowe błędy": zmierzone, że recenzent zrobił JEDEN przebieg wobec `bfb5e26`, po czym weszły 3 commity (w tym naprawy jego własnych uwag i nowy organ) i PR został zmergowany — **756 linii .py trafiło do `main` bez spojrzenia**. Cisza recenzenta czytała się jak zgoda, bo nic nie pytało, czy nadążył. Pyta endpoint `reviews` (przebieg istnieje także bez uwag), rozróżnia lukę naprawialną pushem od NIEODWRACALNEJ po mergu, a braku sieci NIGDY nie melduje jako zieleni — kod wyjścia 2 to niewiedza, nie zgoda. Krok 3 domknięcia wachty; poza hookiem startowym, bo wymaga sieci | [I, XV, XXI] |
| **Exactor Renuntiationis** (Poborca Meldunku) | `imperium/pretorianie/exactor.py` | bierze TEKST meldunku, który ma pójść do Cezara, i sprawdza go wobec **żywej checklisty CLAUSURY czytanej z KONSTYTUCJI** — rzymski *exactor* ściągał należne, nie oceniał zamiaru. Powstał 2026-07-30 ze spłaty TALARA `N-b74ce133`: krok 8 nakazuje pełny blok PowerShell (`cd` + `git push origin <gałąź>`), dałem sam `git push`, a pieczęć wydrukowała mi ten rozkaz kilka minut wcześniej — **wiedza była, sprawdzenia nie było**. Jedyny organ czytający to, co MÓWIĘ Cezarowi (reszta bada kod i dokumenty). Kotwice powinności muszą znaleźć swoją frazę w żywym CLAUDE.md — zmiana rozkazu daje alarm `kotwica_osierocona`, nie ciche pilnowanie nieboszczyka. Powinność WARUNKOWA (krok 9) świadomie poza rejestrem i JAWNIE w polu `niepokryte`. Uodpornienie: `--blok-push` **generuje** blok z żywego repo, więc nie ma czego przepisywać z pamięci. Zmierzony na 190 meldunkach z kroniki 144 sesji: krok 8 — recall 4/4, **0 fałszywych** na 156 przekazaniach.<br>Od 2026-07-31 chodzi też jako hook **Stop** (`.claude/hooks/stop.sh`) — sprawdzenie **bez udziału pamięci Architekta**, bo skill trzeba pamiętać wywołać, a to właśnie pamięć zawiodła. Kształt zdarzenia potwierdzony SONDĄ przed napisaniem logiki (`last_assistant_message` niesie gotowy meldunek) — kolejność odwrotna byłaby powtórzeniem błędu, dla którego organ powstał. Hook bada **wyłącznie krok 8**, jedyną powinność ze zmierzonym zerem fałszywych; poziom „domkniecie" do automatu odpalanego po każdej turze nie wchodzi. Bezpieczniki: `stop_hook_active` przerywa pętlę, awaria kończy się kodem 0 i krzykiem na stderr | [I, XV, XXI] |
| **Discriminator** (Rozróżniacz) | `imperium/legiony/discriminator.py` | orzeka, czy SKUPISKO neuronów o wspólnej etykiecie `(KATEGORIA, MECHANIZM)` to naprawdę redundancja — rzymski *discriminator* rozdzielał i rozróżniał. Powstał 2026-07-31 z alarmu Prawa XV (pozycja F0): `raport_mechanizmow()` liczył **17 skupisk**, a `grep` po repozytorium dawał dwa trafienia — własną definicję i test na obecność klucza. Prawdziwa luka była głębsza niż „nikt nie drukuje listy": skupisko jest **kandydatem do pomiaru korelacji**, przyrząd (`korelacja_pearson`) istniał, ścieżka bary→Brama→`interpretuj` też — a kandydaci **nigdy nie trafiali pod przyrząd** (jedyny taki pomiar, `dekorelacja_w322.py`, był skryptem jednorazowym na 5 zahardkodowanych neuronów). Pierwszy bieg: 125 par, **jeden** kandydat do scalenia (`X-05 ↔ XII-02`, r=0,82), stabilny na 6× większej próbce — teza o masowej redundancji **niepotwierdzona**. Świadomie nie wycisza niczego (Prawo XVI: kandydat ≠ wyrok) i nie nazywa ciszy martwym głosem, bo pomiar karmi rój jedną parą i samym OHLCV, więc neurony alt-danych i kontekstu międzyrynkowego milczą **poprawnie** | [XV, XVI, XXII] |
| **Dispensator** (Szafarz) | `imperium/cesarz/dispensator.py` | dobór modelu DeepSeek do trudności zadania (ZASADA OSZCZĘDNOŚCI TOKENÓW) — organ rdzenia Cezara, nie narzędzie; wpisany tu po tym, jak cenzus 2026-07-20 zastał go niezameldowanym w ŻADNYM dokumencie | [XVI, XVIII] |
| **Aerarium** (Skarbiec) | `imperium/cesarz/aerarium.py` | waga kontekstu startowego (ile tokenów płacimy ZANIM Cezar napisze słowo) + **GRADUS OPERIS** — stopnie wysiłku VELES/MILES/CENTURIO/TRIBUNUS/DICTATOR (+AUSPICIUM, PRAEFECTUS FABRUM), źródło prawdy tabeli w CLAUDE.md §💰. Alarmuje, gdy konstytucja przekroczy 200 linii. Świadomie NIE udaje, że zna limit planu Cezara (`/usage` bez API) ani wielkości własnego wydruku hooka — abstynencja zamiast zera | [I, XV, XXI] |
| **Libra Messis** (Waga Plonu) | `narzedzia/ab_plon_hyginusa.py` | A/B jakości zwiadu Hyginusa: świadomość systemu U4 ON/OFF oraz profile Dispensatora na krytyce. Metryki deterministyczne (0 tokenów) + koszt z FAKTYCZNEGO `usage`. Nie dotyka produkcyjnej kolejki hipotez — mierzący nie zmienia mierzonego. Trzyma surowy plon, więc poprawka definicji miary nie wymaga płatnego powtórzenia biegu (`przelicz`). Od 2026-07-27 detektor duplikatów IMPORTUJE z Nomenclatora zamiast go deklarować — jeden egzemplarz, bo kopia rozjechałaby pomiar z produkcją (test tożsamości obiektów pilnuje) | [I, XVI, XXIV] |

---

## ⚖️ ZASADA SYMBIOZY — czego NIE wolno duplikować

> *„Dwóch legionistów na tym samym posterunku to marnotrawstwo. Jeden jest odpowiedzialny — reszta słucha."*

Uratowane z `SYMBIOZA_MODULOW.md` (zarchiwizowana 2026-07-17 — reszta tamtego dokumentu
opisywała kod, który nigdy nie istniał). **To jest żywa doktryna, nie historia:** każda
z tych reguł obowiązuje dziś i jest sprawdzalna w kodzie.

| Zasób / funkcja | Wiele modułów? | JEDYNY właściciel | Dlaczego |
|---|---|---|---|
| Surowe dane OHLCV | ✅ każdy czyta po swojemu | `akwedukty/kwatermistrz_danych.py` (pobieranie) | Każdy Legion może interpretować te same świece inaczej |
| Obliczanie wskaźników (RSI, EMA, ATR…) | ❌ **NIE** | `fundament/brama_kalkulatora.py` | Jeden hash SHA-256 = jeden wynik. Zero rozbieżności między Legionami |
| Wywołania LLM | ❌ **NIE** | `cesarz/deepseek_glos.py` | Jeden punkt kosztu, rate-limitu i konfiguracji modelu. Dzięki temu NOTARIUS łapie wszystkich wołających jednym wpięciem |
| Wykonanie zleceń | ❌ **NIE** | `drogi/` (`oms.py`, `real_order_router.py`) | Tylko jeden moduł dotyka prawdziwych środków. Zero wyścigu |
| Zapis transakcji / historii | ❌ **NIE** | `biblioteki/` (`kronikarz.py`, `mnemosyne.py`) | Jeden schemat zapisu = możliwy backtest i audyt |
| Dane on-chain / makro | ✅ Senat i Cesarz czytają | `oczy/` (pobieranie) | Makro to kontekst, nie sygnał — wiele warstw może go interpretować |
| Konfiguracja ryzyka (% kapitału, SL, TP) | ❌ **NIE** | `pretorianie/` | Jeden arbiter ryzyka. Cesarz proponuje, Pretorianie zatwierdzają lub wetują |

**Pytania przed każdą nową funkcją:** Kto już to robi? · Czy to łamie zasadę jedynego
właściciela (Brama / Głos / Drogi / Kronikarz)? · Gdzie w przepływie to siedzi?

---

## 🔄 Jak płynie sygnał (cykl decyzyjny)

```
   🚰 AKWEDUKTY ── dane OHLCV ──►  🧮 FUNDAMENT (Brama)
   (kwatermistrz)                   liczy RSI/EMA/ATR... (Prawo I)
                                          │  JSON "answer key" + pieczątka
                                          ▼
   👁️ OCZY ── warstwy percepcji ──► ⚔️ LEGIONY (zwiadowcy)
   (wszechoko)                       generują surowe sygnały
                                          │
                                          ▼
   🛡️ PRETORIANIE ── filtr/weto ──► 🏛️ SENAT (debata)        [Prawo IX]
   (aegis, lustro)                   ścierają argumenty
                                          │
                                          ▼
                                   👑 CESARZ (decyzja)        [Prawo III, XIII]
                                   widzi cały zapis debaty
                                          │
                                          ▼
   🛤️ DROGI ── egzekucja ──────────► rynek
   (nexus_hub, oms, real_order_router)
                                          │
                                          ▼
   📚 BIBLIOTEKI (pamięć) + 🎨 ŚWIĄTYNIE (wykres/dashboard)   [Prawo VIII, V]
   🏟️ KOLOSEUM ── testuje strategie zanim wejdą do boju ──    [Prawo VI, VII]
```

---

## 🎯 Cykl bojowy Fazy 0 (to, co realnie się spina dziś)

6 modułów uruchamianych jednym poleceniem (przez `pierwszy_zwiadowca`):

1. **kwatermistrz_danych** → dane (biblioteka / MEXC / syntetyczne)
2. **brama_kalkulatora** → liczy RSI + EMA (Prawo I)
3. **pierwszy_zwiadowca** → strategia trend-following
4. **aegis_tarcza** → ryzyko, circuit breaker
5. **kartograf** → wykres PNG
6. **kronikarz** → raport + dziennik

> Reszta modułów (senat, cesarz, oczy, drogi...) to **sprawdzony kod-baza**,
> jeszcze nie wpięty w cykl. Status uczciwie w [archiwum/AUDYT_ADOPCJI.md](../archiwum/AUDYT_ADOPCJI.md).

---

## ⚠️ Stan realny (Prawo I)

- 🟢 **Brama** — w pełni działa, egzekwuje Prawo I w kodzie.
- 🟡 **Cykl Fazy 0** — kod gotowy i spięty (loader naprawiony po reorganizacji),
  ale **nieuruchomiony na realnych danych** (brak TA-Lib + danych w chmurze).
- 🔴 **`pierwszy_zwiadowca`** — NIE jest "zwalidowaną strategią": dane syntetyczne,
  brak slippage, kruche wyniki. To *wstępny paper-test*. Szczegóły w audycie.

---

## 📚 ŹRÓDŁA — Kanon biblioteki za architekturą (BIB)

> **Po co ta architektura?** Każda warstwa Imperium ma teoretyczne ugruntowanie w bibliotece
> (**<!-- LICZBA:ksiazki -->115<!-- /LICZBA --> książek**). Tu mapa: warstwa → książka.
> Pełna esencja: `bibliotheca_ulpia/encyklopedia/`.

| Warstwa architektury | Dlaczego tak (koncept) | Źródło BIB |
|----------------------|------------------------|-----------|
| **Brama Kalkulatora** (neuron nie liczy sam) | rozdział obliczeń od interpretacji = pipeline Feature/Inference (FTI) | BIB-035 Iusztin&Labonne (LLM Engineer's Handbook) |
| **Meta-labeling (Arbiter Fiduciae)** | rozdzielenie KIERUNEK vs ROZMIAR/pewność sygnału | BIB-007 López de Prado (AFML) |
| **Arena Trzech Bram** | Triple-Barrier Method (TP/SL/czas) zamiast fixed-horizon | BIB-007 López de Prado (AFML) |
| **Koloseum (walidacja DSR/PBO)** | obrona przed backtest overfitting / data-snooping | BIB-007 López de Prado + BIB-041 Taleb |
| **Senat (debata 4 ról + synteza)** | wzorzec Supervisor (multi-round → synteza), nie prosty Router | BIB-034 Infante (AI Agents) |
| **Gubernator + WAGI_REZIMU** | mnożnik reżimu = kontekst makro/cyklu jako TŁO decyzji | BIB-001 Patel (18-letni cykl) |
| **Centrum Pamięci (W-360 v3)** | warstwowa pamięć agenta + decay wg ważności (FinMem) | BIB-033 Huyen + BIB-036 Alto + arXiv MEM-01..04 |
| **Bezpieczniki (Reguła 6%/HALT)** | budżet ryzyka + loss-aversion → nieprzełamywalny stop | BIB-015 Elder + BIB-040 Bernstein |
| **Kalkulator Lewara (VolatilityDrag/Kelly)** | erozja zmiennościowa + fractional Kelly z korektą estymacji | BIB-008/018 Sinclair |
| **Warstwa ryzyka (EWMA/VaR/ES)** | EWMA λ=0.94, Expected Shortfall dla grubych ogonów | BIB-042 Jorion |

> Mapowanie warstwa→klucz neuronu: `docs/KATALOG_NEURONOW.md` § Źródła. Mapowanie strategii: `docs/KATALOG_STRATEGII.md` § Źródła.

---

*PRAWDA. Organizm, nie kolekcja. Mniej, ale prawdziwie.*
— VITRUVIUSZ, architekt Imperium
