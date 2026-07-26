"""
📋 Rejestr Wizji i Decyzji — W4 Centrum Pamięci W-360 v4

WARSTWA 4 — ustrukturyzowana pamięć POMYSŁÓW, WIZJI, DECYZJI i ZMIAN.
Uzupełnia warstwy 1-3 o kontekst strategiczny (co postanowiono, co odrzucono, co planujemy).

Problem rozwiązany:
  Warstwa W3 (lekcje) zbiera "co się nauczyliśmy" — ale "co postanowiliśmy" i "co widzimy
  jako przyszłość" ginęło w masie kroniki (score=0.3 flat, nieszukalne). Teraz ma własną
  warstwę z pełnym scoringiem GA (recency × importance × relevance × regime_match).

TYPY wpisów:
  WIZJA     — długoterminowy kierunek ("portfel 20 par multiasset")
  DECYZJA   — zamknięta sprawa ("NIE robimy X bo Y") — żeby nie wracać do tego
  POMYSŁ    — open backlog ("RAG z wektorami — czeka na dostęp do sieci")
  ZMIANA    — rejestr wdrożeń ("dodano neuron X-28 MTF, sesja 2026-06-25")

STATUSY:
  POMYSŁ / PLANOWANE / WDROŻONA / ODRZUCONA / ZAWIESZONA / ZAMKNIĘTA

Format JSONL (jeden wpis = jedna linia JSON):
  {"data": "RRRR-MM-DD", "typ": "WIZJA|DECYZJA|POMYSŁ|ZMIANA",
   "tytul": "...", "tresc": "...", "status": "...", "rezim": "BULL|..."}

CLI:
  python -m imperium.biblioteki.rejestr_wizji dodaj WIZJA "tytuł" "treść"
  python -m imperium.biblioteki.rejestr_wizji lista
  python -m imperium.biblioteki.rejestr_wizji szukaj "zapytanie"
  python -m imperium.biblioteki.rejestr_wizji status "tytuł" WDROŻONA
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional, Any

ROOT = Path(__file__).resolve().parent.parent.parent
PLIK_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "wizje_i_decyzje.jsonl"

TYPY_DOZWOLONE = {"WIZJA", "DECYZJA", "POMYSŁ", "ZMIANA"}
STATUSY_DOZWOLONE = {"POMYSŁ", "PLANOWANE", "WDROŻONA", "ODRZUCONA", "ZAWIESZONA", "ZAMKNIĘTA"}

# Wagi ważności per typ — wpływają na scoring GA (recency decay i importance)
_WAGA_TYPU: Dict[str, float] = {
    "WIZJA":    0.9,   # strategicznie ważna — powoli opada
    "DECYZJA":  0.85,  # zamknięta sprawa — wysoka waga by nie wracać do niej
    "ZMIANA":   0.7,   # wdrożenie — średnia waga
    "POMYSŁ":   0.5,   # open backlog — niska, może być wiele
}

# Mnożniki statusu: WDROŻONA/ZAMKNIĘTA tracą na ważności z czasem (są archiwum)
_MNOZNIK_STATUSU: Dict[str, float] = {
    "POMYSŁ":      1.0,
    "PLANOWANE":   1.0,
    "WDROŻONA":    0.6,   # historyczne — mniej pilne
    "ODRZUCONA":   0.4,   # mniej pilne, ale pamiętamy "czego nie robić"
    "ZAWIESZONA":  0.8,
    "ZAMKNIĘTA":   0.5,
}


def _dzis() -> str:
    return date.today().isoformat()


def _wczytaj(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    if plik is None:
        plik = PLIK_DOMYSLNY
    if not plik.exists():
        return []
    wynik = []
    for linia in plik.read_text(encoding="utf-8", errors="ignore").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            wynik.append(json.loads(linia))
        except (json.JSONDecodeError, ValueError):
            continue
    return wynik


def _zapisz_dopisz(wpis: Dict[str, Any], plik: Optional[Path] = None) -> None:
    if plik is None:
        plik = PLIK_DOMYSLNY
    plik.parent.mkdir(parents=True, exist_ok=True)
    with plik.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False) + "\n")


def _nadpisz(wszystkie_wpisy: List[Dict[str, Any]], plik: Optional[Path] = None) -> None:
    if plik is None:
        plik = PLIK_DOMYSLNY
    plik.parent.mkdir(parents=True, exist_ok=True)
    with plik.open("w", encoding="utf-8") as f:
        for w in wszystkie_wpisy:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")


# ─── CRUD ──────────────────────────────────────────────────────────────────────

def dodaj(typ: str, tytul: str, tresc: str,
          status: str = "POMYSŁ", rezim: str = "",
          data: Optional[str] = None,
          plik: Optional[Path] = None,
          dedup: bool = True) -> bool:
    """
    Dodaje nowy wpis do rejestru. Zwraca True gdy dopisano, False gdy pominięto (duplikat).

    dedup=True (domyślnie): pomija wpis, jeśli istnieje już wpis mówiący TO SAMO.
    Naprawa L6 (audyt 2026-06-26): auto_lekcja co sesję mogła dublować te same wizje.

    🚨 DEDUP SEMANTYCZNY, NIE PO NAPISIE (naprawa 2026-07-26). Wcześniej porównywaliśmy
    wyłącznie (typ, tytuł) znak w znak, a wpisy pisze DeepSeek, który parafrazuje przy
    każdym przebiegu: „Zsynchronizowac repo z chmura (rozjazd 2⇄2)" i „Rozwiązanie rozjazdu
    repo przez stash/rebase" to jeden pomysł i dwa wpisy. Zmierzone w dniu naprawy:
    11 zduplikowanych tytułów na 827 wpisów przeszło przez bramkę po dokładnym tytule.

    Używamy TEGO SAMEGO predykatu, co pamięć lekcji (`pamiec_sesji.czy_duplikaty`) —
    jeden predykat, dwa rejestry (Prawo XVI). Dwa osobne progi podobieństwa rozjechałyby
    się i ten sam pomysł byłby duplikatem w jednym rejestrze, a nowością w drugim.
    """
    if plik is None:
        plik = PLIK_DOMYSLNY
    typ = typ.upper()
    status = status.upper()
    if typ not in TYPY_DOZWOLONE:
        raise ValueError(f"Typ musi być jednym z: {TYPY_DOZWOLONE}")
    if status not in STATUSY_DOZWOLONE:
        raise ValueError(f"Status musi być jednym z: {STATUSY_DOZWOLONE}")

    tytul = tytul.strip()
    if dedup:
        # Import lokalny: rejestr wizji jest warstwą niżej niż pamięć lekcji, więc import
        # na szczycie modułu zawiązałby cykl. Awaria predykatu nie może zablokować zapisu —
        # wtedy schodzimy do porównania napisów (gorsze, ale nigdy nie gubi wpisu).
        try:
            from imperium.biblioteki.pamiec_sesji import czy_duplikaty
        except Exception:                       # noqa: BLE001 — zapis ważniejszy niż dedup
            czy_duplikaty = None
        for istn in _wczytaj(plik):
            if istn.get("typ", "").upper() != typ:
                continue                        # różne typy to różne byty (WIZJA ≠ ZMIANA)
            if istn.get("tytul", "").strip().lower() == tytul.lower():
                return False                    # sito 1: identyczny tytuł
            if czy_duplikaty is not None and czy_duplikaty(
                    tytul, tresc, istn.get("tytul", ""), istn.get("tresc", "")):
                return False                    # sito 2: ta sama treść, inna parafraza

    wpis = {
        "data": data or _dzis(),
        "typ": typ,
        "tytul": tytul,
        "tresc": tresc.strip(),
        "status": status,
        "rezim": rezim.upper() if rezim else "",
    }
    _zapisz_dopisz(wpis, plik)
    return True


def wszystkie(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Zwraca wszystkie wpisy z rejestru."""
    return _wczytaj(plik)


def zmien_status(tytul: str, nowy_status: str,
                 plik: Optional[Path] = None) -> bool:
    """Zmienia status wpisu o danym tytule. Zwraca True gdy znaleziono."""
    nowy_status = nowy_status.upper()
    if nowy_status not in STATUSY_DOZWOLONE:
        raise ValueError(f"Status musi być jednym z: {STATUSY_DOZWOLONE}")
    wpisy = _wczytaj(plik)
    zmieniono = False
    for w in wpisy:
        if w.get("tytul", "").lower() == tytul.lower():
            w["status"] = nowy_status
            # KIEDY zapadła decyzja — bez tego Refleksja (W9) liczyła wiek wpisu
            # ZAWIESZONEGO od jego UTWORZENIA, więc świeżo podjęta decyzja „odłóż"
            # natychmiast wracała jako „⏳ wisi, zdecyduj". Alarmu nie dawało się
            # wyciszyć decyzją — a alarm, którego nie można wyciszyć, uczy ignorowania
            # alarmów (zmierzone 2026-07-20: wpis zamknięty rano nadal nagabywał).
            w["data_statusu"] = date.today().isoformat()
            zmieniono = True
            break
    if zmieniono:
        _nadpisz(wpisy, plik)
    return zmieniono


def szukaj(zapytanie: str, limit: int = 10,
           plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Pełnotekstowe przeszukanie rejestru (bez scoringu GA — do CLI)."""
    q = zapytanie.lower()
    wyniki = []
    for w in _wczytaj(plik):
        tekst = f"{w.get('tytul','')} {w.get('tresc','')}".lower()
        if q in tekst:
            wyniki.append(w)
        if len(wyniki) >= limit:
            break
    return wyniki


# ─── SCORING GA (recency × importance × relevance × regime_match) ─────────────

def score_wizji(wpis: Dict[str, Any], zapytanie: str = "",
                rezim_biezacy: str = "") -> float:
    """
    Scoring Generative Agents dla wpisu W4.
    recency × importance(typ×status) × relevance × regime_match.
    """
    from imperium.biblioteki.centrum_pamieci import (
        _recency, _relevance, _regime_match, _wykryj_rezim,
    )

    importance = _WAGA_TYPU.get(wpis.get("typ", "POMYSŁ"), 0.5)
    importance *= _MNOZNIK_STATUSU.get(wpis.get("status", "POMYSŁ"), 1.0)
    importance = max(importance, 0.3)

    rec = _recency(wpis.get("data", ""), importance)
    rel = _relevance(zapytanie, wpis.get("tytul", ""), wpis.get("tresc", ""))

    # Reżim: z jawnego pola "rezim" lub wykryty z tekstu
    rezim_wsp = wpis.get("rezim") or _wykryj_rezim(
        wpis.get("tytul", "") + " " + wpis.get("tresc", ""))
    rz = _regime_match(rezim_wsp, rezim_biezacy)

    baza = rec * importance * rel if zapytanie else rec * importance
    return baza * rz


def szukaj_scored(zapytanie: str = "", limit: int = 10,
                  rezim_biezacy: str = "",
                  plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Scored search W4 — jak top_lekcji, ale dla wizji/decyzji/pomysłów.
    Zwraca [{"score": float, "warstwa": "wizje", ...pola wpisu}].
    """
    wyniki = []
    for w in _wczytaj(plik):
        s = score_wizji(w, zapytanie, rezim_biezacy)
        q = zapytanie.lower() if zapytanie else ""
        tekst = f"{w.get('tytul','')} {w.get('tresc','')}".lower()
        if q and q not in tekst and s < 0.05:
            continue
        wyniki.append({
            "warstwa": "wizje",
            "score": s,
            "data": w.get("data", ""),
            "typ": w.get("typ", ""),
            "status": w.get("status", ""),
            "tytul": w.get("tytul", ""),
            "tresc": w.get("tresc", "")[:200],
        })
    wyniki.sort(key=lambda x: x["score"], reverse=True)
    return wyniki[:limit]


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Rejestr Wizji i Decyzji — W4")
    sub = p.add_subparsers(dest="cmd")

    p_dodaj = sub.add_parser("dodaj", help="Dodaj wpis")
    p_dodaj.add_argument("typ", choices=["WIZJA", "DECYZJA", "POMYSL", "ZMIANA"])
    p_dodaj.add_argument("tytul")
    p_dodaj.add_argument("tresc")
    p_dodaj.add_argument("--status", default="POMYSŁ")
    p_dodaj.add_argument("--rezim", default="")

    p_lista = sub.add_parser("lista", help="Pokaż wszystkie wpisy")
    p_lista.add_argument("--typ", default="")
    p_lista.add_argument("--status", default="")

    p_szuk = sub.add_parser("szukaj", help="Szukaj w rejestrze (scored)")
    p_szuk.add_argument("zapytanie")
    p_szuk.add_argument("--limit", type=int, default=10)
    p_szuk.add_argument("--rezim", default="")

    p_status = sub.add_parser("status", help="Zmień status wpisu")
    p_status.add_argument("tytul")
    p_status.add_argument("nowy_status")

    args = p.parse_args()

    if args.cmd == "dodaj":
        typ = args.typ.replace("POMYSL", "POMYSŁ")
        dodaj(typ, args.tytul, args.tresc, args.status, args.rezim)
        print(f"✅ Dodano [{typ}] {args.tytul!r}")

    elif args.cmd == "lista":
        wpisy = wszystkie()
        if args.typ:
            wpisy = [w for w in wpisy if w.get("typ", "").upper() == args.typ.upper()]
        if args.status:
            wpisy = [w for w in wpisy if w.get("status", "").upper() == args.status.upper()]
        if not wpisy:
            print("(brak wpisów)")
        for w in wpisy:
            print(f"[{w['data']}] {w['typ']:8s} {w['status']:10s} {w['tytul']}")

    elif args.cmd == "szukaj":
        wyniki = szukaj_scored(args.zapytanie, args.limit, args.rezim)
        if not wyniki:
            print("(brak wyników)")
        for w in wyniki:
            print(f"score={w['score']:.3f} [{w['typ']}:{w['status']}] {w['tytul']}")
            print(f"  {w['tresc'][:120]}")

    elif args.cmd == "status":
        ok = zmien_status(args.tytul, args.nowy_status)
        print("✅ Zmieniono" if ok else "❌ Nie znaleziono")

    else:
        p.print_help()
        sys.exit(1)
