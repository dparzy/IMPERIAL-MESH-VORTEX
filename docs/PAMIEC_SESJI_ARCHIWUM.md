---
kategoria: ACTA
typ: acta
wlasciciel: —
stan_na: 2026-07-19
powod_acta: "Archiwum lekcji SCHŁODZONYCH z PAMIEC_SESJI.md (konsolidacja, Prawo XV). Wpisy datowane = prawda swojego czasu, nie aktualizujemy wstecz (Prawo I)."
powod_istnienia: "Magazyn starszych/mniej połączonych lekcji — pamięć aktywna ostra, nic nie tracimy (Prawo I). Przeszukiwalne (grep/RAG), poza wstrzykiwanym kontekstem startowym."
---
# 📦 PAMIĘĆ SESJI — ARCHIWUM LEKCJI

> Lekcje schłodzone z docs/PAMIEC_SESJI.md, gdy sekcja aktywna przekroczyła limit (24000 zn.). Kryterium: najniższa wartość retencji (zapominanie.wartosc_retencji — łączność w grafie × świeżość × ważność). NIC nie skasowane.

## 📦 LEKCJE ARCHIWALNE (schłodzone wg wartości retencji)

### 2026-07-27 — Gnicie runbooków W11 - własna treść zamiast referencji
Runbooki gniły, bo zawierały własną, nieaktualną treść, a deduplikacja po nazwie blokowała aktualizację. Rozwiązanie: skille pobierają kroki z CLAUDE.md jako jedyne źródło prawdy.

### 2026-07-27 — Cicha utrata danych przy zapisie runbooka
Metoda `zapisz()` gubiła nieznane pola istniejącego wpisu, nadpisując całość. To klasa cichej utraty danych przy aktualizacji. Naprawiono przez scalanie pól.

### 2026-07-27 — Brak funkcji aktualizacji runbooka
W systemie _ZIARNO nie istniała funkcja aktualizacji istniejącego runbooka, a deduplikacja po nazwie blokowała poprawę. Dziś dodano, ale wada architektoniczna: każda procedura po zapisie gnije.

### 2026-07-27 — Gnicie runbooków przez własną treść
Runbooki W11 zgniły, bo zawierały własną treść zamiast pobierać z CLAUDE.md. Rozwiązanie: skille muszą pobierać kroki z jedynego źródła prawdy, a nie duplikować.

### 2026-07-27 — Testy na starym Fujitsu >2 min to normalne
Stary komputer Fujitsu powoduje, że 2584 testy trwają ponad 2 minuty. Ustalono nie dawać limitu czasu, tylko cyklicznie sprawdzać, czy proces żyje.

### 2026-07-27 — Order zawsze z zyskiem zakończony
Podstawowe motto: każdy order musi być postawiony i zamknięty z zyskiem. To fundament wiarygodności i spójności systemu.

### 2026-07-20 — 20 sprzeczności w Refleksji, 3 pilne
Audyt startowy wykrył 20 sprzeczności, w tym 3 pilne: audytu/nowy, chmura/lokal/naprawa, false/faza – wymagają przeglądu.

### 2026-07-20 — Brudne drzewo – auto_lekcja_przetworzone.txt
Audyt startowy wykazał 3 dopisane linie przez automat w pliku bibliotheca_ulpia/dane/auto_lekcja_przetworzone.txt. Nie jest to zmiana ręczna – wymaga decyzji Cezara.

### 2026-07-20 — MoE niewykonalne na 6GB VRAM
Mixture of Experts wymaga trzymania wszystkich ekspertów w pamięci jednocześnie. 4 eksperty po 7B wymagają ~28B RAM – na RTX 4050 (6GB) to niemożliwe.

### 2026-07-20 — Brak metadanych to źródło bałaganu
64 dokumenty w docs/ mają zero nagłówków metadanych. Audyt nie wie, czym dokument jest, przez co bramki (np. W5, W10) opierają się na ręcznie wpisanych wyrażeniach zamiast na strukturze. To nie skaluje się do 213 plików .md.

### 2026-07-27 — Mutacja przeżyła przez luźną asercję testu zasięgu
Test zasięgu miał asercję 'zbadane ≥ 8+40' zamiast 'równość z policzonym zasięgiem'. Luźny próg przepuszczał zawężenie bramki z 73 do 65. Poprawiono na ścisłą równość; mutacja padła.

### 2026-07-26 — Średnie śledzie w 1L za długie
Medium tracks w pierwszej lidze datasetu ZENITH mają średnio 10K linii, co znacznie przekracza limit 2K. Obniża to jakość danych treningowych i wymaga kryteriów kwalifikacji.

### 2026-07-26 — Commitowanie desktop paths łamie przenośność i PII
W kronice znaleziono bezwzględne ścieżki typu ~\Desktop. Należy używać zmiennych środowiskowych lub przechowywać referencje wewnątrz repozytorium. To narusza bezpieczeństwo i przenośność.

### 2026-07-26 — Bezpośrednia edycja sigillum_probationis.json narusza zasadę
Plik sigillum_probationis.json jest magazynem (ledger) i musi być aktualizowany wyłącznie przez narzędzia sigillarium lub codex_probationum.py. Ręczna edycja jest złamaniem reguły CLAUDE.md i README.md.

### 2026-07-26 — cubic-dev-ai trafny w 20/22, 2 fałszywe alarmy (w tym jedyne P1)
cubic-dev-ai w PR #133 zgłosił 22 zastrzeżenia: **20 słusznych, 2 fałszywe**. Fałszywe to
(1) jedyne **P1** — halucynacja cytująca dwie NIEISTNIEJĄCE reguły o zakazie edycji
`sigillum_probationis.json`; (2) „wrzutnia/consilium nie istnieje" — istnieje, jest
gitignorowany, recenzent pomylił NIEWIDOCZNE z NIEISTNIEJĄCYM. Lekcja: cytat z reguły
sprawdzaj `grep`em, zanim uznasz zarzut.

*Korekta 2026-07-27:* wpis głosił „trafny w 22/22, ale 3 fałszywe alarmy" — liczba przeczyła
sama sobie, licznik fałszywek był zawyżony, a ich nazwy zmyślone. Poprawione wobec ŹRÓDŁA
(Dziennik Nieśmiertelny, wpis `cubic133` pisany w chwili pomiaru). Zgłoszone przez cubic
w PR #134 jako P3 — recenzent miał rację, choć o skali pomylił się w drugą stronę.

### 2026-07-26 — Audyt spójności ukrywa czerwony wynik (stderr zamiast stdout)
W narzedziu audyt_spojnosci.py alarmy sa wypisywane na stderr (linie 1160-1163), podczas gdy hook zbiera tylko stdout. W efekcie czerwony audyt jest niewidoczny w wydruku startowym - sesja wyglada ciszej niz zdrowa. To odwrocona wersja wady klasy 'milczenie udajace wynik' z apert26.

### 2026-07-22 — tail w rurze testów fałszuje kod wyjścia
Komenda `python tests/run_tests.py | tail` zwraca kod wyjścia `tail`, nie testów – maskuje oblane testy (exit 0 mimo 1 porażki). Należy unikać `tail` w rurze lub używać oddzielnej obsługi.

### 2026-07-20 — Audyt spójności pełna harmonia
84 neurony, 15 zwiadowców, 18 elit, ruff czysto, MAPA_KLUCZY pełna – system w pełni harmonijny.

### 2026-07-26 — Path('/home/tiro') na Windows nie działa z startswith('/')
Path('/home/tiro') na Windows normalizuje się do \home\tiro, więc startswith('/') zwraca False. Abstynencja działała tylko w jedną stronę. Naprawa mechanizmem, nie łatką.

### 2026-07-26 — Audyt czerwony niewidoczny przez hook stdout
Hook utrwala tylko stdout, alarmy audytu lecą na stderr. Przy czerwonym wyniku stdout jest pusty – wygląda ciszej niż zielony. Klasa wady z apert26: milczenie udające spokój.

### 2026-07-26 — TIRO: 153 uzyteczne pary = 15% progu 1000
Zbior treningowy TIRO to 348 surowych/153 uzytecznych par, co stanowi 15% docelowego progu 1000. Wymaga kontynuacji sniwa (zadanie E3) przed uruchomieniem pelnego treningu.

### 2026-07-26 — Brak kluczy MEXC uniemozliwia live trading
MEXC_API_KEY i MEXC_SECRET nie sa ustawione w srodowisku. Zero realnych orderow pomimo gotowego kodu (ccxt 4.5.59). Niezbedne do przejscia na live.

### 2026-07-26 — Testy 2882/2885 - 3 obalone, w tym jedna nowa wada
Dwie porazki wynikaja z niesledzonego consilium (znane), trzecia to osobna wada wymagajaca analizy. Pelny bieg testow wciaz leci w tle, stan oficjalnie nieznany.

### 2026-07-26 — Audyt spójności kończy się exit 1 i hook milczy
Podczas audytu środowiska komenda zakończyła się kodem błędu (exit 1), a hook w kroku 0 nie wyświetlił żadnej treści – to klasyczna wada 'milczenie udające wynik'.

### 2026-07-20 — Hipoteza B potwierdzona OOS
Ważenie głosów IC (Legatus) daje +3.6pp na 5/5 parach poza próbą – czeka na zgodę Cezara na wpięcie do kodu.

### 2026-07-20 — Audyt exit 0 nie oznacza prawdy
INDEKS_IMPERIUM.md podaje dwie różne liczby neuronów: 299 w nagłówku (data 2026-06-09) i 87 w sekcji MAPA KODU. Audyt przepuszcza, bo W5 czyta tylko z MAPA KODU. To dowód, że dokument może kłamać obok bramki.

### 2026-07-20 — Hotspoty: _py_supertrend i _py_volume_profile
Czysto-pythonowe pętle O(okno) na wskaźnikach supertrend i volume_profile są ciężkie (okno 251, wiele symboli). Kandydaci do wektoryzacji numpy.

### 2026-07-26 — Wynik BREVIARIUM 2882/2882 dotyczy innego kodu
Testy uruchomione w tle (BREVIARIUM) zwróciły wynik 2882/2882, ale ten wynik pochodzi z innej wersji kodu niż dzisiejsza – nie można go używać do oceny bieżącego stanu.

### 2026-07-26 — Klasa wady apert26: milczenie udające poprawne działanie
Wada polegająca na tym, że hook nie drukuje nic, choć powinien raportować stan. Wymaga wyczulenia przy interpretacji wyników audytu.

### 2026-07-26 — BIB-032 O'Hara – PDF skanowany, OCR niedziałający
Książka BIB-032 (O'Hara) to skanowany obraz PDF. OCR generuje śmieci. Zgodnie z Prawem I (zero fabrykacji) nie została zindeksowana w RAG. Status: pominięta.

### 2026-07-20 — Rozbieżność baneru startowego: pokazuje CHMURA zamiast LOKAL
Baner z hooka centrum_pamieci głosi 'Środowisko: CHMURA', ale żywy detektor wykryj_srodowisko() zwraca 'lokal'. Źródło baneru jest nieaktualne. Do naprawy w ramach higieny.

### 2026-07-20 — Środowisko lokalne z pełnym dostępem do książek i cache
Empirycznie potwierdzono: Claude działa na laptopie Pixel (Windows 10) w katalogu /c/Projekty/imperial-mesh-vortex. Dostępne wszystkie 69 książek (559 MB) w bibliotheca_ulpia/ oraz RAG tekst_cache (59 MB). Ciężka robota z książkami jest teraz możliwa.

### 2026-07-20 — Przekroczenie limitu sekcji LEKCJE
Sekcja LEKCJE ma 27 234 znaki przy limicie 24 000 – wymaga konsolidacji najstarszych wpisów (P0).

### 2026-07-20 — Audyt dotyczy tylko imperium/biblioteki/, inne katalogi pomijane
Warstwa 11 audytu sprawdza meldunek tylko w imperium/biblioteki/. Organy w imperium/cesarz/ i narzedzia/ są poza zasięgiem – exit 0 może kłamać. Rozszerzono na wszystkie organy + narzedzia/ (nowa warstwa 17).

### 2026-07-20 — Legalne abstynencje zmysłów zidentyfikowane
Niektóre neurony legalnie nie głosują: PSY-01 (funding=8e-5, brak ekstremum), PSY-04 (OI_PREV==OI, 1. odczyt), NEWS-02/03/04 (stan kroczący ≥2 bary), RADAR/N/CP (potrzebują serii cen – nie podano w teście). Zero martwych głosów.

### 2026-07-20 — 20/22 moduły żywe na realnych danych, 2 warunkowo ciche
Sonda diagnostyczna wykazała, że AUG-01 milczy z powodu braku aktywnego zdarzenia, a RADAR-05 z powodu słabej korelacji lead-lag (<0.20). NEWS-03/04 ożywają po rozgrzewce. Stan faktyczny: 20/22 ŻYWE po rozgrzewce, pozostałe 2 to poprawna abstynencja.

### 2026-07-20 — NEWS-03/04 wymagają min. 2 barów rozgrzewki
Moduły NEWS-03 (sentyment delta) i NEWS-04 (attention spike) mają stan kroczący i potrzebują ≥2 barów z feedem, by wygenerować sygnał. Po jednym barze rozgrzewki ożywają.

### 2026-07-20 — Warunkowe milczenie AUG-01 i RADAR-05
AUG-01 milczy gdy brak aktywnego zdarzenia (bramka EVENT_*). RADAR-05 (LEAD_BTC) abstynuje gdy |korelacja lead-lag| < 0.20 – celowa bramka projektowa, nie defekt.

### 2026-07-20 — Tabularium w trybie miękkim nie blokuje commita
Tabularium wykryło 10 dokumentów z przestarzałymi metadanymi (stan_na), ale działa w trybie miękkim – nie blokuje commita. Może to być celowe, aby nie hamować prac, ale wymaga świadomości, że dokumenty nie są w pełni aktualne.

### 2026-07-20 — CODEX gubi wyniki spoza schematu AB/IC
Ledger zna tylko typy AB i IC, porównanie interwałów było trzykrotnie zgłaszane jako luka, ale nigdy nie naprawione. Dodano typ POMIAR/INTERWAŁ i arkusz 'Pomiary'. Główny werdykt poprzedniej sesji odzyskany i dopisany wstecz.

### 2026-07-20 — Zawartość pliku w wrzutni
Plik z wrzutnia to dump rozmów z Hyginusem (DeepSeek) zawierający research hybrydy LLM: modele 3B, LoRA, LARSA/AlphaQuanter, Fin-R1, Unsloth/QLoRA, fine-tuning na chmurze. Wątek hybrydy-ucznia od linii 2163.

### 2026-07-20 — CODEX gubił wyniki spoza AB/IC – luka 3x zgłoszona
Pomiar interwałów (4h +3.26 / 1d -3.03 / 1h -3.37 / 15m -5.71) nie mieścił się w schemacie ledgera. Sugestie z 07-19, 07-20 i 07-20 nie zostały naprawione aż do tej sesji – brak mechanizmu, nie tylko wpisu.

### 2026-07-20 — Dispensator był organem-widmem
Kod imperium/cesarz/dispensator.py (152 linie) nie był zameldowany w żadnym dokumencie. Dotychczasowy audyt sprawdzał tylko imperium/biblioteki/, pozostawiając luki w innych katalogach.

### 2026-07-20 — Hook startowy pominął auto-pull przy brudnym drzewie
Gałąź była o 30 commitów za remote, bo hook pominął pull, gdy drzewo było brudne. Wymusiło to rebase z remote i rozstrzygnięcie konfliktu tylko w liniach daty.

### 2026-07-20 — Testy W6 czerwone – data w README/MANIFEST starsza niż commit
Dwa testy w Warstwie 6 oblały, bo README.md i docs/MANIFEST_KODU.md deklarowały datę starszą niż ostatni commit. Zgodnie z Prawem XVIII to błahostka – naprawiono samodzielnie.

### 2026-07-20 — Petla live karmi RADAR i RS
Sprawdzono, że pętla live (petla_live.py) karmi RADAR (skanuj linia 422) oraz cross-sectional RS (C-01, linia 437), więc w trybie multi-symbol RADAR też ożywa. Infrastruktura E kompletna.

### 2026-07-20 — Audyt spojnosci i skan wad przed pushem – pelna harmonia
Przeprowadzono audyt spojnosci (ruff W13 + dokumenty W14) oraz heurystyczny skan wad. Oba zakonczone exit 0 – stan kodu spojny przed commitem.

### 2026-07-20 — Windows cp1250 wymaga PYTHONIOENCODING=utf-8
Konsola Windows w cp1250 wywala się na emoji. Aby testy i audyt działały poprawnie, należy ustawić zmienną środowiskową PYTHONIOENCODING=utf-8 przed każdą komendą.

### 2026-07-21 — Cichy audyt – hook nie drukował wyniku przy uruchomieniu
Audyt złapał nowy organ w trzech warstwach naraz (W11, W15, W17), ale hook nie wyświetlił wyniku. To klasa 'mechanizm, który przy awarii wygląda na sprawny' – naprawiono.

### 2026-07-20 — Winget dostępny jako narzędzie do instalacji
Na laptopie Cezara dostępne jest winget (Windows Package Manager) – może służyć do cichej instalacji djvulibre i innych narzędzi bez uruchamiania interaktywnych instalatorów.

### 2026-07-20 — Neurony on-chain ożywają na realnej dacie
Neurony OC-06 (S2F) i OC-08 (inflacja) były martwe w audycie z powodu sztucznego timestamp 1970. Na realnej dacie (block height 956179, S2F=180, inflacja 0.555%) oddają głos. OC-07/Z-06/Z-07 legalnie NEUTRAL.

### 2026-07-20 — Ograniczenie model merging – ta sama architektura
Scalanie wag (SLERP/TIES) działa tylko w modelach o identycznej architekturze i tokenizerze. Nie da się zlać Gemmy z Llamą – to ograniczenie fizyczne, a nie narzędziowe.

### 2026-07-22 — Leksykon potwierdzał samego siebie – fałszywe wpisy
Leksykon zbudowany tylko z nazw plików generował fałszywe dowody (np. 'order_flow' – jedyne wystąpienie w WPISIE leksykonu). Naprawiono u źródła: weryfikacja czyta rzeczywisty kod, nie własne deklaracje.

### 2026-07-22 — LIBRA MESSIS – metryka nasyca się przez wadliwy dzielnik
Dzielnik kandydatów nie radzi sobie z formatem `### 1. **Nazwa**` – łączy 21/33 cząstek w jeden blok, przez co metryka nasyca się (95%) i nie odróżnia ramion. Naprawiono parser.

### 2026-07-22 — Backticki w powłoce podmieniają tekst
Prozy z backtickami (np. `element`) przekazywane przez `python -c` w bashu ulegają podmianie – wnioskiem dyscyplina: unikać tej konstrukcji, używać plików tymczasowych.

### 2026-07-20 — Audyt spójności ma ślepe plamy – whitelist bez C/D, ruff pomija skrypty
CLAUDE.md KROK 0 whitelist nie zawiera kategorii C i D (fałszywy alarm), a `audyt_spojnosci.py` nie skanuje `skrypty/` – dwa F541 przechodzą jako 'czysto'.

### 2026-07-21 — Archiwum lekcji niewidoczne dla szukaj()
Schłodzone lekcje mają inny nagłówek w pliku, więc parser modułu nie czyta archiwum. Luka powstała przy wdrażaniu chłodzenia. Wymaga poprawy parsowania.

### 2026-07-20 — Samo-recenzja przed pushem – wymog procesu
Cezar zadal samo-recenzji z uzyciem wzorca high-effort recall-biased przed pushem. Zastosowano metode 'review target --diff' – potwierdzono, ze jest to wymagane przed kazdym commitem.

### 2026-07-20 — Regresja danych w katalogu ksiąg – enrichment nadpisał poprawne wartości
10 wpisów straciło autora/tytuł (Kissell → Nieznany, garble LŁpez). Przyczyna: calibre placeholder nadpisał dane z plików.

### 2026-07-20 — Stan neuronów: 84, w tym 78 aktywnych, 6 wyciszonych
Potwierdzono liczbę neuronów oraz ich status. 22 neurony (rodziny NEWS, PSY, RADAR, OC, C, V, Z) czekają na adaptery/dane – to stan zgodny z Prawem XV.

### 2026-07-20 — Potrójna symbioza audit-sigilium: mechanizm wykrywa własne organy w wielu warstwach
Audyt W11/W15/W17 złapał nowe sigilium (runbook, licznik w README, rekord w codicilu) – symbioza działa przeciw autorowi. Wymusza to ostrożność przy dodawaniu nowych elementów.

### 2026-06-30 — Kruchość hardcodowanych liczników neuronów w testach
Wprowadzenie 47. neuronu złamało testy z hardcoded 46. Konieczne dynamiczne wykrywanie liczby neuronów lub automatyczne generowanie testów.

### 2026-06-30 — Signal Signature – struktura sygnału
Każdy sygnał w systemie IMV ma pola: confidence, adversary_confidence, final_confidence, source, reasons. To standard dla wszystkich modułów – umożliwia filtrowanie i debatę senatorską.

### 2026-06-30 — Synchronizacja liczników w testach przy dodawaniu neuronów
W-053 dodał 47. neuron (H-01), ale testy miały zakodowane 46 – konieczność aktualizacji hardcoded wartości w test_integracja.py. Lekcja: każda zmiana liczby neuronów wymaga przeglądu testów.

### 2026-06-30 — Wartości mocków muszą mieścić się w zakresach detekcji neuronów
Podczas tworzenia testów okazało się, że mocki muszą precyzyjnie trafiać w progi neuronów (np. FUNDING_RATE > 0.001, LONG_SHORT_RATIO między 0 a 1). Niewłaściwe wartości powodują fałszywe wyniki.

### 2026-07-20 — README/requirements kłamią – testy wymagają TA-Lib mimo deklaracji
Brama celowo rzuca RuntimeError bez TA-Lib, a dokumentacja twierdzi 'testy bez zależności'. Fałszywa obietnica dla użytkownika.

### 2026-07-20 — Test K1 czerwony – martwy assert na 5 przy gitignorowanym CSV
test_realne_dane_1h twardo assertuje `==5`, ale CSV jest gitignorowane od 4 lipca 2026. Test zawsze pada na świeżym klonie – wymaga zmiany (skip albo dynamiczna detekcja).

### 2026-07-20 — Zwiad bibliotekarza tylko 1/5 tematów
Hyginus przeskanował tylko 1 z 5 domyślnych tematów (mean reversion). Pozostałe 4 (momentum, regime detection, order flow, position sizing) nie ruszane. Kandydaci nie mają pomiaru redundancji ani walidacji areną.

### 2026-07-20 — Hyginus znalazł 2 kandydatów
Z tematu 'mean reversion' znaleziono Model Vasicka i Cross-sectional mean reversion, jeszcze bez walidacji.

### 2026-07-21 — Problem z \b w regexie dla identyfikatorów BIB z podkreślnikiem
\b nie zamyka się przed '_', więc 'BIB-006_Carson' nie jest wykrywany jako osobne słowo. To znana klasa z Księgi Wad (#53). Naprawiono w PROBATORZE przez użycie innej granicy (np. (?:^|[\s,;.!?])).

### 2026-07-21 — Auto-lekcja przekracza limit znaków – potrzeba chłodzenia
Auto-lekcja dopisała 21 wpisów z 3 sesji, limit 24000 znaków pęknięty. Konsolidacja co sesję to alarm wiecznie żywy. Lekarstwo: auto_lekcja sama egzekwuje limit przy zapisie.

### 2026-07-21 — Auto-lekcja nie egzekwuje limitu przy zapisie
Dotychczas auto_lekcja dopisywała wpisy bez sprawdzania limitu, co powodowało przepełnienie i fałszywy alarm przy każdej sesji. Rozwiązanie: wpięcie konsolidacji w metodę zapisu.

### 2026-07-20 — Luka pokrycia 4h – tylko 10 par zamiast 15
Pomiar wykazuje brak plików 4h dla BNB/BTC/DOGE/ETH/SOL. Wpływa na redukcję kombinacji do 40 zamiast potencjalnych 45.

### 2026-07-20 — Wynik WF-IC dla 15 par 4h
32/49 neuronow ROBUST, 17 szum/niepewne. Czołówka: EXP-13, SMC-01, V-02/V-13/V-14, rodzina X-*. UWAGA: EXP-13 (6 okien), SMC-01 (5), V-13 (3) maja malo okien -> ROBUST slabiej podparty niz X-17/X-01 (25 okien).

### 2026-07-21 — Aktualizuj_lekcje to bliźniaczy kanał wzrostu objętości
Funkcja aktualizuj_lekcje również powiększa sekcję LEKCJE, ale nie była objęta ogranicznikiem. Wprowadzono parę miar dla obu funkcji, by egzekwować limit także przy aktualizacji.

### 2026-07-20 — Statystyki zwiadowców i strategii
15 zwiadowców (13 aktywnych, 2 wyciszonych), 18 neuronów elitarnych, 20 strategii z 34 kluczami – Klucznik spójny.

### 2026-07-20 — Background task może dać pusty output
Zadanie uruchomione w tle (z &) nie zwróciło żadnego outputu (0 bajtów). W praktyce lepiej uruchamiać w foreground, aby uzyskać wynik.

### 2026-07-20 — Teza zwiadowcy wymaga pomiaru, nie wiary
Subagent-zwiadowca twierdził ~25 miejsc zip w Bramie - faktycznie 10. Twierdził brak ochrony w diagnostyce korelacji - 4/4 już strzeżone. Kandydat ≠ prawda. ZASADA WERYFIKACJI obligatoryjna przed naprawą.

### 2026-07-20 — EXP-13 GARCH: niska dekorelacja + stabilny skill
Średnie max|ρ| = 0.141 (poniżej progu 0.20), IC = 0.247/0.245/0.254 dla h=1/6/30. Potwierdza filar siły i realny sygnał predykcyjny na wszystkich parach.

### 2026-07-20 — djvu wymaga djvutxt (djvulibre), nie calibre
Konwersja djvu do tekstu wymaga narzędzia 'djvutxt' z djvulibre; calibre historycznie nie czyta djvu. Wszystkie 5 ksiąg do domknięcia QNT/RLA/Aronson to djvu – calibre jest dla nich bezużyteczne.

### 2026-07-20 — Asymetria otwarcia i zamknięcia sesji
Otwarcie sesji nie ma egzekwowanej checklisty, w przeciwieństwie do 9-krokowej checklisty zamknięcia. Ryzyko pominięcia kluczowych kroków startu.

### 2026-06-30 — Audyt źródła pure-Python w Bramie: brakowało _PURE_PYTHON_INDICATORS
Wszystkie wskaźniki w Bramie miały źródło TA-Lib. Dodano zbiór _PURE_PYTHON_INDICATORS (11 wskaźników) i warunek SOURCE_TAG_PY w compute(). Naprawiono rozróżnienie źródła dla wskaźników własnych.

### 2026-06-30 — HA doji: strict > zamiast >=
HA_BULL = c > o (nie >=) — doji neutralny, nie byczy.

### 2026-07-20 — API-widma to osobna klasa błędu od dokumentacyjnego gnicia
Spłata długu gnicia nie wykrywa widm API (pliki istnieją w kodzie, ale w innym miejscu lub są martwymi komendami). Warstwa 16 wykryła 3 widma: mexc_feed.py, calculator_gate.py, veto_check.py. Różnica między gnicie a widmem kluczowa dla architektury audytu.

### 2026-07-21 — _ jest znakiem słownym –  nie zamyka BIB-006_Carson
Wzorzec regex  nie zamykał się na identyfikatorze BIB z podkreśleniem. Złapane przez test negatywny. Wpis do Księgi Wad.

### 2026-07-21 — Archiwum lekcji ma inny nagłówek – schłodzone lekcje niewidoczne dla szukaj()
Parser modułu LEKCJE nie obsługiwał nagłówka archiwum, przez co po schłodzeniu lekcje znikały z wyszukiwania. Luka wykryta i naprawiona.

### 2026-07-21 — Archiwum lekcji ma inny nagłówek – szukaj() go nie widzi
Schłodzone lekcje do archiwum mają inny nagłówek niż główna sekcja, przez co funkcja szukaj() w module nie przeszukuje archiwum. Wykryto i naprawiono.

### 2026-07-20 — Runbooki W11 gniją – nieaktualna treść i duplikacja CLAUDE.md
Runbooki W11 zawierają własną, ręcznie wpisaną treść (np. 'git push -u origin') zamiast pobierać kroki z CLAUDE.md – jedynego źródła prawdy. Ponadto funkcja dodaj() dedupuje po nazwie, co uniemożliwia aktualizację istniejącego runbooku.

### 2026-06-30 — W6 milczące pominięcie przy braku 'Stan na:'
Audyt W6 nie raportował błędu gdy brak 'Stan na:'. Dodano else skutkujący błędem oraz rozszerzono regex na markdown.

### 2026-06-30 — Zasada symbiozy zamiast zero duplikatów
Moduły mogą być wielofunkcyjne, jeśli każdy pokrywa INNY aspekt (np. 4 moduły wielorybów każdy na inne dane). Złe = 5 modułów czytających ten sam kanał. Test: 'Co unikalnego wnosi ten moduł?'

### 2026-07-21 — Alarm i konsolidacja liczyły niezależne progi – sprzężenie
Próg alarmu (24000) i cel chłodzenia (22000) były niezależne – obniżenie progu cicho psułoby chłodzenie. Naprawiono ujednolicając źródło.

### 2026-07-21 — PROBATOR wykrył realny nieugruntowany plon Hyginusa mimo promptu
2367 znaków w kolejce Hyginusa bez żadnego cytowania źródła, choć prompt wyraźnie tego wymaga. Organ wychwycił to przy pierwszym pomiarze.

### 2026-07-21 — Znaleziono realnie nieugruntowany plon Hyginusa w kolejce
Pierwszy bieg Probatora na realnym plonie wykrył 2367 znaków kandydatów bez żadnego powołania na źródło, mimo że prompt tego żądał. Potwierdzona potrzeba weryfikacji.

### 2026-07-21 — Znak _ jest słowny, więc \b nie zamyka się w identyfikatorach z podkreślnikiem
Detektor cytatów używał \b, co nie oddzielało poprawnie identyfikatorów typu BIB-006_Carson. Poprawiono logikę granic w Probatorze.

### 2026-07-20 — EXP-14 Kyle: bardzo niska korelacja + wysoki IC
Średnie max|ρ| = 0.087 (prawie ortogonalny do reszty roju), IC = 0.301/0.302/0.308. Silny wkład informacyjny bez redundancji.

### 2026-07-20 — EXP-15 PIN martwy na wszystkich parach
Pomiar potwierdził, że EXP-15 (PIN) nie generuje sygnału na żadnej z 40 kombinacji (15 par × 3 TF). Już wcześniej wyciszony (DOSTEPNY=False), ale weryfikacja usztywnia decyzję.

### 2026-06-30 — Audyt dokumentacji wymaga egzekwowania
Użytkownik nakazał: przed dalszymi wdrożeniami należy zaktualizować wszystkie dokumenty z INDEKS_IMPERIUM i dodać ich sprawdzanie do audyt_spojnosci.py. Obecnie sprawdzane tylko 7 z ~32 plików.

### 2026-06-30 — Meta-gate defensive neurons zawsze NEUTRAL kierunek
Neurony obronne (Z-01, N-01, H-01, OC-05) ustawiają pewnosc_przeciwnika zamiast kierunku, wywołują s.policz_finalna() — to wzorzec dla wszystkich bram obronnych.

### 2026-06-30 — 12/17 bloków strategii miało błędne klucze w KATALOGU
Stare klucze projektowe (np. XII-08) nie istniały w kodzie. Audyt W9 wykrywa obce klucze w blokach zaimplementowanych strategii. Wszystkie 17 zsynchronizowane.

### 2026-07-20 — Pure-Python funkcje cicho produkują błędne wyniki przy nierównych seriach
TA-Lib głośno rzuca Exception, ale VWAP i VWAP_STD milcząco dają błędne wyniki (różnica 10.0, ~7%). Pieczątka audytu kłamie: input_len=100 przy rzeczywistych 80 barach. Złamanie Praw XIII i I.

### 2026-07-20 — Mechanizm zasiewu połyka regex z checklisty
Funkcja 'zasiej_startowe' cicho ignoruje pole 'regex' wpisu w checkliście – wzorce w Księdze Wad nigdy nie skanowały. Przyczyna: domyślna inicjalizacja pomija nieobowiązkowe klucze.

### 2026-06-30 — Podczas implementacji pomijano aktualizację dokumentacji modułowej (KALKULATOR_LEWARA.md, IGRZYSKA_IMPERIUM.md, GENERAL_LEGATUS.md)
Użytkownik zwrócił uwagę, że dokumentacje specyficzne dla modułów nie były aktualizowane ani egzekwowane przez audyt_spojnosci.py. Nakazano audyt wszystkich dokumentów z indeksu.

### 2026-06-30 — Archiwizacja bez przeczytania pliku prowadzi do utraty ważnych danych
ARSENAL_IMPERIUM (zweryfikowany katalog ~220 narzędzi) i WZORZEC_DNSS (referencja architektury) zostały błędnie zarchiwizowane. Wymusiło to dodanie Zasady Archiwizacji do CLAUDE.md.

### 2026-06-30 — Konieczność audytu dokumentacji przed dalszym rozwojem
Użytkownik zwrócił uwagę, że dokumentacja nie jest aktualizowana podczas implementacji wizji; nakazał audyt wszystkich dokumentów z INDEKS_IMPERIUM względem kodu i dodanie egzekucji w narzędziu audytu.

### 2026-06-30 — VPIN neuron nigdy nie jest kierunkowy
NeuronToxicFlow (Z-01) zawsze zwraca NEUTRAL kierunek. Jego rola to tylko tłumienie roju przez pewnosc_przeciwnika gdy VPIN>0.7. Nigdy nie głosuje na stronę.

### 2026-06-30 — DeepSeek API klucz NIGDY w kodzie ani w czacie
Zasada bezpieczeństwa: klucz DeepSeek API musi być tylko w zmiennych środowiskowych. W kodzie użyto [ZREDAGOWANO] jako placeholder. Dotyczy to wszystkich plików w Imperium.

### 2026-07-10 — Równa waga = 48.2% odtwarza diagnozę triady 48.3%
Pomiar hipotezy B na 5 parach 4h OOS daje globalnie 48.2% dla równej wagi, co odtwarza diagnozę triady 48.3% co do promila — walidacja pomiaru.

### 2026-07-20 — zasiej_startowe cicho zjada regex z checklisty
Mechanizm zasiewu wzorców nie przenosi regexu z checklisty do wzorców startowych, bo lista WZORCE_STARTOWE kończy się wcześniej. Wzorce leżą martwe w checkliście.

### 2026-07-21 — Ukryta zależność od monkeypatch w runnerze Imperium
Testy PEDES przechodzą pod pytest, ale padają pod własnym runnerem Imperium, którego shim monkeypatch nie ma metody setitem. Naprawiono bez zależności od shimu.

### 2026-07-20 — Parametry Fujitsu Lifebook E754
CPU i5-4200M Haswell 2013, 2 rdzenie/4 wątki, 2.5 GHz. RAM 16 GB (9 GB wolne). GPU Intel HD 4600 1 GB – bezużyteczne do LLM. Inferencja tylko CPU, maksymalny model 3-8B mocno skwantyzowany.

### 2026-07-20 — Testy 1648/1648 zielone – kod stabilny
Po wymuszeniu UTF-8 testy przechodzą w 100%. Fałszywy alarm w aktualizuj.ps1 wynikał z kodowania konsoli (cp1250 nie obsługuje emoji).

### 2026-07-20 — IC EXP-13/14 podejrzanie wysoki – możliwy artefakt autokorelacji
IC ~0.25-0.30, podczas gdy typowe IC >0.05 jest rzadkie. Wskazuje to na możliwość łapania autokorelacji zmienności, a nie czystego forward-return. Wymaga kontroli na nienakładających się zwrotach.

### 2026-07-20 — CODEX: 30 sugestii na 46 rekordów - dominacja sugestii
Z 46 rekordów CODEX-u 30 to sugestie (A/B 11, IC 4, pomiary 1). Proporcja sugeruje, że system gromadzi głównie nierozstrzygnięte pomysły, a nie faktyczne pomiary czy decyzje. Może to wskazywać na potrzebę przeglądu i priorytetyzacji.

### 2026-07-20 — Runbooki W11 gniją przez deduplikację po nazwie
Runbook 'Bezpieczny commit' zawiera nieaktualny krok 'git push -u', a funkcja dodaj() uniemożliwia aktualizację przez deduplikację po nazwie. Każda procedura raz zapisana pozostaje niezmienna, co prowadzi do gnicia treści.

### 2026-07-20 — Tempo przetwarzania WF-IC
~2 min/para (15 par ~30 min). BTC/ETH cięższe. Można szacować czas przyszłych uruchomień.

### 2026-07-20 — Buforowanie stdout w Pythonie
Raport WF-IC jest buforowany do końca; aby widzieć postęp na żywo, należy uruchomić skrypt z flagą -u (unbuffered).

### 2026-07-20 — Testy na starym Fujitsu trwają >2 minuty — normalne
Testy (2584) zajmują ponad 2 minuty na starym sprzęcie. Nie dawaj limitu czasu, uruchamiaj w tle i cyklicznie sprawdzaj, czy żyje. Zapamiętane na stałe, nie wracamy do tematu.

### 2026-06-30 — Zbyt sztywne progi powodują martwe neurony
BB Squeeze 4%→2.5%, RSI Div delta 2.0→0.3, Bart Pattern 30%→10% – neurony zwracały 100% NEUTRAL. Po korekcie zaczęły generować sygnały.

### 2026-06-30 — Proces deduplikacji neuronów
Podczas skanowania agent otrzymał instrukcję deduplikacji, co pozwoliło osiągnąć ostateczną liczbę 261 unikalnych neuronów zamiast potencjalnie większej liczby powtórzeń.

### 2026-06-30 — Higuchi Fractal Dimension wymaga pełnej serii – niemożliwy w Brama
D≈1.0 = trending, D≈2.0 = ranging/chaotic, D≈1.5 = random walk. Wymaga min. 50 świec do obliczenia – nie da się zredukować do pojedynczej wartości Brama. Uzasadnia wyjątek Prawa I dla Exploratores.

### 2026-06-30 — Kategoria S zarezerwowana dla SMC/Struktura
Kategoria S jest już używana przez strukturalne neurony SMC, więc nie można jej użyć dla Sentiment.

### 2026-06-30 — Halucynacje w linkach IMV: defensywne repo i anegdoty
Po weryfikacji ~320 linków przez 3 równoległych agentów okazało się, że core tech stack jest realny, ale część referencji do defensywnych repozytoriów i legend tradingowych była halucynacjami. Zapisano w ARSENAL_IMPERIUM.md.

### 2026-06-30 — DeepSeek API – endpoint i bezpieczeństwo klucza
DeepSeek API jest kompatybilny z OpenAI (base_url: https://api.deepseek.com/v1). Klucz API musi być wyłącznie w zmiennych środowiskowych, nigdy w kodzie ani czacie.

### 2026-06-30 — Separacja Kingdom Pixel od Imperium
Mieszanie zasad Kingdom Pixel (79 Zasad) z Imperium powodowało chaos. Rozwiązanie: Imperium ma własne 14 Praw, Kingdom Pixel jest archiwizowany i nigdy nie modyfikowany.

### 2026-06-30 — Neurony martwe: XII-07, X-12, A-05 (100% NEUTRAL)
Trzy neurony (RSI_14 trend, BB_UPPER, CLOSE_PREV) wykazały 100% NEUTRAL w analizie 500-barowej. Wymagają diagnostyki lub wyłączenia.

### 2026-06-30 — Niezgodność stanu MANIFEST z kodem
7 neuronów oznaczonych jako aktywne w MANIFEST_KODU.md, ale w kodzie miały DOSTEPNY=False. Poprawiono oznakowanie na 'wyciszony'.

### 2026-06-30 — Znalezione 2 neurony sieroty w mikro_neuron.py
NeuronStochRSI i NeuronFundingRate znajdowały się poza rojem neuronów, nie były importowane przez rejestr. Zostały przeniesione do odpowiednich plików.

### 2026-06-30 — API key tylko w zmiennych środowiskowych
Klucz API DeepSeek nie może być umieszczany w kodzie ani w czacie, tylko w environment variable (setx). Bezpieczeństwo.

### 2026-06-30 — Bezpieczeństwo klucza API DeepSeek – tylko env vars
Klucz API DeepSeek NIGDY nie może być w kodzie ani w czacie. Powinien być przechowywany w zmiennych środowiskowych. Kod w PLAN_DEEPSEEK.md zawiera placeholder do zastąpienia.

### 2026-06-30 — Format Katalogu Strategii
ID: [LEGION]-[STYL]-[NUM] (np. X-SC-001). Style: TR/RV/BK/RG/SC/MC/LV/HY. Każda strategia ma: Neurony WEJŚCIE, FILTR, WYJŚCIE, Dźwignia, R:R, Status.

### 2026-06-30 — OpenAlice i Hermes Agent to realne narzędzia
Zweryfikowano, że OpenAlice (4600★ GitHub) i Hermes Agent (Nous Research, 200+ LLM backends) istnieją i są aktywnymi projektami. Wcześniejsze oznaczenie jako 'niezweryfikowane' było błędne.

### 2026-06-30 — NeuronPumpDetect Z-02: 3 warunki OHLCV
Warunek 1: VOLUME/VOLUME_MA20 w [1.5, 4.0]; Warunek 2: (HIGH-LOW)/ATR_14 < 0.75; Warunek 3: OBV > OBV_EMA_20*(1+0.005). Siła = 0.55+0.30*(vol*0.4+zakr*0.3+obv*0.3). Kierunek LONG.

### 2026-07-10 — Ważenie IC podnosi rój ponad 50% na każdej parze OOS
Wynik B (ważony IC) = 51.8% globalnie, bije A o +3.6pp i przekracza 50% na KAŻDEJ z 5 par OOS. Potwierdza hipotezę B: wąskie gardło = agregacja.

### 2026-06-30 — Paradoks Parrondo jako filozofia Kameleon
Sformalizowano, że dwie przegrywające osobno strategie mogą tworzyć wygrywający ensemble. To podstawa systemu Kameleon – kluczowa zasada dywersyfikacji neuronów.

### 2026-06-30 — pewnosc_agregatu zawsze ≈1.0 – źródło strat
Stała wysoka pewność agregatu powoduje maksymalny dźwig, co prowadzi do tight stop-lossów i wielu małych strat. To jest zidentyfikowany defect.

### 2026-06-30 — Ulcer warmup: wystarczy period, nie period+1
Funkcja _py_ulcer używa c[-period:] do obliczeń, więc wymaga tylko 'period' próbek. Poprzedni warunek period+1 był błędny (off-by-one). Naprawiono w bramie kalkulatora.

### 2026-06-30 — Off-by-one warmup Ulcer i Accelerator
Ulcer warmup wymagał period+1 zamiast period (używał c[-period:]). Accelerator miał zbędny +1 w warmup slow+sma_ac. Poprawiono w _py_ulcer() i _py_accelerator().

### 2026-06-30 — Mieszanie zasad źródłem chaosu
Poprzedni projekt popadł w chaos przez mieszanie zasad Kingdom Pixel (79) z Imperium. Rozwiązanie: całkowicie nowe zasady dla Imperium.

### 2026-06-30 — CVD dystrybucja wymaga ujemnego CVD dla sygnału SHORT
Początkowo ustawiono CVD=4000, ale neuron sprawdza czy CVD jest ujemne. Poprawiono na CVD=-4000 (dystrybucja) i CVD=15000 (akumulacja).

### 2026-06-30 — Poprawione wartości mock futures dla triggerów neuronów
Początkowe wartości LONG_SHORT_RATIO=2.4 i FUNDING_RATE=0.0009 nie wywoływały sygnałów. Poprawiono: panika: FUNDING_RATE=-0.0012, LS_RATIO=0.20; chciwość: FUNDING_RATE=0.0015, LS_RATIO=0.85.

### 2026-06-30 — Kolizja nazw NeuronOrderBlock z SMC-01
Nowy neuron w trend.py nazwany NeuronOrderBlock kolidował z istniejącym SMC-01. Rozwiązano przez zmianę nazwy na NeuronOBZone.

### 2026-06-30 — Bezpiecznik Kapitału W-028: AOA 30% drawdown jako circuit-breaker
Gdy strata z AOA przekracza 30%, Scheduler blokuje wszystkie nowe sygnały i zamyka pozycje. Zintegrowany z Scheduler._bezpiecznik_ok() – sprawdzany przed każdą transakcją.

### 2026-06-30 — __pycache__ w git - usunięty i dodany do .gitignore
Po kompilacji brama_kalkulatora.py pliki cache Pythona zostały przypadkowo skomitowane. Naprawa: git rm -r --cached i dodanie __pycache__ do .gitignore.

### 2026-06-30 — Symmetric displacement w EXP-10
Pierwotnie brano tylko |Δhigh|, teraz max(|Δhigh|,|Δlow|) dla symetrycznej detekcji strukturalnego przemieszczenia.

### 2026-06-30 — Wzorzec Observer w Igrzyska umożliwia DRY
Dodanie listy obserwatorów do Igrzyska pozwala HedgeMWU i innym modułom uczyć się na tych samych wynikach transakcji bez duplikacji logiki.

### 2026-06-30 — Yang-Zhang ~14x efektywniejszy niż std(zamknięcie)
Yang-Zhang wykorzystuje OHLC, daje dokładniejszy pomiar zmienności przy mniejszej liczbie obserwacji niż tradycyjne std(close).

### 2026-06-30 — CVD dystrybucja wymaga ujemnej wartości
Neuron V-03 sprawdza ujemne CVD dla SHORT, nie spadek względem poprzedniej wartości; poprawiono mock dystrybucji na CVD=-4000.

### 2026-06-30 — Poprawne equity: kapital_calkowity
W paper_trading dodano właściwość kapital_calkowity = kapital + suma zablokowanego marginu. Wcześniej używano tylko kapital, co powodowało fałszywe redukcje po otwarciu pozycji.

### 2026-06-30 — Metodologia Walk-Forward Validation
Udokumentowano WF: 90 dni treningu, 30 dni testu, 7-dniowy krok. Odchodzi się od Freqtrade/QuantConnect na rzecz własnego rozwiązania.

### 2026-06-30 — CME Gap – historyczna strategia
CME Gap miał 77% wypełnień, ale od 29 maja 2026 CME przechodzi na handel 24/7, co czyni strategię gapową nieaktualną. Należy unikać implementacji.

### 2026-06-30 — Regex W7 niebezpieczny dla domen z .md
Wzorzec W7 szukał linków z '.md' w ścieżce, ale dopasowywał też domeny (jak mdpi.com) zawierające '.md'. Lekcja: regexy dla cross-doc linków muszą ignorować zewnętrzne URL-e już na etapie dopasowania lub wczesnym continue.

### 2026-06-30 — Weryfikacja linków ujawnia halucynacje w arsenale
Spośród ~320 linków z IMV, znaleziono 5 błędnych URL i halucynacje w klastrze 'defensive repos' oraz anegdotach tradingowych. Rdzeń tech stacku jest realny.

### 2026-06-30 — Brak kategorii L (Leverage) w kodzie – 0 neuronów
Kategoria L (Leverage) jest całkowicie pusta w aktywnym kodzie, brak jakichkolwiek neuronów. Zidentyfikowano jako lukę względem dokumentacji.

### 2026-06-30 — Złoty Orzeł (XII-TR-001) – wariant EMA, nie oryginalny SMA
Strategia używa EMA 50/200 zamiast oryginalnego SMA Golden Cross. Fakt został udokumentowany jako odchylenie od kanonu.

### 2026-06-30 — Nazwy neuronów muszą być unikalne w całym systemie
Próba dodania neuronu o nazwie NeuronOrderBlock w trend.py skończyłaby się kolizją z SMC-01. Wdrożono zasadę: każda nowa klasa neuronu musi mieć unikalną nazwę; w razie konfliktu zmienić nazwę.

### 2026-06-30 — Złoty Orzeł nieaktywny na DOGE z powodu death cross
Strategia long-only (EMA50/EMA200) nie aktywowała się, ponieważ EMA50 < EMA200 przez cały okres testu DOGE.

### 2026-06-30 — Konieczność *_PREV dla wykrywania przecięć
Wartości z poprzedniej świecy (*_PREV) są niezbędne do poprawnego wykrywania przecięć linii (np. MACD), ale Brama początkowo ich nie dostarczała – dodano funkcję _second_last_valid.

### 2026-06-30 — Ulcer Index warmup wymaga tylko period próbek
Implementacja Ulcer Index w Bramie używała warunku `< period+1`, co wymuszało niepotrzebnie dłuższy warmup. Poprawiono na `< period`, ponieważ funkcja operuje na c[-period:].

### 2026-06-30 — Relative import problem solved with try/except
Przy uruchamianiu skryptu bezpośrednio, import względny (.modul) zawodzi. Rozwiązano przez próbę względnego, a w razie błędu absolutnego.

### 2026-06-30 — Orphan key X-SC-003 (BROOKS M2B vs IMV-SC-003)
Klucz 'BROOKS M2B' istniał w kodzie, ale katalog rejestrował go jako 'IMV-SC-003'. Wyrównano do kodu zgodnie z Prawem XIX.

### 2026-06-30 — Nazwy strategii IMV-DEF niezgodne z kodem
Kod używał 'TARCZA PRETORIANÓW' / 'MUR KONTRWYWIADU', katalog miał 'TARCZA WASH' / 'GÓRA LODOWA'. Wprowadzono dual names (rzymska + funkcja).

### 2026-06-30 — Testy nieaktualne po obudzeniu neuronów
Testy zakładały DOSTEPNY=False dla PSY i V-03. Po Fazie B/C testy failowały. Przepisano: test_futures_aktywuj_i_usypiaj, test_cvd_aktywuj_i_usypiaj, test_stan_globalny_przywrocony.

### 2026-06-30 — Zbyt ostre progi w neuronach – poprawa czułości
X-12 (BB squeeze): 4%→2.5% (BTC daily rzadko osiąga 4%). XII-07 (RSI divergence): 2.0→0.3 (sąsiadujące bary rzadko >2). A-05 (Bart pattern): 30%→10% (30% Donchiana zbyt rzadkie).

### 2026-06-30 — Stop Hunt – wzorzec sweepu płynności
Market makerzy pushują cenę poniżej/ponad stop lossy, zbierają płynność, a potem zawracają. Neuron StopHunt wykrywa to za pomocą Donchian channel.

### 2026-06-30 — 403 Push Permission Error
Początkowe pushy nie działały z powodu błędnych uprawnień GitHub App. Użytkownik naprawił uprawnienia, push ostatecznie powiódł się.

### 2026-06-30 — Permutation Entropy >0.85 = chaos → NEUTRAL
NeuronPermEntropy (N-01): PE>0.85 → NEUTRAL 'chaos', PE<0.65 → podąża za mikro-ruchem, mid → NEUTRAL niska pewność. Meta-gate nie głosuje kierunkowo przy wysokiej entropii.

### 2026-06-30 — kapital_calkowity = free + locked margin (true equity)
BezpiecznikKrzywejKapitalu używał tylko wolnego kapitału, co fałszywie triggerowało REDUCED przy otwarciu pozycji (margin przechodzi free→locked). Poprawiono: kapital_calkowity = self.kapital + sum(p.kapital_zablokowany).

### 2026-06-30 — TA-Lib blokerem 9 modułów
Brak TA-Lib (pip install TA-Lib) uniemożliwia uruchomienie 9 modułów systemu. To najważniejsza zależność do odblokowania.

### 2026-06-30 — TA-Lib na Windows 10: pip install działa w 2026
Współczesna instalacja TA-Lib na Windows jest prostsza — pip install TA-Lib często działa, fallback do wheeli z github.com/cgohlke/talib-build.

### 2026-06-30 — Pre-commit: stash isolation dla staged
Dodano git stash push --keep-index --include-untracked + trap przywracający working tree. Testy działają na staged, nie na working tree.

### 2026-06-30 — Czytnik symbol z nazwy pliku: split('_')[-2]
Fallback symbol z nazwy pliku Binance_BTCUSDT_1h dawał BINANCE przez split('_')[0]. Poprawiono na [-2].

### 2026-06-30 — SkalowanieFrakcjaDD: ciągłe skalowanie pozycji od DD
frakcja = max(min_frakcja, min(1.0, 1.0 - dd/prog_max)). Domyślnie prog_max=20%, min_frakcja=10%. Wpływa na rozmiar pozycji przez frakcja_dd w PlanPozycji.

### 2026-06-30 — Wash Trading Detection: Benford chi² + round-number clustering
Wash score = sqrt(benford_score * rounding_score). Benford: chi2_obs/20.09 capped 1.0. Rounding: (round_frac-0.20)/0.20 clamped [0,1]. Prog ostrzeżenia 0.35, silny 0.65.

### 2026-06-30 — CalcResult vs float w testach HURST_DFA
HURST_DFA zwraca obiekt CalcResult, nie float. Należy używać r.value, nie r.

### 2026-06-30 — Pewność vs pewność_finalna w testach
W teście Z-02 asercja musi być na s.pewnosc (>=0.55), a nie s.pewnosc_finalna, bo ta uwzględnia WAGĘ.

### 2026-06-30 — Zasada 2% kapitału i R:R minimum 1:2
Max ryzyko 2% kapitału na transakcję lewarowaną. Wymagany stosunek Risk:Reward minimum 1:2. Wyjątek: Druckenmiller Mode (pewnosc >0.92) pozwala na 5% kapitału i dźwignia ×1.5.

### 2026-06-30 — Wzór ceny likwidacji LONG/SHORT
LONG: Entry * (1 - 1/Leverage + 0.005). SHORT: Entry * (1 + 1/Leverage - 0.005). Stop-loss = 50% drogi do likwidacji. OPLATA_UTRZYMANIA = 0.005 (Binance/MEXC).

### 2026-06-30 — ImportError w legatus.py przy uruchomieniu bezpośrednim
Relative import from .mikro_neuron fails gdy plik uruchamiany bezpośrednio. Rozwiązanie: try/except z fallbackiem do from mikro_neuron import.

### 2026-06-30 — Format CSV CryptoDataDownload wymaga specjalnego czytnika
Pliki CSV z CDD mają pierwszy wiersz URL, nagłówek w drugim, dane malejąco, timestamp w ms. Kolumna wolumenu bazowego to 'Volume' (nie 'Volume USDT'). Czytnik CSV musi to obsługiwać.

### 2026-06-30 — Slabosc: reczny parametr rezimu w strategiach
Testy na 3 scenariuszach rynkowych wykazaly, ze reczne podawanie rezimu (NORMAL, TREND_STRONG itp.) jest slabym punktem. Nastepny krok: automatyczny klasyfikator rezimu.

### 2026-06-30 — JG z GUSI Pro/Omni-Wave to ten sam JG co DNSS
Odkryto, że 'R.G. JG' (twórca GUSI Pro, Omni-Wave w bazie wskaźników) to prawdopodobnie ta sama osoba co twórca systemu DNSS (79 agentów). Potwierdza to linię Calculator Pattern.

### 2026-06-30 — Kategoria Z już zajęta przez zagrożenie
Kategoria Z (Zagrożenie) zarezerwowana dla VPIN meta-bramy (Z-01) i PumpDetect (Z-02). Sentiment nie może użyć Z.

### 2026-06-30 — Triple Barrier: SL wygrywa przy jednoczesnym trafieniu TP i SL
W metodzie oznacz_bariera, jeśli TP i SL są trafione w tej samej świecy, wygrywa SL (konserwatywnie). timeliness = 1.0 - (bar_nr-1)/max(max_bary-1, 1).

### 2026-07-10 — Katalog scratchpad nie istniał — redirect padł
Przy uruchamianiu biegów równoległych katalog scratchpad nie istniał, co spowodowało ciche niepowodzenie zapisu. Po utworzeniu katalogu bieg działa poprawnie.

### 2026-06-30 — Binance depth zwraca stringi a nie floaty
L2 order book od Binance ma ceny i wolumeny jako stringi. Dodano float(b[1]) i float(a[1]) w exp_atmabhan._imbalance().

### 2026-06-30 — Diagnostyka fałszywie alarmowała martwe neurony
Pary z 1 próbką były klasyfikowane jako 'martwe' (len(set)==1). Dodano wymóg >=2 próbek do detekcji stałej serii. Nowy klucz: pary_niedostateczne_dane.

### 2026-06-30 — pewnosc_agregatu ≈ 1.0 to root cause strat
KalkulatorLewara używa pewnosc_agregatu do wyznaczania dźwigni, ale zawsze ≈1.0 → max leverage → ciasne stop lossy → wiele małych strat. To jest pierwotna przyczyna wszystkich strat systemu.

### 2026-06-30 — Wolumen bazowy: Volume BTC/ETH ≠ Volume USDT
W plikach CDD kolumna 'Volume BTC' lub 'Volume ETH' to wolumen w kryptowalucie, a nie w USDT. Czytnik CSV wykrywa kolumnę zaczynającą się od 'volume' i różną od 'volume usdt' jako bazową.

### 2026-06-30 — Format CryptoDataDownload: linia URL i dane malejąco
Pliki CSV z CryptoDataDownload mają pierwszą linię z URL-em, drugą z nagłówkami, dane są w kolejności malejącej (od najnowszych do najstarszych). Czytnik CSV automatycznie pomija URL i odwraca kolejność na rosnącą.

### 2026-06-30 — Kanoniczna liczba neuronów: 299
299 unikalnych kluczy z KATALOG_NEURONOW.md, a nie 261/303/306/328 (stare estymaty). 27 zaimplementowanych w kodzie.

### 2026-06-30 — EXP-12 +106,692% ROI to fantazja/lookahead
Oryginalny Atmabhan ma nierealistyczne wyniki z powodu lookahead bias. Wdrożono ostrzeżenie w docstringu.

### 2026-06-30 — Martwy głos ATR_MULT w EXP-07
EXP-07 miał ATR_MULT=1.5 ale ATR nie był używany w logice. Poprawiono na ATR_MULT=0.15 i faktyczne użycie ATR.

### 2026-06-30 — Yang-Zhang ~14x wydajniejszy od std(close)
Drift-independent OHLC volatility estimator. Potwierdzono empirycznie: ~14x więcej próbek niż close-only std(close) przy tej samej długości okna.

### 2026-06-30 — CME gap edge martwy od 2026-05-29
CME uruchomiło 24/7 kontrakty futures na BTC, co eliminuje weekendowe luki cenowe. Nie implementować jako sygnału live.

### 2026-06-30 — HA doji neutralny i ATR=0
HA_BULL zmieniono z >= na > (doji neutralny). Przy ATR=0 dodano jawne zera dla HA_MOMENTUM i HA_VOLATILITY_INDEX.

### 2026-06-30 — HA bez repainting: rekurencyjny HA_Open
Heiken Ashi bez repainting wymaga HA_Open[i] = (HA_Open[i-1] + HA_Close[i-1]) / 2, a nie (Open[-1]+Close[-1])/2. Zaimplementowano w _dodaj_ha().

### 2026-06-30 — Kategoria A przeniesiona z PLANOWANE do AKTYWNE
WAGI_REZIMU_PLANOWANE zmienione z {'A','L','V'} na {'L','V'} — kategoria A jest już w kodzie z neuronami Dywizji Straży. WAGI_REZIMU: A ×2.0 (VOLATILE) i ×3.0 (PANIC).

### 2026-06-30 — Brak *_PREV uniemożliwia detekcję crossoverów
Brama nie dostarczała poprzednich wartości (RSI_PREV, EMA_PREV, MACD_HIST_PREV), przez co neurony crossoverowe były martwe. Naprawiono przez _second_last_valid() i rozszerzenie rejestru Bramy.

### 2026-06-30 — Martwy głos ATR w Night Turbo
Oryginalny Night Turbo miał ATR zdefiniowany ale nieużywany. Poprawiono: PROG_ATR_MULT = 0.5 faktycznie używa ATR.

### 2026-06-30 — Lookahead bias w SMC Engine
Oryginalny SMC engine używał .shift(-1)/.shift(-2) – patrzenie w przyszłość. Poprawiono w EXP-09: tylko bary[start:n] (przeszłość).

### 2026-06-30 — Cross jako EVENT, nie STATE
EXP-11 sygnalizuje tylko przy świeżym przecięciu (fast>slow AND prev_fast<=prev_slow), a nie na każdym barze gdzie fast>slow.

### 2026-06-30 — True Range: poprawna definicja
True Range = max(H-L, |H-prevC|, |L-prevC|). Poprawiono we wszystkich adoptowanych wskaźnikach (EXP-06..12).

### 2026-06-30 — Kategoria R w WAGI_REZIMU istniała tylko w PANIC
Sentyment (R) miał wagę tylko w trybie PANIC (veto). Dodano mnożniki dla VOLATILE (×1.3), RANGING (×1.2), NORMAL (×1.1), TREND_STRONG (×0.8).

### 2026-06-30 — Bart Pattern threshold 30% Donchian zbyt rzadki
Warunek 30% kanału Donchiana występuje ekstremalnie rzadko. Zmieniono na 10%.

### 2026-06-30 — RSI Div threshold 2.0 zbyt wysoki dla sąsiednich barów daily
Delta RSI między sąsiednimi barami daily rzadko przekracza 2 pkt. Zmieniono na 0.3.

### 2026-06-30 — BB Squeeze threshold 4% zbyt restrykcyjny dla BTC daily
Na dziennych barach BTC typowa szerokość BB to 3-8%, próg 4% był praktycznie nieosiągalny. Zmieniono na 2.5%.

