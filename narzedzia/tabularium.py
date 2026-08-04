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

# ── WŁAŚCICIEL: KIEDY WOLNO GO NIE MIEĆ (naprawa 2026-08-04) ──────────────────
# SPRZECZNOŚĆ W SAMYM ORGANIE, zmierzona na 22 dokumentach: parser świadomie zamienia
# `—` na pustkę („— musi znaczyć BRAK właściciela" — kontrakt utrwalony testem), a bramka
# T1 zaraz potem żąda wartości NIEPUSTEJ. Organ wypisywał więc `—` we własnym katalogu
# jako wartość poprawną i karał za jej wpisanie. Skutek uboczny był gorszy od samego
# błędu: dokument bez właściciela wypadał TAKŻE z bramki GNICIA, bo pętla po właścicielach
# nie wykonywała się ani razu. Dostawał błąd i zwolnienie z kontroli w jednym ruchu —
# czyli klasa „milczenie czytane jako zieleń" (K2 przeglądu LUSTRATIO).
#
# Rozstrzygnięcie: brak właściciela jest DOZWOLONY, ale nigdy MILCZĄCY. Ten sam wzorzec
# co `powod_acta` i `dublet_rozstrzygniety`: wyciszenie bramki zawsze wymaga powodu,
# który zostaje na widoku (K4).
POLE_BEZ_WLASCICIELA = "bez_wlasciciela"

# Kategorie, w których brak właściciela jest SPRZECZNOŚCIĄ Z DEFINICJĄ KATEGORII,
# więc żaden powód go nie usprawiedliwia:
#   TABULA  — „rejestr prawdy o kodzie, musi zgadzać się 1:1" → rejestr, który nie
#             wskazuje żadnego kodu, nie ma z czym się zgadzać,
#   FORMA   — „opis budowy organu" → opis budowy bez organu,
#   MENSURA — „pomiar z danych" → pomiar bez mierzonego przedmiotu.
KATEGORIE_Z_OBOWIAZKOWYM_WLASCICIELEM = ("TABULA", "FORMA", "MENSURA")

# Zastępczy zegar świeżości dla dokumentów BEZ właściciela. Bez niego brak kodu
# oznaczałby brak jakiejkolwiek kontroli aktualności — a doktryna też się starzeje.
DNI_BEZ_WLASCICIELA = 90

# Poza rejestrem — każde z własnymi zasadami, Tabularium pilnuje ŻYWEJ dokumentacji:
#   archiwum/          — magazyn, otwierany na rozkaz Cezara (ZASADA ARCHIWIZACJI)
#   bibliotheca_ulpia/ — księgozbiór i kronika sesji: historia, Prawo I zabrania tykać
#   wrzutnia/          — skrzynka wejściowa, treść surowa przed obróbką
#   .claude/           — konfiguracja harnessa; agenci mają WŁASNY nagłówek (name/tools),
#                        który Tabularium wzięłoby za deklarację dokumentu
#   dane/              — katalogi danych; README to drogowskaz („tu wrzucasz CSV"), nie opis
POZA_REJESTREM = ("archiwum", "bibliotheca_ulpia", "wrzutnia", ".claude", "dane",
                  ".git", ".pytest_cache", "node_modules", "__pycache__")

# Żywe DROGOWSKAZY spoza rejestru organów, których LICZBY mają jednak nadążać za kodem.
# `bibliotheca_ulpia/README.md` jest w POZA_REJESTREM (historia — nie tykamy T1/T2 bez
# frontmatter), ALE podaje liczbę ksiąg, która gniła niezauważona (69 przy 115, wstyd
# Cezara 2026-07-21 — żadna bramka jej nie pilnowała). Wpinamy TYLKO w warstwę liczb (T4),
# nie w T1/T2 — blok `<!-- LICZBA:ksiazki -->` jest teraz przepisywany i audytowany.
DROGOWSKAZY_Z_LICZBAMI = ("bibliotheca_ulpia/README.md",)

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
    from imperium.biblioteki.srodowisko_pamieci import (
        fragmenty_w_bazie, korpus_ksiazek_obecny, ksiazki_w_bazie, sesje_w_kronice,
    )
    from imperium.legiony.rejestr import (
        neurony_dla_trybu, raport_elity, wszystkie_neurony, wszyscy_zwiadowcy,
    )
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    neurony = wszystkie_neurony()
    wartosci = {
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
        # Biblioteka rośnie (BIB-070..274 w planie) — liczba książek wpisana w dokument
        # zestarzeje się tak samo, jak zaszyte w kodzie „42" zestarzało się przy 79.
        "ksiazki": ksiazki_w_bazie(),
        "fragmenty": fragmenty_w_bazie(),
        # Kronika rośnie od SAMEJ PRACY, bez żadnego commitu w plikach-właścicielach —
        # dlatego bramka gnicia (T2) nigdy jej nie złapie. Zmierzone 2026-08-04: dwa
        # dokumenty pisały „102 sesji" przy 154 realnych. Liczba wstrzykiwana zamyka
        # klasę u źródła: dokument NIE MA JAK skłamać o wielkości, której nie zapisuje.
        "sesje_kroniki": sesje_w_kronice(),
    }
    # ABSTYNENCJA ZAMIAST ZERA (Prawo XV, zmierzone 2026-07-26). Książki są świadomie poza
    # gitem, więc chmura mierzy 0 książek i 551 fragmentów tam, gdzie lokal ma 115/37331.
    # Bez tej bramki W15 kazała przepisać „115 → 0" w sześciu dokumentach — narzędzie od
    # prawdy namawiało do skasowania prawdy. Środowisko bez korpusu NIE MA GŁOSU o korpusie.
    if not korpus_ksiazek_obecny():
        wartosci["ksiazki"] = None
        wartosci["fragmenty"] = None
    # Liczba plików .py per organ (mapa README/ARCHITEKTURA — była ręczna i rozjechała
    # się z kodem: legiony podawane jako 40 przy 67 realnych, 2026-07-19). Wstrzykiwana,
    # żeby schemat Imperium nigdy więcej nie kłamał o własnej wielkości (Warstwa 15).
    organy = os.path.join(ROOT, "imperium")
    if os.path.isdir(organy):
        for nazwa in sorted(os.listdir(organy)):
            folder = os.path.join(organy, nazwa)
            if not os.path.isdir(folder):
                continue
            ile = sum(1 for _r, _d, pliki in os.walk(folder)
                      for p in pliki if p.endswith(".py"))
            wartosci[f"organ_{nazwa}"] = ile
    return wartosci


def wstrzyknij_liczby(sucho=False, tylko=None):
    """Przepisuje każdy blok <!-- LICZBA:x --> z żywego kodu. → (zmiany, bledy).

    Dokumenty `typ: acta` (LOG_ZMIAN, migawki) są POMIJANE: wpis datowany jest prawdą
    swojego czasu i cytuje liczby z dnia zapisu (Prawo I — nie falsyfikujemy historii).
    Bez tego filtra wpis z 2026-07-17 mówiący „87 neuronów" cicho stałby się „90", gdy rój
    urośnie — kłamstwo tym groźniejsze, że wyprodukowane przez narzędzie od prawdy.

    `tylko` = lista ścieżek (bezwzględnych lub względnych wobec ROOT), do których wolno
    pisać. ZASIĘG ISTNIEJE DLA TESTÓW (zmierzone 2026-07-26): test granicy wołał
    `sucho=False` na CAŁYM korpusie i realnie przepisywał produkcyjne README — wada
    UTAJONA, bo dopóki liczby się nie zmieniały, plik po zapisie wyglądał identycznie.
    Ujawniła się dopiero, gdy `organ_cesarz` wzrósł 12→13, czyli w najgorszym możliwym
    momencie: przy zmianie kodu. Zasięg zamyka całą klasę — test nie ma jak dotknąć
    dokumentu, którego nie wymienił. `tylko=[]` NIE znaczy „wszystko": znaczy „nic".
    """
    wartosci = wartosci_z_kodu()
    zmiany, bledy = [], []
    # USŁUGA, nie sędzia — naprawia znaczniki gdziekolwiek je zastanie (patrz docstring
    # `zbierz_dokumenty`); filtr gita obowiązuje wyłącznie bramki orzekające.
    dokumenty = list(zbierz_dokumenty(tylko_sledzone=False))
    # Dołącz żywe drogowskazy spoza rejestru (np. README biblioteki) — tylko warstwa liczb.
    for wzgl in DROGOWSKAZY_Z_LICZBAMI:
        if os.path.exists(os.path.join(ROOT, wzgl)):
            dokumenty.append((wzgl, {}))
    if tylko is not None:
        dozwolone = {os.path.abspath(os.path.join(ROOT, p)) for p in tylko}
        dokumenty = [(s, m) for s, m in dokumenty
                     if os.path.abspath(os.path.join(ROOT, s)) in dozwolone]
    for sciezka, meta in dokumenty:
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
            if wartosci[klucz] is None:
                # Klucz abstynuje w TYM środowisku (brak korpusu) — zostawiamy dokument
                # nietknięty. Milczenie nie jest pomiarem: nie kasujemy liczby zmierzonej
                # tam, gdzie zasób istnieje (Prawo I + XV).
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


def _sledzone_przez_git():
    """Zbiór ścieżek wersjonowanych, albo None gdy gita nie ma (wtedy nie filtrujemy).

    ZMIERZONE 2026-08-04: Tabularium żądało metadanych od `raporty/RAPORT_TOKENY_2026-07-26.md`,
    który jest **gitignored** (`.gitignore:20`). Plik spoza kontroli wersji nie jest
    dokumentem Imperium — nie ma go na branchu, więc wedle Prawa XIX nie istnieje.
    Naprawa KLASOWA, nie punktowa: dopisanie `raporty` do POZA_REJESTREM uciszyłoby
    ten jeden katalog, a każdy następny ignorowany katalog powtórzyłby alarm.
    Brak gita nie może wywrócić spisu — wtedy zachowujemy się jak dawniej.
    """
    try:
        wynik = subprocess.run(
            ["git", "ls-files", "*.md"], capture_output=True, text=True, timeout=30,
            cwd=ROOT, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if wynik.returncode != 0:
        return None
    return {l.strip() for l in wynik.stdout.splitlines() if l.strip()}


def zbierz_dokumenty(tylko_sledzone=True):
    """Wszystkie żywe .md Imperium → [(sciezka_wzgledna, meta)] posortowane.

    `tylko_sledzone=False` wyłącza filtr gita. SĘDZIA vs USŁUGA (rozstrzygnięcie
    2026-08-04): bramki (`sprawdz`, `katalog_md`) ORZEKAJĄ o dokumentach Imperium,
    więc plik spoza kontroli wersji ich nie obchodzi. Wstrzykiwacz liczb niczego nie
    osądza — naprawia znaczniki tam, gdzie je zastanie, także w dokumencie roboczym.
    Rozdzielenie jest potrzebne, bo filtr założony bez niego wyciął testom grunt pod
    nogami: sprawdzały wstrzykiwacz na pliku tymczasowym, czyli z definicji nieśledzonym.
    """
    znalezione = []
    sledzone = _sledzone_przez_git() if tylko_sledzone else None
    for katalog, podkatalogi, pliki in os.walk(ROOT):
        podkatalogi[:] = [d for d in podkatalogi if d not in POZA_REJESTREM]
        for plik in pliki:
            if not plik.endswith(".md"):
                continue
            pelna = os.path.join(katalog, plik)
            wzgledna = os.path.relpath(pelna, ROOT).replace("\\", "/")
            if sledzone is not None and wzgledna not in sledzone:
                continue          # poza kontrolą wersji = poza Imperium (Prawo XIX)
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


_DEF_W_DIFFIE = re.compile(r"^[+-]\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)")
_DEF_W_HUNKU = re.compile(r"^@@ .* @@\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)")
_DEF_W_KODZIE = re.compile(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)", re.M)
_CYTAT_BACKTICK = re.compile(r"`([^`\n]{1,120})`")
_IDENTYFIKATOR = re.compile(r"[A-Za-z_]\w*")

# Symbol zdefiniowany w tylu plikach (lub więcej) jest HOMONIMEM, nie świadectwem.
# Próg zmierzony 2026-08-04 na populacji 26 gnijących dokumentów: rozkład jest
# bimodalny (symbole unikalne żyją w 1–3 plikach, pospolite w 40–97), więc progi
# 2, 3, 5 i 10 dają IDENTYCZNY wynik — 9 mocnych świadectw. Brak wrażliwości na
# próg to dowód, że nie stroimy go pod oczekiwany wynik. Bez niego `main` (84 pliki)
# „dowodził", że SCIAGA_LOKAL opisuje zmieniony kod — świadectwo mówiące tylko tyle,
# że oba pliki są Pythonem.
PROG_POSPOLITOSCI = 5
_POSPOLITOSC_CACHE = None


def _pliki_py_repo():
    """Wersjonowane pliki .py. WŁASNE zapytanie — `_sledzone_przez_git()` listuje `*.md`.

    Zmierzone 2026-08-04 przy pierwszym biegu tego organu: przefiltrowanie listy `*.md`
    po `.endswith('.py')` dawało ZBIÓR PUSTY, więc mapa pospolitości była pusta, a
    `licznik.get(s, 0) < PRÓG` przepuszczał KAŻDY symbol jako rzadki — `main` (84 pliki)
    awansował na świadectwo. Filtr nie krzyknął, tylko cicho przestał filtrować: dokładnie
    klasa „milczenie udające wynik". Stąd zapora w `_pospolitosc_symboli()`.
    """
    try:
        wynik = subprocess.run(
            ["git", "ls-files", "*.py"], capture_output=True, text=True, timeout=30,
            cwd=ROOT, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if wynik.returncode != 0:
        return []
    return [l.strip() for l in wynik.stdout.splitlines() if l.strip()]


def _pospolitosc_symboli():
    """Symbol → w ilu plikach .py repo jest DEFINIOWANY (cache na proces).

    Pusta mapa NIE oznacza „same rzadkie symbole" — oznacza, że pomiar padł. Zwracamy
    wtedy None, a wołający ma obowiązek uznać świadectwo za NIEROZSTRZYGNIĘTE, zamiast
    hurtowo awansować homonimy (Prawo XV: brak danych to abstynencja, nie wynik).
    """
    global _POSPOLITOSC_CACHE
    if _POSPOLITOSC_CACHE is not None:
        return _POSPOLITOSC_CACHE
    licznik = {}
    for sciezka in _pliki_py_repo():
        try:
            with open(os.path.join(ROOT, sciezka), encoding="utf-8", errors="replace") as f:
                tresc = f.read()
        except OSError:
            continue
        for nazwa in set(_DEF_W_KODZIE.findall(tresc)):
            licznik[nazwa] = licznik.get(nazwa, 0) + 1
    _POSPOLITOSC_CACHE = licznik or None
    return _POSPOLITOSC_CACHE


def _symbole_zmienione(sciezka_wlasciciela, stan_na):
    """Nazwy funkcji/klas, których diff DOTKNĄŁ po dacie `stan_na`.

    Nagłówek hunka (`@@ … @@ def foo`) niesie funkcję-kontekst, więc łapiemy też
    zmianę CIAŁA funkcji, nie tylko jej sygnatury.
    """
    nastepny_dzien = stan_na + timedelta(days=1)
    try:
        log = subprocess.run(
            ["git", "log", f"--since={nastepny_dzien.isoformat()}", "--format=%H",
             "--", sciezka_wlasciciela],
            capture_output=True, text=True, timeout=20, cwd=ROOT,
            encoding="utf-8", errors="replace",
        )
        if log.returncode != 0:
            return set()
        symbole = set()
        for sha in log.stdout.split():
            pokaz = subprocess.run(
                ["git", "show", sha, "--unified=0", "--", sciezka_wlasciciela],
                capture_output=True, text=True, timeout=20, cwd=ROOT,
                encoding="utf-8", errors="replace",
            )
            for linia in pokaz.stdout.splitlines():
                trafienie = _DEF_W_HUNKU.match(linia) or _DEF_W_DIFFIE.match(linia)
                if trafienie:
                    symbole.add(trafienie.group(1))
        return symbole
    except (OSError, subprocess.SubprocessError):
        return set()


def _symbole_cytowane(tresc):
    """Identyfikatory, które dokument realnie WYMIENIA (w backtickach)."""
    znalezione = set()
    for cytat in _CYTAT_BACKTICK.findall(tresc):
        znalezione.update(_IDENTYFIKATOR.findall(cytat))
    return znalezione


def swiadectwo_gnicia(sciezka, meta):
    """DRUGIE ŚWIADECTWO T2: czy ruszyło się to, co dokument OPISUJE? → (waga, symbole).

    DLACZEGO ISTNIEJE (zmierzone 2026-08-04, kalibracja na 6 losowanych dokumentach
    z zamrożoną prawdą podstawową): sam sygnał „commit dotknął pliku-właściciela" ma
    **33% precyzji** (2 z 6 dokumentów realnie kłamało), a wskazanego przez siebie
    SPRAWCĘ trafił **0 razy na 6** — oba prawdziwe gnicia wzięły się z liczb rosnących
    same (fragmenty RAG, sesje kroniki), nie z żadnego commitu. Bramka o takiej precyzji
    uczy ignorować siebie: 26 pozycji, z których dwie są prawdziwe, czyta się jak tapetę.

    NIE KASUJE ALARMU — nadaje mu wagę (klasa K2 z LUSTRATIO: milczenie nie może być
    zielenią). Dokument bez mocnego świadectwa nadal jest zgłoszony, tylko niżej w
    kolejce. Zmierzone na tej samej próbce: waga MOCNA trafia 2/2 prawdziwych i 0/4
    fałszywek, a populacja 26 dzieli się na 9 pilnych i 17 do przeglądu okazjonalnego.

    ŚWIADOMY LIMIT: zmiana zachowania wewnątrz funkcji, o której dokument mówi PROZĄ
    (bez nazwy w backtickach), dostanie wagę słabą. Dlatego waga, nie filtr.
    """
    stan_na = meta.get("stan_na")
    try:
        stan_na = date.fromisoformat(stan_na) if isinstance(stan_na, str) else stan_na
    except (TypeError, ValueError):
        return "SŁABE", []
    if not stan_na:
        return "SŁABE", []
    try:
        with open(os.path.join(ROOT, sciezka), encoding="utf-8") as f:
            cytowane = _symbole_cytowane(f.read())
    except OSError:
        return "SŁABE", []
    pospolitosc = _pospolitosc_symboli()
    if pospolitosc is None:
        return "NIEROZSTRZYGNIĘTE", []
    zmienione = set()
    for wlasciciel in _wlasciciele(meta):
        if os.path.exists(os.path.join(ROOT, wlasciciel)):
            zmienione |= _symbole_zmienione(wlasciciel, stan_na)
    wspolne = sorted(s for s in (zmienione & cytowane)
                     if pospolitosc.get(s, 0) < PROG_POSPOLITOSCI)
    return ("MOCNE" if wspolne else "SŁABE"), wspolne


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
            if pole == "wlasciciel":
                continue        # osobny tryb — patrz BRAMKA 1b
            if not meta.get(pole):
                bledy.append(f"[T1] {sciezka}: brak pola `{pole}` w nagłówku")
        kategoria = meta.get("kategoria", "")

        # ── BRAMKA 1b: WŁAŚCICIEL ALBO JAWNY POWÓD JEGO BRAKU ───────────────
        # Brak właściciela jest dozwolony, ale nigdy milczący (patrz komentarz
        # przy POLE_BEZ_WLASCICIELA). Kategoria orzeka, czy w ogóle wolno go nie mieć.
        if not meta.get("wlasciciel"):
            powod_braku = meta.get(POLE_BEZ_WLASCICIELA, "")
            if kategoria in KATEGORIE_Z_OBOWIAZKOWYM_WLASCICIELEM:
                bledy.append(
                    f"[T1] {sciezka}: kategoria `{kategoria}` WYMAGA właściciela — "
                    f"{KATEGORIE.get(kategoria, '')}. Dokument tej kategorii bez wskazanego "
                    f"kodu nie ma z czym się zgadzać. Wskaż plik albo zmień kategorię")
            elif not powod_braku:
                bledy.append(
                    f"[T1] {sciezka}: brak właściciela BEZ POWODU — dopisz "
                    f"`{POLE_BEZ_WLASCICIELA}: \"<czemu ten dokument nie opisuje kodu>\"`. "
                    f"Samo `—` nie wystarcza: wyciszenie bramki zawsze wymaga powodu "
                    f"na widoku (jak `powod_acta` i `dublet_rozstrzygniety`)")
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
        # ── BRAMKA 2b: ZEGAR ZASTĘPCZY dla dokumentów BEZ właściciela ───────
        # Zmierzone 2026-08-04: 22 dokumenty bez właściciela były NIEWIDZIALNE dla T2,
        # bo pętla `for wlasciciel in _wlasciciele(meta)` nie wykonywała się ani razu.
        # Nie „przechodziły kontrolę" — nie były kontrolowane. Doktryna też się starzeje,
        # więc dostaje własny zegar liczony od `stan_na`, nie od cudzego kodu.
        if typ == "zywy" and stan_na and not zastapiony and not _wlasciciele(meta):
            wiek = (date.today() - stan_na).days
            if wiek > DNI_BEZ_WLASCICIELA:
                ostrzezenia.append(
                    f"[T2b] {sciezka}: dokument bez właściciela nie był weryfikowany "
                    f"od {wiek} dni (próg {DNI_BEZ_WLASCICIELA}). Brak kodu nie może "
                    f"oznaczać braku kontroli — przejrzyj i przestaw `stan_na`")

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
    parser.add_argument("komenda",
                        choices=["sprawdz", "katalog", "dublety", "liczby", "swiadectwa"])
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

    dokumenty = list(zbierz_dokumenty())
    bledy, ostrzezenia, info = sprawdz(dokumenty)

    if args.komenda == "swiadectwa":
        # ŚWIADOMIE POZA AUDYTEM: jedno `git show` na commit kosztuje ~60 ms, a populacja
        # gnijących ma ich ponad dwieście — audyt startowy musi zostać szybki, bo chodzi
        # w hooku KAŻDEJ sesji. To narzędzie do PRZEGLĄDU, nie do bramkowania commita.
        gnijace = {}
        for o in ostrzezenia:
            trafienie = re.match(r"\[T2\] GNICIE (\S+) ", o)
            if trafienie:
                gnijace[trafienie.group(1)] = o
        meta_wg = dict(dokumenty)
        oceny = []
        for i, sciezka in enumerate(sorted(gnijace), 1):
            _pasek(i, len(gnijace), sciezka)
            waga, symbole = swiadectwo_gnicia(sciezka, meta_wg.get(sciezka, {}))
            oceny.append((waga, sciezka, symbole))
        print("🏛️ TABULARIUM — świadectwa gnicia (waga alarmu, nie jego kasowanie)")
        mocne = [o for o in oceny if o[0] == "MOCNE"]
        nieznane = [o for o in oceny if o[0] == "NIEROZSTRZYGNIĘTE"]
        print(f"   • Zgłoszonych przez T2: {len(oceny)} → 🔴 MOCNE {len(mocne)} · "
              f"🟡 SŁABE {len(oceny) - len(mocne) - len(nieznane)} · ⚫ NIEROZSTRZYGNIĘTE "
              f"{len(nieznane)}")
        print(f"   • Próg pospolitości symbolu: < {PROG_POSPOLITOSCI} plików "
              f"(homonim nie jest świadectwem)")
        znaki = {"MOCNE": "🔴", "SŁABE": "🟡", "NIEROZSTRZYGNIĘTE": "⚫"}
        kolejnosc = {"MOCNE": 0, "NIEROZSTRZYGNIĘTE": 1, "SŁABE": 2}
        for waga, sciezka, symbole in sorted(oceny, key=lambda o: (kolejnosc[o[0]], o[1])):
            if waga == "NIEROZSTRZYGNIĘTE":
                powod = "🚨 pomiar pospolitości padł — świadectwa NIE MA (nie mylić ze słabym)"
            elif symbole:
                powod = f"dokument opisuje ruszone: {', '.join(symbole[:5])}"
            else:
                powod = "zmiany poza tym, co dokument cytuje"
            print(f"   {znaki[waga]} [{waga}] {sciezka} — {powod}")
        if not oceny:
            print("   ✅ Żaden dokument nie jest zgłoszony jako gnijący")
        return 0

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
