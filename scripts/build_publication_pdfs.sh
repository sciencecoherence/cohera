#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEX_DIR="$REPO_ROOT/site/publications/tex"
PDF_DIR="$REPO_ROOT/site/publications/pdf"
BUILD_DIR="$REPO_ROOT/.build/texpdf"

mkdir -p "$PDF_DIR" "$BUILD_DIR"
rm -f "$PDF_DIR"/*.pdf

for tex in "$TEX_DIR"/*.tex; do
  [ -f "$tex" ] || continue
  base="$(basename "$tex" .tex)"
  wrapper="$BUILD_DIR/${base}_wrapper.tex"

  cat > "$wrapper" <<EOF
\\documentclass[11pt]{article}
\\usepackage[a4paper,margin=1in]{geometry}
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

  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -output-directory="$BUILD_DIR" "$wrapper"

  mv "$BUILD_DIR/${base}_wrapper.pdf" "$PDF_DIR/${base}.pdf"
done

cat > "$PDF_DIR/index.html" <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PDF Publications · Cohera Lab</title>
  <link rel="stylesheet" href="/cohera/assets/style.css" />
</head>
<body>
  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">
    <a href="/cohera/index.html">Home</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/publications/tex/index.html">TeX Sources</a>
  </nav></div></header>
  <main class="container">
    <section class="hero"><h1>PDF Publications</h1><p class="small">Auto-built from TeX sources.</p></section>
    <section class="card"><ul class="clean">
EOF

for pdf in "$PDF_DIR"/*.pdf; do
  [ -f "$pdf" ] || continue
  name="$(basename "$pdf")"
  echo "      <li><a href=\"/cohera/publications/pdf/$name\">$name</a></li>" >> "$PDF_DIR/index.html"
done

cat >> "$PDF_DIR/index.html" <<'EOF'
    </ul></section>
  </main>
</body>
</html>
EOF

echo "PDF build complete."