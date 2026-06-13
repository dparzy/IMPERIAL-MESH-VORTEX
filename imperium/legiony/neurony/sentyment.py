"""
🏛️ IMV-ORI | Neurony Sentymentu Newsów — Dywizja Wyrocznia (NEWS)

NEWS-01 Sentyment Newsów LLM — głos nastroju z nagłówków/feedu rynkowego.

DOSTĘPNOŚĆ (Faza D — obudzony przez AdapterNewsLLM):
  NEWS-01 NEWS_SENTYMENT — AdapterNewsLLM (DeepSeek LLM + fallback słownikowy).
  Prawo XV: w czystym backteście z CSV (bez feedu newsów) neuron ABSTYNUJE
  (zwraca NEUTRAL, rój wyklucza go z głosu kierunkowego — nie martwy ciężar).
  W trybie live/paper adapter dolewa NEWS_SENTYMENT (-1..+1) → neuron głosuje.

ZASADA PEŁNEGO OPISU (ZPO):
  LLM = Large Language Model (DeepSeek deepseek-chat). NIE liczy matematyki —
  tylko KLASYFIKUJE wydźwięk nagłówków (Prawo I). Adapter mapuje werdykt LLM
  na liczbę NEWS_SENTYMENT, neuron ją interpretuje (kierunek + pewność).

Sentyment newsów to sygnał MOMENTUM informacyjnego, nie kontrariański:
  silnie pozytywne nagłówki (partnerstwa, adopcja, ETF) → LONG;
  silnie negatywne (hacki, regulacje, upadki) → SHORT. W strefie szumu — cisza.
"""

from imperium.legiony.mikro_neuron import MikroNeuron, SygnalNeuronu


class NeuronSentymentNews(MikroNeuron):
    """
    NEWS-01 | Sentyment Newsów LLM (W-297) — wydźwięk feedu rynkowego.

    Czyta z Bramy (dostarczone przez AdapterNewsLLM):
      • NEWS_SENTYMENT ∈ [-1, +1] — uśredniony wydźwięk (−1 skrajnie negatywny,
        +1 skrajnie pozytywny, 0 neutralny/mieszany).
      • NEWS_PEWNOSC  ∈ [0, 1]    — pewność klasyfikacji LLM (modulator).
      • NEWS_N        : int       — ile nagłówków złożyło się na werdykt.

    Logika (momentum informacyjny, nie kontrariański):
      • |sentyment| < PROG_SZUMU lub N < MIN_NAGLOWKOW → NEUTRAL (za słaby sygnał).
      • sentyment ≥ +PROG_SZUMU → LONG, pewność = |s| · pewnosc_llm (cap 0.85).
      • sentyment ≤ −PROG_SZUMU → SHORT, analogicznie.
    Brak feedu (NEWS_SENTYMENT None) → abstynencja (Prawo XV — nie martwy głos).
    """
    KLUCZ = "NEWS-01"
    LEGION = "WSPOLNY"
    WSKAZNIK = "NEWS_SENTYMENT"
    KATEGORIA = "R"
    WAGA = 6
    DOSTEPNY = True   # AdapterNewsLLM (DeepSeek + fallback słownikowy, offline-first)

    PROG_SZUMU = 0.30      # |sentyment| poniżej → strefa neutralna (szum informacyjny)
    PROG_MOCNY = 0.65      # |sentyment| powyżej → silny sygnał kierunkowy
    MIN_NAGLOWKOW = 2      # mniej niż tyle nagłówków = anegdota, nie sygnał
    PEWNOSC_MAX = 0.85     # sufit pewności (news to sygnał wspierający, nie wyrocznia)

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        sent = wskazniki.get("NEWS_SENTYMENT")
        if sent is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0,
                ["Brak feedu newsów (Sentyment milczy)"])

        n = wskazniki.get("NEWS_N") or 0
        pewnosc_llm = wskazniki.get("NEWS_PEWNOSC")
        if pewnosc_llm is None:
            pewnosc_llm = 1.0

        if n < self.MIN_NAGLOWKOW:
            return self._bazowy_sygnal(sent, "NEUTRAL", 0.20,
                [f"📰 tylko {n} nagłówków — za mało na werdykt (Prawo I)"])

        mocny = abs(sent) >= self.PROG_MOCNY
        if sent >= self.PROG_SZUMU:
            pewnosc = min(self.PEWNOSC_MAX, abs(sent) * pewnosc_llm)
            etykieta = "MOCNO pozytywny" if mocny else "pozytywny"
            return self._bazowy_sygnal(sent, "LONG", pewnosc,
                [f"📰 Sentyment {etykieta} ({sent:+.2f}, n={n}, "
                 f"pewność LLM {pewnosc_llm:.0%}) — momentum informacyjny LONG"])
        if sent <= -self.PROG_SZUMU:
            pewnosc = min(self.PEWNOSC_MAX, abs(sent) * pewnosc_llm)
            etykieta = "MOCNO negatywny" if mocny else "negatywny"
            return self._bazowy_sygnal(sent, "SHORT", pewnosc,
                [f"📰 Sentyment {etykieta} ({sent:+.2f}, n={n}, "
                 f"pewność LLM {pewnosc_llm:.0%}) — momentum informacyjny SHORT"])
        return self._bazowy_sygnal(sent, "NEUTRAL", 0.15,
            [f"📰 Sentyment w strefie szumu ({sent:+.2f}, n={n}) — bez przewagi"])
