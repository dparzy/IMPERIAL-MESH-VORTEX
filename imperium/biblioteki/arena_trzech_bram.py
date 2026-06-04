"""
🏛️ IMV | Arena Trzech Bram — potrójna bariera (W-035)

WIZJA (Cezar):
  Sprawiedliwy scoring Igrzysk: zamiast pytać "czy cena wzrosła?",
  stawiamy 3 bariery i sprawdzamy KTÓRA padła pierwsza.

Potrójna Bariera (Triple Barrier Method, López de Prado):
  ┌─────────────────────────────────────────────────────┐
  │  BRAMA I  — Take-Profit  (+tp_pct od ceny wejścia)  │ ← contribution +1.0
  │  BRAMA II — Stop-Loss    (-sl_pct od ceny wejścia)  │ ← contribution -1.0
  │  BRAMA III— Czas         (max_bary barów)            │ ← contribution  0.0
  └─────────────────────────────────────────────────────┘

Dlaczego lepiej niż pnl > 0:
  - Premia za SZYBKOŚĆ (timeliness): sygnał TP na 3. barze > TP na 20. barze
  - Neutralna bariera czasowa: nie każe za "nic się nie stało"
  - Uczciwe RR: TP=2×SL → sygnał musi być dobry, żeby wygrać na dłuższą metę

Użycie w Igrzyskach:
  wynik = oznacz_bariera(kierunek, cena_wejscia, bary_przyszle)
  igrzyska.zarejestruj_wynik(klucz, kierunek, zyskowny_kierunek,
                              contribution=wynik.contribution,
                              timeliness=wynik.timeliness)

Źródło: López de Prado (2018), "Advances in Financial Machine Learning",
         Chapter 3 — Triple-Barrier Method. Wiley.
         https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086
Weryfikacja: ✅ peer-reviewed (monografia akademicka, standard quant ML)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class WynikBariery:
    """
    Wynik potrójnej bariery dla jednego sygnału.

    contribution:
      +1.0  = Brama I  (Take-Profit) — neuron przewidział trafnie i szybko
      -1.0  = Brama II (Stop-Loss)   — neuron się mylił, kosztuje kapitał
       0.0  = Brama III(Czas)        — neutralne, rynek stał w miejscu

    timeliness ∈ [0,1]:
      1.0 = bariera trafiła na 1. barze (błyskawicznie)
      0.0 = bariera trafiła dokładnie na ostatnim barze (na granicy)
      TP szybki jest cenniejszy niż TP powolny (motywuje do sygnałów pewnych)
    """
    bariera: str             # "TP" / "SL" / "CZAS"
    bary_do_wyniku: int      # ile barów zajęło (1 = następny bar)
    max_bary: int
    contribution: float      # +1.0 / -1.0 / 0.0
    timeliness: float        # 1.0 = błyskawicznie, 0.0 = ostatni bar
    cena_wejscia: float
    cena_wyjscia: Optional[float]  # None gdy bariera czasowa

    @property
    def opis(self) -> str:
        t = f"{self.timeliness:.2f}"
        if self.bariera == "TP":
            return f"✅ TP po {self.bary_do_wyniku} barach (timeliness {t})"
        if self.bariera == "SL":
            return f"❌ SL po {self.bary_do_wyniku} barach (timeliness {t})"
        return f"⏱️ CZAS ({self.max_bary} barów) — pozycja neutralna"


def oznacz_bariera(
    kierunek: str,
    cena_wejscia: float,
    bary_przyszle: List[Dict[str, Any]],
    tp_pct: float = 0.02,
    sl_pct: float = 0.01,
    max_bary: int = 20,
) -> WynikBariery:
    """
    Etykietuje jeden sygnał metodą potrójnej bariery.

    Parametry:
      kierunek       LONG lub SHORT
      cena_wejscia   cena zamknięcia baru z sygnałem
      bary_przyszle  lista barów NASTĘPNYCH po sygnale (każdy: dict z high/low/close)
      tp_pct         frakcja TP od ceny wejścia (domyślnie 2% = +0.02)
      sl_pct         frakcja SL od ceny wejścia (domyślnie 1% = +0.01)
      max_bary       maksymalna liczba barów przed barierą czasową

    Domyślnie: RR 1:2 (sl=1%, tp=2%).
    Bariery sprawdzane na intrabar high/low dla uczciwości.

    Zwraca WynikBariery.
    """
    if not bary_przyszle or cena_wejscia <= 0:
        return WynikBariery(
            bariera="CZAS", bary_do_wyniku=0, max_bary=max_bary,
            contribution=0.0, timeliness=0.0,
            cena_wejscia=cena_wejscia, cena_wyjscia=None,
        )

    long = kierunek.upper() == "LONG"
    tp_cena = cena_wejscia * (1.0 + tp_pct) if long else cena_wejscia * (1.0 - tp_pct)
    sl_cena = cena_wejscia * (1.0 - sl_pct) if long else cena_wejscia * (1.0 + sl_pct)

    limit = min(max_bary, len(bary_przyszle))
    for i, bar in enumerate(bary_przyszle[:limit]):
        high = bar.get("high", bar.get("close", 0.0))
        low = bar.get("low", bar.get("close", 0.0))
        bar_nr = i + 1  # 1-indeksowany

        # Sprawdź TP
        tp_hit = (high >= tp_cena) if long else (low <= tp_cena)
        # Sprawdź SL
        sl_hit = (low <= sl_cena) if long else (high >= sl_cena)

        if tp_hit and sl_hit:
            # Oba w tym samym barze → konwencja: SL wygrywa (ostrożność)
            timeliness = 1.0 - (bar_nr - 1) / max(max_bary - 1, 1)
            return WynikBariery(
                bariera="SL", bary_do_wyniku=bar_nr, max_bary=max_bary,
                contribution=-1.0, timeliness=round(timeliness, 4),
                cena_wejscia=cena_wejscia, cena_wyjscia=sl_cena,
            )
        if tp_hit:
            timeliness = 1.0 - (bar_nr - 1) / max(max_bary - 1, 1)
            return WynikBariery(
                bariera="TP", bary_do_wyniku=bar_nr, max_bary=max_bary,
                contribution=1.0, timeliness=round(timeliness, 4),
                cena_wejscia=cena_wejscia, cena_wyjscia=tp_cena,
            )
        if sl_hit:
            timeliness = 1.0 - (bar_nr - 1) / max(max_bary - 1, 1)
            return WynikBariery(
                bariera="SL", bary_do_wyniku=bar_nr, max_bary=max_bary,
                contribution=-1.0, timeliness=round(timeliness, 4),
                cena_wejscia=cena_wejscia, cena_wyjscia=sl_cena,
            )

    # Bariera czasowa — żadna z bramek nie padła
    return WynikBariery(
        bariera="CZAS", bary_do_wyniku=limit, max_bary=max_bary,
        contribution=0.0, timeliness=0.0,
        cena_wejscia=cena_wejscia, cena_wyjscia=None,
    )


@dataclass
class RaportAreny:
    """Zbiorczy raport z przebiegu Areny (backtest z potrójną barierą)."""
    sygnaly_tp: int = 0
    sygnaly_sl: int = 0
    sygnaly_czas: int = 0
    srednia_timeliness_tp: float = 0.0
    srednia_timeliness_sl: float = 0.0
    # {klucz_neuronu: {"contribution": float, "timeliness_sum": float, "n": int}}
    kontryb_neuronow: Dict[str, Dict] = None

    def __post_init__(self):
        if self.kontryb_neuronow is None:
            self.kontryb_neuronow = {}

    def zarejestruj(self, wynik: "WynikBariery",
                    sygnaly_json: Optional[List[Dict]] = None):
        """Rejestruje wynik bariery + opcjonalnie contributes neuronów."""
        if wynik.bariera == "TP":
            self.sygnaly_tp += 1
        elif wynik.bariera == "SL":
            self.sygnaly_sl += 1
        else:
            self.sygnaly_czas += 1

        if sygnaly_json:
            for s in sygnaly_json:
                klucz = s.get("k") or s.get("klucz")
                kier = s.get("d") or s.get("kierunek")
                if not klucz or kier not in ("LONG", "SHORT"):
                    continue
                if klucz not in self.kontryb_neuronow:
                    self.kontryb_neuronow[klucz] = {
                        "contribution": 0.0, "timeliness_sum": 0.0, "n": 0
                    }
                self.kontryb_neuronow[klucz]["contribution"] += wynik.contribution
                self.kontryb_neuronow[klucz]["timeliness_sum"] += wynik.timeliness
                self.kontryb_neuronow[klucz]["n"] += 1

    @property
    def lacznie(self) -> int:
        return self.sygnaly_tp + self.sygnaly_sl + self.sygnaly_czas

    @property
    def win_rate_tp(self) -> float:
        if self.lacznie == 0:
            return 0.0
        return self.sygnaly_tp / self.lacznie

    def drukuj(self):
        print(f"\n{'═'*62}")
        print(f"  🏛️ ARENA TRZECH BRAM — raport")
        print(f"{'═'*62}")
        print(f"  Sygnały łącznie: {self.lacznie}")
        print(f"  ✅ TP (Brama I) : {self.sygnaly_tp:>4}  ({self.win_rate_tp:.1%})")
        print(f"  ❌ SL (Brama II): {self.sygnaly_sl:>4}")
        print(f"  ⏱️ CZAS(Brama III):{self.sygnaly_czas:>3}")
        if self.kontryb_neuronow:
            print(f"\n  Top neuro-kontrybutorzy:")
            ranking = sorted(
                self.kontryb_neuronow.items(),
                key=lambda x: x[1]["contribution"],
                reverse=True,
            )
            for klucz, dane in ranking[:5]:
                avg_c = dane["contribution"] / dane["n"]
                avg_t = dane["timeliness_sum"] / dane["n"]
                print(f"    {klucz:>8}: "
                      f"contrib={dane['contribution']:+.1f}  "
                      f"avg_c={avg_c:+.2f}  "
                      f"timeliness={avg_t:.2f}  (n={dane['n']})")
        print(f"{'═'*62}\n")
