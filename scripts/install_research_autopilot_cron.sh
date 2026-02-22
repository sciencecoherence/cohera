#!/usr/bin/env bash
set -euo pipefail

SCRIPT="/home/xavier/cohera-repo/scripts/research_autopilot.py"
CRON_EXPR="11 */6 * * *"
CRON_LINE="$CRON_EXPR /usr/bin/python3 $SCRIPT >> /home/xavier/cohera-repo/chatgpt/research_autopilot.log 2>&1"

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

echo "Installed research autopilot cron: $CRON_LINE"
