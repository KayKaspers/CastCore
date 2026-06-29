# Work Package Queue – CastCore

| ID | Title | Priority | Status | Prompt |
|---|---|---|---|---|
| CC-WP-001 | Add NDF baseline | P1 | done_after_commit | README_NDF_BASELINE.md |
| CC-WP-002 | Stabilize docs-status generation | P1 | ready | prompts/claude/CC-WP-002-docs-status-stability.md |
| CC-WP-003 | CastCore Health Score Review | P2 | ready | prompts/claude/CC-WP-003-health-score-review.md |
| CC-WP-004 | CastCore Release Readiness Review | P2 | draft | prompts/claude/CC-WP-004-release-readiness-review.md |
| CC-WP-005 | Add README NDF section | P3 | draft | prompts/claude/CC-WP-005-readme-ndf-section.md |
| CC-WP-006 | Security baseline review | P2 | draft | prompts/claude/CC-WP-006-security-baseline-review.md |

## Prioritätsregel

Erst Baseline committen.  
Dann `CC-WP-002` bearbeiten.

## Grenzen

- Keine großen Refactorings ohne Nova-Review.
- Keine unkontrollierten CI-Änderungen.
- Tests bleiben ffmpeg-frei/gemockt.
- Claude committet und pusht nicht.
