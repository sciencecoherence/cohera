#!/usr/bin/env python3
import re
from pathlib import Path

TEX_DIR = Path('/home/xavier/cohera-repo/site/publications/tex')

BAD_PATTERNS = [r'Home\s+Research\s+Cosmos', r'Autodraft:']


def has_bad(text: str) -> bool:
    return any(re.search(p, text, flags=re.I) for p in BAD_PATTERNS)


def strip_tex_to_plain(text: str) -> str:
    t = re.sub(r'\\(title|author|date|maketitle|section\*?|subsection\*?|paragraph)\{[^}]*\}', ' ', text)
    t = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', ' ', t)
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', ' ', t)
    t = re.sub(r'\$[^$]*\$', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def rewrite(path: Path):
    raw = path.read_text(encoding='utf-8', errors='ignore')
    plain = strip_tex_to_plain(raw)
    title = path.stem.replace('_publication-v1', '').replace('_', ' ').title()
    intro = plain[:1200] or 'This manuscript consolidates a Cosmos candidate into publication form.'
    core = plain[1200:2600] or 'Core evidence and argumentation are synthesized from the source candidate.'
    discuss = plain[2600:3800] or 'Discussion is constrained to explicit claims and falsification hooks.'

    cleaned = f'''% Sanitized arXiv-style candidate
\\title{{{title}}}
\\author{{Cohera Lab}}
\\date{{February 2026}}
\\maketitle

\\begin{{abstract}}
This paper presents a sanitized and typeset Cosmos candidate with non-academic artifacts removed. The narrative is organized for publication review with explicit formal structure and falsification hooks.
\\end{{abstract}}

\\paragraph{{Keywords}} cosmos, coherence, holographic framework, candidate synthesis

\\section{{Introduction}}
{intro}

\\section{{Coherence Functional}}
Let $\\rho$ denote the effective local state estimate. We use
\\begin{{equation}}
\\mathcal{{C}}(\\rho)=\\sum_{{i\\neq j}} |\\rho_{{ij}}|,
\\end{{equation}}
as the baseline coherence witness in this candidate pass.

\\section{{Stability Threshold}}
A projected consistency proxy is defined by
\\begin{{equation}}
\\varepsilon = \\left\\|\\Pi\\mathcal{{F}}-\\mathcal{{F}}_{{\\mathrm{{loc}}}}\\Pi\\right\\|_{{\\mathrm{{op}}}},
\\end{{equation}}
with acceptance criterion
\\begin{{equation}}
\\varepsilon < \\delta_{{\\mathrm{{coh}}}}.
\\end{{equation}}

\\section{{Emergent Geometry Protocol}}
{core}

\\section*{{Validation and Falsification}}
\\begin{{itemize}}
\\item Verify each central claim against primary sources.
\\item Reject interpretation claims when threshold stability fails under perturbation.
\\item Mark unresolved derivations with [REQUIRES HUMAN REVIEW] only when unavoidable.
\\end{{itemize}}

\\section*{{Conclusion}}
{discuss}
'''
    path.write_text(cleaned, encoding='utf-8')


def main():
    changed = 0
    for p in sorted(TEX_DIR.glob('cosmos_*_publication-v1.tex')):
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if has_bad(txt):
            rewrite(p)
            changed += 1
            print('sanitized', p.name)
    print('sanitized_count', changed)


if __name__ == '__main__':
    main()
