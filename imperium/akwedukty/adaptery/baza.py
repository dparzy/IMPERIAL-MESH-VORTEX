"""
🔌 AdapterDanych — bazowy most: zewnętrzne API → dict `wskazniki` → rój budzi neurony.

WIZJA (Cezar): "teraz wersja testowa, a później łatwe auto-wybudzenie".
  Ten framework realizuje DOKŁADNIE ten model. Wzór skopiowany z mostu SMC
  (EXP-05 `wstrzyknij()` + `aktywuj_neurony_smc()`), który już działa w roju.

JAK DZIAŁA (identycznie jak SMC, tylko źródłem są dane API, nie bary):
  1. `wzbogac(wskazniki, symbol)` — dolewa klucze API do dict (jak EXP-05.wstrzyknij)
  2. `aktywuj()` — budzi neurony domeny (DOSTEPNY=True), jak aktywuj_neurony_smc()
  3. rój głosuje — wyciszone dotąd neurony interpretują świeże dane

WERSJA TESTOWA → PRODUKCYJNA (łatwe przełączenie):
  - dziś: AdapterTestowy* (mock, dane syntetyczne, działa offline, testowalny)
  - jutro: podklasa z `pobierz()` uderzającym w prawdziwe API (MEXC/Glassnode)
  - interfejs ten sam → reszta pipeline bez zmian (Prawo XIX: kontrakt stały)

BEZPIECZEŃSTWO (NIENARUSZALNE):
  Adaptery produkcyjne czytają klucze TYLKO ze zmiennych środowiskowych
  (os.getenv). Żadnych kluczy w kodzie. Mock nie potrzebuje żadnych kluczy.

PRAWO XV (zero martwych głosów):
  `aktywuj()` budzi neuron TYLKO razem z adapterem, który faktycznie dostarcza
  jego dane. Bez adaptera neuron śpi — świadomie, nie jako martwy głos.
  `usypiaj()` przywraca stan (ważne w testach — by nie zafałszować audytu).
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("Adapter")


class AdapterDanych:
    """
    Bazowy adapter. Podklasy nadpisują `pobierz()` (skąd dane) i deklarują:
      NAZWA        — czytelna nazwa domeny (logi)
      KLUCZE       — które klucze `wskazniki` dostarcza (dokumentacja/audyt)
      _NEURONY     — krotka klas neuronów, które ten adapter budzi
      _POWOD_USPIENIA — tekst przywracany przy usypianiu (spójny z neuronem)
    """
    NAZWA: str = "bazowy"
    KLUCZE: List[str] = []
    _NEURONY: tuple = ()
    _POWOD_USPIENIA: str = "Adapter danych odpięty."

    # ── Dostarczanie danych ──────────────────────────────────────────────────
    def pobierz(self, symbol: str) -> Dict[str, Any]:
        """
        Zwraca dict {KLUCZ: wartość} z danymi domeny dla symbolu.
        Podklasa MUSI nadpisać. Mock zwraca dane syntetyczne, produkcja — z API.
        """
        raise NotImplementedError("Podklasa musi zaimplementować pobierz().")

    def wzbogac(self, wskazniki: dict, symbol: str = "") -> dict:
        """
        MOST DO NEURONÓW (analogia EXP-05.wstrzyknij).
        Dolewa dane API do dict `wskazniki` (in-place + zwraca).
        Wartości None pomijane — nie nadpisujemy istniejących kluczy pustką.
        """
        try:
            dane = self.pobierz(symbol)
        except Exception as e:
            logger.error(f"[Adapter:{self.NAZWA}] pobierz() padł dla {symbol}: {e}")
            return wskazniki
        wskazniki.update({k: v for k, v in dane.items() if v is not None})
        return wskazniki

    # ── Wybudzanie neuronów ──────────────────────────────────────────────────
    def aktywuj(self) -> List[str]:
        """
        Budzi neurony domeny (DOSTEPNY=True). Wywołaj RAZ, gdy adapter jest
        podpięty i będzie dostarczał dane. Zwraca listę kluczy obudzonych neuronów.
        """
        obudzone = []
        for klasa in self._NEURONY:
            klasa.DOSTEPNY = True
            klasa.POWOD_NIEDOSTEPNOSCI = ""
            obudzone.append(klasa.KLUCZ)
        if obudzone:
            logger.info(f"[Adapter:{self.NAZWA}] obudzono neurony: {obudzone}")
        return obudzone

    def usypiaj(self) -> List[str]:
        """
        Przywraca neurony domeny do stanu wyciszonego (DOSTEPNY=False).
        Używane w testach (teardown), by nie zafałszować statycznego audytu,
        oraz gdy adapter zostaje odpięty (np. utrata połączenia z API).
        """
        uspione = []
        for klasa in self._NEURONY:
            klasa.DOSTEPNY = False
            klasa.POWOD_NIEDOSTEPNOSCI = self._POWOD_USPIENIA
            uspione.append(klasa.KLUCZ)
        return uspione

    def neurony_obslugiwane(self) -> List[str]:
        """Klucze neuronów, które ten adapter budzi (do audytu/dokumentacji)."""
        return [k.KLUCZ for k in self._NEURONY]
