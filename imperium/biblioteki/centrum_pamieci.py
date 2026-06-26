"""
🧠 Centrum Pamięci Imperium (W-360 v5) — zunifikowany hub wszystkich warstw pamięci.

PROBLEM: pamięć Imperium rozrosła się do 5 warstw, każda z osobnym API. Jedynym
wejściem jest git/RAG (wyszukiwanie ręczne). Brak: cross-layer search, scoringu
lekcji (Generative Agents: recency·importance·relevance), proaktywnych przypomnień.

ROZWIĄZANIE: ten moduł jest FASADĄ (nie duplikuje logiki!) — jedyna ścieżka do całej
pamięci Imperium. Zastępuje rozsiane importy jednym `from imperium.biblioteki import
centrum_pamieci as pm`.

WARSTWY (każda pozostaje samodzielna, tu tylko spięta w całość):
  W1 — pamiec_absolutna.py: logi SYGNAŁÓW, TRADE, ANALIZA, TEST (JSONL / TypLogu) ✅ ŻYWA
  W2 — bibliotheca_ulpia/ : RAG semantyczny (FTS5, 41/42 książek + encyklopedia) ✅ ZBUDOWANA
  W3 — pamiec_sesji.py   : LEKCJE z sesji + PROFIL Cezara (markdown → git) ✅ ŻYWA
  W3 — kronika_czatu.py  : PEŁNY DIALOG (destylat transkryptów → git) ✅ ŻYWA
  W4 — rejestr_wizji.py  : WIZJE, DECYZJE, POMYSŁY, ZMIANY (JSONL → git) ✅ ŻYWA [v4]
  (~) pamiec_refleksyjna.py: narracyjne refleksje po handlu (imperium/cesarz/) ✅ ŻYWA
  (~) ksiega_wad.py       : prewencja powtarzania błędów (imperium/cesarz/) ✅ ŻYWA
  WYCOFANY: mnemosyne.py  — SQLite trade-learning zastąpiony przez pamiec_refleksyjna
                            + ksiega_wad (Prawo XVI: mierzalna redundancja → wycofanie)

NOWOŚCI v5 (2026-06-26 — Pełna Symbioza + Most Chmura↔Lokal):
  • W2 RAG podpięty do szukaj_wszedzie (naprawa L2): fasada konsultuje 42 książki —
    wcześniej "jedyna ścieżka do pamięci" pomijała największą warstwę wiedzy.
  • W5 refleksje rynkowe podpięte (naprawa L4): narracyjne lekcje z pipeline teraz
    widoczne w cross-layer search (graceful: chmura logs/ gitignore → pusto).
  • Most Chmura↔Lokal (srodowisko_pamieci.py, UNIKAT): pamięć środowiskowo-adaptacyjna —
    chmura FTS (przeżywa przez git), lokal upgrade do wektorów semantycznych.
  • Deduplikacja (naprawa L6): auto_lekcja + rejestr_wizji nie dublują wpisów.
  • Cross-layer = 6 warstw: lekcje+kronika+wizje+logi+wiedza(RAG)+refleksje.

NOWOŚCI v4 (2026-06-26):
  • W4 Rejestr Wizji i Decyzji: ustrukturyzowana pamięć WIZJI/DECYZJI/POMYSŁÓW/ZMIAN.
    szukaj_wszedzie() teraz zwraca wyniki z 4 warstw (lekcje+kronika+logi+wizje).
    Każdy wpis ma typ, status, pełny scoring GA × reżim.

  • Scoring kroniki (opcja B): kronika dostaje recency×relevance zamiast flat 0.3.
    Świeższy fragment z pasującym słowem kluczowym wyprzedza stary przypadkowy.

  • Auto-lekcja (opcja C): narzedzia/auto_lekcja.py — DeepSeek API ekstrahuje lekcje,
    wizje i decyzje z ostatniej sesji. Uruchamiany przez SessionStart hook.

NOWOŚCI v3 (adopcja badań 2024-2026):
  • Scoring Generative Agents (Park et al., arXiv:2304.03442):
    score = recency × importance × relevance
  • Zanik warstwowy (adopcja FinMem, arXiv:2311.13743).
  • Pamięć Reżimowa (UNIKAT): 4. wymiar scoringu — regime_match.
  • Cross-layer search: lekcje (W3) + kronika (W3b) + logi (W1) + wizje (W4).

ARCHITEKTURA PAMIĘCI (dla SessionStart hook):
  centrum_pamieci podsumowanie_startowe → hook wyświetla scored TOP-3 + cross-layer

Bez zależności zewnętrznych (stdlib: re, datetime, pathlib) → działa w chmurze.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional, Any

# Importy warstw (leniwe → nie wymuszają wszystkich zależności, jeśli warstwa niedostępna)
from imperium.biblioteki import pamiec_sesji as _ps
from imperium.biblioteki import kronika_czatu as _kc
from imperium.biblioteki import rejestr_wizji as _rw

ROOT = Path(__file__).resolve().parent.parent.parent

# ─── SCORING GENERATIVE AGENTS (Park et al., 2304.03442) ─────────────────────

# (poprzedni stały zanik 0.995 zastąpiony zanikiem warstwowym — patrz niżej;
#  recency liczone względem date.today() — patrz _recency)

# ── ZANIK WARSTWOWY (adopcja FinMem arXiv:2311.13743 — layered long-term memory) ──
# FinMem trzyma 3 dyskretne warstwy (shallow/intermediate/deep) z RÓŻNYM tempem
# zaniku — ważne wydarzenia trafiają głębiej i żyją dłużej. Nasz UNIKAT: zamiast
# 3 kubełków robimy CIĄGŁĄ funkcję zaniku od ważności (importance → tempo zaniku).
# Lekcja rutynowa (i=0.3) zanika szybko (half-life ~69 dni); lekcja krytyczna
# (i=1.0, "utrata potencjału") zanika wolno (half-life ~690 dni). Bez tego lekcja
# o bugu znikała tak samo szybko jak notatka o profilu — UTRATA POTENCJAŁU (Prawo XV).
_DECAY_SHALLOW = 0.99    # rutyna (importance≈0.3) — płytka warstwa, szybki zanik
_DECAY_DEEP = 0.999     # krytyczne (importance≈1.0) — głęboka warstwa, wolny zanik


def _decay_dla_waznosci(importance: float) -> float:
    """
    FinMem layered decay jako funkcja ciągła: importance → tempo zaniku per dzień.
    i=0.3 → 0.99 (płytka), i=1.0 → 0.999 (głęboka). Interpolacja liniowa, clamp [0.3,1.0].
    """
    i = min(max(importance, 0.3), 1.0)
    frakcja = (i - 0.3) / (1.0 - 0.3)
    return _DECAY_SHALLOW + frakcja * (_DECAY_DEEP - _DECAY_SHALLOW)

# Słowa wskazujące na ważność lekcji (heurystyka zamiast LLM — zero kosztu).
# Wzorowane na Mem0 ADD/UPDATE metadanych: lekcje z bugiem/odkryciem/prawem ważniejsze.
_SLOWA_WAZNE = {
    "bug": 0.9, "fix": 0.8, "błąd": 0.9, "odkrycie": 0.9, "prawo": 0.8,
    "utrata potencjału": 1.0, "prawo xv": 1.0, "prawo xxi": 1.0,
    "speedup": 0.7, "optymalizacja": 0.6, "adopcja": 0.7,
    "backtest": 0.6, "sharpe": 0.7, "reżim": 0.7, "signal": 0.6,
    "mcp": 0.5, "pamięć": 0.5, "kronika": 0.5, "profil": 0.4,
}


def _recency(data_str: str, importance: float = 0.6) -> float:
    """
    Wykładniczy zanik od daty lekcji do dziś (1.0 = dziś).
    Tempo zaniku zależy od ważności (FinMem layered decay): lekcja krytyczna
    zanika wolniej niż rutynowa. importance domyślnie 0.6 (środek) gdy nieznana.
    """
    try:
        d = date.fromisoformat(data_str)
    except ValueError:
        return 0.5
    delta = (date.today() - d).days
    return _decay_dla_waznosci(importance) ** max(delta, 0)


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


# ── PAMIĘĆ REŻIMOWA (UNIKAT IMPERIUM — 4. wymiar scoringu) ───────────────────
# Konkurencja (Mem0, Zep/Graphiti, Letta, A-Mem) jest DOMENOWO ŚLEPA: retrieval po
# podobieństwie semantycznym + recency + (Zep) ważności czasowej. ŻADEN nie wie, że
# ważność wspomnienia TRADINGOWEGO zależy od REŻIMU rynku. Lekcja „kupuj dołki" z
# hossy (TREND_STRONG) jest AKTYWNIE SZKODLIWA w bessie/krachu. Warunkujemy retrieval
# na bieżącym reżimie (z Gubernatora / klasyfikuj_rezim): wspomnienie z tego samego
# reżimu pełna waga, z innego — tłumione. Wspomnienie bez tagu reżimu → neutralne 1.0
# (nie karzemy lekcji ogólnych). To czyni pamięć Imperium reżimowo-świadomą.
_DAMPEN_REZIM = 0.4   # mnożnik dla wspomnienia z INNEGO reżimu (zmierzona ostrożność)

# Kanoniczne tokeny reżimu (z legatus.klasyfikuj_rezim + pole log.rezim + lekcje).
_REZIMY_KANON = ("VOLATILE", "TREND_STRONG", "RANGING", "NORMAL", "BULL", "BEAR")


def _wykryj_rezim(tekst: str) -> Optional[str]:
    """Wykrywa kanoniczny token reżimu we wspomnieniu. None = brak tagu (neutralne)."""
    g = tekst.upper()
    # TREND_STRONG przed BULL/BEAR (bardziej specyficzny), by nie złapać podłańcucha
    for r in _REZIMY_KANON:
        if r in g:
            return r
    return None


def _regime_match(rezim_wspomnienia: Optional[str], rezim_biezacy: str) -> float:
    """
    Dopasowanie reżimu: 1.0 gdy zgodny / brak tagu, _DAMPEN_REZIM gdy inny.
    Brak bieżącego reżimu ('') → 1.0 (funkcja wyłączona, wstecznie kompatybilne).
    """
    if not rezim_biezacy or rezim_wspomnienia is None:
        return 1.0
    return 1.0 if rezim_wspomnienia.upper() == rezim_biezacy.upper() else _DAMPEN_REZIM


def score_lekcji(lekcja: Dict[str, str], zapytanie: str = "",
                 rezim_biezacy: str = "") -> float:
    """
    Scoring Generative Agents + UNIKAT reżimowy:
    score = recency × importance × relevance × regime_match.
    rezim_biezacy='' → regime_match=1.0 (wstecznie kompatybilne, funkcja wyłączona).
    """
    i = _importance(lekcja["tytul"], lekcja["tresc"])
    r = _recency(lekcja["data"], i)   # FinMem: tempo zaniku zależy od ważności
    v = _relevance(zapytanie, lekcja["tytul"], lekcja["tresc"])
    rz = _regime_match(_wykryj_rezim(lekcja["tytul"] + " " + lekcja["tresc"]), rezim_biezacy)
    baza = r * i * v if zapytanie else r * i
    return baza * rz


# ─── CROSS-LAYER SEARCH ───────────────────────────────────────────────────────

def szukaj_wszedzie(zapytanie: str, limit: int = 10,
                   cel_kronika: Optional[Path] = None,
                   rezim_biezacy: str = "") -> List[Dict[str, Any]]:
    """
    Cross-layer search (v5 — 6 warstw): jedno zapytanie → lekcje (W3) + kronika (W3b)
    + wizje (W4) + logi (W1) + wiedza/RAG (W2) + refleksje (W5). Każda warstwa scored.

    rezim_biezacy (UNIKAT): gdy podany (np. 'TREND_STRONG' z Gubernatora) — pamięć
    reżimowo-świadoma: wspomnienia z innego reżimu tłumione (×_DAMPEN_REZIM).

    Returns [{"warstwa": "lekcje"|"kronika"|"wizje"|"logi"|"wiedza"|"refleksje",
              "score": float, "tresc": str, ...}]
    """
    wyniki: List[Dict[str, Any]] = []

    # W3 — lekcje (scored + reżimowo)
    for lek in _ps.lekcje(plik=_ps.DOMYSLNY_PLIK):
        s = score_lekcji(lek, zapytanie, rezim_biezacy)
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

    # W3b — kronika (FTS + scoring recency×relevance zamiast flat 0.3)
    cel = cel_kronika or _kc.CEL_DOMYSLNY
    for t in _kc.szukaj(zapytanie, cel, limit=limit):
        sesja_data = t.get("data", "")
        rec = _recency(sesja_data, 0.5) if sesja_data else 0.5
        rel = _relevance(zapytanie, "", t["fragment"]) if zapytanie else 0.5
        score_k = rec * max(rel, 0.3)   # floor 0.3 by kronika nie spadła poniżej szumu
        wyniki.append({
            "warstwa": "kronika",
            "score": score_k,
            "sesja": t["sesja"],
            "tresc": t["fragment"],
        })

    # W4 — wizje, decyzje, pomysły, zmiany (rejestr_wizji — scored GA × reżim)
    try:
        for w in _rw.szukaj_scored(zapytanie, limit, rezim_biezacy):
            wyniki.append(w)
    except Exception:
        pass

    # W1 — logi transakcji (pamiec_absolutna: najbogatsze dane — rezim/PnL/MAE/MFE).
    # Naprawa UTRATY POTENCJAŁU (Prawo XV): te logi były dotąd poza zasięgiem fasady.
    for w in _szukaj_w_logach(zapytanie, limit, rezim_biezacy):
        wyniki.append(w)

    # W2 — RAG (42 książki + encyklopedia + docs). Naprawa L2 (audyt 2026-06-26):
    # fasada reklamowana jako "jedyna ścieżka do całej pamięci" pomijała największą
    # warstwę wiedzy. Teraz konsultuje wiedzę domenową. Graceful: brak bazy → [].
    if zapytanie:
        for w in _szukaj_w_rag(zapytanie, limit):
            wyniki.append(w)

    # W5 — pamięć refleksyjna (narracyjne lekcje rynkowe, imperium/cesarz/).
    # Graceful: w chmurze logs/ gitignore → pusto; lokalnie żywa. Naprawa L4.
    for w in _szukaj_w_refleksjach(zapytanie, limit, rezim_biezacy):
        wyniki.append(w)

    wyniki.sort(key=lambda x: x["score"], reverse=True)
    return wyniki[:limit]


def _szukaj_w_logach(zapytanie: str, limit: int,
                     rezim_biezacy: str = "") -> List[Dict[str, Any]]:
    """
    W1 cross-layer: przeszukuje logi TRADE_CLOSE z pamiec_absolutna.
    Tekst budowany z pól semantycznych (symbol/rezim/powód/notatka/kierunek),
    scoring = recency × relevance × regime_match. Resilient: brak logów → [].
    Logi mają JAWNE pole rezim → dopasowanie reżimowe jest precyzyjne (nie z tekstu).
    """
    try:
        from imperium.biblioteki import pamiec_absolutna as _pa
    except Exception:
        return []
    try:
        # jawne LOG_DIR (nie default arg) → testowalne przez monkeypatch
        logi = _pa.PamiecAbsolutna(_pa.LOG_DIR).wczytaj(log_typ=_pa.TypLogu.TRADE_CLOSE)
    except Exception:
        return []

    wyniki: List[Dict[str, Any]] = []
    for log in logi:
        tekst = " ".join(str(x) for x in (
            log.symbol, log.rezim, log.kierunek_pozycji,
            log.powod_zamkniecia, log.notatka, log.strategia_id,
        ) if x)
        data = (log.timestamp_utc or "")[:10]
        # logi mają znaczenie bazowe 0.7 (twarde dane wyniku, nie proza)
        rec = _recency(data, 0.7)
        rel = _relevance(zapytanie, log.symbol, tekst)
        rz = _regime_match(log.rezim or None, rezim_biezacy)   # jawne pole rezim
        score = (rec * 0.7 * rel if zapytanie else rec * 0.7) * rz
        if zapytanie and rel < 0.05:
            continue
        wyniki.append({
            "warstwa": "logi",
            "score": score,
            "data": data,
            "symbol": log.symbol,
            "rezim": log.rezim,
            "tresc": f"{log.kierunek_pozycji} {log.symbol} PnL={log.pnl_pct:+.2f}% "
                     f"MAE={log.mae_pct:.2f}% MFE={log.mfe_pct:.2f}% "
                     f"({log.powod_zamkniecia}) {log.notatka}".strip(),
        })
    wyniki.sort(key=lambda x: x["score"], reverse=True)
    return wyniki[:limit]


def _wektory_dostepne() -> bool:
    """True gdy baza RAG ma wektory semantyczne (lokal po indeksacji). Chmura: False."""
    try:
        from imperium.biblioteki import srodowisko_pamieci as _sp
        return _sp._wektory_w_bazie() > 0 and _sp._model_embeddings_dostepny()
    except Exception:
        return False


def _szukaj_w_rag(zapytanie: str, limit: int) -> List[Dict[str, Any]]:
    """
    W2 cross-layer: przeszukuje RAG (42 książki + encyklopedia + docs).
    Naprawa L2 (audyt 2026-06-26): wiedza domenowa była poza zasięgiem fasady.
    BM25 zwraca ujemne (mniejsze=lepsze) → normalizujemy do skali GA 0–1.
    Resilient: brak bazy/modułu → []. Limit ≤3 by nie zalać wynikami z książek.
    """
    try:
        from narzedzia.rag import szukaj as _rag
    except Exception:
        return []
    try:
        # tryb="fts" wymusza BM25 — nie próbuje ładować modelu embeddings (proxy blokuje
        # huggingface w chmurze → wyjątek sieciowy). Lokalnie można podnieść do hybrid.
        tryb = "hybrid" if _wektory_dostepne() else "fts"
        trafienia = _rag.szukaj(zapytanie, topk=min(limit, 3), tryb=tryb, cichy=True)
    except Exception:
        return []

    wyniki: List[Dict[str, Any]] = []
    for w in trafienia:
        # BM25 ujemny (np. -8 silne, -1 słabe) → mapowanie na 0–1; brak recency (książki ponadczasowe)
        try:
            ga = min(1.0, abs(float(w.score)) / 10.0)
        except (TypeError, ValueError):
            ga = 0.3
        wyniki.append({
            "warstwa": "wiedza",   # W2 RAG — wiedza domenowa z książek
            "score": ga * 0.6,     # waga 0.6: wiedza wspiera, nie dominuje nad lekcjami z sesji
            "zrodlo": getattr(w, "zrodlo", ""),
            "tytul": getattr(w, "tytul", ""),
            "tresc": (getattr(w, "tekst", "") or "")[:200],
        })
    return wyniki


def _szukaj_w_refleksjach(zapytanie: str, limit: int,
                          rezim_biezacy: str = "") -> List[Dict[str, Any]]:
    """
    W5 cross-layer: narracyjne refleksje rynkowe (imperium/cesarz/pamiec_refleksyjna).
    Naprawa L4 (audyt 2026-06-26): refleksje były czytane tylko w pipeline backtestu,
    nigdy w cross-layer search ani podsumowaniu startowym. Resilient: brak danych → [].
    W chmurze logs/ gitignore → zwykle pusto; lokalnie żywe.
    """
    try:
        from imperium.cesarz import pamiec_refleksyjna as _pr
    except Exception:
        return []
    try:
        wszystkie = _pr.PamiecRefleksyjna().wczytaj_wszystkie()
    except Exception:
        return []

    wyniki: List[Dict[str, Any]] = []
    for r in wszystkie:
        # Lekcja (dataclass): data, rezim, interwal, wynik, pnl_usdt, lekcja_tekst, zrodlo
        tekst = " ".join(str(x) for x in (
            getattr(r, "lekcja_tekst", ""), getattr(r, "rezim", ""),
            getattr(r, "interwal", ""), getattr(r, "wynik", ""),
        ) if x)
        rezim_r = getattr(r, "rezim", None)
        data = str(getattr(r, "data", ""))[:10]
        rel = _relevance(zapytanie, "", tekst) if zapytanie else 0.5
        if zapytanie and rel < 0.05:
            continue
        rz = _regime_match(rezim_r, rezim_biezacy)
        rec = _recency(data, 0.6) if data else 0.5
        score = (rec * 0.6 * rel if zapytanie else rec * 0.6) * rz
        wyniki.append({
            "warstwa": "refleksje",
            "score": score,
            "data": data,
            "tresc": tekst[:200].strip(),
        })
    wyniki.sort(key=lambda x: x["score"], reverse=True)
    return wyniki[:limit]


# ─── TOP-K LEKCJI (SCORED) ────────────────────────────────────────────────────

def top_lekcji(k: int = 3, zapytanie: str = "",
               rezim_biezacy: str = "") -> List[Dict[str, Any]]:
    """
    Top-k lekcji wg scoringu Generative Agents + reżim (recency×importance×relevance×regime).
    Zastępuje proste 'ostatnie N' — wypływają najważniejsze+świeże+pasujące do reżimu.
    rezim_biezacy='' → bez warunkowania reżimem (wstecznie kompatybilne).
    """
    wszystkie = _ps.lekcje(plik=_ps.DOMYSLNY_PLIK)
    scored = [(score_lekcji(lek, zapytanie, rezim_biezacy), lek) for lek in wszystkie]
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
    linie = ["🧠 CENTRUM PAMIĘCI (W-360 v5) — ciągłość między sesjami:"]

    # Most chmura↔lokal (W5) — środowisko + alarmy dostępności (UTRATA POTENCJAŁU)
    try:
        from imperium.biblioteki import srodowisko_pamieci as _sp
        rap = _sp.raport_dostepnosci()
        linie.append(
            f"   🌉 Środowisko: {rap['srodowisko'].upper()} | "
            f"RAG: {rap['rag_tryb']} ({rap['rag_fragmenty']} frag.) | "
            f"kronika: {rap['kronika_sesje']} sesji | wizje: {rap['wizje_wpisy']}"
        )
    except Exception:
        pass

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
    ap = argparse.ArgumentParser(description="Centrum Pamięci Imperium (W-360 v5)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("start", help="podsumowanie startowe (hook)")
    sub.add_parser("top", help="top-3 lekcji wg scoringu GA")
    p_szuk = sub.add_parser("szukaj", help="cross-layer search (opcjonalnie reżimowy)")
    p_szuk.add_argument("zapytanie", nargs="+")
    p_szuk.add_argument("--limit", type=int, default=10)
    p_szuk.add_argument("--rezim", default="",
                        help="UNIKAT: warunkuj reżimem (TREND_STRONG/VOLATILE/RANGING/NORMAL/BULL/BEAR)")
    args = ap.parse_args()

    if args.cmd == "start":
        print(podsumowanie_startowe())
    elif args.cmd == "top":
        for lek in top_lekcji(5):
            print(f"[{lek['score']:.3f}] [{lek['data']}] {lek['tytul']}")
    elif args.cmd == "szukaj":
        q = " ".join(args.zapytanie)
        for w in szukaj_wszedzie(q, args.limit, rezim_biezacy=args.rezim):
            warstwa = w["warstwa"]
            tresc = w.get("tytul", w.get("tresc", ""))[:80]
            print(f"[{w['score']:.3f}][{warstwa}] {tresc}")
    else:
        print(podsumowanie_startowe())
