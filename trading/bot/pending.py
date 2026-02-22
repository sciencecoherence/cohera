#!/usr/bin/env python3
import json
from pathlib import Path

p = Path(__file__).resolve().parent / 'state' / 'pending_order.json'
if not p.exists():
    print('NO_PENDING_ORDER')
    raise SystemExit(0)

print('PENDING_ORDER')
print(json.dumps(json.loads(p.read_text(encoding='utf-8')), indent=2))
