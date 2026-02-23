#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/home/xavier/cohera-repo')
DELTA_PATH = REPO / 'chatgpt' / 'research_delta_latest.json'
BACKLOG_PATH = REPO / 'chatgpt' / 'research_backlog_run.json'
PUB_FINDINGS = REPO / 'site' / 'publications' / 'findings-latest.html'


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def main() -> int:
    delta = load_json(DELTA_PATH)
    backlog = load_json(BACKLOG_PATH)

    promoted = int(backlog.get('count', 0) or 0)
    autodrafts = int((delta.get('counts') or {}).get('autodrafts_created', 0) or 0)
    total_sources = int((delta.get('counts') or {}).get('total_sources', 0) or 0)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    synthesis_html = (
        '<section class="card" id="cohera-synthesis"><h3>Autonomous Cohera synthesis</h3>'
        '<p><strong>Theoretical integration:</strong> Current cycle indicates a stability phase with '
        f'<strong>{promoted}</strong> unfinished items promoted and <strong>{autodrafts}</strong> new autodraft vectors over '
        f'<strong>{total_sources}</strong> tracked sources. '
        'Interpretation: the research graph is consolidating; synthesis emphasis should prioritize '
        'cross-thread convergence over intake expansion in the next recursion window.</p>'
        f'<p class="small">Injected automatically at {now}.</p></section>'
    )

    html = PUB_FINDINGS.read_text(encoding='utf-8') if PUB_FINDINGS.exists() else ''

    if 'id="cohera-synthesis"' in html:
        html = re.sub(
            r'<section class="card" id="cohera-synthesis">.*?</section>',
            synthesis_html,
            html,
            flags=re.S,
        )
    elif '</main>' in html:
        html = html.replace('</main>', synthesis_html + '\n</main>')
    else:
        html += '\n' + synthesis_html + '\n'

    PUB_FINDINGS.write_text(html, encoding='utf-8')

    print(f'Promoted unfinished items: {promoted}')
    print(f'Autodrafts in delta: {autodrafts}')
    print(f'Updated: {PUB_FINDINGS}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
