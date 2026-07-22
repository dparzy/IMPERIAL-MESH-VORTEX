"""
🖋️ SCRIBA CODEX PROBATIONUM — skryba, który dopisuje wyniki testów do ledgera.

Rzymski *scriba* = urzędnik-pisarz prowadzący oficjalne rejestry (acta). Tutaj:
jedyny, reużywalny appender do `bibliotheca_ulpia/dane/rejestr_testow.jsonl` —
wersjonowanego źródła prawdy wyników A/B i IC, z którego CODEX_PROBATIONUM.xlsx
generuje arkusze (patrz narzedzia/codex_probationum.py).

CEL (ROZKAZ CODEX, Cezar 2026-07-18): narzędzia A/B i pomiar-IC dopisują wynik do
ledgera SAM (flaga --ledger), żeby CODEX rósł bez ręcznego wklejania linii JSON.

GWARANCJE:
- **Append-only** (Prawo I: nic nie kasujemy) — nowy pomiar = nowa linia.
- **Idempotentny** — dwa identyczne biegi (te same parametry, ten sam wynik, ten
  sam dzień) NIE mnożą linii: identyczny rekord jest pomijany. Inny wynik/inny dzień
  = nowa linia (historia pomiarów, o to chodzi w rejestrze testów).
- **Klucze zgodne ze schematem** czytanym przez codex_probationum (Prawo XXI): AB i IC
  mają dokładnie te pola, których oczekuje generator arkuszy.

Nie liczy niczego — tylko formatuje i dopisuje. Pomiar robi narzędzie wołające.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "bibliotheca_ulpia" / "dane" / "rejestr_testow.jsonl"

# Kolejność pól = schemat czytany przez codex_probationum (Prawo XXI: bez aliasów).
POLA_AB = ("typ", "sygnal", "neuron", "interwal", "okno_barow", "roi_b", "roi_a",
           "delta_pp", "maxdd_delta", "werdykt", "ranga", "pokrycie_ery",
           "data", "zrodlo", "uwaga")
POLA_IC = ("typ", "sygnal", "neuron", "horyzont", "ic", "tryb", "prog", "werdykt",
           "kierunek", "data", "zrodlo", "uwaga")
POLA_SUGESTIA = ("typ", "element", "dzial", "uzasadnienie", "zgodnosc_imperium",
                 "status", "data", "zrodlo")
# POMIAR — rekord dla wyniku, który NIE jest ani A/B jednego sygnału, ani IC.
# Powód (NOTA N-a0b792e1, zmierzone 2026-07-20 na zarzut Cezara): schemat znał
# wyłącznie AB i IC, więc GŁÓWNY werdykt wachty 07-20 — porównanie interwałów
# (4h +3.26 / 1d -3.03 / 1h -3.37 / 15m -5.71) — nie miał gdzie trafić i CODEX go
# zgubił. Lukę zgłaszałem jako SUGESTIĘ trzy razy (ab_wXXX, NIEZMIENNIK, ponownie)
# i ani razu nie zamknąłem: sugestia w ledgerze to odłożenie z alibi, nie naprawa.
# `warianty` = {nazwa: wartość} — dowolna liczba ramion (interwały, profile, progi),
# bo pomiar wielowariantowy zredukowany do pary A/B traci informację (Prawo XV).
POLA_POMIAR = ("typ", "temat", "pytanie", "warianty", "metryka", "werdykt", "ranga",
               "pokrycie_ery", "okno_barow", "interwal", "data", "zrodlo", "uwaga")


def _dzis() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _wczytaj(sciezka: Path) -> list[dict]:
    """Czyta ledger (jeden rekord na linię). Brak pliku → []."""
    if not sciezka.exists():
        return []
    out = []
    for ln in sciezka.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def _linia(rekord: dict) -> str:
    """Deterministyczna serializacja (klucze wg schematu) — porównywalna bit-w-bit."""
    return json.dumps(rekord, ensure_ascii=False, sort_keys=True)


def _dopisz(rekord: dict, sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord, jeśli identyczny jeszcze nie istnieje. Zwraca True gdy dopisano.

    Idempotencja po CAŁYM rekordzie (z datą): ten sam bieg tego samego dnia nie
    mnoży linii; zmieniony wynik lub inny dzień = nowa linia.
    """
    istniejace = {_linia(r) for r in _wczytaj(sciezka)}
    if _linia(rekord) in istniejace:
        return False
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


# LIMEN FENESTRAE — próg reprezentatywności okna. Poniżej niego werdykt A/B jest
# WSTĘPNY, nie rozstrzygający. Zmierzone 2026-07-20 (NOTA N-4f7032a6): ten sam sygnał
# na tym samym interwale dał przeciwne werdykty zależnie od okna —
#   2 000 barów  → „POMAGA"    (Δ +1.77 pp)
#   pełna era    → „NEUTRALNE" (Δ +0.24 pp, 649 transakcji)
# Ledger trzymał oba jako równorzędne werdykty, więc krótki bieg mógł zamknąć temat
# fałszywym wnioskiem. Od teraz pokrycie jedzie W REKORDZIE, nie w pamięci operatora.
PROG_REPREZENTATYWNOSCI = 0.5


def ocen_pokrycie(okno_barow: int, dostepne_barow: int | None) -> dict:
    """Jaką część dostępnej ery pokrywa okno testu → czy werdykt jest rozstrzygający.

    Brak wiedzy o dostępnych barach (None) → „NIEZNANE": nie udajemy, że wiemy
    (Prawo I) — ale i nie ogłaszamy wyniku pełnowartościowym.
    """
    if not dostepne_barow or dostepne_barow <= 0:
        return {"pokrycie": None, "ranga": "NIEZNANE",
                "nota": "pokrycie ery nieznane — werdykt traktuj jako wstępny"}
    udzial = min(1.0, okno_barow / dostepne_barow)
    if udzial >= PROG_REPREZENTATYWNOSCI:
        return {"pokrycie": round(udzial, 3), "ranga": "ROZSTRZYGAJACY",
                "nota": f"okno pokrywa {udzial:.0%} dostępnej ery"}
    return {"pokrycie": round(udzial, 3), "ranga": "WSTEPNY",
            "nota": (f"okno pokrywa tylko {udzial:.0%} dostępnej ery — werdykt WSTĘPNY, "
                     "nie zamykaj tematu (ten sam sygnał potrafi zmienić werdykt na pełnym oknie)")}


def zapisz_ab(*, sygnal: str, neuron: str, interwal: str, okno_barow: int,
              roi_b: float, roi_a: float, maxdd_delta: float, werdykt: str,
              zrodlo: str, uwaga: str = "", data: str | None = None,
              dostepne_barow: int | None = None,
              sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord A/B (Δ PnL). delta_pp liczone tu (roi_a - roi_b).

    werdykt: krótki token ("POMAGA"/"SZKODZI"/"NEUTRALNE"/…), NIE długi baner z emoji.
    `dostepne_barow`: ile barów dawała cała era — pozwala oznaczyć rangę werdyktu
    (ROZSTRZYGAJACY / WSTEPNY), żeby krótki bieg nie uchodził za pełnowartościowy.
    """
    ocena = ocen_pokrycie(int(okno_barow), dostepne_barow)
    uwaga = f"{uwaga} | {ocena['nota']}" if uwaga else ocena["nota"]
    rekord = {
        "typ": "AB", "sygnal": sygnal, "neuron": neuron, "interwal": interwal,
        "okno_barow": int(okno_barow), "roi_b": round(float(roi_b), 2),
        "roi_a": round(float(roi_a), 2), "delta_pp": round(float(roi_a) - float(roi_b), 2),
        "maxdd_delta": round(float(maxdd_delta), 2), "werdykt": werdykt,
        "ranga": ocena["ranga"], "pokrycie_ery": ocena["pokrycie"],
        "data": data or _dzis(), "zrodlo": zrodlo, "uwaga": uwaga,
    }
    return _dopisz(rekord, sciezka)


def zapisz_ic(*, sygnal: str, neuron: str, horyzont: str, ic: float, tryb: str,
              prog: float, werdykt: str, kierunek: str, zrodlo: str, uwaga: str = "",
              data: str | None = None, sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord IC (skill sygnału na horyzoncie)."""
    rekord = {
        "typ": "IC", "sygnal": sygnal, "neuron": neuron, "horyzont": str(horyzont),
        "ic": round(float(ic), 4), "tryb": tryb, "prog": round(float(prog), 4),
        "werdykt": werdykt, "kierunek": kierunek, "data": data or _dzis(),
        "zrodlo": zrodlo, "uwaga": uwaga,
    }
    return _dopisz(rekord, sciezka)


def zapisz_pomiar(*, temat: str, pytanie: str, warianty: dict, metryka: str,
                  werdykt: str, zrodlo: str, okno_barow: int = 0, interwal: str = "",
                  uwaga: str = "", data: str | None = None,
                  dostepne_barow: int | None = None,
                  sciezka: Path = LEDGER) -> bool:
    """Dopisuje POMIAR wielowariantowy (porównanie interwałów, profili, progów…).

    Dla wyników, których schemat AB (jeden sygnał ON/OFF) ani IC (skill na horyzoncie)
    nie obejmuje. `warianty` to {nazwa: wartość} w jednostce `metryka` — np.
    {"4h": 3.26, "1H": -3.37} przy metryce "ROI %".

    Ranga werdyktu liczona tym samym LIMEN FENESTRAE co A/B: krótkie okno daje
    werdykt WSTĘPNY, nie rozstrzygający (ta sama pułapka dotyczy każdego pomiaru,
    nie tylko A/B).
    """
    if not warianty:
        raise ValueError("POMIAR bez wariantów — nie ma czego porównać (Prawo I)")
    ocena = ocen_pokrycie(int(okno_barow), dostepne_barow)
    uwaga = f"{uwaga} | {ocena['nota']}" if uwaga else ocena["nota"]
    rekord = {
        "typ": "POMIAR", "temat": temat, "pytanie": pytanie,
        # sort_keys w _linia i tak porządkuje — jawne sortowanie tu, żeby ten sam
        # pomiar wpisany w innej kolejności argumentów nie zrobił drugiej linii.
        "warianty": {k: warianty[k] for k in sorted(warianty)},
        "metryka": metryka, "werdykt": werdykt, "ranga": ocena["ranga"],
        "pokrycie_ery": ocena["pokrycie"], "okno_barow": int(okno_barow),
        "interwal": interwal, "data": data or _dzis(), "zrodlo": zrodlo, "uwaga": uwaga,
    }
    return _dopisz(rekord, sciezka)


def zapisz_sugestia(*, element: str, dzial: str, uzasadnienie: str,
                    zgodnosc_imperium: str, status: str = "KANDYDAT", zrodlo: str,
                    data: str | None = None, sciezka: Path = LEDGER) -> bool:
    """Dopisuje SUGESTIĘ rozbudowy (KANDYDAT — Prawo I) do arkusza Sugestie CODEX.

    Idempotencja po ELEMENCIE (nie po całym rekordzie z datą): sugestia to UNIKAT
    (jedna pozycja backlogu), nie szereg czasowy pomiarów — ta sama sugestia w innym
    dniu/biegu NIE dubluje linii. Status aktualizuje się ręcznie w ledgerze/generatorze.
    """
    rekord = {
        "typ": "SUGESTIA", "element": element, "dzial": dzial,
        "uzasadnienie": uzasadnienie, "zgodnosc_imperium": zgodnosc_imperium,
        "status": status, "data": data or _dzis(), "zrodlo": zrodlo,
    }
    for r in _wczytaj(sciezka):
        if r.get("typ") == "SUGESTIA" and r.get("element") == element:
            return False   # sugestia o tym elemencie już jest — nie dubluj
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


def zamknij_sugestia(*, element: str, powod: str, zrodlo: str,
                     status: str = "ZAMKNIETE", data: str | None = None,
                     sciezka: Path = LEDGER) -> bool:
    """Zamyka/koryguje istniejącą SUGESTIĘ — dopisując rekord zamknięcia (append-only).

    Powód istnienia (zmierzone 2026-07-19): sugestia „Naprawa backtestu O(n^2)" została
    obalona pomiarem (backtest jest LINIOWY), LOG_ZMIAN ogłosił korektę — ale ledger
    NIGDY jej nie dostał i dalej pokazywał „OCZEKUJE decyzji Cezara". Przyczyna klasy:
    zamykanie sugestii nie miało własnego API, więc robiono je „w widoku" i ginęło.
    Teraz zamknięcie jest operacją pierwszej kategorii, tak samo jak zapis.

    Historii NIE falsyfikujemy (Prawo I): pierwotny wpis zostaje, zamknięcie to NOWA
    linia z tym samym `element`. Zamknąć można tylko sugestię, która realnie istnieje.
    """
    istniejace = _wczytaj(sciezka)
    zrodlowa = next((r for r in istniejace
                     if r.get("typ") == "SUGESTIA" and r.get("element") == element), None)
    if zrodlowa is None:
        raise ValueError(
            f"zamknij_sugestia: brak SUGESTII o elemencie '{element}' — "
            "nie zamykamy czegoś, czego nie ma (KANDYDAT≠PRAWDA)."
        )
    rekord = {
        "typ": "SUGESTIA", "element": element, "dzial": zrodlowa.get("dzial", ""),
        "uzasadnienie": powod,
        "zgodnosc_imperium": zrodlowa.get("zgodnosc_imperium", ""),
        "status": status, "data": data or _dzis(), "zrodlo": zrodlo,
    }
    return _dopisz(rekord, sciezka)
