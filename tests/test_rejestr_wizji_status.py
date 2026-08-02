"""Spójność TYPU i STATUSU w rejestrze wizji — wpis nie może przeczyć sam sobie.

POWÓD ZMIERZONY (recenzja cubic PR #138, uwaga J5 — i jej zasięg był większy niż uwaga):
recenzent wskazał JEDEN wpis „ZMIANA ze statusem POMYSŁ", którego treść mówiła „dodano
obsługę, testy zielone". Policzenie całego ledgera pokazało **56 z 1013** takich wpisów
(44 × ZMIANA+POMYSŁ, 12 × DECYZJA+POMYSŁ) — czyli klasę, nie incydent.

Przyczyna nie leżała w danych, tylko w DWÓCH domyślnych wartościach:
  • `rejestr_wizji.dodaj(status="POMYSŁ")` — jedna stała dla wszystkich typów,
  • `auto_lekcja` przy `ValueError` ratował się twardym `status="POMYSŁ"`.
Oba naprawione: status domyślny jest teraz WYWODZONY Z TYPU i odtwarza kanon zmierzony
w tych samych danych (ZMIANA→WDROŻONA 444, DECYZJA→ZAMKNIĘTA 201, POMYSŁ→POMYSŁ 200,
WIZJA→PLANOWANE 111 — 94,5% rejestru).
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imperium.biblioteki import rejestr_wizji as rw  # noqa: E402


def _tmp():
    return Path(tempfile.mkdtemp()) / "wizje.jsonl"


def _ostatni(plik):
    import json
    return json.loads(plik.read_text(encoding="utf-8").splitlines()[-1])


def test_status_domyslny_wywodzi_sie_z_typu():
    """Sedno naprawy: brak jawnego statusu NIE oznacza „zamiar" dla rzeczy dokonanej."""
    plik = _tmp()
    for typ, oczekiwany in (("ZMIANA", "WDROŻONA"), ("DECYZJA", "ZAMKNIĘTA"),
                            ("WIZJA", "PLANOWANE"), ("POMYSŁ", "POMYSŁ")):
        rw.dodaj(typ, f"Tytuł {typ}", f"treść {typ}", plik=plik, dedup=False)
        assert _ostatni(plik)["status"] == oczekiwany, typ


def test_zmiana_z_etykieta_zamiaru_jest_odrzucana():
    """Wpis mówiący „zrobione" ze statusem „POMYSŁ" nie pozwala czytelnikowi rozstrzygnąć,
    czy to fakt, czy propozycja — a rejestr istnieje po to, żeby nie wracać do zamkniętych
    tematów (Prawo XV)."""
    plik = _tmp()
    for typ in ("ZMIANA", "DECYZJA"):
        try:
            rw.dodaj(typ, f"Sprzeczny {typ}", "treść", status="POMYSŁ",
                     plik=plik, dedup=False)
            raise AssertionError(f"{typ} + POMYSŁ przeszło bez słowa")
        except ValueError as e:
            assert "sprzeczn" in str(e).lower(), str(e)


def test_legalne_kombinacje_nadal_przechodza():
    """Bramka jest WĄSKA z rozmysłu — blokuje wyłącznie parę wskazaną pomiarem.
    `POMYSŁ + ZAWIESZONA` występuje w ledgerze (1 raz) i jest sensowne."""
    plik = _tmp()
    rw.dodaj("POMYSŁ", "Odłożony pomysł", "treść", status="ZAWIESZONA",
             plik=plik, dedup=False)
    assert _ostatni(plik)["status"] == "ZAWIESZONA"
    rw.dodaj("ZMIANA", "Cofnięta zmiana", "treść", status="ODRZUCONA",
             plik=plik, dedup=False)
    assert _ostatni(plik)["status"] == "ODRZUCONA"


def test_kanon_domyslnych_zgadza_sie_ze_slownikami():
    """Niezmiennik: każdy typ ma domyślny status, i żaden domyślny nie jest sprzeczny
    z własnym typem (inaczej `dodaj` bez statusu rzucałby wyjątkiem)."""
    for typ in rw.TYPY_DOZWOLONE:
        domyslny = rw.STATUS_DOMYSLNY.get(typ)
        assert domyslny, f"typ {typ} bez domyślnego statusu"
        assert domyslny in rw.STATUSY_DOZWOLONE
        assert domyslny not in rw.STATUSY_SPRZECZNE.get(typ, ())
