"""
🍂 Mądre Zapominanie — W10 Centrum Pamięci W-360 v10: LEARNED FORGETTING (UNIKAT)

ROZKAZ CEZARA (2026-06-29): „wszystko dawaj" — kolejne warstwy, autorskie moduły, wg zasad.

DEEP RESEARCH — GRANICA 2026 (ZPO): trzeci z trzech nierozwiązanych problemów pamięci
agentów (po reflection=W9 i contradiction=W9) to LEARNED FORGETTING:
  • Przegląd arXiv:2603.07670: „Forgetting is not a bug but a feature — obecne systemy
    radzą sobie z nim PRYMITYWNIE (twarde wygaszanie czasowe lub eviction po limicie);
    problem badawczy = NAUCZYĆ selektywnego zapominania."
  • SSGM (arXiv:2603.11768): zarządzanie ewoluującą pamięcią z bezpieczeństwem.

CO ROBIMY (autorski, deterministyczny, bez API): zapominanie NIE czasowe, lecz WARTOŚCIOWE.
Każde wspomnienie (lekcja W3 / wizja W4) dostaje WARTOŚĆ RETENCJI z wielu sygnałów:
    retencja = ważność × świeżość × łączność_w_grafie × (status otwarty?)
  • ważność: heurystyka słów-kluczy (jak scoring GA — bug/utrata/prawo ważą więcej)
  • świeżość: zanik warstwowy (FinMem) — ważne zanikają wolniej
  • łączność: stopień węzła w Grafie Pamięci (W8) — wspomnienie-HUB jest cenne (wiele połączeń)
  • status: otwarte plany (POMYSŁ/PLANOWANE) chronione (nie zapominaj niezałatwionego)

Niska retencja + wiek → KANDYDAT do schłodzenia (nie usunięcia!). W10 decyduje CO,
Kustosz (W7) to KOMPRESUJE do zimnej warstwy (.md.gz, wciąż przeszukiwalnej → zero blindness).

ZASADA ANTY-UTRWALANIA (jak W9, wprost z granicy 2026): NIGDY nie kasuje automatycznie —
tylko PROPONUJE schłodzenie/archiwizację. Cezar dysponuje (Prawo XVIII). To „safe forgetting":
nic nie ginie (git + zimna warstwa), tylko schodzi z gorącego kontekstu. Odwracalne.

Pod zarządem Kustosza (W7); używa wartości z Grafu (W8) i scoringu (Centrum W3).

CLI:
  python -m imperium.biblioteki.zapominanie raport
  python -m imperium.biblioteki.zapominanie kandydaci --prog 0.15 --dni 30
"""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, Any, List, Optional

_MIN_DL = 4


def _stopien_w_grafie() -> Dict[str, int]:
    """Mapa encja→stopień (łączność) z Grafu Pamięci W8. Pusto gdy brak grafu."""
    try:
        from imperium.biblioteki import graf_pamieci as _gp
        graf = _gp._wczytaj()
        st: Dict[str, int] = {}
        for kr in graf.get("krawedzie", []):
            st[kr["a"]] = st.get(kr["a"], 0) + kr["waga"]
            st[kr["b"]] = st.get(kr["b"], 0) + kr["waga"]
        return st
    except Exception:
        return {}


def _laczność_wpisu(tekst: str, stopnie: Dict[str, int]) -> int:
    """Suma stopni encji wpisu — jak mocno wpis jest 'wpleciony' w sieć pamięci."""
    if not stopnie:
        return 0
    enc = set(re.findall(r"[a-ząćęłńóśźż0-9_\-]{%d,}" % _MIN_DL, tekst.lower()))
    return sum(stopnie.get(e, 0) for e in enc)


def wartosc_retencji(wpis: Dict[str, Any], stopnie: Optional[Dict[str, int]] = None) -> float:
    """
    Deterministyczna wartość retencji wspomnienia w [0,1+]. Wyższa = trzymaj w gorącym.
    Łączy: ważność (słowa-klucze) × świeżość (zanik warstwowy) × bonus łączności w grafie.
    Otwarte plany (status POMYSŁ/PLANOWANE) dostają mnożnik ochronny.
    """
    from imperium.biblioteki.centrum_pamieci import _importance, _recency

    tytul = wpis.get("tytul", "")
    tresc = wpis.get("tresc", "")
    waznosc = _importance(tytul, tresc)              # 0.3–1.0
    swiezosc = _recency(wpis.get("data", ""), waznosc)  # 0–1, zanik wg ważności

    if stopnie is None:
        stopnie = _stopien_w_grafie()
    lacz = _laczność_wpisu(tytul + " " + tresc, stopnie)
    # bonus łączności: log-skala, nasycenie ~+0.3 dla silnych hubów
    import math
    bonus = min(0.3, 0.05 * math.log1p(lacz)) if lacz > 0 else 0.0

    retencja = waznosc * swiezosc + bonus

    status = (wpis.get("status", "") or "").upper()
    if status in ("POMYSŁ", "POMYSL", "PLANOWANE"):
        retencja = max(retencja, 0.5)   # nie zapominaj niezałatwionych planów

    return retencja


def _zrodla() -> List[Dict[str, Any]]:
    """Wspomnienia podlegające ocenie retencji: lekcje W3 + wizje W4."""
    wpisy: List[Dict[str, Any]] = []
    try:
        from imperium.biblioteki import pamiec_sesji as _ps
        for lek in _ps.lekcje(plik=_ps.DOMYSLNY_PLIK):
            wpisy.append({"zrodlo": "lekcje", "tytul": lek.get("tytul", ""),
                          "tresc": lek.get("tresc", ""), "data": lek.get("data", ""),
                          "status": ""})
    except Exception:
        pass
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        for w in _rw.wszystkie():
            wpisy.append({"zrodlo": "wizje", "tytul": w.get("tytul", ""),
                          "tresc": w.get("tresc", ""), "data": w.get("data", ""),
                          "status": w.get("status", "")})
    except Exception:
        pass
    return wpisy


def kandydaci_do_zapomnienia(prog: float = 0.15, dni: int = 30,
                             limit: int = 30) -> List[Dict[str, Any]]:
    """
    Wspomnienia o niskiej retencji (< prog) i wieku ≥ dni → kandydaci do SCHŁODZENIA.
    TYLKO propozycja (anti-utrwalanie): Cezar/Kustosz decyduje. Nigdy nie kasuje.
    """
    stopnie = _stopien_w_grafie()
    dzis = date.today().toordinal()
    wyniki = []
    for w in _zrodla():
        try:
            wiek = dzis - date.fromisoformat(w["data"]).toordinal()
        except (ValueError, TypeError):
            continue
        if wiek < dni:
            continue
        r = wartosc_retencji(w, stopnie)
        if r < prog:
            wyniki.append({"retencja": round(r, 3), "wiek_dni": wiek,
                           "zrodlo": w["zrodlo"], "tytul": w["tytul"]})
    wyniki.sort(key=lambda x: x["retencja"])   # najsłabsze najpierw
    return wyniki[:limit]


def raport(prog: float = 0.15, dni: int = 30) -> Dict[str, Any]:
    kand = kandydaci_do_zapomnienia(prog=prog, dni=dni)
    wszystkie = _zrodla()
    return {"ocenionych": len(wszystkie), "kandydatow": len(kand), "kandydaci": kand}


def raport_startowy(prog: float = 0.15, dni: int = 30) -> str:
    """Linia do startu — tylko gdy są kandydaci do schłodzenia."""
    kand = kandydaci_do_zapomnienia(prog=prog, dni=dni)
    if not kand:
        return ""
    return (f"   🍂 Zapominanie (W10): {len(kand)} wspomnień niskiej wartości "
            f"do schłodzenia (przejrzyj: zapominanie kandydaci)")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Mądre Zapominanie — W10 learned forgetting (W-360 v10)")
    sub = p.add_subparsers(dest="cmd")
    pr = sub.add_parser("raport", help="Podsumowanie retencji")
    pr.add_argument("--prog", type=float, default=0.15)
    pr.add_argument("--dni", type=int, default=30)
    pk = sub.add_parser("kandydaci", help="Kandydaci do schłodzenia")
    pk.add_argument("--prog", type=float, default=0.15)
    pk.add_argument("--dni", type=int, default=30)
    args = p.parse_args()

    if args.cmd == "kandydaci":
        for k in kandydaci_do_zapomnienia(prog=args.prog, dni=args.dni):
            print(f"  🍂 retencja={k['retencja']} wiek={k['wiek_dni']}d [{k['zrodlo']}] {k['tytul']}")
    else:
        r = raport(prog=args.prog, dni=args.dni)
        print(f"Ocenionych: {r['ocenionych']} | kandydatów do schłodzenia: {r['kandydatow']}")
        for k in r["kandydaci"][:10]:
            print(f"  🍂 {k['retencja']} ({k['wiek_dni']}d) [{k['zrodlo']}] {k['tytul']}")
