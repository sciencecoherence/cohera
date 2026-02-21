#!/usr/bin/env bash
set -euo pipefail

SCRIPT="/home/xavier/cohera-repo/scripts/vault_snapshot.sh"
CRON_EXPR="17 3 * * *"
CRON_LINE="$CRON_EXPR $SCRIPT >> /home/xavier/cohera-repo/vault/cron.log 2>&1"

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

echo "Installed daily vault snapshot cron: $CRON_LINE"
