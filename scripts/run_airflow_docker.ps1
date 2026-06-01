# Airflow DAG test via Docker. Requires Docker Desktop RUNNING.
# Usage: .\scripts\run_airflow_docker.ps1

param(
    [string]$LogicalDate = "2024-01-01"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-DockerDaemon {
    $null = docker version --format "{{.Server.Version}}" 2>$null
    return $LASTEXITCODE -eq 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found. Install Docker Desktop."
    exit 1
}

if (-not (Test-DockerDaemon)) {
    Write-Host ""
    Write-Host "Docker daemon is NOT running."
    Write-Host ""
    Write-Host "Fix (Windows):"
    Write-Host "  1. Start 'Docker Desktop' from Start menu"
    Write-Host "  2. Wait until tray icon says 'Docker Desktop is running'"
    Write-Host "  3. Run: docker info   (Server section must appear)"
    Write-Host "  4. If still fails: restart PC, run Docker Desktop as Administrator"
    Write-Host "  5. Docker Desktop -> Settings -> General -> Use WSL 2 based engine"
    Write-Host ""
    Write-Host "Without Docker: see dags/superstore_etl.py and docs/airflow.md"
    Write-Host ""
    exit 1
}

if (-not (Test-Path "data\processed\orders_clean.parquet")) {
    Write-Host "Running ETL first..."
    if (Test-Path ".venv\Scripts\python.exe") {
        .\.venv\Scripts\python -m superstore.etl.load_and_clean
    } else {
        python -m superstore.etl.load_and_clean
    }
}

Write-Host ""
Write-Host "Running: airflow dags test superstore_etl $LogicalDate"
Write-Host ""

docker compose -f docker-compose.airflow.yml run --rm -e "LOGICAL_DATE=$LogicalDate" airflow-dag-test
exit $LASTEXITCODE
