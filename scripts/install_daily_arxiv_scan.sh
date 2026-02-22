#!/usr/bin/env bash
set -euo pipefail

SCRIPT="/home/xavier/cohera-repo/scripts/daily_arxiv_scan.py"
# Run at 05:00 AM daily (before the 6-hour autopilot cycle)
CRON_EXPR="0 5 * * *"
CRON_LINE="$CRON_EXPR /usr/bin/python3 $SCRIPT >> /home/xavier/cohera-repo/chatgpt/daily_scan.log 2>&1"

chmod +x "$SCRIPT"

current="$(crontab -l 2>/dev/null || true)"
if grep -Fq "$SCRIPT" <<< "$current"; then
  echo "Cron already installed."
  exit 0
fi

{
  printf "%s\n" "$current"
  printf "%s\n" "$CRON_LINE"
} | crontab -

echo "Installed daily ArXiv scan cron: $CRON_LINE"
