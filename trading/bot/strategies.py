from typing import List, Dict
from datetime import datetime, timezone


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


def classify_wyckoff_proxy(closes: List[float], highs: List[float], lows: List[float], vols: List[float]) -> str:
    # Lightweight phase proxy (not full Wyckoff engine)
    hh = max(highs[-20:])
    ll = min(lows[-20:])
    mid = (hh + ll) / 2
    last = closes[-1]
    vol_last = vols[-1]
    vol_avg = sum(vols[-20:]) / 20

    if last > mid and vol_last > vol_avg:
        return 'markup'
    if last < mid and vol_last > vol_avg:
        return 'markdown'
    if last > mid:
        return 'accumulation-like'
    return 'distribution-like'


def detect_liquidity_events(highs: List[float], lows: List[float], closes: List[float]) -> Dict:
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


def in_preferred_session(ts_ms: int) -> bool:
    # Prefer high-liquidity windows (rough proxy): 12:00-20:00 UTC
    h = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).hour
    return 12 <= h <= 20


def grade_from_score(score: int) -> str:
    if score >= 6:
        return 'A'
    if score >= 4:
        return 'B'
    return 'C'


def grade_rank(g: str) -> int:
    return {'A': 3, 'B': 2, 'C': 1}.get(g, 0)


def generate_signal(klines: List[list], min_score: int = 5, rr_target: float = 2.8, min_grade: str = 'A') -> Dict:
    closes = [float(k[4]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    opens = [float(k[1]) for k in klines]
    vols = [float(k[5]) for k in klines]
    last_ts = int(klines[-1][0])

    last = closes[-1]
    prev = closes[-2]
    e50 = ema(closes[-120:], 50)
    e200 = ema(closes, 200)
    a14 = atr(highs, lows, closes, 14)
    atr_pct = (a14 / last * 100) if last else 0
    regime = classify_regime(last, e50, e200, atr_pct)
    wyckoff = classify_wyckoff_proxy(closes, highs, lows, vols)
    liq = detect_liquidity_events(highs, lows, closes)

    if regime == 'compression':
        return {'status': 'NO_TRADE', 'reason': 'Volatility too low (compression)', 'regime': regime,
                'market': {'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3), 'wyckoff': wyckoff}}

    if regime == 'range':
        return {'status': 'NO_TRADE', 'reason': 'Range regime (skip)', 'regime': regime,
                'market': {'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3), 'wyckoff': wyckoff}}

    score = 0
    checks = []

    vol_last = vols[-1]
    vol_avg = sum(vols[-20:]) / 20
    spread_last = highs[-1] - lows[-1]
    spread_avg = sum((highs[i] - lows[i]) for i in range(-20, 0)) / 20

    # VSA-like effort/result proxy
    if vol_last > vol_avg and spread_last > spread_avg:
        score += 1; checks.append('vsa_effort_result')

    # Session filter bonus
    if in_preferred_session(last_ts):
        score += 1; checks.append('preferred_session')

    if regime == 'uptrend':
        side = 'LONG'
        setup = 'V2.2 long: trend + raid/reclaim + VSA'
        if closes[-1] > opens[-1]:
            score += 1; checks.append('bullish_close')
        if last > prev:
            score += 1; checks.append('momentum_up')
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append('entry_not_extended')
        if liq['sweep_low_reclaim']:
            score += 2; checks.append('liquidity_sweep_reclaim')
        if last > max(highs[-6:-1]):
            score += 1; checks.append('micro_breakout')
        if wyckoff in {'markup', 'accumulation-like'}:
            score += 1; checks.append('wyckoff_aligned')

        entry = last
        stop = min(lows[-10:])
        tp1 = entry + rr_target * (entry - stop)
    else:
        side = 'SHORT'
        setup = 'V2.2 short: trend + raid/reject + VSA'
        if closes[-1] < opens[-1]:
            score += 1; checks.append('bearish_close')
        if last < prev:
            score += 1; checks.append('momentum_down')
        if abs(last - e50) <= 1.2 * a14:
            score += 1; checks.append('entry_not_extended')
        if liq['sweep_high_reject']:
            score += 2; checks.append('liquidity_sweep_reject')
        if last < min(lows[-6:-1]):
            score += 1; checks.append('micro_breakdown')
        if wyckoff in {'markdown', 'distribution-like'}:
            score += 1; checks.append('wyckoff_aligned')

        entry = last
        stop = max(highs[-10:])
        tp1 = entry - rr_target * (stop - entry)

    rr = abs((tp1 - entry) / (entry - stop)) if (entry - stop) != 0 else 0
    grade = grade_from_score(score)

    if score < min_score:
        return {
            'status': 'NO_TRADE',
            'reason': f'Confluence too weak ({score}/{min_score})',
            'regime': regime,
            'grade': grade,
            'market': {
                'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3),
                'score': score, 'checks': checks, 'liq': liq, 'wyckoff': wyckoff,
            }
        }

    if grade_rank(grade) < grade_rank(min_grade):
        return {
            'status': 'NO_TRADE',
            'reason': f'Grade {grade} below required {min_grade}',
            'regime': regime,
            'grade': grade,
            'market': {
                'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3),
                'score': score, 'checks': checks, 'liq': liq, 'wyckoff': wyckoff,
            }
        }

    confidence = 'high' if grade == 'A' else 'medium'

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
        'grade': grade,
        'checks': checks,
        'regime': regime,
        'liq': liq,
        'wyckoff': wyckoff,
        'market': {'last': last, 'ema50': e50, 'ema200': e200, 'atr_pct': round(atr_pct, 3)},
    }
