$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$dst = "$Root\data\raw\global_superstore.csv"
if (-not (Test-Path $dst)) {
    Write-Host "Положите global_superstore.csv в data\raw\ (см. data\raw\README.md)"
}

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (Test-Path $dst) {
    python -m superstore.etl.load_and_clean
    python -m superstore.analysis.eda
}
