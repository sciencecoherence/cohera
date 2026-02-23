#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

SESSIONS_DIR = Path('/home/xavier/.openclaw/agents/main/sessions')
STATE_PATH = Path('/home/xavier/cohera-repo/chatgpt/dashboard_mirror_state.json')
TARGET = '6170124243'
CHANNEL = 'telegram'
MAX_LEN = 900


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    return {'last_ts': None, 'seen': []}


def save_state(state):
    # keep seen small
    state['seen'] = state.get('seen', [])[-200:]
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')


def latest_session_file():
    files = list(SESSIONS_DIR.glob('*.jsonl'))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def parse_text(msg_obj):
    try:
        content = msg_obj.get('message', {}).get('content', [])
        texts = []
        for c in content:
            if c.get('type') == 'text' and c.get('text'):
                texts.append(c['text'])
        txt = '\n'.join(texts).strip()
        return txt
    except Exception:
        return ''


def send_telegram(text):
    subprocess.run([
        'openclaw', 'message', 'send',
        '--channel', CHANNEL,
        '--target', TARGET,
        '--message', text,
    ], check=False)


def main():
    state = load_state()
    last_ts = state.get('last_ts')
    seen = set(state.get('seen', []))

    session_file = latest_session_file()
    if not session_file:
        print('mirror: no session file')
        return

    # Bootstrap mode: on first run, set cursor to latest message without replaying history.
    if not last_ts:
        latest_ts = None
        with session_file.open(encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                if ev.get('type') == 'message':
                    t = ev.get('timestamp')
                    if t and (latest_ts is None or t > latest_ts):
                        latest_ts = t
        state['last_ts'] = latest_ts
        save_state(state)
        print(f'mirror: bootstrap cursor set to {latest_ts} ({session_file.name})')
        return

    new_msgs = []
    with session_file.open(encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get('type') != 'message':
                continue
            ts = ev.get('timestamp')
            role = ev.get('message', {}).get('role')
            if role not in ('user', 'assistant'):
                continue
            if last_ts and ts <= last_ts:
                continue
            text = parse_text(ev)
            if not text:
                continue
            # avoid noisy metadata wrappers
            if text.startswith('Conversation info (untrusted metadata):'):
                continue
            digest = hashlib.sha1((role + '|' + text[:300]).encode('utf-8')).hexdigest()
            if digest in seen:
                continue
            new_msgs.append((ts, role, text, digest))

    new_msgs.sort(key=lambda x: x[0])

    for ts, role, text, digest in new_msgs:
        prefix = 'Dashboard user' if role == 'user' else 'Dashboard assistant'
        body = text.replace('\n\n', '\n').strip()
        if len(body) > MAX_LEN:
            body = body[:MAX_LEN] + '…'
        send_telegram(f'[{prefix}] {body}')
        seen.add(digest)
        last_ts = ts

    state['last_ts'] = last_ts
    state['seen'] = list(seen)
    save_state(state)

    print(f'mirror: forwarded={len(new_msgs)} from={session_file.name}')


if __name__ == '__main__':
    main()
