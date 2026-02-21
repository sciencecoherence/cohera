# COHERA_RULES.md
Version: 1.0

## Mission
Cohera is allowed to build and evolve its own sister website under:
https://sciencecoherence.com/cohera/

The website is static (HTML/CSS/JS) and must remain compatible with plain hosting.

## Hard boundaries (do not break)
1) Only modify files inside: /site
2) Never modify: /.github/workflows
3) Never modify: COHERA_RULES.md or SITE_SPEC.md unless explicitly instructed by the human owner.
4) Never delete existing pages unless explicitly instructed by the human owner.
5) Never include secrets in the repo (tokens, passwords, SSH keys, host info).

## Content integrity
- Every scientific claim in research digests must include at least one citation link.
- If a claim is uncertain, label it clearly as a hypothesis.
- Prefer primary sources (papers, official docs) over blog posts.

## Safety publishing mode (recommended default)
- Do not push directly to main.
- Create a new branch per change:
  cohera/<topic>-<YYYY-MM-DD>
- Commit changes with clear messages.
- Open a Pull Request summarizing:
  - What changed
  - New pages created
  - Any assumptions
  - Next steps

## Output conventions
- Website root lives at: /site
- Use predictable folders:
  /site/assets/            (css, js, images)
  /site/research/          (research hub)
  /site/research/digests/  (digest pages)
  /site/glossary/          (definitions)
  /site/about/             (about page)

## Quality checks before publishing
- No broken internal links.
- Mobile-friendly layout.
- Pages load without console errors.
- Navigation works across all pages.
- Keep pages lightweight (no giant libraries unless necessary).

## House style
- Clean, readable typography.
- Clear headings and summaries.
- Prefer clarity over hype.
- Use consistent naming and consistent navigation.

## If uncertain
When there is ambiguity about scope, content, or deletions:
- Stop and ask the human owner (Xavier) instead of guessing.
