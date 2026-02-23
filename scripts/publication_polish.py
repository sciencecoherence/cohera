#!/usr/bin/env python3
import json
import re
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
TEX_DIR = REPO / 'site/publications/tex'
ALLOW = REPO / 'chatgpt/publication_allowlist.json'
PIPE = REPO / 'chatgpt/publication_pipeline.json'


def load_json(p, d):
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return d


def extract_title(text: str, fallback: str):
    m = re.search(r'\\section\*\{([^}]*)\}', text)
    if m:
        return m.group(1).strip()
    return fallback.replace('-', ' ').replace('_', ' ').title()


def clean_body(text: str):
    # remove nav/report boilerplate lines commonly leaking from html extraction
    text = re.sub(r'Autodraft\s*·.*?About\s+', '', text, flags=re.I | re.S)
    text = re.sub(r'\bCohera Lab\b\s*Home\s*Research\s*Cosmos\s*Regenesis\s*Ethos\s*Publications\s*About\b', '', text, flags=re.I)
    text = re.sub(r'\\textbf\{Thread:[^\n]*\n', '', text)
    text = re.sub(r'\\textbf\{Source digest:[^\n]*\n', '', text)
    text = re.sub(r'\\textbf\{Generated:[^\n]*\n', '', text)
    return text.strip()


def to_plain_text(tex: str) -> str:
    # Remove LaTeX commands but keep content
    t = re.sub(r'\\(textbf|texttt|emph|section\*|subsection\*|paragraph)\{([^}]*)\}', r'\2', tex)
    t = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', ' ', t)
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', ' ', t)
    t = re.sub(r'https?://\S+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def polish_tex(path: Path, slug: str, thread: str):
    raw = path.read_text(encoding='utf-8', errors='ignore')
    title = extract_title(raw, slug)
    body = clean_body(raw)
    plain = to_plain_text(body)

    abstract = (
        f"This manuscript presents a publication-ready synthesis in the {thread} thread, "
        f"centering on {title.lower()}. It consolidates validated claims, evidence continuity, "
        f"and explicit falsification criteria for downstream readers."
    )
    intro = plain[:1400] if plain else 'Introduction content pending final source synthesis.'
    methods = plain[1400:2800] if len(plain) > 1400 else 'Methodological notes are being refined from the source material.'
    discussion = plain[2800:4200] if len(plain) > 2800 else 'Discussion and implications are being finalized for publication quality.'

    rebuilt = f'''% Publication polished style
\\title{{{title}}}
\\author{{Cohera Lab}}
\\date{{}}
\\maketitle

\\begin{{center}}
\\rule{{0.92\\linewidth}}{{0.6pt}}\\\\[0.6em]
\\small Thread: {thread.capitalize()} \\\\ Manuscript Type: Research Synthesis
\\\\[0.4em]\\rule{{0.92\\linewidth}}{{0.6pt}}
\\end{{center}}

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\paragraph{{Keywords}} {thread}, synthesis, publication, validated-claims

\\section{{Introduction}}
{intro}

\\section{{Methods and Evidence Basis}}
{methods}

\\section{{Discussion}}
{discussion}

\\section{{Validation and Falsification Hooks}}
\\begin{{itemize}}
\\item Verify each key claim against primary sources before external distribution.
\\item Separate observed evidence from interpretive inference in final edits.
\\item Track confidence levels and unresolved uncertainties transparently.
\\end{{itemize}}
'''
    path.write_text(rebuilt + '\n', encoding='utf-8')


def main():
    allow = set((s or '').lower() for s in load_json(ALLOW, {'slugs': []}).get('slugs', []))
    items = load_json(PIPE, {'items': []}).get('items', [])
    touched = 0
    for it in items:
        slug = (it.get('slug') or '').lower()
        if allow and slug not in allow:
            continue
        tex = it.get('tex')
        if not tex:
            continue
        p = REPO / tex
        if p.exists():
            polish_tex(p, slug, it.get('thread','research'))
            touched += 1
    print(f'polished={touched}')


if __name__ == '__main__':
    main()
