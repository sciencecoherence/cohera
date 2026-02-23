# HEARTBEAT.md

## Daily Morning Routine (07:00 AM Lima time)

- Check the current time (America/Lima).
- If time is between 07:00 and 07:30:
  - Read `memory/morning-state.json`.
  - If `last_sent` is NOT today's date (YYYY-MM-DD):
    - **Weather**: Fetch forecast for Lima (wttr.in).
    - **Work Done**: Read yesterday's memory file (`memory/YYYY-MM-DD.md`) and summarize key actions.
    - **Work Plan**: Read `/home/xavier/cohera-repo/TODO.md` (if it exists) for current focus items.
    - **Trades**: Run `python3 /home/xavier/cohera-repo/trading/bot/status.py` and `python3 /home/xavier/cohera-repo/trading/bot/journal.py --last 5` (if available) for open positions and recent activity.
    - **Research**: Check `chatgpt/research_autopilot.log` (last lines) and `site/publications/` for any new findings or queue updates from the last 24h.
    - **Action**: Send a consolidated "Morning Briefing" message with Weather, Work Done, Plan, Trade Status, and Research Updates.
    - **Update State**: Write `{"last_sent": "YYYY-MM-DD"}` to `memory/morning-state.json`.
