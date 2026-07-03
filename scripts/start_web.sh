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

# Clash/Cursor 等可能在环境里注入代理变量，东财接口必须直连
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
unset SOCKS_PROXY SOCKS5_PROXY socks_proxy socks5_proxy

if [[ ! -d "frontend/dist" ]]; then
  echo "Building frontend..."
  (cd frontend && npm install && npm run build)
fi

pip install -q -r backend/requirements.txt
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 "$@"
