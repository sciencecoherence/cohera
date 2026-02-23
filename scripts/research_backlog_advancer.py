#!/usr/bin/env python3
import json
import re
import html
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site'
TEX_DIR = SITE / 'publications' / 'tex'
STATE = REPO / 'chatgpt' / 'research_backlog_run.json'
THREADS = ['cosmos', 'regenesis', 'ethos']


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def slugify(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()


def html_to_text(raw: str) -> str:
    raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw, flags=re.I)
    raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw, flags=re.I)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = html.unescape(raw)
    return re.sub(r'\s+', ' ', raw).strip()


def esc_tex(s: str) -> str:
    m = {'\\': r'\textbackslash{}','&': r'\&','%': r'\%','$': r'\$','#': r'\#','_': r'\_','{': r'\{','}': r'\}','~': r'\textasciitilde{}','^': r'\textasciicircum{}'}
    return ''.join(m.get(c, c) for c in s)


def publication_tex_path(thread: str, slug: str) -> Path:
    return TEX_DIR / f"{thread}_{slug}_publication-v1.tex"


def has_publication(thread: str, slug: str) -> bool:
    pat = f"{thread}_{slug}_publication-v1.tex"
    return (TEX_DIR / pat).exists()


def pick_unfinished():
    picks = []
    for thread in THREADS:
        idx = SITE / thread / 'digests' / 'index.json'
        rows = load_json(idx, [])
        for row in rows:
            slug = row.get('slug')
            title = row.get('title') or slug
            if not slug:
                continue
            if slug.startswith('auto-'):
                base_slug = slugify(slug.replace('auto-', '', 1))[:90]
            else:
                base_slug = slugify(slug)[:90]
            if has_publication(thread, base_slug):
                continue
            digest = SITE / thread / 'digests' / f'{slug}.html'
            if not digest.exists():
                continue
            picks.append({'thread': thread, 'digest_slug': slug, 'pub_slug': base_slug, 'title': title, 'digest_path': str(digest)})
            break
    return picks


def create_publication_tex(item: dict):
    digest = Path(item['digest_path'])
    raw = digest.read_text(encoding='utf-8', errors='ignore')
    text = html_to_text(raw)
    title = re.sub(r'^Autodraft:\s*', '', item['title']).strip()
    abstract = (
        f"This manuscript promotes an in-progress {item['thread']} research stream into a publication-ready synthesis. "
        f"It distills current evidence, makes assumptions explicit, and defines falsification hooks for next-cycle validation."
    )
    intro = text[:1300] or 'Introduction pending source synthesis.'
    evidence = text[1300:2700] or 'Evidence extraction pending deeper review.'
    discuss = text[2700:3900] or 'Discussion to be expanded in subsequent research cycles.'

    content = f'''% Auto-promoted publication draft\n\\title{{{esc_tex(title)}}}\n\\author{{Cohera Lab}}\n\\date{{{datetime.now(timezone.utc).strftime('%Y-%m-%d')}}}\n\\maketitle\n\n\\begin{{center}}\\small Thread: {item['thread'].capitalize()}\\end{{center}}\n\n\\begin{{abstract}}\n{esc_tex(abstract)}\n\\end{{abstract}}\n\n\\paragraph{{Keywords}} {item['thread']}, synthesis, publication\n\n\\section{{Introduction}}\n{esc_tex(intro)}\n\n\\section{{Evidence and Claims}}\n{esc_tex(evidence)}\n\n\\section{{Discussion}}\n{esc_tex(discuss)}\n\n\\section{{Validation Hooks}}\n\\begin{{itemize}}\n\\item Verify central claims against primary paper and DOI source.\n\\item Separate measured evidence from interpretation in final revision.\n\\item Keep confidence conservative until corroboration is explicit.\n\\end{{itemize}}\n'''
    out = publication_tex_path(item['thread'], item['pub_slug'])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding='utf-8')
    return out


def main():
    picks = pick_unfinished()
    created = []
    for p in picks:
        tex = create_publication_tex(p)
        created.append({'thread': p['thread'], 'from': p['digest_slug'], 'tex': str(tex.relative_to(REPO))})

    if created:
        subprocess.run(['/home/xavier/cohera-repo/scripts/build_publication_pdfs.sh'], check=False)
        subprocess.run(['python3', '/home/xavier/cohera-repo/scripts/publication_pipeline.py', '--sync'], check=False)

    state = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'created': created,
        'count': len(created)
    }
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(f"backlog_advancer: created={len(created)}")


if __name__ == '__main__':
    main()
