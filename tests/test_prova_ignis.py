"""
🔥 PROVA IGNIS — próba ognia egzekucji (L1 planu domykania luk, 2026-07-05).

Nie testy jednostkowe (te są w test_oms.py — pojedyncze przejścia stanów), lecz
KAMPANIE CHAOSU: wielokrokowe scenariusze awarii odgrywane od początku do końca,
jak w prawdziwym boju — zrywane łącze w połowie zlecenia, restart procesu z odzyskiem
przez reconcile, zdublowane potwierdzenia, wyścig anulacji z wypełnieniem, burza
wielu zleceń na kapryśnej giełdzie. Deterministyczne (sekwencje awarii zadane jawnie,
zero random) — Prawo I: każda porażka odtwarzalna.

Filozofia: NautilusTrader ma to zbite latami produkcji — my zbijamy to próbą ognia
PRZED pierwszym realnym zleceniem, nie po pierwszej stracie.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.drogi.oms import (
    NielegalnePrzejscie,
    StanZlecenia,
    Strona,
    ZarzadcaZlecen,
)


class KapryśnaGielda:
    """Symulator wrogiej giełdy: skrypt awarii per wywołanie (deterministyczny).

    scenariusz_submit: lista wyników kolejnych submit(): "ok" | "timeout" |
        "ok_ale_wyjatek" (zlecenie WCHODZI na giełdę, ale odpowiedź ginie — klasyk).
    """

    def __init__(self, scenariusz_submit):
        self.scenariusz = list(scenariusz_submit)
        self.przyjete: dict = {}     # klucz_idempotencji -> zlecenie (prawda giełdy)
        self.wywolania_submit = 0

    def submit(self, zlecenie):
        krok = (self.scenariusz[self.wywolania_submit]
                if self.wywolania_submit < len(self.scenariusz) else "ok")
        self.wywolania_submit += 1
        if krok == "timeout":
            raise TimeoutError("sieć padła przed dotarciem do giełdy")
        if krok == "ok_ale_wyjatek":
            self.przyjete[zlecenie.klucz_idempotencji] = zlecenie   # weszło!
            raise ConnectionError("odpowiedź giełdy zginęła w drodze powrotnej")
        self.przyjete[zlecenie.klucz_idempotencji] = zlecenie
        return {"id": f"EX-{len(self.przyjete)}"}

    def query(self, zlecenie):
        """Czy giełda zna to zlecenie? (anti-double-submit)"""
        z = self.przyjete.get(zlecenie.klucz_idempotencji)
        return {"id": "EX-known"} if z is not None else None


def _oms(gielda, max_prob=3):
    return ZarzadcaZlecen(submit_fn=gielda.submit, query_fn=gielda.query,
                          max_prob=max_prob, backoff_bazowy_s=0.0)


# ── Kampania 1: odpowiedź ginie w drodze — NIE wolno zdublować zlecenia ──────

def test_kampania_zgubiona_odpowiedz_bez_duplikatu():
    gielda = KapryśnaGielda(["ok_ale_wyjatek"])   # weszło, ale my o tym nie wiemy
    oms = _oms(gielda)
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is True                    # retry→query wykrywa: już jest
    assert z.stan == StanZlecenia.ZLOZONE
    assert len(gielda.przyjete) == 1              # KRYTYCZNE: jedno, nie dwa


# ── Kampania 2: seria timeoutów → jawny BLAD, potem świadome ponowienie ──────

def test_kampania_total_blackout_konczy_jawnym_bledem():
    gielda = KapryśnaGielda(["timeout", "timeout", "timeout"])
    oms = _oms(gielda, max_prob=3)
    z = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    assert oms.zloz(z) is False
    assert z.stan == StanZlecenia.BLAD            # porażka jawna, nie cicha (Prawo I)
    assert len(gielda.przyjete) == 0              # nic nie weszło na giełdę
    # świadome ponowienie = NOWE zlecenie (stare jest końcowe — nie wskrzeszamy)
    z2 = oms.utworz("BTCUSDT", Strona.KUP, 1.0)
    gielda.scenariusz = ["ok"]; gielda.wywolania_submit = 0
    assert oms.zloz(z2) is True and len(gielda.przyjete) == 1


# ── Kampania 3: crash w połowie partiala → restart → reconcile domyka prawdę ─

def test_kampania_restart_w_polowie_partiala():
    gielda = KapryśnaGielda(["ok"])
    oms = _oms(gielda)
    z = oms.utworz("ETHUSDT", Strona.KUP, 10.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 4.0, 100.0)   # partial przed crashem
    assert z.stan == StanZlecenia.CZESCIOWE
    # ...crash procesu; po restarcie giełda mówi: dopełnione do 10 po lepszej średniej
    skoryg = oms.reconcile({z.zlecenie_id: {
        "ilosc_wypelniona": 10.0, "cena_srednia": 99.0, "stan": "FILLED"}})
    assert z.zlecenie_id in skoryg
    assert z.stan == StanZlecenia.WYPELNIONE
    assert z.ilosc_wypelniona == 10.0


# ── Kampania 4: zdublowany webhook wypełnienia → over-fill zablokowany ───────

def test_kampania_zdublowane_potwierdzenie_fill():
    oms = ZarzadcaZlecen()                        # paper
    z = oms.utworz("BTCUSDT", Strona.SPRZEDAJ, 2.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 2.0, 50_000.0)
    assert z.stan == StanZlecenia.WYPELNIONE
    with pytest.raises((NielegalnePrzejscie, ValueError)):
        oms.zarejestruj_wypelnienie(z.zlecenie_id, 2.0, 50_000.0)   # duplikat webhooka
    assert z.ilosc_wypelniona == 2.0              # księga nietknięta


# ── Kampania 5: wyścig anulacji z wypełnieniem — prawda giełdy wygrywa ───────

def test_kampania_wyscig_anulacji_z_wypelnieniem():
    oms = ZarzadcaZlecen()
    z = oms.utworz("SOLUSDT", Strona.KUP, 5.0)
    oms.zloz(z)
    oms.anuluj(z.zlecenie_id, "Cezar zmienił zdanie")
    assert z.stan == StanZlecenia.ANULOWANE
    # ...ale giełda wypełniła ZANIM anulacja doszła. Reconcile NIE cofa stanu
    # końcowego (bezpiecznik) — rozjazd zostaje JAWNY do decyzji wyżej, nie znika.
    skoryg = oms.reconcile({z.zlecenie_id: {
        "ilosc_wypelniona": 5.0, "cena_srednia": 150.0, "stan": "FILLED"}})
    assert skoryg == []                            # nie udaje, że umie to naprawić
    assert z.stan == StanZlecenia.ANULOWANE       # stan końcowy nienaruszony


# ── Kampania 6: burza — 10 zleceń, kapryśna sieć, księga musi się zgadzać ────

def test_kampania_burza_dziesieciu_zlecen():
    # co trzecie submit: odpowiedź ginie; reszta ok — deterministyczna burza
    scenariusz = []
    for i in range(30):
        scenariusz.append("ok_ale_wyjatek" if i % 3 == 0 else "ok")
    gielda = KapryśnaGielda(scenariusz)
    oms = _oms(gielda)
    zlecenia = []
    for i in range(10):
        z = oms.utworz("BTCUSDT", Strona.KUP if i % 2 == 0 else Strona.SPRZEDAJ,
                       1.0 + i)
        assert oms.zloz(z) is True
        zlecenia.append(z)
    # KRYTYCZNE: mimo burzy — dokładnie 10 zleceń na giełdzie, zero duplikatów
    assert len(gielda.przyjete) == 10
    # wypełnij wszystkie i sprawdź księgę końcową
    for z in zlecenia:
        oms.zarejestruj_wypelnienie(z.zlecenie_id, z.ilosc, 100.0)
    raport = oms.raport()
    assert raport["rozklad_stanow"][StanZlecenia.WYPELNIONE.value] == 10
    assert oms.aktywne() == []                    # nic nie wisi


# ── Kampania 7: reconcile z kłamiącą giełdą (mniej niż OMS wie) — ignoruj ────

def test_kampania_gielda_raportuje_mniej_niz_wiemy():
    oms = ZarzadcaZlecen()
    z = oms.utworz("BTCUSDT", Strona.KUP, 3.0)
    oms.zloz(z)
    oms.zarejestruj_wypelnienie(z.zlecenie_id, 2.0, 100.0)
    # opóźniony snapshot giełdy twierdzi: tylko 1.0 wypełnione — NIE zmniejszamy
    skoryg = oms.reconcile({z.zlecenie_id: {"ilosc_wypelniona": 1.0}})
    assert skoryg == []
    assert z.ilosc_wypelniona == 2.0              # nie cofamy wypełnień (bezpiecznik)
