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
echo "[$DATE_STR] DEPLOY PHASE: guarded auto-commit/push"
echo "=============================================="

# Hard guard: pipeline is allowed to mutate only specific files/paths.
# If anything else changed, abort and require explicit human approval.
mapfile -t CHANGED_PATHS < <(git status --porcelain | awk '{print $2}')

is_allowed_change() {
  local p="$1"
  case "$p" in
    site/index.html|site/research/index.html|site/publications/index.html)
      return 0
      ;;
    site/publications/pdf/*)
      return 0
      ;;
    research/pipeline/*|research/sources/*|research/digests/*|research/synthesis-latest.md)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

DISALLOWED=()
for p in "${CHANGED_PATHS[@]}"; do
  [[ -z "$p" ]] && continue
  if ! is_allowed_change "$p"; then
    DISALLOWED+=("$p")
  fi
done

if (( ${#DISALLOWED[@]} > 0 )); then
  echo "GUARD VIOLATION: pipeline produced disallowed file changes:" >&2
  printf ' - %s\n' "${DISALLOWED[@]}" >&2
  echo "Aborting commit. No files were staged." >&2
  exit 1
fi

if ! git diff --quiet -- site/index.html site/research/index.html site/publications/index.html site/publications/pdf research/pipeline research/sources research/digests research/synthesis-latest.md; then
  git add site/index.html site/research/index.html site/publications/index.html site/publications/pdf research/pipeline research/sources research/digests research/synthesis-latest.md
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
