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


def classify_regime(last: float, e50: float, e200: float, atr_pct: float) -> str:
    if atr_pct < 0.35:
        return 'compression'
    if last > e50 > e200:
        return 'uptrend'
    if last < e50 < e200:
        return 'downtrend'
    return 'range'


def detect_liquidity_events(highs: List[float], lows: List[float], closes: List[float]) -> Dict:
    # Simple proxy for sweep/reclaim and sweep/reject behavior.
    prev_low = min(lows[-8:-1])
    prev_high = max(highs[-8:-1])
    last_low = lows[-1]
    last_high = highs[-1]
    last_close = closes[-1]

    sweep_low_reclaim = last_low < prev_low and last_close > prev_low
    sweep_high_reject = last_high > prev_high and last_close < prev_high

    return {
        'prev_low': prev_low,
        'prev_high': prev_high,
        'sweep_low_reclaim': sweep_low_reclaim,
        'sweep_high_reject': sweep_high_reject,
    }


def generate_signal(klines: List[list], min_score: int = 4, rr_target: float = 2.5) -> Dict:
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

    regime = classify_regime(last, e50, e200, atr_pct)
    liq = detect_liquidity_events(highs, lows, closes)

    if regime == 'compression':
        return {
            'status': 'NO_TRADE',
            'reason': 'Volatility too low (compression)',
            'regime': regime,
            'market': {'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3)}
        }

    score = 0
    checks = []

    if regime == 'uptrend':
        side = 'LONG'
        setup = 'V2.1 long: trend + reclaim'
        if closes[-1] > opens[-1]:
            score += 1; checks.append('bullish_close')
        if last > prev:
            score += 1; checks.append('momentum_up')
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append('entry_not_extended')
        if liq['sweep_low_reclaim']:
            score += 1; checks.append('liquidity_sweep_reclaim')
        if last > max(highs[-6:-1]):
            score += 1; checks.append('micro_breakout')

        entry = last
        stop = min(lows[-10:])
        tp1 = entry + rr_target * (entry - stop)

    elif regime == 'downtrend':
        side = 'SHORT'
        setup = 'V2.1 short: trend + reject'
        if closes[-1] < opens[-1]:
            score += 1; checks.append('bearish_close')
        if last < prev:
            score += 1; checks.append('momentum_down')
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append('entry_not_extended')
        if liq['sweep_high_reject']:
            score += 1; checks.append('liquidity_sweep_reject')
        if last < min(lows[-6:-1]):
            score += 1; checks.append('micro_breakdown')

        entry = last
        stop = max(highs[-10:])
        tp1 = entry - rr_target * (stop - entry)
    else:
        return {
            'status': 'NO_TRADE',
            'reason': 'Range regime (skip)',
            'regime': regime,
            'market': {'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3)}
        }

    rr = abs((tp1 - entry) / (entry - stop)) if (entry - stop) != 0 else 0

    if score < min_score:
        return {
            'status': 'NO_TRADE',
            'reason': f'Confluence too weak ({score}/{min_score})',
            'regime': regime,
            'market': {
                'last': last,
                'ema50': e50,
                'ema200': e200,
                'atr_pct': round(atr_pct, 3),
                'score': score,
                'checks': checks,
                'liq': liq,
            }
        }

    confidence = 'high' if score >= min_score + 1 else 'medium'

    return {
        'status': 'SETUP',
        'side': side,
        'setup': setup,
        'entry': round(entry, 2),
        'stop': round(stop, 2),
        'tp1': round(tp1, 2),
        'rr': round(rr, 2),
        'confidence': confidence,
        'score': score,
        'checks': checks,
        'regime': regime,
        'liq': liq,
        'market': {
            'last': last,
            'ema50': e50,
            'ema200': e200,
            'atr_pct': round(atr_pct, 3),
        },
    }
