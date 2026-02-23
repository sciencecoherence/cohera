#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
CHATGPT = REPO / 'chatgpt'
QUEUE = CHATGPT / 'research_queue.json'
STATE = CHATGPT / 'research_state.json'
LAST = CHATGPT / 'research_delta_last.json'
OUT_JSON = CHATGPT / 'research_delta_latest.json'
OUT_MD = CHATGPT / 'research_delta_latest.md'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def to_dt(s: str):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def main():
    now = datetime.now(timezone.utc)
    queue = load_json(QUEUE, {})
    state = load_json(STATE, {})
    prev = load_json(LAST, {'queue_generated_at': None, 'state_generated_at': None})

    q_ts = queue.get('generated_at')
    s_ts = state.get('generated_at')

    changes = queue.get('changes', [])
    new_files = [c for c in changes if c.get('change') == 'new']
    updated_files = [c for c in changes if c.get('change') == 'updated']
    removed_files = [c for c in changes if c.get('change') == 'removed']
    autodrafts = queue.get('autodrafts_created', [])

    threads = {}
    for c in new_files + updated_files:
        t = c.get('thread', 'unknown')
        threads[t] = threads.get(t, 0) + 1

    summary = {
        'generated_at': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'queue_generated_at': q_ts,
        'state_generated_at': s_ts,
        'since_previous': {
            'previous_queue_generated_at': prev.get('queue_generated_at'),
            'previous_state_generated_at': prev.get('state_generated_at'),
        },
        'counts': {
            'new': len(new_files),
            'updated': len(updated_files),
            'removed': len(removed_files),
            'autodrafts_created': len(autodrafts),
            'total_sources': queue.get('total_sources', 0),
        },
        'thread_activity': threads,
        'new_files': new_files[:50],
        'updated_files': updated_files[:50],
        'removed_files': removed_files[:50],
        'autodrafts_created': autodrafts,
        'top_priority': queue.get('top_priority', [])[:10],
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Research Delta Summary')
    lines.append('')
    lines.append(f"- Generated: {summary['generated_at']} UTC")
    lines.append(f"- Queue snapshot: {q_ts or 'missing'}")
    lines.append(f"- State snapshot: {s_ts or 'missing'}")
    lines.append('')
    lines.append('## Counts')
    for k, v in summary['counts'].items():
        lines.append(f'- {k}: {v}')
    lines.append('')
    lines.append('## Thread activity')
    if threads:
        for k, v in sorted(threads.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(f'- {k}: {v}')
    else:
        lines.append('- none')
    lines.append('')
    lines.append('## Autodrafts created')
    if autodrafts:
        for a in autodrafts:
            lines.append(f"- [{a.get('thread')}] {a.get('slug')} ← {a.get('source')}")
    else:
        lines.append('- none')

    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    LAST.write_text(json.dumps({'queue_generated_at': q_ts, 'state_generated_at': s_ts}, indent=2), encoding='utf-8')

    print(f"delta: new={len(new_files)} updated={len(updated_files)} removed={len(removed_files)} autodrafts={len(autodrafts)}")


if __name__ == '__main__':
    main()
