"""
W-344 — OMS (Order Management System) — Zarządca Zleceń Imperium.

Jawna MASZYNA STANÓW cyklu życia zlecenia — luka zidentyfikowana w skanie
konkurencji (NautilusTrader ma to od lat, my mieliśmy fire-and-forget create_order
w RealOrderRouter). Daje wzorzec „parity backtest=live": ten sam cykl życia zlecenia
w trybie paper (symulowane wypełnienia) i realnym (CCXT na MEXC), bez ryzyka kapitału.

DLA NOWICJUSZA: zlecenie na giełdzie nie jest natychmiastowe. Składasz je (SUBMIT),
giełda potwierdza, potem wypełnia (FILL) — czasem w częściach (PARTIAL), czasem
odrzuca (REJECT). Połączenie może paść w połowie. Bez jawnego śledzenia stanu nie
wiesz, czy Twoja pozycja faktycznie istnieje na giełdzie — a to droga do rozjazdu
kapitału. OMS pilnuje każdego zlecenia od narodzin do śmierci.

MASZYNA STANÓW (dozwolone przejścia):

    NOWE ──zloz()──► ZLOZONE ──fill(część)──► CZESCIOWE ──fill(reszta)──► WYPELNIONE
      │                 │                          │
      │                 ├──fill(całość)───────────────────────────────► WYPELNIONE
      │                 ├──odrzuc()──► ODRZUCONE                          (stan końcowy)
      │                 └──anuluj()──► ANULOWANE
      └──anuluj()──► ANULOWANE

    Każda próba zloz() która padnie → retry z backoffem; po wyczerpaniu prób → BLAD.

Zasady:
  • Prawo I — OMS nie zgaduje: stan zlecenia wynika z faktów (potwierdzeń giełdy /
    symulowanych wypełnień), nie z nadziei. Nielegalne przejście = wyjątek, nie cisza.
  • Prawo XV — partial-fill akumulowany (nie gubimy częściowych wypełnień); retry
    odzyskuje przejściowe błędy sieci zamiast porzucać zlecenie.
  • Prawo XXI — granice testowane: 0 ilości, over-fill, nielegalne przejścia,
    wyczerpanie retry, dokładne wypełnienie do zera reszty.

Tryb paper (domyślny): submit_fn = None → zlecenie od razu „złożone", wypełnienia
wstrzykuje wołający (symulacja). Tryb realny: submit_fn = callable(Zlecenie)->dict
(np. RealOrderRouter._zloz_zlecenie) — OMS owija je w retry+maszynę stanów.
"""

import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("OMS")


class StanZlecenia(str, Enum):
    """Stany cyklu życia zlecenia. Końcowe: WYPELNIONE/ODRZUCONE/ANULOWANE/BLAD."""
    NOWE = "NOWE"               # utworzone, jeszcze niezłożone na giełdę
    ZLOZONE = "ZLOZONE"         # potwierdzone przez giełdę, czeka na wypełnienie
    CZESCIOWE = "CZESCIOWE"     # częściowo wypełnione
    WYPELNIONE = "WYPELNIONE"   # w pełni wypełnione (stan końcowy)
    ODRZUCONE = "ODRZUCONE"     # odrzucone przez giełdę (stan końcowy)
    ANULOWANE = "ANULOWANE"     # anulowane przez nas (stan końcowy)
    BLAD = "BLAD"               # błąd po wyczerpaniu retry (stan końcowy)


class Strona(str, Enum):
    KUP = "BUY"
    SPRZEDAJ = "SELL"


class TypZlecenia(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


# Stany końcowe — z nich nie ma już przejść
STANY_KONCOWE = frozenset({
    StanZlecenia.WYPELNIONE, StanZlecenia.ODRZUCONE,
    StanZlecenia.ANULOWANE, StanZlecenia.BLAD,
})

# Dozwolone przejścia maszyny stanów (Prawo I — nielegalne = wyjątek)
_PRZEJSCIA: Dict[StanZlecenia, frozenset] = {
    StanZlecenia.NOWE:      frozenset({StanZlecenia.ZLOZONE, StanZlecenia.ANULOWANE,
                                       StanZlecenia.BLAD}),
    StanZlecenia.ZLOZONE:   frozenset({StanZlecenia.CZESCIOWE, StanZlecenia.WYPELNIONE,
                                       StanZlecenia.ODRZUCONE, StanZlecenia.ANULOWANE}),
    StanZlecenia.CZESCIOWE: frozenset({StanZlecenia.CZESCIOWE, StanZlecenia.WYPELNIONE,
                                       StanZlecenia.ANULOWANE}),
}


class NielegalnePrzejscie(Exception):
    """Próba przejścia stanu zlecenia niezgodna z maszyną stanów (Prawo I)."""


@dataclass
class Zlecenie:
    """
    Jedno zlecenie i jego cykl życia. ilosc_wypelniona akumuluje partial-fille;
    cena_srednia to średnia ważona wolumenem ceny wszystkich wypełnień.
    """
    zlecenie_id: str
    symbol: str
    strona: Strona
    ilosc: float                       # docelowa ilość (bazowa)
    typ: TypZlecenia = TypZlecenia.MARKET
    cena: Optional[float] = None       # None dla MARKET; wymagana dla LIMIT
    stan: StanZlecenia = StanZlecenia.NOWE
    ilosc_wypelniona: float = 0.0
    cena_srednia: float = 0.0
    proby: int = 0                     # ile razy próbowano złożyć
    ostatni_blad: str = ""
    klient_meta: dict = field(default_factory=dict)  # dowolny kontekst wołającego
    historia_stanow: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def ilosc_pozostala(self) -> float:
        """Ile jeszcze do wypełnienia (nie schodzi poniżej zera)."""
        return max(0.0, round(self.ilosc - self.ilosc_wypelniona, 12))

    @property
    def zakonczone(self) -> bool:
        return self.stan in STANY_KONCOWE

    @property
    def aktywne(self) -> bool:
        return self.stan in (StanZlecenia.ZLOZONE, StanZlecenia.CZESCIOWE)

    def _przejdz(self, nowy: StanZlecenia) -> None:
        """Waliduje i wykonuje przejście stanu (Prawo I — nielegalne = wyjątek)."""
        dozwolone = _PRZEJSCIA.get(self.stan, frozenset())
        if nowy not in dozwolone:
            raise NielegalnePrzejscie(
                f"Zlecenie {self.zlecenie_id}: {self.stan.value} → {nowy.value} "
                f"niedozwolone (dozwolone: {[s.value for s in dozwolone]})"
            )
        self.historia_stanow.append(f"{self.stan.value}→{nowy.value}")
        self.stan = nowy


class ZarzadcaZlecen:
    """
    OMS — śledzi wszystkie zlecenia, egzekwuje maszynę stanów, retry, reconciliację.

    Użycie (paper):
        oms = ZarzadcaZlecen()
        z = oms.utworz(symbol="BTCUSDT", strona=Strona.KUP, ilosc=0.5)
        oms.zloz(z)                          # paper: od razu ZLOZONE
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.2, 50000)  # CZESCIOWE
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 0.3, 50100)  # WYPELNIONE

    Użycie (realny):
        oms = ZarzadcaZlecen(submit_fn=router._zloz_zlecenie, max_prob=3)
        oms.zloz(z)   # owija submit w retry+backoff; ZLOZONE gdy giełda potwierdzi
    """

    def __init__(self, submit_fn: Optional[Callable[[Zlecenie], dict]] = None,
                 max_prob: int = 3, backoff_bazowy_s: float = 0.0):
        """
        submit_fn: callable(Zlecenie) -> dict potwierdzenia giełdy. None = tryb paper
                   (zlecenie od razu ZLOZONE bez sieci). Wyjątek z submit_fn → retry.
        max_prob:  ile razy próbować złożyć przy błędach przejściowych (>=1).
        backoff_bazowy_s: baza backoffu wykładniczego (proba i → bazowy*2^i). 0 = bez
                   pauzy (testy). Produkcja: 1.0–2.0 s.
        """
        assert max_prob >= 1, "max_prob musi być >= 1"
        self.submit_fn = submit_fn
        self.max_prob = max_prob
        self.backoff_bazowy_s = backoff_bazowy_s
        self._zlecenia: Dict[str, Zlecenie] = {}
        self._licznik = 0

    # ── Tworzenie ────────────────────────────────────────────────────────────
    def utworz(self, symbol: str, strona: Strona, ilosc: float,
               typ: TypZlecenia = TypZlecenia.MARKET,
               cena: Optional[float] = None,
               zlecenie_id: Optional[str] = None,
               klient_meta: Optional[dict] = None) -> Zlecenie:
        """Tworzy zlecenie w stanie NOWE. Waliduje ilość i (dla LIMIT) cenę."""
        if ilosc <= 0:
            raise ValueError(f"Ilość zlecenia musi być > 0, podano {ilosc}")
        if typ == TypZlecenia.LIMIT and (cena is None or cena <= 0):
            raise ValueError("Zlecenie LIMIT wymaga dodatniej ceny")
        self._licznik += 1
        zid = zlecenie_id or f"ORD-{self._licznik:06d}"
        if zid in self._zlecenia:
            raise ValueError(f"Zlecenie o id {zid} już istnieje")
        z = Zlecenie(
            zlecenie_id=zid, symbol=symbol, strona=strona, ilosc=ilosc,
            typ=typ, cena=cena, klient_meta=klient_meta or {},
        )
        self._zlecenia[zid] = z
        return z

    # ── Składanie (z retry) ──────────────────────────────────────────────────
    def zloz(self, zlecenie: Zlecenie) -> bool:
        """
        Składa zlecenie na giełdę: NOWE → ZLOZONE. W trybie paper (submit_fn=None)
        od razu sukces. W realnym — woła submit_fn z retry+backoffem; po wyczerpaniu
        prób → stan BLAD i zwraca False (Prawo I — porażka jest jawna, nie cicha).
        """
        if zlecenie.stan != StanZlecenia.NOWE:
            raise NielegalnePrzejscie(
                f"zloz() wymaga stanu NOWE, jest {zlecenie.stan.value}")

        if self.submit_fn is None:
            zlecenie.proby += 1
            zlecenie._przejdz(StanZlecenia.ZLOZONE)
            return True

        for i in range(self.max_prob):
            zlecenie.proby += 1
            try:
                self.submit_fn(zlecenie)
                zlecenie._przejdz(StanZlecenia.ZLOZONE)
                return True
            except Exception as e:  # noqa: BLE001 — celowo łapiemy każdy błąd sieci/API
                zlecenie.ostatni_blad = str(e)
                logger.warning(
                    f"[OMS] zloz({zlecenie.zlecenie_id}) próba "
                    f"{zlecenie.proby}/{self.max_prob} padła: {e}")
                if i < self.max_prob - 1 and self.backoff_bazowy_s > 0:
                    time.sleep(self.backoff_bazowy_s * (2 ** i))

        zlecenie._przejdz(StanZlecenia.BLAD)
        return False

    # ── Wypełnienia (partial-fill akumulowany) ───────────────────────────────
    def zarejestruj_wypelnienie(self, zlecenie_id: str, ilosc: float,
                                cena: float) -> Zlecenie:
        """
        Rejestruje (częściowe) wypełnienie. Akumuluje ilość i przelicza cenę średnią
        ważoną wolumenem. ZLOZONE→CZESCIOWE→WYPELNIONE gdy reszta spadnie do zera.

        Prawo XXI (granica): over-fill (więcej niż zamówiono) → wyjątek, nie cichy
        nadmiar. Dokładne domknięcie reszty → WYPELNIONE (nie CZESCIOWE).
        """
        z = self._wymagaj(zlecenie_id)
        if z.stan not in (StanZlecenia.ZLOZONE, StanZlecenia.CZESCIOWE):
            raise NielegalnePrzejscie(
                f"Wypełnienie wymaga ZLOZONE/CZESCIOWE, jest {z.stan.value}")
        if ilosc <= 0:
            raise ValueError(f"Ilość wypełnienia musi być > 0, podano {ilosc}")
        nowa_suma = round(z.ilosc_wypelniona + ilosc, 12)
        if nowa_suma > z.ilosc + 1e-9:
            raise ValueError(
                f"Over-fill: {nowa_suma} > zamówione {z.ilosc} "
                f"(zlecenie {zlecenie_id})")

        # Cena średnia ważona wolumenem
        if z.ilosc_wypelniona <= 0:
            z.cena_srednia = cena
        else:
            z.cena_srednia = round(
                (z.cena_srednia * z.ilosc_wypelniona + cena * ilosc) / nowa_suma, 12)
        z.ilosc_wypelniona = nowa_suma

        if z.ilosc_pozostala <= 1e-9:
            z._przejdz(StanZlecenia.WYPELNIONE)
        else:
            # ZLOZONE→CZESCIOWE (pierwszy partial); CZESCIOWE→CZESCIOWE (kolejny)
            z._przejdz(StanZlecenia.CZESCIOWE)
        return z

    # ── Odrzucenie / anulowanie ──────────────────────────────────────────────
    def odrzuc(self, zlecenie_id: str, powod: str = "") -> Zlecenie:
        """Giełda odrzuciła zlecenie: ZLOZONE → ODRZUCONE."""
        z = self._wymagaj(zlecenie_id)
        z.ostatni_blad = powod or "odrzucone przez giełdę"
        z._przejdz(StanZlecenia.ODRZUCONE)
        return z

    def anuluj(self, zlecenie_id: str, powod: str = "") -> Zlecenie:
        """Anulujemy zlecenie. Dozwolone z NOWE/ZLOZONE/CZESCIOWE (nie z końcowych)."""
        z = self._wymagaj(zlecenie_id)
        z.ostatni_blad = powod or "anulowane"
        z._przejdz(StanZlecenia.ANULOWANE)
        return z

    # ── Reconciliacja ────────────────────────────────────────────────────────
    def reconcile(self, stan_gieldy: Dict[str, dict]) -> List[str]:
        """
        Uzgadnia stan OMS z prawdą giełdy (Prawo I — giełda jest źródłem prawdy).

        stan_gieldy: {zlecenie_id: {"ilosc_wypelniona": float, "cena_srednia": float,
                      "stan": "FILLED"/"CANCELED"/"REJECTED"/...}}.
        Zwraca listę zlecenie_id, których stan SKORYGOWANO (rozjazd OMS↔giełda).

        Bezpieczne: nie cofa stanów końcowych ani nie zmniejsza wypełnienia —
        tylko domyka rozjazdy w stronę prawdy giełdy (więcej wypełnione / zakończone).
        """
        skorygowane: List[str] = []
        for zid, prawda in stan_gieldy.items():
            z = self._zlecenia.get(zid)
            if z is None or z.zakonczone:
                continue
            zmieniono = False

            wyp = prawda.get("ilosc_wypelniona")
            if wyp is not None and wyp > z.ilosc_wypelniona + 1e-9:
                ilosc_doplyw = round(wyp - z.ilosc_wypelniona, 12)
                cena = prawda.get("cena_srednia", z.cena_srednia or 0.0)
                try:
                    self.zarejestruj_wypelnienie(zid, ilosc_doplyw, cena)
                    zmieniono = True
                except (ValueError, NielegalnePrzejscie) as e:
                    logger.warning(f"[OMS] reconcile {zid} wypełnienie pominięte: {e}")

            stan_g = (prawda.get("stan") or "").upper()
            if stan_g in ("CANCELED", "CANCELLED") and not z.zakonczone:
                z._przejdz(StanZlecenia.ANULOWANE)
                zmieniono = True
            elif stan_g == "REJECTED" and z.stan == StanZlecenia.ZLOZONE:
                z._przejdz(StanZlecenia.ODRZUCONE)
                zmieniono = True

            if zmieniono:
                skorygowane.append(zid)
        return skorygowane

    # ── Zapytania ────────────────────────────────────────────────────────────
    def zlecenie(self, zlecenie_id: str) -> Optional[Zlecenie]:
        return self._zlecenia.get(zlecenie_id)

    def aktywne(self) -> List[Zlecenie]:
        """Zlecenia w locie (ZLOZONE/CZESCIOWE) — kandydaci do reconciliacji."""
        return [z for z in self._zlecenia.values() if z.aktywne]

    def wszystkie(self) -> List[Zlecenie]:
        return list(self._zlecenia.values())

    def raport(self) -> dict:
        """Diagnostyka: rozkład stanów + liczba aktywnych/zakończonych."""
        rozklad: Dict[str, int] = {}
        for z in self._zlecenia.values():
            rozklad[z.stan.value] = rozklad.get(z.stan.value, 0) + 1
        return {
            "lacznie": len(self._zlecenia),
            "aktywne": len(self.aktywne()),
            "rozklad_stanow": rozklad,
        }

    # ── Wewnętrzne ───────────────────────────────────────────────────────────
    def _wymagaj(self, zlecenie_id: str) -> Zlecenie:
        z = self._zlecenia.get(zlecenie_id)
        if z is None:
            raise KeyError(f"Nieznane zlecenie: {zlecenie_id}")
        return z
