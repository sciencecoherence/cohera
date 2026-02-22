#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from journal import append_trade

BASE = Path(__file__).resolve().parent
STATE = BASE / 'state'
OPEN = STATE / 'open_position.json'
HISTORY = STATE / 'closed_trades.jsonl'
CFG = BASE / 'config.json'
EXIT_ORDER = STATE / 'exit_order.json'


def usage():
    raise SystemExit(
        'USAGE:\n'
        '  close_trade.py tp [percent]           # arm TP (executes only when hit)\n'
        '  close_trade.py sl [percent]           # arm SL (executes only when hit)\n'
        '  close_trade.py close now [percent]    # immediate close at market\n'
        '  close_trade.py close <price> [percent]\n'
    )


def parse_percent(arg: str | None) -> float:
    if arg is None:
        return 100.0
    p = float(arg)
    if p <= 0 or p > 100:
        raise SystemExit('percent must be >0 and <=100')
    return p


def fetch_current_price(symbol: str) -> float:
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return float(r.json()['price'])


def execute_close(pos: dict, reason: str, exit_price: float, percent: float):
    entry = float(pos['entry_fill'])
    stop = float(pos['stop'])
    side = pos['side']
    size_usd = float(pos['size_usd'])
    close_size_usd = round(size_usd * (percent / 100.0), 2)
    remaining_size_usd = round(size_usd - close_size_usd, 2)

    risk_per_unit = abs(entry - stop)
    if risk_per_unit <= 0:
        r_mult = 0.0
    else:
        pnl_per_unit = (exit_price - entry) if side == 'LONG' else (entry - exit_price)
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
        'size_usd_closed': close_size_usd,
        'size_usd_before': size_usd,
        'size_usd_after': remaining_size_usd,
        'percent_closed': percent,
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
        'size': close_size_usd,
        'result_r': closed['result_r'],
        'confidence': 'n/a',
        'rule_break': '',
        'lesson': f"closed {percent}% via {reason}",
    })

    if remaining_size_usd <= 0.0:
        OPEN.unlink(missing_ok=True)
        EXIT_ORDER.unlink(missing_ok=True)
        status = 'POSITION_FULLY_CLOSED'
    else:
        pos['size_usd'] = remaining_size_usd
        pos['last_partial_close_at'] = closed['closed_at']
        pos['last_partial_percent'] = percent
        OPEN.write_text(json.dumps(pos, indent=2), encoding='utf-8')
        status = 'POSITION_PARTIALLY_CLOSED'

    print(status)
    print(json.dumps(closed, indent=2))


if not OPEN.exists():
    raise SystemExit('NO_OPEN_POSITION')

args = sys.argv[1:]
if not args:
    usage()

cmd = args[0].lower()
pos = json.loads(OPEN.read_text(encoding='utf-8'))
symbol = pos['symbol']
side = pos['side']

if cmd in {'tp', 'sl'}:
    percent = parse_percent(args[1] if len(args) > 1 else None)
    target = float(pos['tp1'] if cmd == 'tp' else pos['stop'])
    current = fetch_current_price(symbol)

    # Trigger conditions by side
    if cmd == 'tp':
        hit = current >= target if side == 'LONG' else current <= target
    else:  # sl
        hit = current <= target if side == 'LONG' else current >= target

    if hit:
        execute_close(pos, cmd, current, percent)
    else:
        armed = {
            'armed_at': datetime.now(timezone.utc).isoformat(),
            'symbol': symbol,
            'side': side,
            'type': cmd,
            'target': target,
            'percent': percent,
            'note': 'Will execute when target is hit. Use monitor script or run command again later.'
        }
        EXIT_ORDER.write_text(json.dumps(armed, indent=2), encoding='utf-8')
        print('ARMED_EXIT_ORDER')
        print(json.dumps(armed, indent=2))
elif cmd == 'close':
    if len(args) < 2:
        usage()
    if args[1].lower() == 'now':
        exit_price = fetch_current_price(symbol)
        percent = parse_percent(args[2] if len(args) > 2 else None)
    else:
        exit_price = float(args[1])
        percent = parse_percent(args[2] if len(args) > 2 else None)
    execute_close(pos, 'manual', exit_price, percent)
else:
    usage()
