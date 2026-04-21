#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

if [ ! -d venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt >/dev/null

# Single-instance guard: only one polling process may run at a time.
exec flock -n /tmp/telegram-ai-operator.lock python app/bot.py
