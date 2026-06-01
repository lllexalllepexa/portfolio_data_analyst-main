# SQL-demo bez Docker (DuckDB)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Db = "data\processed\superstore.duckdb"
$Parquet = "data\processed\orders_clean.parquet"

if (-not (Test-Path $Parquet)) {
    .\.venv\Scripts\python -m superstore.etl.load_and_clean
}

$Duck = Join-Path $Root ".venv\Scripts\duckdb.exe"
if (-not (Test-Path $Duck)) {
    .\.venv\Scripts\pip install -q duckdb
    $Duck = Join-Path $Root ".venv\Scripts\duckdb.exe"
}

Write-Host "=== Top regions by revenue ==="
& $Duck $Db -c "SELECT region, ROUND(SUM(sales),2) AS revenue FROM orders GROUP BY 1 ORDER BY 2 DESC LIMIT 8;"

Write-Host "`n=== Mart region year (view) ==="
& $Duck $Db -c "SELECT * FROM mart_region_year ORDER BY revenue DESC LIMIT 10;"
