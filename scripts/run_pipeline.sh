#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
LOG="$REPO/chatgpt/run_pipeline.log"

{
  echo "[$(date -Is)] run_pipeline start"
  /home/xavier/cohera-repo/scripts/research_recursive_cycle.sh
  echo "[$(date -Is)] run_pipeline done"
} >> "$LOG" 2>&1
