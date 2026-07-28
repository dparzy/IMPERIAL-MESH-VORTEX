"""Testy RECOGNITORA — bramki „czy recenzja pokrywa dzisiejszy HEAD".

Organ powstał z KONKRETNEGO przeoczenia (PR #134, 2026-07-27): recenzent wykonał jeden
przebieg wobec `bfb5e26`, po czym weszły trzy commity i PR został zmergowany. Pytanie
Cezara „czy znalazł nowe błędy" dostało odpowiedź „nie", bo nikt nie sprawdził, czy
recenzent w ogóle patrzył. Dlatego testy pilnują nie tylko dodatniego przypadku, ale
przede wszystkim GRANICY: żaden stan niepewności nie ma prawa wyjść zielony.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.pretorianie import recognitor as rec  # noqa: E402

# Prawdziwe skróty z PR #134 — przypadek z historii, nie wymyślony.
BFB = "bfb5e269f6c1fc34a7781f6b3e6ffc32367fb5af"
OB8 = "0b85b81d5b1520c8af5c3b57ccfc138512d479c6"
CUBIC = [{"commit": BFB, "kiedy": "2026-07-27T10:34:58Z", "recenzent": "cubic-dev-ai[bot]"}]


def test_pokryte_gdy_recenzja_stoi_na_head():
    w = rec.ocen_pokrycie(head=BFB, recenzje=CUBIC, commity_po=[], stan_pr="OPEN", pr_numer=134)
    assert w["status"] == "pokryte"
    assert w["exit"] == 0
    assert w["ile_po"] == 0


def test_luka_zamknieta_odtwarza_przypadek_PR_134():
    """Trzy commity weszły PO jedynym przebiegu, PR zmergowany — luka nieodwracalna.

    To jest dokładnie ten stan, którego nikt nie zauważył: brak nowych uwag wyglądał
    identycznie jak brak wad."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, stan_pr="MERGED", pr_numer=134,
                          commity_po=["0b85b81 Domkniecie wachty nomen27",
                                      "bc4913c NOMENCLATOR + U4 OFF",
                                      "4c7aa70 auto: sync pamieci sesji"])
    assert w["status"] == "luka_zamknieta"
    assert w["exit"] == 1
    assert w["ile_po"] == 3
    assert w["naprawialne"] is False, "zmergowanego PR nie da się naprawić pushem — organ musi to mówić"
    assert w["recenzowany"] == BFB


def test_zmergowany_PR_ale_galaz_poszla_dalej_JEST_naprawialna():
    """Wada znaleziona przez UŻYCIE organu w domknięciu, pierwszego dnia jego życia.

    Werdykt „nowy PR pokaże zero różnicy" jest prawdziwy TYLKO gdy HEAD stoi na commicie,
    który wszedł do mergu. Gdy gałąź poszła dalej, nowe commity obejmie NOWY PR — a organ
    odradzał wtedy jedyną skuteczną drogę. Strażnik mówiący „nie da się" tam, gdzie się da,
    zniechęca do naprawy, więc jest gorszy od milczenia."""
    w = rec.ocen_pokrycie(head="9999999", recenzje=CUBIC, stan_pr="MERGED", pr_numer=134,
                          head_pr=OB8, commity_po=["9999999 nowa praca po mergu"])
    assert w["status"] == "luka_otwarta"
    assert w["naprawialne"] is True
    assert "NOWY PR" in w["opis"]


def test_zmergowany_PR_na_commicie_mergu_JEST_nieodwracalny():
    """GRANICA DRUGIEJ STRONY: gdy HEAD == head PR-a, luka naprawdę jest nie do odrobienia —
    zawężanie na oślep skasowałoby prawdziwe ostrzeżenie z PR #134."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, stan_pr="MERGED", pr_numer=134,
                          head_pr=OB8, commity_po=["0b85b81 domkniecie", "bc4913c organ"])
    assert w["status"] == "luka_zamknieta"
    assert w["naprawialne"] is False
    assert "NIEODWRACALNA" in w["opis"]


def test_luka_otwarta_jest_naprawialna_pushem():
    w = rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, stan_pr="OPEN", pr_numer=134,
                          commity_po=["bc4913c NOMENCLATOR"])
    assert w["status"] == "luka_otwarta"
    assert w["exit"] == 1
    assert w["naprawialne"] is True


def test_brak_recenzji_nie_jest_zielony():
    """Cisza recenzenta to brak spojrzenia, nie brak wad — sedno klasy wady."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=[], commity_po=[], stan_pr="OPEN", pr_numer=134)
    assert w["status"] == "brak_recenzji"
    assert w["exit"] == 1


def test_niezmierzone_nigdy_nie_udaje_zielonego():
    """Brak `gh`/sieci musi być WIDOCZNY jako niewiedza (Prawo I), nie jako zgoda."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=[], commity_po=None, stan_pr="",
                          gh_ok=False, powod_bledu="brak narzędzia `gh` w PATH")
    assert w["status"] == "niezmierzone"
    assert w["exit"] == 2
    assert "gh" in w["opis"]


def test_commit_recenzji_nieobecny_lokalnie_to_niewiedza():
    """Force-push kasuje recenzowany commit — wtedy pokrycia NIE DA SIĘ policzyć."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, commity_po=None, stan_pr="OPEN", pr_numer=134)
    assert w["status"] == "commit_nieznany"
    assert w["exit"] == 2


def test_brak_pr_jest_stanem_normalnym():
    """Praca lokalna bez PR nie ma recenzenta, więc nie ma czyjego milczenia źle odczytać."""
    w = rec.ocen_pokrycie(head=OB8, recenzje=[], commity_po=[], stan_pr="", pr_numer=None)
    assert w["status"] == "brak_pr"
    assert w["exit"] == 0


def test_liczy_sie_NAJNOWSZA_recenzja_nie_ostatnia_na_liscie():
    """GitHub nie gwarantuje porządku — sortujemy po czasie, inaczej stara recenzja
    mogłaby zaświadczyć pokrycie nowego commita."""
    recenzje = [{"commit": OB8, "kiedy": "2026-07-27T12:00:00Z", "recenzent": "cubic-dev-ai[bot]"},
                {"commit": BFB, "kiedy": "2026-07-27T10:34:58Z", "recenzent": "cubic-dev-ai[bot]"}]
    w = rec.ocen_pokrycie(head=OB8, recenzje=recenzje, commity_po=[], stan_pr="OPEN", pr_numer=134)
    assert w["status"] == "pokryte"


def test_recenzja_obcego_autora_nie_zalicza_pokrycia():
    """Pilnujemy MILCZENIA KONKRETNEGO recenzenta. Zatwierdzenie przez kogoś innego nie
    zastępuje przebiegu bota — inaczej własne `approve` gasiłoby bramkę."""
    w = rec.ocen_pokrycie(head=OB8, stan_pr="OPEN", pr_numer=134, commity_po=[],
                          recenzje=[{"commit": OB8, "kiedy": "2026-07-27T12:00:00Z",
                                     "recenzent": "Pixel"}])
    assert w["status"] == "brak_recenzji"
    assert w["exit"] == 1


def test_granica_zielone_tylko_dla_dwoch_stanow():
    """REGUŁA TEST-GRANIC: bramka wolna od fałszywego spokoju. Kod 0 mają PRAWO mieć
    wyłącznie `pokryte` (zmierzone pokrycie) i `brak_pr` (nie ma recenzenta). Gdyby ktoś
    dopisał status i zapomniał o kodzie wyjścia, ten test go zatrzyma."""
    przypadki = [
        rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, commity_po=["x y"], stan_pr="OPEN", pr_numer=1),
        rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, commity_po=["x y"], stan_pr="MERGED", pr_numer=1),
        rec.ocen_pokrycie(head=OB8, recenzje=[], commity_po=[], stan_pr="OPEN", pr_numer=1),
        rec.ocen_pokrycie(head=OB8, recenzje=CUBIC, commity_po=None, stan_pr="OPEN", pr_numer=1),
        rec.ocen_pokrycie(head=OB8, recenzje=[], commity_po=None, stan_pr="", gh_ok=False),
    ]
    for w in przypadki:
        assert w["exit"] != 0, f"status {w['status']} nie ma prawa być zielony"
        assert w["status"] not in ("pokryte", "brak_pr")


def test_banner_jest_jednolinijkowy():
    """ZASADA WYDRUKU: organ w bramce drukuje JEDNĄ linię (koszt kontekstu jest mierzony)."""
    w = rec.ocen_pokrycie(head=BFB, recenzje=CUBIC, commity_po=[], stan_pr="OPEN", pr_numer=134)
    assert "\n" not in rec.banner(w)
