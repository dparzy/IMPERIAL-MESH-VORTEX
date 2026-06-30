"""
🏛️ IMV-ORI | Neurony Dynamiki Newsów — Dywizja Wyrocznia (NEWS)

NEWS-03 Spike Uwagi      — nagły wysyp nagłówków = przełom uwagi (breakout informacyjny).
NEWS-04 Δ Sentymentu     — ZMIANA wydźwięku w czasie (momentum informacyjny, nie poziom).

RÓŻNICA OD NEWS-01/02 (Prawo XVI — nie redundancja):
  NEWS-01 = poziom sentymentu (JAK pozytywny). NEWS-02 = typ zdarzenia (JAKI).
  NEWS-04 = POCHODNA sentymentu (czy się POPRAWIA/POGARSZA — sygnał wyprzedzający).
  NEWS-03 = POCHODNA UWAGI (czy nagle DUŻO o tym piszą — przełom, zmienność).
  Cztery różne wymiary newsów: poziom, typ, momentum, uwaga.

DANE z Bramy (AdapterNewsLLM, stan kroczący):
  NEWS_SENTYMENT_DELTA ∈ ℝ — bieżący sentyment − średnia historyczna (momentum).
  NEWS_ATTENTION_SPIKE ≥ 0  — liczba nagłówków / średnia historyczna (1.0 = normalnie).
Brak historii/feedu → None → abstynencja (Prawo XV).
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronDeltaeSentymentu(MikroNeuron):
    """
    NEWS-04 | Δ Sentymentu (W-382) — momentum informacyjny (pochodna sentymentu).

    Sentyment ROSNĄCY (Δ>0) → poprawa nastroju, bias LONG (wyprzedza poziom).
    Sentyment OPADAJĄCY (Δ<0) → pogorszenie, bias SHORT. |Δ| < próg → NEUTRAL.
    """
    KLUCZ = "NEWS-04"
    LEGION = "WSPOLNY"
    WSKAZNIK = "NEWS_SENTYMENT_DELTA"
    KATEGORIA = "R"
    WAGA = 5
    DOSTEPNY = True

    PROG = 0.25          # |Δ| poniżej → szum
    PEWNOSC_MAX = 0.75   # momentum to sygnał wspierający

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        d = wskazniki.get("NEWS_SENTYMENT_DELTA")
        if d is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak historii sentymentu (Δ milczy)"])
        if abs(d) < self.PROG:
            return self._bazowy_sygnal(d, "NEUTRAL", 0.15,
                [f"📈 Δsentyment słaby ({d:+.2f}) — bez momentum"])
        pewnosc = min(self.PEWNOSC_MAX, abs(d))
        if d >= self.PROG:
            return self._bazowy_sygnal(d, "LONG", pewnosc,
                [f"📈 Sentyment POPRAWIA się (Δ{d:+.2f}) — momentum informacyjny LONG"])
        return self._bazowy_sygnal(d, "SHORT", pewnosc,
            [f"📉 Sentyment POGARSZA się (Δ{d:+.2f}) — momentum informacyjny SHORT"])


class NeuronSpikeUwagi(MikroNeuron):
    """
    NEWS-03 | Spike Uwagi (W-382) — przełom informacyjny (nagły wysyp nagłówków).

    Spike sam w sobie jest BEZKIERUNKOWY (zwiastun zmienności). Łączymy go z bieżącym
    sentymentem: silny spike + wyraźny sentyment → przełom w tym kierunku (breakout
    informacyjny). Spike bez kierunku sentymentu → NEUTRAL (czujność, nie pozycja).
    """
    KLUCZ = "NEWS-03"
    LEGION = "WSPOLNY"
    WSKAZNIK = "NEWS_ATTENTION_SPIKE"
    KATEGORIA = "R"
    WAGA = 5
    DOSTEPNY = True

    PROG_SPIKE = 2.0     # ≥2× średniej uwagi = przełom (nagły wysyp)
    PROG_SENT = 0.20     # potrzebny minimalny kierunek sentymentu, by zająć pozycję
    PEWNOSC_MAX = 0.80

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        spike = wskazniki.get("NEWS_ATTENTION_SPIKE")
        if spike is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak historii uwagi (Spike milczy)"])
        if spike < self.PROG_SPIKE:
            return self._bazowy_sygnal(spike, "NEUTRAL", 0.15,
                [f"📡 Uwaga normalna ({spike:.1f}×) — brak przełomu"])
        sent = wskazniki.get("NEWS_SENTYMENT") or 0.0
        if abs(sent) < self.PROG_SENT:
            return self._bazowy_sygnal(spike, "NEUTRAL", 0.25,
                [f"📡 SPIKE uwagi ({spike:.1f}×) bez kierunku sentymentu — czujność (zmienność)"])
        pewnosc = min(self.PEWNOSC_MAX, 0.4 + (spike - self.PROG_SPIKE) * 0.1)
        if sent > 0:
            return self._bazowy_sygnal(spike, "LONG", pewnosc,
                [f"📡 PRZEŁOM informacyjny ({spike:.1f}× uwagi) + sentyment {sent:+.2f} → LONG"])
        return self._bazowy_sygnal(spike, "SHORT", pewnosc,
            [f"📡 PRZEŁOM informacyjny ({spike:.1f}× uwagi) + sentyment {sent:+.2f} → SHORT"])
