"""
🪞 Refleksja Pamięci — W9 Centrum Pamięci W-360 v9: SPRZECZNOŚCI + PRZEDAWNIENIE (UNIKAT)

ROZKAZ CEZARA (2026-06-28): „sprawdź czy pamięć jest najlepsza na świecie, ulepsz o
kolejne warstwy i autorskie moduły — deep research, kreatywność, wizja, wg zasad."

DEEP RESEARCH — GRANICA 2026 (ZPO, pełne źródła):
  • Przegląd „Memory for Autonomous LLM Agents" (arXiv:2603.07670) — otwarte problemy:
    continual consolidation, causally-grounded retrieval, TRUSTWORTHY REFLECTION,
    LEARNED FORGETTING, contradiction handling.
  • „Self-Consolidation for Self-Evolving Agents" (arXiv:2602.01966).
  • OSTRZEŻENIE z literatury (kluczowe): refleksja potrafi UTRWALAĆ błędy — jeśli agent
    fałszywie uzna „podejście A zawsze zawodzi", nigdy go nie przetestuje. Rozwiązanie:
    walidacja zewnętrzna + polityki wygaszania + człowiek-w-pętli. Zep: okno ważności faktu.

CO ROBIMY (autorski moduł, deterministyczny, bez API — Prawo I; chmura i lokal):
  Refleksja, która NIE utrwala błędów, bo TYLKO ZGŁASZA (Cezar decyduje — Prawo XVIII):
  1. SPRZECZNOŚCI/ROZSTRZYGNIĘCIA: wpisy o tym samym temacie z PRZECIWNYM kierunkiem
     statusu w czasie (np. DECYZJA „NIE robimy X" → później ZMIANA „zrobiono X";
     albo lekcja „X NIEZROBIONE" → „X ODHACZONE"). Dwa typy:
       • ROZSTRZYGNIĘTE ✅ — postęp (stary plan zrealizowany) — to DOBRZE, koniec krążenia.
       • SPRZECZNE ⚠️ — realna kolizja decyzji — do przeglądu Cezara.
  2. PRZEDAWNIENIE (staleness, jak okno ważności Zep): POMYSŁ/PLANOWANE starsze niż N dni
     bez późniejszego śladu realizacji → „wisi, zdecyduj" (zrób / odrzuć / odłóż świadomie).

ZASADA ANTY-UTRWALANIA (wprost z granicy 2026): moduł NIGDY nie kasuje ani nie nadpisuje
pamięci automatycznie. Generuje RAPORT do rozstrzygnięcia. To „trustworthy reflection":
maszyna proponuje, Cezar dysponuje. Zero ryzyka, że błędna refleksja zamknie dobry trop.

Pod zarządem Kustosza (W7); używa temporalności Grafu (W8) i statusów Rejestru Wizji (W4).

CLI:
  python -m imperium.biblioteki.refleksja_pamieci raport
  python -m imperium.biblioteki.refleksja_pamieci sprzecznosci
  python -m imperium.biblioteki.refleksja_pamieci przedawnienia --dni 21
"""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, Any, List, Optional, Set

# Markery kierunku statusu — do wykrywania „flipu" w czasie.
_NEGATYW = {"odrzucona", "odrzucone", "nie", "niezrobione", "niezrobiona", "zawieszona",
            "porzucone", "wstrzymane", "kandydat", "planowane", "pomysł", "pomysl"}
_POZYTYW = {"wdrożona", "wdrozona", "wdrożone", "zrobione", "zrobiona", "gotowe",
            "odhaczona", "odhaczone", "ukończone", "zamknięta", "zamknieta"}

_MIN_DL = 4
_STOP = {"prawo", "sesja", "claude", "cezar", "memory", "pamięci", "pamiec", "warstwa",
         "system", "tylko", "więcej", "robić", "który", "która", "które", "wszystko"}

# Źródła niosące REALNY status per-przedmiot (wizje mają pole status: WDROŻONA/POMYSŁ/…).
# Detekcja sprzeczności ogranicza się do nich — dziennik to narracja osi czasu, nie ledger
# statusu (patrz docstring wykryj_sprzecznosci: mieszanie dawało 92 fałszywe pozytywy).
_ZRODLA_STATUSOWE = {"wizje"}


def _dzis_ord() -> int:
    return date.today().toordinal()


def _tematy(tekst: str) -> Set[str]:
    """Znaczące tokeny tematu (do dopasowania wpisów o tym samym przedmiocie)."""
    out = set()
    for w in re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9_\-]{%d,}" % _MIN_DL, tekst.lower()):
        if w in _STOP or w.isdigit() or w in _NEGATYW or w in _POZYTYW:
            continue
        out.add(w)
    return out


def _kierunek(tekst: str) -> Optional[str]:
    """'+' gdy tekst niesie realizację, '-' gdy negację/plan, None gdy neutralny."""
    low = set(re.findall(r"[a-ząćęłńóśźż]+", tekst.lower()))
    poz = bool(low & _POZYTYW)
    neg = bool(low & _NEGATYW)
    if poz and not neg:
        return "+"
    if neg and not poz:
        return "-"
    return None


# ─── ŹRÓDŁA (W4 wizje + W3 lekcje + W6 dziennik) ───────────────────────────────

def _wpisy_statusowe() -> List[Dict[str, Any]]:
    """
    Zbiera wpisy z polem czasu + tematem + kierunkiem statusu.
    [{data, tematy:set, kierunek:'+'/'-'/None, opis, zrodlo, status}]
    """
    wpisy: List[Dict[str, Any]] = []
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        for w in _rw.wszystkie():
            txt = f"{w.get('tytul','')} {w.get('tresc','')} {w.get('status','')}"
            wpisy.append({
                "data": w.get("data", ""),
                "tematy": _tematy(w.get("tytul", "") + " " + w.get("tresc", "")),
                "kierunek": _kierunek(w.get("status", "") + " " + txt),
                "opis": w.get("tytul", ""),
                "zrodlo": "wizje",
                "status": w.get("status", ""),
            })
    except Exception:
        pass
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        for w in _dn.wszystkie():
            for c in w.get("co", []) + w.get("decyzje", []):
                wpisy.append({
                    "data": w.get("data", ""),
                    "tematy": _tematy(c),
                    "kierunek": _kierunek(c),
                    "opis": c[:120],
                    "zrodlo": "dziennik",
                    "status": "",
                })
    except Exception:
        pass
    return wpisy


def _nakladanie(a: Set[str], b: Set[str], minimum: int = 2) -> bool:
    """Czy dwa wpisy dotyczą tego samego przedmiotu (≥minimum wspólnych tematów)."""
    return len(a & b) >= minimum


# ─── DETEKCJA SPRZECZNOŚCI / ROZSTRZYGNIĘĆ ─────────────────────────────────────

def wykryj_sprzecznosci(limit: int = 20,
                        zrodla: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    """
    Pary wpisów o tym samym temacie z PRZECIWNYM kierunkiem statusu w czasie.
    Wcześniejszy '-' + późniejszy '+' = ROZSTRZYGNIĘTE (postęp, koniec krążenia).
    Wcześniejszy '+' + późniejszy '-' = SPRZECZNE (regres/kolizja — do przeglądu).

    ŹRÓDŁA (Prawo I — pomiar 2026-07-12): sprzeczność ma sens TYLKO między wpisami
    niosącymi REALNY status per-przedmiot (wizje: WDROŻONA/POMYSŁ/PLANOWANE/ZAMKNIĘTA).
    Dziennik to narracja osi czasu — jego „co zrobiliśmy" prawie zawsze ma słowo
    pozytywne (→+), a „czego NIE robić" ma „nie" (→−); parowanie takich zdań z wizjami
    dawało 92 FAŁSZYWE pozytywy (tylko-wizje=0, tylko-dziennik=1, mieszane=92). Dlatego
    domyślnie liczymy tylko ze źródeł statusowych. `zrodla=None` → {"wizje"}; podaj
    jawny zbiór (np. {"wizje","dziennik"}) by rozszerzyć świadomie.
    """
    if zrodla is None:
        zrodla = _ZRODLA_STATUSOWE
    wpisy = [w for w in _wpisy_statusowe()
             if w["kierunek"] and w["tematy"] and w["zrodlo"] in zrodla]
    wpisy.sort(key=lambda w: w["data"])
    wyniki = []
    for i in range(len(wpisy)):
        for j in range(i + 1, len(wpisy)):
            a, b = wpisy[i], wpisy[j]
            if a["kierunek"] == b["kierunek"]:
                continue
            if a["data"] == b["data"]:
                continue
            if not _nakladanie(a["tematy"], b["tematy"]):
                continue
            wczesny, pozny = (a, b) if a["data"] <= b["data"] else (b, a)
            typ = "ROZSTRZYGNIĘTE" if (wczesny["kierunek"] == "-" and pozny["kierunek"] == "+") \
                else "SPRZECZNE"
            wyniki.append({
                "typ": typ,
                "temat": sorted(a["tematy"] & b["tematy"])[:4],
                "wczesny": f"[{wczesny['data']}] {wczesny['opis']}",
                "pozny": f"[{pozny['data']}] {pozny['opis']}",
            })
    # SPRZECZNE najpierw (ważniejsze do uwagi)
    wyniki.sort(key=lambda x: 0 if x["typ"] == "SPRZECZNE" else 1)
    return wyniki[:limit]


# ─── DETEKCJA PRZEDAWNIENIA (staleness / okno ważności) ────────────────────────

def wykryj_przedawnienia(dni: int = 21, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Otwarte pomysły/plany (POMYSŁ/PLANOWANE) starsze niż `dni` bez późniejszego
    śladu realizacji na tych samych tematach → „wisi, zdecyduj" (rób/odrzuć/odłóż).
    """
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        wpisy = _rw.wszystkie()
    except Exception:
        return []
    realizacje = [w for w in _wpisy_statusowe() if w["kierunek"] == "+"]
    stale = []
    for w in wpisy:
        status = (w.get("status", "") or "").upper()
        if status not in ("POMYSŁ", "POMYSL", "PLANOWANE", "ZAWIESZONA"):
            continue
        data = w.get("data", "")
        try:
            wiek = _dzis_ord() - date.fromisoformat(data).toordinal()
        except (ValueError, TypeError):
            continue
        if wiek < dni:
            continue
        tematy = _tematy(w.get("tytul", "") + " " + w.get("tresc", ""))
        # czy jest późniejsza realizacja na tych tematach? → już nie wisi
        zrealizowane = any(
            r["data"] > data and _nakladanie(tematy, r["tematy"]) for r in realizacje)
        if zrealizowane:
            continue
        stale.append({
            "wiek_dni": wiek,
            "status": status,
            "opis": w.get("tytul", ""),
            "data": data,
        })
    stale.sort(key=lambda x: x["wiek_dni"], reverse=True)
    return stale[:limit]


# ─── RAPORT ZBIORCZY ───────────────────────────────────────────────────────────

def raport(dni_przedawnienia: int = 21) -> Dict[str, Any]:
    spr = wykryj_sprzecznosci()
    prz = wykryj_przedawnienia(dni=dni_przedawnienia)
    return {
        "sprzeczne": [s for s in spr if s["typ"] == "SPRZECZNE"],
        "rozstrzygniete": [s for s in spr if s["typ"] == "ROZSTRZYGNIĘTE"],
        "przedawnione": prz,
    }


def raport_startowy(dni_przedawnienia: int = 21) -> str:
    """Zwięzła linia do podsumowania startowego (tylko gdy jest co zgłosić)."""
    r = raport(dni_przedawnienia)
    n_spr = len(r["sprzeczne"])
    n_prz = len(r["przedawnione"])
    if not n_spr and not n_prz:
        return ""
    czesci = []
    if n_spr:
        czesci.append(f"⚠️ {n_spr} sprzeczności do przeglądu")
    if n_prz:
        czesci.append(f"⏳ {n_prz} pomysłów wisi >{dni_przedawnienia}d (zdecyduj)")
    return "   🪞 Refleksja (W9): " + " | ".join(czesci)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Refleksja Pamięci — W9 sprzeczności+przedawnienie (W-360 v9)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("raport", help="Pełny raport refleksji")
    sub.add_parser("sprzecznosci", help="Sprzeczności i rozstrzygnięcia")
    pp = sub.add_parser("przedawnienia", help="Przedawnione otwarte pomysły")
    pp.add_argument("--dni", type=int, default=21)
    args = p.parse_args()

    if args.cmd == "sprzecznosci":
        for s in wykryj_sprzecznosci():
            znak = "⚠️" if s["typ"] == "SPRZECZNE" else "✅"
            print(f"{znak} {s['typ']} {s['temat']}\n   wcześ: {s['wczesny']}\n   późn:  {s['pozny']}")
    elif args.cmd == "przedawnienia":
        for s in wykryj_przedawnienia(dni=args.dni):
            print(f"⏳ {s['wiek_dni']}d [{s['status']}] {s['opis']} ({s['data']})")
    else:
        r = raport()
        print(f"⚠️ Sprzeczne: {len(r['sprzeczne'])} | ✅ Rozstrzygnięte: {len(r['rozstrzygniete'])} "
              f"| ⏳ Przedawnione: {len(r['przedawnione'])}")
        for s in r["sprzeczne"]:
            print(f"  ⚠️ {s['temat']}: {s['wczesny']} ↔ {s['pozny']}")
        for s in r["przedawnione"][:5]:
            print(f"  ⏳ {s['wiek_dni']}d [{s['status']}] {s['opis']}")
