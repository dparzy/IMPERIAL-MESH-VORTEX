"""
LiveMonitor — TUI dashboard na żywo (W-341, Prawo XXIV: Widoczność Operacyjna).

Bez zewnętrznych zależności — czyste ANSI escape codes.
Wyświetla aktualny stan Imperium: reżim, pozycje, neurony, P&L, Gubernator.

Uruchomienie: wywoływane przez PętlęLive co N barów lub osobno.
"""

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


# ─── ANSI ─────────────────────────────────────────────────────────────────────

_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_WHITE  = "\033[37m"
_DIM    = "\033[2m"
_BG_DARK = "\033[40m"

_TEAL   = "\033[96m"
_ORANGE = "\033[33m"


def _kolor_kierunku(kierunek: str) -> str:
    if kierunek == "LONG":
        return _GREEN + _BOLD
    if kierunek == "SHORT":
        return _RED + _BOLD
    return _DIM


def _kolor_pnl(pnl: float) -> str:
    if pnl > 0:
        return _GREEN
    if pnl < 0:
        return _RED
    return _WHITE


def _kolor_rezimu(rezim: str) -> str:
    return {
        "TREND_STRONG": _GREEN,
        "RANGING": _CYAN,
        "VOLATILE": _YELLOW,
        "PANIC": _RED + _BOLD,
        "NORMAL": _WHITE,
    }.get(rezim, _WHITE)


def _pasek(wartosc: float, szerokosc: int = 10, znak: str = "█") -> str:
    """Pasek postępu [0,1] → ████░░░░░░."""
    wypelniony = max(0, min(szerokosc, int(wartosc * szerokosc)))
    return znak * wypelniony + "░" * (szerokosc - wypelniony)


def _clear() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")


# ─── Stan dashboardu ──────────────────────────────────────────────────────────

@dataclass
class StanPozycji:
    symbol: str
    kierunek: str           # LONG/SHORT
    wejscie: float
    aktualny: float
    wielkosc: float         # w USD
    sl: float = 0.0
    tp: float = 0.0

    @property
    def pnl_pct(self) -> float:
        if self.wejscie == 0:
            return 0.0
        if self.kierunek == "LONG":
            return (self.aktualny - self.wejscie) / self.wejscie
        return (self.wejscie - self.aktualny) / self.wejscie


@dataclass
class StanNeuronu:
    klucz: str
    kierunek: str
    pewnosc: float
    waga: float


@dataclass
class StanDashboardu:
    """Migawka stanu Imperium do wyświetlenia na TUI."""
    symbol: str = "???"
    rezim: str = "UNKNOWN"
    kierunek_legatus: str = "NEUTRAL"
    pewnosc: float = 0.0
    kapital: float = 0.0
    kapital_start: float = 0.0
    pozycje: List[StanPozycji] = field(default_factory=list)
    neurony_top: List[StanNeuronu] = field(default_factory=list)
    postawa_gubernatora: str = "NORMALNY"
    mnoznik_gubernatora: float = 1.0
    bary_przetworzone: int = 0
    decyzje_wejscia: int = 0
    weta: int = 0
    bledy: int = 0
    czas_ostatniego_bara: Optional[datetime] = None
    meta_bet_size: float = 0.0      # B-01 meta-labeling
    aktualny_rezim_turbo: Optional[bool] = None   # W-340 vol-gate
    dodatkowe: Dict[str, str] = field(default_factory=dict)
    # SPECULA (W-361) — świece OHLC w terminalu (opcjonalny panel, wymaga plotext).
    # bary: nasz format {timestamp, open, high, low, close, ...}. Puste → panel pominięty.
    swiece: List[Dict] = field(default_factory=list)
    # znaczniki wejść/wyjść bota na świecach: {timestamp, cena, kierunek, typ}
    znaczniki_swiec: List[Dict] = field(default_factory=list)
    swiece_wysokosc: int = 14       # wysokość panelu świec w liniach


# ─── Renderer ─────────────────────────────────────────────────────────────────

class LiveMonitor:
    """
    Prawo XXIV — Widoczność Operacyjna.
    Renderuje TUI dashboard do terminala. Zero zależności zewnętrznych.
    """

    SZEROKOSC = 72

    def __init__(self, odswiezaj_co_s: float = 0.0):
        self._odswiezaj = odswiezaj_co_s
        self._stan = StanDashboardu()

    def aktualizuj(self, stan: StanDashboardu) -> None:
        """Przyjmij nowy stan — wywołaj przed render()."""
        self._stan = stan

    def render(self, clear: bool = True) -> None:
        """Wyrenderuj dashboard do stdout."""
        if clear:
            _clear()
        s = self._stan
        w = self.SZEROKOSC
        linie = []

        # ── Nagłówek ──
        ts = s.czas_ostatniego_bara.strftime("%Y-%m-%d %H:%M:%S") if s.czas_ostatniego_bara else "--:--:--"
        linie.append(_BOLD + _TEAL + "╔" + "═" * (w - 2) + "╗" + _RESET)
        tytul = f"🏛️  IMPERIAL MESH VORTEX  ·  {ts}"
        pad = w - 2 - len(tytul) + 4  # +4 emoji adjustment
        linie.append(_BOLD + _TEAL + "║" + _RESET + _BOLD + f" {tytul}" + " " * max(0, pad - 1) + _TEAL + "║" + _RESET)
        linie.append(_TEAL + "╠" + "═" * (w - 2) + "╣" + _RESET)

        # ── Reżim + Legatus ──
        rkolor = _kolor_rezimu(s.rezim)
        kk = _kolor_kierunku(s.kierunek_legatus)
        pewnosc_bar = _pasek(s.pewnosc, 12)
        turbo_tag = ""
        if s.aktualny_rezim_turbo is True:
            turbo_tag = f"  {_YELLOW}[TURBO🌪️]{_RESET}"
        elif s.aktualny_rezim_turbo is False:
            turbo_tag = f"  {_DIM}[calm]{_RESET}"
        linie.append(
            f"║  REŻIM: {rkolor}{s.rezim:<16}{_RESET}"
            f"  SYGNAŁ: {kk}{s.kierunek_legatus:<8}{_RESET}"
            f"  {pewnosc_bar} {s.pewnosc:.0%}{turbo_tag}"
        )

        # ── Meta-bet (B-01) + Gubernator ──
        bet_bar = _pasek(s.meta_bet_size, 8)
        gkolor = _GREEN if s.postawa_gubernatora == "EKSPANSJA" else (
            _RED if s.postawa_gubernatora == "KWARANTANNA" else _WHITE)
        linie.append(
            f"║  META-BET: {bet_bar} {s.meta_bet_size:.0%}"
            f"   GUBERNATOR: {gkolor}{s.postawa_gubernatora}{_RESET}"
            f" ×{s.mnoznik_gubernatora:.2f}"
        )
        linie.append("║" + "─" * (w - 2) + "")

        # ── Kapitał + P&L ──
        pnl_total = s.kapital - s.kapital_start if s.kapital_start else 0.0
        pnl_pct = pnl_total / s.kapital_start if s.kapital_start else 0.0
        pkolor = _kolor_pnl(pnl_total)
        linie.append(
            f"║  KAPITAŁ: {_BOLD}${s.kapital:>10,.2f}{_RESET}"
            f"   P&L: {pkolor}{pnl_total:+.2f} ({pnl_pct:+.1%}){_RESET}"
            f"   BARY: {s.bary_przetworzone}"
        )
        linie.append(
            f"║  WEJŚCIA: {s.decyzje_wejscia}"
            f"   WETO: {s.weta}"
            f"   BŁĘDY: {s.bledy}"
        )

        # ── Otwarte pozycje ──
        if s.pozycje:
            linie.append("║" + "─" * (w - 2) + "")
            linie.append(f"║  POZYCJE ({len(s.pozycje)}):")
            for p in s.pozycje[:4]:
                kk2 = _kolor_kierunku(p.kierunek)
                pkol = _kolor_pnl(p.pnl_pct)
                linie.append(
                    f"║    {kk2}{p.symbol:<12}{_RESET} {p.kierunek:<5}"
                    f"  @{p.wejscie:.4f}→{p.aktualny:.4f}"
                    f"  {pkol}{p.pnl_pct:+.1%}{_RESET}"
                    f"  SL:{p.sl:.4f}"
                )

        # ── Top neurony ──
        if s.neurony_top:
            linie.append("║" + "─" * (w - 2) + "")
            linie.append(f"║  NEURONY (top {min(5, len(s.neurony_top))}):")
            for n in s.neurony_top[:5]:
                nkolor = _kolor_kierunku(n.kierunek)
                pasek = _pasek(n.pewnosc, 8)
                linie.append(
                    f"║    {nkolor}{n.klucz:<10}{_RESET}"
                    f" {n.kierunek:<7} {pasek} {n.pewnosc:.0%}"
                    f"  w={n.waga:.1f}"
                )

        # ── Dodatkowe info ──
        if s.dodatkowe:
            linie.append("║" + "─" * (w - 2) + "")
            for k, v in list(s.dodatkowe.items())[:3]:
                linie.append(f"║  {_DIM}{k}: {v}{_RESET}")

        linie.append(_TEAL + "╚" + "═" * (w - 2) + "╝" + _RESET)

        # ── SPECULA (W-361): panel świec OHLC w terminalu (opcjonalny) ──
        if s.swiece:
            from imperium.swiatynie.specula_swiec import render_swiece
            tytul = f"{s.symbol}  ·  świece"
            linie.append(render_swiece(
                s.swiece,
                wysokosc=s.swiece_wysokosc,
                szerokosc=w,
                tytul=tytul,
                znaczniki=s.znaczniki_swiec or None,
            ))

        print("\n".join(linie))
        sys.stdout.flush()

    def render_petla(self, pobierz_stan, odswiezaj_co_s: float = 5.0) -> None:
        """
        Pętla odświeżania — do użycia w osobnym wątku lub procesie.
        pobierz_stan: callable() → StanDashboardu
        """
        while True:
            try:
                self.aktualizuj(pobierz_stan())
                self.render()
                time.sleep(odswiezaj_co_s)
            except KeyboardInterrupt:
                break


# ─── Telegram alert (Prawo XXIV) ─────────────────────────────────────────────

class TelegramAlert:
    """
    Wysyła powiadomienia do Telegrama przez Bot API (HTTP POST).
    Klucze WYŁĄCZNIE przez env (Prawo bezpieczeństwa):
      TELEGRAM_BOT_TOKEN  — token bota (@BotFather)
      TELEGRAM_CHAT_ID    — ID chatu (twoje lub grupowe)
    Gdy brak kluczy: loguje ostrzeżenie, nie crashuje.
    """

    def __init__(self) -> None:
        import logging
        self._log = logging.getLogger("TelegramAlert")
        self._token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if not self._token or not self._chat_id:
            self._log.info(
                "[TelegramAlert] Brak TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID — "
                "powiadomienia wyłączone."
            )

    @property
    def aktywny(self) -> bool:
        return bool(self._token and self._chat_id)

    def wyslij(self, tekst: str, parse_mode: str = "Markdown") -> bool:
        """Wyślij wiadomość. Zwraca True jeśli sukces."""
        if not self.aktywny:
            return False
        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": self._chat_id,
            "text": tekst,
            "parse_mode": parse_mode,
        }).encode()
        try:
            req = urllib.request.Request(url, data=payload, method="POST")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            self._log.warning(f"[TelegramAlert] Błąd wysyłki: {e}")
            return False

    def alert_sygnal(self, symbol: str, kierunek: str, pewnosc: float,
                     rezim: str, kapital: float) -> bool:
        """Standardowy alert o sygnale wejścia."""
        emoji = "🟢" if kierunek == "LONG" else "🔴"
        tekst = (
            f"{emoji} *IMPERIUM SIGNAL*\n"
            f"`{symbol}` — *{kierunek}*\n"
            f"Pewność: `{pewnosc:.0%}`\n"
            f"Reżim: `{rezim}`\n"
            f"Kapitał: `${kapital:,.2f}`"
        )
        return self.wyslij(tekst)

    def alert_zamkniecie(self, symbol: str, pnl_pct: float,
                         kapital: float, powod: str = "") -> bool:
        """Alert o zamknięciu pozycji z P&L."""
        emoji = "✅" if pnl_pct > 0 else "❌"
        tekst = (
            f"{emoji} *CLOSE* `{symbol}`\n"
            f"P&L: `{pnl_pct:+.1%}`\n"
            f"Kapitał: `${kapital:,.2f}`"
        )
        if powod:
            tekst += f"\nPowód: `{powod}`"
        return self.wyslij(tekst)

    def alert_weto(self, powod: str, rezim: str) -> bool:
        """Alert gdy Imperium wstrzymuje handel (weto/panic)."""
        tekst = (
            f"⛔ *WETO IMPERIUM*\n"
            f"Powód: `{powod}`\n"
            f"Reżim: `{rezim}`"
        )
        return self.wyslij(tekst)

    def alert_blad(self, tresc: str) -> bool:
        """Alert o błędzie krytycznym."""
        return self.wyslij(f"🚨 *BŁĄD IMPERIUM*\n`{tresc}`")


# ─── Demo / test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime

    monitor = LiveMonitor()

    demo = StanDashboardu(
        symbol="BTCUSDT",
        rezim="TREND_STRONG",
        kierunek_legatus="LONG",
        pewnosc=0.78,
        kapital=52980.0,
        kapital_start=50000.0,
        pozycje=[
            StanPozycji("BTCUSDT", "LONG", 67800.0, 68900.0, 5000.0,
                        sl=66500.0, tp=71000.0),
            StanPozycji("ETHUSDT", "SHORT", 3520.0, 3490.0, 2000.0,
                        sl=3580.0, tp=3400.0),
        ],
        neurony_top=[
            StanNeuronu("X-01", "LONG", 0.82, 8.0),
            StanNeuronu("XII-03", "LONG", 0.75, 7.5),
            StanNeuronu("V-02", "LONG", 0.61, 6.0),
            StanNeuronu("Z-01", "NEUTRAL", 0.0, 5.0),
            StanNeuronu("BOCPD-01", "LONG", 0.55, 6.0),
        ],
        postawa_gubernatora="EKSPANSJA",
        mnoznik_gubernatora=1.3,
        bary_przetworzone=1247,
        decyzje_wejscia=18,
        weta=3,
        bledy=0,
        czas_ostatniego_bara=datetime.now(),
        meta_bet_size=0.73,
        aktualny_rezim_turbo=False,
        dodatkowe={
            "MasterSwitch": "TREND (VR=1.12, HL=42, AR1=+0.14)",
            "Top strategia": "XII-TR-001 PIORUN CEZARA (87% dopasowanie)",
        },
    )

    monitor.aktualizuj(demo)
    monitor.render(clear=False)

    print("\n--- Test TelegramAlert (bez kluczy — powinien logować info) ---")
    ta = TelegramAlert()
    print(f"Aktywny: {ta.aktywny}")
    ta.alert_sygnal("BTCUSDT", "LONG", 0.78, "TREND_STRONG", 52980.0)
