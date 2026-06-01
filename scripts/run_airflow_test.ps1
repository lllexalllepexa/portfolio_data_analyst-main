param(
    [string]$LogicalDate = "2024-01-01"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root


if (Test-Path ".venv/Scripts/Activate.ps1") { . .venv/Scripts/Activate.ps1 }
elseif (Test-Path ".venv/bin/activate") { . .venv/bin/activate }

$env:AIRFLOW_HOME = Join-Path $Root ".airflow"
$env:PYTHONPATH = $Root
$env:AIRFLOW_PROJECT_ROOT = $Root
$env:AIRFLOW__CORE__DAGS_FOLDER = Join-Path $Root "dags"
$env:AIRFLOW__CORE__LOAD_EXAMPLES = "False"

if (-not (Test-Path $env:AIRFLOW_HOME)) {
    airflow db migrate
}

airflow dags test superstore_etl $LogicalDate
