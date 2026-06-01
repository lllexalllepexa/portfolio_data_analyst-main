# Postgres via Docker + load parquet
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-DockerDaemon {
    docker info 2>&1 | Out-Null
    return $LASTEXITCODE -eq 0
}

if (-not (Test-DockerDaemon)) {
    Write-Host @"

Docker is not running. Start Docker Desktop, then: docker info

SQL without Docker: .\scripts\sql_duckdb_demo.ps1
See: docs/sql_postgres.md

"@
    exit 1
}

docker compose up -d postgres
Start-Sleep -Seconds 8
.\.venv\Scripts\python -m superstore.loaders.load_postgres
