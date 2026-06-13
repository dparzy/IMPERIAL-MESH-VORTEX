"""
🧬 IMV-ORI | Synapsy Reżimowe — Regime-Aware Decorrelated Coalition Graph (W-299).

KONCEPCJA (dla nowicjusza):
  Standardowy MWU (HedgeMWU) uczy się wagi PER-NEURON: „X-01 jest dobry w trendzie".
  Synapsy Reżimowe uczą się wagi PER-PARA: „X-01 + XII-04 razem w TREND_STRONG = złoty
  duet, ale X-01 + XII-02 to echo (wysoka korelacja) — mniej wartości informacyjnej".

  Reguła Hebb'a adaptowana dla rynku:
    w[i][j][rezim] += eta * pnl_znak / (1 + |corr(i,j)|)
  Zysk → wzmocnienie pary, strata → osłabienie. KORELACJA jako kara: dwie silnie
  skorelowane synapsy uczą się WOLNIEJ — ich zgodność to redundancja, nie siła.

  Wynik: mnoznik_pewnosci = 1.0 ± boost z aktywnych par.
  Tylko dekorelowane pary z pozytywnymi synapsami wzmacniają sygnał.

UNIKALNA WŁAŚCIWOŚĆ (niespotykana w retail):
  Żaden znany retail/open-source system nie robi REŻIMOWO-WARUNKOWANEGO uczenia
  ZDEKORELOWANYCH koalicji neuronów. Łączy Prawo XVI (dekorelacja mierzona) z
  uczeniem online (Hebbian × MWU) × pamięcią per-reżim.

INTEGRACJA:
  Legatus.fokus() → po policzeniu pewnosc_agregatu → wzmocnij_pewnosc()
  Dyrygent._aktualizuj_synapsy() → po zamknięciu pozycji → aktualizuj()
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Parametry uczenia
ETA = 0.05              # współczynnik uczenia (konserwatywny — wolne, stabilne)
ALPHA_DECAY = 0.001     # zapomnienie per-bar (synaps dryf ku 0 bez potwierdzenia)
MAX_WZMOCNIENIE = 0.25  # max +25% boost pewności od aktywnych dobrych par
MAX_REDUKCJA = 0.15     # max -15% kara za aktywne złe pary
MIN_WYMAGAN_TRAD = 3    # minimalna liczba aktualizacji zanim synaps „głosuje"
SILA_MIN = 0.05         # poniżej tej wartości bezwzględnej synaps jest neutralny


@dataclass
class StatystykiSynapsy:
    """Diagnostyka stanu grafu — używana w audycie i testach."""
    n_par_aktywnych: int      # par z |sila| ≥ SILA_MIN
    n_par_razem: int          # wszystkich par w silo
    n_rezimow: int            # unikalnych reżimów z historią
    srednia_sila: float       # średnia wartość bezwzględna synaps
    top3: List[Tuple[str, float]]   # top 3 najsilniejsze pary (klucz, sila)


class SynapsyRezimowe:
    """
    Graf koalicji par neuronów warunkowany reżimem × dekorelacja.

    Klucz synapsy: "KlA|KlB@REZIM" (para sortowana leksykograficznie →
    „X-01|XII-04@TREND_STRONG" = „XII-04|X-01@TREND_STRONG").

    Nie modyfikuje WAGI_REZIMU ani mnozniki_neuronow — działa PONAD nimi
    jako mnożnik pewności agregatu (komplementarny, nie zastępujący).
    """

    def __init__(
        self,
        eta: float = ETA,
        alpha_decay: float = ALPHA_DECAY,
        max_wzmocnienie: float = MAX_WZMOCNIENIE,
        max_redukcja: float = MAX_REDUKCJA,
        min_trad: int = MIN_WYMAGAN_TRAD,
        sciezka_stanu: Optional[str] = None,
    ):
        self.eta = eta
        self.alpha_decay = alpha_decay
        self.max_wzmocnienie = max_wzmocnienie
        self.max_redukcja = max_redukcja
        self.min_trad = min_trad
        self.sciezka_stanu = sciezka_stanu
        # {klucz_pary: sila} — graf w flat dict
        self._silo: Dict[str, float] = {}
        # {klucz_pary: liczba_aktualizacji} — pewność statystyczna pary
        self._licznik: Dict[str, int] = {}

        if sciezka_stanu:
            self._wczytaj(sciezka_stanu)

    # ── Aktualizacja (uczenie) ────────────────────────────────────────────────

    def aktualizuj(
        self,
        sygnaly: list,          # List[SygnalNeuronu] ze zwróconego RaportLegatusa
        kierunek_decyzji: str,  # "LONG" lub "SHORT"
        pnl_pct: float,         # % zysk (>0) / strata (<0) z zamkniętej pozycji
        rezim: str,
        korelacje: Optional[Dict[Tuple[str, str], float]] = None,
    ) -> None:
        """
        Aktualizuje synaps par neuronów po zamknięciu pozycji.

        sygnaly: lista SygnalNeuronu z raport.sygnaly (te co głosowały w cyklu wejścia).
        pnl_pct: pnl jako procent (np. 2.5 = +2.5%, -1.2 = -1.2%).
        korelacje: {(ki, kj): corr} z diagnostyka_korelacji (opcjonalne).
                   Brak = traktuje wszystkie pary jako niezależne (corr=0).
        """
        if not sygnaly or kierunek_decyzji == "NEUTRAL":
            return

        pnl_znak = 1.0 if pnl_pct > 0 else -1.0
        zgodne = [s for s in sygnaly if s.kierunek == kierunek_decyzji]

        if len(zgodne) < 2:
            return  # para potrzebuje co najmniej 2 neuronów

        korelacje = korelacje or {}

        for idx_i in range(len(zgodne)):
            for idx_j in range(idx_i + 1, len(zgodne)):
                ni = zgodne[idx_i]
                nj = zgodne[idx_j]
                klucz = _klucz_pary(ni.neuron_id, nj.neuron_id, rezim)

                corr = abs(korelacje.get((ni.neuron_id, nj.neuron_id), 0.0)
                           or korelacje.get((nj.neuron_id, ni.neuron_id), 0.0))
                kara_korelacji = 1.0 + corr   # corr=0 → 1.0 (pełne uczenie), corr=1 → 2.0 (wolne)

                delta = self.eta * pnl_znak / kara_korelacji
                stara = self._silo.get(klucz, 0.0)
                nowa = max(-1.0, min(1.0, stara + delta))
                self._silo[klucz] = round(nowa, 6)
                self._licznik[klucz] = self._licznik.get(klucz, 0) + 1

    def zapomnij(self) -> None:
        """Stosuje decay do wszystkich synaps (wywołaj co bar lub co N barów)."""
        for k in list(self._silo.keys()):
            v = self._silo[k]
            if abs(v) < self.alpha_decay:
                del self._silo[k]
            else:
                self._silo[k] = round(v * (1.0 - self.alpha_decay), 6)

    # ── Wzmocnienie pewności (inference) ─────────────────────────────────────

    def wzmocnij_pewnosc(
        self,
        pewnosc: float,
        sygnaly_zgodne: list,    # List[SygnalNeuronu] głosujące ZA kierunkiem
        rezim: str,
        korelacje: Optional[Dict[Tuple[str, str], float]] = None,
    ) -> float:
        """
        Zwraca zmodyfikowaną pewność w [0, 1] po uwzględnieniu synaps aktywnych par.

        Pary z silnymi pozytywnymi synapsami i niską korelacją → wzmocnienie.
        Pary z negatywnymi synapsami → redukcja.
        Brak par lub za mało historii → brak zmiany (neutralne).
        """
        if len(sygnaly_zgodne) < 2:
            return pewnosc

        korelacje = korelacje or {}
        score_sum = 0.0
        n_par = 0

        for idx_i in range(len(sygnaly_zgodne)):
            for idx_j in range(idx_i + 1, len(sygnaly_zgodne)):
                ni = sygnaly_zgodne[idx_i]
                nj = sygnaly_zgodne[idx_j]
                klucz = _klucz_pary(ni.neuron_id, nj.neuron_id, rezim)

                if self._licznik.get(klucz, 0) < self.min_trad:
                    continue  # za mało historii → neutralne

                sila = self._silo.get(klucz, 0.0)
                if abs(sila) < SILA_MIN:
                    continue  # pomijamy neutralne

                # Amplifikacja przez dekorelację: para niezależna (corr≈0) = pełny głos
                corr = abs(korelacje.get((ni.neuron_id, nj.neuron_id), 0.0)
                           or korelacje.get((nj.neuron_id, ni.neuron_id), 0.0))
                dekorelacja = 1.0 - corr   # 0 = wysoce skorelowane, 1 = niezależne

                score_sum += sila * dekorelacja
                n_par += 1

        if n_par == 0:
            return pewnosc

        # Normalizacja i ograniczenie zakresu wpływu
        score_norm = score_sum / n_par
        boost = max(-self.max_redukcja, min(self.max_wzmocnienie, score_norm))
        wynik = max(0.0, min(1.0, pewnosc + boost))
        return round(wynik, 4)

    # ── Statystyki ────────────────────────────────────────────────────────────

    def statystyki(self) -> StatystykiSynapsy:
        aktywne = [(k, v) for k, v in self._silo.items() if abs(v) >= SILA_MIN]
        rezimy = set(k.split("@")[1] for k in self._silo if "@" in k)
        srednia = (sum(abs(v) for v in self._silo.values()) / max(len(self._silo), 1))
        top3 = sorted(aktywne, key=lambda x: abs(x[1]), reverse=True)[:3]
        return StatystykiSynapsy(
            n_par_aktywnych=len(aktywne),
            n_par_razem=len(self._silo),
            n_rezimow=len(rezimy),
            srednia_sila=round(srednia, 4),
            top3=[(k, v) for k, v in top3],
        )

    def ile_par(self) -> int:
        return len(self._silo)

    # ── Persystencja ─────────────────────────────────────────────────────────

    def zapisz(self, sciezka: Optional[str] = None) -> None:
        """Zapisuje silo i liczniki do JSON (opcjonalna persystencja)."""
        sciezka = sciezka or self.sciezka_stanu
        if not sciezka:
            return
        Path(sciezka).write_text(
            json.dumps({"silo": self._silo, "licznik": self._licznik}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _wczytaj(self, sciezka: str) -> None:
        p = Path(sciezka)
        if not p.exists():
            return
        try:
            dane = json.loads(p.read_text(encoding="utf-8"))
            self._silo = dane.get("silo", {})
            self._licznik = dane.get("licznik", {})
        except Exception:
            pass  # uszkodzony plik → zaczynamy od zera


# ── helpers ──────────────────────────────────────────────────────────────────

def _klucz_pary(ki: str, kj: str, rezim: str) -> str:
    """Deterministyczny klucz pary (niezależny od kolejności) + reżim."""
    a, b = (ki, kj) if ki <= kj else (kj, ki)
    return f"{a}|{b}@{rezim}"
