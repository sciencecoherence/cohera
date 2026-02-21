#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/xavier/cohera-repo"
WORKSPACE_DIR="/home/xavier/.openclaw/workspace"
VAULT_DIR="$REPO_DIR/vault"
STAMP="$(date +%F_%H%M%S)"
SNAP_DIR="$VAULT_DIR/snapshot-$STAMP"
KEEP_COUNT=10

mkdir -p "$SNAP_DIR"

copy_file() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    cp -f "$src" "$dst"
  fi
}

copy_tree() {
  local src="$1"
  local dst="$2"
  if [[ -d "$src" ]]; then
    mkdir -p "$dst"
    rsync -a --exclude '__pycache__/' --exclude '*.pyc' --exclude '.env' --exclude 'out/' "$src"/ "$dst"/
  fi
}

# Core workspace continuity files
copy_file "$WORKSPACE_DIR/AGENTS.md" "$SNAP_DIR/workspace/AGENTS.md"
copy_file "$WORKSPACE_DIR/SOUL.md" "$SNAP_DIR/workspace/SOUL.md"
copy_file "$WORKSPACE_DIR/USER.md" "$SNAP_DIR/workspace/USER.md"
copy_file "$WORKSPACE_DIR/IDENTITY.md" "$SNAP_DIR/workspace/IDENTITY.md"
copy_file "$WORKSPACE_DIR/TOOLS.md" "$SNAP_DIR/workspace/TOOLS.md"
copy_file "$WORKSPACE_DIR/HEARTBEAT.md" "$SNAP_DIR/workspace/HEARTBEAT.md"
copy_file "$WORKSPACE_DIR/BOOTSTRAP.md" "$SNAP_DIR/workspace/BOOTSTRAP.md"

# Mail integration scaffold (safe files only)
copy_tree "$WORKSPACE_DIR/integrations/hostinger-mail" "$SNAP_DIR/integrations/hostinger-mail"

# Cohera repo specs + published site
copy_file "$REPO_DIR/COHERA_RULES.md" "$SNAP_DIR/repo/COHERA_RULES.md"
copy_file "$REPO_DIR/SITE_SPEC.md" "$SNAP_DIR/repo/SITE_SPEC.md"
copy_tree "$REPO_DIR/site" "$SNAP_DIR/repo/site"

cat > "$SNAP_DIR/README.md" <<EOF
# Vault Snapshot: $STAMP

Generated automatically by scripts/vault_snapshot.sh.

Includes:
- workspace continuity files
- hostinger mail integration scaffold (without secrets/artifacts)
- cohera repo specs + /site content

Excludes:
- .env, tokens, passwords
- runtime outputs/logs/cache
EOF

# Build manifest.json (path + size + mtime)
SNAP_DIR="$SNAP_DIR" python3 - <<'PY'
import json
import os
from pathlib import Path
from datetime import datetime, timezone

snap = Path(os.environ["SNAP_DIR"])
manifest = []
for p in sorted(snap.rglob("*")):
    if p.is_file() and p.name not in {"checksums.txt"}:
        st = p.stat()
        manifest.append({
            "path": str(p.relative_to(snap)),
            "size": st.st_size,
            "mtime": int(st.st_mtime),
            "mtime_iso": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
        })

(snap / "manifest.json").write_text(json.dumps({
    "snapshot": snap.name,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "files": manifest,
}, indent=2), encoding="utf-8")
PY

# Build checksums.txt (sha256)
(
  cd "$SNAP_DIR"
  find . -type f ! -name 'checksums.txt' -print0 \
    | sort -z \
    | xargs -0 sha256sum > checksums.txt
)

# Keep only latest N snapshot directories to prevent repo bloat.
# Applies to directories named snapshot-* and bootstrap-* inside /vault.
mapfile -t old_dirs < <(
  find "$VAULT_DIR" -mindepth 1 -maxdepth 1 -type d \( -name 'snapshot-*' -o -name 'bootstrap-*' \) -printf '%T@ %p\n' \
    | sort -nr \
    | awk -v keep="$KEEP_COUNT" 'NR>keep {print $2}'
)

for d in "${old_dirs[@]:-}"; do
  [[ -n "$d" ]] && rm -rf "$d"
done

# Commit + push (safe even when nothing changed)
cd "$REPO_DIR"
git add vault
if ! git diff --cached --quiet; then
  git commit -m "vault: snapshot $STAMP (auto, keep last $KEEP_COUNT)"
  git push origin main
fi

echo "Snapshot complete: $SNAP_DIR"
