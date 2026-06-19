# =====================================================================
#  POBIERZ_DANE.ps1 — Akwedukt Imperium: pobiera historyczne OHLCV
#  ze CryptoDataDownload (Binance) do folderu dane/ w poprawnym układzie.
#
#  Format docelowy pasuje 1:1 do imperium/akwedukty/czytnik_csv.py
#  (CryptoDataDownload: linia URL + nagłówek Unix,Date,Symbol,OHLCV...).
#
#  UŻYCIE (PowerShell, w katalogu repo):
#     .\narzedzia\pobierz_dane.ps1                  # wszystkie pary, wszystkie interwały
#     .\narzedzia\pobierz_dane.ps1 -Pary BTC,ETH    # tylko wybrane pary
#     .\narzedzia\pobierz_dane.ps1 -Interwaly 1h,4h # tylko wybrane interwały
#
#  Jeśli PowerShell blokuje skrypt:
#     powershell -ExecutionPolicy Bypass -File .\narzedzia\pobierz_dane.ps1
# =====================================================================

param(
    [string[]]$Pary = @("BTC","ETH","SOL","BNB","DOGE","XRP","ADA","AVAX","LINK","LTC","DOT","MATIC","TRX","ATOM","NEAR"),
    [string[]]$Interwaly = @("minute","1h","4h","d")
)

$ErrorActionPreference = "Continue"
$baza = "https://www.cryptodatadownload.com/cdd"

# Interwał CDD -> (folder Imperium, sufiks pliku, etykieta interwału)
$mapa = @{
    "minute" = @{ folder = "dane/minutowe";  sufiks = "minute" }
    "1h"     = @{ folder = "dane/godzinowe";  sufiks = "1h" }
    "4h"     = @{ folder = "dane/4h";         sufiks = "4h" }
    "d"      = @{ folder = "dane/dzienne";    sufiks = "d" }
}

$ok = 0; $blad = 0
Write-Host "Akwedukt Imperium - pobieranie danych CryptoDataDownload" -ForegroundColor Cyan
Write-Host "Pary: $($Pary -join ', ')" -ForegroundColor DarkGray
Write-Host "Interwaly: $($Interwaly -join ', ')`n" -ForegroundColor DarkGray

foreach ($interw in $Interwaly) {
    if (-not $mapa.ContainsKey($interw)) {
        Write-Host "  ! Nieznany interwal: $interw (dozwolone: minute,1h,4h,d)" -ForegroundColor Yellow
        continue
    }
    $cfg = $mapa[$interw]
    if (-not (Test-Path $cfg.folder)) { New-Item -ItemType Directory -Path $cfg.folder -Force | Out-Null }

    foreach ($p in $Pary) {
        $para = "$($p.ToUpper())USDT"
        $url  = "$baza/Binance_${para}_$($cfg.sufiks).csv"
        $cel  = Join-Path $cfg.folder "Binance_${para}_$($cfg.sufiks).csv"
        Write-Host -NoNewline "  $para [$interw] ... "
        try {
            curl.exe -s -f -o $cel $url
            if ($LASTEXITCODE -eq 0 -and (Test-Path $cel) -and (Get-Item $cel).Length -gt 200) {
                $kb = [math]::Round((Get-Item $cel).Length / 1KB)
                Write-Host "OK ($kb KB)" -ForegroundColor Green
                $ok++
            } else {
                if (Test-Path $cel) { Remove-Item $cel }   # usun pusty/404
                Write-Host "BRAK na CDD (pomijam)" -ForegroundColor DarkYellow
                $blad++
            }
        } catch {
            Write-Host "BLAD: $_" -ForegroundColor Red
            $blad++
        }
    }
}

Write-Host "`nGotowe. Pobrano: $ok | Pominieto/blad: $blad" -ForegroundColor Cyan
Write-Host "Sprawdz dane:  python -c `"from imperium.akwedukty.czytnik_csv import wczytaj_csv; b=wczytaj_csv('dane/godzinowe/Binance_BTCUSDT_1h.csv', interwal='1H'); print(len(b), 'barow')`"" -ForegroundColor DarkGray
