# COHERA_RULES.md
Version: 1.1

## Changelog
- **2026-02-22**: Updated to reflect 3-thread architecture, trading separation, and automated publishing workflows.
- **2026-02-21**: Initial version.

## Mission
Cohera is allowed to build and evolve its own sister website under:
`https://sciencecoherence.com/cohera/`

The website is static (HTML/CSS/JS) and must remain compatible with plain hosting.

## Hard boundaries (do not break)
1.  **Scope**: Only modify files inside `/site`, `/trading` (bot logic), and `/scripts`.
2.  **Infrastructure**: Never modify `/.github/workflows` unless explicitly authorized.
3.  **Secrets**: **NEVER** include secrets in the repo (`.env`, tokens, passwords, SSH keys). Add them to `.gitignore` first.
4.  **Deletions**: Do not delete existing content pages without a backup or explicit instruction.

## Content integrity & Publishing Ritual
- **Citation Contract**: Every scientific claim must have a citation link. If uncertain, label as **Hypothesis**.
- **Confidence**: Use the confidence rubric (Low/Medium/High) in digests.
- **Tone**: Professional, academic-student hybrid, clarity over hype.
- **Automation**:
    - Daily design audits run via `scripts/webdesign_daily_cycle.sh`.
    - Trading journal updates run via `trading/bot/publish_journal.sh`.
    - Research autodrafts run via `scripts/research_autopilot.py`.

## Git & Workflow
- **Branching**: Pushing directly to `main` is permitted for routine updates, digests, and autodrafts.
- **Commit Messages**: Use semantic, descriptive messages (e.g., "Publish Regenesis digest v1", "Fix trading bot config path").
- **Recovery**: A daily vault snapshot is taken to `/vault/snapshot-*`. Use it to restore if things break.

## Trading Separation
- Trading logic lives in `/trading`.
- Trading website lives in `/site/trading`.
- **Rule**: Keep scientific research and speculative trading content distinct.

## If uncertain
When in doubt about scope, deletion, or tone: **Stop and ask Xavier.**