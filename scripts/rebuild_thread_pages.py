#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site'
THREADS = {
    'cosmos': 'Framework physics, coherence operators, and emergence geometry.',
    'regenesis': 'Bioelectricity, recovery protocols, and validation loops.',
    'ethos': 'Research literacy, governance, and epistemic discipline.',
}


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def render_thread(thread: str, subtitle: str):
    idx = SITE / thread / 'digests' / 'index.json'
    rows = load_json(idx, [])
    updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    items = []
    for r in rows[:16]:
        slug = r.get('slug')
        title = r.get('title') or slug
        if not slug:
            continue
        status = 'pipeline draft' if str(title).lower().startswith('autodraft:') or str(slug).startswith('auto-') else 'candidate'
        items.append((title, slug, status, r.get('date', '')))

    lines = [
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        f'  <title>{thread.title()} · Cohera Lab</title>',
        '  <link rel="stylesheet" href="/cohera/assets/style.css" />',
        '</head>',
        '<body>',
        '  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">',
        '    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/cosmos/index.html">Cosmos</a><a href="/cohera/regenesis/index.html">Regenesis</a><a href="/cohera/ethos/index.html">Ethos</a>',
        '  </nav></div></header>',
        '  <main class="container">',
        f'    <section class="hero"><h1>{thread.title()}</h1><p class="small">{subtitle}</p><p class="small">Updated: {updated}</p></section>',
        '    <section class="card"><h3>Thread pipeline items</h3><ul class="clean">',
    ]

    if items:
        for title, slug, status, date in items:
            lines.append(f'      <li><a href="/cohera/{thread}/digests/{slug}.html">{title}</a> <span class="small">· {status}{" · " + date if date else ""}</span></li>')
    else:
        lines.append('      <li>No items yet.</li>')

    lines += [
        '    </ul></section>',
        '    <section class="card"><h3>Flow rule</h3><p class="small">Items here are active research. Only finalized, polished papers move to Publications.</p></section>',
        '  </main>',
        '</body>',
        '</html>',
    ]

    (SITE / thread / 'index.html').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    for t, subtitle in THREADS.items():
        render_thread(t, subtitle)
    print('thread_pages_rebuilt=cosmos,regenesis,ethos')


if __name__ == '__main__':
    main()
