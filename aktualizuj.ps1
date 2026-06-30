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

# --- Krok 5: zaleznosci (pip) ---
Krok 5 "Instaluje/aktualizuje zaleznosci (requirements.txt)..."
python -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  UWAGA: pip mial problem - sprawdz powyzej (czesc moze dzialac mimo to)." -ForegroundColor Yellow
}

# --- Krok 6: testy ---
Krok 6 "Uruchamiam testy (musza byc zielone)..."
python tests/run_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nUWAGA: testy NIE przeszly. Sprawdz powyzej." -ForegroundColor Red
    exit 1
}

# --- Krok 7: indeks RAG (wektory lokalnie jesli dostepne, inaczej FTS) ---
Krok 7 "Buduje indeks wiedzy RAG (pelny korpus)..."
python narzedzia/rag/indeksuj.py --korpus wszystko --tylko-nowe
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Wektory niedostepne - probuje FTS (bez modelu)..." -ForegroundColor Yellow
    python narzedzia/rag/indeksuj.py --korpus wszystko --bez-wektorow --tylko-nowe
}

# --- Krok 8: pamiec - katalog + graf + mapa 13 warstw ---
Krok 8 "Odswiezam pamiec (katalog, graf) i pokazuje mape..."
python -m imperium.biblioteki.kustosz_pamieci kataloguj
python -m imperium.biblioteki.graf_pamieci buduj
python -m imperium.biblioteki.kustosz_pamieci mapa

# --- Krok 9: DeepSeek (jesli klucz ustawiony) ---
Krok 9 "Sprawdzam DeepSeek (opcjonalny - tylko jesli ustawiles klucz)..."
if ($env:DEEPSEEK_API_KEY) {
    python -c "from imperium.cesarz.deepseek_glos import GlosImperium; print('DeepSeek:', 'OK' if GlosImperium().test_polaczenia() else 'BLAD')"
} else {
    Write-Host "  DeepSeek pominiety (brak DEEPSEEK_API_KEY). Aby wlaczyc:" -ForegroundColor Yellow
    Write-Host '     setx DEEPSEEK_API_KEY "twoj-klucz"  (potem nowy terminal)' -ForegroundColor Yellow
}

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host " GOTOWE. Imperium aktualne, testy zielone, pamiec odswiezona." -ForegroundColor Green
Write-Host " Paper-trading:  python skrypty/start.py  (dashboard :8777)" -ForegroundColor Green
Write-Host " Przewodnik:     docs/START_LOKAL.md" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
