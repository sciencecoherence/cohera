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
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return default

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
        'counts': {
            'new': len(new_files),
            'updated': len(updated_files),
            'removed': len(removed_files),
            'autodrafts_created': len(autodrafts),
        },
        'thread_activity': threads,
        'autodrafts_created': autodrafts,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    # --- UPGRADED MARKDOWN GENERATOR ---
    lines = [
        '# SYSTEM WAKE: Research Delta Briefing',
        f'_Generated: {summary["generated_at"]} UTC_',
        '',
        '## Pipeline Status',
        f'- **New Raw Files:** {summary["counts"]["new"]}',
        f'- **Updated Files:** {summary["counts"]["updated"]}',
        f'- **Autodrafts Promoted (State 1):** {summary["counts"]["autodrafts_created"]}',
        ''
    ]

    if threads:
        lines.append('## Active Thread Concentrations')
        for k, v in sorted(threads.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(f'- **{k.upper()}**: {v} active modifiers')
        lines.append('')

    lines.append('## Cohera Action Directives')
    if autodrafts:
        lines.append('**Immediate Synthesis Required:**')
        lines.append('The following Autodrafts have been extracted and await Candidate promotion. Apply `AXIOMS.md` logic, formalize the math, and trigger the State 2 transition.')
        for a in autodrafts:
            lines.append(f"- `[{a.get('thread').upper()}]` target: {a.get('slug')} (Source: {a.get('source')})")
    elif new_files or updated_files:
        lines.append('No new Autodrafts generated. Review updated files for outstanding `[REQUIRES HUMAN REVIEW]` blocks or formatting anomalies.')
    else:
        lines.append('No active pipeline changes. Run systemic coherence checks on existing Candidates or optimize backend structures.')

    lines.append('')
    lines.append('***')
    lines.append('_End of brief. Acknowledge this delta and execute highest priority directive._')

    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    LAST.write_text(json.dumps({'queue_generated_at': q_ts, 'state_generated_at': s_ts}, indent=2), encoding='utf-8')

    print(f"Delta Briefing compiled: {len(new_files)} new, {len(autodrafts)} autodrafts injected to pipeline.")

if __name__ == '__main__':
    main()
