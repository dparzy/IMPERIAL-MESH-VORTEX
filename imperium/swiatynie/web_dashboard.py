"""
🌐 WEB DASHBOARD — Panel Kapitolu (W-346 + W-354, realizuje W-004 + W-031).

W-346: Panel webowy (http://localhost:8777) — rój 78 neuronów widoczny w przeglądarce.
W-354: TradingView Webhook Receiver — alerty z TV wchodzą przez POST /webhook/tv
       i trafiają do roju; wykres świecowy (Lightweight Charts) renderuje bary na żywo.

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

function kolorPnl(v){return v>0?'zielony':v<0?'czerwony':''}

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

    /* Update webhook status */
    if (s.webhook) {
      const w = s.webhook;
      document.getElementById('webhook-status').textContent =
        `webhook: ${w.lacznie_alertow} alertów | ${w.bledy_parsowania} błędów`;
      /* Update symbol selector */
      const sel = document.getElementById('sel-symbol');
      const obecne = new Set([...sel.options].map(o => o.value));
      for (const sym of (w.symbole || [])) {
        if (!obecne.has(sym)) {
          const opt = document.createElement('option');
          opt.value = sym; opt.textContent = sym;
          sel.appendChild(opt);
        }
      }
      /* Auto-select first symbol if none selected */
      if (!aktywnySymbol && w.symbole && w.symbole.length) {
        aktywnySymbol = w.symbole[0];
        sel.value = aktywnySymbol;
        ladujWykres();
      }
    }

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
setInterval(odswiez, 2000);
setInterval(ladujWykres, 5000);   // wykres świeży co 5s
</script>
</body></html>"""


def obsluz_sciezke(path: str, stan, odbiornik=None) -> Tuple[int, str, bytes]:
    """
    Czysty GET router (testowalny bez gniazda). Zwraca (status, content_type, body_bytes).
      GET /                        → HTML panelu
      GET /stan.json               → bieżący StanDashboardu + webhook stats jako JSON
      GET /godlo.svg               → SVG godła
      GET /wykresy/{SYMBOL}.json   → historia świec dla symbolu (W-354)
      inne                         → 404
    """
    sciezka = path.split("?", 1)[0]
    if sciezka in ("/", "/index.html"):
        return 200, "text/html; charset=utf-8", _html_strona().encode("utf-8")
    if sciezka == "/stan.json":
        dane = stan_do_json(stan)
        if odbiornik is not None:
            dane["webhook"] = odbiornik.statystyki()
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
        if odbiornik is not None:
            swiece = odbiornik.swiecze_json(symbol)
        else:
            swiece = []
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
        status, ctype, body = obsluz_sciezke(self.path, stan, odbiornik)
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

    def aktualizuj(self, stan) -> None:
        """Podmienia bieżącą migawkę stanu (wołane co bar z pętli live)."""
        self._stan = stan
        if self._serwer is not None:
            self._serwer.stan_dashboardu = stan

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
