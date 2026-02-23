#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site' / 'research'
OUT_DIR = REPO / 'site' / 'publications'
HEALTH = REPO / 'chatgpt' / 'research_health.json'
DELTA = REPO / 'chatgpt' / 'research_delta_latest.json'
BACKLOG = REPO / 'chatgpt' / 'research_backlog_run.json'
PIPE = REPO / 'chatgpt' / 'publication_pipeline.json'


def load_json(p: Path, d):
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return d


def li(items, empty='none'):
    if not items:
        return f'<li>{empty}</li>'
    return ''.join(f'<li>{x}</li>' for x in items)


def main():
    now = datetime.now(timezone.utc)
    day = now.strftime('%Y-%m-%d')

    health = load_json(HEALTH, {})
    delta = load_json(DELTA, {})
    backlog = load_json(BACKLOG, {'created': []})
    pipe = load_json(PIPE, {'totals': {}})

    backlog_rows = [f"{x.get('thread')}: <code class=\"inline\">{x.get('from')}</code>" for x in backlog.get('created', [])]
    top_rows = []
    for t in delta.get('top_priority', [])[:8]:
        top_rows.append(f"{t.get('thread','unknown')}: <code class=\"inline\">{t.get('path','')}</code>")

    out = OUT_DIR / f'findings-{day}.html'
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Findings Report · {day} · Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
</head>
<body>
<header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
<a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
</nav></div></header>
<main class="container">
<section class="hero"><h1>Findings Report · {day}</h1><p class="small">Auto-updated each recursive research cycle.</p></section>
<section class="card"><h3>Pipeline health</h3><ul class="clean">
<li>Status: <strong>{health.get('status','unknown')}</strong></li>
<li>Issues: {len(health.get('issues', []))}</li>
<li>Queue changes detected: {health.get('queue_changes_count', 0)}</li>
<li>Autodrafts created: {health.get('autodrafts_created_count', 0)}</li>
</ul></section>
<section class="card"><h3>Delta snapshot</h3><ul class="clean">
<li>New: {delta.get('counts',{}).get('new',0)}</li>
<li>Updated: {delta.get('counts',{}).get('updated',0)}</li>
<li>Removed: {delta.get('counts',{}).get('removed',0)}</li>
<li>Total sources tracked: {delta.get('counts',{}).get('total_sources',0)}</li>
</ul></section>
<section class="card"><h3>Backlog promoted this cycle</h3><ul class="clean">{li(backlog_rows, 'no backlog promotions this cycle')}</ul></section>
<section class="card"><h3>Top source priorities</h3><ul class="clean">{li(top_rows, 'no priority items')}</ul></section>
<section class="card"><h3>Publication readiness</h3><ul class="clean">
<li>Items: {pipe.get('totals',{}).get('items',0)}</li>
<li>With TeX: {pipe.get('totals',{}).get('with_tex',0)}</li>
<li>With PDF: {pipe.get('totals',{}).get('with_pdf',0)}</li>
<li>Ready publications: <strong>{pipe.get('totals',{}).get('ready_publications',0)}</strong></li>
</ul></section>
</main>
</body></html>
''', encoding='utf-8')

    latest = OUT_DIR / 'findings-latest.html'
    latest.write_text(out.read_text(encoding='utf-8'), encoding='utf-8')

    # surface from research section too
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / 'findings-latest.html').write_text(out.read_text(encoding='utf-8'), encoding='utf-8')

    print(f'findings_updated={out.relative_to(REPO)}')


if __name__ == '__main__':
    main()
