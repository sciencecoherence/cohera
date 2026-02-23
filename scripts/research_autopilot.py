#!/usr/bin/env python3
import json
import re
import subprocess
import tempfile
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

REPO = Path('/home/xavier/cohera-repo')
CHATGPT_DIR = REPO / 'chatgpt'
SITE_DIR = REPO / 'site'
STATE_PATH = CHATGPT_DIR / 'research_state.json'
QUEUE_PATH = CHATGPT_DIR / 'research_queue.json'
PUB_PAGE = SITE_DIR / 'research' / 'autopilot-queue.html'

# Upgraded to heavily weight the specific frameworks
THREAD_KEYWORDS = {
    'cosmos': [
        'cosmos', 'quantum', 'gravity', 'spacetime', 'holographic', 'entropy',
        'floquet', 'dark-matter', 'time-crystal', 'bures', 'fisher', 'tensor', 
        'geometry', 'emergence', 'coherence'
    ],
    'regenesis': [
        'sleep', 'nutrition', 'biology', 'metabolic', 'autophagy', 'ghk-cu',
        'regeneration', 'gut', 'circadian', 'bioelectric', 'microtubule', 
        'chemiosmosis', 'mitochondria', 'pump-alignment', 'time-crystalline'
    ],
    'ethos': [
        'ethos', 'education', 'epistemology', 'agency', 'governance', 
        'qualitative', 'methodology', 'philosophy', 'cognition', 'judgment'
    ],
}

# Scientific markers for better claim extraction
CLAIM_MARKERS = re.compile(r'\b(we show|demonstrate|propose|conclude|results indicate|evidence suggests|hypothesize|measure)\b', re.IGNORECASE)

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
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            logging.warning(f"Corrupted JSON at {path}. Reverting to default.")
    return default

def collect_sources() -> List[Item]:
    items = []
    for p in CHATGPT_DIR.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.pdf', '.tex'}:
            continue
        st = p.stat()
        thread = classify_thread(p.name)
        # Prioritize PDFs and recently modified files
        score = 2 if p.suffix.lower() == '.pdf' else 1
        score += int((datetime.now().timestamp() - st.st_mtime) < 7 * 86400) * 2 
        items.append(Item(
            path=str(p.relative_to(REPO)),
            ext=p.suffix.lower().lstrip('.'),
            mtime=int(st.st_mtime),
            size=st.st_size,
            thread=thread,
            score=score,
        ))
    return sorted(items, key=lambda x: (x.score, x.mtime), reverse=True)

def extract_text_preview(abs_path: Path, max_chars: int = 8000) -> Tuple[str, str]:
    if not abs_path.exists():
        return '', 'n/a'
    suffix = abs_path.suffix.lower()
    try:
        if suffix == '.pdf':
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=True) as tf:
                subprocess.run(
                    ['pdftotext', '-f', '1', '-l', '3', str(abs_path), tf.name], # Extended to 3 pages for better abstracts
                    check=True, capture_output=True, text=True
                )
                txt = Path(tf.name).read_text(encoding='utf-8', errors='ignore')
                return re.sub(r'\s+', ' ', txt).strip()[:max_chars], 'Pages 1-3'
        
        return re.sub(r'\s+', ' ', abs_path.read_text(encoding='utf-8', errors='ignore')).strip()[:max_chars], 'full-text'
    except Exception as e:
        logging.error(f"Failed to extract text from {abs_path.name}: {e}")
        return '', 'n/a'

def extract_structured_notes(src_rel: str) -> dict:
abs_path = REPO / src_rel
preview, page_window = extract_text_preview(abs_path)
base = Path(src_rel).stem.replace('_', ' ')
pretty_title = re.sub(r'\s+', ' ', base).strip()

abstract = ''
doi = ''
if preview:
    m_doi = re.search(r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', preview, re.IGNORECASE)
    if m_doi:
        doi = m_doi.group(1)
    
    m_abs = re.search(r'(?i)abstract[\s\.\-\:]*(.*?)(?=(?i)(introduction|1\.\s|keywords|background))', preview)
    if m_abs:
        abstract = m_abs.group(1).strip()
    else:
        abstract = preview[:500] + "..."

# Robust Claim Extraction
try:
    sentences = [s.strip() for s in re.split(r'[.!?]\s+', preview) if len(s.strip()) > 40]
except Exception:
    sentences = [s.strip() for s in preview.split('\n') if len(s.strip()) > 40]

claim_map = []
scientific_claims = [s for s in sentences if CLAIM_MARKERS.search(s)]
target_sentences = scientific_claims[:3] if scientific_claims else sentences[3:6]

for s in target_sentences:
    short_claim = s[:150] + ('...' if len(s) > 150 else '')
    claim_map.append({
        'claim': short_claim,
        'evidence_quote': s,
        'page_hint': page_window
    })

findings = [
    f"Domain classification: {classify_thread(pretty_title).upper()}",
    "Source ingested via Auto-Research Pipeline.",
    "Awaiting Phase 2 Synthesis (Candidate Promotion)."
]

return {
    'title': pretty_title,
    'abstract': abstract,
    'doi': doi,
    'findings': findings,
    'evidence': [f"Source: {src_rel}", f"Scope: {page_window}"],
    'claim_map': claim_map
}

# Smart Claim Extraction with Safe Fall-through
    try:
        # We use a non-capturing group for the split to prevent regex errors on malformed text
        sentences = [s.strip() for s in re.split(r'(?:[.!?])\s+', preview) if len(s.strip()) > 40]
    except re.error:
        # Fallback to simple newline split if the complex regex fails
        sentences = [s.strip() for s in preview.split('\n') if len(s.strip()) > 40]

    claim_map = []
    
    # Prioritize sentences with actual scientific claim markers
    scientific_claims = [s for s in sentences if CLAIM_MARKERS.search(s)]
    
    # Use scientific claims first; fallback to sentences in the middle of the preview 
    # (avoiding potential title/author junk at the start)
    target_sentences = scientific_claims[:3] if scientific_claims else sentences[3:6]

    for s in target_sentences:
        short_claim = s[:150] + ('…' if len(s) > 150 else '')
        claim_map.append({
            'claim': short_claim,
            'evidence_quote': s,
            'page_hint': page_window,
        }))

    findings = [
        f"Domain classification: {classify_thread(pretty_title).upper()}",
        "Source ingested via Auto-Research Pipeline.",
        "Awaiting Phase 2 Synthesis (Candidate Promotion)."
    ]

    return {
        'title': pretty_title,
        'abstract': abstract,
        'doi': doi,
        'findings': findings,
        'evidence': [f"Source: {src_rel}", f"Scope: {page_window}"],
        'claim_map': claim_map,
    }

def upsert_digest_stub(thread: str, src_rel: str, date_str: str) -> str:
    notes = extract_structured_notes(src_rel)
    base = Path(src_rel).stem
    digest_dir = SITE_DIR / thread / 'digests'
    digest_dir.mkdir(parents=True, exist_ok=True)

    stable_slug = slugify(f'auto-{base}')
    index_path = digest_dir / 'index.json'
    idx = load_json(index_path, [])

    existing_slug = next((row.get('slug') for row in idx if row.get('title') == f"Autodraft: {notes['title']}"), None)
    slug = existing_slug or stable_slug
    html_path = digest_dir / f'{slug}.html'

    claim_map_html = ''.join([
        f"<div class='claim-block'><p><strong>Claim:</strong> {c['claim']}</p><blockquote>{c['evidence_quote']}</blockquote><small>Loc: {c['page_hint']}</small></div>"
        for c in notes.get('claim_map', [])
    ]) or '<p>No structural claims detected.</p>'
    
    doi_link = f"<a href='https://doi.org/{notes['doi']}' target='_blank'>{notes['doi']}</a>" if notes['doi'] else "N/A"

    # Brutalist / Organic Modernist HTML Template
    html_path.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{notes['title']} | Cohera Pipeline</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
  <style>
    /* Brutalist overrides for internal tools */
    body {{ background: #0a0a0a; color: #e0e0e0; font-family: monospace; line-height: 1.6; padding: 2rem; }}
    .status-badge {{ display: inline-block; background: #e0e0e0; color: #0a0a0a; padding: 2px 8px; font-weight: bold; margin-bottom: 1rem; }}
    .card {{ border: 1px solid #333; padding: 1.5rem; margin-top: 1rem; }}
    blockquote {{ border-left: 3px solid #555; padding-left: 1rem; margin-left: 0; color: #aaa; }}
    h1, h3 {{ text-transform: uppercase; letter-spacing: 1px; }}
  </style>
</head>
<body>
  <main class="container">
    <header>
        <h1>Autodraft</h1>
        <h2>{notes['title']}</h2>
        <div class="status-badge">[STATUS: READY FOR SYNTHESIS]</div>
        <p>Thread: {thread.upper()} | Ingested: {date_str}</p>
    </header>
    
    <article class="card">
      <h3>Metadata</h3>
      <p><strong>File:</strong> <code>{src_rel}</code></p>
      <p><strong>DOI:</strong> {doi_link}</p>
      
      <h3>Raw Abstract</h3>
      <blockquote>{notes['abstract']}</blockquote>
      
      <h3>Extracted Vectors</h3>
      {claim_map_html}
    </article>
  </main>
</body>
</html>
''', encoding='utf-8')

    # Update index
    if not existing_slug:
        idx.insert(0, {
            'slug': slug,
            'title': f"Autodraft: {notes['title']}",
            'date': date_str,
            'tags': [thread, 'autodraft', Path(src_rel).suffix.lstrip('.')],
            'confidence': 'Phase 1 - Unverified'
        })
    
    # Deduplicate and save
    seen = set()
    dedup = [row for row in idx if row.get('slug') and not (row['slug'] in seen or seen.add(row['slug']))]
    index_path.write_text(json.dumps(dedup, indent=2), encoding='utf-8')

    return slug

def main():
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_str = datetime.now().strftime('%Y-%m-%d')

    prev = load_json(STATE_PATH, {'files': {}})
    prev_files = prev.get('files', {})

    items = collect_sources()
    current_files = {it.path: {'mtime': it.mtime, 'size': it.size, 'thread': it.thread} for it in items}

    changed = [
        {'path': p, 'change': 'new', **meta} for p, meta in current_files.items() if p not in prev_files
    ] + [
        {'path': p, 'change': 'updated', **meta} for p, meta in current_files.items() 
        if p in prev_files and (prev_files[p].get('mtime') != meta['mtime'] or prev_files[p].get('size') != meta['size'])
    ]

    changed_candidates = [c for c in changed if c.get('thread')]
    per_thread = {c.get('thread'): c for c in changed_candidates}

    if len(per_thread) < 3:
        for it in items:
            if it.thread not in per_thread:
                per_thread[it.thread] = {'thread': it.thread, 'path': it.path, 'change': 'priority-fallback'}
            if len(per_thread) >= 3:
                break

    created = []
    for thread in ['cosmos', 'regenesis', 'ethos']:
        if c := per_thread.get(thread):
            slug = upsert_digest_stub(thread, c['path'], date_str)
            created.append({'thread': thread, 'slug': slug, 'source': c['path']})

    queue = {
        'generated_at': ts,
        'total_sources': len(items),
        'autodrafts_created': created,
    }
    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    STATE_PATH.write_text(json.dumps({'generated_at': ts, 'files': current_files}, indent=2), encoding='utf-8')
    
    logging.info(f"Pipeline executed. Sources ingested: {len(items)}. Stubs generated: {len(created)}")

if __name__ == '__main__':
    main()
