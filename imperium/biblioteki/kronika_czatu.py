"""
📜 Kronika Czatu (W-360) — trwała pamięć CAŁEJ rozmowy między sesjami.

PROBLEM (Cezar, 2026-06-22): „abyśmy pamiętali wszystkie nasze rozmowy i cały czat
— lokalnie i w chmurze". Claude Code zapisuje transkrypty w ~/.claude/projects/
<projekt>/*.jsonl, ale ten katalog jest POZA repo i GINIE w świeżym kontenerze
chmury. Hermes Agent rozwiązuje to przez session_search po SQLite (~/.hermes/state.db).
My robimy odpowiednik, ale lepiej dla nas: destylujemy transkrypty do REPO (git),
więc historia płynie razem z kodem na każdą maszynę (lokal i chmura).

CO ROBI:
  • destyluj_jsonl()  — z surowego transkryptu wyciąga sam dialog (user + tekst
    asystenta), odrzuca szum tool_use/tool_result; redaguje to, co wygląda na klucz API.
  • eksportuj()       — zapisuje destylat per-sesja do bibliotheca_ulpia/dane/kronika/
    (korpus RAG `dane` → przeszukiwalny FTS5/wektory). Przyrostowy: pomija już zapisane.
  • szukaj()          — pełnotekstowe przeszukanie kroniki (gdy RAG niedostępny).

WARSTWA PAMIĘCI: to rozszerzenie Warstwy 3 (ciągłość sesji). pamiec_sesji.py trzyma
DESTYLAT (lekcje, mapa); kronika_czatu trzyma SUROWY DIALOG (pełny zapis), tak jak
u Hermesa MEMORY.md (rdzeń) ⊥ session_search (pełna historia).

Markdown w git (świadomie): czytelny dla Cezara, wersjonowany, indeksowany w RAG.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Iterator

ROOT = Path(__file__).resolve().parent.parent.parent
CEL_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "kronika"

# Katalog transkryptów Claude Code dla TEGO projektu (ścieżka = repo z '/' → '-').
_SLUG = str(ROOT).replace("/", "-")
ZRODLO_DOMYSLNE = Path.home() / ".claude" / "projects" / _SLUG

# Redakcja sekretów (Prawo Bezpieczeństwa: klucze NIGDY w repo). Wzorce typowych kluczy.
_WZORY_SEKRETOW = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),               # OpenAI/DeepSeek styl
    re.compile(r"\b[A-Za-z0-9]{32,}\b"),              # długie tokeny hex/base
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*\S+"),
]


def _redaguj(tekst: str) -> str:
    """Zamienia ciągi wyglądające na klucz API na [ZREDAGOWANO] — bezpieczeństwo."""
    for wzor in _WZORY_SEKRETOW:
        tekst = wzor.sub("[ZREDAGOWANO]", tekst)
    return tekst


def _tekst_z_tresci(c) -> str:
    """Wyciąga czysty tekst z pola content (str lub lista bloków)."""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(b.get("text", "") for b in c
                       if isinstance(b, dict) and b.get("type") == "text")
    return ""


def destyluj_jsonl(sciezka: Path) -> List[Dict[str, str]]:
    """
    Z transkryptu JSONL zwraca [{"rola": "user|assistant", "tekst": "..."}]
    — tylko realny dialog, bez tool_use/tool_result/meta. Sekrety zredagowane.
    """
    wynik: List[Dict[str, str]] = []
    if not sciezka.exists():
        return wynik
    for line in sciezka.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            o = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        m = o.get("message") or {}
        rola = m.get("role") or o.get("type")
        if rola not in ("user", "assistant"):
            continue
        txt = _tekst_z_tresci(m.get("content")).strip()
        if txt:
            wynik.append({"rola": rola, "tekst": _redaguj(txt)})
    return wynik


def _na_markdown(dialog: List[Dict[str, str]], id_sesji: str) -> str:
    """Składa dialog w czytelny markdown (jeden plik = jedna sesja)."""
    linie = [f"# Kronika sesji {id_sesji}", ""]
    for w in dialog:
        kto = "🧑 Cezar" if w["rola"] == "user" else "🏛️ Claude"
        linie.append(f"## {kto}")
        linie.append(w["tekst"])
        linie.append("")
    return "\n".join(linie)


def _pliki_zrodlowe(zrodlo: Path) -> Iterator[Path]:
    if zrodlo.exists():
        yield from sorted(zrodlo.glob("*.jsonl"))


def eksportuj(zrodlo: Path = ZRODLO_DOMYSLNE, cel: Path = CEL_DOMYSLNY,
              tylko_nowe: bool = True, min_wiadomosci: int = 2) -> Dict[str, int]:
    """
    Destyluje wszystkie transkrypty z `zrodlo` do `cel` (jeden .md per sesja).
    tylko_nowe=True → pomija sesje już wyeksportowane (przyrostowy, jak RAG --tylko-nowe).
    Zwraca statystyki {sesje, zapisane, pominiete, wiadomosci}.
    """
    cel.mkdir(parents=True, exist_ok=True)
    stat = {"sesje": 0, "zapisane": 0, "pominiete": 0, "wiadomosci": 0}
    for src in _pliki_zrodlowe(zrodlo):
        stat["sesje"] += 1
        id_sesji = src.stem
        cel_plik = cel / f"sesja_{id_sesji}.md"
        if tylko_nowe and cel_plik.exists():
            stat["pominiete"] += 1
            continue
        dialog = destyluj_jsonl(src)
        if len(dialog) < min_wiadomosci:
            stat["pominiete"] += 1
            continue
        cel_plik.write_text(_na_markdown(dialog, id_sesji), encoding="utf-8")
        stat["zapisane"] += 1
        stat["wiadomosci"] += len(dialog)
    return stat


def szukaj(zapytanie: str, cel: Path = CEL_DOMYSLNY,
           limit: int = 20) -> List[Dict[str, str]]:
    """
    Pełnotekstowe przeszukanie kroniki (fallback gdy RAG niedostępny).
    Zwraca [{"sesja": id, "fragment": "...linia z trafieniem..."}], max `limit`.
    """
    q = zapytanie.lower()
    trafienia: List[Dict[str, str]] = []
    if not cel.exists():
        return trafienia
    for plik in sorted(cel.glob("sesja_*.md")):
        for linia in plik.read_text(encoding="utf-8", errors="ignore").splitlines():
            if q in linia.lower():
                trafienia.append({"sesja": plik.stem.replace("sesja_", ""),
                                  "fragment": linia.strip()[:300]})
                if len(trafienia) >= limit:
                    return trafienia
    return trafienia


def statystyki(cel: Path = CEL_DOMYSLNY) -> Dict[str, int]:
    """Ile sesji i znaków jest już w kronice (do raportu startowego)."""
    if not cel.exists():
        return {"sesje": 0, "znaki": 0}
    pliki = list(cel.glob("sesja_*.md"))
    znaki = sum(p.stat().st_size for p in pliki)
    return {"sesje": len(pliki), "znaki": znaki}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Kronika czatu Imperium (W-360)")
    sub = ap.add_subparsers(dest="cmd")
    p_eksp = sub.add_parser("eksportuj", help="destyluj transkrypty do repo")
    p_eksp.add_argument("--wszystko", action="store_true", help="nadpisz też istniejące")
    p_szuk = sub.add_parser("szukaj", help="przeszukaj kronikę")
    p_szuk.add_argument("zapytanie", nargs="+")
    sub.add_parser("statystyki", help="ile sesji w kronice")
    args = ap.parse_args()

    if args.cmd == "eksportuj":
        s = eksportuj(tylko_nowe=not args.wszystko)
        print(f"📜 Kronika: {s['zapisane']} zapisane, {s['pominiete']} pominięte, "
              f"{s['wiadomosci']} wiadomości z {s['sesje']} sesji.")
    elif args.cmd == "szukaj":
        for t in szukaj(" ".join(args.zapytanie)):
            print(f"[{t['sesja'][:8]}] {t['fragment']}")
    elif args.cmd == "statystyki":
        st = statystyki()
        print(f"📜 Kronika: {st['sesje']} sesji, {st['znaki']/1e6:.2f} MB tekstu.")
    else:
        ap.print_help()
