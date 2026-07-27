"""
📜 NOTARIUS — pisarz Imperium: stenografuje słowa Nauczyciela (Filar 2 TIRO, distylacja).

W Rzymie *notarius* to skryba, który zapisywał mowy DOSŁOWNIE i na bieżąco, nie ingerując
w treść ani nie przerywając mówcy. Ten organ robi dokładnie to samo: przy KAŻDYM przejściu
przez most `GlosImperium.zapytaj()` zapisuje parę `prompt → odpowiedź nauczyciela` do JSONL.
To surowiec Szkoły TIRO (etapy E2→E4 planu `docs/PLAN_TIRO_LOKALNY_LLM.md`).

DLA NOWICJUSZA: żeby wytrenować własnego małego ucznia (TIRO), potrzeba przykładów
„na takie pytanie dobry nauczyciel odpowiada tak". Każde pytanie, które Imperium już dziś
zadaje Hyginusowi (DeepSeek), może zostawić taki przykład ZA DARMO — pytanie i tak leci,
odpowiedź i tak wraca. NOTARIUS tylko zapisuje to, co przelatuje. Im wcześniej zacznie,
tym większy zbiór treningowy zastanie nowy sprzęt.

╔═══════════════════════════════════════════════════════════════════════════════╗
║ ŻELAZNA ZASADA: NOTARIUS NIGDY NIE PRZERYWA NAUCZYCIELOWI.                    ║
║ Każdy błąd zapisu (dysk pełny, brak praw, zepsuty JSON) jest ŁYKANY i logowany║
║ jako warning. Awaria pisarza NIE MOŻE wywrócić wywołania API — mowa jest       ║
║ ważniejsza niż jej protokół.                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

ZASADA WPIĘCIA — dlaczego zbieranie jest domyślnie WŁĄCZONE:
    Rozkaz „opt-in domyślnie OFF" dotyczy zmian wpływających na WEJŚCIE/WYJŚCIE z pozycji
    (próg, weto, sizing, filtr). NOTARIUS **tylko obserwuje i zapisuje** — nie dotyka ścieżki
    decyzyjnej, nie zmienia ani jednego głosu neuronu. Dlatego zbieranie działa domyślnie
    (wyłącznik: `TIRO_NOTARIUS=0`). Domyślnie OFF pozostaje to, co faktycznie decyduje:
    wpięcie ucznia jako głosu (E5, awans po zielonym egzaminie w arenie — decyzja Cezara).

🚨 GRANICA PRAWNA (Prawo I — zweryfikowane 2026-07-16, zwiad web):
    Nauczycielem wag TIRO może być **WYŁĄCZNIE DeepSeek** — jego regulamin wprost dopuszcza
    distylację („training other models") dla użytku niekonkurencyjnego. Regulaminy Anthropic
    i OpenAI **ZAKAZUJĄ** trenowania modeli na ich wyjściach — dlatego NOTARIUS pisze tylko
    to, co przechodzi przez `GlosImperium` (most do DeepSeek), i NIGDY nie zapisuje odpowiedzi
    Vitruviusza/Opusa. Opus jest Architektem i Sędzią, nie nauczycielem wag.

CLI: python -m imperium.biblioteki.notarius {raport|eksport|wyczysc-duplikaty}
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger("Notarius")

ROOT = Path(__file__).resolve().parent.parent.parent
DOMYSLNA = ROOT / "bibliotheca_ulpia" / "dane" / "tiro_pary_nauczyciela.jsonl"

# Zmienna wyłączająca (Prawo XVIII: Cezar musi móc zgasić pisarza bez zmiany kodu).
ENV_WYLACZNIK = "TIRO_NOTARIUS"

# Twardy limit znaków na pole. Prompty z fragmentami RAG bywają długie — chcemy je w całości
# (to esencja przykładu treningowego), ale bez ryzyka, że jeden zdziczały wpis urośnie w GB.
# 200k znaków ≈ 50k tokenów — powyżej i tak nie zmieści się w kontekście ucznia 1-4B.
LIMIT_ZNAKOW = 200_000

# 🚨 LIMIT PRÓBEK NA PYTANIE — bezpiecznik przeciw MONOKULTURZE (zmierzone 2026-07-16).
# POWÓD (twardy dowód z danych, nie teoria): pętla live pyta o TE SAME nagłówki co cykl.
# Zmierzone: 17 par news_llm = tylko 4 unikalne zestawy nagłówków; jeden pytany 10× dostał
# 10 RÓŻNYCH odpowiedzi (sentyment od +0.8 do -0.4). Dedup po całej parze tego NIE łapie,
# bo odpowiedzi się różnią. Skutek bez limitu: ~4 pary/min z pętli live = ~5000/dobę
# near-duplikatów, które utopiłyby wartościowe pary z bibliotekarza, a model uczyłby się
# SPRZECZNYCH etykiet dla identycznego wejścia (najgorszy możliwy sygnał treningowy).
#
# Dlaczego limit, a nie dedup po samym pytaniu: kilka próbek tego samego wejścia MA wartość —
# pozwalają policzyć KONSENSUS przy eksporcie (self-consistency: mediana kilku próbek bije
# pojedynczy strzał nauczyciela). Kilka = sygnał, dziesięć = zalew. Stąd limit, nie zakaz.
LIMIT_PROBEK_NA_PYTANIE = 3

# 🚨 DWA RODZAJE ZADAŃ W JEDNYM LEDGERZE (zmierzone 2026-07-27, Prawo XV).
# POWÓD: próg `min_znakow_odpowiedzi` powstał dla odpowiedzi PROZĄ (rozwinięcia bibliotekarza,
# auto-lekcje), gdzie krótka odpowiedź naprawdę znaczy „nie wiem". Ale ledger trzyma też plon
# KLASYFIKACJI: adapter newsów prosi o `{"sentyment": ..., "pewnosc": ...}` — poprawna odpowiedź
# ma 34-41 znaków Z DEFINICJI. Zmierzone: 102 pary `news_llm` → 0 użytecznych, czyli 27% ledgera
# było niewidzialne dla treningu, a meldunek nazywał to postępem. Długość jest PROXY jakości
# prawdziwym tylko dla prozy; dla wyjścia strukturalnego kłamie w 100% przypadków.
# LEKARSTWEM NIE JEST OBNIŻENIE PROGU (to naginanie miary pod wynik), tylko test WŁAŚCIWY
# RODZAJOWI: proza → długość, klasyfikacja → czy odpowiedź jest poprawnym obiektem JSON.
#
# Rodzaj bierzemy z pola `rodzaj` (jeśli wpis je ma), a dla wpisów starszych odtwarzamy ze
# ŹRÓDŁA — ta sama technika, którą stosuje `_wczytaj_stan` dla brakującego `odcisk_pytania`.
# Rejestr trzyma źródła, nie schematy: Notarius sprawdza STRUKTURĘ (obiekt JSON), nigdy
# semantykę dziedziny — inaczej ledger treningowy zacząłby znać się na sentymencie rynku.
RODZAJ_PROZA = "proza"
RODZAJ_KLASYFIKACJI = "klasyfikacja"
ZRODLA_KLASYFIKACJI = frozenset({"news_llm"})


def rodzaj_pary(para: Dict[str, Any]) -> str:
    """Jakiego RODZAJU zadania uczy ta para? Pole `rodzaj` > odtworzenie ze źródła."""
    jawny = (para.get("rodzaj") or "").strip().lower()
    if jawny in (RODZAJ_PROZA, RODZAJ_KLASYFIKACJI):
        return jawny
    return (RODZAJ_KLASYFIKACJI if para.get("zrodlo") in ZRODLA_KLASYFIKACJI
            else RODZAJ_PROZA)

# Progi zbioru — ILE PAR TRZEBA, żeby trening miał sens (zwiad web 2026-07-16, badania distylacji).
# Bez tych progów licznik „zebrano 47" nic nie mówi; z nimi Cezar widzi postęp wobec CELU (Prawo XXIV).
# ⚠️ To orientacyjne progi z literatury, nie prawo natury — rozstrzyga egzamin w arenie (E5).
PROGI_DATASETU = [
    (500,   "adaptacja stylu/formatu (uczeń zacznie brzmieć jak nauczyciel)"),
    (1_000, "specjalizacja domenowa — MINIMUM sensownego treningu LoRA"),
    (5_000, "mocna specjalizacja domenowa (wzorzec LIMA: 1000 doskonałych > 50000 miernych)"),
    (50_000, "nowe zdolności (poza naszym horyzontem — tyle nie uzbieramy szybko)"),
]


def postep_zbioru(par: int) -> Dict[str, Any]:
    """Do którego progu treningowego nam bliżej? Zwraca cel, procent i ile brakuje."""
    for prog, opis in PROGI_DATASETU:
        if par < prog:
            return {"cel": prog, "opis": opis, "procent": round(100.0 * par / prog, 1),
                    "brakuje": prog - par}
    ostatni, opis = PROGI_DATASETU[-1]
    return {"cel": ostatni, "opis": opis, "procent": 100.0, "brakuje": 0}


def wlaczony() -> bool:
    """Czy pisarz ma zapisywać? Wyłącznik: TIRO_NOTARIUS=0/false/nie."""
    wartosc = os.getenv(ENV_WYLACZNIK, "1").strip().lower()
    return wartosc not in ("0", "false", "nie", "off", "")


def _przytnij(tekst: str) -> tuple[str, bool]:
    """Zwraca (tekst, czy_przycięty). Przycięcie odnotowujemy — nie udajemy pełnego przykładu."""
    if len(tekst) <= LIMIT_ZNAKOW:
        return tekst, False
    return tekst[:LIMIT_ZNAKOW], True


def odcisk(system_prompt: str, tresc: str, odpowiedz: str) -> str:
    """
    Odcisk CAŁEJ pary (sha256, 16 znaków) — łapie dosłowne powtórzenie (re-run bez nowej wiedzy).
    Uwaga: sam ten odcisk NIE wystarcza — patrz `odcisk_pytania` i LIMIT_PROBEK_NA_PYTANIE.
    """
    surowe = f"{system_prompt}\x00{tresc}\x00{odpowiedz}".encode("utf-8", errors="replace")
    return hashlib.sha256(surowe).hexdigest()[:16]


def odcisk_pytania(system_prompt: str, tresc: str) -> str:
    """Odcisk SAMEGO pytania (bez odpowiedzi) — do limitowania próbek tego samego wejścia."""
    surowe = f"{system_prompt}\x00{tresc}".encode("utf-8", errors="replace")
    return hashlib.sha256(surowe).hexdigest()[:16]


def _zrodlo_wywolania() -> str:
    """
    Kto zadał pytanie? Idziemy w górę stosu do pierwszej ramki spoza organów mostu/pisarza.
    Dzięki temu wołający NIE MUSI nic przekazywać — a my wiemy, czy para pochodzi z analizy
    newsów, auto-lekcji, czy zwiadu bibliotekarza (przyda się przy ważeniu datasetu w E4).
    """
    try:
        import inspect
        wlasne = {"notarius.py", "deepseek_glos.py"}
        # `stack(0)` = context=0: BEZ czytania plików źródłowych. Domyślne `stack()` otwiera
        # i czyta plik KAŻDEJ ramki, żeby dołączyć linię kontekstu, której tu nie używamy
        # (bierzemy sam .filename) — przy głębokim stosie to kilkanaście zbędnych I/O na parę.
        for ramka in inspect.stack(0)[1:]:
            nazwa = Path(ramka.filename).name
            if nazwa not in wlasne and not nazwa.startswith("<"):
                return Path(ramka.filename).stem
    except Exception:  # noqa: BLE001 — rozpoznanie źródła nigdy nie może wywrócić zapisu
        pass
    return "nieznane"


class _Stan:
    """Stan zbioru potrzebny do decyzji o zapisie: odciski par + licznik próbek per pytanie."""

    __slots__ = ("pary", "pytania")

    def __init__(self) -> None:
        self.pary: set[str] = set()               # odciski całych par (dosłowne powtórzenia)
        self.pytania: Dict[str, int] = {}         # odcisk pytania → ile próbek już mamy


def _wczytaj_stan(sciezka: Path) -> _Stan:
    """Pełny odczyt stanu z pliku. Zepsute linie pomijamy — plik ma być odporny."""
    stan = _Stan()
    try:
        with sciezka.open("r", encoding="utf-8") as f:
            for linia in f:
                linia = linia.strip()
                if not linia:
                    continue
                try:
                    wpis = json.loads(linia)
                except json.JSONDecodeError:
                    continue          # uszkodzona linia nie blokuje reszty
                if not isinstance(wpis, dict):
                    continue
                if h := wpis.get("odcisk"):
                    stan.pary.add(h)
                # Starsze wpisy (sprzed limitu próbek) nie mają `odcisk_pytania` — odtwarzamy
                # go z treści, żeby limit działał też na tym, co już zebrane.
                hp = wpis.get("odcisk_pytania")
                if not hp and (wpis.get("prompt") is not None):
                    hp = odcisk_pytania(wpis.get("system") or "", wpis.get("prompt") or "")
                if hp:
                    stan.pytania[hp] = stan.pytania.get(hp, 0) + 1
    except OSError as e:
        logger.warning(f"[Notarius] Nie mogę odczytać {sciezka.name}: {e}")
    return stan


# Cache odcisków per plik: {ścieżka: (mtime_ns, rozmiar, zbiór_odcisków)}.
# POWÓD (recenzja 2026-07-16): bez cache dedup czytał i parsował CAŁY plik przy KAŻDYM
# zapisie — a zapis siedzi w ścieżce wywołania API. Przy docelowych 5000 par (plik dziesiątki
# MB) dawało to koszt kwadratowy i rosnące opóźnienie KAŻDEGO wywołania Hyginusa. To ta sama
# klasa wady, którą Księga Wad Kodu nazywa „I/O per iteracja → batchuj".
# Poprawność mimo cache: stat() (2 liczby) wykrywa zmianę pliku spoza procesu → przeładowanie.
_CACHE_STANU: Dict[str, tuple[int, int, _Stan]] = {}


def _znany_stan(sciezka: Path) -> _Stan:
    """
    Stan zbioru — z cache. Zamiast czytać cały plik, robimy `stat()`: gdy mtime i rozmiar
    zgadzają się z zapamiętanymi, plik jest ten sam → cache jest prawdą. Zmiana spoza procesu
    (inny proces, ręczna edycja) → przeładowanie. Brak pliku → stan pusty.
    """
    klucz = str(sciezka)
    try:
        st = sciezka.stat()
    except OSError:
        _CACHE_STANU.pop(klucz, None)      # plik zniknął → cache bezwartościowy
        return _Stan()

    wpis = _CACHE_STANU.get(klucz)
    if wpis and wpis[0] == st.st_mtime_ns and wpis[1] == st.st_size:
        return wpis[2]

    stan = _wczytaj_stan(sciezka)
    _CACHE_STANU[klucz] = (st.st_mtime_ns, st.st_size, stan)
    return stan


def _dopisz_do_cache(sciezka: Path, h: str, hp: str) -> None:
    """
    Po własnym zapisie: dołóż odciski i przestempluj stat — inaczej następny zapis czytałby plik od nowa.

    🚨 GRANICA (bug złapany testem 2026-07-16): inkrementujemy TYLKO gdy mamy cache sprzed zapisu.
    Gdy cache jest zimny, `_wczytaj_stan` czyta plik JUŻ ZAWIERAJĄCY nowy wpis — policzył go więc
    sam. Dodatkowa inkrementacja liczyłaby tę samą parę dwa razy i limit odpalałby o jeden
    za wcześnie. (Na zbiorze `pary` niewidoczne — set jest idempotentny; widać dopiero na liczniku.)
    """
    klucz = str(sciezka)
    try:
        st = sciezka.stat()
    except OSError:
        _CACHE_STANU.pop(klucz, None)
        return
    wpis = _CACHE_STANU.get(klucz)
    if wpis:
        stan = wpis[2]                                    # stan sprzed zapisu → dolicz nowy wpis
        stan.pary.add(h)
        stan.pytania[hp] = stan.pytania.get(hp, 0) + 1
    else:
        stan = _wczytaj_stan(sciezka)                     # świeży odczyt — nowy wpis już wliczony
    _CACHE_STANU[klucz] = (st.st_mtime_ns, st.st_size, stan)


def zapisz_pare(system_prompt: str,
                tresc: str,
                odpowiedz: str,
                model: str,
                temperatura: Optional[float] = None,
                zrodlo: Optional[str] = None,
                sciezka: Optional[Path] = None) -> bool:
    """
    Zapisz parę nauczyciel→odpowiedź. Zwraca True gdy dopisano nowy wpis.

    NIGDY nie rzuca wyjątku (żelazna zasada: pisarz nie przerywa mówcy). Pomija zapis gdy:
      • wyłączony przez TIRO_NOTARIUS=0,
      • pusta treść lub pusta odpowiedź (nie ma czego uczyć — Prawo XV: nie karmimy śmieciem),
      • dosłowny duplikat (identyczne pytanie ORAZ odpowiedź już w zbiorze),
      • osiągnięty LIMIT_PROBEK_NA_PYTANIE dla tego wejścia (anty-monokultura — patrz stała).
    """
    try:
        if not wlaczony():
            return False
        # Puste = bezwartościowe jako przykład treningowy. `None` też tu wpada (getattr-safe).
        if not (tresc and str(tresc).strip()) or not (odpowiedz and str(odpowiedz).strip()):
            return False

        cel = Path(sciezka) if sciezka else DOMYSLNA
        system_prompt = system_prompt or ""

        h = odcisk(system_prompt, tresc, odpowiedz)
        hp = odcisk_pytania(system_prompt, tresc)
        stan = _znany_stan(cel)

        if h in stan.pary:
            return False                       # dosłowne powtórzenie — zero nowej wiedzy
        if stan.pytania.get(hp, 0) >= LIMIT_PROBEK_NA_PYTANIE:
            # Mamy już dość próbek TEGO wejścia. Kolejne to monokultura (pętla live pyta
            # o te same nagłówki w kółko) + sprzeczne etykiety dla identycznego promptu.
            return False

        prompt_t, prompt_przyciety = _przytnij(str(tresc))
        odp_t, odp_przycieta = _przytnij(str(odpowiedz))
        system_t, system_przyciety = _przytnij(str(system_prompt))

        wpis: Dict[str, Any] = {
            "odcisk": h,
            # Zapisany wprost, żeby eksport mógł grupować próbki tego samego pytania
            # (konsensus) bez przeliczania hasha z treści.
            "odcisk_pytania": hp,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model": model,
            "temperatura": temperatura,
            "zrodlo": zrodlo or _zrodlo_wywolania(),
            "system": system_t,
            "prompt": prompt_t,
            "odpowiedz": odp_t,
            "znakow_prompt": len(str(tresc)),
            "znakow_odpowiedzi": len(str(odpowiedz)),
        }
        if prompt_przyciety or odp_przycieta or system_przyciety:
            # Prawo I: przycięty przykład jest oznaczony, nie udaje pełnego.
            wpis["przyciety"] = True

        cel.parent.mkdir(parents=True, exist_ok=True)
        with cel.open("a", encoding="utf-8") as f:
            f.write(json.dumps(wpis, ensure_ascii=False) + "\n")
        _dopisz_do_cache(cel, h, hp)
        return True

    except Exception as e:  # noqa: BLE001 — ŻELAZNA ZASADA: awaria pisarza ≠ awaria nauczyciela
        logger.warning(f"[Notarius] Nie zapisałem pary (nauczyciel działa dalej): {e}")
        return False


def czytaj_pary(sciezka: Optional[Path] = None) -> Iterator[Dict[str, Any]]:
    """Strumień zapisanych par (leniwie — zbiór może urosnąć; ZASADA ANALIZY CZĄSTKOWEJ)."""
    cel = Path(sciezka) if sciezka else DOMYSLNA
    if not cel.exists():
        return
    with cel.open("r", encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                continue
            try:
                wpis = json.loads(linia)
            except json.JSONDecodeError:
                continue
            if isinstance(wpis, dict):
                yield wpis


def statystyki(sciezka: Optional[Path] = None) -> Dict[str, Any]:
    """
    Ile mamy materiału treningowego? (Prawo XXIV — Cezar ma WIDZIEĆ postęp zbierania.)

    Liczy STRUMIENIOWO — `czytaj_pary` obiecuje leniwość (ZASADA ANALIZY CZĄSTKOWEJ), więc
    jej jedyny konsument nie może tego niweczyć przez `list()`. Materializacja 5000 par po
    ~200k znaków to ~1 GB na maszynie, która ma 16 GB i ledwo mieści model (recenzja 2026-07-16).
    """
    zrodla: Dict[str, int] = {}
    modele: Dict[str, int] = {}
    znakow = 0
    par = 0
    przyciete = 0
    pierwszy = ostatni = None
    for p in czytaj_pary(sciezka):
        par += 1
        zrodla[p.get("zrodlo", "nieznane")] = zrodla.get(p.get("zrodlo", "nieznane"), 0) + 1
        modele[p.get("model", "?")] = modele.get(p.get("model", "?"), 0) + 1
        znakow += int(p.get("znakow_odpowiedzi") or 0)
        if p.get("przyciety"):
            przyciete += 1
        # min/max w locie — nie trzymamy listy dat tylko po to, żeby wziąć z niej dwa końce.
        if ts := p.get("ts"):
            if pierwszy is None or ts < pierwszy:
                pierwszy = ts
            if ostatni is None or ts > ostatni:
                ostatni = ts
    return {
        "par": par,
        "przyciete": przyciete,
        "postep": postep_zbioru(par),
        "zrodla": dict(sorted(zrodla.items(), key=lambda x: -x[1])),
        "modele": modele,
        "znakow_odpowiedzi": znakow,
        # Zgrubny przelicznik: ~4 znaki/token dla tekstu PL/EN — orientacyjny, nie pomiar.
        "szac_tokenow_odpowiedzi": znakow // 4,
        "pierwszy": pierwszy,
        "ostatni": ostatni,
        "wlaczony": wlaczony(),
        "plik": str(Path(sciezka) if sciezka else DOMYSLNA),
    }


def _obiekt_json(odpowiedz: str) -> Optional[Dict[str, Any]]:
    """Odpowiedź klasyfikatora jako obiekt JSON — albo None, gdy to nie jest obiekt JSON.

    Test WŁAŚCIWY RODZAJOWI zadania (patrz `RODZAJ_KLASYFIKACJI`): zepsuty JSON uczyłby ucznia
    produkować wyjście, którego parser wołającego nie przyjmie — a to gorsze niż brak przykładu.
    """
    try:
        wynik = json.loads(odpowiedz)
    except (json.JSONDecodeError, TypeError):
        return None
    return wynik if isinstance(wynik, dict) and wynik else None


def _konsensus_klasyfikacji(odpowiedzi: List[str]) -> Optional[str]:
    """
    MEDIANA kilku strzałów nauczyciela zamiast pierwszego z brzegu (self-consistency).

    DŁUG SPŁACONY, NIE NOWY POMYSŁ: pole `odcisk_pytania` zostało dopisane do każdego wpisu
    właśnie po to, „żeby eksport mógł grupować próbki tego samego pytania (konsensus)", a
    `eksportuj_sft` odkładał to na E4 i brał PIERWSZĄ próbkę. Zmierzone 2026-07-27 na żywym
    ledgerze: 32 pytania miały >1 próbkę, a w 3 z nich pierwsza próbka ma ZNAK PRZECIWNY niż
    mediana (np. próbki +0.20 / −0.30 / −0.20 → pierwsza uczy byka, konsensus niedźwiedzia).
    Czyli 9% etykiet klasyfikacji było odwróconych — to nie oszczędność, to trucizna.

    Reguła: pola liczbowe obecne we WSZYSTKICH próbkach → mediana; pozostałe → wartość z
    pierwszej próbki (kolejność kluczy też z pierwszej — wynik ma być deterministyczny).
    Wyjście serializujemy KANONICZNIE: uczeń ma widzieć jeden format, nie raz wcięcia, raz nie.
    """
    obiekty = [o for o in (_obiekt_json(x) for x in odpowiedzi) if o is not None]
    if not obiekty:
        return None
    pierwszy = obiekty[0]
    zgoda: Dict[str, Any] = {}
    for klucz, wartosc in pierwszy.items():
        probki = [o[klucz] for o in obiekty if klucz in o]
        liczbowe = [x for x in probki
                    if isinstance(x, (int, float)) and not isinstance(x, bool)]
        zgoda[klucz] = (statistics.median(liczbowe)
                        if len(liczbowe) == len(obiekty) else wartosc)
    return json.dumps(zgoda, ensure_ascii=False)


def _przyklad_sft(para: Dict[str, Any], odpowiedz: str) -> Dict[str, Any]:
    """Jedna para → format `{"messages": [...]}` (Unsloth/TRL/Axolotl bez konwersji)."""
    wiadomosci: List[Dict[str, str]] = []
    if para.get("system"):
        wiadomosci.append({"role": "system", "content": para["system"]})
    wiadomosci.append({"role": "user", "content": para.get("prompt", "")})
    wiadomosci.append({"role": "assistant", "content": odpowiedz})
    return {"messages": wiadomosci}


def pary_sft(sciezka: Optional[Path] = None,
             min_znakow_odpowiedzi: int = 0,
             pomin_przyciete: bool = True,
             jedna_probka_na_pytanie: bool = True) -> Iterator[Dict[str, Any]]:
    """
    JEDYNE miejsce, gdzie żyje filtr zbioru treningowego — strumień gotowych przykładów SFT.

    Wydzielone z `eksportuj_sft` (recenzja 2026-07-26): meldunek BREVIARIUM potrzebuje samej
    LICZBY par użytecznych, a żeby ją poznać, serializował cały zbiór do pliku tymczasowego —
    czyli płacił zapisem dysku za policzenie. Konsumenci (eksport i licznik) muszą jednak
    dzielić DOKŁADNIE ten sam filtr: dwa niezależne filtry rozjadą się co do sztuki i meldunek
    zacznie opisywać inny zbiór niż ten, który pojedzie na trening (Prawo XVI).

    DWA TORY WEDŁUG RODZAJU ZADANIA (2026-07-27, patrz `RODZAJ_KLASYFIKACJI`):
      • proza — próg długości + pierwsza próbka na pytanie (zachowanie niezmienione),
      • klasyfikacja — próg długości NIE OBOWIĄZUJE (poprawny werdykt ma 34 znaki), decyduje
        poprawność struktury, a próbki tego samego pytania zwija KONSENSUS, nie „pierwsza".

    Leniwość: proza leci strumieniem jak dotąd; bufor trzyma wyłącznie krótkie odpowiedzi
    klasyfikacji (≤ LIMIT_PROBEK_NA_PYTANIE na pytanie), więc obietnica z `czytaj_pary`
    zostaje w mocy — konsensus z definicji wymaga zobaczenia wszystkich próbek pytania.

    Znaczenie filtrów opisuje `eksportuj_sft` — tam została pełna argumentacja każdego progu.
    """
    widziane_pytania: set[str] = set()
    kubelki: Dict[str, tuple[Dict[str, Any], List[str]]] = {}
    for p in czytaj_pary(sciezka):
        if pomin_przyciete and p.get("przyciety"):
            continue
        odp = p.get("odpowiedz") or ""
        # Starsze wpisy nie mają pola — odtwarzamy odcisk z treści, żeby kolaps
        # działał też na tym, co zebrano przed wprowadzeniem limitu.
        hp = p.get("odcisk_pytania") or odcisk_pytania(p.get("system") or "",
                                                       p.get("prompt") or "")
        if rodzaj_pary(p) == RODZAJ_KLASYFIKACJI:
            if _obiekt_json(odp) is None:
                # Zepsuty JSON nie wchodzi do zbioru W ŻADNYM TRYBIE. Sam konsensus by tu nie
                # wystarczył — on pomija wadliwe próbki, ale tylko na ścieżce zwijania; przy
                # `jedna_probka_na_pytanie=False` wadliwa próbka poszłaby prosto na eksport.
                # (Ta bramka była opisana jako obrona przed „wadliwą pierwszą próbką" — MUTACJA
                #  2026-07-27 pokazała, że przed TYM broni już konsensus, a prawdziwy powód jest
                #  ten powyżej. Komentarz opisuje teraz to, co test faktycznie udowadnia.)
                continue
            if not jedna_probka_na_pytanie:
                yield _przyklad_sft(p, odp)
                continue
            kubelki.setdefault(hp, (p, []))[1].append(odp)
            continue
        if len(odp) < min_znakow_odpowiedzi:
            continue
        if jedna_probka_na_pytanie:
            if hp in widziane_pytania:
                continue
            widziane_pytania.add(hp)
        yield _przyklad_sft(p, odp)

    for szablon, odpowiedzi in kubelki.values():     # dict trzyma kolejność wstawiania → determinizm
        if (zgoda := _konsensus_klasyfikacji(odpowiedzi)) is not None:
            yield _przyklad_sft(szablon, zgoda)


def policz_sft(sciezka: Optional[Path] = None,
               min_znakow_odpowiedzi: int = 0,
               pomin_przyciete: bool = True,
               jedna_probka_na_pytanie: bool = True) -> int:
    """Ile par PRZEŻYJE eksport — bez zapisywania czegokolwiek na dysk.

    Meldunek o postępie Szkoły TIRO biegnie na OBU końcach każdej sesji, więc nie ma prawa
    kosztować zapisu całego zbioru (koszt rósłby z każdą zebraną parą). Liczy ten sam filtr,
    co eksport — `pary_sft`.
    """
    return sum(1 for _ in pary_sft(sciezka, min_znakow_odpowiedzi,
                                   pomin_przyciete, jedna_probka_na_pytanie))


def eksportuj_sft(cel: Path, sciezka: Optional[Path] = None,
                  min_znakow_odpowiedzi: int = 0,
                  pomin_przyciete: bool = True,
                  jedna_probka_na_pytanie: bool = True) -> int:
    """
    Eksport do formatu SFT (Supervised Fine-Tuning) — `{"messages": [...]}` per linia.
    To format, który łykają Unsloth / TRL / Axolotl bez konwersji (etap E4, trening w Colab).

    `min_znakow_odpowiedzi` — filtr jakości: krótkie odpowiedzi („nie wiem", błąd) uczą szumu.
    🚨 DOTYCZY WYŁĄCZNIE PROZY. Dla par klasyfikacji (`RODZAJ_KLASYFIKACJI`) poprawna odpowiedź
    jest krótka z definicji, więc o dopuszczeniu decyduje poprawność struktury, nie długość.

    `pomin_przyciete` (domyślnie True) — 🚨 przycięta odpowiedź URYWA SIĘ W PÓŁ SŁOWA. Podana
    uczniowi jako wzorzec uczy go, że tak wygląda poprawna odpowiedź — czyli uczy urywania.
    To trucizna wprost przeciw zasadzie LIMA (1000 doskonałych > 50000 miernych), na której
    oparliśmy progi zbioru. Wyłączaj świadomie i tylko do inspekcji (recenzja 2026-07-16).

    `jedna_probka_na_pytanie` (domyślnie True) — 🚨 zbiór trzyma do LIMIT_PROBEK_NA_PYTANIE
    próbek tego samego wejścia, a nauczyciel bywa NIESPÓJNY: zmierzone 2026-07-16 — ten sam
    zestaw nagłówków dostał sentyment +0.8 i -0.4. Wyeksportowanie obu uczy model SPRZECZNYCH
    etykiet dla identycznego promptu (najgorszy możliwy sygnał).
      • proza — bierzemy PIERWSZĄ próbkę per pytanie (dwóch rozwinięć nie da się uśrednić),
      • klasyfikacja — bierzemy KONSENSUS (mediana pól liczbowych, `_konsensus_klasyfikacji`).
    Konsensus domyka dług zapisany w tym docstringu jako „praca na E4": surowe próbki leżały
    w zbiorze po to, by go policzyć, a eksport i tak brał pierwszą z brzegu. Zmierzone
    2026-07-27: w 3 z 32 wielopróbkowych pytań pierwsza próbka ma znak PRZECIWNY do mediany.

    Zwraca liczbę wyeksportowanych przykładów.
    """
    cel = Path(cel)
    cel.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with cel.open("w", encoding="utf-8") as f:
        for przyklad in pary_sft(sciezka, min_znakow_odpowiedzi,
                                 pomin_przyciete, jedna_probka_na_pytanie):
            f.write(json.dumps(przyklad, ensure_ascii=False) + "\n")
            n += 1
    return n


def raport(sciezka: Optional[Path] = None) -> str:
    """Czytelny raport stanu zbierania."""
    s = statystyki(sciezka)
    stan = "✅ WŁĄCZONY" if s["wlaczony"] else f"⏸️ WYŁĄCZONY ({ENV_WYLACZNIK}=0)"
    p = s["postep"]
    # Pasek postępu (Prawo XXIV): Cezar ma WIDZIEĆ, jak daleko do progu treningu.
    wypelnienie = int(p["procent"] / 5)   # 20 pól = 100%
    pasek = "█" * min(wypelnienie, 20) + "░" * max(0, 20 - wypelnienie)
    linie = [
        "📜 NOTARIUS — protokół słów Nauczyciela (surowiec Szkoły TIRO)",
        f"   • Stan pisarza: {stan}",
        f"   • Par zebranych: {s['par']}",
        f"   • Do progu:  [{pasek}] {p['procent']}% — {s['par']}/{p['cel']} "
        f"(brakuje {p['brakuje']})",
        f"     ↳ próg = {p['opis']}",
        f"   • Materiał: ~{s['szac_tokenow_odpowiedzi']:,} tokenów odpowiedzi "
        f"({s['znakow_odpowiedzi']:,} znaków, szacunek 4 zn./token)",
        f"   • Plik: {s['plik']}",
    ]
    if s["zrodla"]:
        linie.append("   • Źródła: " + ", ".join(f"{k}={v}" for k, v in s["zrodla"].items()))
    if s["modele"]:
        linie.append("   • Nauczyciele: " + ", ".join(f"{k}={v}" for k, v in s["modele"].items()))
    if s["pierwszy"]:
        linie.append(f"   • Zakres: {s['pierwszy']} → {s['ostatni']}")
    if s["par"] == 0:
        linie.append("   ℹ️ Pusto — pary pojawią się przy pierwszym wywołaniu Hyginusa (GlosImperium).")
    return "\n".join(linie)


if __name__ == "__main__":
    import sys

    komenda = sys.argv[1] if len(sys.argv) > 1 else "raport"
    if komenda == "raport":
        print(raport())
    elif komenda == "eksport":
        wyjscie = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "dane" / "tiro_sft.jsonl"
        ile = eksportuj_sft(wyjscie, min_znakow_odpowiedzi=50)
        print(f"✅ Wyeksportowano {ile} przykładów SFT → {wyjscie}")
    else:
        print(__doc__)
        print(f"Nieznana komenda: {komenda}")
        sys.exit(1)
