"""
🏛️ TABULARIUM — archiwum państwowe Imperium: rejestr wszystkich żywych dokumentów.

Rzymskie Tabularium na Kapitolu przechowywało oficjalne rejestry państwa; porządku
pilnował CENZOR — urzędnik od spisu i regimen morum. To narzędzie robi to samo dla
dokumentacji: każdy żywy dokument DEKLARUJE SAM SIEBIE w nagłówku, a Tabularium
sprawdza deklaracje i GENERUJE katalog.

DLACZEGO ISTNIEJE (dowód, nie opinia — Prawo I):
Ręcznie pisany indeks kłamie z definicji. 2026-07-17 INDEKS_IMPERIUM.md twierdził
„299 mikro-neuronów (72 w kodzie)" przy 87 w kodzie — i przechodził audyt na zielono,
bo bramka W5 czytała liczbę z innej sekcji tego samego pliku. Dokument bez metadanych
jest dla audytu nieprzezroczysty: każda bramka to osobne, ręcznie dopisane wyrażenie.
Metadane odwracają ciężar dowodu — dokument mówi, czym jest, a maszyna to weryfikuje.

TRZY BRAMKI (Prawo XXI — spójność mierzona):
  1. DEKLARACJA — żywy dokument ma nagłówek: kategoria ze słownika, typ, właściciel,
     stan_na, powód istnienia. Brak nagłówka = dokument, którego nikt nie pilnuje.
  2. GNICIE — jeśli `wlasciciel` (plik kodu) zmienił się PO dacie `stan_na`, opis nie
     nadąża za kodem. To ostrzejsze niż W6b, która porównuje dokument z jego WŁASNĄ
     zmianą (poprawka literówki zerowała zegar → fałszywa zieleń).
  3. DUBLET — dwa żywe dokumenty o tej samej kategorii i tym samym właścicielu opisują
     ten sam kod dwa razy (Prawo XVI: redundancja mierzona, nie zgadywana).

ZASADA WPIĘCIA: domyślnie tryb MIĘKKI (raportuje, nie wywraca commita). Twardy dopiero
po spłacie długu — inaczej bramka zablokowałaby każdy commit w dniu wdrożenia.

Uruchom:  python narzedzia/tabularium.py sprawdz
          python narzedzia/tabularium.py sprawdz --twardy    # exit 1 przy błędach
          python narzedzia/tabularium.py katalog             # generuj katalog na stdout
          python narzedzia/tabularium.py katalog --zapisz     # wstaw do INDEKS_IMPERIUM
          python narzedzia/tabularium.py dublety             # kandydaci do scalenia
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date, timedelta

_s = getattr(sys, "stdout", None)
if _s is not None and hasattr(_s, "reconfigure"):
    try:
        _s.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:  # noqa: BLE001 — brak reconfigure → zostaje domyślne kodowanie
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)   # bez tego `liczby` nie zaimportuje rejestru (jak audyt_spojnosci)

# ── SŁOWNIK ZAMKNIĘTY (rzymski, dobrany do funkcji — ZASADA NOMENKLATURY) ──────
# Zamknięty, bo otwarty słownik zamienia się w śmietnik: każdy nowy dokument
# wymyślałby własną kategorię i katalog znów przestałby cokolwiek porządkować.
KATEGORIE = {
    "LEX":        "prawo i rozkazy stałe — obowiązuje, nie opisuje",
    "TABULA":     "rejestr / źródło prawdy o kodzie — musi zgadzać się 1:1",
    "FORMA":      "opis budowy organu — jak moduł jest zbudowany",
    "DISCIPLINA": "manual — jak coś zrobić krok po kroku",
    "CONSILIUM":  "plan / wizja — zamiar na przyszłość, nie fakt",
    "MENSURA":    "pomiar / analiza z danych — wynik, nie opinia",
    "ACTA":       "datowana historia — prawda swojego czasu (Prawo I: nie tykamy)",
}
TYPY = {"zywy", "acta"}
POLA_WYMAGANE = ("kategoria", "typ", "wlasciciel", "stan_na", "powod_istnienia")

# Poza rejestrem — każde z własnymi zasadami, Tabularium pilnuje ŻYWEJ dokumentacji:
#   archiwum/          — magazyn, otwierany na rozkaz Cezara (ZASADA ARCHIWIZACJI)
#   bibliotheca_ulpia/ — księgozbiór i kronika sesji: historia, Prawo I zabrania tykać
#   wrzutnia/          — skrzynka wejściowa, treść surowa przed obróbką
#   .claude/           — konfiguracja harnessa; agenci mają WŁASNY nagłówek (name/tools),
#                        który Tabularium wzięłoby za deklarację dokumentu
#   dane/              — katalogi danych; README to drogowskaz („tu wrzucasz CSV"), nie opis
POZA_REJESTREM = ("archiwum", "bibliotheca_ulpia", "wrzutnia", ".claude", "dane",
                  ".git", ".pytest_cache", "node_modules", "__pycache__")

ZNACZNIK_START = "<!-- TABULARIUM:start — sekcja generowana, NIE edytuj ręcznie -->"
ZNACZNIK_KONIEC = "<!-- TABULARIUM:koniec -->"

# ── LICZBY WSTRZYKIWANE (Filar 4) ────────────────────────────────────────────
# Ręcznie wpisana liczba w dokumencie ZAWSZE się rozjedzie — bo rośnie kod, a nie
# dokument. Zmierzone 2026-07-17: trzy dokumenty podawały „neuronów w kodzie" jako
# 47, 27 i 55, przy 87 w rejestrze. Każda z nich była prawdziwa w dniu pisania.
# Lekarstwo nie polega na poprawieniu liczb (za miesiąc znów skłamią), tylko na
# ODEBRANIU dokumentom prawa do ich wpisywania: liczba żyje między znacznikami
# i jest przepisywana z żywego kodu.
#     Użycie w dokumencie:  <!-- LICZBA:neurony -->87<!-- /LICZBA -->
#
# Treść bloku NIE MOŻE zawierać `<!--` — inaczej otwarcie bez własnego domknięcia sklei się
# z domknięciem NASTĘPNEGO bloku i `sub()` skasuje wszystko pomiędzy. Zmierzone 2026-07-17:
# jeden niedomknięty znacznik zacytowany w LOG_ZMIAN zjadł 44 linie historii (Prawo I).
# Granica bloku, nie „najbliższy pasujący ogon” — regex bez tego ograniczenia jest nożem.
LICZBA_WZORZEC = re.compile(
    r"<!--\s*LICZBA:(\w+)\s*-->((?:(?!<!--)[\s\S])*?)<!--\s*/LICZBA\s*-->"
)


def policz_prawa():
    """Liczba Praw Imperium — liczona z ZASADY_FUNDAMENTALNE.md (źródło prawdy LEX).

    JEDEN parser dla całego Imperium (Prawo XVI: jeden format = jeden parser; dwa
    rozjadą się co do znaku). Audyt (W10) woła tę funkcję zamiast trzymać własny regex.
    Historia: bramka W10 miała kiedyś liczbę praw ZASZYTĄ i żądała „21", gdy praw było 25
    — egzekwowała kłamstwo. Zaszyta liczba MUSI się zestarzeć.
    """
    with open(os.path.join(ROOT, "ZASADY_FUNDAMENTALNE.md"), encoding="utf-8") as f:
        return len(set(re.findall(r"PRAWO\s+([IVXL]+)\b", f.read())))


def wartosci_z_kodu():
    """Żywe liczby Imperium prosto ze źródeł prawdy: rejestry (kod) + ZASADY (LEX)."""
    import dataclasses

    from imperium.biblioteki.pamiec_absolutna import ImperiumLog
    from imperium.legiony.rejestr import (
        neurony_dla_trybu, raport_elity, wszystkie_neurony, wszyscy_zwiadowcy,
    )
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    neurony = wszystkie_neurony()
    return {
        "neurony": len(neurony),
        "neurony_aktywne": len([n for n in neurony if getattr(n, "DOSTEPNY", True)]),
        "zwiadowcy": len(wszyscy_zwiadowcy()),
        "strategie": len(wszystkie_strategie()),
        "elity": raport_elity()["lacznie_elite"],
        "pola_logu": len(dataclasses.fields(ImperiumLog)),
        # Profile stylu (W-323) — tabela NEURONY_STYLU jest „strojona pomiarem”, więc te
        # liczby zmieniają się przy każdym A/B. Zmierzone 2026-07-17: jeden dokument podawał
        # je kolejno jako 41/59/35, 65/65/70 i 75/75/87 — każda prawdziwa w dniu zapisu.
        "styl_scalp": len(neurony_dla_trybu("SCALP")),
        "styl_swing": len(neurony_dla_trybu("SWING")),
        "styl_invest": len(neurony_dla_trybu("INVEST")),
        "prawa": policz_prawa(),
    }


def wstrzyknij_liczby(sucho=False):
    """Przepisuje każdy blok <!-- LICZBA:x --> z żywego kodu. → (zmiany, bledy).

    Dokumenty `typ: acta` (LOG_ZMIAN, migawki) są POMIJANE: wpis datowany jest prawdą
    swojego czasu i cytuje liczby z dnia zapisu (Prawo I — nie falsyfikujemy historii).
    Bez tego filtra wpis z 2026-07-17 mówiący „87 neuronów" cicho stałby się „90", gdy rój
    urośnie — kłamstwo tym groźniejsze, że wyprodukowane przez narzędzie od prawdy.
    """
    wartosci = wartosci_z_kodu()
    zmiany, bledy = [], []
    for sciezka, meta in zbierz_dokumenty():
        if meta.get("typ") == "acta":
            continue
        pelna = os.path.join(ROOT, sciezka)
        with open(pelna, encoding="utf-8") as f:
            tresc = f.read()
        if "<!-- LICZBA:" not in tresc:
            continue

        lokalne = []

        def podmien(m, _sciezka=sciezka, _lokalne=lokalne):
            klucz, stara = m.group(1), m.group(2).strip()
            if klucz not in wartosci:
                bledy.append(f"[T4] {_sciezka}: nieznana liczba `{klucz}` "
                             f"(dostępne: {', '.join(sorted(wartosci))})")
                return m.group(0)
            nowa = str(wartosci[klucz])
            if stara != nowa:
                _lokalne.append(f"{klucz}: {stara or '—'} → {nowa}")
            return f"<!-- LICZBA:{klucz} -->{nowa}<!-- /LICZBA -->"

        nowa_tresc = LICZBA_WZORZEC.sub(podmien, tresc)
        if lokalne:
            zmiany.append(f"{sciezka}: {'; '.join(lokalne)}")
            if not sucho:
                with open(pelna, "w", encoding="utf-8") as f:
                    f.write(nowa_tresc)
    return zmiany, bledy


def _pasek(i, n, opis):
    """Pasek postępu na stderr (Prawo XXIV — widoczność operacyjna)."""
    print(f"\r[{i}/{n}] {opis[:60]:<60}", end="", file=sys.stderr, flush=True)


def czytaj_naglowek(sciezka):
    """Nagłówek metadanych z pliku .md → dict (puste, gdy brak nagłówka).

    Parser świadomie minimalny (płaskie `klucz: wartosc`) — bez zależności od pyyaml,
    bo runner Imperium ma działać bez instalacji (`python tests/run_tests.py`).
    """
    try:
        with open(sciezka, encoding="utf-8") as f:
            tresc = f.read()
    except (OSError, UnicodeDecodeError):
        return {}
    if not tresc.startswith("---"):
        return {}
    czesci = tresc.split("---", 2)
    if len(czesci) < 3:
        return {}
    meta = {}
    for linia in czesci[1].strip().splitlines():
        if ":" not in linia or linia.strip().startswith("#"):
            continue
        klucz, _, wartosc = linia.partition(":")
        wartosc = wartosc.strip().strip('"').strip("'")
        meta[klucz.strip()] = "" if wartosc in ("null", "~", "—") else wartosc
    return meta


def zbierz_dokumenty():
    """Wszystkie żywe .md Imperium → [(sciezka_wzgledna, meta)] posortowane."""
    znalezione = []
    for katalog, podkatalogi, pliki in os.walk(ROOT):
        podkatalogi[:] = [d for d in podkatalogi if d not in POZA_REJESTREM]
        for plik in pliki:
            if not plik.endswith(".md"):
                continue
            pelna = os.path.join(katalog, plik)
            wzgledna = os.path.relpath(pelna, ROOT).replace("\\", "/")
            znalezione.append((wzgledna, czytaj_naglowek(pelna)))
    return sorted(znalezione)


def _data_ostatniej_zmiany(sciezka_wzgledna):
    """Data ostatniego commitu pliku (YYYY-MM-DD) lub None, gdy brak w historii."""
    try:
        wynik = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", sciezka_wzgledna],
            capture_output=True, text=True, timeout=10, cwd=ROOT,
            encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if wynik.returncode != 0 or not wynik.stdout.strip():
        return None
    try:
        return date.fromisoformat(wynik.stdout.strip())
    except ValueError:
        return None


def _commity_wlasciciela_po(sciezka_wlasciciela, stan_na):
    """Commity właściciela z dni PÓŹNIEJSZYCH niż stan_na → dowód gnicia (nie domysł).

    GRANICA (bug złapany testem 2026-07-17): `git --since=<data>` obejmuje TEN SAM
    dzień, więc dokument zaktualizowany w jednym commicie z kodem — czyli wzorowa
    ZASADA PEŁNEJ SYMBIOZY — zapalałby się jako gnijący. Ta sama klasa fałszywek
    zmusiła nas do naprawy W6 dnia 2026-07-04. Liczymy od NASTĘPNEGO dnia:
    „stan na 17 lipca" ma pokrywać wszystko, co wydarzyło się 17 lipca.
    """
    nastepny_dzien = stan_na + timedelta(days=1)
    try:
        wynik = subprocess.run(
            ["git", "log", f"--since={nastepny_dzien.isoformat()}", "--format=%h %s",
             "--", sciezka_wlasciciela],
            capture_output=True, text=True, timeout=10, cwd=ROOT,
            encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if wynik.returncode != 0:
        return []
    return [w for w in wynik.stdout.strip().splitlines() if w.strip()]


def _wlasciciele(meta):
    """Pole `wlasciciel` → lista ścieżek (dopuszczamy kilka po przecinku)."""
    surowe = meta.get("wlasciciel", "").strip()
    if not surowe:
        return []
    return [w.strip() for w in surowe.split(",") if w.strip()]


def sprawdz(dokumenty=None):
    """Trzy bramki → (bledy, ostrzezenia, info). Nie drukuje — zwraca fakty.

    `dokumenty`: [(sciezka, meta)] do wstrzyknięcia w testach; None → skan repo.
    """
    bledy, ostrzezenia, info = [], [], []
    dokumenty = zbierz_dokumenty() if dokumenty is None else list(dokumenty)
    bez_naglowka = []

    for i, (sciezka, meta) in enumerate(dokumenty, 1):
        _pasek(i, len(dokumenty), sciezka)
        if not meta:
            bez_naglowka.append(sciezka)
            continue

        # ── BRAMKA 1: DEKLARACJA ────────────────────────────────────────────
        for pole in POLA_WYMAGANE:
            if not meta.get(pole):
                bledy.append(f"[T1] {sciezka}: brak pola `{pole}` w nagłówku")
        kategoria = meta.get("kategoria", "")
        if kategoria and kategoria not in KATEGORIE:
            bledy.append(f"[T1] {sciezka}: kategoria `{kategoria}` spoza słownika "
                         f"({'/'.join(sorted(KATEGORIE))})")
        typ = meta.get("typ", "")
        if typ and typ not in TYPY:
            bledy.append(f"[T1] {sciezka}: typ `{typ}` spoza słownika ({'/'.join(sorted(TYPY))})")

        stan_na = None
        if meta.get("stan_na"):
            try:
                stan_na = date.fromisoformat(meta["stan_na"])
            except ValueError:
                bledy.append(f"[T1] {sciezka}: stan_na `{meta['stan_na']}` nie jest datą ISO")

        zastapiony = meta.get("zastapiony_przez", "")
        if zastapiony and not os.path.exists(os.path.join(ROOT, zastapiony)):
            bledy.append(f"[T1] {sciezka}: zastapiony_przez wskazuje na nieistniejący "
                         f"`{zastapiony}`")

        # ── BRAMKA 5: UCIECZKA W HISTORIĘ ───────────────────────────────────
        # TYLNE DRZWI, które sam odkryłem 2026-07-17 przy MAPA_IMPERIUM_FLOW: przeklasyfikowanie
        # `zywy → acta` NATYCHMIAST ucisza bramkę gnicia (migawka z definicji nie gnije).
        # Czyli KAŻDY gnijący dokument da się „naprawić" ogłaszając go historią — bramka
        # z tylnymi drzwiami to bramka pozorna. Zapora: historia musi UMIEĆ SIĘ WYTŁUMACZYĆ —
        # data w nazwie (urodzona jako migawka), wskazany następca (zdegradowana świadomie),
        # albo jawny `powod_acta`. Ta sama zasada co przy `dublet_rozstrzygniety`:
        # wyciszenie bramki ZAWSZE wymaga podania powodu, który zostaje na widoku.
        if typ == "acta":
            data_w_nazwie = re.search(r"\d{4}-\d{2}-\d{2}", os.path.basename(sciezka))
            if not (data_w_nazwie or zastapiony or meta.get("powod_acta")):
                ostrzezenia.append(
                    f"[T5] {sciezka}: deklaruje się historią (typ: acta), ale nie tłumaczy "
                    f"CZEMU — brak daty w nazwie, następcy i pola `powod_acta`. Czy to naprawdę "
                    f"migawka, czy ucieczka od bramki gnicia? Dopisz `powod_acta: \"…\"` "
                    f"albo `zastapiony_przez:`")

        # ── BRAMKA 2: GNICIE (właściciel ruszył się, opis nie) ───────────────
        # ACTA pomijamy świadomie: migawka to prawda swojego czasu (Prawo I).
        # Raport AGREGOWANY per dokument (Prawo XXIV): jedna linia = jeden dokument.
        # Powód: rozbicie na (dokument × właściciel) dało 86 linii dla 20 dokumentów —
        # ściana tekstu, której nikt nie czyta, to bramka, której nikt nie słucha.
        if typ == "zywy" and stan_na and not zastapiony:
            gnijace, lacznie = [], 0
            for wlasciciel in _wlasciciele(meta):
                if not os.path.exists(os.path.join(ROOT, wlasciciel)):
                    bledy.append(f"[T2] {sciezka}: właściciel `{wlasciciel}` NIE ISTNIEJE "
                                 f"— dokument opisuje nieistniejący kod")
                    continue
                commity = _commity_wlasciciela_po(wlasciciel, stan_na)
                if commity:
                    gnijace.append((len(commity), wlasciciel))
                    lacznie += len(commity)
            if gnijace:
                gnijace.sort(reverse=True)
                szczegol = ", ".join(f"{w.split('/')[-1]} {n}×" for n, w in gnijace[:3])
                if len(gnijace) > 3:
                    szczegol += f" (+{len(gnijace) - 3})"
                ostrzezenia.append(
                    f"[T2] GNICIE {sciezka} — stan_na {stan_na}, a kod zmieniony {lacznie}× "
                    f"od tej daty w {len(gnijace)} plikach: {szczegol}")

    # ── BRAMKA 3: DUBLETY (ta sama kategoria + ten sam właściciel) ───────────
    # `dublet_rozstrzygniety: <plik> — <powód>` WYCISZA parę, którą człowiek już osądził
    # jako komplementarną. Powód (lekcja 2026-07-17): START_LOKAL („pełny przewodnik dla
    # nowicjusza") i SCIAGA_LOKAL („ściąga, 24 komendy") opisują ten sam kod, ale służą
    # różnym momentom — scalenie zabiłoby przewodnik, na którym stoi ZPO. Bez możliwości
    # zapisania werdyktu bramka krzyczałaby co sesję, a bramka krzycząca fałszywie uczy
    # ignorować WSZYSTKIE bramki. Wyciszenie wymaga PODANIA POWODU — nie da się go schować
    # po cichu, powód zostaje w nagłówku na widoku.
    wg_wlasciciela, meta_wg = {}, {}
    for sciezka, meta in dokumenty:
        if not meta or meta.get("typ") != "zywy" or meta.get("zastapiony_przez"):
            continue
        meta_wg[sciezka] = meta
        for wlasciciel in _wlasciciele(meta):
            wg_wlasciciela.setdefault((meta.get("kategoria", "?"), wlasciciel), []).append(sciezka)

    rozstrzygniete = 0
    for (kategoria, wlasciciel), pliki in sorted(wg_wlasciciela.items()):
        if len(pliki) < 2:
            continue
        sporne = [p for p in pliki
                  if not any(inny.split("/")[-1] in meta_wg[p].get("dublet_rozstrzygniety", "")
                             for inny in pliki if inny != p)]
        if len(sporne) < 2:
            rozstrzygniete += 1
            continue
        ostrzezenia.append(
            f"[T3] DUBLET: {len(sporne)} dokumenty {kategoria} opisują `{wlasciciel}` "
            f"→ {', '.join(sporne)} (kandydaci do scalenia — Prawo XVI; jeśli to świadomy "
            f"podział ról, zapisz werdykt: `dublet_rozstrzygniety: <plik> — <powód>`)")
    if rozstrzygniete:
        info.append(f"Dublety rozstrzygnięte świadomie (z powodem w nagłówku): {rozstrzygniete}")

    print("\r" + " " * 72 + "\r", end="", file=sys.stderr, flush=True)

    if bez_naglowka:
        ostrzezenia.append(
            f"[T1] {len(bez_naglowka)} dokumentów BEZ nagłówka (poza rejestrem Tabularium, "
            f"nikt nie pilnuje ich świeżości): {', '.join(bez_naglowka[:8])}"
            + (f" … +{len(bez_naglowka) - 8}" if len(bez_naglowka) > 8 else ""))

    zarejestrowane = len(dokumenty) - len(bez_naglowka)
    info.append(f"Tabularium: {zarejestrowane}/{len(dokumenty)} dokumentów zadeklarowanych")
    if zarejestrowane:
        rozklad = {}
        for _, meta in dokumenty:
            if meta.get("kategoria"):
                rozklad[meta["kategoria"]] = rozklad.get(meta["kategoria"], 0) + 1
        info.append("Rozkład: " + " | ".join(f"{k} {v}" for k, v in sorted(rozklad.items())))
    return bledy, ostrzezenia, info


def katalog_md():
    """Katalog dokumentów jako markdown — GENEROWANY, więc nie umie kłamać."""
    dokumenty = [(s, m) for s, m in zbierz_dokumenty() if m.get("kategoria") in KATEGORIE]
    linie = [ZNACZNIK_START, ""]
    linie.append(f"> 🏛️ Sekcja generowana przez `python narzedzia/tabularium.py katalog --zapisz` "
                 f"z nagłówków dokumentów. Ostatni spis: {date.today().isoformat()} "
                 f"({len(dokumenty)} pozycji).")
    linie.append("")
    for kategoria, opis in KATEGORIE.items():
        grupa = [(s, m) for s, m in dokumenty if m.get("kategoria") == kategoria]
        if not grupa:
            continue
        linie.append(f"### {kategoria} — {opis}")
        linie.append("")
        linie.append("| Dokument | Po co istnieje | Właściciel (kod) | Stan na |")
        linie.append("|---|---|---|---|")
        for sciezka, meta in sorted(grupa):
            zastapiony = meta.get("zastapiony_przez", "")
            nazwa = f"`{sciezka}`" + (f" ⛔ zastąpiony przez `{zastapiony}`" if zastapiony else "")
            wlasciciel = ", ".join(f"`{w}`" for w in _wlasciciele(meta)) or "—"
            linie.append(f"| {nazwa} | {meta.get('powod_istnienia', '—')} | {wlasciciel} "
                         f"| {meta.get('stan_na', '—')} |")
        linie.append("")
    linie.append(ZNACZNIK_KONIEC)
    return "\n".join(linie)


def zapisz_katalog(sciezka_indeksu="docs/INDEKS_IMPERIUM.md"):
    """Wstaw wygenerowany katalog między znaczniki. Zwraca (ok, komunikat)."""
    pelna = os.path.join(ROOT, sciezka_indeksu)
    if not os.path.exists(pelna):
        return False, f"Brak {sciezka_indeksu}"
    with open(pelna, encoding="utf-8") as f:
        tresc = f.read()
    if ZNACZNIK_START not in tresc or ZNACZNIK_KONIEC not in tresc:
        return False, (f"Brak znaczników w {sciezka_indeksu} — wstaw w miejscu katalogu:\n"
                       f"{ZNACZNIK_START}\n{ZNACZNIK_KONIEC}")
    # Treść między znacznikami nie może zawierać KOLEJNEGO otwarcia — inaczej znacznik
    # zacytowany w tekście (a INDEKS to dokument O dokumentach, więc cytat jest naturalny)
    # skleiłby się z domknięciem prawdziwej sekcji i `sub()` zjadłby wszystko pomiędzy.
    # Ta sama klasa zjadła 44 linie LOG_ZMIAN przez wstrzykiwacz liczb (2026-07-17).
    wzorzec = re.compile(
        re.escape(ZNACZNIK_START)
        + r"(?:(?!" + re.escape(ZNACZNIK_START) + r")[\s\S])*?"
        + re.escape(ZNACZNIK_KONIEC)
    )
    nowa = wzorzec.sub(lambda _: katalog_md(), tresc, count=1)
    if nowa == tresc:
        return True, f"{sciezka_indeksu}: katalog bez zmian"
    with open(pelna, "w", encoding="utf-8") as f:
        f.write(nowa)
    return True, f"{sciezka_indeksu}: katalog przepisany z nagłówków ✅"


def main():
    parser = argparse.ArgumentParser(description="Tabularium — rejestr dokumentów Imperium")
    parser.add_argument("komenda", choices=["sprawdz", "katalog", "dublety", "liczby"])
    parser.add_argument("--twardy", action="store_true",
                        help="exit 1 przy błędach (domyślnie miękki — ZASADA WPIĘCIA)")
    parser.add_argument("--zapisz", action="store_true",
                        help="katalog: wstaw do INDEKS_IMPERIUM zamiast drukować")
    args = parser.parse_args()

    if args.komenda == "liczby":
        zmiany, bledy = wstrzyknij_liczby(sucho=not args.zapisz)
        print("🏛️ TABULARIUM — liczby wstrzykiwane z żywego kodu")
        print("   • Prawda z rejestrów: "
              + " | ".join(f"{k} {v}" for k, v in sorted(wartosci_z_kodu().items())))
        for z in zmiany:
            print(f"   {'✏️' if args.zapisz else '⚠️ ROZJAZD'} {z}")
        for b in bledy:
            print(f"   🚨 {b}")
        if not zmiany and not bledy:
            print("   ✅ Wszystkie wstrzyknięte liczby zgadzają się z kodem")
        if bledy:
            return 1
        # Suchy bieg z rozjazdem = dokument kłamie → sygnał dla bramki audytu.
        return 1 if (zmiany and not args.zapisz) else 0

    if args.komenda == "katalog":
        if args.zapisz:
            ok, komunikat = zapisz_katalog()
            print(komunikat)
            return 0 if ok else 1
        print(katalog_md())
        return 0

    bledy, ostrzezenia, info = sprawdz()

    if args.komenda == "dublety":
        dublety = [o for o in ostrzezenia if o.startswith("[T3]")]
        print("🏛️ TABULARIUM — dublety (Prawo XVI)")
        for d in dublety:
            print(f"   • {d}")
        if not dublety:
            print("   BRAK ✅ — żaden kod nie jest opisany dwa razy")
        return 0

    print("🏛️ TABULARIUM — rejestr dokumentów Imperium")
    for i in info:
        print(f"   • {i}")
    if ostrzezenia:
        print(f"\n⚠️ Ostrzeżenia ({len(ostrzezenia)}):")
        for o in ostrzezenia:
            print(f"   • {o}")
    if bledy:
        print(f"\n🚨 Błędy ({len(bledy)}):")
        for b in bledy:
            print(f"   • {b}")
        if args.twardy:
            return 1
        print("\n   ℹ️ Tryb miękki — nie wywracam commita. Twardy: --twardy")
    elif not ostrzezenia:
        print("\n✅ Pełna harmonia rejestru")
    return 0


if __name__ == "__main__":
    sys.exit(main())
