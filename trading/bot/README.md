# Cohera Trading Bot (Semi-Auto v1)

This is a **human-in-the-loop** trading stack:
- Signal engine (BTC playbook-style conditions)
- Risk engine (1% per trade + max loss guards)
- Approval gate (no auto-execution by default)
- Paper executor (default)

## Quick start

1. Copy config:
```bash
cp bot/config.example.json bot/config.json
```

2. Generate signal and pending order:
```bash
python3 bot/main.py
```

3. Review pending order:
```bash
cat bot/state/pending_order.json
```

4. Approve and execute (paper):
```bash
python3 bot/approve_order.py
```

## Modes
- `paper` (default): simulated execution only
- `semi_auto`: requires explicit approval for each order
- `live` exists as a placeholder but is intentionally blocked in v1

## Safety
- No withdrawals logic
- No live order placement in v1
- Hard risk caps enforced before order creation
