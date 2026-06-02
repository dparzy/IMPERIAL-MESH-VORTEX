# IMPERIUM — Instrukcje stałe dla Claude

> Ten plik jest czytany na początku każdej sesji. Zasady tu zapisane obowiązują ZAWSZE.

## 📜 Konstytucja

Pełne prawa: [`ZASADY_FUNDAMENTALNE.md`](./ZASADY_FUNDAMENTALNE.md).
Każda decyzja musi być zgodna z **21 Prawami Imperium**.

**Prawo XVIII (decyzyjność):** gdy widzisz niespójność/błąd — rozstrzygasz SAM
(najlepsza opcja zgodna z zasadami), nie pytasz o błahostki. Źródło prawdy:
kod+testy > ZASADY > liczby policzone z plików > pamięć. Pytasz Cezara tylko o
decyzje kierunkowe/nieodwracalne (kasowanie, kapitał, zmiana strategii, koszt).

## 🗺️ PRAWO XVII — ROZPOZNANIE TERENU (ROZKAZ STAŁY, ROBISZ TO PIERWSZE)

### 🔒 KROK 0 — PEŁNA WERYFIKACJA SPÓJNOŚCI (ABSOLUTNIE PIERWSZE, przed czymkolwiek)

**Prawo XXI nakazuje chirurgiczną precyzję — zero tolerancji na rozbieżności.**

```bash
# 1. Stan git
git status                    # musi być: "nothing to commit, working tree clean"
python tests/run_tests.py     # musi być: X/X zielone

# 2. Żywy rój — liczby z kodu (nie z pamięci!)
python -c "
from imperium.legiony.rejestr import wszystkie_neurony, wszyscy_zwiadowcy, raport_potencjalu, raport_elity
n=wszystkie_neurony(); z=wszyscy_zwiadowcy(); p=raport_potencjalu(); e=raport_elity()
print(f'Neurony: {len(n)} | aktywne: {p[\"neurony_aktywne\"]} | wyciszone: {p[\"neurony_wyciszone\"]}')
print(f'Zwiadowcy: {len(z)} | aktywni: {p[\"zwiadowcy_aktywni\"]} | wyciszeni: {p[\"zwiadowcy_wyciszeni\"]}')
print(f'Elitarne: {e[\"lacznie_elite\"]} | Kategorie: {sorted({x.KATEGORIA for x in n})}')
bad=[x for x in n if x.KATEGORIA not in \"MTVFOLRSAKEGm\"]; print(f'Bad KAT: {[(x.KLUCZ,x.KATEGORIA) for x in bad]}')
"

# 3. WAGI_REZIMU — martwe litery (planowane A/L/V są OK — pre-zarejestrowane)
python -c "
from imperium.legiony.legatus import WAGI_REZIMU, WAGI_REZIMU_PLANOWANE
from imperium.legiony.rejestr import wszystkie_neurony, wszyscy_zwiadowcy
cats={n.KATEGORIA for n in wszystkie_neurony()} | {getattr(z,'KATEGORIA','?') for z in wszyscy_zwiadowcy()}
dead=[(r,k) for r,m in WAGI_REZIMU.items() for k in m if k!='_default' and k not in cats and k not in WAGI_REZIMU_PLANOWANE]
print('Nieoczekiwane martwe KAT:', dead or 'BRAK ✅')
"

# 4. Klucze MANIFEST vs KOD (Prawo XXI — klucze muszą się zgadzać)
python -c "
import re
from imperium.legiony.rejestr import wszystkie_neurony
with open('docs/MANIFEST_KODU.md') as f: txt=f.read()
section=txt.split('## ⚡')[1].split('## 📋')[0] if '## ⚡' in txt else ''
mkeys=set(re.findall(r'^\|\s*([A-Z][\w-]+)',section,re.M)) - {'KLUCZ'}
ckeys={n.KLUCZ for n in wszystkie_neurony()}
print('Tylko w MANIFEST:', sorted(mkeys-ckeys) or '✅')
print('Tylko w kodzie:  ', sorted(ckeys-mkeys) or '✅')
"
```

Sprawdź, że ta sama liczba neuronów pojawia się w **trzech miejscach jednocześnie**:
- `rejestr.py` → `wszystkie_neurony()` — ile klas zarejestrowanych?
- `docs/MANIFEST_KODU.md` → nagłówek "Zaimplementowane"
- `README.md` → liczba podana wprost

Jeśli którakolwiek się różni → STOP, napraw spójność zanim zaczniesz nowe zadanie.

**Niespójność = złamanie Prawa XVII + XXI. Każda sesja zaczyna się od czystego stanu.**

---

**Na początku KAŻDEJ sesji i przed KAŻDYM nowym zadaniem** — przeczytaj
stan Imperium, NIE zgaduj z pamięci:
- [ ] `README.md`, `CLAUDE.md`, `ZASADY_FUNDAMENTALNE.md`
- [ ] `docs/MANIFEST_KODU.md` — ile neuronów ✅ w kodzie (jedyne źródło prawdy)
- [ ] `docs/` — indeksy i katalogi (KATALOG_NEURONOW, KATALOG_STRATEGII, INDEKS_IMPERIUM)
- [ ] realny kod w `imperium/` vs to, co mówią dokumenty (katalog ≠ kod)
- [ ] aktualne liczby: neurony, zwiadowcy, prawa, testy — **policzone, nie z pamięci**

Po KAŻDEJ zmianie systemu **zaktualizuj dokumentację w tym samym ruchu**
(README, MANIFEST, indeksy, katalogi, liczby, status). Nieaktualny dokument = kłamstwo.

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

## 🔱 PRAWO XIX — KOD JEST PRAWEM (ROZKAZ STAŁY)

**Nic nie „istnieje" w Imperium bez kodu + testów na branchu `claude/sleepy-fermi-dsdE4`.**

Checklist Prawa XIX (sprawdzaj na początku sesji):
- [ ] Przeczytaj `docs/MANIFEST_KODU.md` — ile modułów naprawdę istnieje w kodzie?
- [ ] `grep "🔴" docs/MANIFEST_KODU.md` — które są tylko w katalogu?
- [ ] Po każdym nowym wdrożeniu → zaktualizuj MANIFEST_KODU.md w tym samym commicie.
- [ ] Nigdy nie mów "mamy X neuronów" bez sprawdzenia MANIFEST — tylko `✅` liczy się.

**Złamanie Prawa XIX:** twierdzenie, że moduł istnieje, gdy nie ma kodu na branchu.

## 🔬 PRAWO XXI — PROTOKÓŁ SPÓJNOŚCI: CHIRURGICZNA PRECYZJA (ROZKAZ STAŁY)

**Po KAŻDEJ zmianie kodu i przed KAŻDYM commitem** — uruchom pełny KROK 0 powyżej i sprawdź:

- [ ] **Warstwa 1 (kod):** KLUCZ, WSKAZNIK, KATEGORIA, WAGA, DOSTEPNY, ELITARNY — wszystkie poprawne
- [ ] **Warstwa 2A (WAGI_REZIMU):** każda litera KAT w mapie istnieje w `{n.KATEGORIA for n in wszystkie_neurony()}` — zero martwych liter
- [ ] **Warstwa 2B (Budowniczy):** każdy WSKAZNIK aktywnego neuronu jest produkowany przez Budowniczego (`wskazniki["KLUCZ"]` w kodzie)
- [ ] **Warstwa 3 (MANIFEST):** KLUCZ w tabeli = n.KLUCZ w kodzie — żadnych aliasów, żadnych starych nazw
- [ ] **Warstwa 3 (README):** liczba neuronów, testy, prawa = liczby z kodu (policzone, nie z pamięci)
- [ ] **Data "Stan na:"** w MANIFEST i README = data bieżącego commitu

**9 Nienaruszalnych Reguł (pełne: ZASADY_FUNDAMENTALNE.md § PRAWO XXI):**
1. Klucze MANIFEST = KLUCZ w kodzie — żadnych aliasów
2. KATEGORIA ∈ M/T/V/F/O/L/R/S/A/K/E/G — brak "?" u aktywnych
3. WAGI_REZIMU — tylko litery KAT faktycznie używane w kodzie
4. WSKAZNIK aktywnego neuronu = klucz produkowany przez Budowniczego
5. DOSTEPNY=False → neuron nie produkuje głosu (lista_niedostepnych())
6. ELITARNY=True → niepusty POWOD_ELITARNOSCI (raport_elity())
7. Testy zielone przed każdym push
8. Liczby w README/MANIFEST policzone, nie zaokrąglone
9. Data "Stan na:" = data commitu

**Złamanie Prawa XXI:** commit z rozbieżnością między kodem a dokumentacją.

## 🎖️ PRAWO XX — STATUS ELITARNY (MIERZONY, NIE OPINIĄ)

`rejestr.raport_elity()` — lista elit z kryterium E1-E7. Test `test_prawo_xx_status_elitarny` weryfikuje każdą sesję.

Checklist Prawa XX (sprawdzaj po każdej sesji z nowymi modułami):
- [ ] `raport_elity()["lacznie_elite"]` > 0 (minimum jeden elitarny moduł istnieje)
- [ ] Każdy ZwiadowcaElitarny ma ELITARNY=True (definicja Exploratores — kryterium E1)
- [ ] Neurony spełniające E1–E7 mają ELITARNY=True + niepusty POWOD_ELITARNOSCI
- [ ] Kryteria E1–E7 opisane w ZASADY_FUNDAMENTALNE.md § PRAWO XX

**Złamanie Prawa XX:** przyznanie statusu bez kryterium, lub posiadanie E1-E7 bez oznaczenia.

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
