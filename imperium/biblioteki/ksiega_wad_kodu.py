"""
🐞 KSIĘGA WAD KODU — pamięć wzorców błędów (samo-leczenie, Prawo XV/XVI).

Odpowiednik `ksiega_wad` (wady setupu tradingowego), ale dla KODU. Zapamiętuje
klasy błędów, które łapie recenzja (cubic / `/code-review`), żeby NIE powtarzać ich
w przyszłości: przy pisaniu/recenzji kodu Claude sprawdza księgę NAJPIERW.

Dwie zdolności:
  • pamięć (JSONL, wersjonowana w git — wiedza uniwersalna, nie per-maszyna),
  • heurystyczny skan: `skanuj(tekst)` dopasowuje znane wzorce (regex) do kodu i
    zwraca trafienia z lekcją. To NUDGE, nie dowód (Prawo I) — sygnalizuje „sprawdź to".

DLA NOWICJUSZA: cubic (zewnętrzny bot) łapał błędy, których my sami nie sprawdzaliśmy —
bo pisaliśmy „happy path". Ta księga to pamięć „co MOŻE pójść źle", zbierana z każdej
recenzji, więc z czasem sami łapiemy to, co wcześniej łapał tylko cubic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOMYSLNA = ROOT / "bibliotheca_ulpia" / "dane" / "ksiega_wad_kodu.jsonl"

# Wzorce startowe — destylat realnych uwag cubic (2026-07). Wysokosygnałowe, niskofałszywe.
WZORCE_STARTOWE = [
    {"kat": "kontrakt", "regex": r'\.get\(\s*interwal\s*[,)]',
     "opis": "Słownik keyed interwałem czytany SUROWĄ etykietą (bez normalizacji)",
     "lekcja": "Etykieta interwału krąży w dwóch konwencjach ('4h' z czytnika CSV, '4H' w "
               "słownikach Imperium, 'H4' w strategiach). `.get(interwal, domyslne)` po surowym "
               "kluczu nie chybia GŁOŚNO — spada na fallback, więc cała warstwa wyłącza się w "
               "ciszy. Zmierzone 2026-07-29: '4h' wyłączało formację legionów Legatusa (SCALP "
               "głosował na 4H), dawało Hermesowi 60 min zamiast 240 i annualizowało Sharpe "
               "jak świece dzienne. Normalizuj OBIE strony przez "
               "`strategie.baza.normalizuj_interwal`; 'nieznany interwał' ma znaczyć naprawdę "
               "nieznany, nie 'inaczej zapisany'. Szum zmierzony: 2 trafienia / 255 plików, "
               "obydwa prawdziwe (dublowane klucze '4h'+'4H' to ta sama klasa — plaster, nie lek).",
     "zrodlo": "DISCIPULUS / A/B ucz_mwu (2026-07-29)"},
    {"kat": "odpornosc", "regex": r'req\s*\[\s*[\'"]params[\'"]\s*\]\s*\[',
     "opis": "Dostęp do pól requestu POZA try",
     "lekcja": "Parsuj pola żądania WEWNĄTRZ try — malformed request → JSON-RPC error, nie crash procesu.",
     "zrodlo": "cubic arena_mcp P1 (2026-07-05)"},
    {"kat": "kontrakt", "regex": r'ORDER BY id\b',
     "opis": "Sortowanie po id zamiast po czasie zdarzenia",
     "lekcja": "Dla danych z timestampem sortuj ORDER BY ts (id jako tie-breaker) — backfill nie udaje najnowszego.",
     "zrodlo": "cubic arena_baza P2 (2026-07-05)"},
    {"kat": "kontrakt", "regex": r'int\(\s*\w+\.get\(\s*[\'"]limit[\'"]',
     "opis": "limit z requestu bez clampu do reklamowanego zakresu",
     "lekcja": "Reklamujesz zakres (np. 1-100) → wymuś go: min(max, max(min, wartosc)).",
     "zrodlo": "cubic arena_mcp P2 (2026-07-05)"},
    {"kat": "granice", "regex": r'pytest\.raises\(ValueError\)',
     "opis": "Test progu bez przypadku None",
     "lekcja": "Reguła Test-Granic: None w progu daje TypeError, nie ValueError — dodaj jawny przypadek None.",
     "zrodlo": "cubic test_kalibrator P2 (2026-07-05)"},
    {"kat": "odpornosc", "regex": r'for .+ in .+:\s*(#.*)?\n\s+.*(connect|_polacz)\(',
     "opis": "Połączenie do bazy w pętli (I/O per iteracja)",
     "lekcja": "Batchuj zapisy — jedno połączenie na partię, nie per-element (latencja w pętli live).",
     "zrodlo": "cubic petla_live P2 (2026-07-05)"},
    # ── cubic PR#122 (2026-07-13) — wzorce składniowe, które POPRAWNY kod omija ──
    {"kat": "cache", "regex": r'pytaj_pomiary\([^)]*neuron\s*=\s*nazwa\b',
     "opis": "Wznawianie z areny kluczowane samą nazwą pliku (bez podpisu konfiguracji)",
     "lekcja": "Klucz areny/cache MUSI nieść podpis konfiguracji (frac/okno/cap/interwał) — inaczej "
               "zmiana parametru cicho podstawia nieświeży wynik. Wpuść config w klucz `neuron=` "
               "albo zwaliduj parametry z noty przed pominięciem pary.",
     "zrodlo": "cubic PR#122 ab_* P1/P2 (2026-07-13)"},
    {"kat": "granice",
     "regex": r'add_argument\(\s*[\'"]--(?:topk|top-k|prog[_-]?ic)[\'"][^)]*type\s*=\s*(?:int|float)\b',
     "opis": "Argument liczbowy sterujący kosztem API / progiem bez walidacji zakresu",
     "lekcja": "Argument sterujący kosztem (topk → rozmiar korpusu do PŁATNEGO API) lub semantyką progu "
               "(prog_ic) waliduj przy parsowaniu — type=funkcja z zakresem/skończonością, nie gołe int/float.",
     "zrodlo": "cubic PR#122 bibliotekarz/ab_pnl P2/P3 (2026-07-13)"},
    # ── sesja 2026-07-16 (TIRO/biblioteka) — wzorce ZMIERZONE na 375 plikach przed dodaniem ──
    {"kat": "wydajnosc", "regex": r'inspect\.stack\(\s*\)',
     "opis": "inspect.stack() bez context=0 — czyta PLIKI ŹRÓDŁOWE każdej ramki stosu",
     "lekcja": "Domyślne inspect.stack() otwiera i czyta plik źródłowy KAŻDEJ ramki, żeby dołączyć "
               "linię kontekstu. Gdy bierzesz sam .filename/.function — użyj inspect.stack(0): ten sam "
               "wynik bez I/O. Przy głębokim stosie w ścieżce gorącej to kilkanaście zbędnych odczytów "
               "na wywołanie.",
     "zrodlo": "self-review NOTARIUS (2026-07-16) — zmierzone: 0 fałszywek na 375 plikach"},
    # ── sesja 2026-07-17 (Tabularium) — wada ŚRODOWISKA, nie logiki ──
    {"kat": "kodowanie",
     "regex": r'subprocess\.run\((?:(?!encoding\s*=)[\s\S]){0,300}?\btext\s*=\s*True'
              r'(?:(?!encoding\s*=)[\s\S]){0,150}?\)',
     "opis": "🚨 subprocess.run(text=True) BEZ encoding='utf-8' — na polskim Windowsie dekoduje cp1250",
     "lekcja": "`text=True` każe Pythonowi dekodować wyjście procesu kodowaniem KONSOLI (cp1250 na polskim "
               "Windowsie), nie UTF-8. Nasze commity zaczynają się od emoji, komentarze mają polskie znaki, "
               "więc każdy odczyt `git log --format=%s` / wyjścia ruffa to ruletka: albo krzaki "
               "(`status.py`: „8f18d07 đź§ą PORZÄ„DEK…”), albo UnicodeDecodeError w wątku czytającym → "
               "`stdout=None` → bramka CICHNIE NA GŁUCHO i zawsze przechodzi. Dokładnie tak uciszona była "
               "bramka gnicia Tabularium w dniu powstania. Najpodlejszy przypadek: W13 (ruff) — pęka "
               "WTEDY, GDY ZNAJDZIE buga, bo dopiero wtedy cytuje polską linię źródła. "
               "ZAWSZE: encoding='utf-8', errors='replace'. Zmierzone: 6 trafień / 377 plików .py, "
               "zero trafień w kodzie naprawionym (wzorzec sprawdzony w obie strony).",
     "zrodlo": "self-review Tabularium — 2 wady aktywne + 4 utajone, w tym W6b i W13 (2026-07-17)"},
    # ── sesja 2026-07-17 (dług gnicia) — regex, który zjadł historię ──
    {"kat": "parsowanie",
     "regex": r"re\.compile\((?:(?!\)\s*$)[\s\S]){0,300}?\.\*\?[\s\S]{0,300}?re\.DOTALL",
     "opis": "🚨 Regex DOTALL z leniwym `.*?` między znacznikami — osierocone otwarcie zjada cudzą treść",
     "lekcja": "Realny incydent (2026-07-17): `<!--\\s*LICZBA:(\\w+)\\s*-->(.*?)<!--\\s*/LICZBA\\s*-->` "
               "z re.DOTALL. Jeden ZACYTOWANY znacznik bez własnego domknięcia skleił się z domknięciem "
               "NASTĘPNEGO bloku, a `sub()` zastąpił całość jedną liczbą — 44 linie historii LOG_ZMIAN "
               "ZJEDZONE (Prawo I złamane przez narzędzie od prawdy). Leniwy `.*?` NIE zatrzymuje się na "
               "granicy bloku, tylko na najbliższym pasującym OGONIE — a ten może należeć do cudzego wpisu "
               "kilkadziesiąt linii niżej. ZAWSZE zabroń treści bloku zawierać otwarcie: "
               "`((?:(?!<!--)[\\s\\S])*?)` — wtedy osierocony znacznik nie dopasuje się, zamiast kasować. "
               "Klasa jest podstępna, bo przy jednym poprawnym bloku testy przechodzą — pęka dopiero, gdy "
               "ktoś zacytuje składnię w tekście, czyli w dokumentacji O NARZĘDZIU. "
               "Zmierzone na 379 plikach .py: baza miała DWA wystąpienia tej bomby (wstrzykiwacz liczb "
               "`(.*?)` w nawiasie + generator katalogu z gołym `.*?`) — oba naprawione, więc wzorzec "
               "daje dziś 0 trafień i 0 fałszywek. Sprawdzony w obie strony na obu wariantach: łapie "
               "`.*?` i w nawiasie, i gołe; przepuszcza `.*?` bez DOTALL, DOTALL bez `.*?` oraz formę "
               "z jawną granicą bloku.",
     "zrodlo": "self-review Tabularium — wstrzykiwacz zjadł historię LOG_ZMIAN (2026-07-17)"},
    # ── sesja 2026-07-17 (dług gnicia) — bezpiecznik, który nie może się zapalić ──
    {"kat": "bezpiecznik",
     "regex": r"\b(?!exist_ok|parents)\w*(?:hash|integr|weryf|verified|valid|sprawdz|checksum)\w*"
              r"\s*=\s*True\b",
     "opis": "🚨 Bramka integralności/weryfikacji karmiona literałem True — zawsze przepuszcza",
     "lekcja": "Realny przypadek (2026-07-17): `dyrygent.py` wołał doradcę Hermesa z `hash_ok=True` NA "
               "SZTYWNO. Hermes ma gałąź `if not dane.hash_ok → BRUDNE`, więc kod WYGLĄDA na chroniony, "
               "a bramka nie może zapalić się NIGDY — martwy głos (Prawo XV) udający bezpiecznik. Klasa "
               "jest podstępna, bo test „czy Hermes odrzuca zły hash” PRZECHODZI (testuje Hermesa, nie "
               "wywołanie), a łańcuch jest przerwany gdzie indziej: Brama liczy `sha256` per wskaźnik, "
               "ale `ImperiumLog.hash_sha256` nie jest wypełniany przez NIC (0 przypisań) — nie było czego "
               "porównywać, więc literał `True` zabetonował lukę. Bezpiecznik, który dostaje swój werdykt "
               "jako stałą, nie jest bezpiecznikiem: policz warunek u źródła albo przyznaj się flagą "
               "`None/nieznany` i traktuj brak dowodu jako brak zgody. "
               "Zmierzone: 1 trafienie / 377 plików .py w zakresie skanu (imperium/, narzedzia/) — "
               "dokładnie ten bug, zero fałszywek; idiom `mkdir(exist_ok=True)` wykluczony z wzorca.",
     "zrodlo": "weryfikacja PAMIEC_ABSOLUTNA wobec kodu — dług gnicia (2026-07-17)"},
]

# ── CHECKLISTA REVIEW (bez regexu) — klasy SEMANTYCZNE, których forma składniowa jest
# identyczna z poprawnym kodem (flip znaku, nan, suma%, niezgodne długości). Regex dałby
# tu SZUM na naszym własnym poprawnym kodzie (zmierzone: „SHORT if ==LONG" = 11 trafień
# legalnego idiomu), więc NIE auto-skanujemy — pokazujemy jako checklistę przed pushem
# (obok /code-review). „Wszystko ma być łapane" (Prawo XV) dwiema warstwami: regex łapie
# formę, checklista łapie znaczenie.
CHECKLIST_STARTOWA = [
    {"kat": "parsowanie",
     "opis": "Blok o ZMIENNEJ długości parsowany po STAŁYM oknie znaków/linii zamiast po granicach",
     "lekcja": "Realny przypadek (2026-07-17): bramka W6b szukała `stan_na` w oknie `tresc[:600]` "
               "nagłówka dokumentu. Dokumenty z wieloma właścicielami mają je na pozycji 609 i 778 — "
               "więc CICHO omijały bramkę: im dłuższy (bogatszy) nagłówek, tym pewniej dokument "
               "wymykał się kontroli. Klasa jest podstępna, bo testy na typowym pliku przechodzą, "
               "a wymykają się właśnie przypadki NAJBOGATSZE, czyli najważniejsze. ZAWSZE parsuj po "
               "granicach bloku (separator `---`, domknięcie nawiasu) i UŻYJ ISTNIEJĄCEGO parsera "
               "formatu zamiast pisać drugi (Prawo XVI: jeden format = jeden parser; dwa parsery "
               "rozjadą się co do znaku).",
     "zrodlo": "self-review Tabularium — W6b omijana przez dokumenty z długim nagłówkiem (2026-07-17)"},
    {"kat": "dane",
     "opis": "Narzędzie „odświeżające prawdę” przepisuje też dokumenty HISTORYCZNE (datowane wpisy)",
     "lekcja": "Realny przypadek (2026-07-17): `wstrzyknij_liczby` iterował WSZYSTKIE dokumenty, w tym "
               "`typ: acta` (LOG_ZMIAN). Wpis z 2026-07-17 cytuje „87 neuronów” jako prawdę swojego dnia — "
               "gdy rój urośnie do 90, narzędzie CICHO przepisze historię na 90 i wpis zacznie kłamać o "
               "przeszłości. Utajone: dziś liczba się zgadza, więc podmiana jest no-op i nikt nie widzi "
               "bomby. Zawsze pytaj, czy dokument OPISUJE stan (ma nadążać) czy REJESTRUJE zdarzenie "
               "(ma zamarznąć) — automat odświeżający musi omijać drugą klasę (Prawo I).",
     "zrodlo": "self-review Tabularium — W15 vs LOG_ZMIAN typ:acta (2026-07-17)"},
    {"kat": "proces",
     "opis": "Bramka i akcja w jednym skrypcie — akcja wykonuje się NIEZALEŻNIE od wyniku bramki",
     "lekcja": "Realna wpadka Vitruviusza (2026-07-17): `python tests/run_tests.py; git commit …` "
               "w jednym bloku. Testy wypisały „1 oblane”, commit poszedł mimo to — bo kolejne "
               "polecenia nie sprawdzają wyniku poprzedniego. Bramka ISTNIAŁA i nie bramkowała: "
               "ta sama klasa co `hash_ok=True` (bezpiecznik, który nie może się zapalić), tylko "
               "na poziomie procesu, nie kodu. Podstępne, bo wynik testów JEST na ekranie — a i tak "
               "umyka, gdy commit przewija go w tym samym wyjściu. ZAWSZE: uruchom bramkę, ODCZYTAJ "
               "wynik jako osobny krok, dopiero potem commituj; albo połącz warunkiem "
               "(`&&` / `if $?`), żeby czerwone testy fizycznie zatrzymały commit.",
     "zrodlo": "self-review wachty porządkowej — commit 1f8d0ce poszedł z czerwonym testem (2026-07-17)"},
    {"kat": "kierunek",
     "opis": "Odwrócenie kierunku (flip znakiem) bez propagacji do WSZYSTKICH konsumentów",
     "lekcja": "Gdy odwracasz kierunek (np. ujemny IC → LONG↔SHORT), KAŻDY konsument w dół (dobór "
               "strategii, weto konfluencji, licznik zgodnych, synapsy) musi czytać kierunek EFEKTYWNY, "
               "nie surowy — inaczej wejdzie na przeciwną stronę niż skorygowany agregat. Surowe znaki "
               "zostaw wyłącznie do audytu/treningu.",
     "zrodlo": "cubic PR#122 legatus P1 (2026-07-13)"},
    {"kat": "granice",
     "opis": "Wartość nan/nieskończona przed zapisem cząstki, porównaniem lub agregatem",
     "lekcja": "Funkcja zwracająca nan (brak decyzji, pusty mianownik) — zanim wynik trafi do checkpointu "
               "areny lub porównania (nan>x=False cicho przekłamuje werdykt), sprawdź math.isfinite i "
               "pomiń/oznacz jako niekonkluzywne; kolejne jednostki mają liczyć się dalej.",
     "zrodlo": "cubic PR#122 ab_wazenie_ic P2 (2026-07-13)"},
    {"kat": "kontrakt",
     "opis": "Suma procentowych zwrotów per-jednostka prezentowana jako wynik portfela",
     "lekcja": "Suma % rośnie liniowo z liczbą par/jednostek — to nie P&L portfela. Uśrednij (sum/N) lub "
               "zważ przed prezentacją; werdykt oparty na sumie zawyża się z rozmiarem próby.",
     "zrodlo": "cubic PR#122 ab_strategy_mwu P2 (2026-07-13)"},
    {"kat": "werdykt",
     "opis": "Werdykt/większość liczona z jednostek bez realnego samplu",
     "lekcja": "Jednostki bez transakcji/decyzji (ret 0, brak głosów) nie mogą przechylać większości ani "
               "portfela — licz werdykt z par spełniających próg (np. ≥ MIN_TRADES) lub oznacz bieg niekonkluzywnym.",
     "zrodlo": "cubic PR#122 ab_tryb_strategii P2 (2026-07-13)"},
    {"kat": "kontrakt",
     "opis": "Niezgodne długości sparowanych serii (sygnał ↔ etykieta forward)",
     "lekcja": "Serie, które MUSZĄ być równoległe (sygnał i etykieta forward, cena i wynik), sprawdzaj na "
               "równość długości i odrzucaj rozjazd zanim policzysz — zip cicho ucina ogon i liczy z "
               "niezamierzonego podzbioru (look-ahead / skażone wagi).",
     "zrodlo": "cubic PR#122 legatus/hipoteza_b P2/P3 (2026-07-13)"},

    # ══ sesja 2026-07-16 (TIRO + biblioteka) — 7 realnych bugów jednego dnia ══════════════
    # Wszystkie znalezione SAMI (self-review + Test-Granic + czytanie danych), nie przez cubic.
    {"kat": "obietnica",
     "opis": "🚨 Docstring OBIECUJE odporność, której kod NIE DOWOZI (obietnica bez pokrycia)",
     "lekcja": "Gdy docstring mówi „graceful”, „nie wysypuje pipeline”, „abstynuje przy braku danych” — "
               "SPRAWDŹ, czy kod to realizuje. Realny przypadek: `buduj_cache` deklarował „GRACEFUL "
               "(Prawo XV) — nie wysypuje pipeline”, a leciał wyjątkiem z jednej książki i zabijał bieg "
               "po 70 poprawnych. To gorsze niż brak obietnicy: czytający UFA docstringowi i nie sprawdza. "
               "Każda deklaracja odporności = test, który ją udowadnia.",
     "zrodlo": "self-review konwerter (2026-07-16)"},
    {"kat": "odpornosc",
     "opis": "Pętla po jednostkach (pliki/książki/okna/pary) BEZ try/except per jednostka",
     "lekcja": "Jedna zła jednostka zabija cały bieg i wyrzuca do kosza całą pracę wykonaną wcześniej. "
               "Każda pętla po zewnętrznych danych (pliki użytkownika, API, konwersje) MUSI mieć "
               "try/except wewnątrz + GŁOŚNY raport co nie weszło. Cisza jest gorsza od błędu, ale "
               "przerwanie biegu jest gorsze od obu. (Wzorzec: ZASADA ANALIZY CZĄSTKOWEJ — bieg który "
               "padnie nie traci nic.)",
     "zrodlo": "self-review konwerter/buduj_cache (2026-07-16)"},
    {"kat": "wydajnosc",
     "opis": "Dedup/cache czytający CAŁY zbiór przy KAŻDYM zapisie — koszt kwadratowy w ścieżce gorącej",
     "lekcja": "Sprawdzenie „czy już mam” przez pełny odczyt pliku/tabeli przy każdym dopisie daje O(n²) "
               "i ROSNĄCE opóźnienie im więcej zebrano — najgorzej gdy siedzi w ścieżce płatnego API. "
               "Trzymaj zbiór w cache i wykrywaj zmianę spoza procesu tanio (stat: mtime+rozmiar). "
               "GRANICA: po własnym zapisie NIE inkrementuj licznika, jeśli właśnie przeładowałeś plik "
               "z dysku — on już ten wpis policzył (podwójne liczenie, niewidoczne na zbiorach/setach!).",
     "zrodlo": "self-review NOTARIUS (2026-07-16) — bug i jego poprawka miały TEN SAM dzień"},
    {"kat": "dane",
     "opis": "🚨 Eksport danych treningowych/wynikowych BEZ filtra jakości (ucięte, sprzeczne, zepsute)",
     "lekcja": "Dane, na których model się UCZY, wymagają twardszego filtra niż dane do podglądu. Trzy "
               "realne trucizny: (1) odpowiedź ucięta na limicie — uczy urywania w pół słowa; (2) ten sam "
               "prompt z RÓŻNYMI odpowiedziami (temperatura >0) — uczy SPRZECZNYCH etykiet dla "
               "identycznego wejścia, najgorszy możliwy sygnał; (3) zepsuty format od nauczyciela (np. "
               "niepoprawny JSON) — uczy produkować śmieci. Filtruj przy EKSPORCIE, nie przy zapisie "
               "(surowe dane zostawiaj — pozwolą policzyć konsensus).",
     "zrodlo": "self-review NOTARIUS + zmierzone dane (2026-07-16)"},
    {"kat": "dowod",
     "opis": "🚨 Nazwa (pliku/klucza/etykiety) traktowana jako DOWÓD zamiast treści",
     "lekcja": "Nazwa jest deklaracją, nie dowodem. Realny przypadek: plik "
               "`BIB-073_Boyd-Vandenberghe_Convex-Optimization.pdf` zawierał ZBIÓR ZADAŃ, nie podręcznik "
               "(na stronie autora oba PDF-y leżą obok siebie). Bez zajrzenia do treści RAG serwowałby "
               "zadania domowe jako teorię — sygnał cichy i FAŁSZYWY, nie do wykrycia po fakcie. "
               "Przy przyjmowaniu danych z zewnątrz: czytaj pierwsze zdania i sprawdzaj frazy-świadki.",
     "zrodlo": "BIB-073 Boyd (2026-07-16)"},
    {"kat": "testy",
     "opis": "🚨 Testy dotykające SIECI lub PŁATNEGO API (nieszczelne, kosztowne, niedeterministyczne)",
     "lekcja": "Zmierzone: `test_petla_live.py` = 8 płatnych wywołań DeepSeek i 4 min 42 s, bo "
               "`handluj_live` buduje `AdapterNewsLLM(fetcher=FetcherNewsRSS())`, a `uzyj_llm` jest "
               "domyślnie True + `glos=None` → lazy-init z klucza. Trzy szkody naraz: wynik zależy od "
               "tego, co akurat piszą w newsach (niedeterminizm), każdy przebieg kosztuje, bramka jest "
               "wolna. Domyślne argumenty adapterów sięgające sieci to pułapka — w testach wstrzykuj "
               "atrapę fetchera i `uzyj_llm=False`. "
               "🔁 NAWRÓT 2026-07-17: NOTARIUS złapał KOLEJNE 5 płatnych wywołań podczas zwykłego biegu "
               "`run_tests.py` — bo wada została ZAPISANA, ale NIE NAPRAWIONA. Księga, która tylko notuje, "
               "jest pamiętnikiem, nie systemem samo-leczenia. "
               "✅ NAPRAWA U ŹRÓDŁA (2026-07-17): `tests/conftest.py` ODBIERA testom klucze "
               "(DEEPSEEK_API_KEY, MEXC_API_KEY, MEXC_SECRET) przy imporcie — zamiast łatać każde "
               "wywołanie z osobna, zabijamy całą klasę: lazy-init nie znajduje klucza → deterministyczny "
               "fallback, zero kosztu. Dowód: par NOTARIUSA przed biegiem 162, po biegu 162. "
               "Test `test_zapora_testow.py` pilnuje, że zapora żyje (i że faktycznie odbiera).",
     "zrodlo": "wykryte przez NOTARIUSA (2026-07-16), NAWRÓT i naprawa u źródła (2026-07-17)"},
    {"kat": "sciezki",
     "opis": "Ścieżka pliku budowana bez limitu długości (Windows MAX_PATH = 260)",
     "lekcja": "Nazwa pliku legalna (Windows: do 255 zn./człon) NIE znaczy, że legalna jest ścieżka "
               "pochodna (katalog + nazwa + hasz + sufiks). Realnie: książka o nazwie 190 zn. dała ścieżkę "
               "cache 282 zn. → FileNotFoundError. Licz budżet pod NAJDŁUŻSZY wariant (np. .tmp przy "
               "zapisie atomowym) i skracaj WARUNKOWO — bezwarunkowe skracanie unieważnia istniejący "
               "cache i wymusza pełną rekonwersję. O zgodności decyduje HASZ, nie nazwa.",
     "zrodlo": "self-review konwerter (2026-07-16)"},
    {"kat": "odpornosc",
     "opis": "Biblioteka zewnętrzna bez fallbacku — jej kruchość staje się NASZĄ cichą stratą",
     "lekcja": "Realny przypadek: `ebooklib` 0.20.0 robi `xpath(\"//nav[@*='toc']\")[0]` bez zabezpieczenia "
               "→ IndexError na POPRAWNYM epubie, którego nawigacja nie ma elementu `toc` (standard tego "
               "nie wymaga). Efekt: 0 znaków, książka cicho nie weszła do RAG. Parsery cudzych formatów "
               "owijaj w try/except + fallback (u nas: calibre) i traktuj PUSTY WYNIK bez wyjątku tak samo "
               "jak wyjątek — cicha pustka jest gorsza od głośnego błędu.",
     "zrodlo": "BIB-075 whitepaper Bitcoina (2026-07-16)"},
    {"kat": "wspolbieznosc",
     "opis": "Zasób WSPÓŁDZIELONY chroniony blokadą WYŁĄCZNĄ — drugi uczestnik zostaje bez ochrony, "
             "a pierwszy wychodzący otwiera zasób pod trwającym biegiem",
     "lekcja": "Realny przypadek (2026-08-03, dzień po wdrożeniu SILENTIUM): dwie sesje ruszyły o 10:03, "
               "audyt drugiej dostał `RuntimeError: już trwa` i wypisał „bieg idzie BEZ ochrony\" — "
               "NIEPRAWDĘ, bo repo było chronione cudzą ciszą; zaraz potem sesja kończąca pierwsza "
               "ZDJĘŁA ciszę spod wciąż trwającego biegu drugiej. Pytaj, czego blokada naprawdę broni: "
               "wyłączność broniła PLIKU BLOKADY, a chronić miała REPOZYTORIUM. Gdy chroniony jest STAN "
               "WSPÓLNY (repo, katalog, urządzenie), a nie sekcja krytyczna, właściwym wzorcem jest "
               "licznik uczestników — zasób zwalnia OSTATNI wychodzący, nie pierwszy. Osobno: komunikat "
               "musi rozróżniać „nie ma ochrony\" od „ochronę trzyma ktoś inny\" — fałszywy alarm o braku "
               "ochrony uczy ignorować alarmy, więc szkodzi bardziej niż jego brak.",
     "zrodlo": "SILENTIUM — wada znaleziona realnym użyciem nazajutrz po wdrożeniu (2026-08-03)"},
]


class KsiegaWadKodu:
    """Pamięć wzorców błędów kodu + heurystyczny skaner."""

    def __init__(self, sciezka: Path | str = DOMYSLNA):
        self.sciezka = Path(sciezka)
        self.wpisy: list[dict] = []
        self._wczytaj()

    def _wczytaj(self) -> None:
        if not self.sciezka.exists():
            return
        for linia in self.sciezka.read_text(encoding="utf-8").splitlines():
            linia = linia.strip()
            if linia:
                try:
                    self.wpisy.append(json.loads(linia))
                except json.JSONDecodeError:
                    continue

    def zapisz(self) -> None:
        self.sciezka.parent.mkdir(parents=True, exist_ok=True)
        with self.sciezka.open("w", encoding="utf-8") as f:
            for w in self.wpisy:
                f.write(json.dumps(w, ensure_ascii=False) + "\n")

    def dodaj(self, kat: str, regex: str, opis: str, lekcja: str, zrodlo: str = "") -> bool:
        """Dodaje wzorzec. Odrzuca duplikat regex i błędny regex. Zwraca czy dodano.

        Gdy ten sam OPIS istnieje już jako pozycja checklisty (bez regexu) — AWANSUJE ją
        do wzorca zamiast dublować: klasa semantyczna zyskuje auto-skan w dniu, w którym
        zmierzymy jej szum. Bez tego księga trzymałaby dwa wpisy o tej samej wadzie.
        """
        if not regex or not opis:
            raise ValueError("regex i opis są wymagane")
        try:
            re.compile(regex)
        except re.error as e:
            raise ValueError(f"niepoprawny regex: {e}") from e
        if any(w["regex"] == regex for w in self.wpisy):
            return False   # już znany wzorzec — nie dubluj (Prawo XVI)
        nowy = {"kat": kat, "regex": regex, "opis": opis, "lekcja": lekcja, "zrodlo": zrodlo}
        for i, w in enumerate(self.wpisy):
            if not w.get("regex") and w["opis"] == opis:
                self.wpisy[i] = nowy      # awans checklisty → wzorzec
                return True
        self.wpisy.append(nowy)
        return True

    def dodaj_checklist(self, kat: str, opis: str, lekcja: str, zrodlo: str = "") -> bool:
        """Dodaje pozycję CHECKLISTY review (bez regexu — klasa semantyczna, nie auto-skan).
        Dedup po opisie (brak regexu jako klucza). Zwraca czy dodano."""
        if not opis or not lekcja:
            raise ValueError("opis i lekcja są wymagane")
        if any(not w.get("regex") and w["opis"] == opis for w in self.wpisy):
            return False
        self.wpisy.append({"kat": kat, "regex": "", "opis": opis,
                           "lekcja": lekcja, "zrodlo": zrodlo})
        return True

    def skanuj(self, tekst: str) -> list[dict]:
        """Zwraca trafienia: {wpis, linia} — które znane wzorce REGEX pasują do kodu (nudge).
        Pozycje checklisty (pusty regex) są pomijane — nie auto-skanują (byłby szum)."""
        trafienia = []
        for w in self.wpisy:
            if not w.get("regex"):        # checklista review — nie auto-skanujemy
                continue
            try:
                wzor = re.compile(w["regex"], re.MULTILINE)
            except re.error:
                continue
            m = wzor.search(tekst)
            if m:
                linia = tekst.count("\n", 0, m.start()) + 1
                trafienia.append({"kat": w["kat"], "opis": w["opis"],
                                  "lekcja": w["lekcja"], "linia": linia})
        return trafienia

    def wszystkie(self) -> list[dict]:
        return list(self.wpisy)

    def wzorce(self) -> list[dict]:
        """Pozycje z regexem (auto-skanowalne)."""
        return [w for w in self.wpisy if w.get("regex")]

    def checklista(self) -> list[dict]:
        """Pozycje bez regexu — klasy semantyczne do ręcznego przeglądu przed pushem."""
        return [w for w in self.wpisy if not w.get("regex")]


def zasiej_startowe(sciezka: Path | str = DOMYSLNA) -> int:
    """Dosiewa brakujące wzorce REGEX i pozycje CHECKLISTY (idempotentnie). Zwraca liczbę dodanych."""
    k = KsiegaWadKodu(sciezka)
    dodane = 0
    for w in WZORCE_STARTOWE:
        if k.dodaj(w["kat"], w["regex"], w["opis"], w["lekcja"], w["zrodlo"]):
            dodane += 1
    for c in CHECKLIST_STARTOWA:
        # Bramka struktury: pozycja checklisty z regexem to wzorzec wrzucony do złej listy —
        # `dodaj_checklist` nie czyta pola `regex`, więc CICHO stałby się ozdobą (zmierzone
        # 2026-07-17: wzorzec `subprocess text=True` przeleżał tak od dnia dodania, nie
        # skanując niczego). Głośny błąd zamiast cichej pustki — miejsce wpisu decyduje
        # o tym, czy wada jest łapana automatycznie, więc pomyłka nie może być milcząca.
        if c.get("regex"):
            raise ValueError(
                f"CHECKLIST_STARTOWA[{c['kat']}] ma regex — przenieś wpis do WZORCE_STARTOWE "
                f"(checklista nie auto-skanuje): {c['opis'][:60]}"
            )
        if k.dodaj_checklist(c["kat"], c["opis"], c["lekcja"], c["zrodlo"]):
            dodane += 1
    if dodane:
        k.zapisz()
    return dodane
