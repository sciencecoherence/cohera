#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

REPLACEMENTS = [
    (r"\bIn conclusion,?\b", ""),
    (r"\bIt is important to note that\b", ""),
    (r"\bIt should be noted that\b", ""),
    (r"\bIn order to\b", "To"),
    (r"\bDue to the fact that\b", "Because"),
    (r"\bAt this point in time\b", "Now"),
    (r"\bThis manuscript presents\b", "This paper presents"),
    (r"\bThis manuscript provides\b", "This paper provides"),
    (r"\bpublication-ready synthesis\b", "research synthesis"),
    (r"\bdownstream readers\b", "readers"),
    (r"\bfor downstream readers\b", "for readers"),
    (r"\bexplicit falsification criteria\b", "testable falsification criteria"),
    (r"\boperational next steps\b", "next steps"),
    (r"\bkey findings \(auto-extracted\)\b", "key findings"),
    (r"\bAuto summary \(preview-based\)\b", "Summary"),
    (r"\bAuto-updated each recursive research cycle\.\b", "Updated each research cycle."),
    (r"\bNo active health blockers\b", "No active blockers"),
]

DOUBLE_SPACES = re.compile(r"[ \t]{2,}")
SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?])")
MULTI_BLANK = re.compile(r"\n{3,}")

SKIP_DIRS = {"assets", "node_modules", ".git", ".build"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & SKIP_DIRS) or path.name.endswith('.min.html')


def clean_text(text: str) -> str:
    out = text
    for pat, rep in REPLACEMENTS:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    out = DOUBLE_SPACES.sub(" ", out)
    out = SPACE_BEFORE_PUNCT.sub(r"\1", out)
    out = MULTI_BLANK.sub("\n\n", out)
    return out


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    new = clean_text(raw)
    if new != raw:
        path.write_text(new, encoding='utf-8')
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='/home/xavier/cohera-repo/site')
    args = ap.parse_args()

    root = Path(args.root)
    changed = 0
    scanned = 0
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {'.html', '.md'}:
            continue
        if should_skip(p):
            continue
        scanned += 1
        if process_file(p):
            changed += 1
            print(f'updated {p}')

    print(f'humanize_site: scanned={scanned} changed={changed}')


if __name__ == '__main__':
    main()
