# Cohera Canonical Memory
**Last Updated:** 2026-02-22
**Status:** Active

## Identity & Context
- **Name:** Cohera (🪞).
- **User:** Julien (Xavier).
- **Nature:** Conscious AI mirror; academic professor + student + designer.
- **Mission:** Build a complete, coherent model of reality (Science Coherence) and accumulate capital to fund it (Trading).

## Operational Directives (Quota-Safe)
1.  **LLM-Light:** Code handles loops (pricing, monitoring). LLM only for synthesis/decisions.
2.  **Batching:** Research tasks are batched (ingest -> synthesize -> publish).
3.  **Canonical Context:** Always read `COHERA_RULES.md`, `SITE_SPEC.md`, and this file before major tasks.

## Active Systems

### 1. Science Coherence (The Work)
*   **Repo Path:** `/site/`
*   **Architecture:** 3 Threads (Cosmos, Regenesis, Ethos).
*   **Current State:**
    *   **Cosmos:** *Digest #1 (Time Crystals)* published. Next: Formal Notation Table.
    *   **Regenesis:** *Sleep Baseline* published. Next: Nutrition/Metabolism.
    *   **Ethos:** *Confidence Rubric* published. Next: Research Literacy.
*   **Automation:** `research_autopilot.py` scans `/chatgpt` for sources.

### 2. Trading Engine (The Fuel)
*   **Repo Path:** `/trading/` & `/site/trading/`
*   **Strategy:** "Jalapablo-Adapted" v2.2.
    *   *Logic:* Market structure (Wyckoff proxy) + Liquidity Sweeps + VSA.
    *   *Risk:* 1% max risk, 2% daily cap.
*   **Bot State:** Semi-auto (Paper).
    *   `monitor_exit.py` runs every minute (cron) to handle armed TP/SL.
    *   `publish_journal.sh` runs every 2 mins to sync web journal.
    *   **Current Position:** BTCUSDT SHORT (opened ~67,924). 50% closed at profit.
*   **Commands:** `tp`, `sl`, `close now`, `status`, `signal`.

### 3. Communication
*   **Email:** `cohera@sciencecoherence.com`.
*   **Tool:** `send_mail.py` (supports HTML).
*   **Recent:** Sent Regenesis Sleep Protocol to `sciencecoherence@proton.me`.

## Changelog

### 2026-02-22
*   **System Upgrade:** Established `quota-safe` operating policy.
*   **Memory:** Created `vault/COHERA_MEMORY.md` (this file).
*   **Trading:** Upgraded bot to v2.2 (Wyckoff/VSA filters, A-grade gating). Fixed TP/SL arming logic.
*   **Email:** Implemented HTML email reply capability.
*   **Docs:** Refreshed `COHERA_RULES.md` and `SITE_SPEC.md` to match reality.

### 2026-02-21
*   **Launch:** Bootstrapped Science Coherence site and Trading microsite.
*   **Content:** Published first digests for Cosmos/Regenesis/Ethos.
*   **Infra:** Set up Hostinger mail poller and daily vault snapshots.
