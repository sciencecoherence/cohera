#!/usr/bin/env python3
import os, re, json
from pathlib import Path
from datetime import datetime, timezone

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site'
OUT = SITE / 'publications' / 'design-audit-latest.html'

html_files = sorted(SITE.rglob('*.html'))
all_urls = set('/cohera/' + str(p.relative_to(SITE)).replace(os.sep, '/') for p in html_files)

issues = []
summary = {'pages': len(html_files), 'broken_links': 0, 'missing_meta_description': 0, 'missing_h1': 0}

for p in html_files:
    txt = p.read_text(encoding='utf-8', errors='ignore')
    rel = '/cohera/' + str(p.relative_to(SITE)).replace(os.sep, '/')

    if '<meta name="description"' not in txt:
        summary['missing_meta_description'] += 1
        issues.append((rel, 'missing meta description'))
    if '<h1' not in txt:
        summary['missing_h1'] += 1
        issues.append((rel, 'missing h1'))

    for m in re.findall(r'href=["\']([^"\']+)["\']', txt):
        if m.startswith('/cohera/') and not (m in all_urls or m.endswith('/') and (m + 'index.html') in all_urls):
            summary['broken_links'] += 1
            issues.append((rel, f'broken internal link: {m}'))

now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

rows = '\n'.join(f'<li><code>{a}</code> — {b}</li>' for a, b in issues[:200]) or '<li>No structural issues detected in this pass.</li>'

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Daily Design Audit · Cohera Lab</title>
<link rel="stylesheet" href="/cohera/assets/style.css" />
</head><body>
<header><div class="container nav"><div class="brand">Cohera Lab</div><nav class="nav-links">
<a href="/cohera/index.html">Home</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
</nav></div></header>
<main class="container">
<section class="hero"><span class="eyebrow">Daily Audit</span><h1>Website Coherence + Design Audit</h1><p class="small">Generated: {now}</p></section>
<section class="grid">
<article class="card"><h3>Pages</h3><strong>{summary['pages']}</strong></article>
<article class="card"><h3>Broken links</h3><strong>{summary['broken_links']}</strong></article>
<article class="card"><h3>Missing meta description</h3><strong>{summary['missing_meta_description']}</strong></article>
<article class="card"><h3>Missing H1</h3><strong>{summary['missing_h1']}</strong></article>
</section>
<section class="card"><h3>Detected Issues</h3><ul class="clean">{rows}</ul></section>
<section class="card"><h3>Next Design Study Focus</h3><ul class="clean"><li>Typography rhythm and spacing consistency</li><li>Mobile navigation ergonomics</li><li>Card hierarchy and scanability</li></ul></section>
</main></body></html>''', encoding='utf-8')

print('Audit generated:', OUT)
