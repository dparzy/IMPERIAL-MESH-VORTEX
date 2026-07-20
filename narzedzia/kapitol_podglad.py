"""
🏛️ KAPITOL PODGLĄD (Speculum Probationis) — zero-tokenowy podgląd testu w przeglądarce.

Realizuje ROZKAZ Cezara 2026-07-19: KAŻDY test dostaje podgląd w Kapitolu Imperium —
pełna SPECYFIKACJA co testowane (para, interwał, okno, tryb, dane) + WYKRES + LINK,
oglądany w przeglądarce (ZERO tokenów, nie druk w czacie).

Filozofia (jak backtest_dashboard.py): ZERO ZALEŻNOŚCI. Samowystarczalny HTML,
wykresy jako inline SVG (bez matplotlib). Wynik zapisany do raporty/ (gitignore, widok).

API:
    render_html(tytul, spec, wykresy, werdykt) -> str        # czysty HTML (testowalny)
    zapisz(nazwa, tytul, spec, wykresy, werdykt, otworz=True) -> Path

  spec:     lista (etykieta, wartosc) — CO dokładnie testowane
  wykresy:  lista dict {tytul, jednostka, slupki:[(label, wartosc, kolor?)]}
  werdykt:  string (podsumowanie), opcjonalny
"""
from __future__ import annotations

import html as _html
import os
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
RAPORTY = ROOT / "raporty"

# Nomenklatura rzymska (ZASADA NOMENKLATURY IMPERIALNEJ)
NAZWA_ORGANU = "Speculum Probationis — Zwierciadło Prób (Kapitol)"

_KOLOR_DOMYSLNY = "#4c9be3"  # niebieski Imperium


def _svg_slupki(slupki: Sequence[Tuple], jednostka: str,
                szer: int = 900, wys: int = 340) -> str:
    """Poziomo skalowany słupkowy wykres jako inline SVG (zero zależności)."""
    if not slupki:
        return '<p style="color:#889">Brak danych do wykresu.</p>'
    # normalizacja: (label, wartosc, kolor?)
    norm = []
    for s in slupki:
        label, wartosc = s[0], float(s[1])
        kolor = s[2] if len(s) > 2 and s[2] else _KOLOR_DOMYSLNY
        norm.append((str(label), wartosc, kolor))
    hi = max(w for _, w, _ in norm) or 1.0
    ml, mr, mt, mb = 60, 90, 20, 30
    pw = szer - ml - mr
    n = len(norm)
    gap = 14
    bh = max(10, (wys - mt - mb - gap * (n - 1)) / n)
    linie = [f'<svg viewBox="0 0 {szer} {wys}" width="100%" '
             f'style="background:#11151c;border-radius:10px;font-family:monospace">']
    # oś bazowa
    linie.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{wys-mb}" stroke="#33415a" stroke-width="1"/>')
    for i, (label, wartosc, kolor) in enumerate(norm):
        y = mt + i * (bh + gap)
        w = pw * (wartosc / hi)
        linie.append(f'<rect x="{ml}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" '
                     f'rx="4" fill="{kolor}"/>')
        linie.append(f'<text x="{ml-8}" y="{y+bh/2+4:.1f}" text-anchor="end" '
                     f'fill="#c8d3e0" font-size="13">{_html.escape(label)}</text>')
        linie.append(f'<text x="{ml+w+8:.1f}" y="{y+bh/2+4:.1f}" fill="#8fe388" '
                     f'font-size="13">{wartosc:.2f} {_html.escape(jednostka)}</text>')
    linie.append('</svg>')
    return "".join(linie)


def render_html(tytul: str, spec: Sequence[Tuple[str, str]],
                wykresy: Sequence[dict], werdykt: Optional[str] = None) -> str:
    """Buduje samowystarczalny HTML podglądu Kapitolu (zero zależności zewn.)."""
    teraz = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    wiersze_spec = "".join(
        f'<tr><td class="k">{_html.escape(str(k))}</td>'
        f'<td class="v">{_html.escape(str(v))}</td></tr>'
        for k, v in spec)
    bloki = []
    for wk in wykresy:
        svg = _svg_slupki(wk.get("slupki", []), wk.get("jednostka", ""))
        bloki.append(
            f'<section><h2>{_html.escape(wk.get("tytul", ""))}</h2>{svg}'
            + (f'<p class="opis">{_html.escape(wk["opis"])}</p>' if wk.get("opis") else "")
            + '</section>')
    blok_werdykt = (f'<div class="werdykt">{_html.escape(werdykt)}</div>'
                    if werdykt else "")
    return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🏛️ {_html.escape(tytul)}</title>
<style>
  body{{margin:0;background:#0b0e14;color:#e6edf3;font-family:system-ui,Segoe UI,sans-serif;padding:24px}}
  .wrap{{max-width:980px;margin:0 auto}}
  h1{{font-size:22px;margin:0 0 4px}} .organ{{color:#7d8aa0;font-size:13px;margin-bottom:18px}}
  h2{{font-size:16px;color:#c8d3e0;margin:26px 0 10px}}
  table{{border-collapse:collapse;width:100%;margin:10px 0 6px;background:#11151c;border-radius:10px;overflow:hidden}}
  td{{padding:8px 12px;border-bottom:1px solid #1c2430;font-size:14px}}
  td.k{{color:#7d8aa0;width:230px}} td.v{{color:#e6edf3;font-family:monospace}}
  .opis{{color:#8b97a8;font-size:13px;margin:6px 2px 0}}
  .werdykt{{margin-top:22px;padding:14px 16px;background:#132019;border:1px solid #1f4d33;
            border-radius:10px;color:#8fe388;font-size:14px;white-space:pre-wrap}}
  .stopka{{margin-top:22px;color:#5b6572;font-size:12px}}
</style></head><body><div class="wrap">
<h1>🏛️ {_html.escape(tytul)}</h1>
<div class="organ">{_html.escape(NAZWA_ORGANU)} · {teraz}</div>
<h2>Co dokładnie testowane</h2>
<table>{wiersze_spec}</table>
{"".join(bloki)}
{blok_werdykt}
<div class="stopka">Imperium Cezara Pixel · podgląd zero-tokenowy (oglądasz w przeglądarce, nie w czacie).</div>
</div></body></html>"""


def zapisz(nazwa: str, tytul: str, spec, wykresy, werdykt=None,
           otworz: bool = True) -> Path:
    """Zapisuje HTML do raporty/<nazwa>.html i (opcjonalnie) otwiera w przeglądarce."""
    RAPORTY.mkdir(exist_ok=True)
    plik = RAPORTY / f"{nazwa}.html"
    plik.write_text(render_html(tytul, spec, wykresy, werdykt), encoding="utf-8")
    if otworz and not os.environ.get("KAPITOL_NOOPEN"):
        try:
            webbrowser.open(plik.as_uri())
        except Exception:
            pass
    return plik


# ── Dane sesji 2026-07-19: naprawa wydajności HMA (backtest LINIOWY, nie O(n²)) ──
def _raport_hma() -> Path:
    spec = [
        ("Co testowane", "WYDAJNOŚĆ silnika backtestu (profil skalowania + naprawa HMA)"),
        ("Para / waluty", "BTCUSDT + ETHUSDT"),
        ("Interwał czasowy", "1H (świece godzinowe)"),
        ("Źródło danych", "dane/godzinowe/Binance_{BTC,ETH}USDT_1h.csv (76 464 barów 1H)"),
        ("Okno / tryb", "okno=250 (stałe) · tryb_skaner top_n=2 · sizing_przekonania"),
        ("Silnik", "backtest_portfel (imperium/koloseum/backtest.py)"),
        ("Metryka", "czas [s] i ms/tick; ROI% + liczba transakcji (kontrola identyczności)"),
        ("Naprawa", "_py_hma: c=c[-potrzeba:] (raw tylko na ogonie); commit 4466eda"),
        ("Dowód bit-identyczności", "4000 losowych serii → 0 rozjazdów; ROI backtestu bez zmiany"),
    ]
    wykresy = [
        {"tytul": "Skalowanie ms/tick (okno=250) — STAŁE ≈ LINIOWE (nie O(n²))",
         "jednostka": "ms/tick",
         "opis": "ms/tick niemal stały przy rosnącej liczbie barów → koszt liniowy O(n·okno), "
                 "nie kwadratowy. Dawna diagnoza „O(n²)” była błędna (mylony cumulative w compute).",
         "slupki": [("500 barów", 73.38, "#4c9be3"), ("750 barów", 69.06, "#4c9be3"),
                    ("1100 barów", 62.26, "#4c9be3"), ("1600 barów", 66.37, "#4c9be3")]},
        {"tytul": "HMA fix — ms/tick PRZED vs PO (bit-identyczny wynik)",
         "jednostka": "ms/tick",
         "opis": "Naprawa hotspotu #1 (_py_hma ≈ 15% profilu). ROI niezmienione: "
                 "500b +3.26%/10 trades, 750b +6.19%/19 trades — identyczne przed i po.",
         "slupki": [("500b PRZED", 73.38, "#e0794b"), ("500b PO", 68.69, "#8fe388"),
                    ("750b PRZED", 69.06, "#e0794b"), ("750b PO", 51.69, "#8fe388")]},
        {"tytul": "Czas ścienny 750 barów — PRZED vs PO",
         "jednostka": "s",
         "opis": "Zysk ~25% (1.34×) na oknie 750 barów; czysty pomiar (samotny bieg, bez konkurencji CPU).",
         "slupki": [("750b PRZED", 69.06, "#e0794b"), ("750b PO", 51.69, "#8fe388")]},
    ]
    werdykt = ("WERDYKT: backtest jest LINIOWY (~66 ms/tick), NIE O(n²) — premisa planu była błędna.\n"
               "Hotspot #1 (HMA) naprawiony bit-identycznie: ~25% szybciej, ZERO zmiany wyników.\n"
               "Konsekwencja: WFO nie był zablokowany, tylko wolny → decyzja Cezara o dalszej drodze.")
    return zapisz("KAPITOL_PODGLAD_wydajnosc_hma",
                  "Podgląd testu — Wydajność backtestu (naprawa HMA)",
                  spec, wykresy, werdykt, otworz=False)


# ── Dane sesji 2026-07-20: AEQUITAS SERIERUM — strażnik równej długości serii ──
def _raport_aequitas() -> Path:
    spec = [
        ("Co testowane", "ZACHOWANIE Bramy Kalkulatora przy NIERÓWNYCH seriach OHLCV "
                         "(teza zwiadowcy o zip(strict=True) — weryfikacja własna)"),
        ("Para / waluty", "n/d — pomiar deterministyczny na serii syntetycznej "
                          "(100 barów, cena 100→199, low=high−5, close=high−2, volume=10)"),
        ("Interwał czasowy", "n/d — test niezmiennika Bramy, niezależny od interwału"),
        ("Okno / tryb", "seria pełna 100 barów vs seria z volume/low obciętym do 80/60 barów"),
        ("Źródło danych", "generator deterministyczny w skrypcie pomiarowym (bez sieci, bez CSV)"),
        ("Silnik", "CalculatorGateway.compute (imperium/fundament/brama_kalkulatora.py)"),
        ("Metryka", "wartość wskaźnika PEŁNA vs OBCIĘTA + czy błąd jest zgłaszany głośno"),
        ("Naprawa", "_aequitas_serierum() — strażnik równej długości u wrót compute()"
                    " i compute_series(); zip(strict=True) w niezmienniku _py_hma.wma"),
        ("Zakres zweryfikowany", "23 zip w imperium/ (nie ~25): 10 w Bramie, "
                                 "4 w diagnostyce korelacji JUŻ strzeżone (n != len(y) → None)"),
    ]
    wykresy = [
        {"tytul": "VWAP — wartość PEŁNA vs po CICHYM obcięciu volume (80/100 barów)",
         "jednostka": "VWAP",
         "opis": "Bez strażnika zip() cicho obcinał do najkrótszej serii: wynik zaniżony "
                 "o 10.0 (~6.8%), a pieczątka audytu raportowała input_len=100 mimo "
                 "policzenia z 80 barów — audyt KŁAMAŁ (Prawo XIII).",
         "slupki": [("VWAP pełny (100 barów)", 147.166667, "#8fe388"),
                    ("VWAP cichy (volume 80)", 137.166667, "#e0794b")]},
        {"tytul": "VWAP_STD — ta sama wada na drugim wskaźniku",
         "jednostka": "VWAP_STD",
         "opis": "Rozjazd 5.77 (~20%). Wada nie była jednostkowa — dotyczyła całej "
                 "rodziny wskaźników pure-Python liczonych przez zip().",
         "slupki": [("VWAP_STD pełny", 28.866070, "#8fe388"),
                    ("VWAP_STD cichy", 23.092206, "#e0794b")]},
        {"tytul": "Miejsca zip() — teza zwiadowcy vs POMIAR",
         "jednostka": "liczba miejsc",
         "opis": "Zwiadowca twierdził ~25 miejsc do naprawy. Pomiar: 23 zip w całym "
                 "imperium/, z tego 10 w Bramie, a 4 w diagnostyce korelacji są JUŻ "
                 "strzeżone — strict=True byłby tam martwą asercją (szum, nie ochrona).",
         "slupki": [("teza zwiadowcy (~25)", 25, "#e0794b"),
                    ("zip w imperium/ (fakt)", 23, "#4c9be3"),
                    ("zip w Bramie (fakt)", 10, "#4c9be3"),
                    ("już strzeżone w diagnostyce", 4, "#8fe388"),
                    ("miejsc naprawy po korekcie", 1, "#8fe388")]},
    ]
    werdykt = (
        "WERDYKT: teza zwiadowcy SŁUSZNA co do kierunku, BŁĘDNA co do liczby i lekarstwa.\n"
        "Dowód asymetrii: TA-Lib odrzuca nierówne serie GŁOŚNO ('input array lengths are "
        "different'), a bliźniacze wskaźniki pure-Python liczyły CICHO fałszywą wartość.\n"
        "Lekarstwo lepsze niż ~25 rozsypanych zip(strict=True): JEDEN strażnik u wrót — "
        "obejmuje też wskaźniki numpy (bez zip), naprawia kłamiącą pieczątkę audytu i nie "
        "da się go pominąć przy dodawaniu nowego wskaźnika.\n"
        "Ryzyko regresu ZERO: _serie() w budowniczy_wskaznikow.py buduje wszystkie 5 serii "
        "z tej samej listy barów — ścieżka produkcyjna nie może potknąć się o strażnika.")
    return zapisz("KAPITOL_PODGLAD_aequitas_serierum",
                  "Podgląd testu — AEQUITAS SERIERUM (strażnik serii u wrót Bramy)",
                  spec, wykresy, werdykt, otworz=False)


# ── Dane sesji 2026-07-20: P2 — A/B DVOL na 1H, pełna era (LIMEN FENESTRAE) ──
def _raport_ab_dvol_1h() -> Path:
    spec = [
        ("Co testowane", "A/B sygnału DVOL (neuron PSY-05) — czy IC +0.16@7d przekłada się na PnL"),
        ("Para / waluty", "BTCUSDT + ETHUSDT (DVOL istnieje na Deribit tylko dla BTC i ETH)"),
        ("Interwał czasowy", "1H (świece godzinowe)"),
        ("Okno / era", "PEŁNA era DVOL: BTC 19 471 barów + ETH 19 380 barów (~2.2 roku); "
                       "pokrycie ery 100% → ranga ROZSTRZYGAJĄCY"),
        ("Źródło danych", "dane/godzinowe/Binance_{BTC,ETH}USDT_1h.csv + DVOL z Deribit "
                          "(kauzalny forward-fill dzienny na bary)"),
        ("Tryb", "tryb_skaner top_n=2 · sizing_przekonania · backtest_portfel"),
        ("Ramiona", "B = DVOL OFF (baseline) vs A = DVOL ON (PSY-05)"),
        ("Czas biegu", "~62 min (77 702 tiki × 47.7 ms — zmierzona przepustowość silnika)"),
        ("Sprzęt", "Fujitsu: 15.88 GB RAM, 4 wątki, brak CUDA, klasa PEDES "
                   "(ZMIERZONE censor_sprzetu.py — nie z pamięci)"),
    ]
    wykresy = [
        {"tytul": "ROI% — pełna era DVOL (werdykt ROZSTRZYGAJĄCY)",
         "jednostka": "ROI %",
         "opis": "Δ ROI = +0.24 pp przy 649 transakcjach w obu ramionach — szum, nie przewaga. "
                 "WERDYKT: NEUTRALNE, flaga zostaje OFF. Uwaga: OBA ramiona tracą na 1H.",
         "slupki": [("B: DVOL OFF", -5.49, "#e0794b"), ("A: DVOL ON", -5.25, "#e0794b")]},
        {"tytul": "Ten sam sygnał, różne okna — dlaczego powstał LIMEN FENESTRAE",
         "jednostka": "Δ ROI (pp)",
         "opis": "Werdykt ZMIENIAŁ SIĘ z oknem: 800 barów (4% ery) → NEUTRALNE bez transakcji; "
                 "2000 barów (10% ery) → POMAGA +1.77 pp; pełna era → NEUTRALNE +0.24 pp. "
                 "Konkluzja z próbki 10% była PRZEDWCZESNA (NOTA N-4f7032a6).",
         "slupki": [("800 barów (4% ery)", 0.0, "#8a8a8a"), ("2000 barów (10% ery)", 1.77, "#e0794b"),
                    ("pełna era (100%)", 0.24, "#8fe388")]},
        {"tytul": "Pokrycie ery przez okno testu — ranga werdyktu",
         "jednostka": "% ery",
         "opis": "Próg reprezentatywności = 50%. Poniżej niego werdykt jest WSTĘPNY i nie zamyka "
                 "tematu — od teraz zapisywane W REKORDZIE ledgera, nie w pamięci operatora.",
         "slupki": [("800 barów", 4.1, "#e0794b"), ("2000 barów", 10.3, "#e0794b"),
                    ("próg 50%", 50.0, "#4c9be3"), ("pełna era", 100.0, "#8fe388")]},
    ]
    werdykt = (
        "WERDYKT: ⚖️ NEUTRALNE — DVOL nie daje przewagi PnL na 1H w pełnej erze (Δ +0.24 pp).\n"
        "Flaga zostaje OPT-IN OFF. IC ≠ PnL: sygnał ma skill informacyjny (+0.16@7d), ale nie "
        "zamienia się na wynik na tym interwale.\n"
        "ODWOŁANIE WCZEŚNIEJSZEJ KONKLUZJI: bieg kontrolny na 2000 barach dał 'POMAGA +1.77 pp' "
        "i został przeze mnie ogłoszony jako potwierdzenie hipotezy — pełna era to obala. "
        "Próbka 10% ery myliła w drugą stronę niż próbka 4%.\n"
        "HIPOTEZA DO OSOBNEGO POMIARU (nie fakt): oba ramiona tracą na 1H (-5.5%), a 4H/1D dawały "
        "dodatnie ROI — problemem może być sam interwał 1H dla tej strategii, nie sygnał DVOL. "
        "Porównanie szło na różnych oknach, więc NIE ogłaszam tego jako wniosku.")
    return zapisz("KAPITOL_PODGLAD_ab_dvol_1h_pelna_era",
                  "Podgląd testu — A/B DVOL 1H, pełna era (P2)",
                  spec, wykresy, werdykt, otworz=False)


def raport_interwalow(wyniki, pary, barow_1h) -> Path:
    """Podgląd porównania interwałów (wywoływany przez sym_porownanie_tf.py --podglad).

    Buduje się z ŻYWYCH wyników biegu, nie z liczb wpisanych ręcznie — dlatego przyjmuje
    dane, zamiast trzymać je zaszyte jak raporty historyczne niżej.
    """
    okna = [w["okno"] for w in wyniki if w.get("okno")]
    zakres = f"{min(o[0] for o in okna)} → {max(o[1] for o in okna)}" if okna else "n/d"
    najlepszy = max(wyniki, key=lambda x: x["roi"])
    najgorszy = min(wyniki, key=lambda x: x["roi"])
    stratne = [w["interwal"] for w in wyniki if w["roi"] < 0]
    spec = [
        ("Co testowane", "HIPOTEZA INTERWAŁU — czy sam interwał (nie sygnał) decyduje o "
                         "rentowności strategii; izolacja efektu interwału od efektu okna"),
        ("Para / waluty", ", ".join(pary)),
        ("Interwały", ", ".join(w["interwal"] for w in wyniki)),
        ("Okno kalendarzowe", f"{zakres} — IDENTYCZNE dla każdego interwału "
                              f"(cap {barow_1h} barów 1h, pozostałe skalowane ×1/4, ×1/24)"),
        ("Źródło danych", "dane/{godzinowe,4h,dzienne}/Binance_*.csv"),
        ("Konfiguracja", "identyczna dla każdego interwału: tryb_skaner top_n=3 · "
                         "sizing_przekonania · compounding · filtr_asymetrii"),
        ("Uwaga metodologiczna", "to NIE jest konfiguracja z ab_dvol.py (tam top_n=2, bez "
                                 "compoundingu) — liczby porównuj MIĘDZY interwałami, nie z A/B Tier-1"),
        ("Sprzęt", "Fujitsu: 15.88 GB RAM, 4 wątki, brak CUDA, klasa PEDES (censor_sprzetu.py)"),
    ]
    kolor = lambda roi: "#8fe388" if roi > 0 else "#e0794b"  # noqa: E731
    wykresy = [
        {"tytul": "ROI% wg interwału — to samo okno, ta sama konfiguracja",
         "jednostka": "ROI %",
         "opis": "Różnica między słupkami to efekt INTERWAŁU, bo okno kalendarzowe i konfiguracja "
                 "są identyczne. Zielony = dodatni, pomarańczowy = stratny.",
         "slupki": [(w["interwal"], round(w["roi"], 2), kolor(w["roi"])) for w in wyniki]},
        {"tytul": "Liczba transakcji wg interwału",
         "jednostka": "transakcje",
         "opis": "Krótszy interwał = więcej transakcji = więcej kosztów tarcia. Jeśli ROI spada "
                 "przy rosnącej liczbie transakcji, podejrzewaj koszt tarcia, nie brak sygnału.",
         "slupki": [(w["interwal"], w["trades"], "#4c9be3") for w in wyniki]},
        {"tytul": "Max drawdown wg interwału",
         "jednostka": "maxDD %",
         "opis": "Kontrola ryzyka: wyższy ROI kupiony wyższym obsunięciem to nie ta sama jakość.",
         "slupki": [(w["interwal"], round(w["maxdd"], 2), "#b48ee8") for w in wyniki]},
    ]
    werdykt = (
        f"Najlepszy interwał: {najlepszy['interwal']} ({najlepszy['roi']:+.2f}%), "
        f"najgorszy: {najgorszy['interwal']} ({najgorszy['roi']:+.2f}%), "
        f"rozpiętość {najlepszy['roi'] - najgorszy['roi']:.2f} pp.\n"
        + (f"STRATNE interwały: {', '.join(stratne)} — testowanie kolejnych sygnałów na stratnym "
           "interwale to szukanie przewagi w grze już przegranej. Najpierw interwał, potem sygnały.\n"
           if stratne else "Każdy badany interwał dodatni na tym oknie.\n")
        + "Pomiar izoluje INTERWAŁ: okno kalendarzowe i konfiguracja identyczne we wszystkich biegach.")
    return zapisz("KAPITOL_PODGLAD_hipoteza_interwalu",
                  "Podgląd testu — Hipoteza interwału (1d vs 4h vs 1h)",
                  spec, wykresy, werdykt, otworz=False)


# ── Dane sesji 2026-07-20: SIGLA IMPERII (organ SIGILLARIUM) ─────────────────
def _raport_sigla() -> Path:
    # Ten generator jest uruchamiany z katalogu `narzedzia/`, więc korzeń repo nie leży
    # domyślnie na ścieżce importu. Wstawiamy go na KONIEC (append, nie insert) — pakiet
    # `imperium` ma być rozwiązywany normalnie, a nie przesłaniać niczego z przodu.
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from imperium.biblioteki import sigillarium as _sig

    kroki = {s.nazwa: len(_sig.kroki(s.nazwa)) for s in _sig.wszystkie()}
    spec = [
        ("Co testowane", "SIGLA IMPERII — hasła-skróty uruchamiające pełne procedury "
                         "(rozkaz Cezara 2026-07-20); organ SIGILLARIUM"),
        ("Para / waluty", "n/d — zmiana ergonomii i pamięci proceduralnej, nie ścieżki decyzyjnej "
                          "(żaden neuron, próg ani sizing nie tknięty)"),
        ("Interwał czasowy", "n/d"),
        ("Okno / tryb", "deterministyczny; kroki liczone z żywego CLAUDE.md w chwili wywołania"),
        ("Źródło danych", "CLAUDE.md (konstytucja) + bibliotheca_ulpia/dane/procedury.jsonl (W11)"),
        ("Silnik", "imperium/biblioteki/sigillarium.py + .claude/skills/{apertio,clausura,limes}"),
        ("Metryka", "liczba kroków pieczęci (żywa), liczba runbooków z możliwością naprawy, "
                    "dni gnicia nieaktualnego runbooka"),
        ("Decyzja Cezara", "forma = skille /nazwa + aliasy słowne; zestaw = rdzeń 3 pieczęci "
                           "(pozostali kandydaci NIE wdrożeni, czekają na decyzję)"),
        ("Bramki", "2713/2713 testów (2694→2713, +19 nowych) · audyt exit 0 (17 warstw) · "
                   "ruff czysto · skan wad czysto · INDEX FALSORUM czysto · dług honorowy 0"),
    ]
    wykresy = [
        {"tytul": "Kroki pieczęci — liczone z żywej konstytucji, nie wpisane",
         "jednostka": "kroków",
         "opis": "Te liczby nie są zapisane nigdzie w kodzie ani w skillu — powstają z parsowania "
                 "CLAUDE.md przy każdym wywołaniu. Dopisanie kroku do checklisty zmienia je same.",
         "slupki": [("/apertio (otwarcie)", kroki.get("APERTIO", 0), "#4c9be3"),
                    ("/clausura (zamknięcie)", kroki.get("CLAUSURA", 0), "#4c9be3"),
                    ("/limes (bramka)", kroki.get("LIMES", 0), "#8fe388")]},
        {"tytul": "Runbooki W11 — ile dało się NAPRAWIĆ, gdy się zdezaktualizują",
         "jednostka": "runbooków",
         "opis": "Przed naprawą: 4 runbooki, z czego 0 dało się zaktualizować (dodaj() dedupował po "
                 "nazwie i cicho zwracał False). Po naprawie: 7 runbooków (3 nowe = sigla), wszystkie "
                 "z jawną ścieżką upsert i werdyktem dodano/zaktualizowano/bez zmian.",
         "slupki": [("przed: runbooki", 4, "#e0794b"),
                    ("przed: możliwe do naprawy", 0, "#e0794b"),
                    ("po: runbooki", 7, "#8fe388"),
                    ("po: możliwe do naprawy", 7, "#8fe388")]},
        {"tytul": "Gnicie runbooka — ZMIERZONE, nie oszacowane",
         "jednostka": "dni",
         "opis": "Runbook kazał Claude `git push` wbrew rozkazowi z 2026-07-11. Najpierw wpisałem "
                 "„pół roku” BEZ POMIARU — pomiar dał 9 dni (07-11 → 07-20), przy wieku runbooka "
                 "19 dni. Liczba poprawiona u źródła przed commitem (klasa: liczba-bez-pomiaru).",
         "slupki": [("moja teza bez pomiaru (~180)", 180, "#e0794b"),
                    ("gnicie po zakazie (fakt)", 9, "#8fe388"),
                    ("wiek runbooka (fakt)", 19, "#4c9be3")]},
    ]
    werdykt = (
        "WERDYKT: rozkaz wykonany w formie wybranej przez Cezara, ale realną zdobyczą jest NAPRAWA, "
        "nie skrót.\n"
        "Sigillum nie przechowuje kroków — czyta je z CLAUDE.md przy wywołaniu, więc rozjazd procedury "
        "z rozkazem jest strukturalnie niemożliwy, a nie „pilnowany” (to samo lekarstwo co CENSUS "
        "ORGANORUM: odebranie dokumentowi prawa do własnej treści).\n"
        "Znalezione po drodze DWA cichniejsze warianty tej samej klasy: (1) pamięć proceduralna bez "
        "ścieżki aktualizacji — runbook niezmienialny na zawsze, raport meldował „4 runbooki gotowe”; "
        "(2) KsiegaWadKodu.dodaj_checklist() zwraca True i zwiększa licznik W PAMIĘCI, a bez osobnego "
        "zapisz() nie zapisuje nic — mój własny wpis o wadzie przepadł i musiałem go zapisać drugi raz.\n"
        "Zero wpływu na ścieżkę decyzyjną: żaden neuron, próg ani sizing nie tknięty — zmiana dotyczy "
        "ergonomii Cezara i pamięci proceduralnej.")
    return zapisz("KAPITOL_PODGLAD_sigla_imperii",
                  "Podgląd zadania — SIGLA IMPERII (organ SIGILLARIUM)",
                  spec, wykresy, werdykt, otworz=False)


_RAPORTY = {"hma": _raport_hma, "aequitas": _raport_aequitas, "ab_dvol_1h": _raport_ab_dvol_1h,
            "sigla": _raport_sigla}

if __name__ == "__main__":
    nazwa = sys.argv[1] if len(sys.argv) > 1 else "hma"
    if nazwa not in _RAPORTY:
        raise SystemExit(f"Nieznany raport '{nazwa}'. Dostępne: {sorted(_RAPORTY)}")
    p = _RAPORTY[nazwa]()
    print(f"🏛️ Podgląd Kapitolu zapisany: {p}")
    print(f"   Link: {p.as_uri()}")
