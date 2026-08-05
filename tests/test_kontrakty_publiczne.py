"""Kontrakt między organami musi być PUBLICZNY — lek na KLASĘ, nie na instancję.

POWÓD (recenzja 2026-08-05): `conditor_lustri` importował z `maturitas` prywatną funkcję
`_stan_domkniety`. Zmiana nazwy w cudzym module dałaby `ImportError`, a ten wpada w `except`
w `zmierz()` i zamienia kryterium ETAPY w ciche `NIE WIEM` — awaria przebrana za niewiedzę.
Naprawa samego CONDITORA byłaby naprawą INSTANCJI; lekcja tej samej wachty mówi wprost, że
**wzorzec przeżywa naprawę instancji** (naprawiłem bezpiecznik, który nie mógł się zapalić,
i tego samego dnia zbudowałem drugi taki sam oraz jego lustrzane odbicie).

Ten test jest lekiem na wzorzec: **nowy import prywatnej nazwy z cudzego modułu zapala
czerwień**. Podkreślnik jest deklaracją „to moje wnętrze, może zniknąć bez ostrzeżenia" —
kto na nim buduje, bierze zakład o cudzy refaktor.

DŁUG ZNANY, NIE UKRYTY: `ZNANY_DLUG` niżej to lista miejsc, które łamały tę zasadę zanim
została nazwana (zmierzone: 16 plików). Nie naprawiamy ich hurtem w wachcie o czym innym —
naprawa dotyka cudzych API i wymaga własnych testów. Lista ma **maleć, nigdy rosnąć**, i
pilnują tego OBA testy niżej: nowy grzech = czerwień, spłacony dług usunięty z listy = też
czerwień (inaczej lista zgniłaby jak każda ręcznie pisana liczba).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KORZEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KORZENIE = ("imperium", "narzedzia")

# Miejsca łamiące zasadę PRZED jej nazwaniem (2026-08-05). Każdy wiersz to dług do spłaty.
ZNANY_DLUG = {
    "imperium/akwedukty/adaptery/news_llm.py",      # _normalizuj z news_fetcher
    "imperium/biblioteki/pamiec_sesji.py",          # _stopien_w_grafie z zapominanie
    "imperium/biblioteki/zapominanie.py",           # _importance, _recency z centrum_pamieci
    "imperium/legiony/radar_rynku.py",              # _ema z radar_btc
    "narzedzia/ab_dvol.py",                         # _pobierz_dvol, _dzien z pomiar_dvol_ic
    "narzedzia/ab_plon_hyginusa.py",                # _KONTRA_SUFIKS, _topk_arg z bibliotekarz
    "narzedzia/pomiar_dvol_ic.py",                  # _spearman z metryki_ic
    "narzedzia/pomiar_funding_ic.py",               # _spearman, _df_do_barow
    "narzedzia/pomiar_haruspex.py",                 # _df_do_barow z petla_live
    "narzedzia/pomiar_nowe_moduly.py",              # _spearman z metryki_ic
    "narzedzia/pomiar_stablecoin_ic.py",            # _spearman z metryki_ic
    "narzedzia/pomiar_usd_ic.py",                   # _spearman z metryki_ic
    "narzedzia/rag/konwerter.py",                   # _faber z ekstraktor
}

_IMPORT = re.compile(r"^\s*from\s+([\w\.]+)\s+import\s+(.+?)(?:\s*#.*)?$")


def _prywatne_importy() -> dict:
    """{ścieżka względna: [zaimportowane prywatne nazwy]} — skan żywego kodu."""
    out: dict = {}
    for korzen in KORZENIE:
        for biezacy, katalogi, pliki in os.walk(os.path.join(KORZEN, korzen)):
            katalogi[:] = [k for k in katalogi if k not in {"__pycache__", ".pytest_cache"}]
            for plik in pliki:
                if not plik.endswith(".py"):
                    continue
                pelna = os.path.join(biezacy, plik)
                wzgledna = os.path.relpath(pelna, KORZEN).replace(os.sep, "/")
                with open(pelna, encoding="utf-8", errors="replace") as f:
                    tekst = f.read()
                grzechy = []
                for linia in tekst.splitlines():
                    m = _IMPORT.match(linia)
                    if not m or m.group(1) == "__future__":
                        continue
                    for symbol in m.group(2).replace("(", "").replace(")", "").split(","):
                        nazwa = symbol.strip().split(" as ")[0].strip()
                        # `__dunder__` to protokół języka, nie cudze wnętrze.
                        if nazwa.startswith("_") and not nazwa.startswith("__"):
                            grzechy.append(f"{nazwa} ← {m.group(1)}")
                if grzechy:
                    out[wzgledna] = grzechy
    return out


def test_zaden_NOWY_modul_nie_importuje_prywatnej_nazwy():
    """GRANICA: podkreślnik znaczy „wnętrze" — kto na nim buduje, bierze zakład o cudzy refaktor.

    Ten test jest lekiem na KLASĘ wady, nie na jej pojedynczy przypadek: naprawa CONDITORA
    zamknęła jedną instancję, ten test zamyka drogę powrotu wszystkim następnym.
    """
    znalezione = _prywatne_importy()
    nowe = {p: g for p, g in znalezione.items() if p not in ZNANY_DLUG}
    assert not nowe, (
        "import prywatnej nazwy z cudzego modułu (zmiana nazwy u sąsiada = awaria u ciebie):\n"
        + "\n".join(f"  {p}: {', '.join(g)}" for p, g in sorted(nowe.items()))
        + "\n→ poproś producenta o PUBLICZNE API albo skopiuj logikę z powodem w komentarzu"
    )


def test_lista_dlugu_nie_zawiera_juz_splaconych():
    """Lista ręczna GNIJE, jeśli nikt nie pilnuje jej z drugiej strony.

    Spłacony dług musi zniknąć z `ZNANY_DLUG` — inaczej za miesiąc nie da się odróżnić
    długu od pamiątki, a to jest dokładnie klasa „liczba, która przestała odpowiadać kodowi".
    """
    znalezione = set(_prywatne_importy())
    zombie = sorted(ZNANY_DLUG - znalezione)
    assert not zombie, (
        f"te pliki już NIE importują prywatnych nazw — usuń je z ZNANY_DLUG: {zombie}"
    )


def test_conditor_splacil_swoj_dlug():
    """Instancja, od której zaczęła się ta klasa — nie może wrócić na listę."""
    assert "imperium/pretorianie/conditor_lustri.py" not in _prywatne_importy()
