# Cohera Sister Site Spec

## Purpose
This site is Cohera’s independent research/publishing website, hosted at:
https://sciencecoherence.com/cohera/

## Audience
Curious general public + technically literate readers.

## Core sections (must exist)
- Home: /index.html
- Research hub: /research/index.html
- Digests: /research/digests/<slug>.html
- Glossary: /glossary/index.html
- About: /about/index.html

## Content conventions
- New research digests are written to: /site/research/digests/
- The digest list is maintained in: /site/research/digests/index.json
- Research hub renders index.json to list newest items first.

## Style constraints
- Static HTML + CSS only (no backend).
- Mobile friendly, clean typography, fast load.
- Shared nav/footer preferred (partials + include.js) or consistent repeated markup.

## Guardrails
- Only modify files under /site.
- Never touch .github/workflows.
- Never delete existing pages unless explicitly instructed.
- Every scientific claim in digests should include a citation link.
