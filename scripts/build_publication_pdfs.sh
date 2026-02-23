#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEX_DIR="$REPO_ROOT/site/publications/tex"
PDF_DIR="$REPO_ROOT/site/publications/pdf"
BUILD_DIR="$REPO_ROOT/.build/texpdf"

mkdir -p "$PDF_DIR" "$BUILD_DIR"
rm -f "$PDF_DIR"/*.pdf

# Build allowlisted + already-ready manuscripts so throughput keeps advancing.
mapfile -t BUILD_TEX < <(
python3 - <<'PY'
import json
from pathlib import Path
repo=Path("""$REPO_ROOT""")
tex_dir=repo/'site/publications/tex'
ready_path=repo/'chatgpt/publication_ready.json'
allow_path=repo/'chatgpt/publication_allowlist.json'
selected=[]
seen=set()

# 1) explicit allowlist targets (may not be ready yet)
allow=[]
if allow_path.exists():
    allow=json.loads(allow_path.read_text()).get('slugs',[])
for slug in allow:
    slug=(slug or '').lower()
    for p in sorted(tex_dir.glob('*.tex')):
        if slug in p.stem.lower() and p not in seen and 'auto-' not in p.name:
            selected.append(str(p)); seen.add(p)

# 2) already-ready items
if ready_path.exists():
    data=json.loads(ready_path.read_text())
    for row in data.get('ready', []):
        tex=row.get('tex')
        if tex:
            p=repo/tex
            if p.exists() and p.suffix=='.tex' and p not in seen:
                selected.append(str(p)); seen.add(p)

# 3) fallback: non-autodraft tex only
if not selected:
    for p in sorted(tex_dir.glob('*.tex')):
        if 'auto-' in p.name:
            continue
        selected.append(str(p))

for p in selected:
    print(p)
PY
)

for tex in "${BUILD_TEX[@]}"; do
  [ -f "$tex" ] || continue
  base="$(basename "$tex" .tex)"
  wrapper="$BUILD_DIR/${base}_wrapper.tex"

  cat > "$wrapper" <<EOF
\\documentclass[11pt]{article}
\\usepackage[a4paper,margin=1in]{geometry}
\\usepackage{fontspec}
\\setmainfont{TeX Gyre Pagella}
\\setsansfont{TeX Gyre Heros}
\\setmonofont{DejaVu Sans Mono}
\\usepackage{microtype}
\\usepackage{parskip}
\\usepackage{amsmath,amssymb,mathtools}
\\usepackage{physics}
\\usepackage{hyperref}
\\usepackage{xcolor}
\\usepackage{tcolorbox}
\\usepackage{enumitem}
\\hypersetup{colorlinks=true,linkcolor=blue!60!black,urlcolor=blue!60!black}

% Minimal macro set used by COSMOS drafts
\\newcommand{\\Substrate}{S}
\\newcommand{\\Proj}{\\Lambda}
\\newcommand{\\Emerg}{\\Omega}
\\newcommand{\\Integr}{\\Delta}
\\newcommand{\\Htot}{H_{\\mathrm{tot}}}
\\newcommand{\\Floquet}{\\mathcal{F}}

\\tcbset{colback=black!2!white,colframe=black!35,coltitle=black,fonttitle=\\bfseries,boxrule=0.6pt,arc=2mm,left=2mm,right=2mm,top=1.5mm,bottom=1.5mm}
\\newtcolorbox{FormalBox}[1]{title={Formal layer --- #1}}
\\newtcolorbox{MeaningBox}[1]{title={Interpretation --- #1}}
\\newtcolorbox{TestBox}[1]{title={Test hook --- #1}}
\\newtcolorbox{ChildBox}[1]{title={Child intuition --- #1}}

\\begin{document}
\\input{$tex}
\\end{document}
EOF

  latexmk -xelatex -interaction=nonstopmode -halt-on-error \
    -output-directory="$BUILD_DIR" "$wrapper"

  mv "$BUILD_DIR/${base}_wrapper.pdf" "$PDF_DIR/${base}.pdf"
done

python3 - <<'PY'
import json
from pathlib import Path

repo = Path('/home/xavier/cohera-repo')
pdf_dir = repo / 'site/publications/pdf'
pdf_dir.mkdir(parents=True, exist_ok=True)
ready_path = repo / 'chatgpt/publication_ready.json'

ready = []
if ready_path.exists():
    ready = json.loads(ready_path.read_text(encoding='utf-8')).get('ready', [])

cards = []
for r in ready:
    pdf_rel = r.get('pdf')
    if not pdf_rel:
        continue
    pdf_name = Path(pdf_rel).name
    canonical = pdf_name.replace('.pdf', '_publication-v1.pdf')
    chosen = canonical if (pdf_dir / canonical).exists() else pdf_name
    if not (pdf_dir / chosen).exists():
        continue
    cards.append({
        'title': r.get('title', chosen),
        'thread': r.get('thread', 'unknown'),
        'abstract': (r.get('abstract') or '').strip(),
        'pdf': chosen,
    })

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
    '    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/publications/tex/index.html">TeX Sources</a>',
    '  </nav></div></header>',
    '  <main class="container">',
    '    <section class="hero"><h1>PDF Publications</h1><p class="small">Final reader-ready papers only.</p></section>',
]

if cards:
    for c in cards:
        lines += [
            '    <section class="card">',
            f'      <h3>{c["title"]}</h3>',
            f'      <p class="small"><strong>Thread:</strong> {c["thread"]}</p>',
            f'      <p>{c["abstract"][:420] if c["abstract"] else "Publication-ready manuscript."}</p>',
            f'      <p><a href="/cohera/publications/pdf/{c["pdf"]}">Open PDF →</a></p>',
            '    </section>',
        ]
else:
    lines += ['    <section class="card"><p>No publication-ready PDFs available yet.</p></section>']

lines += ['  </main>', '</body>', '</html>']
(pdf_dir / 'index.html').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'pdf_index_cards={len(cards)}')
PY

echo "PDF build complete."