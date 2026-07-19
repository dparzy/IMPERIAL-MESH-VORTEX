"""
🌐 WEB DASHBOARD — Panel Kapitolu (W-346 + W-354, realizuje W-004 + W-031).

W-346: Panel webowy (http://localhost:8777) — rój 78 neuronów widoczny w przeglądarce.
W-354: TradingView Webhook Receiver — alerty z TV wchodzą przez POST /webhook/tv
       i trafiają do roju; wykres świecowy (Lightweight Charts) renderuje bary na żywo.
W-361: Feed MEXC bez webhooka (MagazynSwiec) — pętla live wpycha bary, które bot i tak
       pobiera (bary_per) → wykres pokazuje świece MEXC bez konfiguracji TradingView.
       + Markery wejść bota (▲ LONG / ▼ SHORT) na świecach (znaczniki_do_lwc → setMarkers).

FILOZOFIA: ZERO ZALEŻNOŚCI (jak cały Imperium — runner bez deps). Zamiast FastAPI
używamy `http.server` ze stdlib + samowystarczalny HTML (inline CSS/JS, fetch).
Lightweight Charts ładowane z CDN (TradingView, MIT license).

ARCHITEKTURA (routing wydzielony — testowalny bez gniazda):
    obsluz_sciezke(path, stan, odbiornik) → (status, content_type, body)   # GET router
    obsluz_post(path, body, odbiornik)    → (status, content_type, body)   # POST router
    DashboardHandler                       # cienki adapter http.server
    SerwerDashboard.aktualizuj(stan) / podepnij_webhook(odbiornik) / start() / stop()

TradingView Webhook:
    POST /webhook/tv   Content-Type: text/plain (TV domyślnie)
    Body (Pine Script {{placeholders}}):
      {"symbol":"{{ticker}}","interwal":"{{interval}}","akcja":"NEUTRAL",
       "cena":{{close}},"czas":"{{time}}","open":{{open}},"high":{{high}},
       "low":{{low}},"close":{{close}},"volume":{{volume}},"sekret":"OPC"}

    OdbiornikWebhook buforuje; pętla live pobiera przez odbiornik.pobierz_wszystkie().

Bezpieczeństwo: bind domyślnie 127.0.0.1 — panel lokalny.
Sekret webhooka WYŁĄCZNIE z env WEBHOOK_TV_SEKRET (nigdy hardcode — Prawo I).
"""

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Tuple

logger = logging.getLogger("WebDashboard")


# W-031 Roman Naming — szlacheckie nazwy walut (charakter = charakter waluty)
NAZWY_RZYMSKIE = {
    "BTC": "Capitolium",          # Twierdza Kapitolińska — król, niezdobyta
    "ETH": "Patricii Aeterni",    # Wieczni Patrycjusze — szlachcic, ekosystem
    "SOL": "Velocitas Barbari",   # Prędkość Barbarzyńcy — szybki
    "DOGE": "Mimus Augusti",      # Błazen Cesarza — meme, nieprzewidywalny
    "XRP": "Mercator Pontis",     # Kupiec Mostu — przelewy/płatności
    "BNB": "Aedilis Fori",        # Zarządca Forum — giełdowy token
    "ADA": "Philosophus",         # Filozof — akademicki, formalny
}


def nazwa_rzymska(symbol: str) -> str:
    """Zwraca rzymską nazwę bazowej waluty pary (BTCUSDT → Capitolium). Brak → ''."""
    baza = symbol.upper().replace("USDT", "").replace("USD", "").replace("PERP", "")
    return NAZWY_RZYMSKIE.get(baza.strip(" _-/:"), "")


class MagazynSwiec:
    """
    Thread-safe magazyn świec z NASZEGO feedu (DataLoader / MEXC) — W-361.

    Dopełnia webhooki TradingView (Prawo XVI, nie redundancja): webhook wymaga
    konfiguracji TV + tunelu do localhost; MagazynSwiec pozwala pętli live wprost
    wepchnąć bary, które bot i tak pobiera (bary_per) → wykres pokazuje świece MEXC
    BEZ webhooka. Router serwuje magazyn gdy historia webhooka pusta.

    petla_live woła podaj(symbol, bary); GET /wykresy/{symbol}.json → get(symbol).
    """

    def __init__(self, max_swiec: int = 500):
        self._d: dict = {}
        self._lock = threading.Lock()
        self._max = max_swiec

    def podaj(self, symbol: str, bary) -> None:
        """Wrzuca bary w formacie Imperium {timestamp,open,high,low,close,...} → LWC."""
        sw = []
        for b in bary or []:
            try:
                t = int(b["timestamp"])
                t = t // 1000 if t > 1_000_000_000_000 else t   # ms → s (LWC)
                sw.append({
                    "time": t,
                    "open": float(b["open"]), "high": float(b["high"]),
                    "low": float(b["low"]), "close": float(b["close"]),
                })
            except (KeyError, ValueError, TypeError):
                continue
        sw.sort(key=lambda x: x["time"])
        with self._lock:
            self._d[symbol.upper()] = sw[-self._max:]

    def get(self, symbol: str) -> list:
        with self._lock:
            return list(self._d.get(symbol.upper(), []))

    def symbole(self) -> list:
        with self._lock:
            return sorted(self._d.keys())


def znaczniki_do_lwc(znaczniki) -> list:
    """
    Konwertuje znaczniki wejść/wyjść bota → markery Lightweight Charts (W-361).

    Wejście: [{"timestamp": ms/s, "cena": float, "kierunek": "LONG"/"SHORT",
               "typ": "wejscie"/"wyjscie", "symbol": "BTCUSDT"}]
    Wyjście (posortowane rosnąco po time — wymóg LWC): markery z zachowanym polem
    "symbol" (JS filtruje po aktywnym symbolu i je usuwa przed setMarkers).
      LONG wejście  → ▲ zielony pod świecą
      SHORT wejście → ▼ czerwony nad świecą
      wyjście       → ▼ pomarańczowy nad świecą
    """
    out = []
    for zn in znaczniki or []:
        try:
            t = int(zn["timestamp"])
            t = t // 1000 if t > 1_000_000_000_000 else t
            kier = zn.get("kierunek")
            typ = zn.get("typ", "wejscie")
            sym = (zn.get("symbol") or "").upper()
        except (KeyError, ValueError, TypeError):
            continue
        if typ == "wyjscie":
            m = {"time": t, "position": "aboveBar", "color": "#e67e22",
                 "shape": "arrowDown", "text": "wyjście"}
        elif kier == "SHORT":
            m = {"time": t, "position": "aboveBar", "color": "#e74c3c",
                 "shape": "arrowDown", "text": "SHORT"}
        else:
            m = {"time": t, "position": "belowBar", "color": "#2ecc71",
                 "shape": "arrowUp", "text": "LONG"}
        m["symbol"] = sym
        out.append(m)
    return sorted(out, key=lambda x: x["time"])


def stan_do_json(stan) -> dict:
    """Serializuje StanDashboardu do dict JSON (pozycje, neurony, kapitał, reżim)."""
    pozycje = [{
        "symbol": p.symbol,
        "rzymska": nazwa_rzymska(p.symbol),
        "kierunek": p.kierunek,
        "wejscie": round(p.wejscie, 6),
        "aktualny": round(p.aktualny, 6),
        "wielkosc": round(p.wielkosc, 2),
        "pnl_pct": round(p.pnl_pct * 100, 3),
        "sl": round(p.sl, 6),
        "tp": round(p.tp, 6),
    } for p in getattr(stan, "pozycje", [])]

    neurony = [{
        "klucz": n.klucz, "kierunek": n.kierunek,
        "pewnosc": round(n.pewnosc, 3), "waga": round(n.waga, 2),
    } for n in getattr(stan, "neurony_top", [])]

    kapital = getattr(stan, "kapital", 0.0)
    start = getattr(stan, "kapital_start", 0.0)
    zysk_pct = ((kapital - start) / start * 100) if start else 0.0

    return {
        "symbol": getattr(stan, "symbol", "???"),
        "rezim": getattr(stan, "rezim", "UNKNOWN"),
        "kierunek_legatus": getattr(stan, "kierunek_legatus", "NEUTRAL"),
        "pewnosc": round(getattr(stan, "pewnosc", 0.0), 3),
        "kapital": round(kapital, 2),
        "kapital_start": round(start, 2),
        "zysk_pct": round(zysk_pct, 3),
        "postawa_gubernatora": getattr(stan, "postawa_gubernatora", "NORMALNY"),
        "bary_przetworzone": getattr(stan, "bary_przetworzone", 0),
        "decyzje_wejscia": getattr(stan, "decyzje_wejscia", 0),
        "weta": getattr(stan, "weta", 0),
        "bledy": getattr(stan, "bledy", 0),
        "pozycje": pozycje,
        "neurony_top": neurony,
        "znaczniki": znaczniki_do_lwc(getattr(stan, "znaczniki_swiec", [])),
    }


def _html_strona() -> str:
    """
    Samowystarczalny HTML panelu (W-346 + W-354).
    Lightweight Charts z CDN → wykres świecowy TradingView.
    Selector symbolu/interwału → zmiana pary na żywo.
    """
    return r"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<title>Kapitol Imperium</title>
<link rel="icon" href="/godlo.svg">
<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>
<style>
  :root{--zloto:#D4AF37;--purpura:#4A0E2E;--tlo:#0D0D14;--zielen:#2ecc71;--czerw:#e74c3c;--panel:#16161f;--obr:#2a2a38}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--tlo);color:#e8e8e8;font-family:'Segoe UI',system-ui,sans-serif;padding:16px}
  header{display:flex;align-items:center;gap:12px;border-bottom:2px solid var(--zloto);padding-bottom:12px;margin-bottom:16px;flex-wrap:wrap}
  header img{width:48px;height:48px}
  h1{color:var(--zloto);font-size:20px;letter-spacing:2px}
  .toolbar{display:flex;align-items:center;gap:8px;margin-left:auto;flex-wrap:wrap}
  select{background:#1e1e2e;color:#e8e8e8;border:1px solid var(--obr);border-radius:6px;padding:6px 10px;font-size:13px;cursor:pointer}
  select:focus{outline:none;border-color:var(--zloto)}
  .badge{background:var(--purpura);color:var(--zloto);border-radius:4px;padding:3px 8px;font-size:12px;font-weight:700;letter-spacing:1px}
  .siatka{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px}
  .karta{background:var(--panel);border:1px solid var(--obr);border-radius:8px;padding:14px}
  .karta .etykieta{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#888}
  .karta .wartosc{font-size:24px;font-weight:700;margin-top:4px}
  .zielony{color:var(--zielen)}.czerwony{color:var(--czerw)}.zloty{color:var(--zloto)}
  table{width:100%;border-collapse:collapse;margin-top:6px}
  th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--obr);font-size:13px}
  th{color:var(--zloto);text-transform:uppercase;font-size:10px;letter-spacing:1px}
  .sekcja-tytul{color:var(--zloto);font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:16px 0 6px}
  #wykres-kontener{background:var(--panel);border:1px solid var(--obr);border-radius:8px;margin-bottom:16px;position:relative;height:340px;overflow:hidden}
  #wykres{width:100%;height:100%}
  #wykres-info{position:absolute;top:10px;left:12px;font-size:12px;color:#aaa;pointer-events:none}
  #webhook-status{font-size:11px;color:#888;padding:3px 8px;background:var(--panel);border:1px solid var(--obr);border-radius:4px}
  footer{margin-top:20px;color:#555;font-size:11px;text-align:center}
  .tv-pin{font-size:11px;color:#666;line-height:1.6;background:#0e0e18;border:1px solid var(--obr);border-radius:6px;padding:10px 14px;font-family:monospace;white-space:pre-wrap;overflow-x:auto}
  details summary{cursor:pointer;color:var(--zloto);font-size:12px;text-transform:uppercase;letter-spacing:1px;margin:16px 0 6px;user-select:none}
</style>
</head><body>

<header>
  <img src="/godlo.svg" alt="godło">
  <h1>KAPITOL IMPERIUM</h1>
  <div class="toolbar">
    <span id="rezim" class="badge">—</span>
    <select id="sel-symbol" title="Para walutowa" onchange="zmienSymbol()">
      <option value="">— symbol —</option>
    </select>
    <select id="sel-interwal" title="Interwał" onchange="ladujWykres()">
      <option value="1">1m</option>
      <option value="5">5m</option>
      <option value="15">15m</option>
      <option value="60" selected>1h</option>
      <option value="240">4h</option>
      <option value="D">1D</option>
    </select>
    <span id="webhook-status">webhook: ładowanie…</span>
  </div>
</header>

<!-- WYKRES ŚWIECOWY (W-354) -->
<div id="wykres-kontener">
  <div id="wykres"></div>
  <div id="wykres-info">Brak danych z TradingView — skonfiguruj webhook</div>
</div>

<!-- METRYKI -->
<div class="siatka">
  <div class="karta"><div class="etykieta">Kapitał</div><div class="wartosc" id="kapital">—</div></div>
  <div class="karta"><div class="etykieta">Zysk sesji</div><div class="wartosc" id="zysk">—</div></div>
  <div class="karta"><div class="etykieta">Wejścia / Weta</div><div class="wartosc" id="wejscia">—</div></div>
  <div class="karta"><div class="etykieta">Gubernator</div><div class="wartosc zloty" id="gubernator" style="font-size:18px">—</div></div>
</div>

<div class="sekcja-tytul">⚔️ Otwarte pozycje</div>
<table id="pozycje">
  <thead><tr><th>Para</th><th>Nazwa</th><th>Kierunek</th><th>Wejście</th><th>Teraz</th><th>P&L</th><th>Wielkość</th></tr></thead>
  <tbody></tbody>
</table>

<div class="sekcja-tytul">🧠 Czołowe neurony (rój)</div>
<table id="neurony">
  <thead><tr><th>Klucz</th><th>Kierunek</th><th>Pewność</th><th>Waga</th></tr></thead>
  <tbody></tbody>
</table>

<!-- SZKOŁA TIRO (E2) — postęp zbierania materiału treningowego przez NOTARIUSA -->
<div class="sekcja-tytul">🎓 Szkoła TIRO — nauka lokalnego ucznia</div>
<div class="siatka">
  <div class="karta"><div class="etykieta">Par zebranych</div><div class="wartosc" id="tiro-par">—</div></div>
  <div class="karta"><div class="etykieta">Materiał (tokeny)</div><div class="wartosc" id="tiro-tokeny">—</div></div>
  <div class="karta"><div class="etykieta">Pisarz</div><div class="wartosc" id="tiro-stan" style="font-size:18px">—</div></div>
  <div class="karta"><div class="etykieta">Nauczyciel</div><div class="wartosc" id="tiro-nauczyciel" style="font-size:16px">—</div></div>
</div>
<div style="margin:10px 0 4px">
  <div style="display:flex;justify-content:space-between;font-size:12px;color:#aaa">
    <span id="tiro-prog-opis">—</span><span id="tiro-prog-liczby">—</span>
  </div>
  <div style="background:#1a1a1a;border:1px solid #333;border-radius:6px;height:18px;overflow:hidden;margin-top:4px">
    <div id="tiro-pasek" style="height:100%;width:0%;background:linear-gradient(90deg,#6b4f1d,var(--zloto));transition:width .4s"></div>
  </div>
</div>
<table id="tiro-zrodla">
  <thead><tr><th>Źródło par</th><th>Ile</th></tr></thead>
  <tbody></tbody>
</table>

<!-- KONFIGURACJA TRADINGVIEW -->
<details>
  <summary>📡 Konfiguracja TradingView Webhook (W-354)</summary>
  <p style="color:#aaa;font-size:12px;margin:8px 0">
    W TradingView: <b>Alert → Webhook URL</b> → wpisz adres serwera + <code>/webhook/tv</code>.<br>
    W polu <b>Message</b> użyj Pine Script placeholderów:
  </p>
  <div class="tv-pin" id="tv-template">ładowanie…</div>
  <p style="color:#888;font-size:11px;margin-top:8px">
    ⚠ Ustaw <code>WEBHOOK_TV_SEKRET=twój_sekret</code> w zmiennych środowiskowych serwera (Prawo bezpieczeństwa).<br>
    Gdy TradingView nie może dotrzeć do localhost — użyj <a href="https://ngrok.com" target="_blank" style="color:var(--zloto)">ngrok</a> lub Cloudflare Tunnel.
  </p>
</details>

<footer>Imperium · panel lokalny · auto-odświeżanie co 2 s · wykres z TradingView Lightweight Charts (MIT)</footer>

<script>
/* ── Lightweight Charts setup ─────────────────────────────────── */
const wykresKont = document.getElementById('wykres');
const chart = LightweightCharts.createChart(wykresKont, {
  layout: {background:{color:'#16161f'}, textColor:'#e8e8e8'},
  grid: {vertLines:{color:'#2a2a38'}, horzLines:{color:'#2a2a38'}},
  crosshair: {mode: LightweightCharts.CrosshairMode.Normal},
  rightPriceScale: {borderColor:'#2a2a38'},
  timeScale: {borderColor:'#2a2a38', timeVisible:true, secondsVisible:false},
  width: wykresKont.clientWidth,
  height: 340,
});
const swiece = chart.addCandlestickSeries({
  upColor:'#2ecc71', downColor:'#e74c3c',
  borderUpColor:'#2ecc71', borderDownColor:'#e74c3c',
  wickUpColor:'#2ecc71', wickDownColor:'#e74c3c',
});
window.addEventListener('resize', () => {
  chart.applyOptions({width: wykresKont.clientWidth});
});

/* ── Stan aplikacji ───────────────────────────────────────────── */
let aktywnySymbol = '';
let ostDaneWebhook = null;
let ostatnieZnaczniki = [];   // W-361: markery wejść/wyjść bota (z /stan.json)

function kolorPnl(v){return v>0?'zielony':v<0?'czerwony':''}

/* Markery bota na świecach — filtruj po aktywnym symbolu, zdejmij pole symbol (W-361) */
function ustawMarkery(){
  if (!aktywnySymbol){ swiece.setMarkers([]); return; }
  const m = (ostatnieZnaczniki||[])
    .filter(z => !z.symbol || z.symbol === aktywnySymbol)
    .map(({symbol, ...r}) => r);
  swiece.setMarkers(m);
}

/* ── Ładowanie wykresu z /wykresy/{symbol}.json ──────────────── */
async function ladujWykres() {
  if (!aktywnySymbol) return;
  try {
    const r = await fetch(`/wykresy/${aktywnySymbol}.json`);
    if (!r.ok) { _wykresInfo('Brak danych dla '+aktywnySymbol); return; }
    const dane = await r.json();
    if (!dane.length) { _wykresInfo('Oczekiwanie na alerty z TradingView…'); return; }
    // Lightweight Charts wymaga rosnącego 'time' (Unix sekund lub YYYY-MM-DD)
    const swieczeTV = dane.map(d => ({
      time: _normalizujCzas(d.time),
      open: d.open, high: d.high, low: d.low, close: d.close,
    })).filter(d => d.time).sort((a,b) => a.time - b.time);
    swiece.setData(swieczeTV);
    ustawMarkery();   // W-361: nanieś markery wejść/wyjść bota po (prze)ładowaniu świec
    chart.timeScale().fitContent();
    _wykresInfo(`${aktywnySymbol} · ${dane.length} świec`);
  } catch(e) {
    _wykresInfo('Błąd wykresu: '+e.message);
  }
}

function _normalizujCzas(t) {
  if (!t) return null;
  // Unix ms
  const n = Number(t);
  if (!isNaN(n) && n > 1e12) return Math.floor(n/1000);
  if (!isNaN(n) && n > 1e9) return Math.floor(n);
  // ISO string
  const d = new Date(t);
  if (!isNaN(d)) return Math.floor(d.getTime()/1000);
  return null;
}

function _wykresInfo(txt) {
  document.getElementById('wykres-info').textContent = txt;
}

/* ── Zmiana symbolu ───────────────────────────────────────────── */
function zmienSymbol() {
  aktywnySymbol = document.getElementById('sel-symbol').value;
  ladujWykres();
}

/* ── Odświeżanie stanu (/stan.json co 2s) ─────────────────────── */
async function odswiez() {
  try {
    const s = await (await fetch('/stan.json')).json();
    document.getElementById('rezim').textContent = (s.rezim||'?') + ' · ' + (s.symbol||'?');
    document.getElementById('kapital').textContent = s.kapital.toLocaleString() + ' USDT';
    const z = document.getElementById('zysk');
    z.textContent = (s.zysk_pct >= 0 ? '+' : '') + s.zysk_pct + '%';
    z.className = 'wartosc ' + kolorPnl(s.zysk_pct);
    document.getElementById('wejscia').textContent = s.decyzje_wejscia + ' / ' + s.weta;
    document.getElementById('gubernator').textContent = s.postawa_gubernatora;

    /* Status źródła świec */
    if (s.webhook) {
      const w = s.webhook;
      document.getElementById('webhook-status').textContent =
        `webhook: ${w.lacznie_alertow} alertów | ${w.bledy_parsowania} błędów`;
    } else {
      document.getElementById('webhook-status').textContent = 'feed: MEXC (bez webhooka TV)';
    }
    /* Selektor symboli — z webhooka TV I/LUB feedu MEXC (W-361) */
    const symbole = s.symbole_swiec || (s.webhook && s.webhook.symbole) || [];
    const sel = document.getElementById('sel-symbol');
    const obecne = new Set([...sel.options].map(o => o.value));
    for (const sym of symbole) {
      if (!obecne.has(sym)) {
        const opt = document.createElement('option');
        opt.value = sym; opt.textContent = sym;
        sel.appendChild(opt);
      }
    }
    if (!aktywnySymbol && symbole.length) {
      aktywnySymbol = symbole[0];
      sel.value = aktywnySymbol;
      ladujWykres();
    }
    /* Markery wejść/wyjść bota (W-361) */
    ostatnieZnaczniki = s.znaczniki || [];
    ustawMarkery();

    /* Pozycje */
    const tb = document.querySelector('#pozycje tbody'); tb.innerHTML = '';
    for (const p of s.pozycje) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${p.symbol}</td><td class="zloty">${p.rzymska||'—'}</td>`
        + `<td>${p.kierunek}</td><td>${p.wejscie}</td><td>${p.aktualny}</td>`
        + `<td class="${kolorPnl(p.pnl_pct)}">${p.pnl_pct>=0?'+':''}${p.pnl_pct}%</td><td>${p.wielkosc}</td>`;
      tb.appendChild(tr);
    }
    if (!s.pozycje.length) tb.innerHTML = '<tr><td colspan="7" style="color:#555">brak otwartych pozycji</td></tr>';

    /* Neurony */
    const tn = document.querySelector('#neurony tbody'); tn.innerHTML = '';
    for (const n of s.neurony_top) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${n.klucz}</td><td>${n.kierunek}</td><td>${n.pewnosc}</td><td>${n.waga}</td>`;
      tn.appendChild(tr);
    }
  } catch(e) {
    document.getElementById('rezim').textContent = '⚠ brak połączenia';
  }
}

/* ── Pine Script template ─────────────────────────────────────── */
document.getElementById('tv-template').textContent =
`// ── Pine Script Alert Message ──────────────────────────────
// Wklej do pola "Message" w TradingView Alert (webhook):
{
  "symbol": "{{ticker}}",
  "interwal": "{{interval}}",
  "akcja": "NEUTRAL",
  "cena": {{close}},
  "czas": "{{timenow}}",
  "open": {{open}},
  "high": {{high}},
  "low": {{low}},
  "close": {{close}},
  "volume": {{volume}},
  "sekret": "WSTAW_TWOJ_WEBHOOK_TV_SEKRET"
}
// Webhook URL: http://<twoj-host>:8777/webhook/tv
// Dla BUY/SELL: zamień "NEUTRAL" na "BUY"/"SELL" lub użyj
// {{strategy.order.action}} jeśli alert z Strategy.`;

/* ── Startuj ──────────────────────────────────────────────────── */
odswiez();
// ── Szkoła TIRO: postęp zbierania par (E2). Osobny fetch, bo /tiro.json nie zależy
// od stanu pętli — zbiór rośnie też gdy pętla nie handluje (zwiad, auto-lekcje).
async function odswiezTiro() {
  try {
    const t = await (await fetch('/tiro.json')).json();
    const p = t.postep || {cel:0, procent:0, brakuje:0, opis:'—'};
    document.getElementById('tiro-par').textContent = (t.par ?? 0).toLocaleString('pl-PL');
    document.getElementById('tiro-tokeny').textContent =
      '~' + (t.szac_tokenow_odpowiedzi ?? 0).toLocaleString('pl-PL');
    document.getElementById('tiro-stan').textContent = t.wlaczony ? '✅ zbiera' : '⏸ wyłączony';
    const nauczyciele = Object.keys(t.modele || {});
    document.getElementById('tiro-nauczyciel').textContent = nauczyciele.join(', ') || '—';
    document.getElementById('tiro-prog-opis').textContent = p.opis || '—';
    document.getElementById('tiro-prog-liczby').textContent =
      `${(t.par ?? 0)}/${p.cel} — ${p.procent}% (brakuje ${p.brakuje})`;
    document.getElementById('tiro-pasek').style.width = Math.min(p.procent || 0, 100) + '%';
    const tb = document.querySelector('#tiro-zrodla tbody');
    tb.innerHTML = '';
    for (const [zrodlo, ile] of Object.entries(t.zrodla || {})) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${zrodlo}</td><td>${ile}</td>`;
      tb.appendChild(tr);
    }
  } catch (e) { /* panel poboczny — cisza, nie psujemy reszty dashboardu */ }
}

setInterval(odswiez, 2000);
setInterval(ladujWykres, 5000);   // wykres świeży co 5s
odswiezTiro();
setInterval(odswiezTiro, 5000);   // zbiór rośnie wolno — 5s w zupełności wystarczy
</script>
</body></html>"""


def obsluz_sciezke(path: str, stan, odbiornik=None, magazyn=None) -> Tuple[int, str, bytes]:
    """
    Czysty GET router (testowalny bez gniazda). Zwraca (status, content_type, body_bytes).
      GET /                        → HTML panelu
      GET /stan.json               → StanDashboardu + webhook stats + symbole_swiec
      GET /tiro.json               → postęp Szkoły TIRO (NOTARIUS: pary nauczyciel→odpowiedź)
      GET /godlo.svg               → SVG godła
      GET /wykresy/{SYMBOL}.json   → świece: webhook TV (W-354) LUB feed MEXC (W-361)
      inne                         → 404

    magazyn (MagazynSwiec, W-361): źródło świec z naszego DataLoadera/MEXC — serwowane
    gdy webhook nie ma historii dla symbolu. Symbole obu źródeł łączone w selektorze.
    """
    sciezka = path.split("?", 1)[0]
    if sciezka in ("/", "/index.html"):
        return 200, "text/html; charset=utf-8", _html_strona().encode("utf-8")
    if sciezka == "/praetorium":
        # PRAETORIUM (Kwatera Główna) — WIDOK, nie drugi serwer (Prawo XVI).
        # Import leniwy: kokpit kosztuje ~330 ms odczytów, więc płacimy tylko gdy ktoś wejdzie.
        from imperium.swiatynie.praetorium import render_praetorium, zbierz_stan
        return (200, "text/html; charset=utf-8",
                render_praetorium(zbierz_stan()).encode("utf-8"))
    if sciezka == "/stan.json":
        dane = stan_do_json(stan)
        symbole = set()
        if odbiornik is not None:
            dane["webhook"] = odbiornik.statystyki()
            symbole.update(dane["webhook"].get("symbole", []))
        if magazyn is not None:
            symbole.update(magazyn.symbole())
        dane["symbole_swiec"] = sorted(symbole)
        body = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", body
    if sciezka == "/tiro.json":
        # Panel TIRO (Szkoła — postęp zbierania par przez NOTARIUSA). Świadomie NIEZALEŻNY
        # od `stan` pętli: zbiór rośnie od każdego wywołania Hyginusa (zwiad, auto-lekcje),
        # nie tylko podczas handlu — panel ma pokazywać prawdę nawet gdy pętla nic nie robi.
        try:
            from imperium.biblioteki.notarius import statystyki
            dane = statystyki()
        except Exception as e:  # noqa: BLE001 — panel poboczny NIGDY nie wywraca dashboardu
            dane = {"blad": str(e), "par": 0,
                    "postep": {"cel": 0, "procent": 0.0, "brakuje": 0, "opis": "—"}}
        body = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", body
    if sciezka == "/godlo.svg":
        try:
            from imperium.swiatynie.godlo import generuj_godlo
            return 200, "image/svg+xml", generuj_godlo(rozmiar=64, podpis=False).encode("utf-8")
        except Exception:  # noqa: BLE001 — godło opcjonalne, panel działa bez niego
            return 200, "image/svg+xml", b"<svg xmlns='http://www.w3.org/2000/svg'/>"
    if sciezka.startswith("/wykresy/") and sciezka.endswith(".json"):
        symbol = sciezka[len("/wykresy/"):-len(".json")].upper()
        swiece = []
        if odbiornik is not None:
            swiece = odbiornik.swiecze_json(symbol)
        if not swiece and magazyn is not None:   # W-361: fallback na feed MEXC
            swiece = magazyn.get(symbol)
        body = json.dumps(swiece, ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", body
    return 404, "text/plain; charset=utf-8", "404 — nieznana ścieżka".encode("utf-8")


def obsluz_post(path: str, body: bytes, odbiornik=None) -> Tuple[int, str, bytes]:
    """
    Czysty POST router (W-354 webhook). Zwraca (status, content_type, body_bytes).
      POST /webhook/tv → parsuje alert TradingView, dodaje do OdbiornikWebhook
    """
    sciezka = path.split("?", 1)[0]
    if sciezka == "/webhook/tv":
        if odbiornik is None:
            resp = {"ok": False, "blad": "odbiornik nie skonfigurowany"}
            return 503, "application/json; charset=utf-8", json.dumps(resp).encode()
        ok = odbiornik.dodaj_raw(body)
        if ok:
            resp = {"ok": True, "w_kolejce": odbiornik._q.qsize()}
        else:
            resp = {"ok": False, "blad": "parsowanie lub kolejka pełna"}
        status = 200 if ok else 400
        return status, "application/json; charset=utf-8", json.dumps(resp).encode()
    return 404, "text/plain; charset=utf-8", "404 — nieznana ścieżka POST".encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    """Cienki adapter http.server → obsluz_sciezke/obsluz_post. Stan z atrybutów serwera."""

    def do_GET(self):  # noqa: N802
        stan = getattr(self.server, "stan_dashboardu", None)
        odbiornik = getattr(self.server, "odbiornik_webhook", None)
        magazyn = getattr(self.server, "magazyn_swiec", None)
        status, ctype, body = obsluz_sciezke(self.path, stan, odbiornik, magazyn)
        self._odpowiedz(status, ctype, body)

    def do_POST(self):  # noqa: N802
        odbiornik = getattr(self.server, "odbiornik_webhook", None)
        dl = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(dl) if dl > 0 else b""
        status, ctype, resp_body = obsluz_post(self.path, body, odbiornik)
        self._odpowiedz(status, ctype, resp_body)

    def _odpowiedz(self, status: int, ctype: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")  # TV webhook z zewnątrz
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # noqa: ANN002 — cisza, nie zaśmiecaj logów
        pass


class SerwerDashboard:
    """
    Serwer panelu w wątku w tle (W-346 + W-354).
    aktualizuj(stan) podmienia migawkę co bar.
    podepnij_webhook(odbiornik) aktywuje POST /webhook/tv.

    Domyślnie bind 127.0.0.1 (panel tylko lokalny — nie wychodzi na świat).
    """

    def __init__(self, port: int = 8777, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self._serwer: Optional[HTTPServer] = None
        self._watek: Optional[threading.Thread] = None
        self._stan = _PustyStan()
        self._odbiornik = None
        self._magazyn = MagazynSwiec()   # W-361: feed świec z DataLoadera/MEXC

    def aktualizuj(self, stan) -> None:
        """Podmienia bieżącą migawkę stanu (wołane co bar z pętli live)."""
        self._stan = stan
        if self._serwer is not None:
            self._serwer.stan_dashboardu = stan

    def podaj_swiece(self, symbol: str, bary) -> None:
        """
        W-361: wrzuca bary (format Imperium) do magazynu świec — wykres MEXC bez
        webhooka TV. Wołane co bar z pętli live dla każdego symbolu z bary_per.
        """
        self._magazyn.podaj(symbol, bary)

    def podepnij_webhook(self, odbiornik) -> None:
        """
        Rejestruje OdbiornikWebhook — aktywuje POST /webhook/tv (W-354).
        Wywołaj przed start() lub po — działa w obu przypadkach.
        """
        self._odbiornik = odbiornik
        if self._serwer is not None:
            self._serwer.odbiornik_webhook = odbiornik
        logger.info("[Dashboard] Webhook TV zarejestrowany → POST /webhook/tv")

    def start(self) -> None:
        """Startuje serwer w wątku-daemonie (nie blokuje pętli tradingowej)."""
        if self._serwer is not None:
            return
        self._serwer = HTTPServer((self.host, self.port), DashboardHandler)
        self._serwer.stan_dashboardu = self._stan
        self._serwer.odbiornik_webhook = self._odbiornik
        self._serwer.magazyn_swiec = self._magazyn
        self._watek = threading.Thread(target=self._serwer.serve_forever, daemon=True)
        self._watek.start()
        logger.info(
            "[Dashboard] Panel Kapitolu: http://%s:%d  |  Webhook: POST /webhook/tv",
            self.host, self.port,
        )

    def stop(self) -> None:
        """Zatrzymuje serwer i wątek."""
        if self._serwer is not None:
            self._serwer.shutdown()
            self._serwer.server_close()
            self._serwer = None
            self._watek = None


class _PustyStan:
    """Domyślny pusty stan zanim pętla poda pierwszą migawkę (Prawo XV — nie crash)."""
    symbol = "—"
    rezim = "OCZEKIWANIE"
    kierunek_legatus = "NEUTRAL"
    pewnosc = 0.0
    kapital = 0.0
    kapital_start = 0.0
    postawa_gubernatora = "NORMALNY"
    bary_przetworzone = 0
    decyzje_wejscia = 0
    weta = 0
    bledy = 0
    pozycje: list = []
    neurony_top: list = []
