#!/usr/bin/env bash
set -euo pipefail

TARGETS=(
  "scripts/build_publication_pdfs.sh"
  "scripts/publication_pipeline.py"
)

for f in "${TARGETS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "missing target: $f" >&2
    exit 1
  fi
  if grep -n '/home/xavier/cohera-repo' "$f" >/tmp/ci_guard_match.txt; then
    echo "Hardcoded local path detected in $f" >&2
    cat /tmp/ci_guard_match.txt >&2
    exit 1
  fi
done

echo "ci_guard_paths: OK"
