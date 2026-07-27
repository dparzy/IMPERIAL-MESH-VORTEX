---
name: wiedza
description: ZASADY WIEDZY I NAZEWNICTWA — zwiadowca wiedzy (dwa modele, kandydat≠prawda), MCP jako soczewka, ZASADA PEŁNEGO OPISU, archiwizacja i nomenklatura rzymska. Użyj przy pracy z DeepSeekiem/RAG, przy nazywaniu nowego organu i przed archiwizacją pliku.
---

> 🏛️ **Rozkazy stałe Imperium przeniesione z CLAUDE.md** (odchudzanie konstytucji,
> 2026-07-27). Treść jest ŹRÓDŁEM PRAWDY — nie streszczeniem. W konstytucji została
> linia-wyzwalacz z esencją, żeby zachowanie nie cofnęło się, gdy skill nie jest
> wczytany. Zmieniasz rozkaz TUTAJ, nie w kopii.

## 🔭 ZASADA ZWIADOWCY WIEDZY — DWA MODELE, KANDYDAT ≠ PRAWDA (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-07)

**Zwiad wiedzy (książki, RAG, deep research) prowadzą DWA modele o różnych rolach — tani
zwiadowca proponuje, drogi sędzia rozstrzyga. Nic z ust DeepSeeka nie jest prawdą, dopóki
arena/Sybilla tego nie zmierzy.** (Lekcja: jeden model czytający hurtem gubi hipotezy;
wynik LLM bez pomiaru to wiara, nie fakt — Prawo I.)

- **DeepSeek = tani Zwiadowca (proponent):** czyta cząstkowo (jeden fragment RAG → zapis →
  następny, z paskiem postępu — Prawo XXIV + ZASADA ANALIZY CZĄSTKOWEJ), wyciąga KANDYDATÓW
  na hipotezy/neurony/strategie. Ma API (`DEEPSEEK_API_KEY`), jest tani — więc robi surową
  robotę objętościową, której nie stać na Opusa.
- **Opus/Claude = drogi Sędzia (recenzent kompletności):** drugie przejście adversarialne —
  *„czego DeepSeek NIE wyłapał? który fragment pominął? która hipoteza zniknęła?"*. Krytyk
  kompletności to obowiązkowy DRUGI etap, nie opcja (wzorzec Completeness-Critic).
- **Kandydat ≠ prawda (Prawo I + ZPO):** każdy wynik DeepSeeka to ⚠️ HIPOTEZA/KANDYDAT, nigdy
  fakt. Rozstrzyga wyłącznie POMIAR — arena (IC/WFO/DSR), Sybilla (Brier), triada. DeepSeek
  proponuje „co sprawdzić", arena mówi „co jest prawdą". Wpięcie w ścieżkę decyzyjną dopiero
  po zielonej walidacji A/B (ZASADA WPIĘCIA, opt-in OFF).
- **Dwa modele, bo jeden gubi perły:** różnica ról (proponent vs recenzent) jest źródłem siły —
  redundancja mierzona, nie zgadywana (Prawo XVI): DeepSeek szeroko i tanio, Opus wąsko i głęboko.

**Złamanie:** traktowanie wyniku DeepSeeka jako prawdy bez pomiaru areny; hurtowe czytanie bez
cząstkowania i krytyka kompletności; pominięcie drugiego modela (zwiad jednym okiem = gubione hipotezy).

### 🐎 FRUMENTARIUS — ZWIAD ZEWNĘTRZNY NA UTKNIĘCIE (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-27)

*Frumentarii* byli agentami cesarskimi wysyłanymi POZA Imperium: jechali szybko, tanio, po jedną
rzecz i wracali z meldunkiem — nie z decyzją. Trzeci zwiadowca obok Hyginusa (korpus wewnętrzny)
i Sędziego (osąd) to **szybki, tani subagent wysyłany na ZEWNĄTRZ**, gdy rozstrzygnięcie utknęło.

**WYZWALACZ (kiedy wysyłasz):** utknąłeś na rozstrzygnięciu — nie wiesz, którą drogą pójść, albo
podejrzewasz, że problem jest już rozwiązany u innych (konkurencja, biblioteki, dedykowane skrypty,
publikacje). Zamiast wymyślać od zera albo zgadywać — **wyślij po prior art**.

**WARUNEK OPŁACALNOŚCI (bez niego nie wysyłasz):** subagent startuje ZIMNO (~50–66 tys. tokenów),
więc opłaca się **wyłącznie**, gdy CZYTA DUŻO, a ZWRACA MAŁO — czyli gdy odpowiedzi **nie ma w
naszym repo**. Pytanie wewnętrzne („czy mamy już moduł X") rozstrzygasz `grep`em szybciej i taniej
niż trwa jego zimny start. Wysyłka na drobiazg to złamanie ZASADY OSZCZĘDNOŚCI TOKENÓW (`/gradus`).

**METAPROMPT MUSI ZAWIERAĆ (inaczej wraca ogólnik, czyli zero):**
1. **Jedno pytanie rozstrzygające** — nie temat, tylko pytanie, na które da się odpowiedzieć.
2. **Co JUŻ MAMY** — żeby nie wrócił z tym, co stoi w kodzie (ta sama choroba, którą U4 miał
   leczyć u Hyginusa).
3. **Nasze twarde ograniczenia** — sprzęt (klasa PEDES: 4 wątki, 16 GB, brak CUDA), domena
   (MEXC/krypto), zależności (stdlib-first), dane (bary 1m+, brak L2/tick).
4. **Format meldunku:** teza → ŹRÓDŁO (link/nazwa) → **jak to zmierzyć u nas** → koszt.
5. **Jawny nakaz przyznania się do niewiedzy:** „czego NIE udało się potwierdzić" jest częścią
   meldunku, nie wstydem.

**BARIERKA — MELDUNEK FRUMENTARIUSA TO KANDYDAT, NIGDY PRAWDA.** Zewnętrzność nie daje
nieomylności; daje niezależność. Zmierzone dowody Imperium, wszystkie własne:
- recenzent zewnętrzny (cubic PR #133) miał rację w 20/22 punktach, ale **jedyne P1 cytowało dwie
  NIEISTNIEJĄCE reguły** — cytat z reguły sprawdzaj `grep`em, zanim uznasz zarzut;
- 4/4 werdykty zwiadowców w kampanii porządkowej okazały się błędne po weryfikacji;
- Hyginus przy **39.3%** kandydatów pisał „nie dubluje", gdy pojęcie stało w kodzie (pomiar
  2026-07-27) — deklaracja modelu o nowości jest bezwartościowa bez sprawdzenia.

**CZEGO FRUMENTARIUS NIE ROBI:** nie rozstrzyga decyzji kierunkowych (Prawo XVIII — to Cezar),
nie wpina niczego w ścieżkę decyzyjną (ZASADA WPIĘCIA), nie zastępuje pomiaru areny. Przywozi
materiał; wyrok zapada w domu.

**Złamanie:** wysłanie po coś, co jest w naszym repo (spalony zimny start); przyjęcie meldunku
bez weryfikacji jako faktu; metaprompt bez pytania rozstrzygającego i bez „co już mamy".

---

## 🔌 ZASADA MCP — SOCZEWKA, NIE MÓZG (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-04)

**Rój UCZY SIĘ w KODZIE** (MWU, synapsy reżimowe, igrzyska, ksiega_wad, drift_adapter).
**MCP to SOCZEWKA i RURA** — pozwala Claude oglądać/karmić arenę, ale **nie jest uczącym się
modułem.** Nie mylić: dodanie MCP nie zastępuje logiki uczenia.

- **Nie dodawaj MCP redundantnego** z tym, co już mamy (Prawo XVI). Przykład: odrzucono
  oficjalny „Memory" MCP — mamy własne 13 warstw pamięci. MCP wchodzi TYLKO gdy dokłada
  NOWĄ informację/zdolność (np. Filesystem = pełny dysk, SQL nad wynikami areny).
- **Nasze serwery MCP:** `narzedzia/rag/mcp_server.py` (biblioteka RAG) +
  `narzedzia/arena_mcp.py` (migawka roju + baza wyników `arena_wyniki.db`).
- **Config startowy (`.mcp.json`, hooki) = ZAWSZE decyzja Cezara** — nie wpinamy w auto.

**Złamanie:** dodanie MCP skorelowanego z istniejącym modułem, albo traktowanie MCP jak
learnera zamiast soczewki.

---

## 📐 ZASADA PEŁNEGO OPISU (ZPO) — ROZKAZ STAŁY (Cezar zatwierdził 2026-06-02)

Cezar jest nowicjuszem. Każdy moduł/neuron/strategia/inspiracja opisywany jest KOMPLETNIE:
pełna nazwa (rozwinięcie KAŻDEGO skrótu), link źródła, status weryfikacji (✅/⚠️/❌),
wyjaśnienie "dla nowicjusza", status kod-vs-plan, faza, powód. Szablon: `docs/WZORZEC_OPISU.md`.

- **Nigdy skrótu bez rozwinięcia** (SHARP → Self-Evolving Rubric Policy).
- **Nigdy projektu bez pełnego linku** (`https://arxiv.org/abs/...`, nie "arxiv 2605...").
- **Nigdy fałszywej weryfikacji** (Prawo I): nie sprawdziłem → piszę ⚠️ niezweryfikowany.
- Wszystkie zewnętrzne inspiracje AI/ML: `docs/REJESTR_INSPIRACJI.md` (jedno źródło prawdy).

**Złamanie ZPO:** skrót bez rozwinięcia, projekt bez linku, lub udawana weryfikacja.

---

## 📦 ZASADA ARCHIWIZACJI (ROZKAZ STAŁY — Cezar zatwierdził 2026-06-02)

**Przed przeniesieniem JAKIEGOKOLWIEK pliku do `archiwum/` — przeczytaj go w CAŁOŚCI.**
"Wygląda staro/nieaktualnie" to NIE jest powód. Wygląd ≠ zawartość.

- [ ] Przeczytany cały plik (nie nagłówek, nie pierwsze 50 linii)
- [ ] Potwierdzone, że treść jest faktycznie przestarzała / zastąpiona (z nazwą następcy)
- [ ] Sprawdzone, czy inne dokumenty/kod go nie cytują (grep nazwy pliku)
- [ ] `archiwum/` otwierasz tylko na wyraźne polecenie Cezara — to magazyn, nie warsztat

**Złamanie:** archiwizacja pliku bez przeczytania (nawet przez nieuwagę — Prawo XVIII:
złamanie przez nieuwagę = takie samo złamanie jak celowe).

---

## 🏛️ ZASADA NOMENKLATURY IMPERIALNEJ — WSZYSTKO PO RZYMSKU (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-13)

**Każdy organ, moduł, funkcja, rola, kategoria i agent Imperium nosi nazwę osadzoną w klimacie
Cesarstwa Rzymskiego — dobraną DO FUNKCJI.** To nie ozdoba, to tożsamość Imperium (rozkaz Cezara:
„wszystko, nie tylko imiona, ale i nazwy ze względu na funkcję i kategorię").

- **Rzymska nazwa OBOK technicznej, nie zamiast.** Kod pozostaje jednoznaczny (klucze, klasy, API
  bez zmian) — rzymskie imię żyje w nazwie organu/roli, docstringu, banerach, dokumentacji. Nigdy
  nie łamiemy spójności kluczy (Prawo XXI) dla estetyki.
- **Dobór DO FUNKCJI (nie losowo):** nazwa ma oddawać rolę. Wzorce już żywe:
  - **Osoby/agenci:** VITRUVIUSZ (Architekt = Claude/Opus), HYGINUS (Bibliotekarz-Zwiadowca = DeepSeek), CEZAR PIXEL (Imperator).
  - **Organy (katalogi `imperium/`):** cesarz (rdzeń decyzji), senat (meta-decyzje), legiony (neurony/moduły bojowe),
    pretorianie (bezpieczniki/straż), akwedukty (przepływ danych), drogi (routing/hub), świątynie (wiedza/mapy),
    oczy (percepcja/adaptery), biblioteki (pamięć/RAG), koloseum (walidacja/kontrfaktyki), fundament (narzędzia bazowe).
- **Przy KAŻDYM nowym module/organie/roli — nadaj rzymskie imię pasujące do funkcji** (jak Hyginus dla
  Bibliotekarza). Brak rzymskiej nazwy nowego organu = niedokończone wdrożenie.
- **Źródło prawdy imion:** `docs/PROFIL_CEZARA.md` § Imiona Imperium (agenci) + `docs/ARCHITEKTURA_IMPERIUM.md`
  (organy). Nowe imię → dopisz do właściwego źródła w tym samym commicie (ZASADA PEŁNEJ SYMBIOZY).

**Złamanie:** nowy organ/moduł/rola bez rzymskiej nazwy dopasowanej do funkcji, albo złamanie
spójności kluczy kodu (Prawo XXI) w imię nazewnictwa.
