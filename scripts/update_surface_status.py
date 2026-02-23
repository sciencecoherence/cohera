#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site'
PIPE = REPO / 'chatgpt' / 'publication_pipeline.json'
BACKLOG = REPO / 'chatgpt' / 'research_backlog_run.json'
HEALTH = REPO / 'chatgpt' / 'research_health.json'


def load_json(p, d):
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return d


def main():
    pipe = load_json(PIPE, {'totals': {}, 'items': []})
    backlog = load_json(BACKLOG, {'created': []})
    health = load_json(HEALTH, {'status': 'unknown', 'issues': []})

    totals = pipe.get('totals', {})
    items = pipe.get('items', [])
    promoted = backlog.get('created', [])
    promoted_count = len(promoted)
    updated_at = backlog.get('generated_at') or datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    ready_items = [x for x in items if x.get('ready') and x.get('pdf')]
    unfinished_items = [x for x in items if not x.get('ready')]

    promoted_lines = ''.join([
        f"<li>{x.get('thread','?')}: <code class=\"inline\">{Path(x.get('from','')).name}</code></li>"
        for x in promoted
    ]) or '<li>No promotions in latest run.</li>'

    ready_lines = ''.join([
        f"<li><a href=\"/cohera/publications/pdf/{Path(x.get('pdf','')).name}\">{x.get('title','Untitled')}</a></li>"
        for x in ready_items[:8]
    ]) or '<li>No ready publications yet.</li>'

    unfinished_lines = ''.join([
        f"<li>{x.get('thread','?')}: <code class=\"inline\">{Path((x.get('digest_html') or x.get('tex') or '')).name}</code></li>"
        for x in unfinished_items[:10]
    ]) or '<li>No unfinished entries tracked.</li>'

    research_index = SITE / 'research' / 'index.html'
    research_index.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Research · Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
</head>
<body>
  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/cosmos/index.html">Cosmos</a><a href="/cohera/regenesis/index.html">Regenesis</a><a href="/cohera/ethos/index.html">Ethos</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
  </nav></div></header>
  <main class="container">
    <section class="hero"><h1>Research</h1><p class="small">Live pipeline status. Updated: {updated_at}</p></section>
    <section class="card"><h3>Latest cycle status</h3><ul class="clean">
      <li>Pipeline health: <strong>{health.get('status','unknown')}</strong></li>
      <li>Issues: {len(health.get('issues', []))}</li>
      <li>Backlog promotions this cycle: <strong>{promoted_count}</strong></li>
      <li>Ready publications: <strong>{totals.get('ready_publications',0)}</strong> / {totals.get('items',0)}</li>
    </ul></section>
    <section class="card"><h3>Promoted this cycle</h3><ul class="clean">{promoted_lines}</ul></section>
    <section class="card"><h3>Unfinished queue (next to promote)</h3><ul class="clean">{unfinished_lines}</ul></section>
    <section class="card"><h3>Links</h3><ul class="clean">
      <li><a href="/cohera/research/findings-latest.html">Findings (latest)</a></li>
      <li><a href="/cohera/research/autopilot-queue.html">Autopilot Queue</a></li>
      <li><a href="/cohera/cosmos/index.html">Cosmos</a> · <a href="/cohera/regenesis/index.html">Regenesis</a> · <a href="/cohera/ethos/index.html">Ethos</a></li>
    </ul></section>
  </main>
</body>
</html>
''', encoding='utf-8')

    publications_index = SITE / 'publications' / 'index.html'
    publications_index.write_text(f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publications · Cohera Lab</title><link rel="stylesheet" href="/cohera/assets/style.css" />
</head><body>
<header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
<a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
</nav></div></header>
<main class="container">
<section class="hero"><h1>Publications</h1><p class="small">Final reader-ready papers only. Updated: {updated_at}</p></section>
<section class="card"><ul class="clean">
<li>Ready publications: <strong>{totals.get('ready_publications',0)}</strong></li>
<li>PDF built: {totals.get('with_pdf',0)} / {totals.get('items',0)}</li>
<li>In-progress manuscripts: {len(unfinished_items)}</li>
<li><a href="/cohera/publications/pdf/index.html">PDF Publications</a></li>
<li><a href="/cohera/research/findings-latest.html">Findings (latest)</a></li>
</ul></section>
<section class="card"><h3>Published now</h3><ul class="clean">{ready_lines}</ul></section>
<section class="card"><h3>Currently in publication pipeline</h3><ul class="clean">{unfinished_lines}</ul></section>
</main>
</body></html>
''', encoding='utf-8')

    print('surface_status_updated=research/index.html,publications/index.html')


if __name__ == '__main__':
    main()
