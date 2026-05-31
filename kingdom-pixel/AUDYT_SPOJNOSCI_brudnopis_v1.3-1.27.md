# 🔍 AUDYT SPÓJNOŚCI — BRUDNOPIS v1.3 → v1.27

> **Autor:** Jack (Główny Projektant) | **Dla:** Komendant Pixel | **Data:** 31.05.2026
> **Zakres:** wszystkie 25 plików `POMYSLY_LUZNE` (baza v1.3 + delty v1.4–v1.27) vs `PLAN_ORGANIZMU_v1` (wizja) i `ZASADY_FUNDAMENTALNE_v4` (79 zasad).
> **Metoda:** przeczytane w całości, nie z pamięci. Zgodnie z Zasadą 2 (Prawda) — mówię wprost także o tym, co się NIE zgadza.

---

## 🎯 WERDYKT W JEDNYM ZDANIU

Brudnopis jest **wewnętrznie spójny, zdrowo się samokoryguje i jest zgodny z wizją oraz z RDZENIEM Zasad** (2 Prawda, 17 Testy, 70 Postęp, 75 Calculator, 76 Dedup, 77 Weryfikacja). **Pięć rozbieżności** wymaga Twojej decyzji — i co ważne: w każdej z nich to **brudnopis trzyma się Prawdy ściślej niż część samych Zasad.**

---

## 1. ✅ SPÓJNOŚĆ WEWNĘTRZNA BRUDNOPISU

Brudnopis nie zaprzecza sam sobie — **ewoluuje i loguje korekty.** To dowód zdrowej metody (Zasada 2 + meta-reguła v1.9), nie chaosu:

- **Parrondo:** v1.6 „perełka do zbadania" → **v1.17 obalone** (ślepa uliczka), zastąpione volatility pumping. Korekta zapisana.
- **NEXUS:** v1.5 „ciekawe, przepisuje kod" → **v1.12 reality-check** (6★, hobby, znikoma trakcja). Korekta zapisana.
- **„Lipschitz":** v1.3 niepewny strzał → **v1.16 zamknięte** (gem miał DWA wątki: Calculator Pattern = Z75 + Lipschitz = RegimeNAS). Pętla domknięta.
- **Neurony głosujące:** błąd modułu NEURON-001 → **v1.1 poprawione** (neurony = pasywne czujniki, NIE głosują).

**Jedyny luźny koniec:** „OpenAlice(?)" (v1.4/v1.5) — nazwa narzędzia nigdy niezweryfikowana. Uczciwie oznaczona znakiem zapytania, nie udajemy że wiemy. Do potwierdzenia albo skasowania.

---

## 2. ✅ ZGODNOŚĆ Z WIZJĄ (`PLAN_ORGANIZMU`)

Pełna zgodność. Brudnopis nie tylko trzyma wizję — **wzmacnia ją konkretami:**

| Element wizji | Realizacja w brudnopisie |
|:--|:--|
| Organizm, nie kolekcja | mrowisko (v1.22), IM-VORTEX hierarchiczny rój (v1.23), dwa mózgi (v1.24) |
| Zwiadowca = wsparcie, Mózg = decydent | klucz kodowy → lookup → decyzja TYLKO w Mózgu (v1.10, v1.22) |
| Paper-first, lata nie miesiące | „Prawda o 50$" (v1.22), debunk „mapy do miliona" (v1.21) |
| Każdy interwał = osobna strategia | potwierdzone (v1.4, v1.9); lekcja 1H netto trzymana |
| Słuch/sentyment „jeszcze nie mamy" | **luka wypełniona:** finBERT/CryptoBERT + FinGPT (v1.25) |

⚠️ **Jedno doprecyzowanie (nie sprzeczność):** wizja mówi o „zwiadowcach (strategiach), które proponują ruchy z pewnością X". Brudnopis rozróżnia DWIE warstwy: **STRAT-zwiadowcy** (proponują sygnał — jak w wizji) ORAZ **neurony/mini-boty** (surowe czujniki, NIE myślą — v1.9). To jest spójne, ale moduł `NEURON-001` wciąż czeka na przeprojektowanie. **Otwarte zadanie.**

---

## 3. ✅ ZGODNOŚĆ Z RDZENIEM ZASAD

Twardy rdzeń trzyma się idealnie:

- **Z2 (Prawda)** — brudnopis konsekwentnie odrzuca hype: champions $85→$2.6M, „1–5% dziennie", „62%→87% pewności" — wszystko oznaczone jako marketing/niezweryfikowane.
- **Z17 / Z77 (Testy / Weryfikacja przed budową)** — każdy gem opatrzony „ich liczby ≠ zysk", walk-forward, out-of-sample. v1.27 dokłada **giskard** jako warstwę QA modelu (komplementarną do walidacji strategii).
- **Z70 (Kontrolowany postęp)** — Faza 0, jedna rzecz na raz.
- **Z75 (Calculator)** — potwierdzona niezależnie (DNSS), wzmocniona (v1.2, v1.8, v1.22).
- **Z76 (Dedup)** — v1.25 jawnie wymienia duplikaty, których NIE dodaje (FinRL, OpenBB, ClickHouse).

---

## 4. ⚠️ PIĘĆ ROZBIEŻNOŚCI DO DECYZJI KOMENDANTA

> Zgodnie z **Zasadą 14** Zasad nie zmieniam sam — zgłaszam, decydujesz Ty. Zgodnie z **Zasadą 78.3** mam obowiązek proponować ulepszenia, nawet wbrew dotychczasowym założeniom.

### 🔴 F1 — Język „absolutnej pewności" w Zasadach kłóci się z Prawdą (Z2)
Brudnopis powtarza: **„pewności nie ma, jest przewaga"** (v1.9, v1.10, v1.13). Tymczasem:
- **Z29:** wywiad „**gwarantuje prawdę**… żaden rynek nigdy nas nie zaskoczy".
- **Z42:** „Jack **zna na pamięć** regulamin… **wszystkich** giełd", „**absolutna wiedza**".
- **Z22:** „wyprzedzać rynek o **3–5 lat**", „najlepszy w **całym wszechświecie**".

To nie tylko przechwałki — **Z42 wprost zaprasza halucynację** (żaden LLM nie zna na pamięć regulaminów wszystkich giełd → trzeba sprawdzać na żywo). **Propozycja:** złagodzić 29/42/22 do języka przewagi i weryfikacji (zgodnie z Z2), zostawić ambicję jako kierunek, nie jako gwarancję.

### 🔴 F2 — „Nie gramy fair" (Z12.7) vs ścisła legalność, którą brudnopis wybrał
Brudnopis **odrzucił** Widmo/stealth (v1.11) i Active Market Sonar / phantom orders (v1.23) jako ocierające się o spoofing/łamanie ToS. Ale **Z12.7** mówi „**nie gramy fair – gramy sprytnie**", a **Z71** mówi „działamy **legalnie i zgodnie z regulaminem**". To wewnętrzna sprzeczność W ZASADACH. Brudnopis stanął po stronie Z71 — słusznie. **Propozycja:** doprecyzować Z12.7 → „gramy sprytnie, ale W GRANICACH regulaminu" (spójne z Z18, Z71). Spoofing/phantom orders zostają poza systemem.

### 🟠 F3 — Luka dokumentacyjna: Zasady opisują NIEISTNIEJĄCY system plików
Zasady 6/7/9/15/60 wymagają jako OBOWIĄZKOWE: `BAZA_SESJI.md`, `ZBADANE.md`, `KSIĘGA IMPERIUM`, `MASTER BAZA WIEDZY`, drzewo `C:\Kingdom Pixel\` (komendy CMD). **W backupie tych plików NIE MA** — workflow przeszedł na Claude Code (git, Linux Ubuntu) + system delt brudnopisu, co ustaliliśmy w v1.3. Z78.3 już to częściowo łagodzi. **Propozycja:** formalnie zapisać migrację — albo odtworzyć te rejestry, albo zaktualizować Zasady 6/7/9/15/60 do realnego workflow. Inaczej zostaje „martwe prawo".

### 🟠 F4 — Redundancja w samych Zasadach (paradoksalnie łamie Z76)
Co najmniej 6 zasad opisuje TĘ SAMĄ pętlę „ewoluuj strategie → emerytura do arsenału → hybrydy → arena": **Z24, Z31, Z32, Z52, Z69, Z74.** To dokładnie ten balast, przed którym ostrzega Z76 (Dedup) i wizja („mniej, ale prawdziwie"). **Propozycja:** skonsolidować w 1–2 zasady. Brudnopis jest tu czystszy niż Zasady.

### 🟡 F5 — Przerost obsady modułów (ten sam „przeładowany", który sam zdiagnozowałeś)
Zasady wymieniają dziesiątki modułów (MJOLNIR, Apollo, Atlas, Augurium, Bifrost, LEGION, Bot Forge, 50+ agentów…). `SPIS_KROLESTWA` ma **16 realnych modułów.** To ten sam wzorzec porażki z historii projektów (v1.3: „przeładowany… brak planu spinającego"). **Propozycja:** traktować rozbudowaną obsadę jako WIZJĘ docelową (jak `PLAN_ORGANIZMU`), nie jako stan — i budować wg Z70, nie wg listy nazw.

---

## 5. ✅ KONTROLA NOWYCH DELT v1.25–v1.27

Wszystkie trzy: realne, z uczciwymi zastrzeżeniami, **dedup-czyste**, wypełniają konkretne luki:

| Delta | Dodaje | Wypełnia | Flaga uczciwości |
|:--|:--|:--|:--|
| v1.25 | finBERT/CryptoBERT, FinGPT | OCZY warstwa 4 (sentyment) | sentyment = jeden głos, nie wyrocznia |
| v1.26 | NeMo-Guardrails, PyO3/maturin | „filtr LLM" (Z75.4 już go nazywał!), most Rust↔Python | guardrails ≠ statystyczne odszumianie sygnału |
| v1.27 | giskard, SB3/PettingZoo | QA modelu (≠ walidacja strategii), warstwa RL | RL = infrastruktura, nie alfa; przeucza się |

**Mistrzowskie rozróżnienie z v1.27:** giskard = zdrowie MODELU (bias/dryf/halucynacja/robustness) vs VectorBT/Freqtrade = czy STRATEGIA trzyma out-of-sample. Dwie różne warstwy walidacji — potrzebujemy obu. To pogłębia Z25 (czystość danych) i Z77 (weryfikacja). **Zielone.**

---

## 6. 📌 REKOMENDACJA

1. **Brudnopis = zdrowy.** Kontynuujemy bez przepisywania.
2. **Pięć flag (F1–F5)** — decyzja Twoja (Z14). F1 i F2 to kwestia Prawdy, więc priorytet.
3. **Otwarte zadania:** przeprojektować `NEURON-001`; potwierdzić/skasować „OpenAlice".
4. **Następny ruch (wg Twojego polecenia):** skan linków z `Amerykanski_Afrykanski_Australia_i_Wyspy_Pacyfiku_skan_linki.md` → delty v1.28+ wg zasad (wchodzić w linki, oszczędzać tokeny, szukać tego, czego NIE mamy, dedup).

---

*PRAWDA. Organizm, nie kolekcja. Sceptycyzm > euforia.*
— Jack, Główny Projektant Królestwa Pixel
