"""
🏛️ IMV-ORI | Neuron Taksonomii Zdarzeń — Dywizja Wyrocznia (NEWS)

NEWS-02 Taksonomia Zdarzeń — głos kierunkowy zależny od TYPU zdarzenia (nie polaryzacji).

RÓŻNICA OD NEWS-01 (Prawo XVI — nie redundancja):
  NEWS-01 = JAK pozytywny/negatywny jest wydźwięk (skalar sentymentu).
  NEWS-02 = JAKI TYP zdarzenia i jaki KIERUNEK on implikuje. Research (arXiv:2508.07408):
  niektóre typy są KONTRARIAŃSKIE — „rumor/spekulacja" ma ujemny Sharpe (fade hype).
  Dwa różne sygnały: sentyment ≠ typ-zdarzenia. NEWS-02 łapie to, czego NEWS-01 nie widzi.

DOSTĘPNOŚĆ (Faza D — obudzony przez AdapterNewsLLM, który dolewa NEWS_EVENT_*):
  Prawo XV: bez feedu newsów neuron ABSTYNUJE (NEUTRAL). W live/paper adapter dostarcza
  NEWS_EVENT_KIERUNEK/TYP/PEWNOSC z klasyfikatora zdarzeń → neuron głosuje.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronTaksonomiaZdarzen(MikroNeuron):
    """
    NEWS-02 | Taksonomia Zdarzeń (W-381) — kierunek per typ zdarzenia newsowego.

    Czyta z Bramy (dostarczone przez AdapterNewsLLM + klasyfikator_zdarzen):
      • NEWS_EVENT_KIERUNEK ∈ [-1, +1] — znakowany kierunek implikowany przez typ
        (HACK/UPADEK/REGULACJA → ujemny; ETF/INSTYTUCJONALNY/TECHNICZNY → dodatni;
        RUMOR → ujemny KONTRARIAŃSKI mimo „pozytywnego" hype'u).
      • NEWS_EVENT_TYP      : str — dominujący typ (do uzasadnienia głosu).
      • NEWS_EVENT_PEWNOSC  ∈ [0, 1] — jednoznaczność klasyfikacji (modulator).

    Logika:
      • kierunek ≥ +PROG → LONG; ≤ −PROG → SHORT; |kierunek| < PROG → NEUTRAL.
      • pewność głosu = |kierunek| · pewność_klasyfikacji (cap PEWNOSC_MAX).
    Brak danych (None) → abstynencja (Prawo XV — nie martwy głos).
    """
    KLUCZ = "NEWS-02"
    LEGION = "WSPOLNY"
    WSKAZNIK = "NEWS_EVENT_KIERUNEK"
    KATEGORIA = "R"
    WAGA = 6
    DOSTEPNY = True   # AdapterNewsLLM dolewa NEWS_EVENT_* (klasyfikator deterministyczny)

    PROG = 0.30          # |kierunek| poniżej → neutralna strefa
    PROG_MOCNY = 0.65    # silny sygnał kierunkowy
    PEWNOSC_MAX = 0.85   # sufit (zdarzenia to sygnał wspierający, nie wyrocznia)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        kier = wskazniki.get("NEWS_EVENT_KIERUNEK")
        if kier is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak feedu zdarzeń (Taksonomia milczy)"])

        typ = wskazniki.get("NEWS_EVENT_TYP") or "?"
        pew_klas = wskazniki.get("NEWS_EVENT_PEWNOSC")
        if pew_klas is None:
            pew_klas = 1.0

        if abs(kier) < self.PROG:
            return self._bazowy_sygnal(kier, "NEUTRAL", 0.15,
                [f"🏷️ Zdarzenie [{typ}] kierunek słaby ({kier:+.2f}) — bez przewagi"])

        pewnosc = min(self.PEWNOSC_MAX, abs(kier) * pew_klas)
        mocny = abs(kier) >= self.PROG_MOCNY
        sila = "MOCNY" if mocny else "umiarkowany"
        kontra = " (KONTRARIAŃSKI fade)" if typ == "RUMOR" else ""
        if kier >= self.PROG:
            return self._bazowy_sygnal(kier, "LONG", pewnosc,
                [f"🏷️ [{typ}] sygnał {sila} LONG ({kier:+.2f}, pewność {pew_klas:.0%}){kontra}"])
        return self._bazowy_sygnal(kier, "SHORT", pewnosc,
            [f"🏷️ [{typ}] sygnał {sila} SHORT ({kier:+.2f}, pewność {pew_klas:.0%}){kontra}"])
