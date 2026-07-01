"""
🔍 Pamięć Proweniencji — W13 Centrum Pamięci W-360 v13 (origin trail — UNIKAT)

ROZKAZ CEZARA (2026-06-29): „dawaj" — kolejna warstwa pamięci.

DEEP RESEARCH (ZPO): „From Agent Traces to Trust: Evidence Tracing and Execution
Provenance in LLM Agents" (https://arxiv.org/html/2606.04990) — pamięć agenta wprowadza
artefakty (lekcje, wizje, decyzje), których klasyczna obserwowalność nie chwyta. Potrzeba:
PROVENANCE-AWARE RETRIEVAL + temporal credit assignment — wiedzieć SKĄD wzięła się
informacja, kiedy weszła i jak wędrowała. Bez tego agent nie odróżnia faktu świeżo
wymyślonego od ugruntowanego wieloma sesjami.

CO ROBI (deterministycznie, bez API): dla dowolnego pojęcia/encji buduje ŚLAD POCHODZENIA —
listę wystąpień w czasie przez wszystkie warstwy (kronika W3b + dziennik W6 + lekcje W3
+ wizje W4), z datą i sesją. Pierwsze wystąpienie = GENEZA („tu się to narodziło"),
liczba sesji = ugruntowanie („ile razy wracało"). To „temporal credit assignment".

ODPOWIADA NA: „skąd to wiemy?", „kiedy to się pojawiło?", „czy to świeży pomysł czy
ugruntowana wiedza?". Różne od Grafu (W8=połączenia) i Katalogu (W7=indeks tematów):
proweniencja to OŚ CZASU JEDNEGO pojęcia z atrybucją źródła.

Bez własnego pliku (czyta z istniejących warstw — Prawo XVI, zero redundancji danych).
Pod zarządem Kustosza (W7).

CLI:
  python -m imperium.biblioteki.pamiec_proweniencji skad "numba"
  python -m imperium.biblioteki.pamiec_proweniencji geneza "kustosz"
"""

from __future__ import annotations

import re
from typing import Dict, Any, List, Optional


def _slowa(zapytanie: str) -> List[str]:
    # min. 2 znaki (spójne z kronika/dziennik) — pozwala śledzić ID warstw jak "W3", "W8".
    return [s for s in re.findall(r"\w+", zapytanie.lower()) if len(s) >= 2]


def _trafienie(tekst: str, slowa: List[str]) -> bool:
    low = tekst.lower()
    return any(s in low for s in slowa)


def slad(encja: str, limit: int = 40) -> List[Dict[str, Any]]:
    """
    Ślad pochodzenia encji: wszystkie wystąpienia (data, sesja, warstwa, fragment),
    posortowane chronologicznie (najstarsze = geneza). Czyta wszystkie warstwy.
    """
    slowa = _slowa(encja)
    if not slowa:
        return []
    wyst: List[Dict[str, Any]] = []

    # W6 Dziennik (data + sesja + co/decyzje)
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        for w in _dn.wszystkie():
            for c in w.get("co", []) + w.get("decyzje", []):
                if _trafienie(c, slowa):
                    wyst.append({"data": w.get("data", ""), "sesja": w.get("sesja", ""),
                                 "warstwa": "dziennik", "fragment": c[:140]})
    except Exception:
        pass

    # W4 wizje
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        for w in _rw.wszystkie():
            tekst = f"{w.get('tytul','')} {w.get('tresc','')}"
            if _trafienie(tekst, slowa):
                wyst.append({"data": w.get("data", ""), "sesja": "", "warstwa": "wizje",
                             "fragment": w.get("tytul", "")[:140]})
    except Exception:
        pass

    # W3 lekcje
    try:
        from imperium.biblioteki import pamiec_sesji as _ps
        for lek in _ps.lekcje(plik=_ps.DOMYSLNY_PLIK):
            tekst = f"{lek.get('tytul','')} {lek.get('tresc','')}"
            if _trafienie(tekst, slowa):
                wyst.append({"data": lek.get("data", ""), "sesja": "", "warstwa": "lekcje",
                             "fragment": lek.get("tytul", "")[:140]})
    except Exception:
        pass

    # W3b kronika (data + sesja + fragment) — najbogatsze źródło chronologii.
    # limit szeroki: pełny ślad przed globalnym sortem chronologicznym (inaczej geneza
    # mogłaby zwrócić trafienie rankowane/ucięte, nie prawdziwy początek).
    try:
        from imperium.biblioteki import kronika_czatu as _kc
        for t in _kc.szukaj(encja, limit=max(limit, 500)):
            wyst.append({"data": t.get("data", ""), "sesja": t.get("sesja", "")[:8],
                         "warstwa": "kronika", "fragment": t.get("fragment", "")[:140]})
    except Exception:
        pass

    wyst.sort(key=lambda x: x["data"] or "9999")
    return wyst[:limit]


def geneza(encja: str) -> Optional[Dict[str, Any]]:
    """Pierwsze (najstarsze) wystąpienie encji — „tu się to narodziło"."""
    s = slad(encja, limit=1)
    return s[0] if s else None


def raport(encja: str) -> Dict[str, Any]:
    """Podsumowanie proweniencji: geneza + ugruntowanie (ile sesji/warstw)."""
    s = slad(encja)
    sesje = {w["sesja"] for w in s if w["sesja"]}
    warstwy = {w["warstwa"] for w in s}
    return {
        "encja": encja,
        "geneza": s[0] if s else None,
        "wystapien": len(s),
        "sesje_unikalne": len(sesje),
        "warstwy": sorted(warstwy),
        "slad": s,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Pamięć Proweniencji — W13 origin trail (W-360 v13)")
    sub = p.add_subparsers(dest="cmd")
    ps = sub.add_parser("skad", help="Pełny ślad pochodzenia")
    ps.add_argument("encja")
    pg = sub.add_parser("geneza", help="Pierwsze wystąpienie")
    pg.add_argument("encja")
    args = p.parse_args()

    if args.cmd == "geneza":
        g = geneza(args.encja)
        if g:
            print(f"🔍 Geneza '{args.encja}': [{g['data']}] {g['warstwa']} — {g['fragment']}")
        else:
            print(f"(brak śladu dla '{args.encja}')")
    elif args.cmd == "skad":
        r = raport(args.encja)
        g = r["geneza"]
        print(f"🔍 '{args.encja}': {r['wystapien']} wystąpień, {r['sesje_unikalne']} sesji, "
              f"warstwy {r['warstwy']}")
        if g:
            print(f"   GENEZA: [{g['data']}] {g['warstwa']} — {g['fragment']}")
        for w in r["slad"][:8]:
            print(f"   [{w['data']}] {w['warstwa']}: {w['fragment']}")
    else:
        p.print_help()
