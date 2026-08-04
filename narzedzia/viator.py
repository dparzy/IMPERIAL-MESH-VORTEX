"""
🐎 VIATOR — posłaniec dróg: wsadowy sąd nad linkami w materiale zewnętrznym.

W Rzymie *viator* to urzędnik-posłaniec, który przemierzał drogi, by wezwać senatora
albo sprawdzić, dokąd droga prowadzi. Ten organ robi to samo z linkami: bierze plik
z wrzutni, wyciąga KAŻDY adres i melduje, które drogi są przejezdne, a które prowadzą
donikąd — zanim ktokolwiek zacznie czytać treść.

POWÓD ISTNIENIA (rozkaz Cezara 2026-08-02, zadanie H0): `wrzutnia/Imperium-Botów-
Tradingowych 1.md` ma 13 821 linii i **230 unikalnych linków**. Sprawdzanie ich ręcznie
nie jest pracowitością — jest BŁĘDEM METODY: 230 tur po jednym linku spala kontekst
i tak nie daje liczby, którą można zacytować.

ZASADY, KTÓRE TEN ORGAN RESPEKTUJE:
- **Prawo XXIV (analiza cząstkowa)** — bieg jest WZNAWIALNY: każdy wynik ląduje
  natychmiast w cache JSONL (append-only), więc przerwane 230 linków wznawia się
  od miejsca przerwania, nie od zera. Pasek postępu leci na żywo.
- **Pasek na stderr, wynik na stdout** — lekcja zapłacona w wachcie G1: pasek postępu
  DISCRIMINATORA szedł na stdout i czynił `--json` niesparsowalnym. Testy tego nie
  widziały, bo wołały funkcję, nie CLI.
- **Prawo I (nie zgadujemy)** — link nieosiągalny z powodu blokady bota (403/429) NIE
  jest nazywany martwym. `ZABLOKOWANY` to stan naszego przyrządu, nie stan drogi.
  Tę różnicę zjada każdy naiwny link-checker i produkuje fałszywe „linki nie działają".
- **Grzeczność wobec cudzych serwerów** — odstęp per DOMENA (nie globalny), bo 115 z 230
  linków to jeden host (github.com). Bez tego dostalibyśmy 429 i uznali repo za martwe.
- **Bezpieczeństwo** — adresy lokalne/prywatne (localhost, 127.0.0.1, 10.x, 192.168.x)
  są POMIJANE, nie odpytywane: sprawdzanie ich niczego nie dowodzi o cudzym repo,
  a odpytywanie prywatnej sieci z pliku przyniesionego z zewnątrz to wektor SSRF.

Uruchom:
    python narzedzia/viator.py --plik "wrzutnia/Imperium-Botów-Tradingowych 1.md"
    python narzedzia/viator.py --plik <p> --json            # czysty JSON na stdout
    python narzedzia/viator.py --plik <p> --tylko-podsumowanie
    python narzedzia/viator.py --plik <p> --odswiez         # ignoruj cache
    python narzedzia/viator.py --plik <p> --limit 20        # partia próbna
"""
import argparse
import ipaddress
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from urllib.parse import urlsplit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CACHE_DOMYSLNY = os.path.join(
    os.path.dirname(__file__), "..", "bibliotheca_ulpia", "dane", "viator_cache.jsonl"
)

# Przeglądarkowy UA — bez niego arxiv/github odrzucają ruch skryptowy i dostajemy
# fałszywe „martwe". Nie udajemy człowieka: podajemy się z nazwy poniżej.
UA = "Mozilla/5.0 (compatible; ImperiumViator/1.0; +sad-nad-materialem-zewnetrznym)"

ODSTEP_NA_DOMENE_S = 0.6   # grzeczność: min. przerwa między pukaniem do tego samego hosta
TIMEOUT_S = 12.0
WATKI = 8

# Stany drogi. ZABLOKOWANY i BLAD są świadomie ODDZIELONE od MARTWY (Prawo I).
ZYWY = "ZYWY"                # 2xx — droga przejezdna
PRZEKIEROWANY = "PRZEKIEROWANY"  # 2xx, ale pod innym adresem niż podany
MARTWY = "MARTWY"            # 404/410 — serwer mówi wprost: nie ma tego
ZABLOKOWANY = "ZABLOKOWANY"  # 403/429 — serwer żyje, ale nas nie wpuszcza
AWARIA_SERWERA = "AWARIA_SERWERA"  # 5xx — nie nasza wina i nie wyrok o treści
BLAD = "BLAD"                # DNS/timeout/TLS — nie wiemy, i tak to nazywamy
POMINIETY = "POMINIETY"      # localhost/adres prywatny — świadomie nie pytamy

# Stany, których NIE WOLNO czytać jako „link nie działa" przy sądzie nad materiałem.
NIEROZSTRZYGNIETE = frozenset({ZABLOKOWANY, AWARIA_SERWERA, BLAD})

# Nawias zamykający JEST wpuszczany do dopasowania i dopiero `przytnij_ogon` decyduje,
# czy należy do adresu (Wikipedia: `..._(betting)`), czy zamyka składnię markdown.
# Wyłączenie go z regexa wprost — pierwsza wersja tego organu — cicho ucinało takie
# adresy i zgłaszało je jako MARTWE. Złapał to test granicy, nie bieg na żywo.
# `[` też wyklęte — materiał z czatu DeepSeeka dokleja znaczniki `[reference:8]` wprost
# do adresu (`https://huggingface.co/X)[reference:8`). Druga fałszywka tej samej klasy
# co `)**`, znaleziona w drugim biegu próbnym. W adresach `[` jest enkodowane jako %5B.
# Backtick też — materiał wstawia adresy w `kod`, a znak zamykający kleił się do URL-a.
_WZORZEC_URL = re.compile(r"https?://[^\s<>\"'`\[\]\}\\|]+")
# Ogon interpunkcyjny: „(zob. https://x.org/a.)" — kropka/przecinek nie są częścią adresu.
# Nawias zamykający ŚWIADOMIE poza tym zbiorem: zdejmowany bezwarunkowo psułby
# `..._(betting)`. O jego losie rozstrzyga dopiero test sparowania w `przytnij_ogon`.
#
# GWIAZDKA JEST TU ZA CENĘ POMIARU, NIE Z PRZEZORNOŚCI. Pierwszy bieg próbny na
# realnym materiale zgłosił 19/20 adresów jako MARTWE — wszystkie kończyły się na
# `)**`, czyli markdownowym pogrubieniem `**[nazwa](url)**`. Repozytoria żyły;
# martwy był mój regex. Dlatego partia próbna JEST częścią budowy przyrządu:
# gdyby ten bieg poszedł na 230 adresów i wprost do meldunku, Imperium skasowałoby
# 19 żywych propozycji na podstawie własnej wady (LEX TALARUS).
# `_` świadomie NIE wchodzi: jest częstym znakiem w ścieżkach (`Kelly_criterion`).
_OGON = ".,;:!?'\"’”»*"


@dataclass
class Droga:
    """Werdykt o jednym adresie."""

    url: str
    status: str
    kod: int | None = None
    finalny_url: str | None = None
    komunikat: str = ""
    ts: float = field(default_factory=time.time)

    @property
    def rozstrzygniety(self) -> bool:
        """Czy ten werdykt mówi cokolwiek o TREŚCI pod adresem."""
        return self.status not in NIEROZSTRZYGNIETE


def przytnij_ogon(url: str) -> str:
    """Usuwa interpunkcję zdania doklejoną do adresu i domyka niesparowany nawias."""
    url = url.rstrip(_OGON)
    # „https://en.wikipedia.org/wiki/Foo_(bar)" — nawias JEST częścią adresu, jeśli sparowany.
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1].rstrip(_OGON)
    return url


def wyciagnij_linki(tekst: str) -> list[str]:
    """Zwraca UNIKALNE adresy w kolejności pierwszego wystąpienia (stabilnie, nie losowo)."""
    widziane: dict[str, None] = {}
    for surowy in _WZORZEC_URL.findall(tekst):
        url = przytnij_ogon(surowy)
        if url and url not in widziane:
            widziane[url] = None
    return list(widziane)


def _host_prywatny(host: str) -> bool:
    """True dla localhost i adresów spoza publicznego internetu (ochrona przed SSRF)."""
    if not host:
        return True
    czysty = host.split(":")[0].strip("[]").lower()
    if czysty in ("localhost", "localhost.localdomain") or czysty.endswith(".local"):
        return True
    try:
        return ipaddress.ip_address(czysty).is_private or ipaddress.ip_address(czysty).is_loopback
    except ValueError:
        return False  # nazwa domenowa — rozstrzyga DNS przy realnym połączeniu


def domena(url: str) -> str:
    try:
        return urlsplit(url).netloc.lower()
    except ValueError:
        return ""


def _klasyfikuj(kod: int) -> str:
    if 200 <= kod < 300:
        return ZYWY
    if kod in (404, 410):
        return MARTWY
    if kod in (401, 403, 429):
        return ZABLOKOWANY
    if 500 <= kod < 600:
        return AWARIA_SERWERA
    return BLAD


class _Bramkarz:
    """Pilnuje odstępu między pukaniem do tego samego hosta (grzeczność, nie throttling globalny)."""

    def __init__(self, odstep_s: float = ODSTEP_NA_DOMENE_S) -> None:
        self._odstep = odstep_s
        self._ostatnie: dict[str, float] = {}
        self._zamek = threading.Lock()

    def przepusc(self, host: str) -> None:
        while True:
            with self._zamek:
                teraz = time.monotonic()
                poprzednie = self._ostatnie.get(host, 0.0)
                if teraz - poprzednie >= self._odstep:
                    self._ostatnie[host] = teraz
                    return
                czekaj = self._odstep - (teraz - poprzednie)
            time.sleep(czekaj)


def kontekst_ssl() -> "ssl.SSLContext":
    """Kontekst TLS z certyfikatami `certifi`.

    POWÓD ZMIERZONY 2026-08-02: na tym Windowsie `ssl.get_default_verify_paths().cafile`
    to **None** — Python nie ma ŻADNEGO magazynu zaufanych certyfikatów. Skutek: pierwszy
    pełny bieg VIATORA zgłosił 86 adresów jako BŁĄD z jednym powodem
    (`CERTIFICATE_VERIFY_FAILED`), z czego **83 to arxiv.org** — czyli cały naukowy
    fundament badanego materiału. To była ślepota NASZEGO przyrządu, nie awaria arXiv.

    Weryfikacji NIE WYŁĄCZAMY (`verify_mode=CERT_NONE` uciszyłoby objaw i otworzyło
    nas na podmianę treści w drodze) — dokładamy brakujący magazyn.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001 — brak certifi nie może zabić organu
        return ssl.create_default_context()


def domyslny_otwieracz():
    """urlopen z naszym kontekstem TLS (testy wstrzykują własny otwieracz i tu nie wchodzą)."""
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=kontekst_ssl())).open


def _otworz(url: str, metoda: str, timeout: float, otwieracz) -> tuple[int, str]:
    """Zwraca (kod, finalny_url). Wyjątki HTTP też niosą kod — łapiemy je jako odpowiedź."""
    zadanie = urllib.request.Request(url, method=metoda, headers={"User-Agent": UA})
    if metoda == "GET":
        # Nie ściągamy treści — prosimy o jeden bajt. Serwer i tak zwraca status.
        zadanie.add_header("Range", "bytes=0-0")
    with otwieracz(zadanie, timeout=timeout) as odp:
        return odp.getcode(), odp.geturl()


def sprawdz_link(url: str, timeout: float = TIMEOUT_S, otwieracz=None) -> Droga:
    """Sprawdza JEDEN adres. `otwieracz` wstrzykiwalny — testy nie dotykają sieci."""
    otwieracz = otwieracz or domyslny_otwieracz()
    if _host_prywatny(domena(url)):
        return Droga(url, POMINIETY, komunikat="adres lokalny/prywatny — świadomie nie pytamy")

    for metoda in ("HEAD", "GET"):
        try:
            kod, finalny = _otworz(url, metoda, timeout, otwieracz)
        except urllib.error.HTTPError as e:
            kod, finalny = e.code, getattr(e, "url", url) or url
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            powod = getattr(e, "reason", e)
            return Droga(url, BLAD, komunikat=f"{type(e).__name__}: {powod}")
        except Exception as e:  # noqa: BLE001 — cudzy serwer potrafi wszystko; nie wywracamy biegu
            return Droga(url, BLAD, komunikat=f"{type(e).__name__}: {e}")

        status = _klasyfikuj(kod)
        # 403/405 na HEAD zwykle znaczy „ten serwer nie lubi HEAD", nie „brak zasobu".
        if metoda == "HEAD" and kod in (403, 405, 501):
            continue
        if status == ZYWY and finalny and finalny.rstrip("/") != url.rstrip("/"):
            status = PRZEKIEROWANY
        return Droga(url, status, kod=kod, finalny_url=finalny)

    return Droga(url, BLAD, komunikat="HEAD i GET nie dały rozstrzygnięcia")


def wczytaj_cache(sciezka: str, tylko_rozstrzygniete: bool = True) -> dict[str, Droga]:
    """Cache JSONL append-only. Późniejszy wpis o tym samym URL wygrywa (ostatnie słowo).

    NIEROZSTRZYGNIĘTE NIE WRACAJĄ Z CACHE (`tylko_rozstrzygniete=True`, domyślnie).
    Naprawa własnej wady złapanej recenzją tej wachty: `BLAD` (timeout, DNS) i
    `ZABLOKOWANY` (403/429) to stany NASZEGO przyrządu, nie wyroki o drodze — ten organ
    mówi to wprost w docstringu modułu, a mimo to zapisywał je do cache jak wyroki.
    Skutek: jeden chwilowy timeout na 20 adresach utrwalał się NA ZAWSZE, bo kolejny
    bieg czytał go z pliku i nie pukał ponownie. Jedynym lekarstwem był `--odswiez`,
    który kasuje też setki poprawnych wyników — czyli kara za awarię sieci spadała na
    cały bieg. To ta sama klasa, na którą `ab_plon_hyginusa` ma osobny test
    (`test_blad_sieci_nie_utrwala_sie_jako_wynik`); VIATOR jej nie miał.

    Wpisy ZOSTAJĄ w pliku (kontrakt append-only pilnowany przez VINDEXA jest nienaruszony)
    — po prostu nie są uznawane za wiedzę przy wznowieniu. Ślad pomiaru: tak, wyrok: nie.
    """
    znane: dict[str, Droga] = {}
    if not os.path.exists(sciezka):
        return znane
    with open(sciezka, encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                continue
            try:
                d = json.loads(linia)
                droga = Droga(**d)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue  # uszkodzona linia nie może zabić wznowienia
            if tylko_rozstrzygniete and not droga.rozstrzygniety:
                # świadomie USUWAMY wcześniejszy wyrok, jeśli późniejszy wpis jest
                # nierozstrzygnięty — inaczej „ostatnie słowo" przestałoby obowiązywać
                znane.pop(droga.url, None)
                continue
            znane[droga.url] = droga
    return znane


def sprawdz_wsadowo(
    urls: list[str],
    watki: int = WATKI,
    cache_sciezka: str | None = CACHE_DOMYSLNY,
    odswiez: bool = False,
    postep: bool = True,
    timeout: float = TIMEOUT_S,
    otwieracz=None,
) -> list[Droga]:
    """Sprawdza listę adresów równolegle, wznawialnie, z paskiem postępu na stderr."""
    znane = {} if odswiez or not cache_sciezka else wczytaj_cache(cache_sciezka)
    do_zrobienia = [u for u in urls if u not in znane]
    n = len(do_zrobienia)
    if postep and znane:
        gotowe = len(urls) - n
        print(f"[viator] z cache: {gotowe}/{len(urls)} — do sprawdzenia {n}", file=sys.stderr)

    bramkarz = _Bramkarz()
    zamek_zapisu = threading.Lock()
    licznik = {"i": 0}
    plik = None
    if cache_sciezka and n:
        os.makedirs(os.path.dirname(os.path.abspath(cache_sciezka)), exist_ok=True)
        plik = open(cache_sciezka, "a", encoding="utf-8")  # noqa: SIM115 — zamykany w finally

    def zadanie(url: str) -> Droga:
        bramkarz.przepusc(domena(url))
        wynik = sprawdz_link(url, timeout=timeout, otwieracz=otwieracz)
        with zamek_zapisu:
            licznik["i"] += 1
            if plik:  # zapis NATYCHMIAST — to jest cała wznawialność (Prawo XXIV)
                plik.write(json.dumps(asdict(wynik), ensure_ascii=False) + "\n")
                plik.flush()
            if postep:
                print(
                    f"\r[{licznik['i']}/{n}] {wynik.status:<14} {url[:60]:<60}",
                    end="", file=sys.stderr, flush=True,
                )
        return wynik

    try:
        if n:
            with ThreadPoolExecutor(max_workers=max(1, watki)) as pula:
                for w in pula.map(zadanie, do_zrobienia):
                    znane[w.url] = w
            if postep:
                print("", file=sys.stderr, flush=True)
    finally:
        if plik:
            plik.close()

    return [znane[u] for u in urls if u in znane]


def podsumuj(drogi: list[Droga]) -> dict:
    """Liczby, które wolno zacytować — z jawnym podziałem na rozstrzygnięte i nie."""
    wg_statusu: dict[str, int] = {}
    for d in drogi:
        wg_statusu[d.status] = wg_statusu.get(d.status, 0) + 1
    wg_domen: dict[str, int] = {}
    for d in drogi:
        wg_domen[domena(d.url)] = wg_domen.get(domena(d.url), 0) + 1
    nierozstrzygniete = sum(1 for d in drogi if not d.rozstrzygniety)
    return {
        "lacznie": len(drogi),
        "wg_statusu": dict(sorted(wg_statusu.items(), key=lambda kv: -kv[1])),
        "rozstrzygniete": len(drogi) - nierozstrzygniete,
        "nierozstrzygniete": nierozstrzygniete,
        "martwe": wg_statusu.get(MARTWY, 0),
        "top_domeny": dict(sorted(wg_domen.items(), key=lambda kv: -kv[1])[:10]),
    }


def _drukuj_raport(drogi: list[Droga], podsum: dict) -> None:
    print("🐎 VIATOR — sąd nad drogami (linkami) materiału zewnętrznego")
    print(f"   adresów zbadanych: {podsum['lacznie']}")
    for status, ile in podsum["wg_statusu"].items():
        znak = {ZYWY: "✅", PRZEKIEROWANY: "↪️", MARTWY: "💀", ZABLOKOWANY: "🚧",
                AWARIA_SERWERA: "🔥", BLAD: "⚠️", POMINIETY: "⏭️"}.get(status, "·")
        print(f"   {znak} {status:<15} {ile}")
    print(f"\n   ROZSTRZYGNIĘTE: {podsum['rozstrzygniete']} "
          f"| NIEROZSTRZYGNIĘTE: {podsum['nierozstrzygniete']} "
          f"(blokada/awaria/błąd — to stan PRZYRZĄDU, nie wyrok o drodze)")
    martwe = [d for d in drogi if d.status == MARTWY]
    if martwe:
        print(f"\n   💀 MARTWE ({len(martwe)}) — te propozycje nie mają już źródła:")
        for d in martwe:
            print(f"      [{d.kod}] {d.url}")
    nieroz = [d for d in drogi if not d.rozstrzygniety]
    if nieroz:
        print(f"\n   ⚠️  NIEROZSTRZYGNIĘTE ({len(nieroz)}) — wymagają ręcznego spojrzenia:")
        for d in nieroz[:20]:
            print(f"      [{d.status}] {d.url}  {d.komunikat[:60]}")
        if len(nieroz) > 20:
            print(f"      … i {len(nieroz) - 20} więcej (pełna lista w --json)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="VIATOR — wsadowy sąd nad linkami")
    p.add_argument("--plik", required=True, help="plik .md do przeskanowania")
    p.add_argument("--watki", type=int, default=WATKI)
    p.add_argument("--timeout", type=float, default=TIMEOUT_S)
    p.add_argument("--limit", type=int, default=0, help="sprawdź tylko pierwsze N (partia próbna)")
    p.add_argument("--cache", default=CACHE_DOMYSLNY)
    p.add_argument("--odswiez", action="store_true", help="ignoruj cache, pukaj od nowa")
    p.add_argument("--json", action="store_true", help="czysty JSON na stdout (pasek idzie na stderr)")
    p.add_argument("--tylko-podsumowanie", action="store_true")
    a = p.parse_args(argv)

    if not os.path.exists(a.plik):
        print(f"🚨 nie ma pliku: {a.plik}", file=sys.stderr)
        return 2

    with open(a.plik, encoding="utf-8", errors="replace") as f:
        tekst = f.read()
    urls = wyciagnij_linki(tekst)
    if a.limit:
        urls = urls[: a.limit]
    if not a.json:
        print(f"[viator] {a.plik}: {len(urls)} unikalnych adresów", file=sys.stderr)

    drogi = sprawdz_wsadowo(
        urls, watki=a.watki, cache_sciezka=a.cache, odswiez=a.odswiez,
        postep=True, timeout=a.timeout,
    )
    podsum = podsumuj(drogi)

    if a.json:
        print(json.dumps(
            {"plik": a.plik, "podsumowanie": podsum, "drogi": [asdict(d) for d in drogi]},
            ensure_ascii=False, indent=2,
        ))
    elif a.tylko_podsumowanie:
        print(json.dumps(podsum, ensure_ascii=False, indent=2))
    else:
        _drukuj_raport(drogi, podsum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
