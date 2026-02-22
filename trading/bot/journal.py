import csv
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
STATE = BASE / 'state'
REPO = BASE.parent.parent
JOURNAL_DIR = REPO / 'site' / 'trading' / 'journal'
TRADES_CSV = JOURNAL_DIR / 'trades.csv'
METRICS_JSON = JOURNAL_DIR / 'metrics.json'


def _load_metrics():
    if METRICS_JSON.exists():
        return json.loads(METRICS_JSON.read_text(encoding='utf-8'))
    return {
        "total_trades": 0,
        "win_rate": 0,
        "avg_win_r": 0,
        "avg_loss_r": 0,
        "expectancy_r": 0,
        "updated_at": None,
    }


def _ensure_csv_header():
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    if not TRADES_CSV.exists():
        TRADES_CSV.write_text(
            "date_time,pair,setup,bias,entry,stop,tp1,tp2,risk_pct,size,result_r,confidence,rule_break,lesson\n",
            encoding='utf-8'
        )


def append_trade(trade: dict):
    _ensure_csv_header()
    metrics = _load_metrics()

    with TRADES_CSV.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            trade.get('date_time', ''),
            trade.get('pair', ''),
            trade.get('setup', ''),
            trade.get('bias', ''),
            trade.get('entry', ''),
            trade.get('stop', ''),
            trade.get('tp1', ''),
            trade.get('tp2', ''),
            trade.get('risk_pct', ''),
            trade.get('size', ''),
            trade.get('result_r', ''),
            trade.get('confidence', ''),
            trade.get('rule_break', ''),
            trade.get('lesson', ''),
        ])

    # Recompute metrics from CSV (small + reliable)
    rows = []
    with TRADES_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                rr = float(r.get('result_r', ''))
                rows.append(rr)
            except Exception:
                pass

    total = len(rows)
    wins = [x for x in rows if x > 0]
    losses = [x for x in rows if x < 0]

    metrics['total_trades'] = total
    metrics['win_rate'] = round((len(wins) / total) * 100, 2) if total else 0
    metrics['avg_win_r'] = round(sum(wins) / len(wins), 2) if wins else 0
    metrics['avg_loss_r'] = round(sum(losses) / len(losses), 2) if losses else 0
    metrics['expectancy_r'] = round(sum(rows) / total, 2) if total else 0
    metrics['updated_at'] = datetime.now(timezone.utc).isoformat()

    METRICS_JSON.write_text(json.dumps(metrics, indent=2), encoding='utf-8')
