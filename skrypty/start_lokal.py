"""
🖥️ START_LOKAL.PY — jednokomendowy rozruch Imperium na maszynie lokalnej (Cezar).

Dla nowicjusza: to JEDNA komenda, która przygotowuje cały lokal po `git pull`.
Robi po kolei (każdy krok osobno, z jasnym komunikatem):

    python skrypty/start_lokal.py

KROKI:
  1. Wykrycie środowiska (chmura vs lokal) — W5 srodowisko_pamieci
  2. Audyt spójności (Prawo XXI) — czy kod=dokumentacja
  3. Budowa katalogu nadrzędnego + grafu pamięci (W7/W8)
  4. Indeks RAG: wektory semantyczne jeśli dostępne (lokal!), inaczej FTS
  5. Mapa pamięci — przegląd 13 warstw (W7 Kustosz)
  6. Wskazówka: jak odpalić paper-trading (skrypty/start.py)

NIE handluje sam (to wymaga kluczy + Twojej decyzji). Przygotowuje pamięć i wiedzę,
żeby lokalny Claude miał PEŁNĄ moc (wektory + pełny dysk przez MCP — patrz docs/START_LOKAL.md).

Bezpieczny: każdy krok w try/except — błąd jednego nie blokuje reszty (raport na końcu).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _krok(nr: int, opis: str):
    print(f"\n{'═' * 64}\n  KROK {nr}: {opis}\n{'═' * 64}")


def _uruchom(cmd: list, opis: str) -> bool:
    """Uruchamia podproces, zwraca True gdy exit 0. Nie rzuca — raportuje."""
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), timeout=600)
        return r.returncode == 0
    except Exception as e:  # noqa: BLE001 — celowo łapiemy wszystko (raport, nie crash)
        print(f"  ⚠️ {opis}: {e}")
        return False


def main() -> int:
    print("🏛️  IMPERIUM — ROZRUCH LOKALNY (start_lokal.py)")
    wyniki = {}

    # 1. Środowisko
    _krok(1, "Wykrycie środowiska (chmura vs lokal)")
    try:
        from imperium.biblioteki import srodowisko_pamieci as sp
        rap = sp.raport_dostepnosci()
        print(f"  🌉 Środowisko: {rap['srodowisko'].upper()} | "
              f"RAG: {rap['rag_tryb']} ({rap['rag_fragmenty']} frag.)")
        wyniki["srodowisko"] = rap["srodowisko"]
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠️ {e}")

    # 2. Audyt spójności
    _krok(2, "Audyt spójności (Prawo XXI)")
    wyniki["audyt"] = _uruchom([sys.executable, "narzedzia/audyt_spojnosci.py"], "audyt")

    # 3. Katalog + graf pamięci
    _krok(3, "Budowa katalogu nadrzędnego (W7) + grafu pamięci (W8)")
    wyniki["katalog"] = _uruchom(
        [sys.executable, "-m", "imperium.biblioteki.kustosz_pamieci", "kataloguj"], "katalog")
    wyniki["graf"] = _uruchom(
        [sys.executable, "-m", "imperium.biblioteki.graf_pamieci", "buduj"], "graf")

    # 4. Indeks RAG (wektory lokalnie!)
    _krok(4, "Indeks RAG — wektory semantyczne (lokal) lub FTS (fallback)")
    indeksuj = ROOT / "narzedzia" / "rag" / "indeksuj.py"
    if indeksuj.exists():
        ok = _uruchom([sys.executable, str(indeksuj)], "RAG wektory")
        if not ok:
            print("  ↪️ Wektory niedostępne — próbuję tryb FTS (bez modelu)...")
            ok = _uruchom([sys.executable, str(indeksuj), "--bez-wektorow"], "RAG FTS")
        wyniki["rag"] = ok
    else:
        print("  ⚠️ narzedzia/rag/indeksuj.py nie znaleziony")
        wyniki["rag"] = False

    # 5. Mapa pamięci
    _krok(5, "Mapa pamięci — 13 warstw pod Kustoszem")
    _uruchom([sys.executable, "-m", "imperium.biblioteki.kustosz_pamieci", "mapa"], "mapa")

    # 6. Podsumowanie + wskazówka
    _krok(6, "Gotowe — podsumowanie")
    for k, v in wyniki.items():
        znak = "✅" if v else ("⚠️" if v is False else "ℹ️")
        print(f"  {znak} {k}: {v}")
    print("\n  ▶️  Paper-trading (symulacja, zero kasy): python skrypty/start.py")
    print("  📖  Pełny przewodnik lokalny: docs/START_LOKAL.md")
    print("  🔓  Wektory/pełny dysk/MCP: sekcja 'Dodatki tylko lokal' w docs/START_LOKAL.md")
    return 0 if all(v for v in wyniki.values() if isinstance(v, bool)) else 1


if __name__ == "__main__":
    sys.exit(main())
