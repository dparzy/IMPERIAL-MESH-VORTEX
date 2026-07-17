"""
🏛️ CENSOR SPRZĘTU — organ „oczu" mierzący majątek maszyny (Prawo XV).

Rzymski Censor prowadził census i przydzielał obywateli do KLAS MAJĄTKOWYCH
(classis) wg posiadanego majątku. Ten organ robi to samo dla ŻELAZA komputera:
mierzy CPU / RAM / GPU, przydziela maszynę do KLASY (tier modelu LLM), a przy
KAŻDEJ zmianie majątku (wzrost RAM, pojawienie się GPU CUDA) podnosi ALARM
POTENCJAŁU (Prawo XV): „stać cię teraz na większy model / trening lokalny /
rola X może przejść na lokalne — MIGRUJ".

Kontekst — projekt TIRO (lokalny LLM-uczeń): uczeń dobiera rozmiar modelu do
KLASY maszyny. Dziś Fujitsu Lifebook E754 (i5-4200M, 16 GB, brak CUDA) = klasa
PEDES (mały model tylko-CPU). Po migracji na sprzęt z GPU CENSOR SAM wykryje
skok i zażąda awansu — nie zgadujemy z pamięci (Prawo XVII, Prawo I).

DOWÓD, NIE ZAŁOŻENIE (Prawo I): mierzy ŻYWY sprzęt (ctypes / /proc / nvidia-smi),
nie ufa zapisom. Baseline leży w git → po `git pull` na nowej maszynie
porównanie live↔baseline ujawnia migrację (most między maszynami).

Bez zależności zewnętrznych (stdlib: os, platform, ctypes, subprocess, json,
datetime, pathlib) → działa wszędzie, także gdy `psutil` niedostępny.

Uruchom:  python -m imperium.oczy.censor_sprzetu            # raport (domyślnie)
          python -m imperium.oczy.censor_sprzetu migawka    # surowy JSON sprzętu
          python -m imperium.oczy.censor_sprzetu klasa       # sama klasa + model
          python -m imperium.oczy.censor_sprzetu zmiana      # wykryj migrację (Prawo XV)
          python -m imperium.oczy.censor_sprzetu zatwierdz   # zaakceptuj nowy baseline
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
BAZA_BASELINE = ROOT / "bibliotheca_ulpia" / "dane" / "censor_sprzet.json"

# Ile GB różnicy RAM traktujemy jako realną zmianę (a nie szum pomiaru/rezerwacji).
PROG_RAM_DELTA_GB = 1.0


# ── KLASY MAJĄTKOWE (classis) — rosnąca ranga = potężniejszy sprzęt ──────────
# Rzymski census przydzielał do klas wg majątku. Tu majątkiem jest żelazo, a
# „klasą" — największy model LLM, który maszyna realnie uciągnie. Ranga rośnie:
# PROLETARIUS (najbiedniejszy, liczony „po głowach") → CONSUL (workstation z GPU).
KLASY = [
    {
        "klasa": "PROLETARIUS",
        "ranga": 0,
        "model_zakres": "≤1.5B (Q4) — tylko najlżejsze zadania",
        "opis": "brak GPU CUDA i < 12 GB RAM — najbiedniejsza maszyna",
    },
    {
        "klasa": "PEDES",
        "ranga": 1,
        "model_zakres": "1–3B szybko (Q4) / 7–8B wsadowo w tle (wolno)",
        "opis": "brak GPU CUDA, ≥ 12 GB RAM — inferencja tylko-CPU (obecny Fujitsu)",
    },
    {
        "klasa": "EQUES",
        "ranga": 2,
        "model_zakres": "3–8B na GPU / lekki LoRA lokalnie",
        "opis": "GPU CUDA 4–8 GB VRAM — jeździec: stać go na przyśpieszenie",
    },
    {
        "klasa": "PRAETOR",
        "ranga": 3,
        "model_zakres": "7–14B na GPU / pełny trening LoRA/QLoRA lokalnie",
        "opis": "GPU CUDA 8–24 GB VRAM — urzędnik z realną władzą obliczeniową",
    },
    {
        "klasa": "CONSUL",
        "ranga": 4,
        "model_zakres": "30B+ / pełny fine-tuning lokalny",
        "opis": "GPU CUDA ≥ 24 GB VRAM (lub multi-GPU) — najwyższa władza",
    },
]
_KLASA_WG_RANGI = {k["ranga"]: k for k in KLASY}


# ── POMIAR ŻYWEGO SPRZĘTU (Prawo I — mierz, nie zgaduj) ──────────────────────
def _ram_gb() -> Optional[float]:
    """Całkowity RAM w GB. Windows: ctypes; Linux: /proc/meminfo; else None."""
    try:
        if sys.platform.startswith("win"):
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return round(stat.ullTotalPhys / (1024 ** 3), 2)
            return None
        # Linux / WSL
        meminfo = Path("/proc/meminfo")
        if meminfo.exists():
            for line in meminfo.read_text().splitlines():
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return round(kb / (1024 ** 2), 2)
        return None
    except Exception:
        return None


def _cpu_nazwa() -> str:
    """Czytelna nazwa CPU (best-effort, stdlib)."""
    try:
        cpuinfo = Path("/proc/cpuinfo")
        if cpuinfo.exists():
            for line in cpuinfo.read_text().splitlines():
                if "model name" in line:
                    return line.split(":", 1)[1].strip()
        # Windows/macOS fallback
        nazwa = platform.processor() or os.getenv("PROCESSOR_IDENTIFIER", "")
        return nazwa.strip() or platform.machine() or "nieznany"
    except Exception:
        return "nieznany"


def _cpu_logiczne() -> int:
    """Liczba logicznych procesorów (0 = nieznana)."""
    return os.cpu_count() or 0


def _gpu_cuda() -> Dict[str, Any]:
    """
    Wykrywa GPU NVIDIA/CUDA przez `nvidia-smi` (jedyny pewny sygnał, że lokalny
    trening/akceleracja są realne). Brak nvidia-smi = brak CUDA (iGPU Intel/AMD
    nie liczy się do treningu LLM). Zwraca vram najsilniejszej karty.
    """
    brak = {"cuda": False, "vram_gb": 0.0, "nazwa": None}
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=6,
            encoding="utf-8", errors="replace",
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return brak
    if out.returncode != 0 or not out.stdout.strip():
        return brak
    najlepsza = brak.copy()
    for line in out.stdout.strip().splitlines():
        czesci = [c.strip() for c in line.split(",")]
        if len(czesci) < 2:
            continue
        nazwa = czesci[0]
        try:
            vram_gb = round(float(czesci[1]) / 1024.0, 2)  # MiB → GiB
        except ValueError:
            continue
        if vram_gb >= najlepsza["vram_gb"]:
            najlepsza = {"cuda": True, "vram_gb": vram_gb, "nazwa": nazwa}
    return najlepsza


def migawka_sprzetu() -> Dict[str, Any]:
    """Pełna migawka żywego sprzętu — jedno źródło prawdy o „majątku" maszyny."""
    gpu = _gpu_cuda()
    return {
        "platforma": f"{platform.system()} {platform.release()}".strip(),
        "cpu_nazwa": _cpu_nazwa(),
        "cpu_logiczne": _cpu_logiczne(),
        "ram_gb": _ram_gb(),
        "gpu_cuda": gpu["cuda"],
        "gpu_vram_gb": gpu["vram_gb"],
        "gpu_nazwa": gpu["nazwa"],
        "znacznik": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# ── KLASYFIKACJA (przydział do classis) ──────────────────────────────────────
def sklasyfikuj(mig: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przydziela maszynę do KLASY majątkowej wg mierzonego sprzętu. Próg główny =
    obecność i wielkość GPU CUDA (największy skok mocy), potem RAM. Nieznany RAM
    (None) traktujemy zachowawczo jako < 12 GB (nie zawyżamy klasy — Prawo I).
    """
    cuda = bool(mig.get("gpu_cuda"))
    vram = float(mig.get("gpu_vram_gb") or 0.0)
    ram = mig.get("ram_gb")
    ram = float(ram) if ram is not None else 0.0

    if cuda and vram >= 24:
        ranga = 4
    elif cuda and vram >= 8:
        ranga = 3
    elif cuda and vram >= 4:
        ranga = 2
    elif ram >= 12:
        ranga = 1
    else:
        ranga = 0
    return dict(_KLASA_WG_RANGI[ranga])


def rekomendowany_tier() -> Dict[str, Any]:
    """Skrót dla TIRO i innych organów: klasa + zakres modelu dla ŻYWEGO sprzętu."""
    return sklasyfikuj(migawka_sprzetu())


# ── BASELINE + WYKRYWANIE ZMIAN (Prawo XV) ───────────────────────────────────
def wczytaj_baseline() -> Optional[Dict[str, Any]]:
    """Ostatnio zatwierdzona migawka (None = pierwszy cenzus na tej gałęzi)."""
    if not BAZA_BASELINE.exists():
        return None
    try:
        import json
        return json.loads(BAZA_BASELINE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def zapisz_baseline(mig: Dict[str, Any]) -> None:
    """Zapisuje migawkę jako nowy baseline (wersjonowany w git — most maszyn)."""
    import json
    BAZA_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BAZA_BASELINE.write_text(
        json.dumps(mig, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _zmiany_pol(base: Dict[str, Any], live: Dict[str, Any]) -> List[str]:
    """Lista czytelnych różnic sprzętowych (pomija znacznik czasu)."""
    zmiany: List[str] = []
    rb, rl = base.get("ram_gb"), live.get("ram_gb")
    if rb is not None and rl is not None and abs(rl - rb) >= PROG_RAM_DELTA_GB:
        zmiany.append(f"RAM: {rb} GB → {rl} GB")
    if bool(base.get("gpu_cuda")) != bool(live.get("gpu_cuda")):
        zmiany.append(
            f"GPU CUDA: {'jest' if base.get('gpu_cuda') else 'brak'} → "
            f"{'jest' if live.get('gpu_cuda') else 'brak'}"
        )
    vb, vl = float(base.get("gpu_vram_gb") or 0), float(live.get("gpu_vram_gb") or 0)
    if abs(vl - vb) >= 0.5:
        zmiany.append(f"VRAM GPU: {vb} GB → {vl} GB")
    if base.get("cpu_logiczne") != live.get("cpu_logiczne"):
        zmiany.append(f"CPU wątki: {base.get('cpu_logiczne')} → {live.get('cpu_logiczne')}")
    if (base.get("cpu_nazwa") or "") != (live.get("cpu_nazwa") or ""):
        zmiany.append(f"CPU: {base.get('cpu_nazwa')} → {live.get('cpu_nazwa')}")
    if (base.get("platforma") or "") != (live.get("platforma") or ""):
        zmiany.append(f"Platforma: {base.get('platforma')} → {live.get('platforma')}")
    return zmiany


def wykryj_zmiane() -> Dict[str, Any]:
    """
    Porównuje ŻYWY sprzęt z baseline i podnosi ALARMY POTENCJAŁU (Prawo XV).
    Read-only: NIE nadpisuje baseline (akceptacja to jawny krok `zatwierdz`),
    żeby alarm był widoczny na starcie każdej sesji aż Cezar go zatwierdzi.
    """
    live = migawka_sprzetu()
    klasa_live = sklasyfikuj(live)
    base = wczytaj_baseline()

    if base is None:
        return {
            "pierwszy_cenzus": True,
            "zmiany": [],
            "alarmy": [],
            "klasa_live": klasa_live,
            "klasa_base": None,
            "live": live,
        }

    klasa_base = sklasyfikuj(base)
    zmiany = _zmiany_pol(base, live)
    alarmy: List[str] = []

    if klasa_live["ranga"] > klasa_base["ranga"]:
        alarmy.append(
            f"🚨 UTRATA POTENCJAŁU (Prawo XV): AWANS KLASY "
            f"{klasa_base['klasa']} → {klasa_live['klasa']}. "
            f"Uciągniesz teraz: {klasa_live['model_zakres']}. "
            f"MIGRUJ TIRO na większy model i rozważ przejęcie ról nauczycieli."
        )
    elif klasa_live["ranga"] < klasa_base["ranga"]:
        alarmy.append(
            f"⚠️ DEGRADACJA KLASY {klasa_base['klasa']} → {klasa_live['klasa']} "
            f"(słabsza maszyna). Zejdź TIRO na: {klasa_live['model_zakres']} — "
            f"żeby nie zawiesić sprzętu."
        )

    if bool(live.get("gpu_cuda")) and not bool(base.get("gpu_cuda")):
        alarmy.append(
            f"🚨 POJAWIŁO SIĘ GPU CUDA ({live.get('gpu_nazwa')}, "
            f"{live.get('gpu_vram_gb')} GB VRAM) — trening lokalny LoRA/QLoRA i "
            f"akceleracja inferencji są TERAZ realne (były niemożliwe na CPU)."
        )
    elif not bool(live.get("gpu_cuda")) and bool(base.get("gpu_cuda")):
        alarmy.append(
            "⚠️ GPU CUDA ZNIKŁO — trening/akceleracja lokalna niedostępne, "
            "wróć na tryb tylko-CPU."
        )

    rb, rl = base.get("ram_gb"), live.get("ram_gb")
    if rb is not None and rl is not None and (rl - rb) >= 4.0:
        alarmy.append(
            f"🚨 RAM WZRÓSŁ {rb} → {rl} GB — większy model / dłuższy kontekst "
            f"mieszczą się teraz w pamięci."
        )

    return {
        "pierwszy_cenzus": False,
        "zmiany": zmiany,
        "alarmy": alarmy,
        "klasa_live": klasa_live,
        "klasa_base": klasa_base,
        "live": live,
    }


# ── RAPORT CZYTELNY ──────────────────────────────────────────────────────────
def raport() -> str:
    """Pełny raport CENSORA — sprzęt, klasa, model, alarmy Prawa XV."""
    wynik = wykryj_zmiane()
    live = wynik["live"]
    kl = wynik["klasa_live"]
    ram = f"{live['ram_gb']} GB" if live["ram_gb"] is not None else "?"
    gpu = (
        f"{live['gpu_nazwa']} ({live['gpu_vram_gb']} GB, CUDA)"
        if live["gpu_cuda"] else "brak CUDA (tylko CPU)"
    )
    linie = [
        "🏛️ CENSOR SPRZĘTU — cenzus majątku maszyny (Prawo XV)",
        "",
        f"   Platforma: {live['platforma']}",
        f"   CPU: {live['cpu_nazwa']}  ({live['cpu_logiczne']} wątków logicznych)",
        f"   RAM: {ram}",
        f"   GPU: {gpu}",
        "",
        f"   → KLASA: {kl['klasa']}  ({kl['opis']})",
        f"   → MODEL TIRO: {kl['model_zakres']}",
    ]
    if wynik["pierwszy_cenzus"]:
        linie += ["", "   ℹ️ Pierwszy cenzus na tej gałęzi — zapisz baseline: "
                  "`python -m imperium.oczy.censor_sprzetu zatwierdz`"]
    if wynik["zmiany"]:
        linie += ["", "   📐 Zmiany vs baseline:"]
        linie += [f"   • {z}" for z in wynik["zmiany"]]
    if wynik["alarmy"]:
        linie += ["", "   ⚡ ALARMY POTENCJAŁU:"]
        linie += [f"   {a}" for a in wynik["alarmy"]]
        linie += ["", "   (zaakceptuj nowy stan: "
                  "`python -m imperium.oczy.censor_sprzetu zatwierdz`)"]
    elif not wynik["pierwszy_cenzus"]:
        linie += ["", "   ✅ Sprzęt bez zmian — klasa stabilna."]
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="CENSOR SPRZĘTU — cenzus majątku maszyny (Prawo XV)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("migawka", help="Surowa migawka sprzętu (JSON)")
    sub.add_parser("klasa", help="Klasa majątkowa + zakres modelu")
    sub.add_parser("zmiana", help="Wykryj migrację sprzętu vs baseline (Prawo XV)")
    sub.add_parser("zatwierdz", help="Zaakceptuj żywy sprzęt jako nowy baseline")
    sub.add_parser("raport", help="Pełny raport (domyślnie)")
    args = p.parse_args()

    if args.cmd == "migawka":
        print(json.dumps(migawka_sprzetu(), indent=2, ensure_ascii=False))
    elif args.cmd == "klasa":
        kl = rekomendowany_tier()
        print(f"{kl['klasa']} — {kl['model_zakres']}  ({kl['opis']})")
    elif args.cmd == "zmiana":
        print(json.dumps(wykryj_zmiane(), indent=2, ensure_ascii=False, default=str))
    elif args.cmd == "zatwierdz":
        mig = migawka_sprzetu()
        zapisz_baseline(mig)
        kl = sklasyfikuj(mig)
        print(f"✅ Baseline zatwierdzony. Klasa: {kl['klasa']} — {kl['model_zakres']}")
    else:  # raport domyślnie
        print(raport())
