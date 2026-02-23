#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
LOG="$REPO/chatgpt/git_autosync.log"
LOCKFILE="/tmp/cohera-git-autosync.lock"

mkdir -p "$(dirname "$LOG")"

{
  echo "[$(date -Is)] autosync start"
  cd "$REPO"

  # Stage everything (tracked + untracked + deletions)
  git add -A

  # Commit only if there are staged changes
  if ! git diff --cached --quiet; then
    git commit -m "autosync: $(date '+%Y-%m-%d %H:%M:%S %z')"
  else
    echo "No local changes to commit"
  fi

  # Rebase on remote and push (keeps history linear)
  git pull --rebase --autostash origin main
  git push origin main

  echo "[$(date -Is)] autosync done"
} >> "$LOG" 2>&1
