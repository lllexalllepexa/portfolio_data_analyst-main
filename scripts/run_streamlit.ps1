$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = $Root

$Pip = Join-Path $Root ".venv\Scripts\pip.exe"
$Streamlit = Join-Path $Root ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $Streamlit)) {
    Write-Host "venv: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}

& $Pip install -q -r requirements.txt
& $Streamlit run dashboard/app.py
