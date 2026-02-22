#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
STATE = BASE / 'state'
OPEN = STATE / 'open_position.json'
EXIT = STATE / 'exit_order.json'


def fetch_current(symbol: str) -> float:
    r = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}', timeout=10)
    r.raise_for_status()
    return float(r.json()['price'])


if not OPEN.exists() or not EXIT.exists():
    print('NO_ARMED_EXIT')
    raise SystemExit(0)

pos = json.loads(OPEN.read_text(encoding='utf-8'))
ex = json.loads(EXIT.read_text(encoding='utf-8'))

cur = fetch_current(pos['symbol'])
side = pos['side']
target = float(ex['target'])
type_ = ex['type']
percent = ex.get('percent', 100)

if type_ == 'tp':
    hit = cur >= target if side == 'LONG' else cur <= target
else:  # sl
    hit = cur <= target if side == 'LONG' else cur >= target

if not hit:
    print('ARMED_EXIT_WAITING')
    print(json.dumps({'current': cur, 'target': target, 'type': type_, 'side': side, 'percent': percent}, indent=2))
    raise SystemExit(0)

# Execute at current market when triggered
res = subprocess.run([sys.executable, str(BASE / 'close_trade.py'), 'close', 'now', str(percent)], capture_output=True, text=True)
if res.returncode == 0:
    EXIT.unlink(missing_ok=True)
print(res.stdout.strip())
if res.stderr.strip():
    print(res.stderr.strip())
