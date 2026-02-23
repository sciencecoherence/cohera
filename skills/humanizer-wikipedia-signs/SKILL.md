---
name: humanizer-wikipedia-signs
description: Humanize website prose by stripping common AI-writing patterns using cues inspired by Wikipedia discussions of AI-generated text/slop (banal style, repetitive structure, filler, generic transitions, and mass-produced tone). Use when polishing pages that sound robotic or templated.
---

Humanize prose with low-risk deterministic edits.

## Workflow
1. Run `scripts/humanize_site.py --root <site_dir>` to apply baseline replacements.
2. Re-read changed files and spot-check key pages (`index`, `research`, `publications`, latest findings).
3. Re-run publication/report generation scripts if needed.
4. Commit with a message that mentions humanization pass.

## Editing Rules (from AI-writing signs)
- Reduce superficial/banal filler (e.g., “in conclusion”, “it is important to note”).
- Remove repetitive signposting and robotic transitions.
- Replace generic inflated wording with direct phrasing.
- Keep claims and equations unchanged.
- Never alter links, code blocks, or HTML tags.

## Guardrails
- Only edit text content in `.html` and `.md` by default.
- Skip `assets/`, `node_modules/`, and minified files.
- Prefer small deterministic substitutions over generative rewrites.
