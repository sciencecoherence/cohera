#!/usr/bin/env python3
import json
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
SCRIPT = REPO / 'scripts' / 'run_pipeline.sh'
STATE = REPO / 'chatgpt' / 'pipeline_manual_state.json'
DELTA = REPO / 'chatgpt' / 'research_delta_latest.json'
LOG = REPO / 'chatgpt' / 'run_pipeline.log'

lock = threading.Lock()
current_proc = None


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {"status": "IDLE", "lastRun": None, "lastExit": None}


def save_state(state):
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def start_pipeline():
    global current_proc
    with lock:
        st = load_state()
        if current_proc and current_proc.poll() is None:
            return False, st
        st['status'] = 'RUNNING'
        st['lastRun'] = now_iso()
        save_state(st)
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open('a', encoding='utf-8') as f:
            f.write(f"[{now_iso()}] manual trigger\n")
        current_proc = subprocess.Popen(['bash', str(SCRIPT)], stdout=LOG.open('a'), stderr=subprocess.STDOUT)
        return True, st


def refresh_status():
    global current_proc
    st = load_state()
    with lock:
        if current_proc and current_proc.poll() is None:
            st['status'] = 'RUNNING'
        elif current_proc:
            code = current_proc.poll()
            st['lastExit'] = code
            st['status'] = 'IDLE' if code == 0 else 'FAILED'
            current_proc = None
            save_state(st)
    return st


class Handler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._json({"ok": True}, 200)

    def do_GET(self):
        if self.path.startswith('/api/pipeline/status'):
            st = refresh_status()
            last_delta = None
            if DELTA.exists():
                try:
                    d = json.loads(DELTA.read_text(encoding='utf-8'))
                    last_delta = d.get('generated_at')
                except Exception:
                    pass
            st['lastDelta'] = last_delta
            return self._json(st)
        if self.path.startswith('/api/pipeline/log'):
            text = ''
            if LOG.exists():
                lines = LOG.read_text(encoding='utf-8', errors='ignore').splitlines()
                text = '\n'.join(lines[-120:])
            return self._json({"log": text})
        return self._json({"error": "not_found"}, 404)

    def do_POST(self):
        if self.path.startswith('/api/pipeline/run'):
            ok, st = start_pipeline()
            return self._json({"started": ok, "state": st})
        return self._json({"error": "not_found"}, 404)


def main():
    server = ThreadingHTTPServer(('0.0.0.0', 8099), Handler)
    print('pipeline_api_server listening on :8099')
    server.serve_forever()


if __name__ == '__main__':
    main()
