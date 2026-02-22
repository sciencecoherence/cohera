#!/usr/bin/env python3
import json
from pathlib import Path

base = Path(__file__).resolve().parent
cfg = base / 'config.json'
pending = base / 'state' / 'pending_order.json'
perf = base / 'state' / 'performance.json'
exec_log = base / 'state' / 'executions.log.jsonl'
kill = base / 'state' / 'kill_switch.json'

if not cfg.exists():
    print('STATUS: NOT_CONFIGURED')
    raise SystemExit(0)

c = json.loads(cfg.read_text(encoding='utf-8'))
print('STATUS')
print(f"mode={c.get('mode')}")
print(f"symbol={c.get('symbol')}")
print(f"kill_switch={'ON' if kill.exists() else 'OFF'}")
print(f"pending_order={'YES' if pending.exists() else 'NO'}")
if perf.exists():
    p = json.loads(perf.read_text(encoding='utf-8'))
    print(f"day_pnl_pct={p.get('day_pnl_pct',0)} week_pnl_pct={p.get('week_pnl_pct',0)}")
if exec_log.exists():
    lines = exec_log.read_text(encoding='utf-8').strip().splitlines()
    print(f"executions={len([x for x in lines if x.strip()])}")
