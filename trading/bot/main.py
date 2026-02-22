#!/usr/bin/env python3
import json
import requests
from pathlib import Path
from risk import RiskConfig, position_size_usd, guards_ok
from strategies import generate_signal
from executor import save_pending

BASE = Path(__file__).resolve().parent
CFG_PATH = BASE / 'config.json'
STATE_PATH = BASE / 'state' / 'performance.json'


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default


def main():
    if not CFG_PATH.exists():
        raise SystemExit('Missing bot/config.json (copy from config.example.json)')

    cfg = load_json(CFG_PATH, {})
    perf = load_json(STATE_PATH, {"day_pnl_pct": 0.0, "week_pnl_pct": 0.0})

    kill = BASE / 'state' / 'kill_switch.json'
    if kill.exists():
        print('NO_TRADE: Kill switch active')
        return

    rcfg = RiskConfig(
        equity=cfg['account_equity_usd'],
        risk_per_trade=cfg['risk_per_trade'],
        max_daily_loss=cfg['max_daily_loss'],
        max_weekly_loss=cfg['max_weekly_loss'],
    )

    ok, msg = guards_ok(perf['day_pnl_pct'], perf['week_pnl_pct'], rcfg)
    if not ok:
        print(f'NO_TRADE: {msg}')
        return

    url = f"https://api.binance.com/api/v3/klines?symbol={cfg['symbol']}&interval={cfg['timeframe']}&limit=250"
    klines = requests.get(url, timeout=10).json()
    min_score = int(cfg.get('min_confluence_score', 4))
    rr_target = float(cfg.get('rr_target', 2.5))
    min_rr = float(cfg.get('min_rr', 2.5))

    sig = generate_signal(klines, min_score=min_score, rr_target=rr_target)

    if sig['status'] != 'SETUP' or sig.get('rr', 0) < min_rr:
        print('NO_TRADE:', sig.get('reason', f'RR below {min_rr} or no setup'))
        print(json.dumps({'debug': sig}, indent=2))
        return

    size_usd = position_size_usd(cfg['account_equity_usd'], cfg['risk_per_trade'], sig['entry'], sig['stop'])
    leverage = float(cfg.get('leverage', 1))
    margin_usd = round(size_usd / leverage, 2) if leverage > 0 else round(size_usd, 2)

    order = {
        "symbol": cfg['symbol'],
        "side": sig['side'],
        "setup": sig['setup'],
        "entry": sig['entry'],
        "stop": sig['stop'],
        "tp1": sig['tp1'],
        "rr": sig['rr'],
        "confidence": sig['confidence'],
        "size_usd": round(size_usd, 2),
        "leverage": leverage,
        "margin_usd": margin_usd,
        "mode": cfg['mode']
    }

    save_pending(order)
    print('PENDING_ORDER_CREATED')
    print(json.dumps(order, indent=2))


if __name__ == '__main__':
    main()
