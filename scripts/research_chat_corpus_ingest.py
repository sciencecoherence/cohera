#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
CHATS_DIR = REPO / 'chatgpt' / 'chats'
INBOX_DIR = REPO / 'chatgpt' / 'inbox'
STATE_PATH = REPO / 'chatgpt' / 'chat_corpus_state.json'
ORDER = ['genesis', 'newreality']


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def extract_messages(conv):
    mapping = conv.get('mapping', {})
    out = []
    for node in mapping.values():
        msg = (node or {}).get('message')
        if not msg:
            continue
        author = (msg.get('author') or {}).get('role')
        content = (msg.get('content') or {}).get('parts') or []
        text = '\n'.join([p for p in content if isinstance(p, str)]).strip()
        ts = msg.get('create_time')
        if author in ('user', 'assistant') and text:
            out.append({'role': author, 'text': text, 'ts': ts})
    out.sort(key=lambda x: x.get('ts') or 0)
    return out


def summarize(messages, max_items=20):
    # simple heuristic summary from user prompts and assistant key lines
    user_lines = [m['text'].replace('\n', ' ')[:180] for m in messages if m['role'] == 'user'][:max_items]
    asst_lines = [m['text'].replace('\n', ' ')[:220] for m in messages if m['role'] == 'assistant'][:max_items]
    return user_lines, asst_lines


def ingest_one(slug: str):
    src = CHATS_DIR / f'{slug}.json'
    if not src.exists():
        return None
    data = load_json(src, [])
    if not data:
        return None
    conv = data[0]
    msgs = extract_messages(conv)
    user_lines, asst_lines = summarize(msgs)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    out = INBOX_DIR / f'{datetime.now(timezone.utc).strftime("%Y-%m-%d")}-chat-corpus-{slug}.md'

    lines = []
    lines.append(f'# Chat Corpus Ingest: {slug.title()}')
    lines.append('')
    lines.append(f'- source: chatgpt/chats/{slug}.json')
    lines.append(f'- conversation_id: {conv.get("conversation_id") or conv.get("id")}')
    lines.append(f'- ingested_at: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}')
    lines.append(f'- messages_extracted: {len(msgs)}')
    lines.append('')
    lines.append('## User intent highlights')
    for u in user_lines[:12]:
        lines.append(f'- {u}')
    lines.append('')
    lines.append('## Assistant response highlights')
    for a in asst_lines[:12]:
        lines.append(f'- {a}')
    lines.append('')
    lines.append('## Next research actions')
    lines.append('- Convert strongest claims into falsifiable hypotheses.')
    lines.append('- Link equations to explicit assumptions and observables.')
    lines.append('- Promote mature segments into publication-ready manuscript sections only after validation.')

    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return {'slug': slug, 'out': str(out.relative_to(REPO)), 'messages': len(msgs)}


def main():
    state = load_json(STATE_PATH, {'completed': []})
    completed = set(state.get('completed', []))

    target = None
    for slug in ORDER:
        if slug not in completed:
            target = slug
            break

    if not target:
        print('chat_corpus_ingest: nothing pending')
        return

    result = ingest_one(target)
    if not result:
        print(f'chat_corpus_ingest: failed on {target}')
        return

    completed.add(target)
    state['completed'] = [s for s in ORDER if s in completed]
    state['last_run'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    state['last_result'] = result
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(f"chat_corpus_ingest: ingested={target} messages={result['messages']} -> {result['out']}")


if __name__ == '__main__':
    main()
