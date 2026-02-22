# Telegram Commands for Cohera Trading Bot

These are the commands you can send me via Telegram to control the bot. I will run the underlying Python scripts for you.

## 📡 Signals & Status

*   **"Status"** or **"Report"**
    *   Runs: `python3 bot/status.py`
    *   *Check current mode, open positions, and kill switch status.*

*   **"Signal"** or **"Scan"**
    *   Runs: `python3 bot/main.py`
    *   *Check for new trading setups. If valid, generates a PENDING order.*

*   **"Journal"** or **"PnL"**
    *   Runs: `python3 bot/journal.py`
    *   *Show recent trade history and performance.*

## ✅ Order Management (Semi-Auto)

*   **"Approve"** or **"Execute"**
    *   Runs: `python3 bot/approve_order.py`
    *   *Approve a pending order and execute it (Paper or Live).*

*   **"Deny"** or **"Reject"**
    *   Runs: `python3 bot/deny_order.py`
    *   *Discard a pending order.*

*   **"Pending"**
    *   Runs: `cat bot/state/pending_order.json`
    *   *View details of the current pending order (if any).*

## ⚠️ Emergency & Exits

*   **"Kill"** or **"Stop Everything"**
    *   Runs: `python3 bot/kill_switch.py`
    *   *IMMEDIATELY stops trading and closes all positions.*

*   **"Exit"** or **"Close"**
    *   Runs: `python3 bot/monitor_exit.py`
    *   *Manually trigger exit logic.*

## ⚙️ Config

*   **"Config"**
    *   *I can read/edit `bot/config.json` for you if you ask.*

---
*Note: I run these commands in `/home/xavier/cohera-repo/trading/`.*
