"""
🗺️ IMV | Dywizja Strategii — bazowy model + silnik dopasowania

WIZJA (Cezar):
  Neurony (cała armia) wysyłają sygnały → "odcisk palca" rynku TERAZ.
  Baza strategii (przepisy ludzi: scalp/swing/invest) czeka w katalogu.
  Silnik AUTOMATYCZNIE dobiera NAJBLIŻSZĄ strategię do bieżących sygnałów.
  Potem: kalibracja w testach/live, a na bazie ustawień — nowe własne strategie.

KLUCZNIK (Prawo XIX/XXI):
  Strategia = nazwana kolekcja neuronów WSKAZANYCH PRZEZ KLUCZ (X-01, XII-04...).
  Każdy klucz MUSI istnieć w kodzie (rejestr.wszystkie_neurony). Strażnik spójności
  (audyt Warstwa 4) pilnuje, że strategia nigdy nie wskazuje neuronu-widma.

Strategia NIE liczy matematyki (Prawo I) — tylko zbiera gotowe sygnały neuronów
i ocenia, jak dobrze pasują do jej przepisu.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Role neuronu w strategii (przepis tradera)
ROLA_WEJSCIE = "WEJSCIE"   # sygnały wyzwalają wejście — powinny być zgodne
ROLA_FILTR = "FILTR"       # muszą potwierdzić przed wejściem
ROLA_WYJSCIE = "WYJSCIE"   # sygnały wyzwalają wyjście


@dataclass
class Strategia:
    """
    Przepis: które neurony, w jakiej roli. Klucze MUSZĄ istnieć w kodzie (Klucznik).
    Pola zgodne z docs/KATALOG_STRATEGII.md (format strategii).
    """
    id: str                       # np. "X-SC-001"
    nazwa: str                    # poetycka nazwa Imperium
    legion: str                   # X / XII / III / VI / IMV
    styl: str                     # TR/RV/BK/RG/SC/MC/LV/HY
    warunki: str                  # gdzie działa najlepiej (opis reżimu)
    neurony_wejscie: List[str] = field(default_factory=list)
    neurony_filtr: List[str] = field(default_factory=list)
    neurony_wyjscie: List[str] = field(default_factory=list)
    interwaly: List[str] = field(default_factory=list)
    rezim_preferowany: str = "NORMAL"   # reżim, w którym strategia ma sens
    dzwignia: str = "1×"
    rr: str = "1:2"
    status: str = "SZKIC"         # SZKIC/TESTOWANA/AKTYWNA/EMERYTOWANA
    zrodlo: str = ""              # twórca / koncepcja źródłowa

    def wszystkie_klucze(self) -> set:
        """Wszystkie klucze neuronów użyte w strategii (do kontroli spójności)."""
        return set(self.neurony_wejscie) | set(self.neurony_filtr) | set(self.neurony_wyjscie)


@dataclass
class DopasowanieStrategii:
    """Wynik oceny, jak strategia pasuje do bieżących sygnałów neuronów."""
    strategia: Strategia
    kierunek: str                 # LONG / SHORT / NEUTRAL
    wynik: float                  # 0.0–1.0 — jak dobrze pasuje TERAZ
    zgodnych_wejsc: int
    potwierdzen_filtr: int
    aktywnych_kluczy: int         # ile kluczy strategii dostało sygnał
    powody: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (f"[{self.strategia.id}] {self.strategia.nazwa} → {self.kierunek} "
                f"(dopasowanie {self.wynik:.0%}, wejść {self.zgodnych_wejsc}, "
                f"filtr {self.potwierdzen_filtr})")


def _kierunek_i_sila(klucze: List[str], sygnaly: Dict[str, object]) -> tuple:
    """
    Z listy kluczy i mapy sygnałów liczy dominujący kierunek + jego siłę.
    sygnaly: {neuron_id: SygnalNeuronu} (duck-typing: .kierunek, .pewnosc_finalna).
    Zwraca (kierunek, sila_long, sila_short, n_long, n_short, n_aktywnych).
    """
    sila_l = sila_s = 0.0
    n_l = n_s = n_akt = 0
    for k in klucze:
        s = sygnaly.get(k)
        if s is None:
            continue
        n_akt += 1
        if s.kierunek == "LONG":
            sila_l += s.pewnosc_finalna
            n_l += 1
        elif s.kierunek == "SHORT":
            sila_s += s.pewnosc_finalna
            n_s += 1
    kierunek = "NEUTRAL"
    if sila_l > sila_s and n_l > 0:
        kierunek = "LONG"
    elif sila_s > sila_l and n_s > 0:
        kierunek = "SHORT"
    return kierunek, sila_l, sila_s, n_l, n_s, n_akt


def dopasuj_strategie(strategia: Strategia, sygnaly: Dict[str, object],
                      rezim: str = "NORMAL") -> DopasowanieStrategii:
    """
    Ocenia, jak strategia pasuje do bieżących sygnałów neuronów.

    Wynik = (zgodność wejść) × (potwierdzenie filtrów) × (bonus reżimu).
    Strategia "pasuje" gdy jej neurony WEJŚCIA są zgodne kierunkowo, a FILTRY potwierdzają.
    Neurony nieobecne w sygnałach (np. wyciszone) są pomijane — nie karzą strategii.
    """
    powody = []

    # 1) Kierunek z neuronów WEJŚCIA
    kier, sl, ss, n_l, n_s, n_akt_we = _kierunek_i_sila(strategia.neurony_wejscie, sygnaly)
    if n_akt_we == 0 or kier == "NEUTRAL":
        return DopasowanieStrategii(
            strategia=strategia, kierunek="NEUTRAL", wynik=0.0,
            zgodnych_wejsc=0, potwierdzen_filtr=0, aktywnych_kluczy=n_akt_we,
            powody=[f"Brak zgodnego sygnału wejścia ({strategia.id})"],
        )
    zgodnych = n_l if kier == "LONG" else n_s
    # frakcja zgodnych względem aktywnych wejść (nie karzemy za wyciszone)
    zgodnosc_wejsc = zgodnych / n_akt_we
    powody.append(f"Wejście: {zgodnych}/{n_akt_we} aktywnych zgodnych na {kier}")

    # 2) Potwierdzenie FILTRÓW (muszą iść w tym samym kierunku)
    kier_f, _, _, fn_l, fn_s, n_akt_f = _kierunek_i_sila(strategia.neurony_filtr, sygnaly)
    potwierdzen = (fn_l if kier == "LONG" else fn_s)
    if strategia.neurony_filtr and n_akt_f:
        filtr_frakcja = potwierdzen / n_akt_f
        powody.append(f"Filtr: {potwierdzen}/{n_akt_f} potwierdza {kier}")
    else:
        # Brak filtrów LUB wszystkie wyciszone → brak warunku.
        # Prawo XV: nieobecny sygnał NIE karze strategii (filtr_frakcja=1.0).
        filtr_frakcja = 1.0
        if strategia.neurony_filtr:
            powody.append("Filtr: wszystkie wyciszone — neutralnie (bez kary)")

    # 3) Bonus reżimu — strategia w swoim żywiole
    bonus_rezim = 1.0
    if strategia.rezim_preferowany != "NORMAL":
        bonus_rezim = 1.15 if rezim == strategia.rezim_preferowany else 0.85
        powody.append(f"Reżim {rezim} vs preferowany {strategia.rezim_preferowany} → ×{bonus_rezim}")

    # Wynik łączny (0–1)
    wynik = min(1.0, zgodnosc_wejsc * (0.5 + 0.5 * filtr_frakcja) * bonus_rezim)

    return DopasowanieStrategii(
        strategia=strategia, kierunek=kier, wynik=round(wynik, 4),
        zgodnych_wejsc=zgodnych, potwierdzen_filtr=potwierdzen,
        aktywnych_kluczy=n_akt_we + n_akt_f, powody=powody,
    )


def _normalizuj_interwal(s: str) -> str:
    """Normalizuje format interwału: '5m'→'M5', '1h'→'1H', 'M5'→'M5' itp.
    Obsługuje oba konwencje: 'M5'/'M15' (strategie) i '5m'/'15m' (czytnik CSV).
    """
    s = s.strip().upper()
    # Już w formacie 'M5', '4H', '1D' — zostawiamy
    if s and not s[0].isdigit():
        return s
    # Format liczbowy '5M' → 'M5', '15M' → 'M15', '4H' → '4H'
    for suffix in ('M', 'H', 'D', 'W'):
        if s.endswith(suffix):
            num = s[:-1]
            return suffix + num
    return s


def _interwal_pasuje(strategia: Strategia, interwal: Optional[str]) -> bool:
    """
    Czy strategia jest przeznaczona na ten interwał? (Prawo XV — ożywia martwe
    metadane: pole interwaly było ignorowane przez selekcję).
    Pusta lista interwaly = strategia uniwersalna (pasuje zawsze).
    Brak interwału na wejściu = nie filtrujemy.
    """
    if not interwal or not strategia.interwaly:
        return True
    cel = _normalizuj_interwal(interwal)
    return any(cel == _normalizuj_interwal(i) for i in strategia.interwaly)


def dobierz_najlepsze(strategie: List[Strategia], sygnaly: Dict[str, object],
                      rezim: str = "NORMAL", top: int = 3,
                      min_wynik: float = 0.3,
                      interwal: Optional[str] = None) -> List[DopasowanieStrategii]:
    """
    Serce wizji: z całej bazy strategii wybiera TOP najlepiej pasujące
    do bieżących sygnałów neuronów. Pomija dopasowania poniżej min_wynik.

    interwal: gdy podany, odfiltrowuje strategie nieprzeznaczone na ten timeframe
              (Timeframe-Aware: scalp M5 nie konkuruje ze swingiem 1D). Prawo XV.
    """
    kandydaci = [s for s in strategie if _interwal_pasuje(s, interwal)]
    wyniki = [dopasuj_strategie(s, sygnaly, rezim) for s in kandydaci]
    wyniki = [d for d in wyniki if d.wynik >= min_wynik and d.kierunek != "NEUTRAL"]
    wyniki.sort(key=lambda d: d.wynik, reverse=True)
    return wyniki[:top]
