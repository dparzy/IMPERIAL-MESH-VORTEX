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
| **Maturitas** (Dojrzałość) | `imperium/oczy/maturitas.py` | odpowiada LICZBĄ Z KODU na trzy pytania: czy **specyfikacja** jest zdrowa (PROMPT), czy **pętle się domykają** (LOOP), czy graf **istnieje / działa / DECYDUJE** (GRAPH) — po 0–4 na piętro. Powstał 2026-08-02 z rozkazu Cezara „pilnujmy stanów prompt/loop/graph": doktryna „domykaj loop, otwieraj graph" była KRYTERIUM bez MIERNIKA, a sam krok w checkliście byłby zasadą bez mechanizmu — tą samą klasą, którą tego dnia złapaliśmy przy append-only. **Pierwsza ŻYWA kategoria projektu INGENIUM** (ósma: PIĘTRO INŻYNIERII), zbudowana wg jego zasad nienaruszalnych: `NIEZNANE` jest wynikiem (brak odczytu grafu ≠ graf pusty), **antywskaźnik obowiązkowy** przy każdym piętrze (jak je oszukać), migawki dają DELTĘ zamiast gołego stanu. **LUSTRO, NIE KIEROWNICA** — Goodhart: test `test_organ_nie_jest_wpiety_w_sciezke_decyzyjna` mechanizmem pilnuje, że żaden moduł ścieżki decyzyjnej go nie importuje. Rozstrzygnięcie progów: **GRAPH 4/4 znaczy wyłącznie „czytany PRZY DECYZJI"** — niższe mierzą rozmiar, nie pożytek. Świadomie NIE liczy jednej oceny Imperium (uśrednienie ukryłoby doskonały LOOP przy zerowym GRAPH) i NIE ocenia wyniku tradingowego. Wpięty w `/apertio` 5b i `/clausura` 5c. Koszt: ~0,41 s | [I, XV, XVI, XIX] |
| **Vindex** (Obrońca Zapisu) | `imperium/pretorianie/vindex.py` | pyta o JEDNO: czy zmiana w repozytorium **złamała kontrakt swojego pliku** — rzymski *vindex* występował w obronie naruszonego prawa. Powstał 2026-08-02 na rozkaz Cezara (zakres B) z pomiaru: kontrakt „append-only" jest DEKLAROWANY w docstringach co najmniej sześciu organów i w nagłówku `LOG_ZMIAN`, a **egzekwowany przez zero mechanizmów** — zasada zapisana, mechanizmu brak (klasa runbooka W11). Stawka: `rejestr_testow.jsonl` jest źródłem prawdy POMIARÓW, więc cicha zmiana starej linii unieważnia decyzje o składzie roju i nikt się nie dowie. Kontrakty pochodzą z KALIBRACJI na historii gita (883 commity, 254 dotykające ledgerów), nie z nazw plików: **ŚCISŁY** (zero usunięć w historii — `codex_notarum`, `dziennik_niesmiertelny`, `tiro_pary`) → alarm; **KORYGOWALNY** (5 usunięć na 254 — `rejestr_testow`, `ksiega_wad`, `index_falsorum`, `ab_plon`) → pytanie o powód; **MUTOWALNY** (`wizje_i_decyzje` — status POMYSŁ→WDROŻONA, `procedury` — runbooki W11) → cisza. Odzywalność zmierzona: **2,0%** (EXACTOR v1 dla porównania: 80% = tapeta). Świadomie NIE kasuje obcych plików (rozkaz Cezara 07-28: kwarantanna, nie kosz) i NIE sądzi ACTA `.md` miarą liniową, bo `stan_na` we frontmatterze dałoby 330 fałszywek na 379 commitach `LOG_ZMIAN` — zasięg stoi JAWNIE w polu `niepokryte`.<br>Chodzi jako hook **PostToolUse: Bash\|PowerShell** (`.claude/hooks/post-bash.sh`) — łata lukę zmierzoną tego samego dnia: matcher VIGILA to `Write\|Edit\|NotebookEdit`, więc plik tworzony komendą powłoki był **niewidzialny**. W automacie zasięg wąski (`--tylko-kontrakty`): obce pliki bada bramka, bo plik roboczy jest nieśledzony aż do `git add`. `krawedzie()` wydaje werdykty jako relacje `(plik) —[naruszenie]→ (commit)` — materiał dla grafu W8 (doktryna: domykać loop, otwierać drogę na graph). Koszt zmierzony: ~0,36 s | [I, XV, XVI, XXI] |
| **Silentium** (Cisza Obrzędowa) | `imperium/pretorianie/silentium.py` | robi JEDNO: na czas biegu bramki **odmawia Architektowi zapisu do repozytorium**. Rzymskie *silentium* to nakazana cisza podczas czynności świętej — byle drgnienie unieważniało auspicja, więc ciszy nie proszono, tylko ją ogłaszano. Powstał 2026-08-03 jako **CORONA A** (LEX TALIONIS, wybór Cezara z trzech opcji) i jest pierwszym organem Imperium, który **ZAPOBIEGA** zamiast wykrywać: strażnik czystości w `run_tests.py` i VINDEX patrzą WSTECZ, a strażnik czystości sam przyznaje w swoim komunikacie, że nie odróżni winy testu od równoległej edycji („to fałszywe oskarżenie, powtórz bieg sam"). Zmierzony koszt luki: **4 unieważnione biegi w 4 dni, dwa w jednej wachcie przez tego samego Architekta, który zasadę zapisał 31.07** — dowód, że sama wiedza nie wystarcza. Blokadę zakłada **proces bramki** (`cisza()` jako menedżer kontekstu w `tests/run_tests.py` i `narzedzia/audyt_spojnosci.py`), nie hook rozpoznający komendę — bo bieg w tle wraca z narzędzia natychmiast, więc hook zdjąłby ciszę w pierwszej sekundzie 20-minutowego biegu (klasa E7: strażnik milknie dokładnie wtedy, gdy jego kontrakt przestaje obowiązywać). **Trzy niezależne bezpieczniki przed zamurowaniem repo**: żywotność PID-u (badana `OpenProcess`, **nigdy** `os.kill` — na Windowsie to `TerminateProcess`, czyli pomiar zabijałby mierzony proces), TTL 45 min i furtka `zdejmij --sila` / `SILENTIUM_OFF=1`. Odczyt (`git status`, `grep`, `pytest`) jest ZAWSZE wolny — strażnik blokujący patrzenie uczy się go obchodzić. Klasyfikator komend **SKALIBROWANY na 120 zaetykietowanych realnych komendach** z transkryptów (korpus 5571): precyzja **93,5%**, czułość ważona populacją **98,3%** — pierwsza wersja „na wyczucie" miała 63,3% i przepuszczała 11/60 zapisów (`narzedzia/kalibracja_silentium.py`). Chodzi jako **PreToolUse** (`.claude/hooks/pre-tool-use-silentium.sh`), osobno od CUSTOS LIMINIS: tamten broni rozkazów STAŁYCH, ten stanu CHWILOWEGO. **Cisza jest WSPÓŁDZIELONA** (naprawa 2026-08-03, wada znaleziona realnym użyciem nazajutrz po wdrożeniu): plik trzyma listę uczestników, każdy bieg dopisuje siebie, a cisza trwa aż wyjdzie OSTATNI. Pierwsza wersja była wyłączna i pękła na własnym starcie — dwie sesje ruszyły o 10:03, drugiemu audytowi odmówiła ochrony komunikatem „bieg idzie BEZ ochrony" (nieprawda: repo było chronione cudzą ciszą), po czym sesja kończąca pierwsza **zdjęła ciszę spod wciąż trwającego biegu**. Wyłączność chroniła plik blokady zamiast repozytorium i kłamała o stanie ochrony — czyli sama była klasą „przyrząd kłamie". Wyłączność została wyłącznie w `zaloz()`, na drodze człowieka. | [I, XV, XIX, XXI, XXIV] |
| **Lustrum** (Obrzęd Oczyszczenia) | `imperium/pretorianie/lustrum.py` | odpowiada na pytanie, którego **CENSUS ORGANORUM nigdy nie zadaje**: nie „czy zameldowany", lecz **„czy jeszcze potrzebny"**. W Rzymie *lustrum* był obrzędem KOŃCZĄCYM cenzus, więc organ nie stoi obok spisu — on go domyka. Powstał 2026-08-04 jako **CORONA A** w wariancie SZEROKIM (decyzja Cezara): jednym mechanizmem obsługuje MODUŁY i **OBCE PLIKI**, bo w obu przypadkach robi to samo — znajdź zapomniane, oceń, przesuń etapami, **nigdy nie kasuj sam**. Kopiuje sprawdzony wzorzec W10 ZAPOMINANIE + W7 KUSTOSZ: liczy wartość, tylko PROPONUJE, a wyrok wykonuje organ nadrzędny. **Pożytek liczony z PIĘCIU świadectw** (wołacz produkcyjny 0.40 · CLI 0.20 · opis w docs 0.15 · ślad w ledgerze 0.15 · test 0.10) — i to jest sedno organu, udowodnione pomiarem: wersja jednosygnałowa („kto mnie woła") zgłosiła **27 z 260 modułów**, z czego **25/25 zbadanych okazało się sprawnymi przyrządami ręcznymi z własnym CLI i opisem w dokumentach** — narzędzie wołane z wiersza poleceń z definicji nie ma wołacza w kodzie, więc **fałszywek byłoby 100%** (precyzja 7,4%). Zamiast jednego wyroku wydaje **cztery werdykty Cezara** i wskazuje ORGAN DECYDUJĄCY: ✅ ZOSTAW · 🔌 WPIĄĆ (Prawo XV / Backlog CODEX) · 🔎 ZBADAĆ (`diagnostyka_korelacji`, Prawo XVI) · 📦 ARCHIWUM (Cezar, Prawo XVIII). SCALIĆ nigdy nie orzeka sam — podobieństwo się MIERZY korelacją, nie ocenia z wyglądu. Etapy wycofania mają zegar w **ledgerze append-only** (`lustrum.jsonl`), nie w pamięci: ⚔️ AKTYWNY → 💤 PODEJRZANY → ⏳ KARENCJA (30 dni) → 🕯️ HONESTA MISSIO, przy czym ostatni stopień **nie powstaje z pomiaru**, wyłącznie z zatwierdzenia. Powrót do służby kasuje zegar JAWNYM rekordem, nie ciszą. Czytanie jest oddzielone od zapisu (`raport` vs `znacz`) — organ, który przy patrzeniu zmienia stan, uczy się być omijany. **Skalibrowany** na ZAMROŻONEJ próbce 59 modułów: precyzja klasy WPIĄĆ 3/3, zero błędnych skierowań do archiwum, zero fałszywych negatywów wśród 7 zbadanych modułów ZOSTAW bez wołacza produkcyjnego. ⚠️ GRANICA POMIARU: prawdę podstawową ustalił Architekt czytaniem kodu, nie niezależny sędzia, a 24 pozycje ZBADAĆ nie były weryfikowane pojedynczo — dług zapisany na etap **L2** przeglądu LUSTRATIO. Pierwszy bieg wskazał **sam siebie** oraz trzy realne straty potencjału: `bary_zdarzeniowe.py`, `kronikarz_zdarzen.py` i `neutralizacja.py` — otestowane, opisane, **bez jednego wołacza produkcyjnego**. | [XV, XVI, XVIII, XIX, XXI] |
| **Conditor Lustri** (Zamykający Lustrum) | `imperium/pretorianie/conditor_lustri.py` | odpowiada JEDNĄ liczbą i JEDNYM kodem wyjścia na pytanie, którego dotąd nikt nie umiał zadać maszynie: **czy wolno już zdjąć ZAMROŻENIE LUSTRATIO**. Rzymscy cenzorzy kończyli lustrację obrzędem *condere lustrum* — dopóki go nie odprawiono, cenzus trwał. Powstał 2026-08-05 jako **U1**, bo rozkaz z 08-04 zabraniał rozwoju, dopóki Imperium nie będzie „w pełni skalibrowane” — **bez liczby**, czyli w stanie niefalsyfikowalnym: zamrożenie albo nigdy się nie kończy, albo kończy się arbitralnie. To ta sama klasa wady, która zamrożenie wywołała — zamrożenie leczące bramki bez miary samo nie miało miary. **Nie liczy niczego sam** (K1): każde z siedmiu kryteriów WOŁA organ, który ten fakt produkuje (audyt · BREVIARIUM · TABULARIUM · CODEX NOTARUM · MATURITAS), bo druga arytmetyka obok istniejącej to nie kontrola, tylko drugie źródło prawdy. **Kryterium ma TRZY stany, a `NIE WIEM` blokuje tak samo jak `NIE`** (K2) — inaczej najtańszą drogą do zielonej bramki byłoby dopisanie kryterium bez miernika, czyli zamiana mierzenia w chwalenie (Goodhart). Awaria producenta też daje `NIE WIEM`: organ, który po wyjątku mówi OK, jest gorszy od organu, którego nie ma. **L4 świadomie poza własną oceną** — to etap, który ten organ domyka, więc w kryteriach żądałby własnego domknięcia, żeby się domknąć. Dwa kryteria (**KLASY**, **KALIBRACJA**) nie mają jeszcze producenta i świecą `NIE WIEM` **wraz z instrukcją, co zbudować** — to one są realnym warunkiem odmrożenia. Pierwszy pomiar 2026-08-05: 1 spełnione / 3 niespełnione / 3 NIE WIEM. **Zamrożenia nie zdejmuje sam** — melduje gotowość, decyzja należy do Cezara (Prawo XVIII). | [I, XV, XVI, XVIII, XIX, XXI] |
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
