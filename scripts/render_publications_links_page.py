#!/usr/bin/env python3
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
PDF_DIR = REPO / 'site/publications/pdf'
PUB_INDEX = REPO / 'site/publications/index.html'
PDF_INDEX = REPO / 'site/publications/pdf/index.html'


def render(path: Path, pdfs):
    lines = [
        '<!doctype html>','<html lang="en">','<head>',
        '  <meta charset="utf-8" />','  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        '  <title>Publications · Cohera Lab</title>','  <link rel="stylesheet" href="/cohera/assets/style.css" />',
        '</head>','<body>',
        '  <header><div class="container nav"><strong>Cohera Lab</strong><nav class="nav-links">',
        '    <a href="/cohera/index.html">Home</a><a href="/cohera/research/index.html">Research</a><a href="/cohera/publications/index.html">Publications</a><a href="/cohera/status/index.html">Status</a>',
        '  </nav></div></header>','  <main class="container">',
        '    <section class="hero"><h1>Publications</h1></section>',
        '    <section class="card"><ul class="clean">'
    ]
    if pdfs:
        for n in pdfs:
            lines.append(f'      <li><a href="/cohera/publications/pdf/{n}">{n}</a></li>')
    else:
        lines.append('      <li>No papers published yet.</li>')
    lines += ['    </ul></section>','  </main>','</body>','</html>']
    path.write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([p.name for p in PDF_DIR.glob('*.pdf') if p.is_file()])
    render(PUB_INDEX, pdfs)
    render(PDF_INDEX, pdfs)
    print(f'publications_links_rendered={len(pdfs)}')


if __name__ == '__main__':
    main()
