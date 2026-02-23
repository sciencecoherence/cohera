#!/usr/bin/env bash
# run_pipeline.sh - The Master Orchestrator for the Cohera Research Engine

set -e # Exit immediately if a command exits with a non-zero status

REPO_DIR="/home/xavier/cohera-repo"
cd "$REPO_DIR"

echo "====================================================="
echo "INITIATING TIME-CRYSTALLINE RESEARCH PIPELINE"
echo "====================================================="

echo "[1/4] Phase 1: Ingesting Sources & Generating Autodrafts..."
python3 chatgpt/auto-research.py

echo "[2/4] Phase 2: Compiling System Wake Delta..."
python3 chatgpt/research_delta.py

echo "[3/4] Phase 3: Generating Daily Findings Framework..."
python3 chatgpt/daily_findings.py

# ---------------------------------------------------------
# [COHERA SYNTHESIS INJECTION POINT]
# If you build a CLI script to trigger Cohera via API, 
# you will uncomment the line below so Cohera writes the 
# abstract into the HTML *before* the code is committed.
#
# python3 chatgpt/trigger_cohera_synthesis.py
# ---------------------------------------------------------

echo "[4/4] Phase 4: Version Control & Deployment..."
git add site/ chatgpt/

# Generate timestamp strictly in dd/mm/yyyy format
COMMIT_DATE=$(date +"%d/%m/%Y")
COMMIT_TIME=$(date +"%H:%M %Z")

# Commit changes, bypassing the error if there is nothing new to commit
git commit -m "Pipeline [Cycle: $COMMIT_DATE] - Ingestion & Synthesis at $COMMIT_TIME" || echo "No changes detected. Skipping commit."

# Push to live
git push origin main

echo "====================================================="
echo "PIPELINE COMPLETE. REPOSITORY SYNCED."
echo "====================================================="
