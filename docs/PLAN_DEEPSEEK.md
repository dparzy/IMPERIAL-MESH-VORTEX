---
kategoria: CONSILIUM
typ: zywy
wlasciciel: imperium/cesarz/deepseek_glos.py, imperium/akwedukty/adaptery/news_llm.py, imperium/biblioteki/notarius.py
stan_na: 2026-07-18
powod_istnienia: "Plan podłączenia DeepSeek API jako 'głosu' Imperium (adapter GlosImperium) + weryfikacja, GDZIE DeepSeek naprawdę trafił — realizacja poszła inną drogą niż plan (nie Senat, lecz Oczy/newsy + zwiad wiedzy + NOTARIUS)."
dublet_rozstrzygniety: docs/PLAN_TIRO_LOKALNY_LLM.md — notarius jest tu opisany jako KONSUMENT GlosImperium (skąd DeepSeek zbiera pary prompt→odpowiedź); w PLAN_TIRO ten sam notarius żyje jako element pipeline TRENINGU lokalnego LLM. Różne role tego samego modułu, świadomy podział, nie dublet treści.
---
# 🧠 PLAN: DeepSeek API jako głos Imperium — plan vs realizacja

> **Źródło:** rozmowa DeepSeek o budowie multi-bota (`archiwum/DeepSeek_API_multibot_oryginal.md`)
> **Po co:** Komendant ma klucz DeepSeek API. To tani, szybki LLM. Adapter `GlosImperium` jest
> jedynym wejściem LLM w Imperium.
>
> **Sprzęt (zmierzone, `censor_sprzetu.py`):** Fujitsu 15.88 GB RAM, 4 wątki, brak CUDA — klasa
> PEDES. Ciężka praca LLM idzie przez API dla SZYBKOŚCI (wąskie gardło to CPU/brak GPU, nie RAM).
> (Projekt TIRO buduje hybrydę lokalną — patrz `docs/PLAN_TIRO_LOKALNY_LLM.md`.)

> **⚠️ Weryfikacja wobec kodu 2026-07-17.** Adapter `GlosImperium` **istnieje i jest żywy** ✅,
> ale **realizacja poszła INNĄ drogą niż ten plan.** Trzy moduły, które plan wskazywał jako
> odbiorców (titan_mind, meta_kora, wszechoko), **wcale nie wołają DeepSeeka** — a wołają go
> cztery inne, których plan nie przewidział. Sekcja niżej rozdziela plan od rzeczywistości.
> Dokument zostaje CONSILIUM (żywy), bo adapter żyje; nie robimy z niego ACTA.

---

## ✅ CO Z PLANU ZREALIZOWANO — i JAK (zmierzone)

| Zamiar planu | Stan | Realizacja |
|---|---|---|
| Adapter `GlosImperium` (jedno wejście LLM) | ✅ | `imperium/cesarz/deepseek_glos.py` — `GlosImperium.zapytaj()` + `test_polaczenia()` |
| Oczy: sentyment newsów | ✅ **inną ścieżką** | `imperium/akwedukty/adaptery/news_llm.py` (nie `wszechoko.py`) — klasyfikuje wydźwięk nagłówków → JSON, z fallbackiem |
| Senat: debata Populares/Optimates przez LLM | 🔴 **NIE** | `meta_kora.py` poszła drogą **agentów ML/deterministycznych** (TrendAgent, SentimentAgent, MicrostructureAgent → MetaJudge/SuperJudge), nie debaty LLM. Wzorzec Populares/Optimates żyje TYLKO w `archiwum/kingdom_pixel_p1/meta_kora_debate.py` |
| Cesarz: decyzja LONG/SHORT/CZEKAJ przez LLM | 🔴 **NIE** | `titan_mind.py` to „Strategy Orchestrator & Scheduler" — nie używa DeepSeeka |

**Odbiorcy, których plan NIE przewidział, a którzy realnie używają `GlosImperium`:**
- 🔬 **NOTARIUS** (`imperium/biblioteki/notarius.py`) — zbiera pary `prompt → odpowiedź nauczyciela`
  do treningu lokalnego LLM (projekt TIRO). To dziś najważniejszy konsument.
- 📚 **Bibliotekarz/Hyginus** (`narzedzia/bibliotekarz.py`) — zwiad wiedzy: rozwijanie tematów
  i krytyka kompletności (temperatura 0.3).
- 🎓 **auto_lekcja** (`narzedzia/auto_lekcja.py`) — automatyczna lekcja po sesji.

> **Wniosek (Prawo I):** DeepSeek trafił do Imperium jako **narzędzie wiedzy i treningu**
> (newsy, zwiad, zbieranie par dla TIRO), a **nie** jako mózg decyzyjny Cesarza/Senatu.
> Ścieżka decyzyjna pozostała deterministyczna (Brama + neurony + Rada) — zgodnie z Prawem I
> („DeepSeek nie liczy matematyki"), ale też szerzej: nie decyduje o wejściach.

---

## 🎯 GDZIE DeepSeek pasuje w Imperium (pierwotny plan — do porównania z tabelą wyżej)

| Dzielnica | Moduł (plan) | Rola DeepSeek wg planu |
|-----------|-------|---------------|
| 👑 Cesarz | titan_mind.py | Czyta raport debaty → decyduje LONG/SHORT/CZEKAJ *(🔴 nie zrealizowane)* |
| 🏛️ Senat | meta_kora.py | Populares (LONG) i Optimates (SHORT) jako wywołania LLM *(🔴 inna droga)* |
| 👁️ Oczy | wszechoko.py | Analiza sentymentu newsów *(✅ ale przez `news_llm.py`)* |

> **Czego DeepSeek NIE robi:** nie liczy matematyki (to Brama/TA-Lib, Prawo I).
> DeepSeek tylko INTERPRETUJE tekst (newsy, tematy wiedzy).

---

## 🔌 Jak podłączyć (DeepSeek = kompatybilny z OpenAI)

Klucz trzymamy w zmiennej środowiskowej (NIGDY w kodzie, NIGDY na czacie):
```bash
# Windows PowerShell:
setx DEEPSEEK_API_KEY "twój-klucz"
```

Realny adapter ([`deepseek_glos.py`](../imperium/cesarz/deepseek_glos.py)) — model **v4**, nie legacy:

```python
# imperium/cesarz/deepseek_glos.py
import os
from openai import OpenAI   # DeepSeek kompatybilny z biblioteką OpenAI

class GlosImperium:
    """Most do DeepSeek. Jedyne wejście LLM w Imperium."""
    MODELE = {
        "szybki":    "deepseek-v4-flash",   # tani (~$0.14/1M in) — debata/zwiad/newsy
        "mysliciel": "deepseek-v4-pro",     # premium reasoning — decyzje
    }
    def __init__(self, model: str = "deepseek-v4-flash"):
        self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                             base_url="https://api.deepseek.com/v1")
        self.model = model

    def zapytaj(self, system_prompt: str, tresc: str, temperatura: float = 0.7) -> str: ...
    def test_polaczenia(self) -> bool: ...   # „powiedz cześć" → sprawdza klucz
```

> ⚠️ **Migracja V4 (zweryfikowane w kodzie 2026-07-17).** Poprzednia wersja podawała model
> `deepseek-chat` — ten (i `deepseek-reasoner`) **zostały wycofane 2026-07-24**. Nowe id:
> `deepseek-chat → deepseek-v4-flash`, `deepseek-reasoner → deepseek-v4-flash thinking /
> deepseek-v4-pro`. `base_url` bez zmian. Domyślny model adaptera to **`deepseek-v4-flash`**.

---

## 🏛️ Wzorzec debaty Senatu (Populares vs Optimates) — 🔴 NIEZREALIZOWANY

> **Ten szkic nigdy nie wszedł do `meta_kora.py`.** Senat poszedł drogą agentów ML
> (TrendAgent/SentimentAgent/MicrostructureAgent → MetaJudge/SuperJudge), nie debaty LLM.
> Wzorzec Populares/Optimates z LLM żyje wyłącznie w
> `archiwum/kingdom_pixel_p1/meta_kora_debate.py` — poniższe zostawiamy jako zapis intencji.

```python
# SZKIC (nie w kodzie meta_kora.py — patrz ostrzeżenie wyżej)
glos = GlosImperium()

# Frakcja LONG — Trybun Ludu (Populares)
arg_long = glos.zapytaj(
    system_prompt="Jesteś Trybunem Ludu. Szukasz WSZYSTKICH argumentów ZA LONG. "
                  "Bazuj TYLKO na podanych liczbach z Bramy. Zero zmyślania.",
    tresc=raport_wskaznikow_json,
)

# Frakcja SHORT — Pretor (Optimates)
arg_short = glos.zapytaj(
    system_prompt="Jesteś Pretorem. Szukasz WSZYSTKICH argumentów ZA SHORT. "
                  "Ostrożność, ochrona kapitału. Bazuj TYLKO na liczbach.",
    tresc=raport_wskaznikow_json,
)

# Cesarz — decyzja na podstawie OBU głosów
decyzja = glos.zapytaj(
    system_prompt="Jesteś Cesarzem. Widzisz oba stanowiska. Zważ je. "
                  "Decyzja: LONG / SHORT / CZEKAJ + krótkie uzasadnienie + pewność %.",
    tresc=f"ZA LONG:\n{arg_long}\n\nZA SHORT:\n{arg_short}",
)
```

---

## 📦 Frameworki z pliku (do rozważenia, nie teraz)

Plik DeepSeek polecał gotowe frameworki multi-agent. Nasza ocena dla Imperium:

| Framework | Werdykt dla Imperium |
|-----------|---------------------|
| **CrewAI** | ⭐ Najłatwiejszy multi-agent, wspiera DeepSeek przez LiteLLM. Dobry na Senat. |
| **LangGraph** | ⭐ Pełna kontrola, graf przepływu. Dobry gdy Imperium urośnie. |
| **AutoGen** | Rozmowy między agentami. Alternatywa dla Senatu. |
| OpenAlice | Jeden potężny agent z toolboxem. Wzorzec dla Cesarza. |
| Własny modularny szkielet | ⭐⭐ Plik dał gotową strukturę (core/llm/memory/tools/flows/channels). **Pasuje do naszej wizji "oryginalne narzędzia".** Ma nawet `flows/debate.py`! |

> **Decyzja otwarta:** zaczynamy od własnego prostego adaptera (powyżej).
> CrewAI/LangGraph dokładamy gdy debata urośnie. Nie komplikujemy na starcie (Prawo VII).

---

## ⚠️ Koszty i ostrożność

- DeepSeek jest tani, ale każde wywołanie to pieniądze. **Cache'ujemy** powtarzalne pytania.
- Na starcie: 1 cykl = ~3 wywołania (long, short, cesarz). Tanio.
- Monitoring zużycia: później (LangFuse darmowy tier wg pliku).

---

## ✅ NASTĘPNY KROK — ZREALIZOWANE (historia planu)

1. ✅ Komendant ustawia `DEEPSEEK_API_KEY` (weryfikacja: `GlosImperium.test_polaczenia()`)
2. ✅ `imperium/cesarz/deepseek_glos.py` istnieje (adapter V4)
3. ✅ Test połączenia wbudowany (`test_polaczenia()` → „powiedz cześć")
4. ✅ Wpięte — ale w **newsy/zwiad/NOTARIUS**, nie w cykl decyzyjny (patrz tabela realizacji)

**Otwarty postulat 🔵:** debata LLM Populares/Optimates w Senacie i decyzja LLM Cesarza —
gdyby kiedyś wracać, wzorzec czeka w `archiwum/kingdom_pixel_p1/meta_kora_debate.py`. Dziś
ścieżka decyzyjna jest w pełni deterministyczna (Brama + neurony + Rada Doradców), co jest
zgodne z kierunkiem (zero halucynacji LLM w wejściach — Prawo I).

---

*VITRUVIUSZ — "Cesarz nie liczy. Cesarz waży i decyduje."*
