#!/usr/bin/env python3
import json
from pathlib import Path
from executor import execute_paper

BASE = Path(__file__).resolve().parent
cfg_path = BASE / 'config.json'
pending_path = BASE / 'state' / 'pending_order.json'

if not cfg_path.exists() or not pending_path.exists():
    raise SystemExit('Missing config.json or pending_order.json')

cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
order = json.loads(pending_path.read_text(encoding='utf-8'))

if cfg.get('mode') == 'live':
    raise SystemExit('Live mode is intentionally blocked in v1. Use paper/semi_auto.')

rec = execute_paper(order, cfg.get('paper_slippage_bps', 3))
print('EXECUTED_PAPER')
print(json.dumps(rec, indent=2))
pending_path.unlink(missing_ok=True)
