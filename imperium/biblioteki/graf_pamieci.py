"""
🕸️ Graf Pamięci — W8 Centrum Pamięci W-360 v8: POŁĄCZENIA NEURONÓW (UNIKAT IMPERIUM)

ROZKAZ CEZARA (2026-06-28): „wielopłaszczyznowe zapamiętywanie POŁĄCZEŃ NEURONÓW —
żeby każde słowo, każda zmiana, każdy punkt łączyły się ze wszystkim. Petarda godna
poza streszczeniem konkurentów, którzy będą tylko marzyć o takim poziomie pamięci."

KONTEKST SOTA 2026 (ZPO — pełne źródła, przegląd globalny Azja/USA/EU):
  • Zep / Graphiti — Temporal Knowledge Graph dla pamięci agenta (USA),
    https://arxiv.org/abs/2501.13956 — fakty jako węzły z OKNEM WAŻNOŚCI (validity window),
    relacje jako krawędzie; bije MemGPT na Deep Memory Retrieval. Klucz: „true now" vs
    „true last quarter" → koniec sprzecznego/nieaktualnego kontekstu.
  • A-Mem — pamięć jako połączone „notatki" z metadanymi, ciągła reorganizacja.
  • MemOS (Tsinghua/Chiny) — pamięć jako zasób systemu operacyjnego (memory OS).
  • Krytyka uczciwa (ZPO): „Does Memory Need Graphs?" https://arxiv.org/pdf/2601.01280
    → graf NIE jest złotym młotkiem; pomaga w pytaniach RELACYJNYCH („co łączy X z Y"),
    nie zastępuje retrievalu. Dlatego graf to DODATKOWA soczewka (W8), nie zamiennik W1-W7.

CO ROBIMY (deterministycznie, bez API — Prawo I, działa chmura i lokal):
  Budujemy graf z DZIENNIKA (W6, esencja sesji) + wizji (W4) + lekcji (W3):
    • WĘZŁY (neurony pamięci): znaczące encje/tematy (Numba, Kustosz, kompresja, Viterbi…)
    • KRAWĘDZIE (synapsy): współwystąpienie w jednym wpisie/sesji — co pojawia się razem,
      jest połączone; waga = liczba współwystąpień.
    • CZAS (validity, jak Zep): każdy węzeł/krawędź ma pierwszy_raz i ostatni_raz.

ZAPYTANIA:
  • polaczenia("Numba")  → z czym Numba jest połączona (Viterbi, JIT, wydajność…) + waga + kiedy
  • centralne(top)       → węzły-HUBY (najbardziej połączone „neurony" projektu)
  • sciezka("Numba","pamięć") → jak dwa pojęcia są ze sobą powiązane (BFS najkrótsza ścieżka)

Graf persystowany do JSON (git → bezgraniczny, przeżywa chmura↔lokal). Pod zarządem
Kustosza (W7). Razem z reżimową (W3/4), środowiskową (W5), dziennikiem (W6) i kompresją
(W7) — tej kombinacji 8 warstw nie ma żaden konkurent.

CLI:
  python -m imperium.biblioteki.graf_pamieci buduj
  python -m imperium.biblioteki.graf_pamieci polacz Numba
  python -m imperium.biblioteki.graf_pamieci centralne
  python -m imperium.biblioteki.graf_pamieci sciezka Numba pamięć
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
GRAF_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "graf_pamieci.json"

# Encje znaczące: terminy ≥4 znaki, nie-szum. Zachowujemy oryginalną pisownię kluczy
# technicznych (Numba, Kustosz, GARCH…) przez kanonizację małymi literami w indeksie.
_STOP = {
    "the", "and", "dla", "jest", "się", "nie", "tak", "czy", "ale", "lub", "oraz",
    "to", "co", "na", "do", "od", "za", "po", "ze", "we", "że", "już", "jak", "bez",
    "claude", "cezar", "sesja", "który", "która", "które", "tylko", "może", "być",
    "next", "następny", "raz", "teraz", "wszystko", "coś", "było", "this", "with",
    "from", "gdy", "ich", "też", "out", "are", "nasz", "naszej",
    # częste czasowniki/wypełniacze (szum w grafie współwystąpień)
    "była", "był", "były", "być", "omawiana", "rozważyć", "brak", "zmierzone",
    "przez", "oraz", "przed", "każdy", "każda", "każde", "więcej", "mniej",
    "robi", "robić", "zrobione", "wciąż", "jeszcze", "całość", "całą", "nową",
    "tej", "tego", "temu", "przy", "która", "także", "wtedy", "potem",
}
_MIN_DL = 4


def _encje(tekst: str) -> List[str]:
    """Kanoniczne encje (lowercase) z tekstu — znaczące terminy, bez szumu."""
    sur = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9_\-]{%d,}" % _MIN_DL, tekst)
    out = []
    for w in sur:
        wl = w.lower()
        if wl in _STOP or wl.isdigit():
            continue
        out.append(wl)
    # unikalne w obrębie wpisu (współwystąpienie liczymy raz na wpis)
    return sorted(set(out))


# ─── BUDOWA GRAFU ──────────────────────────────────────────────────────────────

def _zrodla_wpisow() -> List[Tuple[str, str]]:
    """
    Zbiera (data, tekst) z warstw esencji: Dziennik (W6) + wizje (W4) + lekcje (W3).
    To skondensowane źródła — graf łączy POJĘCIA, nie surowy dialog (tańszy, ostrzejszy).
    """
    wpisy: List[Tuple[str, str]] = []
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        for w in _dn.wszystkie():
            tekst = " ".join(w.get("co", []) + w.get("decyzje", []) + [w.get("nastepny", "")])
            wpisy.append((w.get("data", ""), tekst))
    except Exception:
        pass
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        for w in _rw.wszystkie():
            wpisy.append((w.get("data", ""), f"{w.get('tytul','')} {w.get('tresc','')}"))
    except Exception:
        pass
    try:
        from imperium.biblioteki import pamiec_sesji as _ps
        for lek in _ps.lekcje(plik=_ps.DOMYSLNY_PLIK):
            wpisy.append((lek.get("data", ""), f"{lek.get('tytul','')} {lek.get('tresc','')}"))
    except Exception:
        pass
    return wpisy


def zbuduj_graf(plik: Path = GRAF_PLIK, min_waga: int = 1) -> Dict[str, Any]:
    """
    Buduje temporalny graf współwystąpień. Węzły = encje (z czasem first/last + licznością),
    krawędzie = pary współwystępujące w tym samym wpisie (waga = liczba współwystąpień,
    + okno czasowe). Persystuje do JSON. Zwraca {"wezly": N, "krawedzie": M, ...}.
    """
    wezly: Dict[str, Dict[str, Any]] = {}
    krawedzie: Dict[Tuple[str, str], Dict[str, Any]] = defaultdict(
        lambda: {"waga": 0, "pierwszy": "", "ostatni": ""})

    for data, tekst in _zrodla_wpisow():
        enc = _encje(tekst)
        for e in enc:
            n = wezly.setdefault(e, {"liczba": 0, "pierwszy": data or "", "ostatni": data or ""})
            n["liczba"] += 1
            if data:
                if not n["pierwszy"] or data < n["pierwszy"]:
                    n["pierwszy"] = data
                if data > n["ostatni"]:
                    n["ostatni"] = data
        # krawędzie współwystąpienia (pary w obrębie wpisu)
        for i in range(len(enc)):
            for j in range(i + 1, len(enc)):
                klucz = (enc[i], enc[j])
                kr = krawedzie[klucz]
                kr["waga"] += 1
                if data:
                    if not kr["pierwszy"] or data < kr["pierwszy"]:
                        kr["pierwszy"] = data
                    if data > kr["ostatni"]:
                        kr["ostatni"] = data

    kraw_lista = [
        {"a": a, "b": b, "waga": v["waga"], "pierwszy": v["pierwszy"], "ostatni": v["ostatni"]}
        for (a, b), v in krawedzie.items() if v["waga"] >= min_waga
    ]
    # Filtruj węzły do tych obecnych w ZACHOWANYCH krawędziach — inaczej przy min_waga>1
    # graf trzymałby izolowane węzły-szum niequeryowalne przez polaczenia/centralne.
    aktywne = {kr["a"] for kr in kraw_lista} | {kr["b"] for kr in kraw_lista}
    wezly = {e: dane for e, dane in wezly.items() if e in aktywne}
    graf = {
        "wezly": wezly,
        "krawedzie": kraw_lista,
        "n_wezlow": len(wezly),
        "n_krawedzi": len(kraw_lista),
    }
    plik.parent.mkdir(parents=True, exist_ok=True)
    plik.write_text(json.dumps(graf, ensure_ascii=False, indent=1), encoding="utf-8")
    return graf


def _wczytaj(plik: Path = GRAF_PLIK) -> Dict[str, Any]:
    if not plik.exists():
        return {"wezly": {}, "krawedzie": [], "n_wezlow": 0, "n_krawedzi": 0}
    try:
        return json.loads(plik.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError):
        return {"wezly": {}, "krawedzie": [], "n_wezlow": 0, "n_krawedzi": 0}


# ─── ZAPYTANIA GRAFU ───────────────────────────────────────────────────────────

def polaczenia(encja: str, limit: int = 10, plik: Path = GRAF_PLIK) -> List[Dict[str, Any]]:
    """Z czym dana encja jest połączona (sąsiedzi wg wagi) + okno czasowe."""
    e = encja.lower()
    graf = _wczytaj(plik)
    sasiedzi = []
    for kr in graf["krawedzie"]:
        if kr["a"] == e:
            sasiedzi.append({"encja": kr["b"], "waga": kr["waga"], "od": kr["pierwszy"], "do": kr["ostatni"]})
        elif kr["b"] == e:
            sasiedzi.append({"encja": kr["a"], "waga": kr["waga"], "od": kr["pierwszy"], "do": kr["ostatni"]})
    sasiedzi.sort(key=lambda x: x["waga"], reverse=True)
    return sasiedzi[:limit]


def centralne(top: int = 10, plik: Path = GRAF_PLIK) -> List[Dict[str, Any]]:
    """Węzły-HUBY: najbardziej połączone neurony pamięci (stopień ważony)."""
    graf = _wczytaj(plik)
    stopien: Dict[str, int] = defaultdict(int)
    for kr in graf["krawedzie"]:
        stopien[kr["a"]] += kr["waga"]
        stopien[kr["b"]] += kr["waga"]
    ranking = sorted(stopien.items(), key=lambda x: x[1], reverse=True)[:top]
    return [{"encja": e, "stopien": s, "liczba": graf["wezly"].get(e, {}).get("liczba", 0)}
            for e, s in ranking]


def sciezka(a: str, b: str, plik: Path = GRAF_PLIK) -> List[str]:
    """Najkrótsza ścieżka (BFS) między dwoma pojęciami — JAK są powiązane. [] gdy brak."""
    a, b = a.lower(), b.lower()
    graf = _wczytaj(plik)
    sasiedztwo: Dict[str, set] = defaultdict(set)
    for kr in graf["krawedzie"]:
        sasiedztwo[kr["a"]].add(kr["b"])
        sasiedztwo[kr["b"]].add(kr["a"])
    if a not in sasiedztwo or b not in sasiedztwo:
        return []
    from collections import deque
    kolejka = deque([[a]])
    odwiedzone = {a}
    while kolejka:
        sciezka_akt = kolejka.popleft()
        ostatni = sciezka_akt[-1]
        if ostatni == b:
            return sciezka_akt
        for sas in sasiedztwo[ostatni]:
            if sas not in odwiedzone:
                odwiedzone.add(sas)
                kolejka.append(sciezka_akt + [sas])
    return []


def raport_startowy(plik: Path = GRAF_PLIK) -> str:
    """Zwięzła linia do podsumowania startowego: rozmiar grafu + top huby."""
    graf = _wczytaj(plik)
    if graf["n_wezlow"] == 0:
        return "   🕸️ Graf pamięci (W8): pusty (zbuduj: graf_pamieci buduj)"
    huby = centralne(5, plik)
    nazwy = ", ".join(h["encja"] for h in huby)
    return (f"   🕸️ Graf pamięci (W8): {graf['n_wezlow']} neuronów, "
            f"{graf['n_krawedzi']} połączeń | huby: {nazwy}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Graf Pamięci — W8 połączenia neuronów (W-360 v8)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("buduj", help="Zbuduj/odśwież graf z warstw pamięci")
    pp = sub.add_parser("polacz", help="Z czym połączona jest encja")
    pp.add_argument("encja")
    pc = sub.add_parser("centralne", help="Węzły-huby")
    pc.add_argument("--top", type=int, default=10)
    psc = sub.add_parser("sciezka", help="Ścieżka między dwoma pojęciami")
    psc.add_argument("a")
    psc.add_argument("b")
    args = p.parse_args()

    if args.cmd == "buduj":
        # min_waga=2: tnie szum (jednorazowe współwystąpienia) — graf ostrzejszy i ~20× mniejszy
        # (Prawo XVI: trzymamy zmierzone-powtarzalne powiązania, nie przypadkowe). Konsolidacja v13.
        g = zbuduj_graf(min_waga=2)
        print(f"✅ Graf: {g['n_wezlow']} neuronów, {g['n_krawedzi']} połączeń (synaps, waga≥2)")
    elif args.cmd == "polacz":
        for s in polaczenia(args.encja):
            print(f"  {args.encja} ↔ {s['encja']} (waga {s['waga']}, {s['od']}…{s['do']})")
    elif args.cmd == "centralne":
        for h in centralne(args.top):
            print(f"  {h['encja']}: stopień {h['stopien']} (wystąpień {h['liczba']})")
    elif args.cmd == "sciezka":
        s = sciezka(args.a, args.b)
        print(" → ".join(s) if s else "(brak ścieżki — pojęcia niepołączone)")
    else:
        p.print_help()
