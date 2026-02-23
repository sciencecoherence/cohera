#!/usr/bin/env python3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site' / 'research'
OUT_DIR = REPO / 'site' / 'publications'
HEALTH = REPO / 'chatgpt' / 'research_health.json'
DELTA = REPO / 'chatgpt' / 'research_delta_latest.json'
BACKLOG = REPO / 'chatgpt' / 'research_backlog_run.json'
PIPE = REPO / 'chatgpt' / 'publication_pipeline.json'

def load_json(p: Path, default_val):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            logging.warning(f"Corrupt JSON at {p}. Using default.")
    return default_val

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

    backlog_rows = [f"<strong>{x.get('thread', 'UNKNOWN').upper()}</strong>: <code>{x.get('from')}</code>" for x in backlog.get('created', [])]
    
    top_rows = []
    for t in delta.get('top_priority', [])[:8]:
        src = (t.get('path','') or '').split('/')[-1]
        top_rows.append(f"<strong>{t.get('thread','UNKNOWN').upper()}</strong>: <code>{src}</code>")

    out = OUT_DIR / f'findings-{day}.html'
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Upgraded HTML to match Brutalist/Monospace aesthetic and include the Synthesis Block
    out.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Global Synthesis · {day} | Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
  <style>
    body {{ background: #0a0a0a; color: #e0e0e0; font-family: monospace; line-height: 1.6; padding: 2rem; }}
    .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem; }}
    .card {{ border: 1px solid #333; padding: 1.5rem; background: #111; }}
    .synthesis-zone {{ border: 2px dashed #555; padding: 2rem; margin-top: 2rem; background: #050505; }}
    h1, h3 {{ text-transform: uppercase; letter-spacing: 1px; margin-top: 0; }}
    .highlight {{ color: #fff; font-weight: bold; background: #333; padding: 0 4px; }}
    ul.clean {{ list-style-type: none; padding-left: 0; }}
    ul.clean li {{ margin-bottom: 0.5rem; border-bottom: 1px solid #222; padding-bottom: 0.5rem; }}
    @media (max-width: 800px) {{ .grid-container {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main class="container">
    <header>
      <h1>Global Synthesis Report</h1>
      <p>Cycle Date: {day} | Status: {health.get('status','UNKNOWN').upper()}</p>
    </header>

    <section class="synthesis-zone">
      <h3>Cycle Synthesis (Awaiting Cohera Output)</h3>
      <p><em>[SYSTEM DIRECTIVE: Cohera, replace this text with a highly condensed, high-level narrative connecting the promoted backlog items and top priorities to our core AXIOMS. Do not list numbers. Synthesize the theoretical progress made today.]</em></p>
    </section>

    <div class="grid-container">
      <section class="card">
        <h3>System Metrics</h3>
        <ul class="clean">
          <li>Autodrafts Generated: <span class="highlight">{health.get('autodrafts_created_count', 0)}</span></li>
          <li>New Sources Ingested: <span class="highlight">{delta.get('counts',{{}}).get('new',0)}</span></li>
          <li>Pipeline Issues: <span class="highlight">{len(health.get('issues', []))}</span></li>
        </ul>
      </section>
      
      <section class="card">
        <h3>Publication State</h3>
        <ul class="clean">
          <li>Active Candidates: <span class="highlight">{pipe.get('totals',{{}}).get('items',0)}</span></li>
          <li>TeX Formalized: <span class="highlight">{pipe.get('totals',{{}}).get('with_tex',0)}</span></li>
          <li>Ready for Deployment: <span class="highlight">{pipe.get('totals',{{}}).get('ready_publications',0)}</span></li>
        </ul>
      </section>
    </div>

    <div class="grid-container">
      <section class="card">
        <h3>Promoted to Synthesis (State 2)</h3>
        <ul class="clean">{li(backlog_rows, 'No State 2 promotions this cycle.')}</ul>
      </section>

      <section class="card">
        <h3>High-Priority Targets (State 1)</h3>
        <ul class="clean">{li(top_rows, 'No active targets.')}</ul>
      </section>
    </div>
  </main>
</body>
</html>
''', encoding='utf-8')

    latest = OUT_DIR / 'findings-latest.html'
    latest.write_text(out.read_text(encoding='utf-8'), encoding='utf-8')

    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / 'findings-latest.html').write_text(out.read_text(encoding='utf-8'), encoding='utf-8')

    logging.info(f"Findings generated: {out.relative_to(REPO)}")

if __name__ == '__main__':
    main()
