#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
CHATGPT = REPO / 'chatgpt'
INBOX = CHATGPT / 'inbox'
LOG = CHATGPT / 'ingest_log.jsonl'


def slugify(s: str):
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()[:80] or 'chat-note'


def main():
    parser = argparse.ArgumentParser(description='Ingest chat-provided research input into tracked inbox.')
    parser.add_argument('--thread', default='cosmos', choices=['cosmos', 'regenesis', 'ethos'])
    parser.add_argument('--title', default='chat-input')
    parser.add_argument('--text', required=True)
    parser.add_argument('--source', default='telegram')
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    ts = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    day = now.strftime('%Y-%m-%d')

    INBOX.mkdir(parents=True, exist_ok=True)

    filename = f"{day}-{slugify(args.title)}.md"
    out = INBOX / filename

    content = (
        f"# Chat Research Input\n\n"
        f"- ingested_at: {ts}\n"
        f"- thread: {args.thread}\n"
        f"- source: {args.source}\n"
        f"- title: {args.title}\n\n"
        f"## Content\n\n{args.text.strip()}\n"
    )
    out.write_text(content, encoding='utf-8')

    event = {
        'timestamp': ts,
        'type': 'chat_ingest',
        'thread': args.thread,
        'source': args.source,
        'title': args.title,
        'path': str(out.relative_to(REPO)),
        'bytes': out.stat().st_size,
    }
    with LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

    print(json.dumps(event))


if __name__ == '__main__':
    main()
