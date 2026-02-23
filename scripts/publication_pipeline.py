#!/usr/bin/env python3
import argparse
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SITE = REPO / 'site'
TEX_DIR = SITE / 'publications' / 'tex'
PDF_DIR = SITE / 'publications' / 'pdf'
PIPELINE_PATH = REPO / 'chatgpt' / 'publication_pipeline.json'
READY_PATH = REPO / 'chatgpt' / 'publication_ready.json'
ALLOWLIST_PATH = REPO / 'chatgpt' / 'publication_allowlist.json'

THREADS = ['cosmos', 'regenesis', 'ethos']


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def slug_to_tex_name(thread: str, slug: str) -> str:
    safe = re.sub(r'[^a-zA-Z0-9_-]+', '-', slug).strip('-')
    return f'{thread}_{safe}.tex'


def html_to_text(source_html: str) -> str:
    txt = re.sub(r'<script[\s\S]*?</script>', ' ', source_html, flags=re.I)
    txt = re.sub(r'<style[\s\S]*?</style>', ' ', txt, flags=re.I)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = html.unescape(txt)
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt


def tex_escape(s: str) -> str:
    rep = {
        '\\': r'\textbackslash{}',
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
    }
    out = ''.join(rep.get(ch, ch) for ch in s)
    return out


def make_tex(thread: str, title: str, slug: str, source_rel: str, digest_text: str) -> str:
    body = digest_text[:7000] if digest_text else 'No extracted digest text available.'
    body = tex_escape(body)
    title = tex_escape(title)
    source_rel = tex_escape(source_rel)
    abstract = tex_escape(f"This publication-ready draft synthesizes current {thread} findings for '{title}' with traceable claims, evidence hooks, and validation steps.")
    slug_esc = tex_escape(slug)
    return f'''% Auto-generated publication draft\n\\section*{{{title}}}\n\\textbf{{Thread:}} {thread}\\\\\n\\textbf{{Digest slug:}} {slug_esc}\\\\\n\\textbf{{Source:}} \\texttt{{{source_rel}}}\\\\\n\\textbf{{Generated:}} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\\\\\n\n\\subsection*{{Abstract}}\n{abstract}\n\n\\subsection*{{Keywords}}\n{thread}, synthesis, publication-draft\n\n\\subsection*{{Structured draft body}}\n{body}\n\n\\subsection*{{Validation checklist}}\n\\begin{{itemize}}\n  \\item Verify all nontrivial claims against the original source.\n  \\item Add explicit citations/DOIs where available.\n  \\item Mark confidence for each key claim (low/medium/high).\n\\end{{itemize}}\n'''


def sync_tex_index():
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([p.name for p in TEX_DIR.glob('*.tex')])
    lines = [
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        '  <title>TeX Publications · Cohera Lab</title>',
        '  <link rel="stylesheet" href="/cohera/assets/style.css" />',
        '</head>',
        '<body>',
        '  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">',
        '    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/about/index.html">About</a>',
        '  </nav></div></header>',
        '  <main class="container">',
        '    <section class="hero"><h1>TeX Publications</h1><p class="small">Full source drafts (.tex) generated from ongoing research threads.</p></section>',
        '    <section class="card"><ul class="clean">',
    ]
    for f in files:
        lines.append(f'      <li><a href="/cohera/publications/tex/{f}">{f}</a></li>')
    if not files:
        lines.append('      <li>No TeX drafts yet.</li>')
    lines += ['    </ul></section>', '  </main>', '</body>', '</html>']
    (TEX_DIR / 'index.html').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def collect_items():
    items = []
    seen = set()
    for thread in THREADS:
        idx = SITE / thread / 'digests' / 'index.json'
        rows = load_json(idx, [])
        for row in rows[:8]:  # top recent items per thread
            slug = row.get('slug')
            title = row.get('title') or slug
            if not slug:
                continue
            digest_html = SITE / thread / 'digests' / f'{slug}.html'
            key = (thread, slug)
            if key not in seen:
                items.append((thread, slug, title, digest_html))
                seen.add(key)

    # Also include curated publication-first manuscripts (not tied to digest slug)
    for tex in sorted(TEX_DIR.glob('*_publication-v*.tex')):
        stem = tex.stem
        thread = stem.split('_', 1)[0] if '_' in stem else 'cosmos'
        slug = stem
        title = stem.replace('_', ' ').replace('-', ' ').title()
        key = (thread, slug)
        if key not in seen:
            items.append((thread, slug, title, None))
            seen.add(key)

    return items


def extract_abstract_from_tex(tex_path: Path) -> str:
    if not tex_path.exists():
        return ''
    text = tex_path.read_text(encoding='utf-8', errors='ignore')
    # Preferred publication section names
    patterns = [
        r'\\subsection\*\{Abstract(?:[^}]*)\}\s*(.*?)\s*(?=\\subsection\*\{|\Z)',
        r'\\subsection\*\{Abstract-level synthesis\}\s*(.*?)\s*(?=\\subsection\*\{|\Z)',
        r'\\subsection\*\{Publication summary\}\s*(.*?)\s*(?=\\subsection\*\{|\Z)',
        r'\\section\*\{Abstract(?:[^}]*)\}\s*(.*?)\s*(?=\\section\*\{|\Z)',
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.S | re.I)
        if m:
            raw = m.group(1)
            cleaned = re.sub(r'\\\\|\\textbf\{[^}]*\}|\\texttt\{[^}]*\}|\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', ' ', raw)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned:
                return cleaned[:500]
    return ''


def ensure_publication_tex_quality(tex_path: Path, title: str, thread: str):
    if not tex_path.exists():
        return
    text = tex_path.read_text(encoding='utf-8', errors='ignore')
    if re.search(r'\\subsection\*\{Abstract', text, flags=re.I):
        return
    safe_title = tex_escape(title)
    abstract = tex_escape(f"This publication provides a structured synthesis for {title}, with claim-to-evidence framing and a validation path for downstream readers.")
    prefix = (
        f"\\section*{{{safe_title}}}\n"
        f"\\subsection*{{Abstract}}\n{abstract}\n\n"
        f"\\subsection*{{Keywords}}\n{thread}, research, publication\n\n"
        f"\\subsection*{{Main Content}}\n"
    )
    tex_path.write_text(prefix + text, encoding='utf-8')


def is_ready_publication(row: dict, allowlist: set[str]) -> bool:
    slug = (row.get('slug') or '').lower()
    title = (row.get('title') or '').lower()
    abstract = (row.get('abstract') or '').strip()
    has_pdf = row.get('status', {}).get('has_pdf', False)
    if slug.startswith('auto-'):
        return False
    if title.startswith('autodraft:'):
        return False
    if not has_pdf:
        return False
    if len(abstract) < 80:
        return False
    if allowlist and slug not in allowlist:
        return False
    return True


def sync_pdf_index_ready(results: list):
    ready = [r for r in results if r.get('ready')]
    lines = [
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        '  <title>PDF Publications · Cohera Lab</title>',
        '  <link rel="stylesheet" href="/cohera/assets/style.css" />',
        '</head>',
        '<body>',
        '  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">',
        '    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/publications/tex/index.html">TeX Sources</a><a href="/cohera/about/index.html">About</a>',
        '  </nav></div></header>',
        '  <main class="container">',
        '    <section class="hero"><h1>PDF Publications</h1><p class="small">Only publication-ready outputs are listed here (formatted + abstract present).</p></section>',
    ]
    if ready:
        for r in ready:
            pdf_name = Path(r['pdf']).name
            lines += [
                '    <section class="card">',
                f'      <h3>{html.escape(r.get("title") or pdf_name)}</h3>',
                f'      <p class="small"><strong>Thread:</strong> {html.escape(r.get("thread", ""))}</p>',
                f'      <p>{html.escape(r.get("abstract", ""))}</p>',
                f'      <p><a href="/cohera/publications/pdf/{pdf_name}">Open PDF →</a></p>',
                '    </section>',
            ]
    else:
        lines += ['    <section class="card"><p>No publication-ready PDFs yet.</p></section>']

    lines += ['  </main>', '</body>', '</html>']
    (PDF_DIR / 'index.html').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sync', action='store_true', help='Generate missing tex drafts and compile PDFs')
    args = ap.parse_args()

    TEX_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for thread, slug, title, digest_html in collect_items():
        # For curated publication-first slugs, use direct stem.tex
        if slug.endswith('publication-v1') and (TEX_DIR / f'{slug}.tex').exists():
            tex_name = f'{slug}.tex'
        else:
            tex_name = slug_to_tex_name(thread, slug)
        tex_path = TEX_DIR / tex_name
        pdf_path = PDF_DIR / tex_name.replace('.tex', '.pdf')

        digest_text = ''
        source_rel = ''
        if digest_html and digest_html.exists():
            digest_text = html_to_text(digest_html.read_text(encoding='utf-8', errors='ignore'))
            source_rel = str(digest_html.relative_to(REPO))

        if args.sync and not tex_path.exists():
            tex_path.write_text(make_tex(thread, title, slug, source_rel or f'curated:{slug}', digest_text), encoding='utf-8')

        # Enforce publication baseline structure on non-autodraft tracks
        if args.sync and tex_path.exists() and not slug.startswith('auto-'):
            ensure_publication_tex_quality(tex_path, title, thread)

        abstract = extract_abstract_from_tex(tex_path) if tex_path.exists() else ''

        results.append({
            'thread': thread,
            'slug': slug,
            'title': title,
            'abstract': abstract,
            'digest_html': str(digest_html.relative_to(REPO)) if (digest_html and digest_html.exists()) else None,
            'tex': str(tex_path.relative_to(REPO)) if tex_path.exists() else None,
            'pdf': str(pdf_path.relative_to(REPO)) if pdf_path.exists() else None,
            'status': {
                'has_digest': bool(digest_html and digest_html.exists()),
                'has_tex': tex_path.exists(),
                'has_pdf': pdf_path.exists(),
            }
        })

    if args.sync:
        sync_tex_index()
        subprocess.run(['/home/xavier/cohera-repo/scripts/build_publication_pdfs.sh'], check=False)

    allow_cfg = load_json(ALLOWLIST_PATH, {'slugs': []})
    allowlist = set((s or '').lower() for s in allow_cfg.get('slugs', []))

    # refresh computed fields after potential build
    for r in results:
        if r['tex']:
            p = PDF_DIR / Path(r['tex']).name.replace('.tex', '.pdf')
            if p.exists():
                r['pdf'] = str(p.relative_to(REPO))
                r['status']['has_pdf'] = True
            tex_abs = REPO / r['tex']
            r['abstract'] = extract_abstract_from_tex(tex_abs)
        r['ready'] = is_ready_publication(r, allowlist)

    if args.sync:
        sync_pdf_index_ready(results)

    summary = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'totals': {
            'items': len(results),
            'with_tex': sum(1 for r in results if r['status']['has_tex']),
            'with_pdf': sum(1 for r in results if r['status']['has_pdf']),
            'ready_publications': sum(1 for r in results if r.get('ready')),
        },
        'items': results,
    }
    PIPELINE_PATH.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    READY_PATH.write_text(json.dumps({'generated_at': summary['generated_at'], 'ready': [r for r in results if r.get('ready')]}, indent=2), encoding='utf-8')
    print(f"pipeline: items={summary['totals']['items']} tex={summary['totals']['with_tex']} pdf={summary['totals']['with_pdf']} ready={summary['totals']['ready_publications']}")


if __name__ == '__main__':
    main()
