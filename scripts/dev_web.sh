#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "kronos_env/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "kronos_env/bin/activate"
fi

export PYTHONPATH="${ROOT}/Kronos:${ROOT}"
export MPLBACKEND=Agg

unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
unset SOCKS_PROXY SOCKS5_PROXY socks_proxy socks5_proxy

pip install -q -r backend/requirements.txt

uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

trap 'kill ${BACKEND_PID}' EXIT

cd frontend
npm install
npm run dev
