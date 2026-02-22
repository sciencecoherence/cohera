#!/usr/bin/env python3
import json
import requests
from pathlib import Path

from strategies import generate_signal

BASE = Path(__file__).resolve().parent
CFG_PATH = BASE / 'config.json'


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default


def fmt_bool(checks, key):
    return '✅' if key in checks else '❌'


def main():
    cfg = load_json(CFG_PATH, {})
    if not cfg:
        raise SystemExit('Missing bot/config.json')

    min_score = int(cfg.get('min_confluence_score', 5))
    rr_target = float(cfg.get('rr_target', 2.8))
    min_grade = str(cfg.get('min_grade', 'A')).upper()

    url = f"https://api.binance.com/api/v3/klines?symbol={cfg['symbol']}&interval={cfg['timeframe']}&limit=250"
    klines = requests.get(url, timeout=10).json()
    sig = generate_signal(klines, min_score=min_score, rr_target=rr_target, min_grade=min_grade)

    if sig.get('status') == 'SETUP':
        print('WHY_REPORT: SETUP_AVAILABLE')
        print(f"side={sig['side']} setup={sig['setup']} confidence={sig['confidence']} grade={sig.get('grade','n/a')}")
        print(f"entry={sig['entry']} stop={sig['stop']} tp1={sig['tp1']} rr={sig['rr']}")
        print(f"score={sig.get('score')}/{min_score} checks={', '.join(sig.get('checks', []))}")
        print(f"regime={sig.get('regime')} wyckoff={sig.get('wyckoff')}")
        return

    m = sig.get('market', {})
    checks = m.get('checks', [])
    regime = sig.get('regime', 'n/a')
    reason = sig.get('reason', 'no reason')

    print('WHY_REPORT: NO_TRADE')
    print(f"reason={reason}")
    print(f"regime={regime}")
    if 'last' in m:
        print(f"price={round(m.get('last',0),2)} ema50={round(m.get('ema50',0),2)} ema200={round(m.get('ema200',0),2)} atr_pct={m.get('atr_pct')}")

    # Human-readable confluence checklist
    print('checklist:')
    print(f"  {fmt_bool(checks, 'bullish_close') if regime=='uptrend' else fmt_bool(checks, 'bearish_close')} candle confirmation")
    print(f"  {fmt_bool(checks, 'momentum_up') if regime=='uptrend' else fmt_bool(checks, 'momentum_down')} momentum")
    print(f"  {fmt_bool(checks, 'entry_not_extended')} entry not extended")
    if regime == 'uptrend':
        print(f"  {fmt_bool(checks, 'liquidity_sweep_reclaim')} liquidity sweep reclaim")
        print(f"  {fmt_bool(checks, 'micro_breakout')} micro breakout")
    elif regime == 'downtrend':
        print(f"  {fmt_bool(checks, 'liquidity_sweep_reject')} liquidity sweep reject")
        print(f"  {fmt_bool(checks, 'micro_breakdown')} micro breakdown")


if __name__ == '__main__':
    main()
