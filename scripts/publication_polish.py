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


def polish_tex(path: Path, slug: str, thread: str):
    raw = path.read_text(encoding='utf-8', errors='ignore')
    title = extract_title(raw, slug)
    body = clean_body(raw)

    # strip leading old title block to avoid duplication
    body = re.sub(r'^\s*%.*?\n', '', body, count=1)
    body = re.sub(r'^\s*\\section\*\{[^}]*\}\s*', '', body, count=1)

    # Convert Abstract subsection to proper abstract env
    body = body.replace('\\subsection*{Abstract}', '\\begin{abstract}')
    body = re.sub(r'\\subsection\*\{Keywords\}', r'\\end{abstract}\n\\paragraph{Keywords} ', body, count=1)

    header = f'''% Publication polished style\n\\title{{{title}}}\n\\author{{Cohera Lab}}\n\\date{{}}\n\\maketitle\n\\begin{{center}}\\small Thread: {thread.capitalize()}\\end{{center}}\n\n'''
    path.write_text(header + body + '\n', encoding='utf-8')


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
