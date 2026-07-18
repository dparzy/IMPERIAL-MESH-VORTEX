"""
🌉 Most Chmura↔Lokal — W5 Centrum Pamięci W-360 v5 (UNIKAT IMPERIUM)

PROBLEM (audyt Prawo XV, 2026-06-26): pamięć nie rozróżnia środowiska.
  • W chmurze (Claude Code na webie): kontener efemeryczny, baza RAG (82 MB) i logi
    są gitignore'owane → znikają przy każdym świeżym kontenerze. Wektory semantyczne
    NIE działają (proxy blokuje huggingface.co → model embeddings nie wstaje).
  • Lokalnie (Twój komputer): trwały dysk, brak limitu sieci → wektory działają,
    logi przeżywają, można odbudować pełny RAG.

ROZWIĄZANIE: ten moduł wykrywa środowisko i RAPORTUJE co działa GDZIE, dając:
  1. `wykryj_srodowisko()` — "chmura" | "lokal" (z CLAUDE_CODE_REMOTE + heurystyki)
  2. `raport_dostepnosci()` — które warstwy pamięci są żywe TU i TERAZ (twardy pomiar)
  3. `manifest_pamieci()` — pełny stan WSZYSTKICH warstw: jeden raport, który lokalny
     Claude czyta po `git pull`, by wiedzieć co ma, a czego musi dobudować
  4. `instrukcja_lokal()` — co zrobić lokalnie, by odblokować pełną moc (wektory)

UNIKAT (żaden konkurent tego nie ma — Mem0/Zep/Letta/A-Mem są środowiskowo ślepe):
  pamięć Imperium jest ŚRODOWISKOWO-ADAPTACYJNA. W chmurze działa w trybie FTS
  (przeżywa przez git: kronika+lekcje+wizje commitowane), lokalnie UPGRADE do wektorów
  semantycznych. Ta sama pamięć, dwa tryby — most jest git + ten manifest.

Łączy się z UNIKATEM reżimowym (centrum_pamieci): pamięć jest reżimowo-świadoma
ORAZ środowiskowo-adaptacyjna. To dwa wymiary, których konkurencja nie ma.

Bez zależności zewnętrznych (stdlib: os, sqlite3, pathlib) → działa wszędzie.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent.parent.parent

# Ścieżki warstw pamięci (jedno źródło prawdy o lokalizacjach)
RAG_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"
KRONIKA_DIR = ROOT / "bibliotheca_ulpia" / "dane" / "kronika"
LEKCJE_PLIK = ROOT / "docs" / "PAMIEC_SESJI.md"
WIZJE_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "wizje_i_decyzje.jsonl"
PROFIL_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "PROFIL_CEZARA.md"
LOGI_DIR = ROOT / "imperium" / "biblioteki" / "pamiec" / "logi"
REFLEKSYJNA_DIR = ROOT / "logs"


def wykryj_srodowisko() -> str:
    """
    Zwraca "chmura" gdy działamy w zdalnym kontenerze Claude Code (web/CI),
    "lokal" gdy na trwałym dysku Cezara.

    Kolejność sygnałów (od najsilniejszego):
      1. IMPERIUM_SRODOWISKO — jawne, TRWAŁE nadpisanie Cezara (setx raz na maszynie).
         Rozkaz stały 2026-07-11: domyślnie pracujemy na lokalu danych z dysku.
      2. CLAUDE_CODE_REMOTE=true — twardy sygnał zdalnego harnessa (web/CI).
      3. Windows → LOKAL. Kontenery chmury są Linux; laptop Cezara to Windows.
         To naprawia fałszywy alarm: harness ustawia CLAUDE_ENV_FILE także w hooku
         na lokalu, przez co baner startowy mylnie pokazywał CHMURA (2026-07-11).
      4. CLAUDE_ENV_FILE (tylko nie-Windows) — heurystyka zapasowa dla Linux-chmury.
    """
    override = os.getenv("IMPERIUM_SRODOWISKO", "").strip().lower()
    if override in ("lokal", "chmura"):
        return override
    if os.getenv("CLAUDE_CODE_REMOTE", "").lower() == "true":
        return "chmura"
    # Windows = maszyna Cezara (kontenery chmury Claude Code są Linux) → zawsze lokal.
    if sys.platform.startswith("win"):
        return "lokal"
    # Heurystyka zapasowa (Linux): harness web ustawia CLAUDE_ENV_FILE.
    if os.getenv("CLAUDE_ENV_FILE"):
        return "chmura"
    return "lokal"


def _wektory_w_bazie() -> int:
    """Ile wektorów semantycznych jest w bazie RAG (0 = tylko FTS)."""
    if not RAG_BAZA.exists():
        return 0
    try:
        conn = sqlite3.connect(str(RAG_BAZA))
        try:
            return conn.execute("SELECT COUNT(*) FROM wektory").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def _fragmenty_w_bazie() -> int:
    """Ile fragmentów (chunków) jest zaindeksowanych w RAG."""
    if not RAG_BAZA.exists():
        return 0
    try:
        conn = sqlite3.connect(str(RAG_BAZA))
        try:
            return conn.execute("SELECT COUNT(*) FROM fragmenty").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def fragmenty_w_bazie() -> int:
    """Ile fragmentów RAG — publiczny wrapper (Tabularium/dokumenty liczą stąd, W15).

    Liczba rośnie z każdą dodaną książką/dokumentem — wpisana ręcznie zestarzeje się
    (zmierzone 2026-07-18: PLAN_TIRO podawał „27 959" przy 29 699 realnych)."""
    return _fragmenty_w_bazie()


def ksiazki_w_bazie() -> int:
    """Ile KSIĄŻEK (BIB-*) jest zaindeksowanych w RAG — liczone, nigdy zaszyte.

    JEDNO źródło prawdy dla całego Imperium (Prawo XVI): kustosz (W2), alarmy, instrukcja
    lokalna i dokumenty czytają stąd. Zmierzone 2026-07-17: liczba „42" była ZASZYTA w
    czterech miejscach kodu i w MAPA_PAMIECI, przy 79 książkach realnie w bazie — biblioteka
    rośnie (BIB-070..274 w planie), więc każda wpisana ręcznie liczba musi się zestarzeć.
    Liczymy źródła w bazie, nie pliki na dysku: książka niezaindeksowana nie jest wiedzą W2.
    """
    if not RAG_BAZA.exists():
        return 0
    try:
        conn = sqlite3.connect(str(RAG_BAZA))
        try:
            return conn.execute(
                "SELECT COUNT(DISTINCT zrodlo) FROM fragmenty WHERE zrodlo LIKE 'BIB-%'"
            ).fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def _model_embeddings_dostepny() -> bool:
    """Czy sentence-transformers + model są dostępne (lokal: tak, chmura: zwykle nie)."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def raport_dostepnosci() -> Dict[str, Any]:
    """
    Twardy pomiar: które warstwy pamięci są ŻYWE w tym środowisku TERAZ.
    Nie zgaduje — liczy pliki, wiersze bazy, obecność modułów (Prawo XIX).
    """
    wektory = _wektory_w_bazie()
    fragmenty = _fragmenty_w_bazie()
    kronika_n = len(list(KRONIKA_DIR.glob("sesja_*.md"))) if KRONIKA_DIR.is_dir() else 0
    wizje_n = 0
    if WIZJE_PLIK.exists():
        wizje_n = sum(1 for ln in WIZJE_PLIK.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip())
    logi_n = len(list(LOGI_DIR.glob("*.jsonl"))) if LOGI_DIR.is_dir() else 0
    refleksje = REFLEKSYJNA_DIR.is_dir() and any(REFLEKSYJNA_DIR.glob("*.jsonl"))

    return {
        "srodowisko": wykryj_srodowisko(),
        "rag_baza_istnieje": RAG_BAZA.exists(),
        "rag_fragmenty": fragmenty,
        "rag_wektory": wektory,
        "rag_tryb": "wektory+FTS" if wektory > 0 else ("FTS" if fragmenty > 0 else "brak"),
        "model_embeddings": _model_embeddings_dostepny(),
        "kronika_sesje": kronika_n,
        "wizje_wpisy": wizje_n,
        "logi_trade": logi_n,
        "refleksje_aktywne": bool(refleksje),
        "lekcje_plik": LEKCJE_PLIK.exists(),
        "profil_cezara": PROFIL_PLIK.exists(),
    }


def _alarmy(rap: Dict[str, Any]) -> List[str]:
    """Czerwone alarmy UTRATY POTENCJAŁU (Prawo XV) dla bieżącego środowiska."""
    alarmy = []
    if rap["rag_baza_istnieje"] and rap["rag_wektory"] == 0:
        alarmy.append(
            "🚨 RAG działa tylko w trybie FTS (wektory=0) — semantyka martwa. "
            + ("W chmurze to oczekiwane (proxy blokuje model). Lokalnie: odbuduj wektory."
               if rap["srodowisko"] == "chmura"
               else "LOKALNIE TO STRATA — uruchom: python narzedzia/rag/indeksuj.py (z wektorami).")
        )
    if not rap["rag_baza_istnieje"]:
        alarmy.append(
            "🚨 Brak bazy RAG — CAŁA wiedza z książek niedostępna. "
            "Odbuduj: python narzedzia/rag/indeksuj.py --korpus wszystko"
        )
    if rap["srodowisko"] == "lokal" and not rap["model_embeddings"]:
        alarmy.append(
            "🚨 LOKAL bez sentence-transformers — wektory niemożliwe. "
            "Zainstaluj: pip install sentence-transformers"
        )
    return alarmy


def manifest_pamieci() -> str:
    """
    Pełny manifest stanu pamięci — JEDEN raport, który lokalny Claude czyta po
    `git pull`, by wiedzieć co ma, a co musi dobudować. To rdzeń mostu chmura↔lokal.
    """
    rap = raport_dostepnosci()
    srod = rap["srodowisko"].upper()
    linie = [
        f"🌉 MANIFEST PAMIĘCI W-360 v5 — środowisko: {srod}",
        "",
        "   Warstwy przeżywające przez git (działają WSZĘDZIE):",
        f"   • W3  lekcje (PAMIEC_SESJI.md): {'✅' if rap['lekcje_plik'] else '❌'}",
        f"   • W3b kronika dialogu: {rap['kronika_sesje']} sesji",
        f"   • W4  wizje/decyzje/pomysły: {rap['wizje_wpisy']} wpisów",
        f"   • Profil Cezara: {'✅' if rap['profil_cezara'] else '❌'}",
        "",
        "   Warstwy zależne od środowiska:",
        f"   • W2  RAG: {rap['rag_tryb']} ({rap['rag_fragmenty']} fragmentów, {rap['rag_wektory']} wektorów)",
        f"   • W1  logi trade: {rap['logi_trade']} plików",
        f"   • Refleksje rynkowe: {'✅ aktywne' if rap['refleksje_aktywne'] else '— brak (gitignore/logs)'}",
        f"   • Model embeddings (wektory): {'✅ dostępny' if rap['model_embeddings'] else '❌ niedostępny'}",
    ]
    alarmy = _alarmy(rap)
    if alarmy:
        linie.append("")
        linie.append("   ⚠️ UTRATA POTENCJAŁU (Prawo XV):")
        for a in alarmy:
            linie.append(f"   {a}")
    return "\n".join(linie)


def instrukcja_lokal() -> str:
    """
    Konkretne kroki, by lokalny Claude/Cezar odblokował PEŁNĄ moc pamięci
    (wektory semantyczne — niemożliwe w chmurze przez blokadę proxy).
    """
    return (
        "🖥️ ODBLOKOWANIE PEŁNEJ PAMIĘCI LOKALNIE:\n"
        "   1. git pull origin claude/sleepy-fermi-dsdE4   # cała pamięć z chmury\n"
        "   2. pip install -r requirements.txt              # w tym sentence-transformers\n"
        f"   3. python narzedzia/rag/indeksuj.py --korpus wszystko  # wektory z {ksiazki_w_bazie()} książek + kronika\n"
        "   4. (opcjonalnie) setx DEEPSEEK_API_KEY \"...\"   # auto-lekcja po sesjach\n"
        "   → po tym: szukaj_wszedzie() działa semantycznie (wektory), nie tylko keyword (FTS).\n"
        "   Most: git niesie dialog+lekcje+wizje; wektory budujesz lokalnie z repo."
    )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Most Chmura↔Lokal — W5 W-360 v5")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("manifest", help="Pełny manifest stanu pamięci")
    sub.add_parser("srodowisko", help="Wykryj środowisko (chmura/lokal)")
    sub.add_parser("dostepnosc", help="Raport dostępności warstw (JSON)")
    sub.add_parser("lokal", help="Instrukcja odblokowania pełnej mocy lokalnie")
    args = p.parse_args()

    if args.cmd == "srodowisko":
        print(wykryj_srodowisko())
    elif args.cmd == "dostepnosc":
        import json
        print(json.dumps(raport_dostepnosci(), indent=2, ensure_ascii=False))
    elif args.cmd == "lokal":
        print(instrukcja_lokal())
    else:  # manifest domyślnie
        print(manifest_pamieci())
