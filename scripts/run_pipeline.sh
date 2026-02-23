#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
LOG="$REPO/chatgpt/run_pipeline.log"

mkdir -p "$(dirname "$LOG")"

{
echo "====================================================="
echo "[$(date -Is)] INITIATING TIME-CRYSTALLINE RESEARCH PIPELINE"
echo "====================================================="

echo "[1/4] Phase 1: Ingestion & Diffs..."
/usr/bin/python3 "$REPO/scripts/research_autopilot.py"
/usr/bin/python3 "$REPO/scripts/research_delta.py"
/usr/bin/python3 "$REPO/scripts/research_health.py"

echo "[2/4] Phase 2: Advancing Backlog & Corpus Sync..."
/usr/bin/python3 "$REPO/scripts/research_backlog_advancer.py"
/usr/bin/python3 "$REPO/scripts/research_chat_corpus_ingest.py" || true

echo "[3/4] Phase 3: Indexes & Publication State..."
/usr/bin/python3 "$REPO/scripts/publication_pipeline.py" --sync

 ---------------------------------------------------------
echo "[COHERA SYNTHESIS INJECTION POINT]"


/usr/bin/python3 "$REPO/scripts/trigger_cohera_synthesis.py"


echo "[4/4] Phase 4: Synthesis Prep & Surface Rebuilds..."
/usr/bin/python3 "$REPO/scripts/research_daily_findings.py"
/usr/bin/python3 "$REPO/scripts/update_surface_status.py"
/usr/bin/python3 "$REPO/scripts/rebuild_thread_pages.py"
git add site/ chatgpt/

# Generate timestamp strictly in dd/mm/yyyy format
COMMIT_DATE=$(date +"%d/%m/%Y")
COMMIT_TIME=$(date +"%H:%M %Z")

# Commit changes, bypassing the error if there is nothing new to commit
git commit -m "Pipeline [Cycle: $COMMIT_DATE] - Ingestion & Synthesis at $COMMIT_TIME" || echo "No changes detected. Skipping commit."

# Push to live
git push origin main

echo "====================================================="
echo "[$(date -Is)] PIPELINE SCRIPTS COMPLETE. AWAITING COHERA SYNTHESIS."
echo "====================================================="
} >> "$LOG" 2>&1
