#!/usr/bin/env bash
set -euo pipefail

REPO="/home/xavier/cohera-repo"
cd "$REPO"

/usr/bin/python3 scripts/webdesign_audit.py

# Ensure publication index links the latest audit
python3 - <<'PY'
from pathlib import Path
p = Path('/home/xavier/cohera-repo/site/publications/index.html')
s = p.read_text(encoding='utf-8')
link = '<li><a href="/cohera/publications/design-audit-latest.html">Daily Design Audit (latest)</a></li>'
if link not in s:
    s = s.replace('</ul>', f'{link}\n      </ul>')
p.write_text(s, encoding='utf-8')
PY

git add site/publications/design-audit-latest.html site/publications/index.html
if ! git diff --cached --quiet; then
  git commit -m "webdesign: daily audit refresh"
  git push origin main
fi
