#!/usr/bin/env bash
set -euo pipefail
REPO="/home/xavier/cohera-repo"
cd "$REPO"

if git diff --quiet -- site/trading/journal/trades.csv site/trading/journal/metrics.json; then
  exit 0
fi

git add site/trading/journal/trades.csv site/trading/journal/metrics.json
if ! git diff --cached --quiet; then
  git commit -m "Auto-publish trading journal update"
  git push origin main
fi
