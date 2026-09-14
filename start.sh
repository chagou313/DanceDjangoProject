#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "错误：找不到 $PYTHON_BIN，请先安装 Python 3。" >&2
    exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
    "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate --noinput

echo "项目已准备完成：http://${HOST:-127.0.0.1}:${PORT:-8000}"
exec .venv/bin/python manage.py runserver "${HOST:-127.0.0.1}:${PORT:-8000}" --noreload
