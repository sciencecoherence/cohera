#!/usr/bin/env python3
import json, sys
from datetime import datetime, timezone
from pathlib import Path

k = Path(__file__).resolve().parent / 'state' / 'kill_switch.json'
cmd = (sys.argv[1] if len(sys.argv) > 1 else 'on').lower()

if cmd in ('on','enable'):
    k.write_text(json.dumps({'enabled': True, 'at': datetime.now(timezone.utc).isoformat()}, indent=2), encoding='utf-8')
    print('KILL_SWITCH_ON')
elif cmd in ('off','disable'):
    k.unlink(missing_ok=True)
    print('KILL_SWITCH_OFF')
else:
    print('USAGE: kill_switch.py [on|off]')
