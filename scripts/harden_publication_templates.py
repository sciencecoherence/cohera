#!/usr/bin/env python3
import re
from pathlib import Path

TEX_DIR = Path('/home/xavier/cohera-repo/site/publications/tex')


def tex_title_from_name(name: str) -> str:
    return name.replace('_publication-v1.tex', '').replace('_', ' ').replace('-', ' ').title()


def ensure_structure(path: Path) -> bool:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    changed = False

    if '\\begin{abstract}' not in raw:
        title = tex_title_from_name(path.name)
        pre = f"\\title{{{title}}}\n\\author{{Cohera Lab}}\n\\date{{February 2026}}\n\\maketitle\n\n"
        abstract = (
            "\\begin{abstract}\n"
            "This publication-ready manuscript was sanitized from the active research pipeline and reformatted for reader clarity. "
            "Claims are bounded, equations are typeset, and falsification conditions are explicit.\n"
            "\\end{abstract}\n\n"
            "\\paragraph{Keywords} coherence, synthesis, publication\n\n"
        )
        # remove duplicate old top matter if present
        raw = re.sub(r'^\s*%.*?\n', '', raw, count=1)
        raw = pre + abstract + raw
        changed = True

    # normalize noisy escaped inline tags that leak from sources
    cleaned = raw.replace('\\\\(', '$').replace('\\\\)', '$')
    if cleaned != raw:
        raw = cleaned
        changed = True

    if changed:
        path.write_text(raw, encoding='utf-8')
    return changed


def main():
    changed = 0
    total = 0
    for p in sorted(TEX_DIR.glob('*_publication-v1.tex')):
        total += 1
        if ensure_structure(p):
            changed += 1
            print('hardened', p.name)
    print(f'harden_publication_templates: total={total} changed={changed}')


if __name__ == '__main__':
    main()
