#!/bin/bash
# research_pipeline.sh
# Cohera recursive research + publishing runner

set -euo pipefail

REPO_ROOT="/home/xavier/.openclaw/workspace/cohera-repo"

DATE_STR=$(date +"%d/%m/%Y %H:%M:%S")
echo "=============================================="
echo "[$DATE_STR] RESEARCH PHASE: discovery + structured notes"
echo "=============================================="

cd "$REPO_ROOT"
python3 scripts/recursive_research_pipeline.py

echo "=============================================="
echo "[$DATE_STR] PUBLICATIONS PHASE: PDF sync + ledger update"
echo "=============================================="

bash scripts/build_publication_pdfs.sh

echo "=============================================="
echo "[$DATE_STR] DEPLOY PHASE: optional auto-commit/push"
echo "=============================================="

if ! git diff --quiet -- site research/pipeline research/sources research/digests research/synthesis-latest.md; then
  git add site research/pipeline research/sources research/digests research/synthesis-latest.md
  git commit -m "Automated research pipeline refresh"

  if [[ "${COHERA_AUTO_PUSH:-0}" == "1" ]]; then
    git push origin main
    echo "Auto-push complete."
  else
    echo "Auto-push skipped (set COHERA_AUTO_PUSH=1 to enable)."
  fi
else
  echo "No pipeline content changes detected."
fi

echo "Pipeline execution complete."
