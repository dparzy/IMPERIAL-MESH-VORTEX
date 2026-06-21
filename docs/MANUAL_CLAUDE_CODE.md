# 🤖 MANUAL CLAUDE CODE — Instalacja i konfiguracja z Imperium

> **Stan na:** 2026-06-20
> Dla Cezara-nowicjusza — każdy krok dokładnie.
> Zakładamy: masz już Python 3.11.9, git i TA-Lib na laptopie.

---

## SPIS TREŚCI

1. [Co to jest Claude Code i po co nam to](#1-co-to-jest)
2. [Instalacja Claude Code na laptopie (Windows)](#2-instalacja)
3. [Pierwsze uruchomienie Claude Code z Imperium](#3-pierwsze-uruchomienie)
4. [Jak Claude Code działa z Imperium — automatyki](#4-jak-dziala)
5. [MCP — dodatkowe narzędzia dla Claude](#5-mcp)
6. [Klucze API — bezpieczeństwo](#6-klucze)
7. [Codzienna praca: jak rozmawiać z Claude Code](#7-codzienna-praca)
8. [Problemy i rozwiązania](#8-problemy)

---

## 1. CO TO JEST CLAUDE CODE I PO CO NAM TO <a name="1-co-to-jest"></a>

**Claude Code** to asystent AI od Anthropic, który działa BEZPOŚREDNIO w Twoim terminalu
i ma dostęp do całego kodu Imperium. Zamiast kopiować kod do chatu — Claude Code
**widzi i edytuje pliki na Twoim laptopie w czasie rzeczywistym**.

### Co to zmienia dla Imperium?

Bez Claude Code:
- Kopiujesz kod do chatu na stronie
- Dostajesz odpowiedź — kopiujesz z powrotem
- Ryzyko błędu przy kopiowaniu
- Claude nie widzi całego projektu

Z Claude Code:
- Claude **czyta pliki bezpośrednio** z folderu Imperium
- **Edytuje kod od razu** — bez kopiowania
- **Uruchamia testy** i widzi wyniki
- **Commituje i pushuje** samodzielnie (za Twoją zgodą)
- Rozmowy są **ciągłe między sesjami** (pamięta kontekst)

### Czego potrzebujesz?

- Subskrypcja **Claude Pro** (masz ✅)
- Node.js (instalujemy w kroku 2)
- Terminal na laptopie
- Folder z Imperium (masz ✅)

---

## 2. INSTALACJA CLAUDE CODE NA LAPTOPIE (WINDOWS) <a name="2-instalacja"></a>

### Krok 2.1 — Zainstaluj Node.js

Claude Code działa jako aplikacja Node.js.

1. Wejdź na https://nodejs.org
2. Kliknij duży zielony przycisk **„LTS"** (Long Term Support — stabilna wersja)
3. Pobierz plik `.msi` i uruchom instalator
4. Klikaj „Next" przez cały kreator — domyślne ustawienia są dobre
5. Na końcu kliknij „Finish"

Sprawdź w terminalu (nowym oknie cmd):
```
node --version
```
Powinno pokazać `v20.x.x` lub wyżej ✅

```
npm --version
```
Powinno pokazać `10.x.x` lub wyżej ✅

### Krok 2.2 — Zainstaluj Claude Code

W terminalu (cmd lub PowerShell):
```
npm install -g @anthropic-ai/claude-code
```

Poczekaj aż skończy (30–60 sekund, dużo tekstu — normalne).

Sprawdź:
```
claude --version
```
Powinno pokazać numer wersji ✅

> ⚠️ Jeśli pojawi się błąd o uprawnieniach — uruchom terminal jako **Administrator**
> (kliknij prawym na „cmd" → „Uruchom jako administrator") i powtórz instalację.

### Krok 2.3 — Zaloguj się (połącz z subskrypcją Pro)

```
claude
```

Przy pierwszym uruchomieniu otworzy się przeglądarka z prośbą o logowanie.
Zaloguj się na **to samo konto Anthropic** co Twoja subskrypcja Pro.

Po zalogowaniu wróć do terminala — zobaczysz prompt Claude Code.

Wyjdź z Claude Code na razie:
```
/exit
```

---

## 3. PIERWSZE URUCHOMIENIE CLAUDE CODE Z IMPERIUM <a name="3-pierwsze-uruchomienie"></a>

### Krok 3.1 — Wejdź do folderu Imperium

W terminalu:
```
cd Desktop\imperial-mesh-vortex
```
(lub gdziekolwiek masz sklonowane Imperium — zmień ścieżkę)

### Krok 3.2 — Przełącz na właściwą gałąź

```
git checkout claude/sleepy-fermi-dsdE4
git pull origin claude/sleepy-fermi-dsdE4
```

To pobierze wszystkie najnowsze zmiany (webhook TradingView, moduły AFML, skrypty startowe).

### Krok 3.3 — Uruchom Claude Code w folderze Imperium

```
claude
```

Claude Code uruchomi się i **automatycznie przeczyta** pliki konfiguracyjne Imperium:
- `CLAUDE.md` — instrukcje stałe dla Claude (24 Prawa Imperium, tryb autonomiczny)
- `.claude/settings.json` — uprawnienia i hooki

Po chwili zobaczysz prompt i komunikat że sesja startuje. Hook `SessionStart`
automatycznie:
1. Instaluje zależności (`pip install -r requirements.txt`)
2. Uruchamia **KROK 0 — audyt spójności** (Prawo XXI)
3. Pokazuje stan roju: neurony, zwiadowcy, kategorie, ruff, dokumenty

### Krok 3.4 — Sprawdź że wszystko gra

W prompcie Claude Code wpisz:
```
sprawdź testy
```

Claude uruchomi `python tests/run_tests.py` i pokaże wyniki (1532 testów ✅).

---

## 4. JAK CLAUDE CODE DZIAŁA Z IMPERIUM — AUTOMATYKI <a name="4-jak-dziala"></a>

### 4.1. Hook SessionStart — automatyczny audyt na starcie

Za każdym razem gdy otworzysz Claude Code w folderze Imperium, automatycznie uruchomi się:

```
.claude/hooks/session-start.sh
```

Ten skrypt:
- Instaluje brakujące zależności pip
- Sprawdza ile neuronów, zwiadowców, elitarnych modułów
- Uruchamia ruff (linter)
- Sprawdza spójność dokumentów z kodem

**Nie musisz nic robić** — to dzieje się samo.

### 4.2. Uprawnienia automatyczne (bez klikania „Zezwól")

W `.claude/settings.json` masz preautoryzowane komendy które Claude może wykonywać
bez przerywania i pytania Cię:

```
git add, git commit, git push, git status, git diff, git log
python tests/run_tests.py
python narzedzia/audyt_spojnosci.py
```

Dla wszystkiego innego Claude zapyta Cię o zgodę zanim wykona.

### 4.3. Tryb autonomiczny (Prawo XVIII + TRYB AUTONOMICZNY)

Claude Code ma ustawiony **tryb autonomiczny** dla Imperium — oznacza to:

- **Naprawia rozbieżności dokumentów samodzielnie** (np. liczby się nie zgadzają)
- **Commituje i pushuje po zakończonym zadaniu** — sam, bez pytania
- **Pyta Cię tylko o decyzje kierunkowe** (kasowanie plików, zmiana strategii, koszt)

Jeśli nie chcesz żeby Claude coś zrobił — powiedz `stop` lub `poczekaj, zapytaj mnie`.

### 4.4. Gałąź robocza

Cały kod Imperium jest rozwijany na gałęzi:
```
claude/sleepy-fermi-dsdE4
```

Claude Code zawsze pushuje tam. Do `main` pushuje tylko Cezar ręcznie (przez PR).

---

## 5. MCP — DODATKOWE NARZĘDZIA DLA CLAUDE <a name="5-mcp"></a>

**MCP** (Model Context Protocol) to sposób na podłączenie zewnętrznych narzędzi
do Claude Code — np. GitHub, bazy danych, pliki Excel, przeglądarki.

### 5.1. MCP GitHub (już skonfigurowane)

W tej sesji online mamy MCP GitHub skonfigurowane po stronie serwera.
Na **lokalnym laptopie** możesz go dodać samodzielnie.

Stwórz lub edytuj plik `~/.claude/settings.json`
(czyli `C:\Users\TwojeImie\.claude\settings.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_TwójToken"
      }
    }
  }
}
```

Token GitHub utwórz na: https://github.com/settings/tokens
(zakres uprawnień: `repo`, `read:org`)

Po restarcie Claude Code będzie mógł czytać PR, komentarze, CI — bezpośrednio.

### 5.2. MCP Filesystem (dodatkowy dostęp do plików)

Jeśli chcesz żeby Claude miał dostęp do konkretnych folderów poza Imperium
(np. folder z danymi CSV, folder Downloads):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\TwojeImie\\Desktop\\imperial-mesh-vortex",
        "C:\\Users\\TwojeImie\\Downloads"
      ]
    }
  }
}
```

### 5.3. Jak sprawdzić czy MCP działa

W Claude Code wpisz:
```
/mcp
```
Zobaczysz listę aktywnych MCP serwerów i ich status.

---

## 6. KLUCZE API — BEZPIECZEŃSTWO <a name="6-klucze"></a>

**Prawo V Imperium: klucze NIGDY w kodzie, NIGDY w czacie. Tylko zmienne środowiskowe.**

### Klucze których potrzebujesz (kolejność ważności):

| Klucz | Do czego | Gdzie dostać |
|-------|---------|--------------|
| `MEXC_API_KEY` + `MEXC_SECRET` | Pobieranie danych live + paper trading | mexc.com → API Management |
| `DEEPSEEK_API_KEY` | Cesarz (LLM decyzja końcowa) | platform.deepseek.com |
| `WEBHOOK_TV_SEKRET` | Odbiornik sygnałów TradingView | wymyślasz sam |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | MCP GitHub | github.com/settings/tokens |

### Jak ustawić klucze na Windows (RAZ, trwale):

W cmd jako Administrator:
```
setx MEXC_API_KEY "twój-klucz-mexc"
setx MEXC_SECRET "twój-secret-mexc"
setx DEEPSEEK_API_KEY "twój-klucz-deepseek"
setx WEBHOOK_TV_SEKRET "twojeTajneHaslo123"
```

Potem **zamknij i otwórz nowy terminal** (setx działa od nowego okna).

### Sprawdzenie że klucze są ustawione:
```
echo %MEXC_API_KEY%
echo %DEEPSEEK_API_KEY%
```
Jeśli pojawi się wartość klucza (nie pusta linia) — ustawione ✅

### Klucze a Claude Code:

Claude Code **nigdy nie wysyła kluczy do Anthropic**. Klucze są używane lokalnie
przez Pythona. Claude Code widzi tylko kod, nie wartości kluczy w środowisku.

> ⚠️ Nigdy nie wklejaj klucza do czatu z Claude — powiedz mu tylko „mam MEXC_API_KEY ustawiony"
> a Claude wie co robić.

---

## 7. CODZIENNA PRACA: JAK ROZMAWIAĆ Z CLAUDE CODE <a name="7-codzienna-praca"></a>

### 7.1. Jak zacząć sesję

1. Otwórz terminal
2. `cd Desktop\imperial-mesh-vortex`
3. `git checkout claude/sleepy-fermi-dsdE4`
4. `claude`

Hook startowy odpali się automatycznie — poczekaj na wynik audytu.

### 7.2. Przykładowe komendy (mówisz po polsku — Claude rozumie)

```
dodaj nowego neurona RSI z dywergencją
```
```
uruchom testy i pokaż mi wyniki
```
```
sprawdź czy dokumenty są aktualne
```
```
uruchom paper trading i pokaż mi panel
```
```
co zmieniło się w ostatnim commicie?
```
```
pokaż mi top 5 neuronów według rankingu igrzysk
```
```
zrób backtest strategii TREND_RIDER na BTC ostatnie 30 dni
```

### 7.3. Skróty klawiszowe Claude Code

| Skrót | Co robi |
|-------|---------|
| `Ctrl+C` | Zatrzymaj bieżące działanie Claude |
| `Ctrl+R` | Powtórz ostatnią komendę |
| `/exit` | Wyjdź z Claude Code |
| `/clear` | Wyczyść historię rozmowy (nowa sesja) |
| `/help` | Pomoc — lista komend |
| `/status` | Stan połączenia i modelu |
| `/model` | Zmień model (opus-4-8, sonnet-4-6 itd.) |

### 7.4. Jak zatrzymać Claude gdy za dużo robi

Jeśli Claude zaczął robić coś czego nie chcesz — naciśnij `Ctrl+C`.
Możesz wtedy powiedzieć `cofnij to` albo `nie rób tego, zamiast tego...`.

### 7.5. Plan Mode — gdy chcesz zobaczyć co Claude zamierza ZANIM zacznie

Powiedz:
```
zaplanuj jak dodać nowego zwiadowcę — nie rób niczego, najpierw pokaż plan
```

Claude pokaże plan krok po kroku. Powiedz `tak, działaj` żeby zacząć,
albo `zmień X na Y` żeby skorygować plan.

---

## 8. PROBLEMY I ROZWIĄZANIA <a name="8-problemy"></a>

| Problem | Rozwiązanie |
|---------|-------------|
| `claude: command not found` | Zamknij i otwórz nowy terminal. Jeśli nadal błąd — `npm install -g @anthropic-ai/claude-code` ponownie jako Administrator |
| Prosi o logowanie przy każdej sesji | Sprawdź czy masz stabilne połączenie z internetem. `claude auth login` |
| Hook nie uruchamia się | Sprawdź `ls .claude/hooks/` — czy plik `session-start.sh` istnieje. Uruchom `git pull` |
| „Permission denied" przy edycji pliku | Claude prosi o zgodę — kliknij `Allow` albo `Allow always` dla danego pliku |
| Testy czerwone po pull | Claude automatycznie to zobaczy i naprawi. Możesz też powiedzieć `napraw błędy testów` |
| Claude zapomniał kontekst | To normalne — każda nowa sesja zaczyna się od zera, ale hook startowy i CLAUDE.md dają mu kontekst Imperium. Powiedz `przypomnij sobie cel projektu` |
| `node: command not found` | Node.js nie jest w PATH — zainstaluj ponownie z ptaszkiem „Add to PATH" |
| Słabe odpowiedzi, Claude nie wie o projekcie | Upewnij się że jesteś w folderze `imperial-mesh-vortex` gdy wpisujesz `claude`. CLAUDE.md musi być w tym folderze |

---

## SZYBKIE PRZYPOMNIENIE — START KAŻDEJ SESJI

```
# 1. Otwórz terminal (cmd)

# 2. Wejdź do Imperium
cd Desktop\imperial-mesh-vortex

# 3. Upewnij się na właściwej gałęzi
git checkout claude/sleepy-fermi-dsdE4
git pull origin claude/sleepy-fermi-dsdE4

# 4. Uruchom Claude Code
claude

# 5. Poczekaj na audyt startowy — potem mów co chcesz robić
```

---

*Manual Claude Code dla Imperium — aktualizowany z każdą sesją.*
*Pełna dokumentacja projektu: `docs/INDEKS_IMPERIUM.md`*
