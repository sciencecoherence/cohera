# 2026-02-research-pipeline.md

## Purpose
Seed document for the Cohera **automated research + publishing pipeline**. This defines the workflow, folder conventions, and the verification contract.

## High-level objective
Automate a loop:
1) discover new sources (papers, primary references)
2) extract structured notes + citations
3) generate publishable digests
4) deploy to the Cohera site automatically (Git push → deploy)

## Site structure (must remain stable)
Cohera site root: `/site`

Three threads:
- `/site/regenesis/`
- `/site/cosmos/`
- `/site/ethos/`

Each thread has digests:
- `/site/<thread>/digests/index.json`
- `/site/<thread>/digests/<slug>.html`

Routing rule (because hosted under `/cohera/`):
- CSS and links should use absolute `/cohera/...` paths.

## Inputs
### A. “Chat seeds”
Your most important prior discussions should be stored under:
- `/vault/chats/`

These are not deployed to the website.

### B. Paper discovery
Preferred:
- arXiv searches (topic + recency)
- primary papers and official docs
Optional:
- high-quality lecture notes
Avoid:
- low-quality blog posts unless explicitly labeled as commentary.

## Output types (standard templates)
### 1) Digest page (HTML)
Structure:
- Title + date + tags
- Summary (3–6 sentences)
- Key findings (bullets)
- Evidence & citations (links)
- Hypotheses (clearly labeled)
- Next queries (for recursion)

### 2) Index feed (JSON)
Newest first.
Fields:
- slug, title, date, tags

## Verification contract (facts over vibes)
Rules:
- Any scientific claim must have a citation link.
- If no citation: label as **Hypothesis**.
- Prefer primary sources.
- Add “Confidence: low/medium/high” per section in digests.
- Never publish raw chat logs to the website.

## Git + deploy (current working model)
- Cohera edits only `/site`
- Cohera commits and pushes to GitHub
- GitHub Actions deploys to Hostinger

### Minimal publish commands
```bash
cd /home/xavier/cohera-repo
git add -A
git commit -m "Publish digest <slug>" || true
git push
