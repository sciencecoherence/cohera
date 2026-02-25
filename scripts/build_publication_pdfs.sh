#!/bin/bash
# build_publication_pdfs.sh
# Sync publication PDFs into site/publications/pdf

set -euo pipefail

REPO_ROOT="/home/xavier/.openclaw/workspace/cohera-repo"
SRC_DIR="$REPO_ROOT/research/pdf"
DST_DIR="$REPO_ROOT/site/publications/pdf"

mkdir -p "$DST_DIR"

if [[ -d "$SRC_DIR" ]]; then
  rsync -a --delete "$SRC_DIR/" "$DST_DIR/"
  echo "Synced PDFs: $SRC_DIR -> $DST_DIR"
else
  echo "No research/pdf directory found yet. Skipping PDF sync."
fi
