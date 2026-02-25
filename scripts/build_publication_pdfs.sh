#!/bin/bash
# build_publication_pdfs.sh
# Sync publication PDFs into site/publications/pdf

set -euo pipefail

REPO_ROOT="/home/xavier/.openclaw/workspace/cohera-repo"
SRC_DIR="$REPO_ROOT/research/publications/final"
DST_DIR="$REPO_ROOT/site/publications/pdf"

mkdir -p "$SRC_DIR" "$DST_DIR"

# Strict policy: publications page must only expose Cohera-authored final papers.
# Therefore we sync exclusively from research/publications/final and delete anything else.
rsync -a --delete "$SRC_DIR/" "$DST_DIR/"
echo "Synced Cohera final PDFs only: $SRC_DIR -> $DST_DIR"
