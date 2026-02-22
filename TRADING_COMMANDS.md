# Cohera Trading Bot Commands (Semi-Auto v1)

## Status & Control

*   **Check Status:** `python3 bot/status.py`
    *   Shows mode, symbol, leverage, kill_switch, pending/open orders, and execution count.

*   **Generate Signal & Pending Order:** `python3 bot/main.py`
    *   Runs signal engine and risk checks.
    *   If successful, creates a pending order in `state/pending_order.json`.

*   **Review Pending Order:** `cat bot/state/pending_order.json`
    *   Check details before approving.

*   **Approve Pending Order:** `python3 bot/approve_order.py`
    *   Executes the pending order (Paper or Live depending on config).

*   **Deny Pending Order:** `python3 bot/deny_order.py`
    *   Rejects the pending order.

## Safety & Exits

*   **Emergency Kill Switch:** `python3 bot/kill_switch.py`
    *   Immediately stops all trading and closes positions.

*   **Manual Exit:** `python3 bot/monitor_exit.py`
    *   Runs exit monitor logic (typically automated, but can be forced).

*   **View Journal:** `python3 bot/journal.py`
    *   Shows trading journal and PnL.

## Configuration

*   **Edit Config:** `nano bot/config.json`
    *   Change symbols, risk parameters, and modes.
