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


_RAPORTY = {"hma": _raport_hma, "aequitas": _raport_aequitas}

if __name__ == "__main__":
    nazwa = sys.argv[1] if len(sys.argv) > 1 else "hma"
    if nazwa not in _RAPORTY:
        raise SystemExit(f"Nieznany raport '{nazwa}'. Dostępne: {sorted(_RAPORTY)}")
    p = _RAPORTY[nazwa]()
    print(f"🏛️ Podgląd Kapitolu zapisany: {p}")
    print(f"   Link: {p.as_uri()}")
