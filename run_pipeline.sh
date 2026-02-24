#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
LOG="$REPO/chatgpt/run_pipeline.log"

{
  echo "--- Starting Pipeline: $(date) ---"

  # Phase 1: Ingestion
  python3 "$REPO/scripts/research_autopilot.py"

  # Phase 2: Forced Synthesis (The Brain)
  python3 "$REPO/scripts/trigger_cohera_synthesis.py"

  # Phase 3: Deployment (The Ship)
  cd "$REPO"
  git add .
  # Commit using your preferred dd/mm/yyyy format
  COMMIT_MSG="Pipeline Auto-Update: $(date +'%d/%m/%Y %H:%M')"
  git commit -m "$COMMIT_MSG" || echo "No changes to commit."
  git push origin main

  echo "--- Pipeline Complete: $(date) ---"
} >> "$LOG" 2>&1
