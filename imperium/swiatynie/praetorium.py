"""🏛️ PRAETORIUM — Kwatera Główna Imperatora (Centrum Dowodzenia).

Miejsce, z którego CEZAR PIXEL widzi CAŁE Imperium i podboje oraz wydaje ordery.
Wybrany przez Cezara układ: **hybryda C+A** — kwatera bojowa (kokpit operacyjny)
+ castrum (obóz: kondycja wszystkich organów).

GRANICA WOBEC ISTNIEJĄCYCH ORGANÓW (Prawo XVI — nie duplikujemy):
  • `web_dashboard.py` (Panel Kapitolu) = ŻYWY SERWER http + świece + webhook TV.
    PRAETORIUM nie stawia własnego serwera — daje WIDOK, który tamten może podać.
  • `kapitol_podglad.py` (Speculum Probationis) = podgląd POJEDYNCZEGO testu.
    PRAETORIUM pokazuje STAN CAŁEGO Imperium, nie wynik jednej próby.
  • `live_monitor.py` = alarmy pętli live. PRAETORIUM je prezentuje, nie zastępuje.

FILOZOFIA: ZERO ZALEŻNOŚCI (jak cały Imperium) — samowystarczalny HTML, inline CSS,
bez CDN. Renderer jest CZYSTĄ FUNKCJĄ (`render_praetorium(stan) -> str`), więc jest
testowalny bez gniazda i bez przeglądarki (wzorzec z web_dashboard/kapitol_podglad).

PRAWO I — UCZCIWOŚĆ DANYCH (rdzeń tego organu):
Każdy panel niesie znacznik pochodzenia: **ŻYWE** (policzone z kodu w tej chwili) albo
**BRAK DANYCH** (np. rynek bez połączenia z giełdą). NIGDY nie malujemy wypełniacza tak,
by wyglądał na pomiar — kokpit, który kłamie o stanie, jest gorszy niż brak kokpitu.
"""
from __future__ import annotations

import html
from datetime import datetime

# ── znaczniki pochodzenia danych (Prawo I) ────────────────────────────────────
ZYWE = "ZYWE"          # policzone z żywego kodu/rejestrów w chwili renderu
BRAK = "BRAK"          # brak źródła (np. giełda niepodłączona) — NIE zmyślamy


def _esc(x) -> str:
    return html.escape(str(x), quote=True)


def _bezpiecznie(fn, domyslne=None):
    """Wywołuje źródło danych tak, by JEDNO padnięte nie zabiło całego kokpitu.

    Kwatera Główna musi wstać nawet gdy któryś organ jest chory — wtedy panel
    pokaże BRAK DANYCH zamiast wysypać cały ekran. Awaria źródła to informacja,
    nie katastrofa (a milczący panel jest uczciwy — Prawo I).
    """
    try:
        return fn()
    except Exception:
        return domyslne


def zbierz_stan() -> dict:
    """Zbiera ŻYWY stan Imperium z rejestrów (bez sieci, bez giełdy).

    Wszystkie źródła są TANIE (zmierzone 2026-07-19: łącznie ~334 ms) i offline.
    Rynek (pozycje/kapitał) NIE jest tu zgadywany — wypełnia go dopiero warstwa live.
    """
    from imperium.biblioteki import codex_notarum
    from imperium.legiony.rejestr import (
        raport_elity, wszystkie_neurony, wszyscy_zwiadowcy,
    )
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie

    neurony = wszystkie_neurony()
    aktywne = [n for n in neurony if getattr(n, "DOSTEPNY", True)]
    bilans = codex_notarum.bilans()

    return {
        "imperator": "CEZAR PIXEL",
        "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nastepny_krok": _bezpiecznie(_nastepny_krok),
        "roj": {
            "neurony": len(neurony),
            "neurony_aktywne": len(aktywne),
            "zwiadowcy": len(wszyscy_zwiadowcy()),
            "strategie": len(wszystkie_strategie()),
            "elity": raport_elity()["lacznie_elite"],
            "zrodlo": ZYWE,
        },
        "organy": {"dane": _organy(), "zrodlo": ZYWE},
        "honor": {
            "noty": bilans["noty"], "korony": bilans["korony"],
            "saldo": bilans["saldo"], "dlug": len(bilans["dlug_honorowy"]),
            "ostatnie": _ostatnie_noty(bilans), "zrodlo": ZYWE,
        },
        "zaplecze": _bezpiecznie(_zaplecze, {"zrodlo": BRAK}),
        "codex": _bezpiecznie(_codex, {"zrodlo": BRAK}),
        "refleksja": _bezpiecznie(_refleksja, {"zrodlo": BRAK}),
        # Rynek: świadomie PUSTY — wypełnia pętla live po podłączeniu giełdy.
        "rynek": {"zrodlo": BRAK, "powod": "brak połączenia z giełdą (MEXC)"},
    }


def _nastepny_krok() -> dict:
    """Ostatni „→ następny" z Dziennika Nieśmiertelnego — odpowiedź na „co dalej"."""
    from imperium.biblioteki.dziennik_niesmiertelny import banner_nastepny
    tekst = (banner_nastepny() or "").strip()
    return {"tekst": tekst, "zrodlo": ZYWE if tekst else BRAK}


def _zaplecze() -> dict:
    """PORTITOR (pre-flight) + Censor Sprzętu (klasa maszyny). Stdlib, bez sieci.

    Klucze API: PORTITOR raportuje wyłącznie OBECNOŚĆ (✓/✗), nigdy wartość —
    i tak samo tutaj. Sekret nie ma prawa trafić na ekran ani do pliku HTML.
    """
    from imperium.oczy.censor_sprzetu import rekomendowany_tier
    from imperium.pretorianie.portitor import banner
    tier = rekomendowany_tier() or {}
    return {
        "portitor": (banner() or "").strip(),
        "klasa": tier.get("klasa", "—"),
        "model_zakres": tier.get("model_zakres", "—"),
        "zrodlo": ZYWE,
    }


def _codex() -> dict:
    """Jednolinijkowe podsumowanie rejestru testów (CODEX PROBATIONUM)."""
    from narzedzia.codex_probationum import podsumowanie_ledger
    tekst = (podsumowanie_ledger() or "").strip()
    return {"linia": tekst, "zrodlo": ZYWE if tekst else BRAK}


def _refleksja() -> dict:
    """Refleksja W9 — sprzeczności/przedawnienia pamięci.

    Powód obecności w kokpicie (ZASADA CENSORA): ten alarm wisiał wiele sesji
    niezauważony w logu startowym. Alarm widoczny stale = alarm, na który się reaguje.
    """
    from imperium.biblioteki.refleksja_pamieci import raport_startowy
    tekst = (raport_startowy() or "").strip()
    return {"linia": tekst, "zrodlo": ZYWE if tekst else BRAK}


def _ostatnie_noty(bilans: dict, ile: int = 4) -> list[dict]:
    """Ostatnie noty/laury TREŚCIĄ, nie samą cyfrą — cyfra bez kontekstu nic nie mówi."""
    from imperium.biblioteki.codex_notarum import wczytaj
    rek = _bezpiecznie(wczytaj, []) or []
    return [
        {"typ": r.get("typ", "?"), "id": r.get("id", ""),
         "opis": r.get("opis", ""), "data": r.get("data", "")}
        for r in rek[-ile:]
    ][::-1]


def _organy() -> list[tuple[str, str, int]]:
    """(emoji, nazwa, liczba plików .py) — liczby z tego samego źródła co README."""
    from narzedzia.tabularium import wartosci_z_kodu
    w = wartosci_z_kodu()
    ikony = {
        "cesarz": "👑", "senat": "🏛️", "legiony": "⚔️", "koloseum": "🏟️",
        "pretorianie": "🛡️", "akwedukty": "🏗️", "drogi": "🛤️",
        "swiatynie": "🎨", "biblioteki": "📚", "oczy": "👁️", "fundament": "🧮",
    }
    out = []
    for klucz, ile in sorted(w.items()):
        if klucz.startswith("organ_"):
            nazwa = klucz[len("organ_"):]
            out.append((ikony.get(nazwa, "▪"), nazwa, ile))
    return out


def _znacznik(zrodlo: str) -> str:
    """Widoczna etykieta pochodzenia — rdzeń uczciwości kokpitu (Prawo I)."""
    if zrodlo == ZYWE:
        return '<span class="zn zn-zywe" title="policzone z żywego kodu">ŻYWE</span>'
    return '<span class="zn zn-brak" title="brak źródła danych">BRAK DANYCH</span>'


def _panel_rynek(rynek: dict) -> str:
    """Kwatera bojowa. Gdy giełda niepodłączona — mówimy to WPROST, bez wypełniacza."""
    if rynek.get("zrodlo") != ZYWE:
        powod = _esc(rynek.get("powod", "brak źródła"))
        return f"""
      <div class="karta pusta">
        <h3>Kwatera bojowa — front {_znacznik(BRAK)}</h3>
        <div class="brak-tresc">
          <div class="brak-ikona">⚔️</div>
          <p><b>Front milczy.</b> {powod}.</p>
          <p class="mini">Kapitał, pozycje, obsunięcie i kolejka orderów pojawią się tutaj,
          gdy pętla live połączy się z giełdą. Do tego czasu <b>nie pokazujemy liczb</b> —
          kokpit, który zgaduje, jest gorszy niż kokpit milczący (Prawo I).</p>
        </div>
      </div>"""

    p = rynek
    kl = "zysk" if float(p.get("pnl", 0)) >= 0 else "strata"
    wiersze = "".join(
        f"<tr><td>{_esc(x.get('para'))}</td><td>{_esc(x.get('kierunek'))}</td>"
        f"<td class='num'>{_esc(x.get('wejscie'))}</td>"
        f"<td class='num {'zysk' if float(x.get('wynik', 0)) >= 0 else 'strata'}'>"
        f"{float(x.get('wynik', 0)):+.2f}%</td></tr>"
        for x in p.get("pozycje", [])
    ) or "<tr><td colspan='4' class='mini'>brak otwartych pozycji</td></tr>"

    return f"""
      <div class="karta">
        <h3>Kwatera bojowa — front {_znacznik(ZYWE)}</h3>
        <div class="hud">
          <div class="kafel"><div class="et">Kapitał</div><div class="wa">{_esc(p.get('kapital', '—'))}</div></div>
          <div class="kafel"><div class="et">P&amp;L</div><div class="wa {kl}">{float(p.get('pnl', 0)):+.2f}%</div></div>
          <div class="kafel"><div class="et">Pozycje</div><div class="wa">{len(p.get('pozycje', []))}</div></div>
          <div class="kafel"><div class="et">Postawa</div><div class="wa">{_esc(p.get('postawa', '—'))}</div></div>
        </div>
        <table style="margin-top:12px">
          <tr><th>Para</th><th>Kierunek</th><th class="num">Wejście</th><th class="num">Wynik</th></tr>
          {wiersze}
        </table>
      </div>"""


def _panel_prosty(tytul: str, dane: dict, klucz: str, pusty: str) -> str:
    """Karta z jedną linią tekstu ze źródła (CODEX / Refleksja). Pusto → mówi wprost."""
    zrodlo = (dane or {}).get("zrodlo", BRAK)
    tresc = (dane or {}).get(klucz, "") if zrodlo == ZYWE else ""
    ciało = f'<div class="linia">{_esc(tresc)}</div>' if tresc else \
            f'<div class="mini">{_esc(pusty)}</div>'
    return f"""
      <div class="karta">
        <h3><span>{_esc(tytul)}</span>{_znacznik(zrodlo)}</h3>
        {ciało}
      </div>"""


def _panel_zaplecze(z: dict) -> str:
    """PORTITOR + klasa maszyny. Nigdy nie pokazuje WARTOŚCI kluczy API — tylko obecność."""
    z = z or {}
    if z.get("zrodlo") != ZYWE:
        return f"""
      <div class="karta">
        <h3><span>Zaplecze</span>{_znacznik(BRAK)}</h3>
        <div class="mini">pre-flight niedostępny</div>
      </div>"""
    return f"""
      <div class="karta">
        <h3><span>Zaplecze</span>{_znacznik(ZYWE)}</h3>
        <div class="linia">{_esc(z.get('portitor', ''))}</div>
        <table style="margin-top:9px">
          <tr><td>Klasa maszyny</td><td class="num">{_esc(z.get('klasa', '—'))}</td></tr>
          <tr><td>Zakres modeli</td><td class="num mini">{_esc(z.get('model_zakres', '—'))}</td></tr>
        </table>
      </div>"""


def _panel_noty(honor: dict) -> str:
    """Treść ostatnich NOT/CORON — bo samo „5 / 5" nie mówi, CO poszło nie tak."""
    ostatnie = (honor or {}).get("ostatnie") or []
    if not ostatnie:
        return ""
    wiersze = "".join(
        f'<tr><td><span class="zn {"z-al" if r.get("typ") == "NOTA" else "z-ok"}">'
        f'{_esc(r.get("typ"))}</span></td>'
        f'<td>{_esc(r.get("opis", "")[:110])}</td>'
        f'<td class="num mini">{_esc(r.get("data", ""))}</td></tr>'
        for r in ostatnie
    )
    return f"""
      <div class="karta">
        <h3><span>Księga Not — ostatnie wpisy</span>{_znacznik(honor.get('zrodlo', BRAK))}</h3>
        <table>{wiersze}</table>
      </div>"""


def render_praetorium(stan: dict) -> str:
    """Czysta funkcja: stan → samowystarczalny HTML (bez sieci, bez plików)."""
    roj = stan.get("roj", {})
    honor = stan.get("honor", {})
    organy = stan.get("organy", {}).get("dane", [])
    nk = stan.get("nastepny_krok") or {}
    pasek_nk = (
        f'<div class="nastepny">{_esc(nk.get("tekst", ""))}</div>'
        if nk.get("zrodlo") == ZYWE and nk.get("tekst") else ""
    )

    namioty = "".join(
        f'<div class="namiot"><div class="ikona">{i}</div>'
        f'<div class="licz">{n}</div><div class="nazwa">{_esc(k)}</div></div>'
        for i, k, n in organy
    ) or '<div class="mini">brak danych o organach</div>'

    dlug = int(honor.get("dlug", 0))
    kl_honor = "z-al" if dlug else "z-ok"
    txt_honor = f"{dlug} niespłacony" if dlug else "0 — czysto"

    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PRAETORIUM — Kwatera Główna Imperatora</title>
<style>
:root{{--tlo:#0d1117;--panel:#141b24;--panel2:#1b2430;--linia:#2a3646;--tekst:#e6edf3;
--slaby:#8b98a9;--zloto:#d4a13a;--purpura:#8b2f3f;--zielen:#3fb950;--czerwien:#e5534b;
--mono:ui-monospace,Consolas,monospace;--serif:"Palatino Linotype",Georgia,serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--tlo);color:var(--tekst);
font-family:system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.5}}
.wrap{{max-width:1280px;margin:0 auto;padding:20px}}
.top{{border-bottom:2px solid var(--zloto);padding-bottom:14px;margin-bottom:18px;
display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}}
.top h1{{margin:0;font-family:var(--serif);font-size:1.6rem;letter-spacing:.06em;color:var(--zloto)}}
.top .kto{{color:var(--slaby);font-size:.86rem}}
.chipy{{display:flex;gap:8px;flex-wrap:wrap}}
.zn{{display:inline-block;padding:2px 9px;border-radius:11px;font-size:.68rem;font-weight:700;
letter-spacing:.07em}}
.zn-zywe{{background:rgba(63,185,80,.16);color:var(--zielen)}}
.zn-brak{{background:rgba(212,161,58,.16);color:var(--zloto)}}
.z-ok{{background:rgba(63,185,80,.16);color:var(--zielen)}}
.z-al{{background:rgba(229,83,75,.16);color:var(--czerwien)}}
.siatka{{display:grid;grid-template-columns:1fr 320px;gap:14px}}
.karta{{background:var(--panel);border:1px solid var(--linia);border-radius:8px;padding:14px;
margin-bottom:14px}}
.karta h3{{margin:0 0 11px;font-size:.74rem;text-transform:uppercase;letter-spacing:.13em;
color:var(--slaby);font-weight:600;display:flex;justify-content:space-between;gap:10px}}
.karta.pusta{{border-style:dashed}}
.brak-tresc{{text-align:center;padding:22px 10px;color:var(--slaby)}}
.brak-ikona{{font-size:2.2rem;opacity:.45}}
.brak-tresc p{{margin:8px 0}}
.mini{{font-size:.78rem;color:var(--slaby)}}
.hud{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}
.kafel{{background:var(--panel2);border:1px solid var(--linia);border-left:3px solid var(--zloto);
border-radius:5px;padding:10px}}
.kafel .et{{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:var(--slaby)}}
.kafel .wa{{font-family:var(--mono);font-size:1.4rem;font-weight:700;margin-top:3px}}
.namioty{{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px}}
.namiot{{background:var(--panel2);border:1px solid var(--linia);border-top:3px solid var(--zloto);
border-radius:0 0 6px 6px;padding:10px;text-align:center}}
.namiot .ikona{{font-size:1.3rem}}
.namiot .licz{{font-family:var(--mono);font-weight:700;font-size:1.05rem;color:var(--zloto)}}
.namiot .nazwa{{font-size:.74rem;color:var(--slaby);margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:.85rem}}
th,td{{text-align:left;padding:7px 8px;border-bottom:1px solid var(--linia)}}
th{{color:var(--slaby);font-weight:600;font-size:.71rem;text-transform:uppercase;letter-spacing:.08em}}
td.num{{text-align:right;font-family:var(--mono)}}
.zysk{{color:var(--zielen)}} .strata{{color:var(--czerwien)}}
.duza{{font-size:1.8rem;font-weight:700;font-family:var(--mono);color:var(--zloto)}}
.rozkazy{{background:var(--panel2);border:1px solid var(--purpura);border-radius:6px;padding:12px}}
.przyc{{display:block;width:100%;margin-bottom:8px;padding:9px 12px;border-radius:5px;
border:1px solid var(--linia);background:var(--panel);color:var(--tekst);font-size:.84rem;
cursor:not-allowed;opacity:.55;text-align:left}}
.przyc.glowny{{background:var(--purpura);border-color:var(--purpura);font-weight:600}}
.nastepny{{background:rgba(212,161,58,.10);border:1px solid rgba(212,161,58,.35);
border-radius:6px;padding:10px 13px;margin-bottom:16px;font-size:.87rem}}
.linia{{font-family:var(--mono);font-size:.8rem;white-space:pre-wrap;word-break:break-word;
background:var(--panel2);border-radius:5px;padding:9px 11px;color:var(--tekst)}}
.stopka{{margin-top:20px;color:var(--slaby);font-size:.78rem;text-align:center;
border-top:1px solid var(--linia);padding-top:13px}}
@media(max-width:860px){{.siatka{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">

<div class="top">
  <div>
    <h1>⚔️ PRAETORIUM</h1>
    <div class="kto">Kwatera Główna · Imperator <b>{_esc(stan.get('imperator', '—'))}</b>
      · stan na {_esc(stan.get('czas', '—'))}</div>
  </div>
  <div class="chipy">
    <span class="zn {kl_honor}">DŁUG HONOROWY: {_esc(txt_honor)}</span>
    <span class="zn zn-zywe">RÓJ: {roj.get('neurony', '—')} / {roj.get('zwiadowcy', '—')}</span>
  </div>
</div>

{pasek_nk}

<div class="siatka">
  <div>
    {_panel_rynek(stan.get('rynek', {}))}

    <div class="karta">
      <h3><span>Castrum — organy Imperium</span>{_znacznik(stan.get('organy', {}).get('zrodlo', BRAK))}</h3>
      <div class="namioty">{namioty}</div>
    </div>

    {_panel_noty(honor)}
  </div>

  <aside>
    <div class="rozkazy">
      <h3 style="color:var(--zloto)">🏛️ Rozkazy Imperatora</h3>
      <button class="przyc glowny" disabled>⚔️ Wydaj order</button>
      <button class="przyc" disabled>🛡️ Zamknij pozycję</button>
      <button class="przyc" disabled>⏸️ Wstrzymaj rój</button>
      <div class="mini">Rozkazy nieaktywne — front niepodłączony.
        Wpięcie w egzekucję to osobna, świadoma decyzja (ZASADA WPIĘCIA).</div>
    </div>

    <div class="karta" style="margin-top:14px">
      <h3><span>Arsenał</span>{_znacznik(roj.get('zrodlo', BRAK))}</h3>
      <table>
        <tr><td>Neurony</td><td class="num">{roj.get('neurony', '—')}
            <span class="mini">({roj.get('neurony_aktywne', '—')} akt.)</span></td></tr>
        <tr><td>Zwiadowcy</td><td class="num">{roj.get('zwiadowcy', '—')}</td></tr>
        <tr><td>Strategie</td><td class="num">{roj.get('strategie', '—')}</td></tr>
        <tr><td>Elitarne</td><td class="num">{roj.get('elity', '—')}</td></tr>
      </table>
    </div>

    <div class="karta">
      <h3><span>Księga Not (oko za oko)</span>{_znacznik(honor.get('zrodlo', BRAK))}</h3>
      <table>
        <tr><td>NOTA CENSORIA</td><td class="num">{honor.get('noty', '—')}</td></tr>
        <tr><td>CORONA</td><td class="num">{honor.get('korony', '—')}</td></tr>
        <tr><td>Saldo</td><td class="num">{honor.get('saldo', '—')}</td></tr>
      </table>
    </div>

    {_panel_zaplecze(stan.get('zaplecze', {}))}
    {_panel_prosty('Rejestr prób (CODEX)', stan.get('codex', {}), 'linia',
                   'ledger niedostępny')}
    {_panel_prosty('Refleksja pamięci (W9)', stan.get('refleksja', {}), 'linia',
                   'brak odczytu refleksji')}
  </aside>
</div>

<div class="stopka">
  PRAETORIUM · hybryda C+A · <b>ŻYWE</b> = policzone z kodu przy renderze ·
  <b>BRAK DANYCH</b> = źródło niepodłączone (nie zmyślamy — Prawo I)
</div>
</div></body></html>"""


def zapisz(sciezka: str = "raporty/PRAETORIUM.html") -> str:
    """Renderuje ŻYWY stan do pliku HTML. Zwraca ścieżkę."""
    import os
    tresc = render_praetorium(zbierz_stan())
    os.makedirs(os.path.dirname(sciezka) or ".", exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        f.write(tresc)
    return sciezka


if __name__ == "__main__":
    print(f"🏛️ PRAETORIUM zapisane → {zapisz()}")
