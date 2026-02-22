from typing import List, Dict


def ema(values: List[float], span: int) -> float:
    if not values:
        return 0.0
    a = 2 / (span + 1)
    e = values[0]
    for v in values[1:]:
        e = a * v + (1 - a) * e
    return e


def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    window = trs[-period:]
    return sum(window) / len(window) if window else 0.0


def generate_signal(klines: List[list]) -> Dict:
    closes = [float(k[4]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    opens = [float(k[1]) for k in klines]

    last = closes[-1]
    prev = closes[-2]
    e50 = ema(closes[-120:], 50)
    e200 = ema(closes, 200)
    a14 = atr(highs, lows, closes, 14)
    atr_pct = (a14 / last * 100) if last else 0

    swing_low = min(lows[-20:])
    swing_high = max(highs[-20:])

    # Multi-filter no-trade zones
    if atr_pct < 0.35:
        return {
            "status": "NO_TRADE",
            "reason": "Volatility too low (likely chop)",
            "market": {"last": last, "ema50": e50, "ema200": e200, "atr_pct": round(atr_pct, 3)}
        }

    score = 0
    checks = []

    if last > e50 and e50 > e200:
        side = "LONG"
        score += 1; checks.append("trend_alignment")
        if closes[-1] > opens[-1]:
            score += 1; checks.append("bullish_close")
        if last > prev:
            score += 1; checks.append("momentum_up")
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append("entry_not_extended")
        if last > max(highs[-6:-1]):
            score += 1; checks.append("micro_breakout")

        entry = last
        stop = min(lows[-8:])
        rr_target = 2.5
        tp1 = entry + rr_target * (entry - stop)
        setup = "V2 long confluence"
    elif last < e50 and e50 < e200:
        side = "SHORT"
        score += 1; checks.append("trend_alignment")
        if closes[-1] < opens[-1]:
            score += 1; checks.append("bearish_close")
        if last < prev:
            score += 1; checks.append("momentum_down")
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append("entry_not_extended")
        if last < min(lows[-6:-1]):
            score += 1; checks.append("micro_breakdown")

        entry = last
        stop = max(highs[-8:])
        rr_target = 2.5
        tp1 = entry - rr_target * (stop - entry)
        setup = "V2 short confluence"
    else:
        return {
            "status": "NO_TRADE",
            "reason": "No trend alignment (EMA50/EMA200/price)",
            "market": {"last": last, "ema50": e50, "ema200": e200, "atr_pct": round(atr_pct, 3)}
        }

    rr = abs((tp1 - entry) / (entry - stop)) if (entry - stop) != 0 else 0

    if score < 4:
        return {
            "status": "NO_TRADE",
            "reason": f"Confluence too weak ({score}/5)",
            "market": {
                "last": last,
                "ema50": e50,
                "ema200": e200,
                "atr_pct": round(atr_pct, 3),
                "score": score,
                "checks": checks,
            }
        }

    confidence = "high" if score >= 5 else "medium"

    return {
        "status": "SETUP",
        "side": side,
        "setup": setup,
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "tp1": round(tp1, 2),
        "rr": round(rr, 2),
        "confidence": confidence,
        "score": score,
        "checks": checks,
        "market": {
            "last": last,
            "ema50": e50,
            "ema200": e200,
            "atr_pct": round(atr_pct, 3),
            "swing_low": swing_low,
            "swing_high": swing_high,
        },
    }
