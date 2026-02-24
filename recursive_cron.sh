#!/bin/bash
# recursive_cron.sh
# 100% Uptime Naked Script
# Executes the Genesis Pipeline on a schedule

set -e

LOG_FILE="/home/xavier/cohera-repo/chatgpt/recursive_cron.log"
DATE_STR=$(date +"%d/%m/%Y %H:%M:%S")

echo "[$DATE_STR] Initiating recursive research pipeline..." >> "$LOG_FILE"

cd /home/xavier/cohera-repo
bash research_pipeline.sh >> "$LOG_FILE" 2>&1

echo "[$DATE_STR] Pipeline execution finished." >> "$LOG_FILE"
