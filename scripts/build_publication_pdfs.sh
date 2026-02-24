#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export REPO_ROOT

TEX_DIR="$REPO_ROOT/site/publications/tex"
PDF_DIR="$REPO_ROOT/site/publications/pdf"
BUILD_DIR="$REPO_ROOT/.build/texpdf"

mkdir -p "$PDF_DIR" "$BUILD_DIR"
rm -f "$PDF_DIR"/*.pdf

mapfile -t BUILD_TEX < <(
python3 - <<'PY'
import json, os
from pathlib import Path
repo = Path(os.environ['REPO_ROOT'])
tex_dir = repo / 'site/publications/tex'
ready_path = repo / 'chatgpt/publication_ready.json'
allow_path = repo / 'chatgpt/publication_allowlist.json'
selected, seen = [], set()

allow = []
if allow_path.exists():
    allow = json.loads(allow_path.read_text(encoding='utf-8')).get('slugs', [])
for slug in allow:
    slug = (slug or '').lower()
    for p in sorted(tex_dir.glob('*.tex')):
        stem = p.stem.lower()
        if 'chat-corpus' in stem:
            continue
        if slug in stem and 'auto-' not in p.name and p not in seen:
            selected.append(str(p)); seen.add(p)

if ready_path.exists():
    data = json.loads(ready_path.read_text(encoding='utf-8'))
    for row in data.get('ready', []):
        tex = row.get('tex')
        if tex:
            p = repo / tex
            if p.exists() and p.suffix == '.tex' and p not in seen:
                if 'chat-corpus' in p.stem.lower():
                    continue
                selected.append(str(p)); seen.add(p)

if not selected:
    for p in sorted(tex_dir.glob('*.tex')):
        stem = p.stem.lower()
        if 'auto-' in p.name or 'chat-corpus' in stem:
            continue
        selected.append(str(p))

for p in selected:
    print(p)
PY
)

FAILED_BUILDS=()
for tex in "${BUILD_TEX[@]:-}"; do
  [ -f "$tex" ] || continue
  base="$(basename "$tex" .tex)"
  wrapper="$BUILD_DIR/${base}_wrapper.tex"

  cat > "$wrapper" <<EOF
\documentclass[11pt]{article}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\setsansfont{TeX Gyre Heros}
\setmonofont{DejaVu Sans Mono}
\usepackage{microtype}
\usepackage{parskip}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{physics}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{enumitem}
\hypersetup{colorlinks=true,linkcolor=blue!60!black,urlcolor=blue!60!black}
\newcommand{\Substrate}{S}
\newcommand{\Proj}{\Lambda}
\newcommand{\Emerg}{\Omega}
\newcommand{\Integr}{\Delta}
\newcommand{\Htot}{H_{\mathrm{tot}}}
\newcommand{\Floquet}{\mathcal{F}}
\tcbset{colback=black!2!white,colframe=black!35,coltitle=black,fonttitle=\bfseries,boxrule=0.6pt,arc=2mm,left=2mm,right=2mm,top=1.5mm,bottom=1.5mm}
\newtcolorbox{FormalBox}[1]{title={Formal layer --- #1}}
\newtcolorbox{MeaningBox}[1]{title={Interpretation --- #1}}
\newtcolorbox{TestBox}[1]{title={Test hook --- #1}}
\newtcolorbox{ChildBox}[1]{title={Child intuition --- #1}}
\begin{document}
\input{$tex}
\end{document}
EOF

  if latexmk -xelatex -interaction=nonstopmode -halt-on-error -output-directory="$BUILD_DIR" "$wrapper"; then
    mv "$BUILD_DIR/${base}_wrapper.pdf" "$PDF_DIR/${base}.pdf"
  else
    echo "WARN: build failed for $base" >&2
    FAILED_BUILDS+=("$base")
    continue
  fi
done

# SIMPLE INDEX: links only (as requested)
python3 - <<'PY'
import os
from pathlib import Path
repo = Path(os.environ['REPO_ROOT'])
pdf_dir = repo / 'site/publications/pdf'
pdf_dir.mkdir(parents=True, exist_ok=True)
pdfs = sorted([p.name for p in pdf_dir.glob('*.pdf') if p.is_file()])

lines = [
'<!doctype html>','<html lang="en">','<head>',
'  <meta charset="utf-8" />','  <meta name="viewport" content="width=device-width, initial-scale=1" />',
'  <title>PDF Publications · Cohera Lab</title>','  <link rel="stylesheet" href="/cohera/assets/style.css" />','</head>','<body>',
'  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">',
'    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/status/index.html">Status</a>',
'  </nav></div></header>','  <main class="container">',
'    <section class="hero"><h1>PDF Publications</h1></section>',
'    <section class="card"><ul class="clean">'
]
if pdfs:
    for n in pdfs:
        lines.append(f'      <li><a href="/cohera/publications/pdf/{n}">{n}</a></li>')
else:
    lines.append('      <li>No PDFs published yet.</li>')
lines += ['    </ul></section>','  </main>','</body>','</html>']
(pdf_dir/'index.html').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(f'pdf_index_links={len(pdfs)}')
PY

if [ ${#FAILED_BUILDS[@]} -gt 0 ]; then
  echo "PDF build completed with skips. Failed targets: ${FAILED_BUILDS[*]}"
else
  echo "PDF build complete."
fi
