# 🧠 PLAN: DeepSeek API jako mózg Cesarza i Senatu

> **Źródło:** rozmowa DeepSeek o budowie multi-bota (`archiwum/DeepSeek_API_multibot_oryginal.md`)
> **Po co:** Komendant ma klucz DeepSeek API. To tani, szybki LLM (~10× taniej od GPT-4).
> Podłączamy go jako "głos" agentów — Cesarz decyduje, Senat debatuje.
>
> **Sprzęt:** Fujitsu 8GB RAM. Dlatego ciężka praca (LLM) idzie przez API, nie lokalnie.

---

## 🎯 GDZIE DeepSeek pasuje w Imperium

| Dzielnica | Moduł | Rola DeepSeek |
|-----------|-------|---------------|
| 👑 Cesarz | titan_mind.py | Czyta raport debaty → decyduje LONG/SHORT/CZEKAJ + uzasadnienie |
| 🏛️ Senat | meta_kora.py | Agent Populares (LONG) i Optimates (SHORT) — każdy to wywołanie LLM |
| 👁️ Oczy | wszechoko.py | Analiza sentymentu newsów, odszumianie kanałów |

> **Czego DeepSeek NIE robi:** nie liczy matematyki (to Brama/TA-Lib, Prawo I).
> DeepSeek tylko INTERPRETUJE gotowe liczby i debatuje.

---

## 🔌 Jak podłączyć (DeepSeek = kompatybilny z OpenAI)

Klucz trzymamy w zmiennej środowiskowej (NIGDY w kodzie, NIGDY na czacie):
```bash
# Windows PowerShell:
setx DEEPSEEK_API_KEY "twój-klucz"
```

Kod adaptera (wzorzec z pliku DeepSeek, dostosowany do Imperium):
```python
# imperium/cesarz/deepseek_glos.py
import os
from openai import OpenAI   # DeepSeek używa biblioteki OpenAI!

class GlosImperium:
    """Most do DeepSeek. Jedyne wejście LLM w Imperium."""
    def __init__(self, model="deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        self.model = model

    def zapytaj(self, system_prompt: str, tresc: str, temperatura=0.7) -> str:
        odp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": tresc},
            ],
            temperature=temperatura,
        )
        return odp.choices[0].message.content
```

---

## 🏛️ Wzorzec debaty Senatu (Populares vs Optimates)

```python
# imperium/senat/meta_kora.py (szkic)
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

## ✅ NASTĘPNY KROK (gdy ruszamy z DeepSeek)

1. Komendant ustawia `DEEPSEEK_API_KEY` na swoim PC
2. Tworzymy `imperium/cesarz/deepseek_glos.py` (kod wyżej)
3. Test: jedno pytanie "powiedz cześć po polsku" → sprawdzamy że klucz działa
4. Dopiero potem wpinamy w cykl

---

*VITRUVIUSZ — "Cesarz nie liczy. Cesarz waży i decyduje."*
