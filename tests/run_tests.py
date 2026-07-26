"""
Runner testów Imperium — bez zależności zewnętrznych.

Uruchom:  python tests/run_tests.py

Odkrywa wszystkie funkcje test_* w plikach test_*.py, uruchamia je,
raportuje wynik. Działa też z pytest jeśli zainstalowany (pytest tests/).

Testuje TYLKO moduły niewymagające TA-Lib/numpy/API (czysty Python):
  - kalkulator_lewara (+ bezpiecznik AOA)
  - igrzyska (scoring neuronów)
  - pamiec_absolutna (logi JSONL)
"""

import sys, os, importlib, traceback, inspect, tempfile
import unittest   # SkipTest — jedyne pojęcie abstynencji w stdlib (honoruje je też pytest)
from pathlib import Path

# Windows: konsola cp1250 (polski Windows) wywala się na emoji w wynikach testów.
# Wymuszamy UTF-8 na stdout/stderr — koniec ręcznego PYTHONIOENCODING=utf-8 przy każdym
# uruchomieniu (lekcja lokala 2026-07-05). No-op na Linux/macOS (już UTF-8).
for _strumien in (sys.stdout, sys.stderr):
    try:
        _strumien.reconfigure(encoding="utf-8")   # type: ignore[union-attr]  # Py3.7+
    except Exception:  # noqa: BLE001 — brak reconfigure / przekierowanie → zostaw
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 🛡️ ZAPORA TESTÓW — PRZED odkryciem i importem modułów testowych (import potrafi już
# zbudować adapter sięgający sieci). Testy Imperium nigdy nie płacą i nie dotykają giełdy.
# Dowód konieczności: NOTARIUS złapał 2026-07-17 pięć płatnych wywołań DeepSeeka podczas
# zwykłego biegu tego runnera (`handluj_live` → AdapterNewsLLM → lazy-init z klucza).
# Pełne uzasadnienie: tests/conftest.py (pytest ładuje go sam; my wołamy jawnie).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import conftest SAM zakłada zaporę (jego kod modułowy) — bierzemy stamtąd raport,
# zamiast wołać zaloz_zapore() drugi raz: drugie wywołanie nie ma już czego odebrać
# i milczałoby, a cicha zapora łamie Prawo XXIV (Cezar ma WIDZIEĆ, że działa).
from conftest import _ODEBRANE as _ODEBRANE_KLUCZE  # noqa: E402
print(f"🛡️ Zapora testów: odebrano klucze [{', '.join(_ODEBRANE_KLUCZE) or 'brak w środowisku'}] "
      f"— testy nie płacą i nie dotykają giełdy (tests/conftest.py)")

# AUTO-DISCOVERY (Prawo XV): każdy tests/test_*.py jest zbierany automatycznie.
# Sztywna lista cicho gubiła nowe pliki testów (test_walidacja, 2026-06-10) —
# nowy moduł testowy "istniał", ale nie był uruchamiany = martwy strażnik.
import glob as _glob

class _MonkeyPatch:
    """Namiastka `monkeypatch` pytesta — setattr / setenv / delenv / setitem / delitem.

    DLACZEGO PEŁNIEJSZA, A NIE „minimal" (zmierzone 2026-07-21, drugi raz ta sama klasa):
    ten runner JEST bramką Imperium, a pytest nie. Test używający metody, której shim nie ma,
    jest ZIELONY pod pytest i CZERWONY pod bramką — czyli autor dostaje fałszywy spokój
    dokładnie w narzędziu, któremu ufa. Pierwszy raz złapane 2026-07-20 (brak `setitem`
    przy pieczęciach), drugi raz 2026-07-21 przy leksykonie LIBRA MESSIS — więc lekarstwem
    nie jest omijanie shimu w testach, tylko uzupełnienie shimu.

    Cofanie trzyma się listy WYWOŁAŃ, nie krotek (obj, name, old): stan słownika ma inną
    logikę przywracania niż atrybut (klucz mógł nie istnieć wcale) i mieszanie obu w jednej
    krotce było źródłem gałęzi `if obj is os.environ`.
    """
    _BRAK = object()          # znacznik „klucza/atrybutu nie było" — None jest legalną wartością

    def __init__(self):
        self._undo = []

    def setattr(self, obj, name, value):
        stary = getattr(obj, name, self._BRAK)

        def cofnij():
            if stary is self._BRAK:
                try:
                    delattr(obj, name)
                except AttributeError:
                    pass
            else:
                setattr(obj, name, stary)

        self._undo.append(cofnij)
        # Zwykłe setattr — również dla KLAS. Poprzednia wersja szła dla klas przez
        # `object.__setattr__(klasa, ...)`, co ZAWSZE rzuca TypeError („can't apply this
        # __setattr__ to type object"); gałąź napisana specjalnie dla klas była więc martwa
        # od początku i nie ujawniła się tylko dlatego, że żaden test nie podmieniał
        # atrybutu klasy. Ujawnił ją dopiero test samego shimu (2026-07-21).
        setattr(obj, name, value)

    def _podmien_klucz(self, mapa, klucz, wartosc, usun=False):
        byl = klucz in mapa
        stary = mapa.get(klucz)

        def cofnij():
            if byl:
                mapa[klucz] = stary
            else:
                mapa.pop(klucz, None)

        self._undo.append(cofnij)
        if usun:
            mapa.pop(klucz, None)
        else:
            mapa[klucz] = wartosc

    def setitem(self, mapa, klucz, wartosc):
        self._podmien_klucz(mapa, klucz, wartosc)

    def delitem(self, mapa, klucz, raising=True):
        if raising and klucz not in mapa:
            raise KeyError(klucz)
        self._podmien_klucz(mapa, klucz, None, usun=True)

    def setenv(self, name, value):
        self._podmien_klucz(os.environ, name, str(value))

    def delenv(self, name, raising=False):
        self._podmien_klucz(os.environ, name, None, usun=True)

    def undo(self):
        for cofnij in reversed(self._undo):
            cofnij()
        self._undo.clear()


MODULY_TESTOWE = sorted(
    os.path.splitext(os.path.basename(p))[0]
    for p in _glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "test_*.py"))
)


# ── STRAŻNIK CZYSTOŚCI REPOZYTORIUM (2026-07-26) ────────────────────────────────
# Test ma sprawdzać kod, nie ZMIENIAĆ repozytorium. Klasa złapana dwa razy:
#   07-21 — `--dry-run` reklamowany jako „bez kosztu" dopisywał do produkcyjnej kolejki;
#   07-26 — nowy test Tabularium wołał `wstrzyknij_liczby(sucho=False)` na PRAWDZIWEJ
#           liście dokumentów i przepisał ZERAMI sześć produkcyjnych plików (115 → 0).
# Za drugim razem to samo przeoczenie oznacza, że lekcja bez MECHANIZMU nie działa:
# skutek uboczny testu jest niewidoczny, bo pakiet świeci na zielono, a szkoda leży
# w plikach, na które nikt wtedy nie patrzy. Strażnik czyni ją głośną natychmiast.
KORZEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PLIKI_WOLNO_ZMIENIAC = {
    # Pieczęć odciska SAM runner na końcu biegu — to jego zadanie, nie skutek uboczny.
    "bibliotheca_ulpia/dane/sigillum_probationis.json",
}


def _stan_repo():
    """Zbiór zmienionych plików śledzonych przez git ({} gdy git niedostępny)."""
    import subprocess
    try:
        wynik = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               cwd=KORZEN, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None                      # brak gita = brak pomiaru; NIE udajemy czystości
    if wynik.returncode != 0:
        return None
    return {ln[3:].strip() for ln in wynik.stdout.splitlines() if ln.strip()}


def uruchom():
    repo_przed = _stan_repo()
    zaliczone = 0
    oblane = 0
    # ABSTYNENCJA TESTU (2026-07-26). Runner znał wyłącznie „zaliczony/oblany", więc test
    # wymagający zależności OPCJONALNEJ (ebooklib, plotext) padał wszędzie tam, gdzie jej
    # nie ma — 3 testy EPUB oblewały pakiet w chmurze, choć nie ma tam czego naprawiać.
    # Brak zasobu to nie porażka i nie zieleń: to POMINIĘCIE, GŁOŚNO policzone. Ciche
    # pominięcie byłoby gorsze od obu (udawałoby pokrycie), więc liczymy je i drukujemy.
    pominiete = 0
    powody_pominiec = []
    bledy = []

    for nazwa_modulu in MODULY_TESTOWE:
        try:
            modul = importlib.import_module(f"tests.{nazwa_modulu}")
        except Exception as e:
            print(f"❌ Nie można zaimportować {nazwa_modulu}: {e}")
            oblane += 1
            continue

        funkcje = [f for f in dir(modul) if f.startswith("test_")]
        # UODPORNIENIE (LEX TALIONIS, 2026-07-19): plik test_*.py bez ŻADNEJ funkcji
        # modułowej test_ to prawie zawsze omyłka — np. testy zapisane jako
        # unittest.TestCase (metody w klasie), których runner NIE zbiera → plik cicho
        # niczego nie chroni. Twarda porażka, nie ciche 0 (klasa błędu złapana raz).
        if not funkcje:
            print(f"  💥 {nazwa_modulu}: 0 funkcji modułowych test_ — plik cicho pomijany "
                  "(TestCase/klasa? runner liczy tylko funkcje test_* na poziomie modułu).")
            oblane += 1
            bledy.append((nazwa_modulu, "<0 testów>",
                          "Plik test_*.py bez funkcji modułowych test_ — silent-skip (napraw styl)."))
            continue
        print(f"\n📋 {nazwa_modulu} ({len(funkcje)} testów)")

        for nazwa_f in funkcje:
            funkcja = getattr(modul, nazwa_f)
            params = list(inspect.signature(funkcja).parameters)
            mp = _MonkeyPatch() if "monkeypatch" in params else None
            tmp = tempfile.mkdtemp() if "tmp_path" in params else None
            kwargs = {}
            if mp is not None:
                kwargs["monkeypatch"] = mp
            if tmp is not None:
                kwargs["tmp_path"] = Path(tmp)
            try:
                funkcja(**kwargs)
                print(f"  ✅ {nazwa_f}")
                zaliczone += 1
            except unittest.SkipTest as e:
                print(f"  ⏭️ {nazwa_f}: POMINIĘTY — {e}")
                pominiete += 1
                powody_pominiec.append((nazwa_modulu, nazwa_f, str(e)))
            except AssertionError as e:
                print(f"  ❌ {nazwa_f}: {e}")
                oblane += 1
                bledy.append((nazwa_modulu, nazwa_f, str(e)))
            except Exception as e:
                print(f"  💥 {nazwa_f}: {type(e).__name__}: {e}")
                oblane += 1
                bledy.append((nazwa_modulu, nazwa_f, traceback.format_exc()))
            finally:
                if mp is not None:
                    mp.undo()

    print("\n" + "═" * 60)
    print(f"  WYNIK: {zaliczone} zaliczone, {oblane} oblane "
          f"({zaliczone}/{zaliczone + oblane})"
          + (f", {pominiete} pominięte" if pominiete else ""))
    print("═" * 60)

    # POMINIĘCIA WIDOCZNE ZAWSZE — cicha abstynencja udawałaby pokrycie (Prawo XV).
    if powody_pominiec:
        print("\nPominięte (brak zasobu w TYM środowisku — nie porażka, ale i nie pokrycie):")
        for modul, test, powod in powody_pominiec:
            print(f"  ⏭️ {modul}::{test} — {powod}")

    # STRAŻNIK CZYSTOŚCI — sprawdzany PRZED odciśnięciem pieczęci, żeby jej własny zapis
    # nie liczył się jako brud (i żeby czerwony wynik nie został przypieczętowany jako OK).
    repo_po = _stan_repo()
    if repo_przed is not None and repo_po is not None:
        zabrudzone = sorted((repo_po - repo_przed) - _PLIKI_WOLNO_ZMIENIAC)
        if zabrudzone:
            print("\n🚨 REPOZYTORIUM ZMIENIŁO SIĘ W TRAKCIE BIEGU:")
            for plik in zabrudzone:
                print(f"     ✏️ {plik}")
            print("   Dwie możliwe przyczyny — rozstrzygnij, NIE zgaduj:")
            print("   (a) test pisze do plików Imperium zamiast do swojego tmp_path;")
            print("   (b) bieg szedł RÓWNOLEGLE z procesem zmieniającym repo (edycja, hook,")
            print("       wpis do ledgera) — wtedy to fałszywe oskarżenie, powtórz bieg sam.")
            oblane += 1
            bledy.append(("<strażnik czystości>", "repozytorium zabrudzone przez testy",
                          "Zmienione pliki: " + ", ".join(zabrudzone)))

    _odcisnij_pieczec(zaliczone, oblane)

    if bledy:
        print("\nSzczegóły błędów:")
        for modul, test, blad in bledy:
            print(f"\n  {modul}::{test}")
            print(f"    {blad}")
        return 1
    print("\n✅ Wszystkie testy zaliczone — Imperium gotowe.")
    return 0


def _odcisnij_pieczec(zaliczone: int, oblane: int) -> None:
    """
    Odciska SIGILLUM PROBATIONIS — wynik biegu przypięty do commitu, na którym zapadł.

    POWÓD (zwiad adwersarialny 2026-07-21, dwa niezależne konteksty zbiegły się na tym
    samym): `tests/run_tests.py` NIE jest wołany ani przez hook startowy, ani przez audyt
    (zmierzone: 0 trafień w hooku, w audycie tylko ścieżki `__pycache__`). Testy trwają
    >5 minut, więc wołanie ich przy każdym starcie byłoby okrutne — ale skutkiem było, że
    CZERWONY STAN TESTÓW JEST NIEWIDOCZNY NA OTWARCIU. Sesja urwana przed bramką zamknięcia
    zostawiała złamany kod, a następna sesja widziała „pełną harmonię" audytu i budowała
    dalej na złamanym fundamencie. Ta sama klasa co dług honorowy: bramka istniejąca
    wyłącznie na końcu procesu, który nie musi się wydarzyć.

    Lekarstwem NIE jest powtarzanie biegu, tylko WYKRYWANIE NIEAKTUALNOŚCI: pieczęć wie,
    dla jakiego KODU zapadł wynik, więc otwarcie sesji odróżnia „zielone dla TEGO kodu"
    od „zielone dla kodu, którego już nie ma" — a to drugie jest niewiedzą, nie zgodą.

    Tożsamość kodu to ODCISK TREŚCI ŹRÓDEŁ, nie hash commitu. Porównanie z commitem
    wyglądało sensownie, ale przy naturalnym rytmie pracy (edytuj → uruchom testy na brudnym
    drzewie → commituj) pieczęć NIGDY nie mogłaby powiedzieć „zielone": zawsze albo brudne
    drzewo, albo — po commicie — inny hash. Detektor, który alarmuje zawsze, uczy operatora
    ignorować siebie, czyli psuje dokładnie to, po co powstał. Odcisk źródeł odpowiada na
    właściwe pytanie: czy od czasu biegu ktoś ruszył kod. Zmierzone: 405 plików, 232 ms.
    """
    try:
        import json
        import subprocess
        from datetime import datetime

        korzen = Path(__file__).resolve().parent.parent
        # encoding+errors JAWNIE (klasa z Księgi Wad): samo `text=True` dekoduje kodowaniem
        # KONSOLI, a `git status --porcelain` potrafi zwrócić polską nazwę pliku — wtedy
        # UnicodeDecodeError uciszyłby pieczęć akurat na brudnym drzewie, czyli w stanie,
        # o którym pieczęć ma ostrzegać.
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=10, cwd=korzen)
        brudne = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=10, cwd=korzen)
        from imperium.oczy.breviarium import odcisk_zrodel
        pieczec = {
            "zaliczone": zaliczone,
            "oblane": oblane,
            "odcisk_zrodel": odcisk_zrodel(),          # tożsamość KODU, nie commitu
            "commit": (commit.stdout or "").strip()[:40] or "?",   # informacyjnie
            "drzewo_brudne": bool((brudne.stdout or "").strip()),
            "kiedy": datetime.now().isoformat(timespec="seconds"),
        }
        plik = korzen / "bibliotheca_ulpia" / "dane" / "sigillum_probationis.json"
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text(json.dumps(pieczec, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — pieczęć jest dodatkiem do biegu, nigdy jego warunkiem
        print(f"  (pieczęć testów niezapisana: {e})")


if __name__ == "__main__":
    sys.exit(uruchom())
