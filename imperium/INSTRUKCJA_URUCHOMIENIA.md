# 🚀 JAK URUCHOMIĆ CYKL IMPERIUM — krok po kroku (Windows 10)

> Komendancie — to handel **NA NIBY** (zero ryzyka, zero prawdziwych pieniędzy).
> Jak coś się wysypie: skopiuj czerwony tekst z okna i wyślij mi. Rozwiążemy razem.

---

## 🎯 CO BĘDZIESZ MIAŁ NA KOŃCU

Jedno polecenie, a Imperium samo: dane → policzy → zagra (na niby) →
**narysuje wykres** → **zapisze raport**.

---

## 1. Zainstaluj Pythona i biblioteki

W PowerShell:
```powershell
pip install numpy matplotlib TA-Lib ccxt pandas
```

> ⚠️ **TA-Lib** bywa trudny na Windows. Jeśli `pip install TA-Lib` się wysypie,
> napisz mi — podam gotową paczkę `.whl` do Twojej wersji Pythona.
> **Bez TA-Lib Brama celowo się nie uruchomi** (Prawo I — żadnej ręcznej matematyki).

## 2. Pobierz Imperium

```powershell
git clone https://github.com/dparzy/IMPERIAL-MESH-VORTEX.git
cd IMPERIAL-MESH-VORTEX
```

## 3. (Opcjonalnie) wgraj dane

Wrzuć pliki CSV do `imperium/legiony/dane/` (np. `BTC_1h.csv`).
Nie masz? Cykl użyje danych **syntetycznych** z wyraźnym ostrzeżeniem.

## 4. Uruchom cykl

```powershell
python imperium/legiony/pierwszy_zwiadowca.py
```

## 5. Zobacz wyniki

W folderze `imperium/legiony/` pojawią się:
- `wykres_biegu.png` — otwórz dwuklikiem (cena + EMA + transakcje + kapitał)
- `raport_biegu_*.md` — wyniki (wyślij mi następną sesją)
- `DZIENNIK_WYNIKOW.md` — postęp wszystkich biegów

---

## 🧩 Co się uruchamia (cykl Fazy 0)

`pierwszy_zwiadowca` sam ładuje 5 modułów z dzielnic Imperium:
- `../fundament/brama_kalkulatora.py` (wymagany)
- `../akwedukty/kwatermistrz_danych.py`
- `../pretorianie/aegis_tarcza.py`
- `../swiatynie/kartograf.py`
- `../biblioteki/kronikarz.py`

> Pełna mapa: [../docs/ARCHITEKTURA_IMPERIUM.md](../docs/ARCHITEKTURA_IMPERIUM.md)

---

## ⚠️ Pamiętaj (Prawo I)

Wyniki tego bota to **wstępny paper-test**, NIE zwalidowana strategia.
Dane bywają syntetyczne, brak modelu poślizgu. Sceptycyzm > euforia.
