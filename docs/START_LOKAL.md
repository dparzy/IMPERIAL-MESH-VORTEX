# 🖥️ START LOKALNY — pełny przewodnik (dla Cezara, nowicjusza)

> **Stan na:** 2026-06-30 · Jak uruchomić Imperium na własnym komputerze z PEŁNĄ pamięcią
> (13 warstw) + dodatki, których chmura nie ma. Krok po kroku, bez żargonu.

## 🎯 Po co lokal, skoro jest chmura?

| | ☁️ Chmura (teraz) | 🖥️ Lokal (Twój komputer) |
|--|------------------|---------------------------|
| Pamięć 13 warstw | ✅ (przez git) | ✅ (przez git) |
| Każda nasza rozmowa | ✅ kronika w git | ✅ kronika w git |
| **Wektory semantyczne** (szukanie po znaczeniu) | ❌ proxy blokuje | ✅ |
| **Pełny dysk** (wszystkie pliki, nie tylko repo) | ❌ | ✅ przez MCP |
| **Trwałe logi transakcji** (W1) | znikają z kontenerem | ✅ na dysku |
| **DeepSeek auto-lekcje** | wymaga klucza | ✅ klucz lokalnie |
| Limit kontekstu | mały | większy |

**Najważniejsze:** pamięć (rozmowy, lekcje, wizje, dziennik, graf) jest **ta sama** w obu —
płynie przez git. Lokal **DODAJE** moce, nie zastępuje.

---

## 1️⃣ Aktualizacja lokala — JEDNO KLIKNIĘCIE (Windows/PowerShell)

W folderze repo uruchom:

```powershell
.\aktualizuj.ps1
```
(jeśli PowerShell blokuje: `powershell -ExecutionPolicy Bypass -File .\aktualizuj.ps1`)

Ten jeden skrypt robi WSZYSTKO po kolei: właściwa gałąź → chowa Twoje lokalne zmiany →
`git pull` (cała pamięć 13 warstw) → `pip install` → testy → indeks RAG (wektory) →
odświeża pamięć (katalog+graf) → mapa 13 warstw → test DeepSeek (jeśli ustawiłeś klucz).
Bezpieczny: dane w `dane/` nietknięte, lokalne zmiany schowane i przywrócone.

### Ręcznie (Linux/Mac lub gdy wolisz krok po kroku):
```bash
git checkout claude/sleepy-fermi-dsdE4
git pull origin claude/sleepy-fermi-dsdE4
pip install -r requirements.txt
python skrypty/start_lokal.py                  # rozruch + weryfikacja
```

> ⚠️ Jeśli `git checkout` narzeka na lokalne zmiany — zrób `git stash` najpierw.

---

## 2️⃣ Jedna komenda rozruchu (robi resztę za Ciebie)

```bash
python skrypty/start_lokal.py
```

To zrobi po kolei: wykryje środowisko → audyt spójności → zbuduje katalog + graf pamięci →
zindeksuje RAG (wektory jeśli dostępne) → pokaże mapę 13 warstw. Na końcu da wskazówki.

---

## 3️⃣ Włącz PEŁNĄ moc (dodatki tylko-lokal)

### A) Wektory semantyczne (szukanie po znaczeniu, nie tylko słowach)
```bash
pip install sentence-transformers
python narzedzia/rag/indeksuj.py --korpus wszystko     # zbuduje wektory
```
→ RAG (W2) i potencjalnie graf (W8) zaczynają rozumieć synonimy/parafrazy.
Szczegóły: `narzedzia/rag/SETUP_LOKALNY.md`.

### B) Pełny dysk — Claude widzi WSZYSTKIE Twoje pliki (nie tylko repo)
Dodaj serwer Filesystem MCP (jednorazowo):
```bash
claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem /sciezka/do/folderu
```
→ Claude może czytać/pisać pliki na dysku **za Twoją zgodą per akcja**. Wybierasz które foldery.

### C) DeepSeek auto-lekcje (pamięć sama wyciąga wnioski z sesji)
```bash
setx DEEPSEEK_API_KEY "twój-klucz"     # Windows; Linux/Mac: export w ~/.bashrc
```
→ Hook po sesji uruchomi `narzedzia/auto_lekcja.py` — wnioski trafią do W3/W4 automatycznie.

---

## 4️⃣ Czy lokal ma dostęp do wszystkich dokumentów/kodu?

- **Repo Imperium (kod + 13 warstw pamięci):** TAK, automatycznie po `git pull`.
- **Inne pliki na dysku (poza repo):** TAK, po włączeniu Filesystem MCP (pkt 3B) — wtedy
  Claude widzi wskazane foldery dysku, za Twoją zgodą.
- **Pamięć rozmów:** TAK — kronika (każde zdanie) jest w repo, więc lokal czyta całą historię.

---

## 5️⃣ Paper-trading (symulacja — zero prawdziwych pieniędzy)

```bash
python skrypty/start.py            # uruchamia rój + dashboard na http://localhost:8777
```
Zatrzymanie: `Ctrl+C`. To bezpieczna piaskownica — tu testujesz strategie.

### 🔴 Domknięcie luki (rekomendacja Prawo XV)
Pamięć pokazała, że **konfigurowaliśmy test DOGE/MEXC (06-22), ale wynik nie trafił do pamięci**
(W1 ma 0 logów). Gdy odpalisz lokala — pierwszy paper-trading powinien logować do `pamiec_absolutna`
(W1), żeby każdy trade został zapamiętany na zawsze. Wtedy już nigdy „nie zgubimy testu".

---

## 6️⃣ Weryfikacja, że wszystko gra

```bash
python tests/run_tests.py             # ma być X/X zielone
python narzedzia/audyt_spojnosci.py   # ma być: pełna harmonia (exit 0)
python -m imperium.biblioteki.kustosz_pamieci mapa   # zobacz 13 warstw pamięci
```

---

## 📌 Najważniejsze do zapamiętania

1. **Pamięć płynie przez git** — `git pull` = masz wszystko, co zbudowaliśmy w chmurze.
2. **Lokal = chmura + dodatki** (wektory, pełny dysk, trwałe logi, DeepSeek).
3. **`requirements.txt` musi być zainstalowany w pełni** — inaczej np. BOCPD milczy (brak scipy).
4. **Pierwszy lokalny paper-trading → loguj do W1**, żeby domknąć lukę niezapamiętanego testu.
