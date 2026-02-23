#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
PIPE = REPO / 'chatgpt' / 'publication_pipeline.json'
PDF_DIR = REPO / 'site' / 'publications' / 'pdf'


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def pdf_count():
    return len([p for p in PDF_DIR.glob('*.pdf') if p.is_file()])


def main():
    data = load_json(PIPE, {'totals': {}})
    ready = int(data.get('totals', {}).get('ready_publications', 0) or 0)
    built = int(data.get('totals', {}).get('with_pdf', 0) or 0)
    files = pdf_count()

    # If we have built PDFs but zero ready publications, force a re-sync pass.
    if ready == 0 and (built > 0 or files > 0):
        subprocess.run(['python3', str(REPO / 'scripts' / 'publication_pipeline.py'), '--sync'], check=False)
        data = load_json(PIPE, {'totals': {}})
        ready2 = int(data.get('totals', {}).get('ready_publications', 0) or 0)
        print(f'publication_sanity_guard: repaired ready {ready} -> {ready2}')
    else:
        print(f'publication_sanity_guard: ok ready={ready} built={built} files={files}')


if __name__ == '__main__':
    main()
