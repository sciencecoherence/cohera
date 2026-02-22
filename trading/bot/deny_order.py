#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parent / 'state' / 'pending_order.json'
if not p.exists():
    print('NO_PENDING_ORDER')
else:
    p.unlink(missing_ok=True)
    print('PENDING_ORDER_DENIED')
