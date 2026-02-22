from typing import List, Dict


def ema(values: List[float], span: int) -> float:
    if not values:
        return 0.0
    a = 2 / (span + 1)
    e = values[0]
    for v in values[1:]:
        e = a * v + (1 - a) * e
    return e


def generate_signal(klines: List[list]) -> Dict:
    closes = [float(k[4]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]

    last = closes[-1]
    e50 = ema(closes[-120:], 50)
    e200 = ema(closes, 200)
    swing_low = min(lows[-20:])
    swing_high = max(highs[-20:])

    # Simple v1 logic (conservative)
    if last > e50 and e50 > e200:
        side = "LONG"
        entry = last
        stop = swing_low
        tp1 = entry + 2 * (entry - stop)
        confidence = "medium"
        setup = "Trend continuation / reclaim"
    elif last < e50 and e50 < e200:
        side = "SHORT"
        entry = last
        stop = swing_high
        tp1 = entry - 2 * (stop - entry)
        confidence = "medium"
        setup = "Breakdown retest bias"
    else:
        return {
            "status": "NO_TRADE",
            "reason": "No clean alignment (EMA50/EMA200/price)",
            "market": {"last": last, "ema50": e50, "ema200": e200, "swing_low": swing_low, "swing_high": swing_high}
        }

    rr = abs((tp1 - entry) / (entry - stop)) if (entry - stop) != 0 else 0
    return {
        "status": "SETUP",
        "side": side,
        "setup": setup,
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "tp1": round(tp1, 2),
        "rr": round(rr, 2),
        "confidence": confidence,
        "market": {"last": last, "ema50": e50, "ema200": e200, "swing_low": swing_low, "swing_high": swing_high}
    }
