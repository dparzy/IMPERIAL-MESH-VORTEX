"""
🛡️ WALIDACJA KOLOSEUM — bramka anty-overfittingu (W-282, BIB-007).

Dwa twarde testy statystyczne PRZED dopuszczeniem strategii do żywego roju:

1. DEFLATED SHARPE RATIO (DSR) — Bailey & López de Prado (2014),
   "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest
   Overfitting, and Non-Normality".
   https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

   DLA NOWICJUSZA: gdy testujesz N strategii i wybierasz najlepszą, jej Sharpe
   jest ZAWYŻONY przez sam wybór (selection bias) — nawet czysty szum da
   "zwycięzcę". DSR odpowiada: jakie jest prawdopodobieństwo, że PRAWDZIWY
   Sharpe > 0, po uczciwej korekcie o (a) liczbę prób, (b) skośność i kurtozę
   zwrotów (krypto = grube ogony!), (c) długość próby.
   DSR ≥ 0.95 → ufamy; DSR < 0.95 → strategia może być szczęściarzem z loterii.

2. PBO przez CSCV — Bailey, Borwein, López de Prado, Zhu (2015),
   "The Probability of Backtest Overfitting".
   https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf

   DLA NOWICJUSZA: dzielimy historię na S bloków, bierzemy WSZYSTKIE podziały
   na połowę treningową/testową C(S, S/2). W każdym podziale wybieramy
   strategię najlepszą in-sample i patrzymy, jaki ma RANKING out-of-sample.
   PBO = odsetek podziałów, w których zwycięzca IS wypada PONIŻEJ MEDIANY OOS.
   PBO ≈ 0.5 → wybór najlepszego IS nic nie mówi o OOS (czysty overfitting).
   Próg Imperium: PBO < 0.20 (konserwatywnie; literatura: <0.5 to minimum).

Zero zależności poza numpy (Phi przez math.erf). Prawo I: matematyka, nie opinia.
"""

import math
from itertools import combinations
from typing import List, Sequence

import numpy as np

# Stała Eulera-Mascheroniego (do E[max] przy N próbach)
EULER_GAMMA = 0.5772156649015329

# Progi bramki Imperium (konserwatywne)
PROG_DSR = 0.95     # P(prawdziwy Sharpe > 0) musi być ≥ 95%
PROG_PBO = 0.20     # prawdopodobieństwo overfittingu musi być < 20%


def _phi(x: float) -> float:
    """Dystrybuanta N(0,1) przez erf — bez scipy."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _phi_inv(p: float) -> float:
    """Odwrotna dystrybuanta N(0,1) — aproksymacja Acklama (|błąd|<1.15e-9)."""
    if not (0.0 < p < 1.0):
        raise ValueError("p musi być w (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > p_high:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# ─── 1. DEFLATED SHARPE RATIO ─────────────────────────────────────────────────

def sharpe_zerowy(n_prob: int, var_sharpe: float) -> float:
    """
    SR₀ — oczekiwane maksimum Sharpe z n_prob prób CZYSTEGO SZUMU.
    E[max] ≈ √V[SR] · ((1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)))
    To poprzeczka, którą zawyżył sam WYBÓR najlepszej strategii.
    """
    if n_prob < 1:
        raise ValueError("n_prob musi być ≥ 1")
    if n_prob == 1:
        return 0.0  # jedna próba = brak selection bias
    if var_sharpe <= 0:
        return 0.0
    sd = math.sqrt(var_sharpe)
    return sd * ((1 - EULER_GAMMA) * _phi_inv(1 - 1.0 / n_prob)
                 + EULER_GAMMA * _phi_inv(1 - 1.0 / (n_prob * math.e)))


def deflated_sharpe(zwroty: Sequence[float], n_prob: int = 1,
                    var_sharpe_prob: "float | None" = None) -> dict:
    """
    DSR = Φ( (SR_obs − SR₀)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²) )

    zwroty: seria zwrotów strategii per bar/trade (ta sama częstotliwość co SR).
    n_prob: ile strategii/wariantów PRZETESTOWANO zanim wybrano tę (uczciwie!).
    var_sharpe_prob: wariancja Sharpe między próbami (None → wariancja
        estymatora SR z tej próby: (1+SR²/2)/T — konserwatywny fallback).

    Zwraca dict: sharpe, sr0, dsr (P[prawdziwy SR>0]), ok (dsr ≥ PROG_DSR).
    """
    z = np.asarray(list(zwroty), dtype=float)
    t = z.size
    if t < 10:
        return {"sharpe": None, "sr0": None, "dsr": 0.0, "ok": False,
                "powod": f"za mało obserwacji ({t} < 10)"}
    sd = z.std(ddof=1)
    if sd == 0:
        return {"sharpe": None, "sr0": None, "dsr": 0.0, "ok": False,
                "powod": "zerowa wariancja zwrotów (martwa strategia)"}
    sr = float(z.mean() / sd)
    # momenty wyższe (nienormalność — krypto ma grube ogony)
    m = z - z.mean()
    skew = float((m**3).mean() / sd**3)
    kurt = float((m**4).mean() / sd**4)          # surowa kurtoza (Normal=3)
    if var_sharpe_prob is None:
        var_sharpe_prob = (1 + 0.5 * sr * sr) / t
    sr0 = sharpe_zerowy(n_prob, var_sharpe_prob)
    mianownik = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if mianownik <= 0:
        return {"sharpe": sr, "sr0": sr0, "dsr": 0.0, "ok": False,
                "powod": "patologiczne momenty (mianownik ≤ 0)"}
    statystyka = (sr - sr0) * math.sqrt(t - 1) / math.sqrt(mianownik)
    dsr = _phi(statystyka)
    return {"sharpe": round(sr, 4), "sr0": round(sr0, 4),
            "dsr": round(dsr, 4), "ok": dsr >= PROG_DSR, "powod": ""}


# ─── 2. PBO przez CSCV ────────────────────────────────────────────────────────

def pbo_cscv(macierz_zwrotow: "np.ndarray | List[List[float]]",
             s_blokow: int = 10) -> dict:
    """
    Probability of Backtest Overfitting przez CSCV (Bailey et al. 2015).

    macierz_zwrotow: T×N — T obserwacji (bary/trade'y), N strategii-kandydatów.
        UWAGA: podaj WSZYSTKIE testowane warianty, nie tylko zwycięzcę
        (zatajenie prób = oszukanie bramki = złamanie Prawa I).
    s_blokow: liczba bloków S (parzysta, 8–16 wg paperu).

    Procedura: wszystkie C(S, S/2) podziały bloków na train/test → w każdym
    wybierz najlepszą strategię in-sample (po Sharpe) → policz jej względny
    ranking out-of-sample ω ∈ (0,1) → logit λ=ln(ω/(1−ω)).
    PBO = frakcja podziałów z λ < 0 (zwycięzca IS poniżej mediany OOS).

    Zwraca dict: pbo, n_podzialow, ok (pbo < PROG_PBO).
    """
    m = np.asarray(macierz_zwrotow, dtype=float)
    if m.ndim != 2:
        raise ValueError("macierz_zwrotow musi być 2D (T obserwacji × N strategii)")
    t, n = m.shape
    if n < 2:
        return {"pbo": None, "n_podzialow": 0, "ok": False,
                "powod": "PBO wymaga ≥ 2 strategii-kandydatów"}
    if s_blokow % 2 != 0 or s_blokow < 4:
        raise ValueError("s_blokow musi być parzyste i ≥ 4")
    if t < s_blokow * 2:
        return {"pbo": None, "n_podzialow": 0, "ok": False,
                "powod": f"za mało obserwacji ({t}) na {s_blokow} bloków"}

    bloki = np.array_split(np.arange(t), s_blokow)
    polowa = s_blokow // 2
    logity = []
    for idx_train in combinations(range(s_blokow), polowa):
        maska_train = np.concatenate([bloki[i] for i in idx_train])
        maska_test = np.concatenate([bloki[i] for i in range(s_blokow)
                                     if i not in idx_train])
        sr_is = _sharpe_kolumn(m[maska_train])
        sr_oos = _sharpe_kolumn(m[maska_test])
        najlepszy = int(np.argmax(sr_is))
        # ranking zwycięzcy IS w rozkładzie OOS: ω = rank/(N+1) ∈ (0,1)
        rank = float((sr_oos < sr_oos[najlepszy]).sum() + 1)
        omega = rank / (n + 1)
        logity.append(math.log(omega / (1 - omega)))
    pbo = float(np.mean([l < 0 for l in logity]))
    return {"pbo": round(pbo, 4), "n_podzialow": len(logity),
            "ok": pbo < PROG_PBO, "powod": ""}


def _sharpe_kolumn(m: np.ndarray) -> np.ndarray:
    """Sharpe każdej kolumny (strategii); zerowa wariancja → −inf (martwa)."""
    sd = m.std(axis=0, ddof=1)
    mu = m.mean(axis=0)
    wynik = np.full(m.shape[1], -np.inf)
    zywa = sd > 0
    wynik[zywa] = mu[zywa] / sd[zywa]
    return wynik


# ─── 3. BRAMKA — jedno wejście dla Koloseum ───────────────────────────────────

def bramka_walidacji(zwroty_kandydata: Sequence[float],
                     macierz_wszystkich: "np.ndarray | List[List[float]] | None" = None,
                     n_prob: "int | None" = None,
                     s_blokow: int = 10) -> dict:
    """
    Pełna bramka W-282: strategia przechodzi TYLKO gdy DSR ≥ 0.95 ORAZ
    (gdy podano macierz wszystkich kandydatów) PBO < 0.20.

    zwroty_kandydata: zwroty wybranej strategii.
    macierz_wszystkich: T×N zwroty WSZYSTKICH testowanych wariantów (do PBO).
        None → PBO pominięte (tylko DSR; n_prob nadal koryguje selection bias).
    n_prob: liczba testowanych wariantów; None → N z macierzy lub 1.
    """
    if n_prob is None:
        if macierz_wszystkich is not None:
            n_prob = int(np.asarray(macierz_wszystkich).shape[1])
        else:
            n_prob = 1
    dsr = deflated_sharpe(zwroty_kandydata, n_prob=n_prob)
    wynik = {"dsr": dsr, "pbo": None,
             "ok": dsr["ok"], "powod": dsr.get("powod", "")}
    if macierz_wszystkich is not None:
        pbo = pbo_cscv(macierz_wszystkich, s_blokow=s_blokow)
        wynik["pbo"] = pbo
        wynik["ok"] = bool(dsr["ok"] and pbo["ok"])
        if not pbo["ok"] and not wynik["powod"]:
            wynik["powod"] = (pbo.get("powod")
                              or f"PBO={pbo['pbo']} ≥ {PROG_PBO} (overfitting)")
    if not dsr["ok"] and not wynik["powod"]:
        wynik["powod"] = (dsr.get("powod")
                          or f"DSR={dsr['dsr']} < {PROG_DSR} (Sharpe nieodporny na selection bias)")
    return wynik


# ─── 4. DWU-ZEGAROWY DSR (W-285.2 💎 unikat Imperium) ─────────────────────────

def bary_wolumenowe(bary: List[dict], wolumen_na_bar: "float | None" = None) -> List[dict]:
    """
    Trading-time Mandelbrota (BIB-009, W-144): agreguje bary kalendarzowe w bary
    o (w przybliżeniu) RÓWNYM WOLUMENIE. Rynek "tyka" aktywnością, nie zegarem:
    1 dzień paniki niesie więcej informacji niż tydzień ciszy.

    bary: lista dictów OHLCV (open/high/low/close/volume).
    wolumen_na_bar: próg wolumenu na 1 bar wolumenowy.
        None → automatycznie: total_volume / len(bary) (≈ tyle samo barów co wejście).

    Zwraca listę barów wolumenowych (open pierwszego, close ostatniego,
    high=max, low=min, volume=suma). Końcówka poniżej progu jest ODRZUCANA
    (niepełny bar = nieporównywalny — Prawo I).
    """
    if not bary:
        return []
    vols = [float(b.get("volume", 0.0)) for b in bary]
    total = sum(vols)
    if total <= 0:
        return []
    if wolumen_na_bar is None:
        wolumen_na_bar = total / len(bary)
    if wolumen_na_bar <= 0:
        raise ValueError("wolumen_na_bar musi być > 0")
    wynik: List[dict] = []
    akum = 0.0
    o = h = low = c = None
    for b in bary:
        v = float(b.get("volume", 0.0))
        if o is None:
            o = float(b["open"]); h = float(b["high"])
            low = float(b["low"])
        h = max(h, float(b["high"]))
        low = min(low, float(b["low"]))
        c = float(b["close"])
        akum += v
        if akum >= wolumen_na_bar:
            wynik.append({"open": o, "high": h, "low": low, "close": c,
                          "volume": akum})
            akum = 0.0
            o = None
    return wynik


def zwroty_z_barow(bary: List[dict]) -> List[float]:
    """Proste zwroty close-to-close z listy barów."""
    closes = [float(b["close"]) for b in bary]
    return [(closes[i] - closes[i - 1]) / closes[i - 1]
            for i in range(1, len(closes)) if closes[i - 1] != 0]


def bramka_dwuzegarowa(zwroty_kalendarzowe: Sequence[float],
                       bary_kalendarzowe: List[dict],
                       sygnal_fn,
                       n_prob: int = 1) -> dict:
    """
    💎 W-285.2 | Dwu-zegarowy DSR — ORYGINALNA bramka Imperium.

    DLA NOWICJUSZA: niektóre strategie "działają" w backteście tylko dlatego,
    że czas kalendarzowy nierówno rozkłada informację — długie ciche okresy
    sztucznie wygładzają krzywą. Liczymy DSR DWA RAZY: (1) na zwrotach
    kalendarzowych strategii, (2) na zwrotach tej samej strategii odtworzonej
    w TRADING-TIME (bary wolumenowe). Przechodzi tylko, gdy OBA zegary zielone.

    zwroty_kalendarzowe: zwroty strategii per bar kalendarzowy.
    bary_kalendarzowe: surowe OHLCV (do przeliczenia na bary wolumenowe).
    sygnal_fn: callable(bary) -> lista pozycji {-1, 0, +1} per bar — ta sama
        logika strategii, odpalona na barach wolumenowych. Zwrot strategii
        w trading-time = pozycja[i-1] · zwrot_baru[i] (bez look-ahead).
    n_prob: liczba testowanych wariantów (korekta selection bias).

    Zwraca dict: zegar_kalendarzowy, zegar_wolumenowy, ok (oba ✓), powod.
    """
    dsr_kal = deflated_sharpe(zwroty_kalendarzowe, n_prob=n_prob)
    vb = bary_wolumenowe(bary_kalendarzowe)
    if len(vb) < 12:
        return {"zegar_kalendarzowy": dsr_kal, "zegar_wolumenowy": None,
                "ok": False,
                "powod": f"za mało barów wolumenowych ({len(vb)} < 12)"}
    pozycje = list(sygnal_fn(vb))
    if len(pozycje) != len(vb):
        raise ValueError("sygnal_fn musi zwrócić pozycję dla każdego baru")
    zw_vb = zwroty_z_barow(vb)
    # pozycja z baru i-1 zarabia zwrot baru i (bez look-ahead, Prawo I)
    zw_strat_vb = [pozycje[i - 1] * zw_vb[i - 1] for i in range(1, len(vb))]
    dsr_vol = deflated_sharpe(zw_strat_vb, n_prob=n_prob)
    ok = bool(dsr_kal["ok"] and dsr_vol["ok"])
    powod = ""
    if not dsr_kal["ok"]:
        powod = f"zegar kalendarzowy: {dsr_kal.get('powod') or 'DSR=' + str(dsr_kal['dsr'])}"
    elif not dsr_vol["ok"]:
        powod = (f"zegar wolumenowy: {dsr_vol.get('powod') or 'DSR=' + str(dsr_vol['dsr'])}"
                 " — strategia żyje z nierównej gęstości czasu, nie z przewagi")
    return {"zegar_kalendarzowy": dsr_kal, "zegar_wolumenowy": dsr_vol,
            "ok": ok, "powod": powod}
