"""
Igrzyska — silnik rywalizacji neuronów (W-002).

Czyta logi z Pamięci Absolutnej, ocenia każdy neuron, przydziela rangi
(Tiro → Aquilifer), oblicza mnożniki wag, prowadzi Listę Infamii i
przyznaje Złoty Hełm. Spec: docs/IGRZYSKA_IMPERIUM.md.

Zasada: neuron oceniany za WKŁAD w trafność — czy jego kierunek zgadzał
się z kierunkiem, który okazał się zyskowny.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json

logger = logging.getLogger("Igrzyska")


# ─── Rangi i mnożniki (z IGRZYSKA_IMPERIUM.md) ────────────────────────────────

RANGI = [
    # (nazwa, prog_dolny, mnoznik_wagi)
    ("Aquilifer",   0.93, 2.0),   # 🌟 ZŁOTY HEŁM
    ("PrimusPilus", 0.85, 1.6),   # 🏆
    ("Centurion",   0.73, 1.3),   # 🥇
    ("Optio",       0.60, 1.0),   # 🥈
    ("Miles",       0.45, 0.8),   # 🥉
    ("Tiro",        0.00, 0.5),   # 🏅 nowicjusz
]

PROG_INFAMII = 0.40    # poniżej = kandydat do Listy Infamii
PROG_OSTRZEZENIA = 0.45


def okresl_range(wynik: float) -> tuple:
    """Zwraca (nazwa_rangi, mnoznik_wagi) dla danego wyniku."""
    for nazwa, prog, mnoznik in RANGI:
        if wynik >= prog:
            return nazwa, mnoznik
    return "Tiro", 0.5


# ─── Statystyka pojedynczego neuronu ──────────────────────────────────────────

@dataclass
class StatystykaNeuronu:
    klucz: str
    # Macierz trafności względem kierunku zyskownego
    tp: int = 0          # przewidział kierunek zyskowny
    fp: int = 0          # przewidział kierunek, który NIE był zyskowny
    long_trafne: int = 0
    long_total: int = 0
    short_trafne: int = 0
    short_total: int = 0
    # Stabilność (flip-flop)
    ostatni_kierunek: str = ""
    flipy: int = 0
    sygnaly: int = 0
    # Opcjonalne (gdy mamy bogatsze logi)
    contribution_sum: float = 0.0
    timeliness_sum: float = 0.0
    contribution_n: int = 0

    def zarejestruj(self, kierunek: str, zyskowny_kierunek: str,
                    contribution: Optional[float] = None,
                    timeliness: Optional[float] = None):
        """Jeden sygnał neuronu + faktyczny zyskowny kierunek trade'u."""
        self.sygnaly += 1

        # Flip-flop
        if self.ostatni_kierunek and kierunek != self.ostatni_kierunek:
            self.flipy += 1
        self.ostatni_kierunek = kierunek

        # Trafność
        trafny = (kierunek == zyskowny_kierunek)
        if trafny:
            self.tp += 1
        else:
            self.fp += 1

        if kierunek == "LONG":
            self.long_total += 1
            if trafny:
                self.long_trafne += 1
        elif kierunek == "SHORT":
            self.short_total += 1
            if trafny:
                self.short_trafne += 1

        if contribution is not None:
            self.contribution_sum += contribution
            self.contribution_n += 1
        if timeliness is not None:
            self.timeliness_sum += timeliness

    # ── Metryki ──

    @property
    def accuracy(self) -> float:
        total = self.tp + self.fp
        return self.tp / total if total > 0 else 0.0

    @property
    def precision_dominujaca(self) -> float:
        """Precyzja w dominującym kierunku neuronu."""
        if self.long_total >= self.short_total and self.long_total > 0:
            return self.long_trafne / self.long_total
        elif self.short_total > 0:
            return self.short_trafne / self.short_total
        return 0.0

    @property
    def stability(self) -> float:
        if self.sygnaly <= 1:
            return 1.0
        return 1.0 - (self.flipy / self.sygnaly)

    @property
    def contribution(self) -> float:
        if self.contribution_n > 0:
            return self.contribution_sum / self.contribution_n
        return 0.5  # neutralne dopóki nie mamy danych o wkładzie

    @property
    def timeliness(self) -> float:
        if self.sygnaly > 0 and self.timeliness_sum > 0:
            return self.timeliness_sum / self.sygnaly
        return 0.5  # neutralne dopóki nie mierzymy wyprzedzenia

    @property
    def wynik(self) -> float:
        """WYNIK_NEURONU wg wzoru z IGRZYSKA_IMPERIUM.md."""
        return round(
            0.30 * self.accuracy +
            0.25 * self.precision_dominujaca +
            0.20 * self.contribution +
            0.15 * self.timeliness +
            0.10 * self.stability,
            4
        )


# ─── Wpis na Listę Infamii ────────────────────────────────────────────────────

@dataclass
class WpisInfamii:
    klucz: str
    wynik: float
    powod: str
    sygnaly: int


# ─── Główny silnik ────────────────────────────────────────────────────────────

@dataclass
class Igrzyska:
    """
    Użycie:
        ig = Igrzyska()
        ig.przetworz_logi(logi)         # z Pamięci Absolutnej
        ranking = ig.ranking()          # posortowana tabela liderów
        helm = ig.zloty_helm()          # neuron miesiąca
        wagi = ig.nowe_wagi()           # {klucz: mnoznik} do Legatusa
    """
    statystyki: Dict[str, StatystykaNeuronu] = field(default_factory=dict)
    # Obserwatorzy strumienia wyników (np. HedgeMWU — wizja W-049). Każdy musi mieć
    # metodę zarejestruj_wynik(klucz, kierunek, zyskowny_kierunek, contribution, timeliness).
    # Dzięki temu MWU uczy się z DOKŁADNIE tego samego strumienia, bez duplikacji
    # logiki parowania logów (DRY, Prawo XVI).
    obserwatorzy: list = field(default_factory=list)

    def _stat(self, klucz: str) -> StatystykaNeuronu:
        if klucz not in self.statystyki:
            self.statystyki[klucz] = StatystykaNeuronu(klucz=klucz)
        return self.statystyki[klucz]

    def zarejestruj_wynik(self, klucz: str, kierunek: str,
                          zyskowny_kierunek: str,
                          contribution: Optional[float] = None,
                          timeliness: Optional[float] = None):
        self._stat(klucz).zarejestruj(kierunek, zyskowny_kierunek,
                                       contribution, timeliness)
        for obs in self.obserwatorzy:
            try:
                obs.zarejestruj_wynik(klucz, kierunek, zyskowny_kierunek,
                                      contribution, timeliness)
            except Exception as e:
                logger.error(f"[Igrzyska] Obserwator {obs} padł: {e}")

    def przetworz_logi(self, logi: list):
        """
        Przetwarza listę ImperiumLog. Łączy SYGNAŁ z TRADE_CLOSE po sesja_id.
        Dla każdego trade'u: zyskowny_kierunek = kierunek wejścia jeśli pnl>0,
        w przeciwnym razie kierunek przeciwny.
        """
        # Indeksuj sygnały i zamknięcia po sesji
        sygnaly_po_sesji = {}
        zamkniecia_po_sesji = {}
        for log in logi:
            typ = getattr(log, "log_typ", "")
            sid = getattr(log, "sesja_id", "")
            if typ == "SYGNAŁ":
                sygnaly_po_sesji.setdefault(sid, []).append(log)
            elif typ == "TRADE_CLOSE":
                zamkniecia_po_sesji.setdefault(sid, []).append(log)

        for sid, zamkniecia in zamkniecia_po_sesji.items():
            sygnaly = sygnaly_po_sesji.get(sid, [])
            if not sygnaly:
                continue
            for tc in zamkniecia:
                pnl = getattr(tc, "pnl_pct", 0.0)
                # kierunek wejścia bierzemy z sygnału
                for sig in sygnaly:
                    kier_wejscia = getattr(sig, "legatus_kierunek", "")
                    if kier_wejscia not in ("LONG", "SHORT"):
                        continue
                    zyskowny = kier_wejscia if pnl > 0 else _przeciwny(kier_wejscia)
                    self._przetworz_sygnaly_json(sig, zyskowny)

    def _przetworz_sygnaly_json(self, sig, zyskowny_kierunek: str):
        raw = getattr(sig, "sygnaly_json", "")
        if not raw:
            return
        try:
            lista = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return
        for s in lista:
            klucz = s.get("k") or s.get("klucz")
            kier = s.get("d") or s.get("kierunek")
            if klucz and kier in ("LONG", "SHORT"):
                self.zarejestruj_wynik(klucz, kier, zyskowny_kierunek)

    # ── Wyniki ──

    def ranking(self) -> List[dict]:
        wyniki = []
        for klucz, stat in self.statystyki.items():
            nazwa_rangi, mnoznik = okresl_range(stat.wynik)
            wyniki.append({
                "klucz": klucz,
                "wynik": stat.wynik,
                "ranga": nazwa_rangi,
                "mnoznik": mnoznik,
                "accuracy": round(stat.accuracy, 3),
                "stability": round(stat.stability, 3),
                "sygnaly": stat.sygnaly,
            })
        wyniki.sort(key=lambda x: x["wynik"], reverse=True)
        return wyniki

    def zloty_helm(self) -> Optional[dict]:
        r = self.ranking()
        return r[0] if r else None

    def lista_infamii(self) -> List[WpisInfamii]:
        wpisy = []
        for klucz, stat in self.statystyki.items():
            if stat.wynik < PROG_INFAMII and stat.sygnaly >= 5:
                powod = self._diagnoza(stat)
                wpisy.append(WpisInfamii(klucz, stat.wynik, powod, stat.sygnaly))
        wpisy.sort(key=lambda w: w.wynik)
        return wpisy

    def _diagnoza(self, stat: StatystykaNeuronu) -> str:
        if stat.stability < 0.5:
            return f"flip-flop — {stat.flipy} zmian kierunku w {stat.sygnaly} sygnałach"
        if stat.accuracy < 0.4:
            return f"niska trafność {stat.accuracy:.0%}"
        return f"słaby wynik ogólny {stat.wynik:.2f}"

    def nowe_wagi(self) -> Dict[str, float]:
        """Mnożniki wag do przekazania Legatusowi."""
        return {k: okresl_range(s.wynik)[1] for k, s in self.statystyki.items()}

    def drukuj_kapitol(self, top_n: int = 5):
        r = self.ranking()
        helm = self.zloty_helm()
        infamia = self.lista_infamii()
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║              🏛️  KAPITOL IMPERIUM — LIDERZY                  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        if helm:
            print(f"║  🪖 ZŁOTY HEŁM: {helm['klucz']:<10} wynik={helm['wynik']:.2f} "
                  f"({helm['ranga']})")
        print("║  ── TOP NEURONY ──")
        for i, n in enumerate(r[:top_n], 1):
            print(f"║   {i}. {n['klucz']:<10} {n['wynik']:.2f}  {n['ranga']:<12} "
                  f"×{n['mnoznik']}")
        if infamia:
            print("║  ── ⚫ LISTA INFAMII ──")
            for w in infamia:
                print(f"║   {w.klucz:<10} {w.wynik:.2f} — {w.powod}")
        print("╚══════════════════════════════════════════════════════════════╝")


def _przeciwny(kierunek: str) -> str:
    return "SHORT" if kierunek == "LONG" else "LONG"


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    ig = Igrzyska()

    # Symulacja: 3 neurony, 10 trade'ów
    # X-01 dobry (trafia 8/10), X-02 średni (5/10), X-07 flip-flop słaby
    import random
    random.seed(42)

    for i in range(20):
        # rzeczywisty zyskowny kierunek tej rundy
        zysk = random.choice(["LONG", "SHORT"])

        # X-01 trafia w 80%
        x01 = zysk if random.random() < 0.8 else _przeciwny(zysk)
        ig.zarejestruj_wynik("X-01", x01, zysk)

        # X-02 trafia w 50%
        x02 = zysk if random.random() < 0.5 else _przeciwny(zysk)
        ig.zarejestruj_wynik("X-02", x02, zysk)

        # X-07 losowy + flip-flop (35%)
        x07 = zysk if random.random() < 0.35 else _przeciwny(zysk)
        ig.zarejestruj_wynik("X-07", x07, zysk)

    ig.drukuj_kapitol()

    print("\nNowe wagi (mnożniki dla Legatusa):")
    for klucz, mnoznik in ig.nowe_wagi().items():
        print(f"  {klucz}: ×{mnoznik}")

    helm = ig.zloty_helm()
    assert helm["klucz"] == "X-01", "Najlepszy neuron powinien dostać Złoty Hełm"
    print(f"\n✅ Igrzyska działają — Złoty Hełm: {helm['klucz']} ({helm['wynik']:.2f})")
