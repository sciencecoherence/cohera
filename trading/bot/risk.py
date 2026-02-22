from dataclasses import dataclass

@dataclass
class RiskConfig:
    equity: float
    risk_per_trade: float
    max_daily_loss: float
    max_weekly_loss: float


def position_size_usd(equity: float, risk_per_trade: float, entry: float, stop: float) -> float:
    dist = abs(entry - stop)
    if dist <= 0:
        return 0.0
    risk_usd = equity * risk_per_trade
    qty = risk_usd / dist
    return qty * entry


def guards_ok(day_pnl_pct: float, week_pnl_pct: float, cfg: RiskConfig) -> tuple[bool, str]:
    if day_pnl_pct <= -cfg.max_daily_loss:
        return False, "Daily loss guard triggered"
    if week_pnl_pct <= -cfg.max_weekly_loss:
        return False, "Weekly loss guard triggered"
    return True, "OK"
