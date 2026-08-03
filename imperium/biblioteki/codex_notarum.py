"""CODEX NOTARUM — Księga Not Cenzorskich (LEX TALIONIS IMPERII).

Organ pamięci Imperium (biblioteki/) rejestrujący ZATWIERDZONE noty pracy Architekta:

  • NOTA CENSORIA (−) — zatwierdzony BŁĄD (jak nota infamii rzymskiego cenzora).
  • CORONA        (+) — zatwierdzony ORYGINALNY UNIKAT zgodny z zasadami (laur).

ZASADA „OKO ZA OKO" (LEX TALIONIS): każda NOTA otwiera **dług honorowy**, który
spłaca dopiero CORONA wskazująca tę notę (`splaca=<id_noty>`). Sesja nie powinna
domknąć się z niespłaconym długiem — błąd MUSI urodzić kompensujący unikat. To
silnik antykruchości: Imperium rośnie z własnych pomyłek (nie tylko je liczy).

Filozofia (spójna z resztą Imperium):
  • KANDYDAT ≠ PRAWDA — nic nie liczy się bez `zatwierdzenie` (pomiar/recenzja/Cezar).
    Puste zatwierdzenie = ValueError (Prawo I: bez dowodu nie ma noty ani lauru).
  • Ledger append-only JSONL (jak rejestr_testow.jsonl / Scriba Codex) — źródło
    prawdy, nie pamięć. Idempotencja po całym rekordzie (ten sam dzień nie mnoży linii).
  • Spina się z Księgą Wad (każdy błąd i tak tam ląduje) i CHECKLISTĄ KONIEC SESJI.

Nazwa rzymska (ZASADA NOMENKLATURY): codex notarum = „księga not"; nota censoria =
piętno cenzora; corona = wieniec/nagroda za zasługę.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "bibliotheca_ulpia" / "dane" / "codex_notarum.jsonl"

# Kolejność pól = schemat (Prawo XXI: bez aliasów). `splaca` tylko dla CORONA.
POLA = ("typ", "id", "data", "sesja", "opis", "kategoria", "zatwierdzenie",
        "waga", "splaca", "zrodlo")


def _dzis() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _id(typ: str, opis: str, data: str, sesja: str) -> str:
    """Deterministyczny, krótki identyfikator (idempotencja: ten sam wpis = to samo id)."""
    sygn = f"{typ}|{opis}|{data}|{sesja}".encode()
    return f"{typ[0]}-{hashlib.sha1(sygn).hexdigest()[:8]}"


def _linia(rekord: dict) -> str:
    """Deterministyczna serializacja — porównywalna bit-w-bit (idempotencja)."""
    return json.dumps(rekord, ensure_ascii=False, sort_keys=True)


def wczytaj(sciezka: Path = LEDGER) -> list[dict]:
    """Czyta ledger (jeden rekord na linię). Brak pliku → []."""
    if not sciezka.exists():
        return []
    out = []
    for ln in sciezka.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def _dopisz(rekord: dict, sciezka: Path = LEDGER) -> bool:
    """Dopisuje rekord, jeśli identyczny jeszcze nie istnieje. True gdy dopisano."""
    istniejace = {_linia(r) for r in wczytaj(sciezka)}
    if _linia(rekord) in istniejace:
        return False
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


def _rekord(typ: str, *, opis: str, kategoria: str, zatwierdzenie: str, sesja: str,
            waga: int, splaca: str | None, zrodlo: str, data: str | None) -> dict:
    if not zatwierdzenie or not zatwierdzenie.strip():
        raise ValueError(
            f"{typ}: puste `zatwierdzenie` — KANDYDAT≠PRAWDA (Prawo I). "
            "Nota/laur wymaga dowodu: pomiar / recenzja / decyzja Cezara."
        )
    if not opis or not opis.strip():
        raise ValueError(f"{typ}: pusty `opis`.")
    data = data or _dzis()
    return {
        "typ": typ, "id": _id(typ, opis, data, sesja), "data": data, "sesja": sesja,
        "opis": opis.strip(), "kategoria": kategoria, "zatwierdzenie": zatwierdzenie.strip(),
        "waga": int(waga), "splaca": splaca, "zrodlo": zrodlo,
    }


def dodaj_nota(*, opis: str, kategoria: str, zatwierdzenie: str, sesja: str,
               waga: int = 1, zrodlo: str = "", data: str | None = None,
               sciezka: Path = LEDGER) -> str:
    """Zapisuje ZATWIERDZONY błąd (NOTA CENSORIA, −). Zwraca id noty (do spłaty CORONĄ)."""
    rek = _rekord("NOTA", opis=opis, kategoria=kategoria, zatwierdzenie=zatwierdzenie,
                  sesja=sesja, waga=waga, splaca=None, zrodlo=zrodlo, data=data)
    _dopisz(rek, sciezka)
    return rek["id"]


def dodaj_corona(*, opis: str, kategoria: str, zatwierdzenie: str, sesja: str,
                 splaca: str | None = None, waga: int = 1, zrodlo: str = "",
                 data: str | None = None, sciezka: Path = LEDGER) -> str:
    """Zapisuje ZATWIERDZONY unikat (CORONA, +). `splaca`=id noty → spłata długu honorowego.

    Jeśli `splaca` wskazuje nieistniejącą notę → ValueError (oko za oko musi mieć oko).
    """
    if splaca is not None:
        noty = {r["id"] for r in wczytaj(sciezka) if r.get("typ") == "NOTA"}
        if splaca not in noty:
            raise ValueError(
                f"CORONA.splaca='{splaca}' nie wskazuje żadnej istniejącej NOTY "
                "(oko za oko wymaga realnego oka)."
            )
    rek = _rekord("CORONA", opis=opis, kategoria=kategoria, zatwierdzenie=zatwierdzenie,
                  sesja=sesja, waga=waga, splaca=splaca, zrodlo=zrodlo, data=data)
    _dopisz(rek, sciezka)
    return rek["id"]


def dodaj_odroczenie(*, nota: str, zatwierdzenie: str, sesja: str, plan: str,
                     zrodlo: str = "", data: str | None = None,
                     sciezka: Path = LEDGER) -> str:
    """Odracza spłatę NOTY na późniejszą wachtę — WYŁĄCZNIE decyzją Cezara.

    DLACZEGO ISTNIEJE (zmierzone 2026-08-03): LEX TALIONIS zakłada spłatę w tej samej
    sesji („sesja nie domyka się z długiem honorowym > 0"), a Cezar rozkazał zamknąć
    wachtę i zbudować CORONĘ w następnej. Bez tego rekordu jego rozkaz byłby
    NIEWYKONALNY bez łamania Prawa XXI — a mechanizm, który nie umie przyjąć decyzji
    Imperatora, zmusza do obchodzenia siebie. Obchodzenie bramki jest gorsze od
    odroczenia zapisanego jawnie: pierwsze znika bez śladu, drugie zostaje w ledgerze
    i jest drukowane przy każdym bilansie, dopóki korona nie przyjdzie.

    Odroczenie NIE kasuje długu — zdejmuje wyłącznie blokadę commita.
    """
    if not plan or not plan.strip():
        raise ValueError("ODROCZENIE bez `plan` — odroczenie bez planu spłaty to umorzenie.")
    noty = {r["id"] for r in wczytaj(sciezka) if r.get("typ") == "NOTA"}
    if nota not in noty:
        raise ValueError(f"ODROCZENIE.nota='{nota}' nie wskazuje żadnej istniejącej NOTY.")
    rek = _rekord("ODROCZENIE", opis=plan, kategoria="odroczenie",
                  zatwierdzenie=zatwierdzenie, sesja=sesja, waga=0, splaca=nota,
                  zrodlo=zrodlo, data=data)
    _dopisz(rek, sciezka)
    return rek["id"]


def odroczone(sciezka: Path = LEDGER) -> list[dict]:
    """NOTY z odroczoną spłatą (decyzja Cezara). Dług NADAL istnieje — tylko nie blokuje."""
    rek = wczytaj(sciezka)
    splacone = {r.get("splaca") for r in rek if r.get("typ") == "CORONA" and r.get("splaca")}
    odr = {r.get("splaca") for r in rek if r.get("typ") == "ODROCZENIE" and r.get("splaca")}
    return [r for r in rek if r.get("typ") == "NOTA"
            and r["id"] not in splacone and r["id"] in odr]


def dlug_honorowy(sciezka: Path = LEDGER) -> list[dict]:
    """NOTY bez spłacającej je CORONY i BEZ odroczenia (te blokują domknięcie sesji).

    Noty odroczone decyzją Cezara wychodzą stąd do `odroczone()` — nie znikają, tylko
    przestają zatrzymywać commit. Bilans drukuje je osobno, żeby odroczenie nigdy nie
    stało się cichym umorzeniem.
    """
    rek = wczytaj(sciezka)
    splacone = {r.get("splaca") for r in rek if r.get("typ") == "CORONA" and r.get("splaca")}
    odr = {r.get("splaca") for r in rek if r.get("typ") == "ODROCZENIE" and r.get("splaca")}
    return [r for r in rek if r.get("typ") == "NOTA"
            and r["id"] not in splacone and r["id"] not in odr]


def bilans(sciezka: Path = LEDGER) -> dict:
    """Bilans not: liczby, saldo (Σwag CORONA − Σwag NOTA), lista długu honorowego."""
    rek = wczytaj(sciezka)
    noty = [r for r in rek if r.get("typ") == "NOTA"]
    korony = [r for r in rek if r.get("typ") == "CORONA"]
    suma_not = sum(int(r.get("waga", 1)) for r in noty)
    suma_koron = sum(int(r.get("waga", 1)) for r in korony)
    return {
        "noty": len(noty),
        "korony": len(korony),
        "saldo": suma_koron - suma_not,
        "dlug_honorowy": dlug_honorowy(sciezka),
        "odroczone": odroczone(sciezka),
    }


def raport(sciezka: Path = LEDGER) -> str:
    """Zwięzły raport tekstowy (do banera / Kapitolu — zero-tokenowo)."""
    b = bilans(sciezka)
    znak = "+" if b["saldo"] >= 0 else ""
    linie = [
        "📜 CODEX NOTARUM (LEX TALIONIS) — noty pracy Architekta",
        f"   NOTA CENSORIA: {b['noty']} | CORONA: {b['korony']} | saldo: {znak}{b['saldo']}",
    ]
    dlug = b["dlug_honorowy"]
    if dlug:
        linie.append(f"   🔴 DŁUG HONOROWY (oko za oko niespłacone): {len(dlug)}")
        for r in dlug:
            linie.append(f"      • [{r['id']}] {r['opis']}  ({r['data']})")
    else:
        linie.append("   ✅ Dług honorowy: BRAK — każdy błąd spłacony unikatem")
    # Odroczone drukujemy ZAWSZE i osobno — inaczej odroczenie stałoby się cichym
    # umorzeniem, czyli dokładnie tym, przed czym LEX TALIONIS ma bronić.
    for r in odroczone(sciezka):
        linie.append(f"   ⏳ ODROCZONE decyzją Cezara (dług trwa): [{r['id']}] "
                     f"{r['opis'][:110]}  ({r['data']})")
    return "\n".join(linie)


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="CODEX NOTARUM — noty pracy (LEX TALIONIS)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("bilans", help="pokaż bilans not i dług honorowy")
    pn = sub.add_parser("nota", help="dopisz zatwierdzony błąd (−)")
    pn.add_argument("--opis", required=True)
    pn.add_argument("--kategoria", default="")
    pn.add_argument("--zatwierdzenie", required=True)
    pn.add_argument("--sesja", required=True)
    pn.add_argument("--waga", type=int, default=1)
    pn.add_argument("--zrodlo", default="")
    pc = sub.add_parser("corona", help="dopisz zatwierdzony unikat (+); --splaca id_noty")
    pc.add_argument("--opis", required=True)
    pc.add_argument("--kategoria", default="")
    pc.add_argument("--zatwierdzenie", required=True)
    pc.add_argument("--sesja", required=True)
    pc.add_argument("--splaca", default=None)
    pc.add_argument("--waga", type=int, default=1)
    pc.add_argument("--zrodlo", default="")
    po = sub.add_parser("odroczenie",
                        help="odrocz spłatę NOTY na następną wachtę (WYŁĄCZNIE decyzja Cezara)")
    po.add_argument("--nota", required=True)
    po.add_argument("--zatwierdzenie", required=True)
    po.add_argument("--sesja", required=True)
    po.add_argument("--plan", required=True, help="czym i kiedy dług zostanie spłacony")
    po.add_argument("--zrodlo", default="")
    args = p.parse_args(argv)

    if args.cmd == "odroczenie":
        oid = dodaj_odroczenie(nota=args.nota, zatwierdzenie=args.zatwierdzenie,
                               sesja=args.sesja, plan=args.plan, zrodlo=args.zrodlo)
        print(f"ODROCZENIE zapisane: {oid} (dług NIE znika — patrz `bilans`)")
        return 0

    if args.cmd == "nota":
        nid = dodaj_nota(opis=args.opis, kategoria=args.kategoria,
                         zatwierdzenie=args.zatwierdzenie, sesja=args.sesja,
                         waga=args.waga, zrodlo=args.zrodlo)
        print(f"NOTA zapisana: {nid}")
    elif args.cmd == "corona":
        cid = dodaj_corona(opis=args.opis, kategoria=args.kategoria,
                           zatwierdzenie=args.zatwierdzenie, sesja=args.sesja,
                           splaca=args.splaca, waga=args.waga, zrodlo=args.zrodlo)
        print(f"CORONA zapisana: {cid}")
    print(raport())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
