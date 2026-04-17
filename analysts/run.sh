#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/data/state"
LOG_FILE="$LOG_DIR/run.log"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1

CHANNEL="$(
  PYTHONPATH=src ../.venv/bin/python - <<'PY'
from pathlib import Path
from analysts.config import build_config

config = build_config(Path("."))
print(config.telethon.channel if config.telethon else "")
PY
)"

if [ -z "$CHANNEL" ]; then
  echo "Missing Telegram channel in config.local.json"
  exit 1
fi

run() {
  echo
  echo "== $1 =="
  shift
  "$@"
}

cd "$ROOT"

echo
echo "==== run started $(date '+%Y-%m-%d %H:%M:%S %z') ===="

run "Telegram fetch" \
  env PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --base-dir . --channel "$CHANNEL"

run "Telegram summarize latest" \
  env PYTHONPATH=src ../.venv/bin/python -m analysts.cli summarize-latest --base-dir . --channel "$CHANNEL"

run "Gmail sync" \
  env PYTHONPATH=src ../.venv/bin/python -m analysts.cli gmail-sync-once --base-dir . --limit 20

run "Gmail summarize latest" \
  env PYTHONPATH=src ../.venv/bin/python -m analysts.cli gmail-summarize-latest --base-dir .

echo
echo "==== run finished $(date '+%Y-%m-%d %H:%M:%S %z') ===="
echo "log: $LOG_FILE"
