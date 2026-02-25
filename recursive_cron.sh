#!/bin/bash
# recursive_cron.sh
# Executes the Cohera recursive research pipeline on schedule

set -euo pipefail

mkdir -p /home/xavier/.openclaw/workspace/cohera-repo/chatgpt
LOG_FILE="/home/xavier/.openclaw/workspace/cohera-repo/chatgpt/recursive_cron.log"
DATE_STR=$(date +"%d/%m/%Y %H:%M:%S")

{
  echo "[$DATE_STR] Initiating recursive research pipeline..."
  cd /home/xavier/.openclaw/workspace/cohera-repo
  COHERA_AUTO_PUSH=1 bash research_pipeline.sh
  echo "[$DATE_STR] Pipeline execution finished."
} >> "$LOG_FILE" 2>&1
