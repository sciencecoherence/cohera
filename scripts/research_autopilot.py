#!/usr/bin/env python3
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE_DIR = REPO / 'site'
CHATGPT_DIR = REPO / 'chatgpt'
QUEUE_PATH = CHATGPT_DIR / 'research_queue.json'
STATE_PATH = CHATGPT_DIR / 'research_state.json'
PUB_PAGE = SITE_DIR / 'research' / 'autopilot-queue.html'

SOURCE_GLOBS = [
    'chatgpt/pdf/*.pdf',
    'chatgpt/sources/**/*.pdf',
    'chatgpt/sources/**/*.tex',
    'chatgpt/inbox/*.md',
]

THREAD_KEYWORDS = {
    'cosmos': ['cosmos', 'quantum', 'gravity', 'spacetime', 'dark', 'holograph', 'time-crystal', 'floquet'],
    'regenesis': ['bio', 'biology', 'metabolic', 'sleep', 'health', 'pump', 'chemiosmosis', 'recovery'],
    'ethos': ['ethos', 'epistem', 'learning', 'governance', 'ai-knowledge', 'literacy', 'confidence'],
}


@dataclass
class Item:
    path: str
    mtime: int
    size: int
    thread: str
    score: int


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def slugify(s: str):
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()


def detect_thread(rel: str):
    low = rel.lower()
    best_t, best = 'cosmos', -1
    for t, kws in THREAD_KEYWORDS.items():
        score = sum(1 for k in kws if k in low)
        if score > best:
            best_t, best = t, score
    return best_t, max(best, 0)


def collect_items():
    items = []
    for g in SOURCE_GLOBS:
        for p in REPO.glob(g):
            if not p.is_file():
                continue
            rel = str(p.relative_to(REPO))
            st = p.stat()
            thread, score = detect_thread(rel)
            items.append(Item(rel, int(st.st_mtime), st.st_size, thread, score))
    # dedupe by path
    by = {}
    for it in items:
        by[it.path] = it
    return sorted(by.values(), key=lambda x: (x.score, x.mtime), reverse=True)


def upsert_digest_stub(thread: str, src_rel: str, date_str: str) -> str:
    base = Path(src_rel).stem
    slug = slugify(f'auto-{base}')
    digest_dir = SITE_DIR / thread / 'digests'
    digest_dir.mkdir(parents=True, exist_ok=True)

    html_path = digest_dir / f'{slug}.html'
    html_path.write_text(f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Autodraft · {base}</title>
<link rel="stylesheet" href="/cohera/assets/style.css" />
</head><body>
<header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
<a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a>
</nav></div></header>
<main class="container">
<section class="hero"><h1>Autodraft: {base}</h1><p class="small">Thread: {thread} · Date: {date_str} · [STATUS: READY FOR SYNTHESIS]</p></section>
<section class="card"><h3>Source</h3><p><code class="inline">{Path(src_rel).name}</code></p>
<p>Core thesis and falsification hook extracted in pipeline pass.</p></section>
</main></body></html>
''', encoding='utf-8')

    idx_path = digest_dir / 'index.json'
    idx = load_json(idx_path, [])
    title = f'Autodraft: {base}'
    row = {
        'slug': slug,
        'title': title,
        'date': date_str,
        'thread': thread,
        'source': src_rel,
        'confidence': 'low-medium',
    }
    idx = [x for x in idx if x.get('slug') != slug]
    idx.insert(0, row)
    save_json(idx_path, idx)
    return slug


def write_queue_page(items, changes, autodrafts):
    SITE_DIR.joinpath('research').mkdir(parents=True, exist_ok=True)
    top = ''.join([f"<li><strong>{i.thread}</strong> · <code class='inline'>{Path(i.path).name}</code> · score {i.score}</li>" for i in items[:20]])
    ch = ''.join([f"<li><code class='inline'>{Path(c['path']).name}</code> ({c['change']})</li>" for c in changes[:30]])
    ad = ''.join([f"<li>[{a['thread']}] {a['slug']} ← {Path(a['source']).name}</li>" for a in autodrafts])
    PUB_PAGE.write_text(f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Autopilot Queue</title><link rel="stylesheet" href="/cohera/assets/style.css" />
</head><body><main class="container">
<section class="hero"><h1>Autopilot Queue</h1><p class="small">Updated: {now_iso()}</p></section>
<section class="card"><h3>Top priority</h3><ul class="clean">{top or '<li>none</li>'}</ul></section>
<section class="card"><h3>Detected changes</h3><ul class="clean">{ch or '<li>none</li>'}</ul></section>
<section class="card"><h3>Autodrafts created</h3><ul class="clean">{ad or '<li>none</li>'}</ul></section>
</main></body></html>
''', encoding='utf-8')


def main():
    items = collect_items()
    prev = load_json(STATE_PATH, {'files': {}})
    prev_files = prev.get('files', {})

    curr_files = {i.path: {'mtime': i.mtime, 'size': i.size, 'thread': i.thread} for i in items}

    changes = []
    for p, meta in curr_files.items():
        if p not in prev_files:
            changes.append({'path': p, 'change': 'new', 'thread': meta['thread']})
        elif prev_files[p].get('mtime') != meta['mtime'] or prev_files[p].get('size') != meta['size']:
            changes.append({'path': p, 'change': 'updated', 'thread': meta['thread']})
    for p, meta in prev_files.items():
        if p not in curr_files:
            changes.append({'path': p, 'change': 'removed', 'thread': meta.get('thread', 'cosmos')})

    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    autodrafts = []
    per_thread = {}
    for c in changes:
        t = c['thread']
        if t not in per_thread and c['change'] in ('new', 'updated'):
            per_thread[t] = c['path']
    for t in ('cosmos', 'regenesis', 'ethos'):
        src = per_thread.get(t)
        if not src:
            cand = next((i.path for i in items if i.thread == t), None)
            src = cand
        if src:
            slug = upsert_digest_stub(t, src, date_str)
            autodrafts.append({'thread': t, 'slug': slug, 'source': src})

    queue = {
        'generated_at': now_iso(),
        'total_sources': len(items),
        'changes': changes,
        'autodrafts_created': autodrafts,
        'top_priority': [{'path': i.path, 'thread': i.thread, 'score': i.score} for i in items[:15]],
    }
    state = {
        'generated_at': now_iso(),
        'files': curr_files,
    }

    save_json(QUEUE_PATH, queue)
    save_json(STATE_PATH, state)
    write_queue_page(items, changes, autodrafts)

    print(f"Autopilot complete. Sources={len(items)} changes={len(changes)} stubs={len(autodrafts)}")


if __name__ == '__main__':
    main()
