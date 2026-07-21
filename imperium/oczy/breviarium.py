"""
📋 BREVIARIUM — Zwięzły Spis Sług Imperium (meldunek na otwarcie wachty).

August przekazywał Senatowi *breviarium totius imperii* — zwięzły rachunek zasobów państwa:
ile legionów, ile floty, ile w skarbcu. Tu tak samo: na starcie sesji Cezar widzi JEDNYM
spojrzeniem, czym Imperium dysponuje i w jakim stanie są jego słudzy.

POWÓD ISTNIENIA (zarzut Cezara 2026-07-21, potwierdzony pomiarem): hook startowy wołał 10
organów — audyt, PORTITOR, CENSOR sprzętu, CODEX, pamięć, Dziennik, kronikę, skan wad —
ale **ani jeden nie mówił, co robią HYGINUS i TIRO, ani z jakich modeli korzystamy.** Dwaj
słudzy z osobnymi rozkazami i osobnymi kosztami byli na otwarciu niewidzialni: stan kolejki
hipotez, plon czekający na sędziego, zebrane pary nauczyciela, modele na dysku — wszystko
trzeba było wygrzebywać ręcznie za każdym razem.

ŻELAZNA ZASADA (ta sama co SIGILLARIUM i CENSUS ORGANORUM): **liczby GENERUJEMY z żywego
stanu, nigdy nie przechowujemy.** Meldunek, który trzymałby własną treść, zgniłby jak każdy
ręcznie pisany dokument. Każdy wiersz niżej jest liczony w chwili wywołania.

CZEGO NIE ZMYŚLAMY (Prawo I): **modelu sesji Claude NIE DA SIĘ zmierzyć z hooka** — środowisko
niesie tylko `CLAUDE_EFFORT`, nigdy identyfikatora modelu (sprawdzone: w env jest
`CLAUDE_EFFORT`, `CLAUDE_AGENT_SDK_VERSION`, ale żadnego `*_MODEL`). Dlatego BREVIARIUM
drukuje to, co wie, i JAWNIE żąda od Architekta deklaracji reszty — zamiast wpisać
prawdopodobną nazwę, która zestarzeje się jak każda ręczna liczba.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent

KOLEJKA_HIPOTEZ = ROOT / "docs" / "KOLEJKA_HIPOTEZ_BIBLIOTEKARZ.jsonl"
PARY_TIRO = ROOT / "bibliotheca_ulpia" / "dane" / "tiro_pary_nauczyciela.jsonl"
KATALOG_TIRO = Path(os.getenv("TIRO_HOME", r"C:\TIRO"))


def _linie_jsonl(sciezka: Path) -> List[dict]:
    """Rekordy z pliku JSONL; uszkodzona linia jest pomijana, nie wywala meldunku."""
    if not sciezka.exists():
        return []
    rekordy = []
    for linia in sciezka.read_text(encoding="utf-8", errors="replace").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            rekordy.append(json.loads(linia))
        except json.JSONDecodeError:
            continue
    return rekordy


def stan_hyginusa() -> Dict[str, Any]:
    """
    Stan Bibliotekarza-Zwiadowcy: co zebrał, co czeka na sędziego, czym mówi.

    „Czeka na sędziego" liczymy jako cząstki ze statusem `ok` — plon, którego Opus jeszcze
    nie przerobił na decyzje. To jest DŁUG PRZEGLĄDU: kolejka rosnąca bez sędziego znaczy,
    że płacimy za zwiad, z którego nikt nie korzysta (Prawo XV — utrata potencjału).
    """
    rek = _linie_jsonl(KOLEJKA_HIPOTEZ)
    ok = [r for r in rek if r.get("status") == "ok"]
    znaczniki = [r["ts"] for r in rek if isinstance(r.get("ts"), (int, float))]
    zbadane = [r for r in ok if "probator" in r]
    podejrzane = [r for r in zbadane if not (r.get("probator") or {}).get("czysty", True)]

    model, profile = "?", []
    try:
        from imperium.cesarz import dispensator as dsp
        from imperium.cesarz.deepseek_glos import GlosImperium
        model = GlosImperium.__init__.__defaults__[0]        # domyślny model mowy
        profile = [f"{k}→{v['model'].replace('deepseek-', '')}"
                   f"{'/think-off' if v.get('thinking') else '/' + str(v.get('reasoning_effort', ''))}"
                   for k, v in dsp.PROFILE.items()]
    except Exception:                                        # noqa: BLE001 — meldunek nie może paść
        pass

    return {
        "czastek": len(rek),
        "czeka_na_sedziego": len(ok),
        "ostatni_zwiad": (datetime.fromtimestamp(max(znaczniki)).strftime("%Y-%m-%d %H:%M")
                          if znaczniki else "—"),
        "model": model,
        "profile_dispensatora": profile,
        "zbadane_probatorem": len(zbadane),
        "podejrzane": len(podejrzane),
        "dispensator_wpiety": _czy_dispensator_wpiety(),
    }


def _czy_dispensator_wpiety() -> bool:
    """Czy Hyginus FAKTYCZNIE woła DISPENSATORA (a nie tylko go ma w repo).

    Rozróżnienie istotne: organ istniejący, lecz niewołany, to martwy potencjał — dokładnie
    przypadek, przez który DISPENSATOR przeżył całą erę niezameldowany (cenzus 2026-07-20).
    """
    plik = ROOT / "narzedzia" / "bibliotekarz.py"
    if not plik.exists():
        return False
    return "dispensator" in plik.read_text(encoding="utf-8", errors="replace")


def stan_tiro() -> Dict[str, Any]:
    """
    Stan TIRO (rekruta — lokalny LLM): ile par nauczyciela zebrano, jakie modele na dysku.

    `tiro` to rzymski rekrut w szkoleniu — nazwa oddaje rolę: model, który dopiero się uczy
    od nauczyciela (DeepSeek), pod nadzorem Imperium.
    """
    pary = len(_linie_jsonl(PARY_TIRO))
    modele: List[str] = []
    katalog = KATALOG_TIRO / "modele"
    if katalog.exists():
        modele = sorted(p.name for p in katalog.glob("*.gguf"))
    klasa, zakres = "?", ""
    try:
        from imperium.oczy.censor_sprzetu import rekomendowany_tier
        tier = rekomendowany_tier()
        klasa, zakres = tier.get("klasa", "?"), tier.get("model_zakres", "")
    except Exception:                                        # noqa: BLE001 — meldunek nie może paść
        pass
    return {
        "pary_nauczyciela": pary,
        "modele": modele,
        "silnik": (KATALOG_TIRO / "silnik").exists(),
        "klasa_sprzetu": klasa,
        "zakres_modelu": zakres,
    }


def banner(model_architekta: Optional[str] = None) -> str:
    """
    Meldunek na otwarcie wachty. Zwięzły — ma się zmieścić obok 10 innych organów.

    `model_architekta` podaje wołający, JEŚLI wie. Hook nie wie (env nie niesie modelu),
    więc drukuje żądanie deklaracji — brak wiedzy nazwany wprost jest uczciwszy niż
    prawdopodobna nazwa udająca pomiar.
    """
    h, t = stan_hyginusa(), stan_tiro()
    wiersze = ["📋 BREVIARIUM — słudzy Imperium:"]

    dysp = "wpięty" if h["dispensator_wpiety"] else "🚨 NIEWPIĘTY (martwy potencjał)"
    wiersze.append(
        f"   📚 HYGINUS (Bibliotekarz-Zwiadowca): kolejka {h['czastek']} cząstek | "
        f"czeka na sędziego {h['czeka_na_sedziego']} | ostatni zwiad {h['ostatni_zwiad']}"
    )
    wiersze.append(f"      model: {h['model']} | DISPENSATOR: {dysp}")
    if h["profile_dispensatora"]:
        wiersze.append(f"      profile: {', '.join(h['profile_dispensatora'])}")
    if h["zbadane_probatorem"]:
        wiersze.append(f"      PROBATOR: zbadanych {h['zbadane_probatorem']}, "
                       f"podejrzanych {h['podejrzane']}")

    silnik = "llama.cpp ✓" if t["silnik"] else "🚨 brak silnika"
    modele = ", ".join(m.replace(".gguf", "") for m in t["modele"]) or "🚨 brak modeli"
    wiersze.append(
        f"   🎓 TIRO (rekrut — lokalny LLM): pary nauczyciela {t['pary_nauczyciela']} | "
        f"{silnik} | klasa {t['klasa_sprzetu']}"
    )
    wiersze.append(f"      modele na dysku: {modele}"
                   + (f" | sprzęt unosi: {t['zakres_modelu']}" if t["zakres_modelu"] else ""))

    if model_architekta:
        wiersze.append(f"   🏛️ VITRUVIUSZ (Architekt): {model_architekta}")
    else:
        wiersze.append(
            f"   🏛️ VITRUVIUSZ (Architekt): effort={os.getenv('CLAUDE_EFFORT', '?')}, "
            f"SDK {os.getenv('CLAUDE_AGENT_SDK_VERSION', '?')} — "
            "MODEL niemierzalny ze środowiska: Architekt deklaruje go sam na otwarciu"
        )
    return "\n".join(wiersze)


if __name__ == "__main__":                                   # pragma: no cover
    import sys
    print(banner(sys.argv[1] if len(sys.argv) > 1 else None))
