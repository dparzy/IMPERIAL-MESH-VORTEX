# IMPERIUM — Instrukcje stałe dla Claude

> Ten plik jest czytany na początku każdej sesji. Zasady tu zapisane obowiązują ZAWSZE.

## 📜 Konstytucja

Pełne prawa: [`ZASADY_FUNDAMENTALNE.md`](./ZASADY_FUNDAMENTALNE.md).
Każda decyzja musi być zgodna z 16 Prawami Imperium.

## 🚨 PRAWO XV — CZERWONY ALARM UTRATY POTENCJAŁU (ROZKAZ STAŁY)

**Na końcu każdej sesji, każdego audytu i każdego większego zadania** — OBOWIĄZKOWO
sprawdź i odpowiedz Cezarowi na pytanie:

> *„Czy możliwości neuronów, zwiadowców, Bramy lub jakiegokolwiek modułu są
> ograniczone, niewykorzystane albo nieoptymalne?"*

Jeśli TAK — **podnieś głośny czerwony alarm 🚨**, nazwij to „UTRATA POTENCJAŁU",
zaraportuj wprost, napraw i zweryfikuj testami. **Milczenie = złamanie Prawa XV.**

Checklist utraty potencjału (sprawdzaj zawsze):
- [ ] Czy jakiś neuron zwraca zawsze NEUTRAL bo nie dostaje danych? (martwy głos)
- [ ] Czy jakiś wskaźnik jest liczony, ale nieużywany?
- [ ] Czy Brama umie mniej niż wymagają neurony? (wąskie gardło)
- [ ] Czy jakiś zwiadowca/moduł jest gotowy, ale niepodpięty do pipeline?
- [ ] Czy jakieś crossovery łamią się przez brak danych z poprzedniego baru?
- [ ] Czy dane wieloskładnikowe są redukowane do jednej liczby, gdy niosą więcej?

Cel: potencjał Imperium wykorzystany w 100%, nie w 11%.

## 📊 PRAWO XVI — REDUNDANCJA MIERZONA, NIE ZGADYWANA

Nie odrzucaj modułu za podobieństwo — odrzucaj za **skorelowany sygnał bez nowej
informacji**. Decyzja o redundancji opiera się na pomiarze, nie na opinii:

- `imperium/legiony/diagnostyka_korelacji.raport_dekorelacji(bary, zwiadowcy)`
- `|korelacja| > 0.80` → kandydat do scalenia / wagi w dół
- `|korelacja| < 0.20` → filar siły (zachować)
- stały sygnał (zerowa wariancja) → martwy głos = czerwony alarm Prawa XV

## 🔐 Bezpieczeństwo (NIENARUSZALNE)

- **KLUCZE API NIGDY W KODZIE, NIGDY W CZACIE** — tylko zmienne środowiskowe.
  - DeepSeek: `api_key=os.getenv("DEEPSEEK_API_KEY")` (`setx DEEPSEEK_API_KEY "..."`)
  - MEXC: `os.getenv("MEXC_API_KEY")`, `os.getenv("MEXC_SECRET")`

## 🧪 Testy

- Runner bez zależności: `python tests/run_tests.py`
- Każda zmiana logiki = nowe testy. Push tylko gdy wszystko zielone.

## 🌿 Git

- Rozwój na branchu: `claude/sleepy-fermi-dsdE4`
- Push: `git push -u origin <branch>`. PR tylko na wyraźną prośbę.
