#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
CHATGPT = REPO / 'chatgpt'
SITE = REPO / 'site'
QUEUE = CHATGPT / 'research_queue.json'
STATE = CHATGPT / 'research_state.json'
OUT = CHATGPT / 'research_health.json'

SLA_HOURS = 6


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def parse_iso_utc(s: str):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def newest_digest_mtime():
    mt = None
    for p in SITE.glob('*/digests/*.html'):
        if p.name == 'index.html':
            continue
        t = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        if mt is None or t > mt:
            mt = t
    return mt


def age_hours(dt: datetime, now: datetime):
    return (now - dt).total_seconds() / 3600.0


def main():
    now = datetime.now(timezone.utc)
    queue = load_json(QUEUE, {})
    state = load_json(STATE, {})

    issues = []

    q_ts = queue.get('generated_at')
    s_ts = state.get('generated_at')

    q_age = None
    s_age = None

    if q_ts:
        q_age = age_hours(parse_iso_utc(q_ts), now)
        if q_age > SLA_HOURS:
            issues.append(f'queue_stale>{SLA_HOURS}h')
    else:
        issues.append('queue_missing_generated_at')

    if s_ts:
        s_age = age_hours(parse_iso_utc(s_ts), now)
        if s_age > SLA_HOURS:
            issues.append(f'state_stale>{SLA_HOURS}h')
    else:
        issues.append('state_missing_generated_at')

    changes = queue.get('changes', [])
    if len(changes) > 0 and len(queue.get('autodrafts_created', [])) == 0:
        issues.append('changes_detected_but_no_autodrafts')

    digest_ts = newest_digest_mtime()
    digest_age = None
    if digest_ts:
        digest_age = age_hours(digest_ts, now)
        if digest_age > SLA_HOURS * 2:
            issues.append(f'digest_output_stale>{SLA_HOURS*2}h')
    else:
        issues.append('no_digest_outputs')

    status = 'ok' if not issues else 'degraded'

    report = {
        'generated_at': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'status': status,
        'sla_hours': SLA_HOURS,
        'queue_age_hours': round(q_age, 2) if q_age is not None else None,
        'state_age_hours': round(s_age, 2) if s_age is not None else None,
        'digest_age_hours': round(digest_age, 2) if digest_age is not None else None,
        'queue_changes_count': len(changes),
        'autodrafts_created_count': len(queue.get('autodrafts_created', [])),
        'issues': issues,
    }

    OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"health={status} issues={len(issues)}")


if __name__ == '__main__':
    main()
