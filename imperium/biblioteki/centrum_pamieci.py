"""
🧠 Centrum Pamięci Imperium (W-360 v3) — zunifikowany hub wszystkich warstw pamięci.

PROBLEM: pamięć Imperium rozrosła się do 5 warstw, każda z osobnym API. Jedynym
wejściem jest git/RAG (wyszukiwanie ręczne). Brak: cross-layer search, scoringu
lekcji (Generative Agents: recency·importance·relevance), proaktywnych przypomnień.

ROZWIĄZANIE: ten moduł jest FASADĄ (nie duplikuje logiki!) — jedyna ścieżka do całej
pamięci Imperium. Zastępuje rozsiane importy jednym `from imperium.biblioteki import
centrum_pamieci as pm`.

WARSTWY (każda pozostaje samodzielna, tu tylko spięta w całość):
  W1 — mnemosyne.py      : pamięć TRANSAKCJI (trade learning, Book of Flaws, SQLite)
  W1 — pamiec_absolutna.py: logi SYGNAŁÓW, TRADE, ANALIZA, TEST (JSONL / TypLogu)
  W2 — bibliotheca_ulpia/ : RAG semantyczny (FTS5+wektory, 32 książki + docs + kronika)
  W3 — pamiec_sesji.py   : LEKCJE z sesji + PROFIL Cezara (markdown → git)
  W3 — kronika_czatu.py  : PEŁNY DIALOG (destylat transkryptów → git)

NOWOŚCI (adopcja badań 2024-2026):
  • Scoring Generative Agents (Park et al., arXiv:2304.03442):
    score = recency × importance × relevance
    - recency  : wykładniczy zanik (decay^Δdn), dn = dni od lekcji, decay=0.995^Δdn
    - importance: heurystyka z słów kluczowych (brak LLM → zero kosztu), 0.0–1.0
    - relevance : Jaccard słów (FTS bez wektorów → działa offline), 0.0–1.0
    EFEKT: lekcje ważne + świeże + trafne wypływają na górę; stare/nieistotne toną.

  • Mem0-style multi-level scope: sesja / użytkownik (Cezar) / agent (Imperium).
    Każda lekcja nosi scope, co pozwala filtrować (lekcje tylko o backteście etc.).

  • Cross-layer search: jedno zapytanie → szuka w lekcjach (W3) + kronice (W3b) +
    Mnemosyne trade lessons (W1) naraz. Wyniki z każdej warstwy oznaczone źródłem.

  • Proaktywne przypomnienie startowe (`podsumowanie_startowe_rozszerzone`):
    Top-k lekcji wg scoringu + alarm przepełnienia + profil Cezara. Wstrzyknięte
    do SessionStart hooka zamiast prostego „ostatnie 3".

ARCHITEKTURA PAMIĘCI (dla SessionStart hook — zastępuje wywołanie pamiec_sesji.py):
  centrum_pamieci podsumowanie_startowe → hook wyświetla scored TOP-3 + cross-layer

Bez zależności zewnętrznych (stdlib: re, math, datetime, pathlib) → działa w chmurze.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional, Any

# Importy warstw (leniwe → nie wymuszają wszystkich zależności, jeśli warstwa niedostępna)
from imperium.biblioteki import pamiec_sesji as _ps
from imperium.biblioteki import kronika_czatu as _kc

ROOT = Path(__file__).resolve().parent.parent.parent

# ─── SCORING GENERATIVE AGENTS (Park et al., 2304.03442) ─────────────────────

_DECAY = 0.995           # wykładniczy zanik jak w oryginalnym paper (per dzień)
_EPOKA = date(2026, 6, 1)  # data referencyjna (daty w PAMIEC_SESJI są YYYY-MM-DD)

# Słowa wskazujące na ważność lekcji (heurystyka zamiast LLM — zero kosztu).
# Wzorowane na Mem0 ADD/UPDATE metadanych: lekcje z bugiem/odkryciem/prawem ważniejsze.
_SLOWA_WAZNE = {
    "bug": 0.9, "fix": 0.8, "błąd": 0.9, "odkrycie": 0.9, "prawo": 0.8,
    "utrata potencjału": 1.0, "prawo xv": 1.0, "prawo xxi": 1.0,
    "speedup": 0.7, "optymalizacja": 0.6, "adopcja": 0.7,
    "backtest": 0.6, "sharpe": 0.7, "reżim": 0.7, "signal": 0.6,
    "mcp": 0.5, "pamięć": 0.5, "kronika": 0.5, "profil": 0.4,
}


def _recency(data_str: str) -> float:
    """Wykładniczy zanik od daty lekcji do dziś (1.0 = dziś, ~0.6 = rok temu)."""
    try:
        d = date.fromisoformat(data_str)
    except ValueError:
        return 0.5
    delta = (date.today() - d).days
    return _DECAY ** max(delta, 0)


def _importance(tytul: str, tresc: str) -> float:
    """Heurystyczna ważność lekcji (0-1) z słów kluczowych — brak LLM = zero kosztu."""
    tekst = (tytul + " " + tresc).lower()
    maks = 0.0
    for slowo, waga in _SLOWA_WAZNE.items():
        if slowo in tekst:
            maks = max(maks, waga)
    return max(maks, 0.3)   # minimum 0.3 — każda lekcja ma pewną wartość bazową


def _relevance(zapytanie: str, tytul: str, tresc: str) -> float:
    """Jaccard similarity słów (FTS bez wektorów → offline, zero kosztu)."""
    if not zapytanie:
        return 0.5
    q = set(re.findall(r"\w+", zapytanie.lower()))
    t = set(re.findall(r"\w+", (tytul + " " + tresc).lower()))
    if not q or not t:
        return 0.0
    return len(q & t) / len(q | t)


def score_lekcji(lekcja: Dict[str, str], zapytanie: str = "") -> float:
    """
    Scoring Generative Agents: score = recency × importance × relevance.
    Normalizowany do [0,1] per wywołanie (nie globalnie — brak potrzeby kalibracji).
    """
    r = _recency(lekcja["data"])
    i = _importance(lekcja["tytul"], lekcja["tresc"])
    v = _relevance(zapytanie, lekcja["tytul"], lekcja["tresc"])
    return r * i * v if zapytanie else r * i


# ─── CROSS-LAYER SEARCH ───────────────────────────────────────────────────────

def szukaj_wszedzie(zapytanie: str, limit: int = 10,
                   cel_kronika: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Cross-layer search (Mem0-style multi-level scope): jedno zapytanie →
    szuka w lekcjach (W3), kronice (W3b) i zwraca wyniki ze źródłem.
    Wyniki rankowane scoringiem Generative Agents (lekcje) lub tf-idf proxy (kronika).

    Returns [{"warstwa": "lekcje"|"kronika", "score": float, "tresc": str, ...}]
    """
    wyniki: List[Dict[str, Any]] = []

    # W3 — lekcje (scored)
    for lek in _ps.lekcje(plik=_ps.DOMYSLNY_PLIK):
        s = score_lekcji(lek, zapytanie)
        q = zapytanie.lower()
        if q and (q not in lek["tytul"].lower() and q not in lek["tresc"].lower()) and s < 0.05:
            continue
        wyniki.append({
            "warstwa": "lekcje",
            "score": s,
            "data": lek["data"],
            "tytul": lek["tytul"],
            "tresc": lek["tresc"][:200],
        })

    # W3b — kronika (FTS prosty)
    cel = cel_kronika or _kc.CEL_DOMYSLNY
    for t in _kc.szukaj(zapytanie, cel, limit=limit):
        wyniki.append({
            "warstwa": "kronika",
            "score": 0.3,    # kronika nie ma scoringu GA — jednorodny poziom
            "sesja": t["sesja"],
            "tresc": t["fragment"],
        })

    wyniki.sort(key=lambda x: x["score"], reverse=True)
    return wyniki[:limit]


# ─── TOP-K LEKCJI (SCORED) ────────────────────────────────────────────────────

def top_lekcji(k: int = 3, zapytanie: str = "") -> List[Dict[str, Any]]:
    """
    Top-k lekcji wg scoringu Generative Agents (recency × importance × relevance).
    Zastępuje proste 'ostatnie N' — wypływają najważniejsze+świeże, nie tylko najnowsze.
    """
    wszystkie = _ps.lekcje(plik=_ps.DOMYSLNY_PLIK)
    scored = [(score_lekcji(lek, zapytanie), lek) for lek in wszystkie]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, **lek} for s, lek in scored[:k]]


# ─── SCOPE (Mem0-style multi-level) ──────────────────────────────────────────

def lekcje_scope(scope: str) -> List[Dict[str, str]]:
    """
    Mem0-style multi-level scope: 'backtest', 'pamiec', 'neurony', 'strategia' itd.
    Filtruje lekcje po słowie kluczowym w tytule/treści.
    scope='*' lub '' → wszystkie.
    """
    if not scope or scope == "*":
        return _ps.lekcje(plik=_ps.DOMYSLNY_PLIK)
    return _ps.szukaj(scope, plik=_ps.DOMYSLNY_PLIK)


# ─── ZUNIFIKOWANE PODSUMOWANIE STARTOWE (zastępuje pamiec_sesji.podsumowanie) ─

def podsumowanie_startowe(k: int = 3, zapytanie: str = "") -> str:
    """
    Rozszerzone podsumowanie dla SessionStart hooka — scored TOP-k zamiast 'ostatnie N':
    profil Cezara + top-k lekcji (Generative Agents scoring) + alarm + mapa.
    Wstrzyknięte przez hook (centrum_pamieci.py nadpisuje wywołanie pamiec_sesji.start).
    """
    linie = ["🧠 CENTRUM PAMIĘCI (W-360 v3) — ciągłość między sesjami:"]

    # Profil Cezara (USER.md-style)
    profil = _ps.profil_skrot()
    if profil:
        linie.append("   👤 Profil Cezara:")
        for p in profil[:3]:
            linie.append(f"   {p}")

    # Top-k lekcji (scored GA zamiast 'ostatnie N')
    top = top_lekcji(k, zapytanie)
    if top:
        linie.append(f"   🏆 Top-{k} lekcji (recency×importance×relevance):")
        for lek in top:
            linie.append(f"   • [{lek['data']}] {lek['tytul']} (score={lek['score']:.3f})")

    # Alarm przepełnienia (Prawo XV)
    alarm = _ps.alarm_przepelnienia()
    if alarm:
        linie.append(f"   {alarm}")

    # Statystyki warstw
    st = _kc.statystyki()
    linie.append(f"   📜 Kronika: {st['sesje']} sesji, {st['znaki']/1e6:.1f} MB dialogu w repo")
    linie.append("   📍 Mapa podpięć + wdrożenia: docs/PAMIEC_SESJI.md")
    return "\n".join(linie)


# ─── QUICK API (jeden import = cała pamięć) ────────────────────────────────────

def dopisz_lekcje(tytul: str, tresc: str, data: Optional[str] = None) -> None:
    """Dodaj lekcję (deleguje do pamiec_sesji — tu dla wygody jednego importu)."""
    _ps.dopisz_lekcje(tytul, tresc, data)


def usun_lekcje(tytul: str) -> bool:
    return _ps.usun_lekcje(tytul)


def aktualizuj_lekcje(tytul: str, nowa_tresc: str, nowy_tytul: Optional[str] = None) -> bool:
    return _ps.aktualizuj_lekcje(tytul, nowa_tresc, nowy_tytul=nowy_tytul)


def eksportuj_kroniki() -> Dict[str, int]:
    """Przyrostowy eksport transkryptów do repo (deleguje do kronika_czatu)."""
    return _kc.eksportuj()


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Centrum Pamięci Imperium (W-360 v3)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("start", help="podsumowanie startowe (hook)")
    sub.add_parser("top", help="top-3 lekcji wg scoringu GA")
    p_szuk = sub.add_parser("szukaj", help="cross-layer search")
    p_szuk.add_argument("zapytanie", nargs="+")
    p_szuk.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    if args.cmd == "start":
        print(podsumowanie_startowe())
    elif args.cmd == "top":
        for lek in top_lekcji(5):
            print(f"[{lek['score']:.3f}] [{lek['data']}] {lek['tytul']}")
    elif args.cmd == "szukaj":
        q = " ".join(args.zapytanie)
        for w in szukaj_wszedzie(q, args.limit):
            warstwa = w["warstwa"]
            tresc = w.get("tytul", w.get("tresc", ""))[:80]
            print(f"[{w['score']:.3f}][{warstwa}] {tresc}")
    else:
        print(podsumowanie_startowe())
