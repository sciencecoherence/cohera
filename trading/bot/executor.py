import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
STATE = BASE / 'state'
STATE.mkdir(parents=True, exist_ok=True)


def save_pending(order: dict):
    (STATE / 'pending_order.json').write_text(json.dumps(order, indent=2), encoding='utf-8')


def execute_paper(order: dict, slippage_bps: float = 3):
    slip = 1 + (slippage_bps / 10000.0) * (1 if order['side'] == 'LONG' else -1)
    fill = order['entry'] * slip
    rec = {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "paper",
        "symbol": order['symbol'],
        "side": order['side'],
        "entry_signal": order['entry'],
        "entry_fill": round(fill, 2),
        "stop": order['stop'],
        "tp1": order['tp1'],
        "size_usd": order['size_usd'],
        "setup": order['setup']
    }
    path = STATE / 'executions.log.jsonl'
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec) + '\n')

    # Keep a single current open paper position for manual close commands.
    open_pos = {
        "opened_at": rec["executed_at"],
        "symbol": rec["symbol"],
        "side": rec["side"],
        "entry_fill": rec["entry_fill"],
        "stop": rec["stop"],
        "tp1": rec["tp1"],
        "size_usd": rec["size_usd"],
        "setup": rec["setup"],
    }
    (STATE / 'open_position.json').write_text(json.dumps(open_pos, indent=2), encoding='utf-8')
    return rec
