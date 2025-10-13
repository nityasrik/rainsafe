#!/usr/bin/env bash

# Cron script for weather data fetching
# - Loads environment from .env (if present)
# - Avoids hardcoded secrets and absolute paths

set -euo pipefail

# Resolve project root (parent of this script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables from .env if available
if [ -f .env ]; then
  # Export all vars defined in .env
  set -a
  . ./.env
  set +a
fi

# Optionally activate virtualenv if it exists
if [ -d "venv" ]; then
  . "venv/bin/activate"
fi

# Run the weather fetcher
python3 app/services/weather_service.py

# Log the execution (optional)
echo "$(date): Weather data fetch completed" >> "$PROJECT_ROOT/cron.log"