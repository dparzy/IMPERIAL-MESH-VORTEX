"""
🧭 IMV-ORI | GUBERNATOR — Homeostatyczny Sterownik Portfela (W-325).

KONCEPCJA (dla nowicjusza):
  Imperium ma wiele lokalnych „rządów": HedgeMWU rządzi wagą każdego neuronu,
  Synapsy rządzą parami neuronów, Namiestnik włącza/wyłącza pojedynczą parę walut,
  Bezpiecznik tnie sizing przy obsunięciu kapitału. Ale NIKT nie rządził CAŁOŚCIĄ —
  nie było jednej dłoni na sterze całej floty 5 par naraz.

  GUBERNATOR to ta dłoń. Jak regulator Watta (odśrodkowy gubernator parowy) trzyma
  stałe obroty maszyny — tu trzyma ZDROWĄ EKSPOZYCJĘ portfela: gdy okazje są wyraźne
  i kapitał zdrowy → pozwala flocie przyspieszyć (mnożnik > 1). Gdy rynek to „papka"
  (żadnej wyraźnej okazji) albo trwa obsunięcie → ściąga ster, chroni proch (mnożnik < 1).
  Łacińskie „gubernator" = sternik. Steruje płynnie, nie skokowo (histereza stanów).

UNIKALNA WŁAŚCIWOŚĆ (niespotykana w retail/open-source):
  Sygnałem pewności jest ROZRZUT OCEN SKANERA — meta-cecha z WŁASNEJ niezgody zespołu
  (López de Prado „meta-labeling", ale na poziomie PORTFELA, nie pojedynczego modelu):
    • duży rozrzut → jest WYRAŹNY lider koszyka → wysoka pewność → ekspansja
    • mały rozrzut → wszystkie pary podobnie mdłe → niska pewność → obrona
  Żaden znany bot retail nie używa wewnętrznej dyspersji rankingu okazji jako
  homeostatycznego regulatora globalnego ryzyka z histerezą stanów.

HOMEOSTAZA Z HISTEREZĄ (płynność, nie skoki):
  Gubernator trzyma STAN (postawę). Przejście między postawami wymaga PRZEKROCZENIA
  progu z marginesem (histereza dwustronna) — to gasi „trzepotanie" (flapping) przy
  wartościach na granicy. Lekcja z literatury regime-gating: pojedynczy próg = flapping.

NEUTRALNOŚĆ (Prawo XV — brak zniekształcenia):
  Dla neutralnego wejścia (konwikcja≈0.5, rozrzut≈0, brak obsunięcia) zwraca mnożnik
  ≈1.0 → portfel działa jak bez Gubernatora. Mnożnik oddala się od 1.0 dopiero gdy
  stan koszyka faktycznie woła o ekspansję albo obronę. Domyślnie OPT-IN w backteście.

INTEGRACJA:
  backtest_portfel(..., gubernator=True) → w pętli sizingu, po skanerze i bezpieczniku:
    g = gub.ocen(konwikcja_koszyka=..., rozrzut_okazji=..., dd_frakcja=..., breadth=...)
    kapital_sizing *= g.mnoznik
"""

from dataclasses import dataclass


# Postawy portfela (od najbardziej agresywnej do najbardziej obronnej).
EKSPANSJA = "EKSPANSJA"      # wyraźny lider + zdrowy kapitał → naciskamy przewagę
NORMALNY = "NORMALNY"        # stan bazowy → mnożnik ≈ 1.0
OSTROZNY = "OSTROZNY"        # lekka niepewność (mdły koszyk) → przyhamuj
OBRONA = "OBRONA"            # obsunięcie lub brak okazji → chroń kapitał
KWARANTANNA = "KWARANTANNA"  # głębokie obsunięcie → minimalna ekspozycja (suchy proch)

KOLEJNOSC_POSTAW = (KWARANTANNA, OBRONA, OSTROZNY, NORMALNY, EKSPANSJA)


@dataclass
class StanGubernatora:
    """Werdykt Gubernatora w jednym tyku — mnożnik + diagnostyka (audyt/raport)."""
    mnoznik: float        # globalny mnożnik sizingu portfela [floor, ceiling]
    postawa: str          # jedna z KOLEJNOSC_POSTAW
    powod: str            # czytelne uzasadnienie (dla Cezara)
    konwikcja: float      # pewność koszyka [0,1] (znormalizowana siła top-okazji)
    rozrzut: float        # dyspersja ocen skanera [0,1] (wyrazistość lidera)
    dd_frakcja: float     # frakcja bezpiecznika DD (1.0=zdrowo, <1=obsunięcie)
    breadth: float        # szerokość okazji [0,1] (ile par ma żywą okazję)


class Gubernator:
    """
    Homeostatyczny sterownik globalnej ekspozycji portfela (W-325).

    floor/ceiling: granice mnożnika (np. 0.5×–1.3×).
    histereza: margines progu gaszący trzepotanie między postawami.
    """

    def __init__(self, floor: float = 0.5, ceiling: float = 1.3,
                 prog_ekspansja: float = 0.62, prog_ostrozny: float = 0.40,
                 prog_obrona_dd: float = 0.95, prog_kwarantanna_dd: float = 0.5,
                 histereza: float = 0.06, alpha_wygladzania: float = 0.30):
        if not (0.0 < floor <= 1.0 <= ceiling):
            raise ValueError("Wymagane: 0 < floor ≤ 1 ≤ ceiling")
        if not (0.0 <= prog_ostrozny < prog_ekspansja <= 1.0):
            raise ValueError("Wymagane: 0 ≤ prog_ostrozny < prog_ekspansja ≤ 1")
        if histereza < 0:
            raise ValueError("histereza ≥ 0")
        self.floor = floor
        self.ceiling = ceiling
        self.prog_ekspansja = prog_ekspansja
        self.prog_ostrozny = prog_ostrozny
        self.prog_obrona_dd = prog_obrona_dd
        self.prog_kwarantanna_dd = prog_kwarantanna_dd
        self.histereza = histereza
        self.alpha = alpha_wygladzania
        self.postawa = NORMALNY            # stan początkowy — neutralny
        self._mnoznik_wygl = 1.0           # wygładzony mnożnik (płynność ruchu stera)

    # ── Wewnętrzna maszyna stanów z histerezą ──────────────────────────────────
    def _docelowa_postawa(self, zdrowie: float, dd_frakcja: float) -> str:
        """
        Wyznacz docelową postawę z wartości zdrowia [0,1] i frakcji DD.
        Histereza: by ZMIENIĆ postawę, sygnał musi przekroczyć próg O margines —
        inaczej zostajemy w obecnej (gasi trzepotanie na granicy).
        """
        h = self.histereza

        # 1) Twarde nadrzędne: głębokie obsunięcie → KWARANTANNA (ochrona kapitału > wszystko).
        if dd_frakcja <= self.prog_kwarantanna_dd:
            return KWARANTANNA
        # 2) Obsunięcie umiarkowane → co najwyżej OBRONA (nie pozwól na ekspansję w DD).
        if dd_frakcja < self.prog_obrona_dd:
            # wyjście z OBRONY w górę wymaga ustąpienia DD — tu DD wciąż trwa.
            # Uproszczone 2026-07-19 BIT-IDENTYCZNIE: był tu `OBRONA if
            # KOLEJNOSC_POSTAW.index(OBRONA) <= idx + 1 else OBRONA` — obie gałęzie
            # zwracały OBRONA, a warunek był zawsze prawdziwy (index(OBRONA)=1 ≤ idx+1
            # dla każdego idx≥0), więc `idx` istniał wyłącznie dla martwego warunku.
            # OTWARTE PYTANIE SEMANTYCZNE (decyzja Cezara, dotyka sizingu → wymaga A/B):
            # „co najwyżej OBRONA" może znaczyć min(obecna, OBRONA) — wtedy KWARANTANNA
            # NIE powinna być podnoszona do OBRONY. Zachowania NIE zmieniam bez walidacji.
            return OBRONA

        # 3) Kapitał zdrowy → postawa z poziomu „zdrowia" koszyka, z histerezą.
        #    Wejście w wyższą postawę: próg + h. Spadek w niższą: próg - h.
        gora = self.prog_ekspansja
        dol = self.prog_ostrozny
        if self.postawa == EKSPANSJA:
            return EKSPANSJA if zdrowie >= gora - h else NORMALNY
        if self.postawa in (NORMALNY, OSTROZNY, OBRONA, KWARANTANNA):
            if zdrowie >= gora + h:
                return EKSPANSJA
            if zdrowie <= dol - h:
                return OSTROZNY
            if zdrowie >= dol + h:
                return NORMALNY
            # w pasie martwym histerezy — zostań przy obecnej (jeśli sensowna)
            return self.postawa if self.postawa in (NORMALNY, OSTROZNY) else NORMALNY
        return NORMALNY

    def _mnoznik_postawy(self, postawa: str, zdrowie: float, dd_frakcja: float) -> float:
        """Mapuj postawę na liczbowy mnożnik w [floor, ceiling]."""
        if postawa == KWARANTANNA:
            return self.floor
        if postawa == OBRONA:
            # skaluj między floor a 1.0 wg tego, jak głębokie obsunięcie
            t = max(0.0, min(1.0, (dd_frakcja - self.prog_kwarantanna_dd)
                             / max(1e-9, self.prog_obrona_dd - self.prog_kwarantanna_dd)))
            return self.floor + t * (1.0 - self.floor)
        if postawa == OSTROZNY:
            return self.floor + (1.0 - self.floor) * 0.7   # lekkie przyhamowanie
        if postawa == NORMALNY:
            return 1.0
        if postawa == EKSPANSJA:
            # skaluj 1.0 → ceiling wg tego, jak bardzo zdrowie przebija próg ekspansji
            t = max(0.0, min(1.0, (zdrowie - self.prog_ekspansja)
                             / max(1e-9, 1.0 - self.prog_ekspansja)))
            return 1.0 + t * (self.ceiling - 1.0)
        return 1.0

    def ocen(self, *, konwikcja_koszyka: float, rozrzut_okazji: float,
             dd_frakcja: float = 1.0, breadth: float = 1.0) -> StanGubernatora:
        """
        Główny puls Gubernatora. Wejścia (wszystkie liczalne w pętli, bez look-ahead):
          konwikcja_koszyka: [0,1] znormalizowana siła najlepszej okazji koszyka.
          rozrzut_okazji:    [0,1] dyspersja ocen skanera (wyrazistość lidera).
          dd_frakcja:        frakcja bezpiecznika DD (1.0=zdrowo, <1=obsunięcie).
          breadth:           [0,1] ułamek par z żywą okazją.

        Zwraca StanGubernatora z mnożnikiem [floor, ceiling] i diagnostyką.
        """
        k = max(0.0, min(1.0, konwikcja_koszyka))
        r = max(0.0, min(1.0, rozrzut_okazji))
        b = max(0.0, min(1.0, breadth))

        # „Zdrowie" koszyka = pewność wzmocniona wyrazistością lidera, lekko karana
        # przez zbyt wąską szerokość (jedyna okazja w martwym rynku = ostrożność).
        zdrowie = 0.55 * k + 0.30 * r + 0.15 * b

        docelowa = self._docelowa_postawa(zdrowie, dd_frakcja)
        self.postawa = docelowa
        mnoznik_cel = self._mnoznik_postawy(docelowa, zdrowie, dd_frakcja)

        # Wygładzanie wykładnicze — ster portfela rusza płynnie, nie skacze (homeostaza).
        self._mnoznik_wygl = (1 - self.alpha) * self._mnoznik_wygl + self.alpha * mnoznik_cel
        mnoznik = max(self.floor, min(self.ceiling, self._mnoznik_wygl))

        powod = self._opis(docelowa, zdrowie, dd_frakcja)
        return StanGubernatora(
            mnoznik=round(mnoznik, 4), postawa=docelowa, powod=powod,
            konwikcja=round(k, 3), rozrzut=round(r, 3),
            dd_frakcja=round(dd_frakcja, 3), breadth=round(b, 3),
        )

    @staticmethod
    def _opis(postawa: str, zdrowie: float, dd: float) -> str:
        if postawa == KWARANTANNA:
            return f"głębokie obsunięcie (DD frakcja {dd:.2f}) → minimalna ekspozycja, suchy proch"
        if postawa == OBRONA:
            return f"obsunięcie kapitału (DD frakcja {dd:.2f}) → chronimy proch"
        if postawa == OSTROZNY:
            return f"mdły koszyk (zdrowie {zdrowie:.2f}) → przyhamowanie ekspozycji"
        if postawa == EKSPANSJA:
            return f"wyraźny lider + zdrowy kapitał (zdrowie {zdrowie:.2f}) → naciskamy przewagę"
        return f"stan bazowy (zdrowie {zdrowie:.2f}) → ekspozycja nominalna"


def rozrzut_ocen(oceny: "list[float]") -> float:
    """
    Dyspersja ocen skanera znormalizowana do [0,1] — „jak wyraźny jest lider koszyka".
    Definicja: (max - mediana) / (max - min), odporna na skalę i znak.
    Pusta/jednoelementowa lista → 0.0 (brak wyrazistości). Zerowy rozstęp → 0.0.
    """
    n = len(oceny)
    if n < 2:
        return 0.0
    s = sorted(oceny)
    lo, hi = s[0], s[-1]
    rozstep = hi - lo
    if rozstep < 1e-12:
        return 0.0
    mediana = s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])
    return max(0.0, min(1.0, (hi - mediana) / rozstep))
