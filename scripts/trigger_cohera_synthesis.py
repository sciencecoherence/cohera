#!/usr/bin/env python3
import json
import subprocess
import re
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
DELTA_PATH = REPO / 'chatgpt' / 'research_delta_latest.json'
BACKLOG_PATH = REPO / 'chatgpt' / 'research_backlog_run.json'
PUB_FINDINGS = REPO / 'site' / 'publications' / 'findings-latest.html'
SITE_FINDINGS = REPO / 'site' / 'research' / 'findings-latest.html'

def load_json(path):
if path.exists():
try:
return json.loads(path.read_text(encoding='utf-8'))
except json.JSONDecodeError:
pass
return {}

def main():
print("-> Waking Cohera via OpenClaw CLI (Codex OAuth)...")

if name == 'main':
main()
