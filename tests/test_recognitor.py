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


# ── FENESTRA RECOGNITIONIS — rozkład po całej historii (2026-08-06) ──────────
# Pojedynczy PR bez recenzji wygląda na potknięcie; dopiero rozkład pokazuje regułę.
# Zmierzone na 141 PR: 92 bez recenzji, 36 z recenzją PO MERGU, 10 na czas (7,1%).
# Testy pilnują GRANICY MIĘDZY „pokryte" A „pokryte NA CZAS" — bo pierwsza wersja
# miernika ich nie rozróżniała i chwaliła proces za recenzje kodu, który już wszedł.

def _pr(nr, *, utworzony="2026-08-01T10:00:00Z", zmergowany="2026-08-01T11:00:00Z",
        head="aaa", recenzje=()):
    return {"numer": nr, "utworzony": utworzony, "zmergowany": zmergowany,
            "head": head, "recenzje": list(recenzje)}


def _rec(commit="aaa", kiedy="2026-08-01T10:30:00Z", kto="cubic-dev-ai[bot]"):
    return {"commit": commit, "kiedy": kiedy, "recenzent": kto}


def test_historia_liczy_recenzje_na_czas():
    """Recenzja na commicie gałęzi ZŁOŻONA PRZED mergem — jedyny przypadek pełnego sukcesu."""
    w = rec.ocen_historie([_pr(1, recenzje=[_rec()])])
    assert w["pokryte"] == 1 and w["pokryte_przed_mergem"] == 1
    assert w["recenzja_po_mergu"] == 0
    assert w["odsetek_na_czas"] == 100.0
    assert w["niepokryte_numery"] == []


def test_recenzja_po_mergu_nie_jest_sukcesem():
    """SEDNO poprawki: recenzja pokrywająca commit, ale złożona PO mergu, opisuje kod,
    który już wszedł do `main`. Liczy się jako `pokryte`, ale NIGDY jako `na czas`."""
    w = rec.ocen_historie([_pr(1, zmergowany="2026-08-01T10:00:00Z",
                               recenzje=[_rec(kiedy="2026-08-01T12:00:00Z")])])
    assert w["pokryte"] == 1           # commit się zgadza…
    assert w["pokryte_przed_mergem"] == 0   # …ale nikogo nie ochroniła
    assert w["recenzja_po_mergu"] == 1
    assert w["niepokryte_numery"] == [1]


def test_granica_sekundy_wokol_mergu():
    """TEST GRANICY (Prawo XXI): sekunda przed mergem to sukces, sekunda po — spóźnienie.
    Bez tego progu 'na czas' byłoby uznaniowe."""
    tuz_przed = rec.ocen_historie([_pr(1, zmergowany="2026-08-01T11:00:00Z",
                                       recenzje=[_rec(kiedy="2026-08-01T10:59:59Z")])])
    tuz_po = rec.ocen_historie([_pr(1, zmergowany="2026-08-01T11:00:00Z",
                                    recenzje=[_rec(kiedy="2026-08-01T11:00:01Z")])])
    rowno = rec.ocen_historie([_pr(1, zmergowany="2026-08-01T11:00:00Z",
                                   recenzje=[_rec(kiedy="2026-08-01T11:00:00Z")])])
    assert tuz_przed["pokryte_przed_mergem"] == 1
    assert tuz_po["pokryte_przed_mergem"] == 0 and tuz_po["recenzja_po_mergu"] == 1
    # Równo w chwili mergu liczymy jako NA CZAS — spóźnienie musi być ściśle dodatnie,
    # inaczej zaokrąglenie znacznika GitHuba do sekundy karałoby recenzenta za remis.
    assert rowno["pokryte_przed_mergem"] == 1 and rowno["recenzja_po_mergu"] == 0


def test_pr_otwarty_nie_jest_spozniony():
    """GRANICA: PR bez daty mergu nic jeszcze nie wpuścił do `main`, więc recenzja
    nie może być 'po mergu'. Inaczej każdy otwarty PR fałszywie psułby statystykę."""
    w = rec.ocen_historie([_pr(1, zmergowany="", recenzje=[_rec()])])
    assert w["recenzja_po_mergu"] == 0
    assert w["pokryte_przed_mergem"] == 1


def test_recenzja_na_starszym_commicie_nie_pokrywa():
    """Klasa PR #134: recenzja BYŁA, tylko trzy commity wcześniej."""
    w = rec.ocen_historie([_pr(1, head=OB8, recenzje=[_rec(commit=BFB)])])
    assert w["z_recenzja"] == 1
    assert w["pokryte"] == 0 and w["pokryte_przed_mergem"] == 0
    assert w["niepokryte_numery"] == [1]


def test_pr_bez_recenzji_wpada_do_niepokrytych():
    w = rec.ocen_historie([_pr(1), _pr(2, recenzje=[_rec()])])
    assert w["bez_recenzji"] == 1 and w["z_recenzja"] == 1
    assert w["niepokryte_numery"] == [1]
    assert w["odsetek_na_czas"] == 50.0


def test_recenzent_spoza_listy_sie_nie_liczy():
    """Milczenie PILNOWANEGO recenzenta to luka — komentarz kogoś innego jej nie zamyka."""
    w = rec.ocen_historie([_pr(1, recenzje=[_rec(kto="ktos-inny")])])
    assert w["z_recenzja"] == 0 and w["bez_recenzji"] == 1


def test_mediana_i_pusta_historia():
    assert rec.mediana([]) is None
    assert rec.mediana([5]) == 5
    assert rec.mediana([1, 3]) == 2          # parzysta — średnia środkowych
    assert rec.mediana([9, 1, 5]) == 5       # sortuje sama
    assert rec.mediana([None, 4, None]) == 4  # braki pomijane, nie zerowane
    pusta = rec.ocen_historie([])
    assert pusta["ogolem"] == 0 and pusta["odsetek_na_czas"] is None


# ── PIĘĆ WAD Z WŁASNEJ RECENZJI ADVERSARIALNEJ (2026-08-06 → naprawa 2026-08-07) ──
# Wszystkie były MOJE i wszystkie mieszczą się w jednej klasie: BRAK DANYCH UDAJĄCY SUKCES —
# czyli dokładnie tym, czego ten organ ma pilnować u innych. Testy poniżej odtwarzają stan
# SPRZED naprawy, żeby powrót wady był czerwony, a nie cichy.

def test_szkic_recenzji_nie_zielenil_BRAMKI():
    """WADA 1, ŚCIEŻKA BRAMKOWA — groźniejsza niż zgłoszona i znaleziona dopiero pomiarem.

    Recenzja zgłosiła ślepy punkt w `ocen_historie` (miernik). Pomiar przed naprawą pokazał
    go TAKŻE w `ocen_pokrycie`, czyli tam, gdzie kod wyjścia zieleni `/limes`: szkic recenzji
    (`submitted_at = null`, stan PENDING) stojący na HEADzie dawał `pokryte, exit 0`.
    ROZPOCZĘCIE pisania recenzji zwalniało bramkę mocniej niż jej ZŁOŻENIE."""
    szkic = [{"commit": OB8, "kiedy": "", "recenzent": "cubic-dev-ai[bot]"}]
    w = rec.ocen_pokrycie(head=OB8, recenzje=szkic, commity_po=[], stan_pr="OPEN", pr_numer=142)
    assert w["status"] == "recenzja_niezlozona"
    assert w["exit"] == 1, "szkic recenzji NIE MA PRAWA zwolnić bramki"
    assert "PENDING" in w["opis"]


def test_zlozona_recenzja_bije_szkic_przy_wyborze_najnowszej():
    """GRANICA DRUGIEJ STRONY: filtr szkiców nie może wyciąć PRAWDZIWEJ recenzji.
    PR ze szkicem OBOK złożonej recenzji jest nadal pokryty — inaczej naprawa
    zamieniłaby fałszywą zieleń na fałszywą czerwień."""
    mieszane = [{"commit": OB8, "kiedy": "", "recenzent": "cubic-dev-ai[bot]"},
                {"commit": OB8, "kiedy": "2026-07-27T10:34:58Z", "recenzent": "cubic-dev-ai[bot]"}]
    w = rec.ocen_pokrycie(head=OB8, recenzje=mieszane, commity_po=[], stan_pr="OPEN", pr_numer=142)
    assert w["status"] == "pokryte" and w["exit"] == 0


def test_szkic_recenzji_nie_liczy_sie_jako_na_czas():
    """WADA 1, ŚCIEŻKA MIERNIKA — odtworzony PR #142: utworzony 18:11:03, zmergowany
    18:11:20 (SIEDEMNAŚCIE SEKUND), zero złożonych recenzji. Przed naprawą
    `_sekundy(...) or 0` zamieniało BRAK daty w zero sekund, więc `0 > 0` było fałszem,
    PR nie był „spóźniony" i wychodziło `odsetek_na_czas = 100%` dla kodu, którego NIKT
    nie przejrzał. Miernik chwalił proces właśnie tam, gdzie ten zawiódł najmocniej."""
    w = rec.ocen_historie([_pr(142, utworzony="2026-08-06T18:11:03Z",
                               zmergowany="2026-08-06T18:11:20Z",
                               recenzje=[_rec(kiedy="")])])
    assert w["pokryte_przed_mergem"] == 0
    assert w["odsetek_na_czas"] == 0.0
    assert w["recenzje_niezlozone"] == 1, "odrzucony szkic musi być WIDOCZNY, nie wycięty w ciszy"
    assert w["bez_recenzji"] == 1 and w["z_recenzja"] == 0
    assert w["niepokryte_numery"] == [142]
    assert "SZKICEM" in rec.raport_historii(w)


def test_nieporownywalny_znacznik_czasu_nie_jest_sukcesem():
    """TA SAMA KLASA NA SĄSIEDNIM WEJŚCIU: zepsuty znacznik mergu też dawał `None`, które
    `or 0` zamieniało w „zdążył". Nieporównywalna data to NIEWIEDZA — nie wolno jej
    zaliczyć na czas i nie wolno jej przemilczeć."""
    w = rec.ocen_historie([_pr(1, zmergowany="ZEPSUTA-DATA", recenzje=[_rec()])])
    assert w["pokryte"] == 1                  # commit się zgadza…
    assert w["pokryte_przed_mergem"] == 0     # …ale czasu NIE ZMIERZYLIŚMY
    assert w["czas_nieporownywalny"] == 1
    assert "nieporównywalnymi" in rec.raport_historii(w)


def test_liczba_z_docstringu_zgadza_sie_z_kodem():
    """WADA 2: docstring `ocen_historie` głosił „13 ze 141 (9,2%)", a ten sam kod na tym
    samym repo zwracał 10 (7,1%) — liczba pochodziła z ręcznego rachunku sprzed dodania
    warunku `kryje_commit`. Klasa Warstwy 23 (liczby w prozie ≠ kod) w docstringu `.py`,
    którego W23 NIE SKANUJE. Test odtwarza deklarowany pomiar z kodu zamiast ufać prozie."""
    pry = ([_pr(i, recenzje=[_rec()]) for i in range(10)]          # 10 na czas
           + [_pr(100 + i, zmergowany="2026-08-01T10:00:00Z",
                  recenzje=[_rec(kiedy="2026-08-01T12:00:00Z")]) for i in range(36)]  # po mergu
           + [_pr(200 + i) for i in range(95)])                    # bez recenzji
    w = rec.ocen_historie(pry)
    assert w["ogolem"] == 141 and w["pokryte_przed_mergem"] == 10
    assert w["odsetek_na_czas"] == 7.1, "liczba w docstringu musi być TĄ, którą zwraca kod"
    tekst = rec.ocen_historie.__doc__
    assert "10 ze 141 PR (7,1%)" in tekst
    # Obalonej liczby NIE kasujemy — zapis własnego błędu jest wart więcej niż czysta karta.
    # Warunek pilnuje więc KONTEKSTU, nie tokenu: „9,2%" wolno stać wyłącznie PO zdaniu,
    # które ją unieważnia. (Ta sama różnica, na której INDEX FALSORUM potyka się dziś,
    # zgłaszając jako fałsz trzy miejsca, które fałsz OBALAJĄ.)
    unieważnienie = tekst.find("BYŁA W TYM DOCSTRINGU FAŁSZYWA")
    assert unieważnienie > 0, "obalona liczba musi być JAWNIE oznaczona jako obalona"
    assert tekst.find("9,2%") > unieważnienie, "obalona liczba nie może stać jako aktualna"


def test_miara_glowna_jest_ta_surowsza():
    """WADA 5: obok siebie stały `odsetek_pokrycia` (32,6%, wlicza recenzje PO mergu)
    i `odsetek_na_czas` (7,1%). Nic nie mówiło, która jest miarą sukcesu — wystarczyłaby
    jedna wygodna edycja nagłówka, żeby miernik zaczął chwalić, i żaden test by nie zapłonął.
    Teraz zwycięzca jest DANĄ, nagłówek go CZYTA, a łagodniejsza liczba nigdy nie jest niższa."""
    w = rec.ocen_historie([_pr(1, zmergowany="2026-08-01T10:00:00Z",
                               recenzje=[_rec(kiedy="2026-08-01T12:00:00Z")]),
                           _pr(2, recenzje=[_rec()])])
    assert w["miara_glowna"] == "odsetek_na_czas"
    assert w["odsetek_pokrycia"] >= w["odsetek_na_czas"], "pochlebna miara nie może być surowsza"
    assert f"({w['odsetek_na_czas']}%)" in rec.raport_historii(w), "nagłówek czyta miarę główną"


def test_historia_z_bramka_ODMAWIA_zamiast_milczec():
    """WADA 4: `historia --bramka` kończyło `sys.exit(0)` PRZED spojrzeniem na flagę —
    CLI przyjmowało ją i nie robiło NIC. Wpięta w bramkę dawałaby wieczną zieleń.
    Świadoma decyzja („to miernik, nie bramka") musi ODMAWIAĆ głośno, nie milczeć."""
    import subprocess
    p = subprocess.run([sys.executable, "-m", "imperium.pretorianie.recognitor",
                        "historia", "--bramka"], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=60)
    assert p.returncode == 2, "cicha akceptacja ignorowanej flagi to fałszywy spokój"
    assert "NIE JEST bramką" in (p.stderr or "")


def test_okno_liczone_w_sekundach():
    assert rec._sekundy("2026-08-01T10:00:00Z", "2026-08-01T10:00:35Z") == 35
    assert rec._sekundy("", "2026-08-01T10:00:00Z") is None   # brak daty ≠ zero
    assert rec._sekundy("2026-08-01T10:00:00Z", "zepsuta") is None
