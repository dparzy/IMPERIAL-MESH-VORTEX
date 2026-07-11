# 🧾 ŚCIĄGA LOKAL — wszystko krok po kroku (dla nowicjusza)

> Jedna kartka ze WSZYSTKIMI komendami do obsługi Imperium na laptopie.
> Kopiuj-wklej do PowerShella. Kolejność sekcji = kolejność, w jakiej ich zwykle używasz.
> **Stan na:** 2026-07-04

---

## 0. Trzy złote zasady (przeczytaj raz)

1. **Zawsze najpierw wejdź do folderu projektu:**
   ```powershell
   cd C:\Projekty\imperial-mesh-vortex
   ```
2. **Używaj jednej maszyny na raz** (albo laptop, albo chmura) — inaczej zmiany się rozjadą.
3. **`bash` w PowerShellu = zepsute WSL.** Do ręcznego odpalania skryptów `.sh` używaj Git Basha:
   ```powershell
   & "C:\Program Files\Git\bin\bash.exe" <ścieżka-skryptu.sh>
   ```
   (Claude Code robi to sam w tle — Ciebie to dotyczy tylko przy ręcznym teście hooka.)

---

## 1. Codzienny start (to robisz najczęściej)

Otwórz terminal i uruchom Claude w folderze projektu:
```powershell
cd C:\Projekty\imperial-mesh-vortex
claude
```
Na starcie zobaczysz komunikaty `[hook] ...`. Szukaj:
- `[hook] SYNC ✅` — laptop sam ściągnął najnowszy stan z GitHub.
- `AUDYT SPÓJNOŚCI ... ✅ pełna harmonia` — kod zgadza się z dokumentacją.
- `CENTRUM PAMIĘCI` — wstrzyknięta pamięć (asystent zna cały łuk projektu).

**To wszystko dzieje się automatycznie.** Jak widzisz te linie — jest dobrze.

---

## 2. Synchronizacja z GitHub (już automatyczna)

- **Start sesji** → auto-pull (Claude sam ściąga).
- **Koniec sesji** → auto-commit + push pamięci (Claude sam zapisuje).

**Ręcznie potrzebujesz tego rzadko.** Gdyby auto-pull się pominął (bo drzewo brudne):
```powershell
git status                                              # co jest zmienione
git stash push -m "chwilowo"                            # schowaj zmiany
git pull --rebase origin claude/sleepy-fermi-dsdE4      # ściągnij najnowsze
git stash pop                                           # przywróć zmiany
```

Sprawdzenie, czy jesteś zsynchronizowany:
```powershell
git status                 # "working tree clean" = czysto
git log --oneline -3       # ostatnie 3 commity
```

---

## 2c. 💰 Oszczędzanie tokenów — ŚWIEŻY START zamiast wznawiania (WAŻNE)

**Wznowienie długiej sesji przesyła CAŁĄ historię czatu za każdą turę** — po całym dniu
pracy to setki tysięcy tokenów przy KAŻDEJ wiadomości (lekcja: sesja urosła do 808k kontekstu).
Dodatkowo pożerają: powtarzane wklejki zmienionych plików, hook startowy, wstrzyknięcie pamięci.

**Lek = nasza własna pamięć.** Zamiast wznawiać gigantyczną sesję:
1. Zakończ: powiedz **„zamknij sesję wg zasad"** (albo `/clear`)
2. Zacznij **ŚWIEŻĄ** sesję (nowy terminal albo po `/clear`)
3. Dziennik Nieśmiertelny + Centrum Pamięci nadrobią cały łuk projektu w **~3k tokenów zamiast 808k**

**Zasada kciuka:** gdy pasek kontekstu przekracza ~50-60% ALBO zmieniamy temat → świeży start.
Wznawianie ma sens tylko dla krótkiej, bieżącej rozmowy. Po to zbudowaliśmy 13 warstw pamięci —
żeby wyrzucić drogi kontekst i tanio odtworzyć stan z gita.

---

## 2d. 📚 Wiedza z książek BEZ tokenów — praca lokalna, potem chirurgiczny RAG

Ciężką pracę z książkami (konwersja djvu/mobi, ekstrakcja, indeks) robimy LOKALNIE narzędziami
deterministycznymi — **0 tokenów Claude**. Dopiero potem Claude pyta RAG i płaci tylko za
zwrócone fragmenty (~setki tokenów), nie za czytanie całych książek (setki tysięcy).

**Jedna komenda (na laptopie, z calibre + djvulibre):**
```powershell
python -m narzedzia.przygotuj_biblioteke
```
Robi 3 kroki, wszystkie token-free: (1) konwersja+cache tekstu (`konwerter`), (2) indeks RAG
(`indeksuj`), (3) katalog metadanych (`metadane_ksiag`). Idempotentne — pomija już zrobione.

**Książki tylko lokalnie, RAG w chmurze z tekstu** (decyzja Cezara 2026-07-11): binaria
książek (epub/pdf/djvu/mobi/azw3) są **poza gitem** — żyją na tym laptopie. Do repo idzie sam
WYEKSTRAHOWANY TEKST (`bibliotheca_ulpia/dane/tekst_cache/`, wersjonowany), więc chmura buduje
pełny RAG bez binariów i bez calibre. Po zbudowaniu cache commituj go:
```powershell
python -m narzedzia.przygotuj_biblioteke     # konwersja+cache+indeks (calibre lokalnie)
git add bibliotheca_ulpia/dane/tekst_cache/  # cache = źródło RAG (nie jest już ignorowany)
git commit -m "cache tekstu książek — chmura czyta bez binariów"
```
Cache jest kluczowany haszem treści → ten sam plik = ten sam cache na obu maszynach (Prawo XVII).
Bez calibre/djvutxt kroki i tak działają dla epub/pdf (djvu abstynuje — Prawo XV).

---

## 3. Testy i audyt (przed każdą większą zmianą)

```powershell
python tests/run_tests.py            # wszystkie testy — muszą być zielone
python narzedzia/audyt_spojnosci.py  # spójność kod↔dokumenty — musi być exit 0
python narzedzia/status.py           # pulpit: rój, testy, git, ostatni LOG_ZMIAN
```

---

## 4. Uruchomienie systemu

### A) Przygotowanie lokala (raz po świeżym `git pull`)
```powershell
python skrypty/start_lokal.py        # audyt + pamięć + indeks RAG + mapa 13 warstw
```

### B) Paper trading (symulacja — ZERO prawdziwych pieniędzy, tu zaczynasz)
```powershell
python skrypty/start.py              # uruchamia rój + panel
```
Potem otwórz w przeglądarce: **http://localhost:8777**
Zatrzymanie: **Ctrl+C** w terminalu.

---

## 5. Backtest i wykresy (oczy Cezara)

### Backtest z panelem HTML (otwiera się sam w przeglądarce):
```powershell
python narzedzia/backtest_dashboard.py dane/4h/Binance_BTCUSDT_4h.csv 4H
python narzedzia/backtest_dashboard.py dane/godzinowe/Binance_ETHUSDT_1h.csv 1H --okno 500
```

### Wykres PNG (cena + transakcje + krzywa kapitału):
```powershell
python narzedzia/wykres_backtestu.py dane/4h/Binance_DOGEUSDT_4h.csv 4h
python narzedzia/wykres_backtestu.py dane/4h/Binance_BTCUSDT_4h.csv 4h --max-barow 3000
```
→ zapisze `wykres_<PARA>_4h.png` obok repo — otwierasz dwuklikiem.

---

## 6. Pomiary skilla neuronów (czy rój naprawdę przewiduje)

```powershell
python narzedzia/raport_ic.py                         # IC roju (który neuron ma przewagę)
python narzedzia/raport_ic.py --glob "dane/dzienne/*_d.csv" --interwal 1d
python narzedzia/walk_forward_ic.py --glob "dane/4h/Binance_*_4h.csv" 4h --okna 4
python narzedzia/scoreboard_neuronow.py               # ranking kontrybucji neuronów
python narzedzia/raport_waznosci.py --do-areny        # Feature Importance MDA/SFI (López de Prado)
python narzedzia/hipoteza_b.py --max-barow 6000       # ważenie głosów IC vs równa waga (agregacja, OOS)
```
Triada pomiaru skilla: **IC** (korelacja) + **walk-forward** (stabilność) + **ważność** (MDA/SFI,
przyczynowość permutacyjna). `--do-areny` zapisuje MDA do bazy → Claude czyta `arena_pytaj`.
Interpretacja IC: `|IC|<0.02` = szum · `~0.03+` = realna przewaga · `>0.05` = mocny sygnał.

Walidacja bramki konformalnej (przed włączeniem `kalibruj_prog`) — A/B baza vs kalibracja:
```powershell
python narzedzia/walidacja_kalibrator.py
```
→ tabela trades/win-rate/PnL + werdykt. Bramka podnosi próg pewności po serii strat
(rój wchodzi rzadziej/pewniej, TYLKO zaostrza). Włączasz `kalibruj_prog=True` w konfiguracji
DOPIERO gdy walidacja to potwierdzi (Prawo I: decyzja z pomiaru).

---

## 7. Pobieranie danych rynkowych (lokalnie, poza gitem)

```powershell
python narzedzia/pobierz_4h_binance.py                # 4h z Binance (bez klucza)
python narzedzia/pobierz_4h_binance.py --pary XRP,ADA,LINK
python narzedzia/pobierz_nowe_pary.py                 # nowe pary z MEXC (1h→4h)
python narzedzia/pobierz_makro.py                     # dane makro
```
> Dane rynkowe (CSV) są **lokalne per-maszyna** — nie idą do gita (celowo). Pobierasz je na laptopie.

---

## 8. Pamięć (13 warstw) — komendy

```powershell
python -m imperium.biblioteki.centrum_pamieci start       # to co widzisz na starcie sesji
python -m imperium.biblioteki.centrum_pamieci szukaj "słowo"   # szukaj w całej pamięci
python -m imperium.biblioteki.dziennik_niesmiertelny ostatni   # ostatnie wpisy osi czasu
python -m imperium.biblioteki.kronika_czatu statystyki    # ile rozmów zapamiętane
```
Dziennik (oś czasu projektu) **pisze Claude sam na koniec sesji** — Ty nie musisz.

---

## 8b. MCP — Claude uczy się areny (soczewka na rój)

Mamy dwa własne serwery MCP + opcjonalny filesystem. Żeby je włączyć, utwórz plik
**`.mcp.json`** w katalogu projektu (raz):
```json
{
  "mcpServers": {
    "biblioteka": { "command": "python", "args": ["${CLAUDE_PROJECT_DIR:-.}/narzedzia/rag/mcp_server.py"] },
    "arena":      { "command": "python", "args": ["${CLAUDE_PROJECT_DIR:-.}/narzedzia/arena_mcp.py"] },
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "${CLAUDE_PROJECT_DIR:-.}"] }
  }
}
```
Przy starcie Claude zapyta o zgodę na te serwery — potwierdź. (Filesystem wymaga Node/npx;
jak nie masz Node, usuń tę linię — biblioteka i arena działają na samym Pythonie.)

Ręczny test Areny bez Claude:
```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python narzedzia/arena_mcp.py
```
Narzędzia areny (Claude woła je sam): `arena_roj` (migawka roju), `arena_neuron` (szczegóły),
`arena_zapisz`/`arena_pytaj` (baza wyników — akumuluje IC/scoreboard przez wachtę).

Domknięcie pętli — zasil bazę areny wynikami IC (odpalasz lokalnie, ma dane CSV):
```powershell
python narzedzia/arena_zasil.py --nota "wachta 0000-1200"
```
→ liczy IC roju i zapisuje per neuron do bazy. Potem Claude pyta `arena_pytaj` (rodzaj='IC')
i czyta skuteczność roju bez ponownego liczenia.

---

## 9. Klucze API (bezpieczeństwo — NIGDY w kodzie/czacie)

Ustawiasz raz jako zmienne środowiskowe (Windows), potem **zamknij i otwórz terminal**:
```powershell
setx DEEPSEEK_API_KEY "twój-klucz"     # doradca AI (platform.deepseek.com)
setx MEXC_API_KEY "twój-klucz"         # giełda MEXC (tylko dla trybu REAL)
setx MEXC_SECRET  "twój-sekret"
```
Test DeepSeek: `python -m imperium.cesarz.deepseek_glos` → ma napisać „Cesarz słyszy".

---

## 10. Rozwiązywanie problemów (rzeczy, na które już wpadliśmy)

| Problem | Objaw | Rozwiązanie |
|---|---|---|
| **Firma blokuje git przez SSH** | `ssh: connect ... port 22: timed out` | SSH przez port 443 — patrz niżej ⬇️ |
| **DeepSeek nie działa** | `FileNotFoundError: ...cacert.pem` | `Remove-Item Env:SSL_CERT_FILE` (kod sam to teraz naprawia) |
| **`bash` nie działa** | `WSL ERROR: /bin/bash` | użyj Git Basha: `& "C:\Program Files\Git\bin\bash.exe" ...` |
| **`git pull` blokuje** | `you have unstaged changes` | `git stash` → `git pull --rebase ...` → `git stash pop` |
| **Utknięty konflikt** | `needs merge` | `git reset` → potem stash/pull/pop |
| **Brak biblioteki** | `ImportError` | `pip install -r requirements.txt` |
| **Emoji wywala narzędzia** | `UnicodeEncodeError` / `cp1250 codec` | `setx PYTHONIOENCODING utf-8` (raz, potem nowy terminal) — patrz niżej ⬇️ |

### UTF-8 na Windows (konsola cp1250 dławi się emoji) — robisz raz:
```powershell
setx PYTHONIOENCODING utf-8
```
Potem **zamknij i otwórz terminal**. To naprawia WSZYSTKIE narzędzia Pythona naraz (mamy
pełno emoji w wynikach). `run_tests.py` i `audyt_spojnosci.py` mają dodatkowy bezpiecznik
w kodzie, ale ta zmienna załatwia całą resztę (raport_ic, arena_mcp, skan_wad…).

### SSH przez port 443 (gdy firma blokuje port 22) — robisz raz:
```powershell
Add-Content "$HOME\.ssh\config" -Value "Host github.com`n Hostname ssh.github.com`n Port 443`n User git"
```

---

## 11. Git — komendy awaryjne

```powershell
git status                     # co jest zmienione
git stash list                 # co masz schowane w kieszeni
git reset                      # odblokuj zablokowany indeks (pliki zostają)
git checkout -- <plik>         # cofnij zmiany w PLIKU (uwaga: kasuje lokalne zmiany)
git log --oneline -5           # ostatnie 5 commitów
```
> Gałąź robocza: **`claude/sleepy-fermi-dsdE4`**. Do `main` merguje **tylko Cezar ręcznie**.

---

## 🏁 Najprostszy dzień w 3 komendach

```powershell
cd C:\Projekty\imperial-mesh-vortex     # 1. wejdź do projektu
claude                                  # 2. odpal Claude (reszta dzieje się sama)
# ...pracujesz, rozmawiasz z Claude...  # 3. zamykasz — pamięć zapisze się sama
```

Wszystko inne z tej ściągi odpalasz **tylko gdy tego potrzebujesz**. Na co dzień: te 3 linie.
