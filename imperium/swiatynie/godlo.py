"""
Godło Imperium (W-342) — generator znaku rozpoznawczego.

Tworzy SVG godła: Aquila (orzeł legionowy) + Vortex (wir) + Mesh (sieć neuronów).
Czysty SVG generowany kodem — zero zależności zewnętrznych (Prawo lokalności).

Symbolika:
  • Aquila      — Legiony (rój neuronów pod jednym dowództwem)
  • Vortex      — wir rynku, który Imperium ujarzmia
  • Mesh        — splot neuronów głosujących (siatka węzłów)
  • Złoto/purpura — barwy cesarskie Rzymu

Użycie:
    from imperium.swiatynie.godlo import generuj_godlo, zapisz_godlo
    svg = generuj_godlo()
    zapisz_godlo("docs/godlo_imperium.svg")
"""

import math


# Barwy cesarskie
ZLOTO = "#D4AF37"
ZLOTO_JASNE = "#F0D77B"
PURPURA = "#4A0E2E"
PURPURA_CIEMNA = "#2A0619"
TLO = "#0D0D14"
SREBRO = "#C8CDD6"


def _wir_sciezka(cx: float, cy: float, r_max: float, obroty: float = 2.5,
                 punktow: int = 80) -> str:
    """Spirala logarytmiczna (wir) jako ścieżka SVG."""
    punkty = []
    for i in range(punktow + 1):
        t = i / punktow
        kat = t * obroty * 2 * math.pi
        r = r_max * t
        x = cx + r * math.cos(kat)
        y = cy + r * math.sin(kat)
        punkty.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(punkty)


def _siatka_wezlow(cx: float, cy: float, r: float, wezlow: int = 8) -> str:
    """Pierścień węzłów (neuronów) połączonych liniami — mesh."""
    elementy = []
    pozycje = []
    for i in range(wezlow):
        kat = (i / wezlow) * 2 * math.pi - math.pi / 2
        x = cx + r * math.cos(kat)
        y = cy + r * math.sin(kat)
        pozycje.append((x, y))

    # Połączenia (co drugi węzeł — splot)
    for i in range(wezlow):
        x1, y1 = pozycje[i]
        for j in (1, 2):
            x2, y2 = pozycje[(i + j) % wezlow]
            elementy.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{ZLOTO}" stroke-width="0.8" opacity="0.35"/>'
            )
    # Węzły
    for x, y in pozycje:
        elementy.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{ZLOTO_JASNE}" '
            f'stroke="{PURPURA}" stroke-width="0.8"/>'
        )
    return "\n    ".join(elementy)


def _aquila(cx: float, cy: float, skala: float = 1.0) -> str:
    """Stylizowany orzeł legionowy (uproszczona, rozpoznawalna sylwetka)."""
    s = skala
    # Skrzydła rozłożone + głowa + korpus — geometria symetryczna
    return f'''<g transform="translate({cx},{cy}) scale({s})">
      <!-- lewe skrzydło -->
      <path d="M0,-8 C-18,-20 -38,-16 -50,-4 C-36,-8 -22,-4 -12,2 C-26,0 -40,4 -48,14
               C-34,8 -20,8 -8,10 Z" fill="{ZLOTO}" stroke="{ZLOTO_JASNE}" stroke-width="0.6"/>
      <!-- prawe skrzydło (lustro) -->
      <path d="M0,-8 C18,-20 38,-16 50,-4 C36,-8 22,-4 12,2 C26,0 40,4 48,14
               C34,8 20,8 8,10 Z" fill="{ZLOTO}" stroke="{ZLOTO_JASNE}" stroke-width="0.6"/>
      <!-- korpus -->
      <path d="M0,-14 C-4,-12 -5,-2 -3,12 C-2,20 0,24 0,24 C0,24 2,20 3,12
               C5,-2 4,-12 0,-14 Z" fill="{ZLOTO_JASNE}" stroke="{PURPURA}" stroke-width="0.6"/>
      <!-- głowa -->
      <circle cx="0" cy="-16" r="5" fill="{ZLOTO_JASNE}" stroke="{PURPURA}" stroke-width="0.8"/>
      <!-- dziób -->
      <path d="M4,-17 L11,-15 L4,-13 Z" fill="{ZLOTO}"/>
      <!-- oko -->
      <circle cx="1.5" cy="-17" r="1.1" fill="{PURPURA_CIEMNA}"/>
    </g>'''


def generuj_godlo(rozmiar: int = 240, podpis: bool = True) -> str:
    """
    Zwraca pełny dokument SVG godła Imperium.

    rozmiar: szerokość/wysokość w px (kwadrat)
    podpis: czy dodać napis IMPERIAL MESH VORTEX pod godłem
    """
    cx = rozmiar / 2
    cy = rozmiar / 2 - (10 if podpis else 0)
    r_zewn = rozmiar * 0.42

    wir1 = _wir_sciezka(cx, cy, r_zewn * 0.85, obroty=2.5)
    wir2 = _wir_sciezka(cx, cy, r_zewn * 0.85, obroty=-2.5)  # przeciwbieżny
    siatka = _siatka_wezlow(cx, cy, r_zewn * 0.62, wezlow=10)
    orzel = _aquila(cx, cy, skala=rozmiar / 130)

    podpis_svg = ""
    if podpis:
        podpis_svg = f'''
  <text x="{cx}" y="{rozmiar - 16}" text-anchor="middle"
        font-family="Georgia, serif" font-size="{rozmiar*0.075:.0f}"
        font-weight="bold" fill="{ZLOTO}" letter-spacing="2">IMPERIAL MESH VORTEX</text>
  <text x="{cx}" y="{rozmiar - 4}" text-anchor="middle"
        font-family="Georgia, serif" font-size="{rozmiar*0.038:.0f}"
        fill="{SREBRO}" letter-spacing="3" opacity="0.7">·  SPQR · ROJ · VORTEX  ·</text>'''

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{rozmiar}" height="{rozmiar}"
     viewBox="0 0 {rozmiar} {rozmiar}">
  <defs>
    <radialGradient id="tlo_grad" cx="50%" cy="45%" r="60%">
      <stop offset="0%" stop-color="{PURPURA}"/>
      <stop offset="100%" stop-color="{TLO}"/>
    </radialGradient>
    <filter id="poswiata" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="1.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- tło: krąg cesarski -->
  <circle cx="{cx}" cy="{cy}" r="{r_zewn}" fill="url(#tlo_grad)"
          stroke="{ZLOTO}" stroke-width="2.5"/>
  <circle cx="{cx}" cy="{cy}" r="{r_zewn-6}" fill="none"
          stroke="{ZLOTO}" stroke-width="0.6" opacity="0.5"/>

  <!-- wir (vortex) przeciwbieżny -->
  <g filter="url(#poswiata)" opacity="0.55">
    <path d="{wir1}" fill="none" stroke="{ZLOTO}" stroke-width="1.1"/>
    <path d="{wir2}" fill="none" stroke="{PURPURA}" stroke-width="1.1" opacity="0.8"/>
  </g>

  <!-- mesh: siatka neuronów -->
  <g opacity="0.85">
    {siatka}
  </g>

  <!-- aquila: orzeł legionowy w centrum -->
  <g filter="url(#poswiata)">
    {orzel}
  </g>
{podpis_svg}
</svg>'''


def zapisz_godlo(sciezka: str, rozmiar: int = 240, podpis: bool = True) -> str:
    """Generuje i zapisuje godło do pliku SVG. Zwraca ścieżkę."""
    svg = generuj_godlo(rozmiar=rozmiar, podpis=podpis)
    with open(sciezka, "w", encoding="utf-8") as f:
        f.write(svg)
    return sciezka


def generuj_favicon(rozmiar: int = 64) -> str:
    """Mała wersja godła bez podpisu — do favicon/ikony."""
    return generuj_godlo(rozmiar=rozmiar, podpis=False)


if __name__ == "__main__":
    import os
    docs = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
    os.makedirs(docs, exist_ok=True)
    p1 = zapisz_godlo(os.path.join(docs, "godlo_imperium.svg"), rozmiar=240)
    p2 = zapisz_godlo(os.path.join(docs, "godlo_favicon.svg"), rozmiar=64, podpis=False)
    print(f"✅ Godło zapisane: {p1}")
    print(f"✅ Favicon zapisany: {p2}")
