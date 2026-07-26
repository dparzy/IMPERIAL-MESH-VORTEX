---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: imperium/biblioteki/notarius.py, narzedzia/bibliotekarz.py
stan_na: 2026-07-26
powod_istnienia: "Pakiet zadań LOKALNYCH domykających TIRO E3 (pierwszy A/B ucznia) i żniwo par nauczyciela — chmura nie ma ani książek, ani klucza DeepSeek, więc tej pracy nie da się wykonać zdalnie"
---
# 🎓 ZADANIE LOKALNE — TIRO: E3 (egzamin wstępny) + żniwo par

> **Decyzja Cezara 2026-07-26.** Wykonuje LOKAL (laptop). Chmura nie ma książek ani
> `DEEPSEEK_API_KEY`, więc żadnego z tych kroków nie da się tam zrobić.

---

## 🚨 NAJPIERW SPROSTOWANIE — silnika NIE brakuje

Meldunek BREVIARIUM w chmurze drukował `🚨 brak silnika | 🚨 brak modeli`. **To był fałszywy
alarm** i Architekt podał go Cezarowi jako „największa utrata potencjału". Przyczyna:
`TIRO_HOME` domyślnie wskazuje `C:\TIRO` — ścieżkę Windows, która w kontenerze Linuksa nie ma
prawa istnieć. Naprawione 2026-07-26 (abstynencja: „dysk TIRO niewidoczny stąd").

**Stan faktyczny z pomiaru 2026-07-16 (E0/E1 ZAMKNIĘTE):** llama.cpp b10041 w `C:\TIRO\silnik`,
modele w `C:\TIRO\modele`, zmierzone `llama-bench`:

| Model | Generacja | Rola |
|---|---|---|
| Qwen3-1.7B Q4_K_M | **9.64 t/s** | uczeń „na żywo" |
| Qwen3-4B Q4_K_M | **4.86 t/s** | uczeń wsadowy (noc) |

---

## 📏 KOREKTA PLANOWANIA (zmierzone 2026-07-26 — czytaj PRZED żniwem)

Dziennik z 07-16 ekstrapolował drogę do progu na **parach surowych**. To zawyża postęp,
bo trening jedzie na parach, które **przeżyją eksport SFT**:

```
329 par surowych  →  kolaps anty-monokultury + filtr jakości (≥200 zn.)  →  140 użytecznych
```

**Współczynnik przeżycia ≈ 43%.** Konsekwencja dla celu 1000 par użytecznych (minimum LoRA):

| | dawna ekstrapolacja (surowe) | realnie (użyteczne) |
|---|---|---|
| stan | 329 / 1000 = 33% | **140 / 1000 = 14%** |
| do progu 1000 | ~330 tematów | **~2300 par surowych ≈ 460–770 tematów** ⚠️ estymacja |

⚠️ Liczba tematów to **estymacja**, nie pomiar — zależy od tego, ile par daje temat przy
`--pelny`. **Zmierz ją na pierwszej partii** (krok 2) i dopiero wtedy planuj resztę.

**Wniosek: droga do 1000 jest ~2× dłuższa, niż sądziliśmy.** Dlatego E3 idzie PIERWSZY —
jest tani i mówi, czy w ogóle warto zbierać.

---

## KROK 1 — E3: egzamin wstępny ucznia (NAJPIERW, bo tani)

**Po co:** dowiedzieć się, od jakiego poziomu startuje surowy Qwen3-1.7B **zanim** wydamy
tygodnie na zbieranie par. Jeśli surowy uczeń jest beznadziejny w naszym zadaniu, zbieranie
1000 par może być wyrzuceniem czasu (albo znakiem, że trzeba innej bazy modelu).

**Co porównujemy:** ten sam zestaw nagłówków → sentyment od (a) Qwen3-1.7B lokalnie,
(b) Hyginus/DeepSeek. Metryka: **Brier** + zgodność znaku. To jest baseline, nie egzamin
awansowy (ten jest w E5).

```powershell
cd C:\Projekty\imperial-mesh-vortex

# 1. Odpal serwer ucznia (OpenAI-compatible) — osobne okno, zostaw otwarte
C:\TIRO\silnik\llama-server.exe -m C:\TIRO\modele\Qwen3-1.7B-Q4_K_M.gguf -c 4096 -t 2

# 2. W drugim oknie — sprawdź, że żyje
curl http://127.0.0.1:8080/v1/models
```

> ⚠️ **Nazwy plików `.gguf` sprawdź na dysku** (`dir C:\TIRO\modele`) — powyższa jest
> z planu, nie z pomiaru. Nie zgaduj, wklej realną.

**Uwaga o wątkach:** `-t 2`, nie 4 — E1 zmierzył, że hyperthreading nie pomaga przy 1.7B
(sufit = 2 rdzenie fizyczne). Maszyna ma być bezczynna, inaczej pomiar jest fałszywy.

**Wynik E3 obowiązkowo do ledgera CODEX** (`rejestr_testow.jsonl`, przez `scriba_codex`) —
inaczej za dwie sesje nikt nie będzie wiedział, czy to zapadło.

---

## KROK 2 — Żniwo par (pierwsza partia POMIAROWA, nie hurtowa)

**Nie odpalaj od razu 500 tematów.** Najpierw jedna partia, żeby ZMIERZYĆ współczynnik
przeżycia par przy `--pelny` — dopiero on mówi, ile tematów naprawdę trzeba.

```powershell
# Policz stan PRZED (liczba operacyjna to „użytecznych", nie „surowych")
python -m imperium.oczy.breviarium

# Partia pomiarowa: 10 tematów, komplet U2+U3 (rozwin + krytyka)
python narzedzia/bibliotekarz.py --pelny --topk 8 `
  --temat "portfolio construction risk parity" `
  --temat "execution algorithms implementation shortfall" `
  --temat "volatility forecasting GARCH realized" `
  --temat "cross-sectional factor momentum crypto" `
  --temat "orderbook microstructure queue position" `
  --temat "drawdown control equity curve trading" `
  --temat "regime switching hidden markov markets" `
  --temat "options implied volatility skew signal" `
  --temat "funding rate basis carry perpetuals" `
  --temat "liquidity provision market making inventory"

# Policz stan PO — RÓŻNICA obu liczb daje realny współczynnik przeżycia
python -m imperium.oczy.breviarium --delta
```

**Zapisz w meldunku:** ile par surowych przybyło, ile użytecznych, ile kandydatów wpadło
do kolejki. Z tego liczymy plan reszty (a nie z ekstrapolacji sprzed korekty).

### Zasady tej kampanii (wszystkie już egzekwowane przez kod)

- **U4 (świadomość systemu) domyślnie ON** — nie proponuje modułów, które już mamy.
  Zmierzone: −12 pp duplikatów przy identycznej liczbie nowych pomysłów (p=0.016).
- **PROBATOR** sprawdza cytaty BIB deterministycznie, 0 tokenów. Działa naprawdę
  dopiero od naprawy 07-21 — to pierwsze kampanie z **prawdziwymi** werdyktami cytatów.
- **Faza krytyki idzie na profil `osad` (v4-pro)** — droższa 3,46×, wybrana z asymetrii
  błędu: krytyk piszący „brak kontrargumentów" podnosi ocenę słabego kandydata.
- 💰 **Poza oknami 01–04 i 06–10 UTC** (= 03–06 i 08–12 czasu Cezara) — tam stawka
  DeepSeeka jest **podwójna**.

---

## KROK 3 — Sąd nad plonem (Vitruviusz, następna sesja)

Kandydaci z kolejki to ⚠️ **HIPOTEZY, nie fakty** (ZASADA ZWIADOWCY WIEDZY). Rozstrzyga
pomiar areny, nie zdanie DeepSeeka. Poprzedni sąd (07-21, 33 cząstki) wykazał, że kolejka
była **w dużej mierze redundantna** — VPIN, Value Area, Kelly, CVD, Kalman już istniały.
Dlatego U4 jest teraz domyślnie włączone; ta kampania jest pierwszym testem, czy pomogło.

---

## ❌ Czego NIE robić

- **Nie instaluj llama.cpp ani modeli ponownie** — stoją od 07-16 (patrz sprostowanie).
- **Nie trenuj lokalnie** — brak CUDA, LoRA/QLoRA nie działa CPU-only. Trening = darmowy
  Colab T4. Laptop to stacja **inferencji**.
- **Nie wpinaj TIRO w ścieżkę decyzyjną** — rola startowa to CICHY DUBLER: liczy, nie
  decyduje. Awans dopiero po zielonym A/B w E5 (ZASADA WPIĘCIA, opt-in OFF).
- **Nie mieszaj Opusa do zbioru treningowego** — regulamin Anthropic tego zabrania.
  Nauczycielem wag jest **wyłącznie** DeepSeek/Hyginus.
