"""
🎯 Pamięć Robocza — W12 Centrum Pamięci W-360 v12 (taksonomia CoALA — domknięcie)

ROZKAZ CEZARA (2026-06-29): „jeszcze kilka warstw pamięci."

DEEP RESEARCH (ZPO): CoALA (https://arxiv.org/abs/2309.02427) — czwarty, brakujący typ
pamięci to PAMIĘĆ ROBOCZA (working memory): „aktywna informacja bieżącego cyklu decyzyjnego
— aktywne CELE przeniesione z poprzedniego cyklu". To różni się od pamięci długoterminowej:
robocza = MAŁA, OSTRA, TU-I-TERAZ; mówi „nad czym pracujemy WŁAŚNIE TERAZ".

Po W11 (proceduralna) to DOMYKA pełną czwórkę CoALA:
  robocza (W12) + epizodyczna (kronika W3b) + semantyczna (lekcje W3 + RAG W2) + proceduralna (W11).
Imperium ma teraz KOMPLETNĄ taksonomię poznawczą pamięci agenta — czego nie ma żaden konkurent.

CO ROBI: składa „ognisko uwagi" sesji z istniejących warstw (nie duplikuje — Prawo XVI):
  • AKTYWNY CEL = ostatni „następny krok" z Dziennika W6 (co miało być zrobione dalej)
  • PILNE = sprzeczności W9 + przedawnienia (jeśli są) — co woła o decyzję
  • To jest „working memory" wstrzykiwana na starcie: jednym rzutem oka wiesz GDZIE WEJŚĆ.

Różnica od Dziennika (W6, epizodyczny): Dziennik = CAŁA oś (cały łuk projektu). Robocza =
JEDEN aktywny cel (ostrze bieżącego cyklu). Dwa różne typy CoALA, nie redundancja.

Deterministyczna, bez API, bez własnego pliku (czyta z W6/W9) → zero kosztu utrzymania.

CLI:
  python -m imperium.biblioteki.pamiec_robocza cel       # aktywny cel
  python -m imperium.biblioteki.pamiec_robocza ognisko   # pełne ognisko uwagi
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional


def aktywny_cel() -> Optional[str]:
    """Ostatni 'następny krok' z Dziennika W6 — co miało być zrobione w tym cyklu."""
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        ost = _dn.ostatni_wpis()
        if ost and ost.get("nastepny"):
            return ost["nastepny"]
    except Exception:
        pass
    return None


def pilne() -> List[str]:
    """Sygnały wołające o decyzję: sprzeczności (W9) + przedawnienia."""
    sygnaly: List[str] = []
    try:
        from imperium.biblioteki import refleksja_pamieci as _rp
        r = _rp.raport()
        for s in r.get("sprzeczne", [])[:3]:
            sygnaly.append(f"⚠️ sprzeczność: {', '.join(s['temat'])}")
        n_prz = len(r.get("przedawnione", []))
        if n_prz:
            sygnaly.append(f"⏳ {n_prz} pomysłów wisi (zdecyduj)")
    except Exception:
        pass
    return sygnaly


def ognisko() -> Dict[str, Any]:
    """Working memory: aktywny cel + pilne sygnały (ostrze bieżącego cyklu)."""
    return {"aktywny_cel": aktywny_cel(), "pilne": pilne()}


def raport_startowy() -> str:
    """Linia 'ognisko uwagi' do startu — tylko gdy jest aktywny cel."""
    cel = aktywny_cel()
    if not cel:
        return ""
    linia = f"   🎯 Aktywny cel (W12): {cel}"
    p = pilne()
    if p:
        linia += f"\n   🎯 Pilne: {' | '.join(p)}"
    return linia


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Pamięć Robocza — W12 CoALA working memory (W-360 v12)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("cel", help="Aktywny cel")
    sub.add_parser("ognisko", help="Pełne ognisko uwagi")
    args = p.parse_args()

    if args.cmd == "ognisko":
        o = ognisko()
        print(f"🎯 Aktywny cel: {o['aktywny_cel'] or '(brak)'}")
        for s in o["pilne"]:
            print(f"   {s}")
    else:
        print(aktywny_cel() or "(brak aktywnego celu — dopisz 'następny' w Dzienniku)")
