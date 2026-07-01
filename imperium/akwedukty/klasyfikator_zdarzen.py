"""
🏷️ Klasyfikator Zdarzeń Newsowych — taksonomia + KIERUNEK per typ (dla NEWS-02).

ŹRÓDŁO (ZPO): „Event-Aware Sentiment Factors from LLM-Augmented Financial Tweets"
(https://arxiv.org/abs/2508.07408) — KLUCZOWE odkrycie: kierunek zależy od TYPU zdarzenia,
nie od samej polaryzacji. „Rumor/Speculation" i „Retail Buzz" mają STATYSTYCZNIE ZNACZĄCY
UJEMNY Sharpe → są KONTRARIAŃSKIE (fade'ować hype, nie gonić). To czyni NEWS-02 mądrzejszym
od płaskiego „pozytywny=LONG" (NEWS-01).

CO ROBI (deterministycznie, bez API — Prawo I): mapuje listę nagłówków na DOMINUJĄCY typ
zdarzenia + KIERUNEK znakowany [-1..+1] + pewność. Słowniki per typ, każdy z własnym
znakiem kierunku (nie polaryzacją). Działa offline, w pełni testowalny. LLM (DeepSeek)
może to później wyostrzyć, ale baza jest deterministyczna i mierzalna.

TAKSONOMIA (typ → bazowy kierunek, research-grounded):
  HACK/EXPLOIT       → -1.0  (ostry short — kradzież środków)
  UPADEK             → -1.0  (bankructwo/likwidacja/delisting)
  REGULACJA_NEG      → -0.7  (ban/pozew/SEC/oszustwo)
  ETF_APPROVAL       → +1.0  (zatwierdzenie ETF — trwały long)
  INSTYTUCJONALNY    → +0.7  (partnerstwo/adopcja/instytucje/integracja)
  TECHNICZNY         → +0.4  (upgrade/halving/mainnet — łagodny long)
  RUMOR/SPEKULACJA   → -0.4  (KONTRARIAŃSKI — fade hype, ujemny Sharpe per research)
  MAKRO              →  0.0  (kontekst, nie kierunek)
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

# typ → (lista słów-kluczy [pełne słowa], bazowy kierunek znakowany)
TAKSONOMIA: Dict[str, Tuple[List[str], float]] = {
    "HACK": (["hack", "hacked", "exploit", "breach", "stolen", "drained", "drain",
              "wlamanie", "kradziez", "wyciek"], -1.0),
    "UPADEK": (["bankruptcy", "bankrupt", "collapse", "insolvency", "insolvent",
                "liquidation", "delisting", "delisted", "bankructwo", "upadek",
                "niewyplacalnosc", "likwidacja"], -1.0),
    "REGULACJA_NEG": (["ban", "banned", "lawsuit", "sue", "sued", "sec", "fraud",
                       "subpoena", "crackdown", "probe", "charges", "zakaz", "pozew",
                       "oszustwo", "sledztwo"], -0.7),
    "ETF_APPROVAL": (["etf", "approval", "approved", "greenlight", "greenlit",
                      "zatwierdzenie", "zatwierdzony"], 1.0),
    "INSTYTUCJONALNY": (["institutional", "institution", "partnership", "adoption",
                         "integration", "treasury", "blackrock", "fidelity",
                         "instytucjonalny", "partnerstwo", "adopcja", "integracja"], 0.7),
    "TECHNICZNY": (["upgrade", "halving", "mainnet", "hardfork", "hard fork",
                    "launch", "deployment", "upgrade'u"], 0.4),
    "RUMOR": (["rumor", "rumour", "rumored", "speculation", "speculative", "reportedly",
               "could", "might", "may", "allegedly", "plotka", "spekulacja", "podobno"], -0.4),
    "MAKRO": (["fed", "inflation", "rates", "cpi", "macro", "recession", "fomc",
               "inflacja", "stopy", "recesja"], 0.0),
}


def _wystepuje(slowo: str, tekst: str) -> bool:
    """Pełne słowo (granice \\b), nie podciąg — chroni przed 'sec' w 'second'."""
    return re.search(r"\b" + re.escape(slowo) + r"\b", tekst) is not None


def klasyfikuj(naglowki: List[str]) -> Dict[str, object]:
    """
    Zwraca {"typ": str, "kierunek": float[-1..1], "pewnosc": float[0..1], "n_trafien": int,
            "rozklad": {typ: liczba}}.

    Dominujący typ = ten z największym WKŁADEM (liczba trafień × |kierunek|).
    Kierunek netto = średnia ważona kierunków trafionych typów (znak ma znaczenie).
    Pewność rośnie z liczbą trafień (saturacja ~6) i jednoznacznością dominacji.
    """
    rozklad: Dict[str, int] = {}
    suma_kierunek = 0.0
    suma_waga = 0.0
    wklad: Dict[str, float] = {}
    n_trafien = 0

    for naglowek in naglowki:
        tekst = naglowek.lower()
        for typ, (slowa, kierunek) in TAKSONOMIA.items():
            trafienia_typu = sum(1 for s in slowa if _wystepuje(s, tekst))
            if trafienia_typu:
                rozklad[typ] = rozklad.get(typ, 0) + trafienia_typu
                n_trafien += trafienia_typu
                # waga = liczba trafień; kierunek znakowany
                suma_kierunek += kierunek * trafienia_typu
                suma_waga += trafienia_typu
                wklad[typ] = wklad.get(typ, 0.0) + trafienia_typu * abs(kierunek)

    if not rozklad:
        return {"typ": "BRAK", "kierunek": 0.0, "pewnosc": 0.0, "n_trafien": 0, "rozklad": {}}

    kierunek_netto = round(max(-1.0, min(1.0, suma_kierunek / suma_waga)), 4)
    suma_wkladu = sum(wklad.values())
    if suma_wkladu > 0:
        typ_dominujacy = max(wklad.items(), key=lambda x: x[1])[0]
        udzial_dom = wklad[typ_dominujacy] / suma_wkladu
    else:
        # tylko zdarzenia neutralne KIERUNKOWO (np. MAKRO, kierunek=0.0) → brak wkładu.
        # Typ po liczbie trafień; kierunek 0 (bez przewagi). Zapobiega ZeroDivisionError.
        typ_dominujacy = max(rozklad.items(), key=lambda x: x[1])[0]
        udzial_dom = 1.0
    # pewność: saturacja liczby trafień × udział dominującego typu w wkładzie
    pewnosc = round(min(1.0, (0.3 + n_trafien / 10.0)) * udzial_dom, 4)

    return {
        "typ": typ_dominujacy,
        "kierunek": kierunek_netto,
        "pewnosc": pewnosc,
        "n_trafien": n_trafien,
        "rozklad": rozklad,
    }
