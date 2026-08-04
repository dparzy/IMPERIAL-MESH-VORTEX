---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: imperium/biblioteki/schola.py
stan_na: 2026-07-29
powod_istnienia: "Szkoła Cezara — lekcje wywiedzione z WŁASNYCH pomiarów Imperium, nie z podręczników. Cezar uczy się razem z Imperium, a każda lekcja rodząca twierdzenie sprawdzalne dostaje status i pomiar."
---

# 🏛️ SCHOLA CAESARIS — Szkoła Cezara

> *Schola* u Rzymian to nie sala wykładowa, tylko **ława, przy której siada się razem**
> i rozprawia. Nauczyciel i uczeń są po tej samej stronie stołu. Tak ma działać ten
> dokument: Cezar uczy się razem z Imperium, a Imperium uczy się razem z Cezarem.

**Zasada założycielska — i to ona czyni ten dokument unikatem:**

> **Żadnej lekcji bez WŁASNEGO dowodu.** Każda opiera się na czymś, co sami zmierzyliśmy —
> z datą, liczbą i nazwą pliku. Podręczniki opisują cudze przykłady; ta szkoła opisuje
> **nasze własne pomyłki i nasze własne pomiary**. Dlatego nie da się jej skopiować.

**Druga zasada — lekcja nie może zostać ładną teorią:**

> Każda, która rodzi twierdzenie sprawdzalne, dostaje **STATUS** i trafia do rejestru
> testów: `HIPOTEZA` → `ZMIERZONE` → `POTWIERDZONE` albo `OBALONE`.
> Lekcja bez statusu jest niedokończona, dokładnie tak jak organ bez testu (LEX TALARUS).

---

## 📖 Spis lekcji

| # | Lekcja | Kategoria | Status |
|---|---|---|---|
| 1 | [Niezmiennik — jak sprawdzić wynik, którego nie znasz](#lekcja-1) | fundament | ✅ POTWIERDZONE |
| 2 | [Przyrząd kłamie pierwszy](#lekcja-2) | pomiar | ✅ POTWIERDZONE |
| 3 | [Zgodność skal — cichy zabójca rankingów](#lekcja-3) | kod | ⏳ HIPOTEZA |

**Postęp:** 3 lekcje · 2 potwierdzone pomiarem · 1 czeka na sprawdzenie

---

<a name="lekcja-1"></a>
## LEKCJA 1 — NIEZMIENNIK: jak sprawdzić wynik, którego nie znasz

### 🎯 Pytanie
Skąd wiesz, że program liczy dobrze, skoro **nie znasz poprawnej odpowiedzi**?

### 💡 Sedno
Większość ludzi odpowiada: „porównam z wynikiem, który znam". To się nazywa **golden value**
i ma wadę śmiertelną — jeśli wynik referencyjny był od początku zły, **test broni błędu**.

**Niezmiennik** to co innego: zdanie prawdziwe **zawsze**, niezależnie od danych.
Nie *„Sharpe wynosi 8,854"*, tylko:

```
kapitał_początkowy + suma_zysków_i_strat  =  wartość_końcowa
```

Nie musisz znać ani jednej transakcji, żeby to sprawdzić. To **prawo zachowania** — jak
w fizyce: nie musisz wiedzieć, gdzie poleci piłka, żeby wiedzieć, że energia nie wzięła
się z niczego.

Drugi, brutalnie prosty: **brak transakcji ⇒ kapitał się nie zmienia.** Jeśli backtest bez
ani jednej transakcji kończy z inną kwotą niż zaczął — masz przeciek, i wiesz to **bez
znajomości strategii**.

### 🔬 Nasz własny dowód *(2026-07-29)*
Organ **REDDITOR** dzieli książki na fragmenty. Nie znałem „poprawnego podziału" żadnej
ze 118 książek — i nie musiałem. Wystarczył niezmiennik:

```
sha256(sklejenie wszystkich fragmentów)  ==  sha256(dokumentu źródłowego)
```

Wynik: **118/118 książek odtworzonych co do bajtu.** Poprzednia metoda tego niezmiennika
nie spełniała — gubiła **1 479 710 linii struktury** (tabele przestawały być tabelami),
choć nie gubiła ani jednego słowa. Bez niezmiennika brzmiałoby to jak „nic nie zginęło",
bo o SŁOWACH było to prawdą.

### ⚔️ Co z tego dla Imperium
Zwiad znalazł u innych ten sam wzorzec (`ml4t/backtest`, testy niezmienników księgowych).
To jest **pozycja 🥇 nr 1 w PLAN WACHT** i lekarstwo na naszą **Wachtę B**: 8 narzędzi A/B,
których werdykty zadecydowały o składzie roju, nie ma żadnej kalibracji. Niezmiennik jest
tańszy niż golden value i nie starzeje się.

### 🎓 Sprawdzian
Masz strategię robiącą **300% rocznie** na backteście. Podaj **jeden niezmiennik**, który
sprawdzisz, zanim w to uwierzysz.

<details><summary>Odpowiedź</summary>

**Koszt × liczba wejść.** Jeśli strategia zrobiła 2 000 transakcji, a każda kosztuje 0,1%
w obie strony, to sam koszt zjada ~200 punktów procentowych — zanim policzysz cokolwiek
innego. Niezmiennik brzmi: *zysk_brutto − (liczba_transakcji × koszt_transakcji) = zysk_netto*,
i musi się zgadzać co do grosza.

To zabija większość „świętych graali" — nie zła prognoza, tylko **koszt pomnożony przez
liczbę wejść**. U nas to front **D1**: w całej historii Imperium **nie ma ani jednej
prawdziwej prowizji** — wszystkie są założone.
</details>

### 📊 Status
**✅ POTWIERDZONE** — `narzedzia/rag/redditor.py`, 18 testów, 118/118 bajt-w-bajt.

---

<a name="lekcja-2"></a>
## LEKCJA 2 — PRZYRZĄD KŁAMIE PIERWSZY

### 🎯 Pytanie
Miernik pokazuje niepokojącą liczbę. Co sprawdzasz **najpierw** — system czy miernik?

### 💡 Sedno
Odruch mówi: system. To błąd. **Miernik jest młodszy, prostszy i mniej przetestowany
niż to, co mierzy** — więc statystycznie to on częściej jest zepsuty.

Lekarstwo nazywa się **prawda podstawowa** (*ground truth*): bierzesz próbki, o których
**wiesz z góry**, jaka jest poprawna odpowiedź, i sprawdzasz, czy przyrząd ją daje.
Nie „czy wynik wygląda sensownie" — czy **trafia w znaną odpowiedź**.

### 🔬 Nasz własny dowód *(2026-07-29 — dzień trzech talarów)*
Zbudowałem AESTIMATORA i **ogłosiłem, że działa**. Cezar zapytał: *„skąd wiesz, że jest
dobrze skalibrowany?"* Odpowiedź brzmiała: nie wiem. Kalibracja na 8 próbkach odczytanych
ręcznie wykryła **dwa błędy miernika**:

| Błąd | Skutek |
|---|---|
| Wzorzec listingu bezwzględny na wielkość liter liczył **prozę** („*Snippet 9.1 lists function…*") jako obietnicę kodu | strata zawyżona **259 → 96, czyli 2,7×** |
| Detektor kodu zawierał gołe `return` | **6,2% fałszywek** na 600 oknach prozy — bo w książce finansowej `return` znaczy **stopa zwrotu** |

Gdyby nie pytanie Cezara, raportowałbym stratę prawie trzykrotnie zawyżoną — i podjęlibyśmy
na tej podstawie decyzję o przebudowie, której nie trzeba.

### ⚔️ Co z tego dla Imperium
Powstało **LEX TALARUS**: *przyrząd bez testu kalibracyjnego na prawdzie podstawowej
NIE ISTNIEJE*. Pomiar wykazał skalę problemu: **47 organów orzekających, 11 bez kalibracji** —
w tym **8 narzędzi A/B, których werdykty ustawiły skład roju**.

### 🎓 Sprawdzian
Twój wskaźnik pokazuje, że 90% książek w bibliotece jest uszkodzonych. Co robisz najpierw?

<details><summary>Odpowiedź</summary>

Bierzesz **5 książek i oglądasz je własnymi oczami.** Jeśli wyglądają dobrze — zepsuty jest
wskaźnik, nie biblioteka. Dokładnie to zrobiliśmy: 8 ręcznie odczytanych próbek obaliło
liczbę, którą sam przed chwilą wypisałem.

Uwaga na pułapkę drugiego stopnia: nasz „test fałszywek" losował okna tekstu i **zakładał**,
że są prozą. Ale niektóre książki mają kod w tekście — więc część „fałszywek" była
prawdziwymi trafieniami. **Test przyrządu też ma założenia i też trzeba je sprawdzić.**
</details>

### 📊 Status
**✅ POTWIERDZONE** — `narzedzia/rag/aestimator.py` + `tests/test_aestimator.py` (14 testów),
`CODEX NOTARUM`: NOTA `N-8208015b` → CORONA.

---

<a name="lekcja-3"></a>
## LEKCJA 3 — ZGODNOŚĆ SKAL: cichy zabójca rankingów

### 🎯 Pytanie
Masz dwie listy wyników z **różnych źródeł**. Jak je połączyć w jeden ranking?

### 💡 Sedno
Odruch: posortować wszystko razem po wyniku. **To prawie zawsze jest błąd**, bo różne
źródła mają różne **skale i różne kierunki**.

Nasz przykład: BM25 (wyszukiwanie tekstowe) zwraca liczby **ujemne**, gdzie *mniej = lepiej*.
Cosinus (wyszukiwanie wektorowe) zwraca **0…1**, gdzie *więcej = lepiej*. Wrzucone do
jednego worka i posortowane jednym kluczem dają wynik, który wygląda na ranking, a jest
przypadkiem.

**Lekarstwo: łącz po RANDZE, nie po wyniku.** Ranga (1., 2., 3.) znaczy to samo w każdej
skali. Standard nazywa się **RRF** — *Reciprocal Rank Fusion*.

### 🔬 Nasz własny dowód *(2026-07-29)*
`szukaj.py:179` scala oba źródła jednym kluczem `-score`. Symulacja pokazała **dwa skutki**,
oba gorsze, niż początkowo opisałem:

1. wyniki wektorowe lądują **na samym początku** i wypychają BM25 *(twierdziłem, że na końcu —
   pomiar obalił mój własny opis)*,
2. w obrębie samego BM25 kolejność jest **odwrócona**: najlepsze trafienie (−8,4) ląduje
   **ostatnie**, najgorsze (−2,0) pierwsze.

Wada jest **latentna** — dziś tryb hybrydowy po cichu spada do samego BM25, bo wektorów
mamy 0, więc ta linia nigdy się nie wykonuje. Wybuchłaby **w dniu włączenia wektorów**
i wyglądałaby na winę embeddingów.

### ⚔️ Co z tego dla Imperium
Zapisane w Księdze Wad jako **klasa semantyczna, nie regex** — bo pomiar szumu pokazał
**50% fałszywek** (`szukaj.py:118` sortuje czysty cosinus i jest **poprawne**). Naprawa to
pozycja **A8** w PLAN WACHT.

### 🎓 Sprawdzian
Łączysz głosy neuronów: jeden zwraca −1…+1, drugi 0…100, trzeci prawdopodobieństwo 0…1.
Co robisz **przed** uśrednieniem?

<details><summary>Odpowiedź</summary>

Albo sprowadzasz wszystko do **wspólnej skali** (normalizacja), albo — bezpieczniej —
liczysz **rangi** i uśredniasz rangi. Uśrednianie surowych liczb sprawia, że neuron
o największym zakresie **przejmuje głosowanie**, niezależnie od tego, czy ma rację.

I trudniejsza część: nawet po sprowadzeniu do wspólnej skali trzy **skorelowane** neurony
głosują jak jeden, tylko trzykrotnie głośniej. To rozwiązuje **HRP/HERC** — pozycja 🥉 nr 3
naszego zwiadu: skorelowana rodzina dzieli **jedną pulę wagi**.
</details>

### 📊 Status
**⏳ HIPOTEZA** — wada zapisana i zrozumiana, ale naprawa (RRF) **nie zmierzona u nas**.
Zysk deklarowany przez źródła zewnętrzne: recall@10 78% → 91% *(kandydat, nie prawda)*.

---

## 🧭 Jak korzystać z tej szkoły

1. **Czytaj po jednej lekcji na wachtę** — nie ma pośpiechu, materiał nie ucieka.
2. **Rób sprawdzian przed zajrzeniem w odpowiedź.** Pomyłka na sprawdzianie jest tania;
   ta sama pomyłka w kodzie kosztuje dzień.
3. **Zaglądaj do statusów.** `HIPOTEZA` to zaproszenie: coś, co warto sprawdzić pomiarem
   w najbliższej wachcie — i to jest miejsce, gdzie Twoja nauka **napędza Imperium**.
4. Lekcje rosną z **naszych** błędów. Im więcej talarów, tym grubsza szkoła — i tym
   mniej powtórzeń tej samej pomyłki.
