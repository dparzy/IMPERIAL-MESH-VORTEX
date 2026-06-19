"""
🌐 WEB DASHBOARD — Panel Kapitolu (W-346, realizuje W-004 + W-031).

Luka #3 ze skanu konkurencji (Freqtrade FreqUI, Jesse UI mają panel webowy; my
mieliśmy tylko LiveMonitor TUI + Telegram). Pozwala WIDZIEĆ walkę roju na żywo
w przeglądarce — ukryta utrata potencjału (Prawo XV): rój 76 neuronów decydował
„w ciemno", bez okna dla Cezara.

FILOZOFIA: ZERO ZALEŻNOŚCI (jak cały Imperium — runner bez deps). Zamiast FastAPI
używamy `http.server` ze stdlib + samowystarczalny HTML (inline CSS/JS, fetch).
Ten sam `StanDashboardu` co LiveMonitor (jedno źródło prawdy — Prawo XVI, nie dublujemy).

W-031 ROMAN NAMING: waluty dostają szlacheckie nazwy rzymskie (BTC=Capitolium…).
W-342 GODŁO: SVG Aquila+Vortex+Mesh osadzone w panelu.

ARCHITEKTURA (routing wydzielony — testowalny bez gniazda):
    obsluz_sciezke(path, stan) -> (status, content_type, body)   # czysta funkcja
    DashboardHandler                                              # cienki adapter http.server
    SerwerDashboard.aktualizuj(stan) / start() / stop()          # wątek w tle

Użycie (w pętli live):
    serwer = SerwerDashboard(port=8777)
    serwer.start()
    ...co bar...
    serwer.aktualizuj(stan_dashboardu)   # ten sam StanDashboardu co LiveMonitor
    # przeglądarka: http://localhost:8777  (auto-odświeża co 2 s przez /stan.json)

Bezpieczeństwo: bind domyślnie 127.0.0.1 (tylko lokalnie — panel nie wychodzi
na świat). Zero zleceń, zero kluczy — tylko odczyt stanu (Prawo I).
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
    """Samowystarczalny HTML panelu (inline CSS/JS). Pobiera /stan.json co 2 s."""
    return """<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<title>Kapitol Imperium</title>
<link rel="icon" href="/godlo.svg">
<style>
  :root{--zloto:#D4AF37;--purpura:#4A0E2E;--tlo:#0D0D14;--zielen:#2ecc71;--czerw:#e74c3c}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--tlo);color:#e8e8e8;font-family:'Segoe UI',system-ui,sans-serif;padding:24px}
  header{display:flex;align-items:center;gap:16px;border-bottom:2px solid var(--zloto);padding-bottom:16px;margin-bottom:24px}
  header img{width:64px;height:64px}
  h1{color:var(--zloto);font-size:24px;letter-spacing:2px}
  .siatka{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
  .karta{background:#16161f;border:1px solid #2a2a38;border-radius:10px;padding:16px}
  .karta .etykieta{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#888}
  .karta .wartosc{font-size:28px;font-weight:700;margin-top:6px}
  .zielony{color:var(--zielen)}.czerwony{color:var(--czerw)}.zloty{color:var(--zloto)}
  table{width:100%;border-collapse:collapse;margin-top:8px}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #2a2a38;font-size:14px}
  th{color:var(--zloto);text-transform:uppercase;font-size:11px;letter-spacing:1px}
  .sekcja-tytul{color:var(--zloto);font-size:14px;text-transform:uppercase;letter-spacing:2px;margin:24px 0 8px}
  .pasek{height:6px;background:#2a2a38;border-radius:3px;overflow:hidden;margin-top:4px}
  .pasek>div{height:100%;background:var(--zloto)}
  footer{margin-top:32px;color:#555;font-size:12px;text-align:center}
</style></head><body>
<header><img src="/godlo.svg" alt="godło"><h1>KAPITOL IMPERIUM</h1>
  <span id="rezim" class="zloty" style="margin-left:auto;font-size:18px"></span></header>
<div class="siatka">
  <div class="karta"><div class="etykieta">Kapitał</div><div class="wartosc" id="kapital">—</div></div>
  <div class="karta"><div class="etykieta">Zysk</div><div class="wartosc" id="zysk">—</div></div>
  <div class="karta"><div class="etykieta">Wejścia / Weta</div><div class="wartosc" id="wejscia">—</div></div>
  <div class="karta"><div class="etykieta">Gubernator</div><div class="wartosc zloty" id="gubernator" style="font-size:20px">—</div></div>
</div>
<div class="sekcja-tytul">⚔️ Otwarte pozycje</div>
<table id="pozycje"><thead><tr><th>Para</th><th>Nazwa</th><th>Kierunek</th><th>Wejście</th><th>Teraz</th><th>P&L</th><th>Wielkość</th></tr></thead><tbody></tbody></table>
<div class="sekcja-tytul">🧠 Czołowe neurony</div>
<table id="neurony"><thead><tr><th>Klucz</th><th>Kierunek</th><th>Pewność</th><th>Waga</th></tr></thead><tbody></tbody></table>
<footer>Imperium · panel lokalny · auto-odświeżanie co 2 s</footer>
<script>
function kolorPnl(v){return v>0?'zielony':v<0?'czerwony':''}
async function odswiez(){
  try{
    const s=await (await fetch('/stan.json')).json();
    document.getElementById('rezim').textContent=s.rezim+' · '+s.symbol;
    document.getElementById('kapital').textContent=s.kapital.toLocaleString()+' USDT';
    const z=document.getElementById('zysk');z.textContent=(s.zysk_pct>=0?'+':'')+s.zysk_pct+'%';
    z.className='wartosc '+kolorPnl(s.zysk_pct);
    document.getElementById('wejscia').textContent=s.decyzje_wejscia+' / '+s.weta;
    document.getElementById('gubernator').textContent=s.postawa_gubernatora;
    const tb=document.querySelector('#pozycje tbody');tb.innerHTML='';
    for(const p of s.pozycje){const tr=document.createElement('tr');
      tr.innerHTML=`<td>${p.symbol}</td><td class="zloty">${p.rzymska||'—'}</td>`+
        `<td>${p.kierunek}</td><td>${p.wejscie}</td><td>${p.aktualny}</td>`+
        `<td class="${kolorPnl(p.pnl_pct)}">${p.pnl_pct>=0?'+':''}${p.pnl_pct}%</td><td>${p.wielkosc}</td>`;
      tb.appendChild(tr);}
    if(!s.pozycje.length)tb.innerHTML='<tr><td colspan="7" style="color:#555">brak otwartych pozycji</td></tr>';
    const tn=document.querySelector('#neurony tbody');tn.innerHTML='';
    for(const n of s.neurony_top){const tr=document.createElement('tr');
      tr.innerHTML=`<td>${n.klucz}</td><td>${n.kierunek}</td><td>${n.pewnosc}</td><td>${n.waga}</td>`;
      tn.appendChild(tr);}
  }catch(e){document.getElementById('rezim').textContent='⚠ brak połączenia';}
}
odswiez();setInterval(odswiez,2000);
</script></body></html>"""


def obsluz_sciezke(path: str, stan) -> Tuple[int, str, bytes]:
    """
    Czysty router (testowalny bez gniazda). Zwraca (status, content_type, body_bytes).
      GET /            → HTML panelu
      GET /stan.json   → bieżący StanDashboardu jako JSON
      GET /godlo.svg   → SVG godła
      inne             → 404
    """
    sciezka = path.split("?", 1)[0]
    if sciezka in ("/", "/index.html"):
        return 200, "text/html; charset=utf-8", _html_strona().encode("utf-8")
    if sciezka == "/stan.json":
        body = json.dumps(stan_do_json(stan), ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", body
    if sciezka == "/godlo.svg":
        try:
            from imperium.swiatynie.godlo import generuj_godlo
            return 200, "image/svg+xml", generuj_godlo(rozmiar=64, podpis=False).encode("utf-8")
        except Exception:  # noqa: BLE001 — godło opcjonalne, panel działa bez niego
            return 200, "image/svg+xml", b"<svg xmlns='http://www.w3.org/2000/svg'/>"
    return 404, "text/plain; charset=utf-8", "404 — nieznana ścieżka".encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    """Cienki adapter http.server → obsluz_sciezke. stan czytany z serwera (atrybut)."""

    def do_GET(self):  # noqa: N802 — wymagana nazwa z BaseHTTPRequestHandler
        stan = getattr(self.server, "stan_dashboardu", None)
        status, ctype, body = obsluz_sciezke(self.path, stan)
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # cisza — nie zaśmiecaj logów requestami
        pass


class SerwerDashboard:
    """
    Serwer panelu w wątku w tle. aktualizuj(stan) podmienia migawkę co bar.

    Domyślnie bind 127.0.0.1 (panel tylko lokalny — nie wychodzi na świat).
    """

    def __init__(self, port: int = 8777, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self._serwer: Optional[HTTPServer] = None
        self._watek: Optional[threading.Thread] = None
        self._stan = _PustyStan()

    def aktualizuj(self, stan) -> None:
        """Podmienia bieżącą migawkę stanu (wołane co bar z pętli live)."""
        self._stan = stan
        if self._serwer is not None:
            self._serwer.stan_dashboardu = stan

    def start(self) -> None:
        """Startuje serwer w wątku-daemonie (nie blokuje pętli tradingowej)."""
        if self._serwer is not None:
            return
        self._serwer = HTTPServer((self.host, self.port), DashboardHandler)
        self._serwer.stan_dashboardu = self._stan
        self._watek = threading.Thread(target=self._serwer.serve_forever, daemon=True)
        self._watek.start()
        logger.info(f"[Dashboard] Panel Kapitolu: http://{self.host}:{self.port}")

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
