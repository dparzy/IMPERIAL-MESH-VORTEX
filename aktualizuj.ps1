# =====================================================================
#  AKTUALIZUJ.ps1 — jednym kliknieciem pobiera najnowsze Imperium.
#
#  Robi 3 kroki: sprawdza lokalne zmiany -> git pull -> testy.
#  Bezpieczny: jesli masz lokalne zmiany, sam je chowa (stash) i przywraca.
#  Dane w dane/ (pobrane z Binance) NIE sa ruszane.
#
#  UZYCIE (PowerShell, w katalogu repo):
#     .\aktualizuj.ps1
#
#  Jesli PowerShell blokuje skrypt:
#     powershell -ExecutionPolicy Bypass -File .\aktualizuj.ps1
# =====================================================================

$BRANCH = "claude/sleepy-fermi-dsdE4"
$ErrorActionPreference = "Stop"

function Krok($n, $txt) { Write-Host "`n[$n] $txt" -ForegroundColor Cyan }

# --- Krok 0: czy jestesmy w repo? ---
if (-not (Test-Path ".git")) {
    Write-Host "BLAD: to nie jest folder repozytorium (brak .git)." -ForegroundColor Red
    Write-Host "Wejdz najpierw: cd C:\Projekty\imperial-mesh-vortex" -ForegroundColor Yellow
    exit 1
}

# --- Krok 1: wlasciwa galaz ---
Krok 1 "Sprawdzam galaz..."
$obecna = (git rev-parse --abbrev-ref HEAD).Trim()
if ($obecna -ne $BRANCH) {
    Write-Host "  Jestes na '$obecna', przelaczam na '$BRANCH'..." -ForegroundColor Yellow
    git checkout $BRANCH
} else {
    Write-Host "  OK, jestes na $BRANCH" -ForegroundColor Green
}

# --- Krok 2: schowaj lokalne zmiany jesli sa ---
$zmiany = git status --porcelain
$schowano = $false
if ($zmiany) {
    Krok 2 "Wykryto lokalne zmiany - chowam je tymczasowo (git stash)..."
    git stash push -u -m "aktualizuj.ps1 auto-stash"
    $schowano = $true
} else {
    Krok 2 "Brak lokalnych zmian - czysto."
}

# --- Krok 3: pobierz najnowsze ---
Krok 3 "Pobieram najnowsze z GitHub (git pull)..."
$ok = $false
for ($i = 1; $i -le 4; $i++) {
    try {
        git pull origin $BRANCH
        $ok = $true
        break
    } catch {
        $wait = [math]::Pow(2, $i)
        Write-Host "  Blad sieci (proba $i/4) - czekam $wait s..." -ForegroundColor Yellow
        Start-Sleep -Seconds $wait
    }
}
if (-not $ok) {
    Write-Host "BLAD: nie udalo sie pobrac po 4 probach (siec?)." -ForegroundColor Red
    if ($schowano) { git stash pop }
    exit 1
}

# --- Krok 4: przywroc schowane zmiany ---
if ($schowano) {
    Krok 4 "Przywracam Twoje lokalne zmiany (git stash pop)..."
    try {
        git stash pop
    } catch {
        Write-Host "  UWAGA: konflikt przy przywracaniu zmian." -ForegroundColor Yellow
        Write-Host "  Twoje zmiany sa bezpieczne w 'git stash list'." -ForegroundColor Yellow
    }
}

# --- Krok 5: testy ---
Krok 5 "Uruchamiam testy (musza byc zielone)..."
python tests/run_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nUWAGA: testy NIE przeszly. Sprawdz powyzej." -ForegroundColor Red
    exit 1
}

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host " GOTOWE. Imperium aktualne, testy zielone." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
