#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from journal import append_trade

BASE = Path(__file__).resolve().parent
STATE = BASE / 'state'
OPEN = STATE / 'open_position.json'
HISTORY = STATE / 'closed_trades.jsonl'
CFG = BASE / 'config.json'

if not OPEN.exists():
    raise SystemExit('NO_OPEN_POSITION')

reason = (sys.argv[1] if len(sys.argv) > 1 else 'tp').lower()
if reason not in {'tp', 'sl', 'manual'}:
    raise SystemExit('USAGE: close_trade.py tp|sl|manual [exit_price]')

pos = json.loads(OPEN.read_text(encoding='utf-8'))

if reason == 'tp':
    exit_price = float(pos['tp1'])
elif reason == 'sl':
    exit_price = float(pos['stop'])
else:
    if len(sys.argv) < 3:
        raise SystemExit('USAGE: close_trade.py manual <exit_price>')
    exit_price = float(sys.argv[2])

entry = float(pos['entry_fill'])
stop = float(pos['stop'])
side = pos['side']

risk_per_unit = abs(entry - stop)
if risk_per_unit <= 0:
    r_mult = 0.0
else:
    if side == 'LONG':
        pnl_per_unit = exit_price - entry
    else:
        pnl_per_unit = entry - exit_price
    r_mult = pnl_per_unit / risk_per_unit

closed = {
    'closed_at': datetime.now(timezone.utc).isoformat(),
    'reason': reason,
    'symbol': pos['symbol'],
    'side': side,
    'entry_fill': entry,
    'exit_price': round(exit_price, 2),
    'stop': stop,
    'tp1': float(pos['tp1']),
    'size_usd': float(pos['size_usd']),
    'setup': pos.get('setup', ''),
    'result_r': round(r_mult, 2),
}

with HISTORY.open('a', encoding='utf-8') as f:
    f.write(json.dumps(closed) + '\n')

risk_pct = 0.01
if CFG.exists():
    try:
        cfg = json.loads(CFG.read_text(encoding='utf-8'))
        risk_pct = float(cfg.get('risk_per_trade', 0.01))
    except Exception:
        pass

append_trade({
    'date_time': closed['closed_at'],
    'pair': closed['symbol'],
    'setup': closed['setup'],
    'bias': 'n/a',
    'entry': closed['entry_fill'],
    'stop': closed['stop'],
    'tp1': closed['tp1'],
    'tp2': '',
    'risk_pct': risk_pct,
    'size': closed['size_usd'],
    'result_r': closed['result_r'],
    'confidence': 'n/a',
    'rule_break': '',
    'lesson': f"closed via {reason}",
})

OPEN.unlink(missing_ok=True)
print('TRADE_CLOSED')
print(json.dumps(closed, indent=2))
