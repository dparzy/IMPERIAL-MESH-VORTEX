"""
👑 Kustosz Pamięci — W7 Centrum Pamięci W-360 v7: NADRZĘDNY ORGAN (UNIKAT IMPERIUM)

ROZKAZ CEZARA (2026-06-28): „nadrzędny organ, który będzie kierował wszystkimi
warstwami pamięci — kompresja, katalogowanie, kodowanie, pamięć bezwzględna,
bezgraniczna — niezależnie czy chmura czy lokal. Coś czego nikt nie ma."

KONTEKST SOTA 2026 (ZPO — pełne źródła):
  • MemGPT/Letta — wirtualna pamięć jak OS: hot context / recall / archival cold storage.
    https://arxiv.org/abs/2310.08560
  • TiMem — Temporal-Hierarchical Memory Consolidation, https://arxiv.org/pdf/2601.02845
  • EverMemOS — self-organizing memory OS; przegląd: arXiv:2603.07670 (Memory for
    Autonomous LLM Agents). GŁÓWNY PROBLEM nazwany przez literaturę: „memory blindness"
    — agent nie wie, że fakt istnieje w zimnym magazynie → archiwizacja = utrata wiedzy.

CO MAMY, CZEGO NIKT NIE MA (połączone w jednym organie):
  1. Pamięć REŻIMOWA (W3/W4 — score × regime_match): retrieval świadomy reżimu rynku.
  2. Pamięć ŚRODOWISKOWA (W5 — chmura/lokal): ta sama pamięć, dwa tryby.
  3. DZIENNIK NIEŚMIERTELNY (W6): pełna oś wstrzykiwana na starcie → ZERO memory blindness.
  4. KUSTOSZ (W7, TU): jeden organ nadrzędny, który tym wszystkim ZARZĄDZA —
     katalog (anti-blindness), kompresja zimnej warstwy (.md.gz, wciąż przeszukiwalna),
     census wszystkich 7 warstw, routing zapytań. Deterministyczny (bez API).

ZASADA „PAMIĘĆ BEZGRANICZNA": git przechowuje WSZYSTKO na zawsze (storage = nieograniczony).
Kustosz pilnuje, by KONTEKST pozostał ograniczony (Dziennik zwięzły + zimne sesje
skompresowane), a NIC nie ginęło (zimne wciąż przeszukiwalne — dekompresja w locie).
To rozwiązuje dylemat literatury: pełna pamięć BEZ memory blindness, BEZ przepełnienia kontekstu.

WARSTWY POD ZARZĄDEM KUSTOSZA:
  W1 logi (pamiec_absolutna) · W2 RAG (książki) · W3 lekcje+kronika · W4 wizje
  W5 most chmura/lokal · W6 dziennik nieśmiertelny · (W7 = ten organ)

CLI:
  python -m imperium.biblioteki.kustosz_pamieci census      # stan wszystkich warstw
  python -m imperium.biblioteki.kustosz_pamieci kataloguj   # zbuduj katalog nadrzędny
  python -m imperium.biblioteki.kustosz_pamieci kompresuj --dni 30   # zimna warstwa → .gz
  python -m imperium.biblioteki.kustosz_pamieci szukaj "zapytanie"
"""

from __future__ import annotations

import gzip
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
KRONIKA_DIR = ROOT / "bibliotheca_ulpia" / "dane" / "kronika"
KATALOG_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "katalog_nadrzedny.json"

# Słowa-szum pomijane przy ekstrakcji tematów katalogu (PL + technikalia formatu).
_STOP = {
    "the", "and", "dla", "jest", "się", "nie", "tak", "czy", "ale", "lub", "oraz",
    "to", "co", "na", "do", "od", "za", "po", "ze", "we", "że", "już", "jak", "bez",
    "claude", "cezar", "sesja", "kronika",
}


# ─── EKSTRAKCJA TEMATÓW (encoding/katalogowanie) ──────────────────────────────

def _tematy_z_tekstu(tekst: str, top: int = 12) -> List[str]:
    """Najczęstsze znaczące słowa (≥4 znaki, nie-szum) — 'kod tematyczny' sesji."""
    licznik: Dict[str, int] = {}
    for w in re.findall(r"[a-ząćęłńóśźż0-9_\-]{4,}", tekst.lower()):
        if w in _STOP:
            continue
        licznik[w] = licznik.get(w, 0) + 1
    return [w for w, _ in sorted(licznik.items(), key=lambda x: x[1], reverse=True)[:top]]


# ─── KATALOG NADRZĘDNY (anti-blindness index) ─────────────────────────────────

def zbuduj_katalog(kronika_dir: Path = KRONIKA_DIR,
                   plik_katalogu: Path = KATALOG_PLIK) -> Dict[str, Any]:
    """
    Buduje katalog nadrzędny: każda sesja → {data, rozmiar, tematy, zimna?}.
    To MAPA przeciw „memory blindness": jeden mały plik mówiący CO gdzie jest.
    Zwraca {"sesje": [...], "n": N, "tematy_globalne": [...]}.
    """
    from imperium.biblioteki import kronika_czatu as _kc
    wpisy = []
    globalne: Dict[str, int] = {}
    if kronika_dir.exists():
        for plik in sorted(_kc._pliki_sesji(kronika_dir)):
            tekst = _kc._czytaj_sesje_tekst(plik)
            tematy = _tematy_z_tekstu(tekst)
            for t in tematy:
                globalne[t] = globalne.get(t, 0) + 1
            wpisy.append({
                "sesja": _kc._id_sesji(plik),
                "data": datetime.utcfromtimestamp(plik.stat().st_mtime).strftime("%Y-%m-%d"),
                "rozmiar": plik.stat().st_size,
                "zimna": plik.name.endswith(".gz"),
                "tematy": tematy,
            })
    katalog = {
        "n": len(wpisy),
        "tematy_globalne": [t for t, _ in sorted(globalne.items(), key=lambda x: x[1], reverse=True)[:30]],
        "sesje": wpisy,
    }
    plik_katalogu.parent.mkdir(parents=True, exist_ok=True)
    plik_katalogu.write_text(json.dumps(katalog, ensure_ascii=False, indent=1), encoding="utf-8")
    return katalog


# ─── KOMPRESJA ZIMNEJ WARSTWY (boundless storage, bounded context) ────────────

def kompresuj_zimne(dni: int = 30, kronika_dir: Path = KRONIKA_DIR,
                    teraz: Optional[float] = None) -> Dict[str, Any]:
    """
    Kompresuje sesje starsze niż `dni` (.md → .md.gz). Wciąż przeszukiwalne
    (kronika.szukaj czyta .gz w locie) → zero memory blindness, mniejszy ślad.

    teraz: timestamp odniesienia (do testów; domyślnie now). Zwraca raport z ratio.
    Bezpieczne: kompresuje tylko gdy .gz jeszcze nie istnieje; usuwa .md po sukcesie.
    """
    import time
    raport = {"skompresowane": 0, "bajty_przed": 0, "bajty_po": 0, "pominiete": 0}
    if dni < 0:
        # Ujemne dni kompresowałoby wszystkie ciepłe sesje (nawet aktywną) — zabronione.
        # „starsze niż dni" nie ma sensu dla dni<0; zwracamy pusty raport bezpiecznie.
        raport["ratio"] = 0.0
        return raport
    prog = (teraz if teraz is not None else time.time()) - dni * 86400
    if not kronika_dir.exists():
        return raport
    for plik in sorted(kronika_dir.glob("sesja_*.md")):
        if plik.stat().st_mtime > prog:
            raport["pominiete"] += 1
            continue
        cel = plik.with_suffix(".md.gz")
        if cel.exists():
            raport["pominiete"] += 1
            continue
        surowe = plik.read_bytes()
        with gzip.open(cel, "wb", compresslevel=9) as f:
            f.write(surowe)
        # zachowaj mtime (data sesji = prawda historii, Prawo I)
        import os
        os.utime(cel, (plik.stat().st_atime, plik.stat().st_mtime))
        raport["bajty_przed"] += len(surowe)
        raport["bajty_po"] += cel.stat().st_size
        plik.unlink()
        raport["skompresowane"] += 1
    raport["ratio"] = (raport["bajty_przed"] / raport["bajty_po"]) if raport["bajty_po"] else 0.0
    return raport


# ─── CENSUS — STAN WSZYSTKICH WARSTW (organ widzi całość) ──────────────────────

def census() -> Dict[str, Any]:
    """Jednolity stan 7 warstw pamięci — organ nadrzędny widzi wszystko naraz."""
    wynik: Dict[str, Any] = {}
    try:
        from imperium.biblioteki import srodowisko_pamieci as _sp
        wynik["srodowisko"] = _sp.raport_dostepnosci()
    except Exception:
        wynik["srodowisko"] = {}
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        wynik["dziennik_wpisy"] = len(_dn.wszystkie())
    except Exception:
        wynik["dziennik_wpisy"] = 0
    try:
        from imperium.biblioteki import kronika_czatu as _kc
        wynik["kronika"] = _kc.statystyki()
    except Exception:
        wynik["kronika"] = {}
    try:
        from imperium.biblioteki import rejestr_wizji as _rw
        wynik["wizje"] = len(_rw.wszystkie())
    except Exception:
        wynik["wizje"] = 0
    wynik["katalog_istnieje"] = KATALOG_PLIK.exists()
    return wynik


# Mapa 13 warstw pamięci (jedno źródło prawdy o architekturze — konsolidacja v13).
# (klucz, nazwa, rola, typ CoALA). Kustosz = organ nadrzędny (W7), nie warstwa-dana.
WARSTWY = [
    ("W1", "pamiec_absolutna", "logi transakcji (PnL/MAE/MFE/rezim)", "epizodyczna"),
    # Rola W2 BEZ liczby książek — biblioteka rośnie, więc liczba w stałej musi się zestarzeć
    # (zmierzone 2026-07-17: „42" przy 79 realnych). Żywą liczbę dokłada `mapa()` z bazy RAG.
    ("W2", "RAG (bibliotheca)", "wiedza z książek + encyklopedia (FTS)", "semantyczna"),
    ("W3", "pamiec_sesji", "lekcje z sesji + profil Cezara", "semantyczna"),
    ("W3b", "kronika_czatu", "pełny dialog (re-eksport rosnący)", "epizodyczna"),
    ("W4", "rejestr_wizji", "wizje/decyzje/pomysły/zmiany (scored)", "semantyczna"),
    ("W5", "srodowisko_pamieci", "most chmura↔lokal + manifest", "meta"),
    ("W6", "dziennik_niesmiertelny", "dożywotnia oś czasu (anti-blindness)", "epizodyczna"),
    ("W7", "kustosz_pamieci", "NADRZĘDNY ORGAN: katalog+kompresja+routing", "organ"),
    ("W8", "graf_pamieci", "połączenia neuronów (temporal KG)", "relacyjna"),
    ("W9", "refleksja_pamieci", "sprzeczności + przedawnienia (trustworthy)", "refleksyjna"),
    ("W10", "zapominanie", "learned forgetting (wartościowe, safe)", "meta"),
    ("W11", "pamiec_proceduralna", "runbooki JAK wykonać (CoALA)", "proceduralna"),
    ("W12", "pamiec_robocza", "aktywny cel cyklu (CoALA working)", "robocza"),
    ("W13", "pamiec_proweniencji", "ślad pochodzenia 'skąd to wiemy'", "meta"),
]


def mapa() -> str:
    """Jednolity przegląd warstw pamięci (organ widzi architekturę).

    Liczba warstw z `len(WARSTWY)`, liczba książek z bazy RAG — obie policzone, nie wpisane
    (zmierzone 2026-07-17: nagłówek głosił „v13", gdy Centrum jest w v5 — numer wersji wziął
    się z pomylenia go z liczbą warstw).
    """
    try:
        from imperium.biblioteki.srodowisko_pamieci import ksiazki_w_bazie
        n_ksiazek = ksiazki_w_bazie()
    except Exception:  # noqa: BLE001 — brak bazy/modułu nie może wywrócić mapy
        n_ksiazek = 0
    # W7 (Kustosz) jest ORGANEM, nie warstwą-daną — liczymy warstwy pod nim, bez niego samego.
    # `len(WARSTWY)` dałoby 14 i cicho przekłamało architekturę o jeden.
    n_warstw = len([w for w in WARSTWY if w[0] != "W7"])
    linie = [f"🗺️ MAPA PAMIĘCI IMPERIUM — {n_warstw} warstw pod Kustoszem (organ W7):"]
    for klucz, nazwa, rola, typ in WARSTWY:
        if klucz == "W2" and n_ksiazek:
            rola = f"{rola} — {n_ksiazek} książek zaindeksowanych"
        linie.append(f"   {klucz:4s} {nazwa:24s} [{typ:12s}] {rola}")
    return "\n".join(linie)


# ─── ROUTING ZAPYTAŃ (organ kieruje do właściwej warstwy) ──────────────────────

def szukaj(zapytanie: str, limit: int = 10, rezim_biezacy: str = "") -> List[Dict[str, Any]]:
    """
    Nadrzędne wyszukiwanie: deleguje do cross-layer (6 warstw) + dziennik (W6).
    Jeden punkt wejścia dla całej pamięci Imperium (organ kieruje, warstwy odpowiadają).
    """
    wyniki: List[Dict[str, Any]] = []
    try:
        from imperium.biblioteki import centrum_pamieci as _cp
        wyniki.extend(_cp.szukaj_wszedzie(zapytanie, limit=limit, rezim_biezacy=rezim_biezacy))
    except Exception:
        pass
    try:
        from imperium.biblioteki import dziennik_niesmiertelny as _dn
        for w in _dn.szukaj(zapytanie, limit=5):
            wyniki.append({"warstwa": "dziennik", "score": 0.5,
                           "tresc": " · ".join(w.get("co", []))[:200], "data": w.get("data", "")})
    except Exception:
        pass
    wyniki.sort(key=lambda x: x.get("score", 0), reverse=True)
    return wyniki[:limit]


def raport_startowy() -> str:
    """Zwięzła linia o stanie organu — do podsumowania startowego."""
    c = census()
    kr = c.get("kronika", {})
    return (f"   👑 Kustosz (W7): {kr.get('sesje', 0)} sesji "
            f"({kr.get('zimne', 0)} zimnych/skompresowanych) | "
            f"dziennik: {c.get('dziennik_wpisy', 0)} | "
            f"katalog: {'✅' if c['katalog_istnieje'] else '— (zbuduj: kustosz kataloguj)'}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Kustosz Pamięci — W7 Nadrzędny Organ (W-360 v7)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("census", help="Stan wszystkich warstw")
    sub.add_parser("mapa", help="Mapa 13 warstw pamięci")
    sub.add_parser("kataloguj", help="Zbuduj katalog nadrzędny (anti-blindness)")
    pk = sub.add_parser("kompresuj", help="Skompresuj zimną warstwę (.md→.md.gz)")
    pk.add_argument("--dni", type=int, default=30)
    ps = sub.add_parser("szukaj", help="Nadrzędne wyszukiwanie")
    ps.add_argument("zapytanie")
    args = p.parse_args()

    if args.cmd == "census":
        print(json.dumps(census(), ensure_ascii=False, indent=2))
    elif args.cmd == "mapa":
        print(mapa())
    elif args.cmd == "kataloguj":
        k = zbuduj_katalog()
        print(f"✅ Katalog: {k['n']} sesji, tematy globalne: {', '.join(k['tematy_globalne'][:10])}")
    elif args.cmd == "kompresuj":
        r = kompresuj_zimne(dni=args.dni)
        print(f"✅ Skompresowano {r['skompresowane']} sesji, ratio {r.get('ratio', 0):.1f}× "
              f"({r['bajty_przed']/1e6:.2f}MB → {r['bajty_po']/1e6:.2f}MB), pominięto {r['pominiete']}")
    elif args.cmd == "szukaj":
        for w in szukaj(args.zapytanie):
            print(f"[{w.get('score', 0):.2f}][{w.get('warstwa', '?')}] {w.get('tresc', '')[:90]}")
    else:
        p.print_help()
