#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
LOG="$REPO/chatgpt/research_recursive_cycle.log"

mkdir -p "$(dirname "$LOG")"

{
  echo "[$(date -Is)] recursive-cycle start"

  /usr/bin/python3 "$REPO/scripts/research_autopilot.py"
  /usr/bin/python3 "$REPO/scripts/research_delta.py"
  /usr/bin/python3 "$REPO/scripts/research_health.py"

  # Advance unfinished backlog even when there are no new source-file changes.
  /usr/bin/python3 "$REPO/scripts/research_backlog_advancer.py"

  # Ingest chat corpus sequentially (Genesis -> NewReality -> ...)
  /usr/bin/python3 "$REPO/scripts/research_chat_corpus_ingest.py" || true

  # Recompute publication indexes/state
  /usr/bin/python3 "$REPO/scripts/publication_pipeline.py" --sync

  # Refresh daily findings report every cycle.
  /usr/bin/python3 "$REPO/scripts/research_daily_findings.py"

  echo "[$(date -Is)] recursive-cycle done"
} >> "$LOG" 2>&1
