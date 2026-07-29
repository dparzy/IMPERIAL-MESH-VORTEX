#!/usr/bin/env python3
"""
🔎 QUAESITOR — Śledczy Biblioteki: mierzy JAKOŚĆ WYSZUKIWANIA w Bibliotheca-RAG.

Rzymski *quaesitor* = urzędnik prowadzący śledztwo (od `quaerere` — szukać, badać).
Tutaj: organ, który po raz pierwszy pyta RAG o rzecz, o którą nigdy go nie pytaliśmy —
*czy on w ogóle znajduje to, czego szukamy?*

POWÓD POWSTANIA (audyt RAG 2026-07-29, wada #8 z ośmiu zmierzonych):
Imperium miało 37 331 fragmentów, dwa tryby wyszukiwania i cztery moduły-konsumentów —
i ZERO pomiarów trafności. Każde zdanie o tym, że „RAG działa dobrze", było wiarą.
Nie da się zdecydować o wektorach, RRF ani rerankingu bez punktu odniesienia, więc
QUAESITOR jest PIERWSZY, a nie ostatni (ZASADA WERYFIKACJI: pomiar przed wdrożeniem).

CO MIERZY — *known-item retrieval*: pytanie ma znaną książkę-odpowiedź (jedną z kilku
dopuszczalnych), sprawdzamy, czy wyszukiwarka postawi ją w pierwszej k-tce.
    recall@k — ułamek pytań, dla których poprawne źródło jest w TOP-k
    MRR       — średnia z 1/pozycja pierwszego trafnego źródła (kara za niską pozycję)

DWIE KLASY PYTAŃ — i to jest sedno konstrukcji, nie ozdoba:
    DOSŁOWNA  — pytanie używa TERMINU, którym posługuje się książka („VPIN flow toxicity").
                Tu BM25 jest u siebie: zgodność słów jest zgodnością znaczeń.
    OPISOWA   — pytanie OPISUJE pojęcie, nie nazywając go („how to tell if the people
                trading against me know something I don't"). Tu BM25 jest strukturalnie
                ślepy — nie ma wspólnych słów, mimo że jest wspólny sens.

RÓŻNICA MIĘDZY TYMI KLASAMI JEST ZMIERZONYM SUFITEM ZYSKU Z WEKTORÓW. Jeśli klasa
opisowa wypada tak samo dobrze jak dosłowna — embeddingi kupią nam niewiele i decyzja
R5 pada sama. Jeśli opisowa leży — wiemy, ile dokładnie leży na stole. Tak wygląda
rozstrzygnięcie z pomiaru zamiast z opinii (Prawo XVI).

UCZCIWOŚĆ ZBIORU (inaczej miara kłamie):
- Pytania pisane Z WIEDZY DZIEDZINOWEJ, nigdy przez zaglądanie do fragmentów w bazie —
  skopiowanie frazy z chunku zrobiłoby BM25 sztuczny wynik bliski 100%.
- Cel to ZBIÓR dopuszczalnych źródeł, nie jedno: „adverse selection" stoi u O'Hary
  i u Harrisa naraz, więc karanie za trafienie w drugą byłoby karą za prawdę.
- Pytania, których cel NIE JEST zaindeksowany, są POMIJANE i liczone osobno —
  miara wobec celu nieosiągalnego to nie porażka wyszukiwarki, tylko braki korpusu
  (93 z 208 książek poza indeksem, stan 2026-07-29).

Użycie:
    python -m narzedzia.rag.quaesitor                      # FTS, topk 10, obie składnie
    python -m narzedzia.rag.quaesitor --tryb hybrid        # gdy pojawią się wektory
    python -m narzedzia.rag.quaesitor --szczegoly          # pytanie po pytaniu
    python -m narzedzia.rag.quaesitor --ledger             # dopisz POMIAR do CODEX
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))

DOMYSLNA_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"

_RE_BIB = re.compile(r"^(BIB-\d+)")
_RE_SLOWO = re.compile(r"[A-Za-z0-9]+")

# ── ZBIÓR EWALUACYJNY ────────────────────────────────────────────────────────
# `zrodla_ok` — identyfikatory BIB, z których KAŻDY jest poprawną odpowiedzią.
# `po_co`     — dlaczego akurat te źródła; bez tego zbiór gnije, bo nikt po latach
#               nie odtworzy, czy trafienie w inną książkę było błędem, czy nie.

ZBIOR: tuple[dict, ...] = (
    # ── KLASA DOSŁOWNA — pytanie mówi językiem książki ───────────────────────
    dict(id="D01", klasa="doslowna", pytanie="VPIN volume synchronized probability of informed trading flow toxicity",
         zrodla_ok=("BIB-071", "BIB-007"), po_co="VPIN to praca Easley-Lopez de Prado-O'Hara; AFML omawia ją wtórnie"),
    dict(id="D02", klasa="doslowna", pytanie="triple barrier labeling meta-labeling sample weights",
         zrodla_ok=("BIB-007",), po_co="triple barrier i meta-labeling to autorskie pojęcia AFML"),
    dict(id="D03", klasa="doslowna", pytanie="fundamental law of active management information ratio breadth",
         zrodla_ok=("BIB-025",), po_co="prawo fundamentalne to Grinold & Kahn"),
    dict(id="D04", klasa="doslowna", pytanie="implementation shortfall transaction cost analysis market impact model",
         zrodla_ok=("BIB-022", "BIB-043", "BIB-020"), po_co="Kissell to podręcznik kosztów; Cartea i Harris omawiają impact"),
    dict(id="D05", klasa="doslowna", pytanie="GARCH conditional heteroskedasticity volatility clustering estimation",
         zrodla_ok=("BIB-031", "BIB-008"), po_co="Tsay to kanon GARCH; Sinclair stosuje do zmienności opcyjnej"),
    dict(id="D06", klasa="doslowna", pytanie="Hurst exponent long memory fractal multifractal price series",
         zrodla_ok=("BIB-009",), po_co="Mandelbrot to źródło fraktalnego ujęcia rynków"),
    dict(id="D07", klasa="doslowna", pytanie="value at risk backtesting exceptions confidence level",
         zrodla_ok=("BIB-042",), po_co="Jorion to podręcznik VaR"),
    dict(id="D08", klasa="doslowna", pytanie="Ito lemma stochastic differential equation Brownian motion martingale",
         zrodla_ok=("BIB-065", "BIB-066"), po_co="Shreve I/II to kanon rachunku stochastycznego"),
    dict(id="D09", klasa="doslowna", pytanie="limit order book depth queue position market maker inventory",
         zrodla_ok=("BIB-043", "BIB-044", "BIB-020", "BIB-032"), po_co="mikrostruktura księgi zleceń — cztery kanoniczne pozycje"),
    dict(id="D10", klasa="doslowna", pytanie="proximal policy optimization clipped surrogate objective advantage estimation",
         zrodla_ok=("BIB-111",), po_co="PPO to praca Schulmana"),
    dict(id="D11", klasa="doslowna", pytanie="LoRA low rank adaptation frozen weights fine tuning adapters",
         zrodla_ok=("BIB-086", "BIB-087"), po_co="LoRA (Hu) i QLoRA (Dettmers)"),
    dict(id="D12", klasa="doslowna", pytanie="scaled dot product self attention multi head transformer encoder",
         zrodla_ok=("BIB-070",), po_co="Attention Is All You Need"),
    dict(id="D13", klasa="doslowna", pytanie="strictly proper scoring rule Brier score calibration sharpness",
         zrodla_ok=("BIB-079",), po_co="Gneiting-Raftery to źródło reguł skoringowych"),
    dict(id="D14", klasa="doslowna", pytanie="constant product automated market maker concentrated liquidity impermanent loss",
         zrodla_ok=("BIB-078", "BIB-077"), po_co="Uniswap v3 core; Flash Boys 2.0 dotyka AMM i MEV"),
    dict(id="D15", klasa="doslowna", pytanie="prospect theory loss aversion anchoring availability heuristic",
         zrodla_ok=("BIB-017", "BIB-061"), po_co="Kahneman i Thaler — kanon ekonomii behawioralnej"),

    # ── KLASA OPISOWA — pytanie opisuje sens, nie nazywa go ──────────────────
    dict(id="O01", klasa="opisowa", pytanie="how do I tell whether the people trading against me know something I do not",
         zrodla_ok=("BIB-071", "BIB-032", "BIB-044", "BIB-020"), po_co="opis selekcji negatywnej / toksyczności przepływu bez użycia tych słów"),
    dict(id="O02", klasa="opisowa", pytanie="a way to mark past examples that respects when the position would already be closed",
         zrodla_ok=("BIB-007",), po_co="opis triple barrier bez nazwy"),
    dict(id="O03", klasa="opisowa", pytanie="why does a rule that looked excellent on old data stop working on new data",
         zrodla_ok=("BIB-007", "BIB-023", "BIB-048"), po_co="opis przeuczenia i selekcji na historii bez słowa overfitting"),
    dict(id="O04", klasa="opisowa", pytanie="what does it cost me to push a large order into a thin market in a hurry",
         zrodla_ok=("BIB-022", "BIB-043", "BIB-020"), po_co="opis wpływu na cenę i kosztu pośpiechu"),
    dict(id="O05", klasa="opisowa", pytanie="why do big price swings arrive in bunches instead of being spread out evenly",
         zrodla_ok=("BIB-031", "BIB-009", "BIB-008"), po_co="opis grupowania zmienności bez słowa GARCH"),
    dict(id="O06", klasa="opisowa", pytanie="how can a machine get better at a task purely by trying things and being rewarded",
         zrodla_ok=("BIB-067", "BIB-108", "BIB-109", "BIB-113"), po_co="opis uczenia ze wzmocnieniem bez nazwy"),
    dict(id="O07", klasa="opisowa", pytanie="making a big model small enough to run on a weak computer without losing much quality",
         zrodla_ok=("BIB-098", "BIB-088", "BIB-087"), po_co="opis kwantyzacji i destylacji bez tych słów"),
    dict(id="O08", klasa="opisowa", pytanie="teaching a model to do what people actually want by showing it which answer they prefer",
         zrodla_ok=("BIB-096", "BIB-097", "BIB-091"), po_co="opis RLHF/DPO bez skrótów"),
    dict(id="O09", klasa="opisowa", pytanie="why do traders keep repeating the same mistakes even when they know better",
         zrodla_ok=("BIB-016", "BIB-050", "BIB-004", "BIB-052"), po_co="psychologia dyscypliny — cztery pozycje wprost o tym"),
    dict(id="O10", klasa="opisowa", pytanie="how do crowds push prices far above any sensible value and then collapse",
         zrodla_ok=("BIB-059", "BIB-063", "BIB-062", "BIB-060"), po_co="manie i krachy — opis bez słowa bubble"),
    dict(id="O11", klasa="opisowa", pytanie="how do I check whether a forecast is honest about how sure it claims to be",
         zrodla_ok=("BIB-079", "BIB-072"), po_co="opis kalibracji prognozy bez słowa calibration"),
    dict(id="O12", klasa="opisowa", pytanie="splitting historical data so that the test cannot peek at answers it should not see",
         zrodla_ok=("BIB-007", "BIB-023", "BIB-072"), po_co="opis purged CV / walk-forward bez nazw"),
    dict(id="O13", klasa="opisowa", pytanie="what happens to a country when the money it owes grows larger than it can carry",
         zrodla_ok=("BIB-056", "BIB-058", "BIB-064"), po_co="cykle długu — Dalio i Reinhart-Rogoff"),
    dict(id="O14", klasa="opisowa", pytanie="a model where every point learns from the points it is connected to",
         zrodla_ok=("BIB-100", "BIB-101", "BIB-103", "BIB-104", "BIB-102"), po_co="opis sieci grafowych bez słowa graph neural network"),
    dict(id="O15", klasa="opisowa", pytanie="why rare enormous events matter more for survival than the typical day",
         zrodla_ok=("BIB-041", "BIB-009"), po_co="grube ogony i ryzyko ruiny — Taleb i Mandelbrot"),
)


def _bib(zrodlo: str) -> str:
    """'BIB-007_Lopez-de-Prado_....epub' → 'BIB-007'. Nie-BIB → ''."""
    m = _RE_BIB.match(zrodlo or "")
    return m.group(1) if m else ""


def _fts_or(zapytanie: str) -> str:
    """Składnia OR — DELEGUJE do `szukaj.sanityzuj_fts` (naprawa u źródła 2026-07-30).

    Ta funkcja była TRZECIĄ kopią tej samej logiki (obok `bibliotekarz._fts_bezpieczne`
    i braku w `mcp_server`). Pomiar z pierwszego biegu pokazał, ile kosztowało
    rozproszenie: ścieżka bez sanityzacji miała recall@5 16,7% zamiast 66,7%.
    Zostaje jako nazwa, implementacja jest już w jednym miejscu.
    """
    from szukaj import sanityzuj_fts  # type: ignore[import]
    return sanityzuj_fts(zapytanie, "or")


def zaindeksowane(baza: Path = DOMYSLNA_BAZA) -> set[str]:
    """Zbiór identyfikatorów BIB obecnych w indeksie (do pomijania celów nieosiągalnych)."""
    if not baza.exists():
        return set()
    conn = sqlite3.connect(str(baza))
    try:
        return {b for b in (_bib(r[0]) for r in conn.execute("SELECT DISTINCT zrodlo FROM fragmenty")) if b}
    finally:
        conn.close()


def _pozycja_trafienia(wyniki, zrodla_ok: tuple[str, ...]) -> int | None:
    """1-indeksowana pozycja PIERWSZEGO wyniku z dopuszczalnego źródła; None = brak."""
    for i, w in enumerate(wyniki, 1):
        if _bib(getattr(w, "zrodlo", "")) in zrodla_ok:
            return i
    return None


def ocen(tryb: str = "fts", topk: int = 10, skladnia: str = "and",
         baza: Path = DOMYSLNA_BAZA, zbior: tuple[dict, ...] = ZBIOR,
         postep: bool = False) -> dict:
    """Przepuszcza zbiór przez wyszukiwarkę i liczy recall@k oraz MRR.

    Zwraca słownik z metrykami globalnymi, rozbiciem na klasy i listą przypadków.
    Cele spoza indeksu trafiają do `pominiete` — NIE są liczone jako porażka.
    """
    from szukaj import szukaj  # type: ignore[import]

    obecne = zaindeksowane(baza)
    przypadki: list[dict] = []
    pominiete: list[dict] = []

    n = len(zbior)
    for i, c in enumerate(zbior, 1):
        osiagalne = tuple(z for z in c["zrodla_ok"] if z in obecne)
        if not osiagalne:
            pominiete.append({**c, "powod": "żaden cel nie jest zaindeksowany"})
            continue
        t0 = time.perf_counter()
        try:
            # Składnię przekazujemy DO `szukaj` (jedno źródło prawdy) zamiast budować
            # zapytanie tutaj — inaczej organ mierzyłby własną kopię logiki, a nie tę,
            # której faktycznie używa produkcja. `and` mierzy surowy MATCH — czyli stan
            # ścieżki MCP przed naprawą — i dlatego zostaje jako ramię porównania.
            wyniki = szukaj(c["pytanie"], topk=topk, tryb=tryb, baza=baza, cichy=True,
                            skladnia=("or" if skladnia == "or" else "surowa"))
        except sqlite3.OperationalError as e:
            # Składnia AND na pytaniu z myślnikiem potrafi wywalić MATCH — to WYNIK
            # (tak zachowa się produkcja), nie powód do przerwania pomiaru. ALE musi być
            # WIDOCZNY: przedtem przy `postep=False` awaria zapytania wchodziła do metryk
            # jako zwykły brak trafienia i raport nie mówił o niej ani słowa, więc werdykt
            # „BM25 słabo radzi sobie z pytaniami opisowymi" mógł w całości pochodzić
            # z zapytań, które się wysypały składniowo (recenzja 2026-07-29).
            wyniki = []
            blad = str(e)
            if postep:
                print(f"   [{i}/{n}] {c['id']}: błąd FTS ({e})", flush=True)
        else:
            blad = ""
        ms = (time.perf_counter() - t0) * 1000
        poz = _pozycja_trafienia(wyniki, osiagalne)
        przypadki.append({
            "id": c["id"], "klasa": c["klasa"], "pytanie": c["pytanie"],
            "cele": osiagalne, "pozycja": poz, "ms": ms, "blad": blad,
            "zwrocone": [_bib(getattr(w, "zrodlo", "")) or "(nie-BIB)" for w in wyniki[:5]],
        })
        if postep:
            znak = f"#{poz}" if poz else "—"
            print(f"   [{i}/{n}] {c['id']} {c['klasa']:9s} {znak:>4s}  {ms:5.0f} ms", flush=True)

    # PROGI RECALL LICZONE Z topk, a nie wpisane na sztywno (naprawione po recenzji
    # 2026-07-29). Poprzednio klucz „recall@10" trzymał `rec(min(10, topk))`, a raport
    # drukował stałe etykiety 1/5/10 — więc bieg z `--topk 3` pokazywał recall@3 w dwóch
    # kolumnach podpisanych „@5" i „@10". Liczba szła do rejestru testów i do decyzji
    # o wektorach jako recall@10, choć nigdy nie oglądano dziesięciu wyników. To ta sama
    # klasa, którą ten organ ma tropić: przyrząd twierdzi coś, czego nie zmierzył.
    progi = sorted({1, min(5, topk), min(10, topk)})

    def _metryki(grupa: list[dict]) -> dict:
        if not grupa:
            return {"n": 0, "progi": progi, "recall": {k: None for k in progi}, "mrr": None}

        def rec(k: int) -> float:
            return sum(1 for p in grupa if p["pozycja"] and p["pozycja"] <= k) / len(grupa)
        mrr = sum((1.0 / p["pozycja"]) if p["pozycja"] else 0.0 for p in grupa) / len(grupa)
        return {"n": len(grupa), "progi": progi,
                "recall": {k: rec(k) for k in progi}, "mrr": mrr}

    dosl = [p for p in przypadki if p["klasa"] == "doslowna"]
    opis = [p for p in przypadki if p["klasa"] == "opisowa"]
    return {
        "tryb": tryb, "skladnia": skladnia, "topk": topk,
        "globalne": _metryki(przypadki),
        "doslowna": _metryki(dosl),
        "opisowa": _metryki(opis),
        "przypadki": przypadki,
        "pominiete": pominiete,
        "bledy": [p for p in przypadki if p["blad"]],
        "ms_srednio": (sum(p["ms"] for p in przypadki) / len(przypadki)) if przypadki else 0.0,
    }


def _proc(x: float | None) -> str:
    return "—" if x is None else f"{x*100:5.1f}%"


def raport(w: dict, szczegoly: bool = False) -> str:
    g, d, o = w["globalne"], w["doslowna"], w["opisowa"]
    L = [
        f"🔎 QUAESITOR — jakość wyszukiwania RAG (tryb={w['tryb']}, składnia={w['skladnia']}, topk={w['topk']})",
        f"   pytań ocenionych: {g['n']} | pominiętych (cel poza indeksem): {len(w['pominiete'])}"
        f" | średni czas zapytania: {w['ms_srednio']:.0f} ms",
        "",
        # Nagłówek generowany z FAKTYCZNYCH progów — etykieta nie może obiecywać @10,
        # gdy oglądaliśmy 3 wyniki (recenzja 2026-07-29).
        "   klasa         n " + "".join(f"  recall@{k:<3}" for k in g["progi"]) + "     MRR",
    ]
    prog_luki = g["progi"][-1] if len(g["progi"]) < 2 else g["progi"][1]
    for nazwa, m in (("DOSŁOWNA", d), ("OPISOWA", o), ("RAZEM", g)):
        mrr = "—" if m["mrr"] is None else f"{m['mrr']:.3f}"
        kolumny = "".join(f"    {_proc(m['recall'][k])}" for k in m["progi"])
        L.append(f"   {nazwa:<10}{m['n']:>4}{kolumny}   {mrr:>5}")

    if d["recall"].get(prog_luki) is not None and o["recall"].get(prog_luki) is not None:
        luka = (d["recall"][prog_luki] - o["recall"][prog_luki]) * 100
        L += ["", f"   📐 LUKA SŁOWNIKOWA (dosłowna − opisowa @{prog_luki}): {luka:+.1f} pp",
              "      To ZMIERZONY SUFIT zysku z embeddingów: tyle trafień gubimy, gdy pytanie",
              "      niesie sens bez wspólnych słów. Luka mała → wektory kupią mało (R5 pada)."]

    if w.get("bledy"):
        L += ["", f"   🚨 ZAPYTANIA, KTÓRE SIĘ WYSYPAŁY: {len(w['bledy'])} — liczone jako BRAK",
              "      trafienia, więc zaniżają recall. To wynik przyrządu, nie wyszukiwarki:"]
        for p in w["bledy"][:5]:
            L.append(f"      • {p['id']}: {p['blad'][:70]}")

    if w["pominiete"]:
        L += ["", f"   ⏭️ pominięte ({len(w['pominiete'])}): " +
              ", ".join(f"{p['id']}({'/'.join(p['zrodla_ok'])})" for p in w["pominiete"])]

    if szczegoly:
        L += ["", "   ── pytanie po pytaniu ──"]
        for p in w["przypadki"]:
            poz = f"#{p['pozycja']}" if p["pozycja"] else "BRAK"
            L.append(f"   {p['id']} {p['klasa']:9s} {poz:>5s}  cele={'/'.join(p['cele'])}"
                     f"  zwrócono={','.join(p['zwrocone']) or '(nic)'}")
            L.append(f"        „{p['pytanie'][:88]}”")
    return "\n".join(L)


def _topk(s: str) -> int:
    """topk z walidacją zakresu — recall@10 nie ma sensu przy topk<10, a wielkie topk
    zamienia known-item retrieval w 'w końcu trafi' (miara przestaje mierzyć rangę)."""
    v = int(s)
    if not 1 <= v <= 100:
        raise argparse.ArgumentTypeError(f"topk poza zakresem 1..100: {v}")
    return v


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="QUAESITOR — pomiar jakości wyszukiwania RAG")
    ap.add_argument("--tryb", choices=["fts", "wektor", "hybrid"], default="fts")
    ap.add_argument("--topk", type=_topk, default=10)
    ap.add_argument("--skladnia", choices=["and", "or", "oba"], default="oba",
                    help="and = domyślny MATCH (ścieżka MCP), or = składnia HYGINUSA")
    ap.add_argument("--baza", default=str(DOMYSLNA_BAZA))
    ap.add_argument("--szczegoly", action="store_true")
    ap.add_argument("--ledger", action="store_true", help="dopisz POMIAR do rejestru testów")
    args = ap.parse_args(argv)

    baza = Path(args.baza)
    if not baza.exists():
        print(f"[QUAESITOR] Brak bazy: {baza}. Uruchom: python narzedzia/rag/indeksuj.py", file=sys.stderr)
        return 2

    skladnie = ["and", "or"] if args.skladnia == "oba" else [args.skladnia]
    wyniki: dict[str, dict] = {}
    for s in skladnie:
        print(f"[QUAESITOR] składnia={s} — {len(ZBIOR)} pytań…", flush=True)
        w = ocen(tryb=args.tryb, topk=args.topk, skladnia=s, baza=baza, postep=args.szczegoly)
        wyniki[s] = w
        print(raport(w, szczegoly=args.szczegoly))
        print()

    if args.ledger:
        from narzedzia import scriba_codex
        # Próg bierzemy z FAKTYCZNIE użytego topk i wpisujemy go do nazwy wariantu —
        # ledger jest append-only, więc etykieta musi mówić prawdę o tym, co zmierzono
        # (przedtem zawsze pisała „@5", także przy `--topk 3`).
        warianty = {}
        prog = min(5, args.topk)
        for s, w in wyniki.items():
            warianty[f"{args.tryb}/{s} recall@{prog}"] = round((w["globalne"]["recall"][prog] or 0) * 100, 1)
            warianty[f"{args.tryb}/{s} opisowa@{prog}"] = round((w["opisowa"]["recall"][prog] or 0) * 100, 1)
        najlepsza = max(wyniki.items(), key=lambda kv: kv[1]["globalne"]["recall"][prog] or 0)
        scriba_codex.zapisz_pomiar(
            temat="RAG — jakość wyszukiwania (QUAESITOR)",
            pytanie="Jaki recall@k ma dzisiejsze wyszukiwanie i ile trafień gubi na pytaniach opisowych?",
            warianty=warianty, metryka=f"recall@{prog} [%]",
            werdykt=f"najlepsza składnia: {najlepsza[0]}",
            zrodlo="narzedzia/rag/quaesitor.py",
            uwaga=f"zbiór {len(ZBIOR)} pytań known-item, {len(najlepsza[1]['pominiete'])} pominiętych (cel poza indeksem)",
        )
        print("[QUAESITOR] POMIAR dopisany do rejestru testów.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
