#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SRC="${HOME}/Downloads/Global Superstore.csv"
DST="$ROOT/data/raw/global_superstore.csv"

mkdir -p "$ROOT/data/raw"
if [[ ! -f "$DST" && -f "$SRC" ]]; then
  cp "$SRC" "$DST"
  echo "CSV скопирован в data/raw/"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
python -m superstore.etl.load_and_clean
python -m superstore.analysis.eda
echo "Запуск: ./scripts/run_streamlit.ps1  или  streamlit run dashboard/app.py"
