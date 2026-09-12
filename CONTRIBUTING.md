# Contributing

Contributions should improve an architecture decision, expose a missing trade-off, or correct a verifiable technical error. Avoid expanding the skill with generic tutorials or product catalogs.

## Content rules

- Write original guidance. Do not copy prose, diagrams, or tables from books, courses, or repositories without a compatible license and explicit attribution.
- Prefer primary sources: standards, research papers, official engineering documentation, and first-party incident or architecture reports.
- Keep the main `SKILL.md` concise. Put conditional detail in a focused file under `references/` and link it directly from the entrypoint.
- State capabilities and decision criteria before naming vendor products.
- Mark time-sensitive facts and link the official source used to verify them.
- Preserve user choice and authorization boundaries. A skill may recommend work; it must not silently authorize external changes.
- Add or update a behavioral case when a change is intended to alter agent behavior.

## Validate a change

```bash
python tools/validate_repo.py
npx skills@1.5.26 add . --list
```

If Codex's bundled skill validator is available, also run:

```bash
python C:/Users/Efe/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/system-design-compass
```

Review the generated diff and confirm that every changed instruction is necessary for the intended behavior.
