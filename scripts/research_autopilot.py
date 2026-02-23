#!/usr/bin/env python3
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO = Path('/home/xavier/cohera-repo')
CHATGPT_DIR = REPO / 'chatgpt'
SITE_DIR = REPO / 'site'
STATE_PATH = CHATGPT_DIR / 'research_state.json'
QUEUE_PATH = CHATGPT_DIR / 'research_queue.json'
PUB_PAGE = SITE_DIR / 'publications' / 'autopilot-queue.html'

THREAD_KEYWORDS = {
    'cosmos': [
        'cosmos', 'quantum', 'gravity', 'spacetime', 'black', 'schrodinger', 'entropy',
        'holograph', 'floquet', 'equilibrium', 'informationportal', 'dark-matter',
        'astroph', 'cosmolog', 'time-crystal', 'crystal', 'qft', 'relativity', 'vacuum'
    ],
    'regenesis': [
        'sleep', 'nutrition', 'biology', 'molecular', 'metabolic', 'autophagy',
        'regeneration', 'gut', 'circadian', 'bioelectric', 'microtubule', 'neuron',
        'chemiosmosis', 'cell', 'mitochond', 'health', 'longevity', 'pump-alignment'
    ],
    'ethos': [
        'ethos', 'education', 'learning', 'epistem', 'practice', 'lifestyle', 'agency',
        'focus', 'governance', 'ethic', 'ai-govern', 'knowledge', 'judgment', 'violence',
        'awareness', 'qualitative', 'methodology', 'philosophy'
    ],
}


@dataclass
class Item:
    path: str
    ext: str
    mtime: int
    size: int
    thread: str
    score: int


def classify_thread(name: str) -> str:
    n = name.lower()
    scores = {k: 0 for k in THREAD_KEYWORDS}
    for thread, kws in THREAD_KEYWORDS.items():
        for kw in kws:
            if kw in n:
                scores[thread] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else 'cosmos'


def slugify(s: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return re.sub(r'-{2,}', '-', s)[:80]


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def collect_sources() -> List[Item]:
    items = []
    for p in CHATGPT_DIR.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {'.pdf', '.tex'}:
            continue
        st = p.stat()
        thread = classify_thread(p.name)
        score = 2 if p.suffix.lower() == '.pdf' else 1
        score += int((datetime.now().timestamp() - st.st_mtime) < 7 * 86400)
        items.append(Item(
            path=str(p.relative_to(REPO)),
            ext=p.suffix.lower().lstrip('.'),
            mtime=int(st.st_mtime),
            size=st.st_size,
            thread=thread,
            score=score,
        ))
    return sorted(items, key=lambda x: (x.score, x.mtime), reverse=True)


def extract_text_preview(abs_path: Path, max_chars: int = 5000):
    if not abs_path.exists():
        return '', 'n/a'
    suffix = abs_path.suffix.lower()
    try:
        if suffix == '.pdf':
            page_window = '1-2'
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=True) as tf:
                subprocess.run(
                    ['pdftotext', '-f', '1', '-l', '2', str(abs_path), tf.name],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                txt = Path(tf.name).read_text(encoding='utf-8', errors='ignore')
                return re.sub(r'\s+', ' ', txt).strip()[:max_chars], page_window
        # lightweight text preview for tex/other text-like files
        return re.sub(r'\s+', ' ', abs_path.read_text(encoding='utf-8', errors='ignore')).strip()[:max_chars], 'full-text'
    except Exception:
        return '', 'n/a'


def extract_structured_notes(src_rel: str):
    abs_path = REPO / src_rel
    preview, page_window = extract_text_preview(abs_path)

    base = Path(src_rel).stem.replace('_', ' ')
    pretty_title = re.sub(r'\s+', ' ', base).strip()

    abstract = ''
    doi = ''
    if preview:
        m_abs = re.search(r'(abstract\s*[:\-]?\s*)(.{120,1200}?)(?:\b(introduction|keywords|1\.|i\.))', preview, re.IGNORECASE)
        if m_abs:
            abstract = m_abs.group(2).strip()
        m_doi = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', preview, re.IGNORECASE)
        if m_doi:
            doi = m_doi.group(1)

    if not abstract and preview:
        abstract = preview[:420]

    # Heuristic findings from filename tokens
    tokens = [t for t in re.split(r'[^a-zA-Z0-9]+', pretty_title.lower()) if len(t) > 3]
    top_tokens = []
    for t in tokens:
        if t not in top_tokens and t not in {'with', 'from', 'that', 'this', 'through', 'into'}:
            top_tokens.append(t)
        if len(top_tokens) == 4:
            break

    findings = [
        f"Primary topic appears to center on: {', '.join(top_tokens) if top_tokens else 'general research content'}.",
        'Source was auto-indexed and text-previewed for rapid triage.',
        'Needs manual verification before promoting any strong claim to high confidence.'
    ]

    # Claim → evidence sentence mapping (heuristic)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', preview) if len(s.strip()) > 60]
    claim_map = []
    for s in sentences[:3]:
        short_claim = s[:180] + ('…' if len(s) > 180 else '')
        claim_map.append({
            'claim': short_claim,
            'evidence_quote': s,
            'page_hint': page_window,
        })

    evidence = []
    if doi:
        evidence.append(f'DOI detected: {doi}')
    evidence.append(f'Source file: {src_rel}')
    evidence.append(f'Extraction scope: {page_window}')
    if abstract:
        evidence.append('Abstract/preview extracted automatically.')

    return {
        'title': pretty_title,
        'abstract': abstract,
        'doi': doi,
        'findings': findings,
        'evidence': evidence,
        'claim_map': claim_map,
    }


def upsert_digest_stub(thread: str, src_rel: str, date_str: str) -> str:
    notes = extract_structured_notes(src_rel)
    base = Path(src_rel).stem
    digest_dir = SITE_DIR / thread / 'digests'
    digest_dir.mkdir(parents=True, exist_ok=True)

    # Stable slug per source to avoid day-by-day duplicates.
    stable_slug = slugify(f'auto-{base}')

    index_path = digest_dir / 'index.json'
    idx = load_json(index_path, [])

    # Reuse existing entry for this source/title when available.
    existing_slug = None
    target_title = f"Autodraft: {notes['title']}"
    for row in idx:
        if row.get('title') == target_title:
            existing_slug = row.get('slug')
            break

    slug = existing_slug or stable_slug
    html_path = digest_dir / f'{slug}.html'

    findings_html = ''.join([f'<li>{x}</li>' for x in notes['findings']])
    evidence_html = ''.join([f'<li>{x}</li>' for x in notes['evidence']])
    claim_map_html = ''.join([
        f"<li><strong>Claim:</strong> {c['claim']}<br/><strong>Evidence quote:</strong> “{c['evidence_quote']}”<br/><strong>Page hint:</strong> {c['page_hint']}</li>"
        for c in notes.get('claim_map', [])
    ]) or '<li>No claim/evidence sentences extracted automatically.</li>'
    abstract_html = notes['abstract'] or 'No abstract preview extracted.'
    doi_html = f"<p><strong>DOI:</strong> <a href=\"https://doi.org/{notes['doi']}\">{notes['doi']}</a></p>" if notes['doi'] else '<p><strong>DOI:</strong> not detected automatically.</p>'

    # Always refresh content so re-runs improve existing drafts.
    html_path.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Autodraft · {notes['title']} · Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
</head>
<body>
  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
    <a href="/cohera/index.html">Home</a><a href="/cohera/cosmos/index.html">Cosmos</a><a href="/cohera/regenesis/index.html">Regenesis</a><a href="/cohera/ethos/index.html">Ethos</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
  </nav></div></header>
  <main class="container">
    <section class="hero">
      <h1>Autodraft: {notes['title']}</h1>
      <p class="small">Date: {date_str} · Thread: {thread} · Status: extracted-draft · Confidence: low-medium</p>
    </section>
    <article class="card">
      <h3>Source</h3>
      <p><code class="inline">{src_rel}</code></p>
      {doi_html}
      <h3>Auto summary (preview-based)</h3>
      <p>{abstract_html}</p>
      <h3>Key findings (auto-extracted)</h3>
      <ul class="clean">{findings_html}</ul>
      <h3>Evidence & citations</h3>
      <ul class="clean">{evidence_html}</ul>
      <h3>Claim → evidence mapping (auto)</h3>
      <ul class="clean">{claim_map_html}</ul>
      <h3>Falsification / validation checklist</h3>
      <ul class="clean">
        <li>Re-read full source and verify the central claim sentence-by-sentence.</li>
        <li>Cross-check against at least one independent source before promotion.</li>
        <li>Keep confidence at low-medium until replication or corroboration is explicit.</li>
      </ul>
      <h3>Next queries</h3>
      <ul class="clean"><li>What is the smallest testable claim from this source?</li></ul>
    </article>
  </main>
</body>
</html>
''', encoding='utf-8')

    if not any(x.get('slug') == slug for x in idx):
        idx.insert(0, {
            'slug': slug,
            'title': target_title,
            'date': date_str,
            'tags': [thread, 'autodraft', Path(src_rel).suffix.lstrip('.')],
            'confidence': 'low-medium'
        })
    else:
        # Refresh date/confidence in index for existing entries.
        for row in idx:
            if row.get('slug') == slug:
                row['date'] = date_str
                row['confidence'] = 'low-medium'

    # Deduplicate by slug, keep first occurrence.
    dedup = []
    seen = set()
    for row in idx:
        s = row.get('slug')
        if s and s not in seen:
            dedup.append(row)
            seen.add(s)
    index_path.write_text(json.dumps(dedup, indent=2), encoding='utf-8')

    return slug


def build_publication_page(ts: str, changed: List[Dict], top_items: List[Item]):
    rows = []
    for it in top_items[:15]:
        rows.append(f"<li><strong>{it.thread}</strong> · <code class=\"inline\">{it.path}</code> · score {it.score}</li>")

    changed_rows = []
    for c in changed[:30]:
        changed_rows.append(f"<li><code class=\"inline\">{c['path']}</code> ({c['change']})</li>")

    PUB_PAGE.parent.mkdir(parents=True, exist_ok=True)
    PUB_PAGE.write_text(f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Autopilot Queue · Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
</head>
<body>
<header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
<a href="/cohera/index.html">Home</a><a href="/cohera/cosmos/index.html">Cosmos</a><a href="/cohera/regenesis/index.html">Regenesis</a><a href="/cohera/ethos/index.html">Ethos</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>
</nav></div></header>
<main class="container">
<section class="hero"><h1>Autopilot Queue</h1><p class="small">Generated at {ts} UTC</p></section>
<section class="card"><h3>Top source priorities</h3><ul class="clean">{''.join(rows) or '<li>No sources found.</li>'}</ul></section>
<section class="card"><h3>Detected changes</h3><ul class="clean">{''.join(changed_rows) or '<li>No changes since last run.</li>'}</ul></section>
</main>
</body></html>
''', encoding='utf-8')


def main():
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_str = datetime.now().strftime('%Y-%m-%d')

    prev = load_json(STATE_PATH, {'files': {}})
    prev_files = prev.get('files', {})

    items = collect_sources()
    current_files = {it.path: {'mtime': it.mtime, 'size': it.size, 'thread': it.thread} for it in items}

    changed = []
    for p, meta in current_files.items():
        if p not in prev_files:
            changed.append({'path': p, 'change': 'new', **meta})
        elif prev_files[p].get('mtime') != meta['mtime'] or prev_files[p].get('size') != meta['size']:
            changed.append({'path': p, 'change': 'updated', **meta})
    for p in prev_files:
        if p not in current_files:
            changed.append({'path': p, 'change': 'removed'})

    # Create digest stubs with per-thread balancing:
    # 1) Prefer changed files (new/updated)
    # 2) If a thread has no changed candidate, fallback to top-ranked source in that thread
    changed_candidates = [c for c in changed if c.get('change') in {'new', 'updated'} and c.get('thread')]
    per_thread = {}
    for c in changed_candidates:
        t = c.get('thread')
        if t and t not in per_thread:
            per_thread[t] = c

    if len(per_thread) < 3:
        for it in items:
            t = it.thread
            if t not in per_thread:
                per_thread[t] = {'thread': t, 'path': it.path, 'change': 'priority-fallback'}
            if len(per_thread) == 3:
                break

    created = []
    for thread in ['cosmos', 'regenesis', 'ethos']:
        c = per_thread.get(thread)
        if c:
            slug = upsert_digest_stub(thread, c['path'], date_str)
            created.append({'thread': thread, 'slug': slug, 'source': c['path'], 'selector': c.get('change', 'unknown')})

    queue = {
        'generated_at': ts,
        'total_sources': len(items),
        'changes': changed,
        'top_priority': [asdict(x) for x in items[:20]],
        'autodrafts_created': created,
    }
    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding='utf-8')

    build_publication_page(ts, changed, items)

    STATE_PATH.write_text(json.dumps({'generated_at': ts, 'files': current_files}, indent=2), encoding='utf-8')
    print(f'Autopilot complete. Sources={len(items)} changes={len(changed)} stubs={len(created)}')


if __name__ == '__main__':
    main()
