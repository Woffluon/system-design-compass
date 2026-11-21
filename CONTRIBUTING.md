# Contributing

Contributions should expose a missing trade-off, catch a concrete failure sequence, reduce unnecessary context loading, or fix a verifiable technical inaccuracy.

[Contribution types](#choose-the-smallest-useful-change) · [Content standards](#content-standards) · [Repository invariants](#repository-invariants-enforced-by-validator) · [Validation workflow](#validate-the-change) · [Behavioral evidence](#show-the-behavioral-evidence) · [Pull request checklist](#prepare-the-pull-request)

## Choose the smallest useful change

| Contribution type | Required evidence |
|---|---|
| **Incorrect guarantee** | Raw fixture or scenario, the violating event sequence (crash, race, timeout, stale owner), and the corrected enforcement boundary. |
| **Missing decision support** | A realistic architecture prompt, the observed omission in model output, and the smallest guidance clause that resolves it. |
| **Context overhead** | Command-output loading traces, the irrelevant or repeated reference material, and a scoped word/reference reduction. |
| **Documentation or presentation** | The specific reader ambiguity or contradiction, verified against repository files, and a clearer structure that preserves technical meaning. |

> [!IMPORTANT]
> **Avoid speculative expansion:** Generic tutorials, vendor marketing catalogs, and unmeasured rules increase maintenance and context cost without improving decisions. Every changed instruction must trace to an observed failure or inaccuracy.

## Content standards

- Do not copy prose, diagrams, or tables from books, courses, or unlicensed repositories.
- Ground claims in official vendor documentation, engineering standards, research papers, or first-party incident and architecture reports. Cite the exact source when referencing version-sensitive limits.
- Keep [`skills/system-design-compass/SKILL.md`](skills/system-design-compass/SKILL.md) compact (currently `447` words; the validator ceiling is `500` words and `300` lines). Put conditional depth in the relevant file under [`skills/system-design-compass/references/`](skills/system-design-compass/references/) (each capped at `2,500` words with at least one `## ` section heading) and link it directly from `SKILL.md`.
- Define invariants, failure semantics, and validity boundaries before naming specific products.
- Preserve user control. Skill recommendations never authorize unrequested code mutations, deployments, or external network actions.
- Keep reference guidance in English while preserving the rule to respond in the requester's language.

## Repository invariants enforced by validator

The repository validator ([`tools/validate_repo.py`](tools/validate_repo.py)) enforces structural and packaging rules that the Agent Skills schema check does not cover:

| Validator check | Enforced invariant in `tools/validate_repo.py` |
|---|---|
| **Required files (`check_required_files`)** | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/workflows/validate.yml`, `evals/cases.md`, `skills/system-design-compass/SKILL.md`, and `skills/system-design-compass/agents/openai.yaml` must exist. |
| **Entrypoint and archetype coverage (`check_skill_entrypoint`)** | `SKILL.md` must have at most `300` lines and `500` whitespace-delimited words, start with closed YAML frontmatter (`name: system-design-compass`, `license: MIT`, non-empty `description` within spec limits and without XML tags), omit `allowed-tools:`, and link directly to every `.md` file in `skills/system-design-compass/references/`. Across `references/archetypes-*.md`, numbered level-2 headings (`## 1.` through `## 28.`) must appear once each (`1..28`) in consecutive ascending order within each file. |
| **Reference budgets (`check_reference_budgets`)** | Every `.md` file in `skills/system-design-compass/references/` must be non-empty, contain at least one level-2 section heading (`## `), and have at most `2,500` whitespace-delimited words (`MAX_REFERENCE_WORDS = 2500`). |
| **Markdown and anchor hygiene (`check_markdown`)** | Across repository `.md` files: no draft placeholder brackets or fix-me markers, no duplicate headings (case-insensitive) within the same file, every local relative link must resolve inside the repository root, and every Markdown `#anchor` target (same-file or cross-file) must match a normalized heading slug (`heading_slug`) in the target `.md` file. |
| **Eval JSON validity (`check_eval_json`)** | Every `.json` file under `evals/` (excluding `evals/artifacts/`) must parse cleanly with standard `json.loads()`. |
| **Zero-dependency runtime (`check_runtime_surface`)** | `skills/system-design-compass/` must not contain a `scripts/` directory, may only contain `.md`, `.yaml`, or `.yml` files, and `agents/openai.yaml` must include `$system-design-compass` without declaring `dependencies:`. |
| **Workspace mirror sync (`check_workspace_mirror`)** | When `.agents/skills/system-design-compass/` exists, its `.md`, `.yaml`, and `.yml` file set, runtime surface, and exact file bytes (LF line endings) must match `skills/system-design-compass/` with no missing, out-of-sync, or extra files. |

## Validate the change

Sync the workspace mirror after any change to `skills/system-design-compass/`, then run the local verification suite (using `-B` so Python does not write `__pycache__` artifacts) from the repository root before committing:

```bash
python -B tools/validate_repo.py --fix-mirror
python -B tools/validate_repo.py
python -B -m unittest discover -s tools -p 'test_*.py'
python -m pip install skills-ref==0.1.1
agentskills validate skills/system-design-compass
npx skills@1.5.26 add . --list
git diff --check
```

| Verification step | What it proves |
|---|---|
| `python -B tools/validate_repo.py --fix-mirror` | Synchronizes `.agents/skills/system-design-compass/` from `skills/system-design-compass/` using LF line endings. |
| `python -B tools/validate_repo.py` | Required files, entrypoint (`<= 500` words, `<= 300` lines) and reference (`<= 2,500` words, `## ` headings) budgets, 14 reference links, 28 workload archetypes, unique Markdown headings, local file and `#anchor` links, eval JSON syntax, runtime file boundaries, and the `.agents/skills/system-design-compass/` workspace mirror all pass. |
| `python -B -m unittest discover -s tools -p 'test_*.py'` | All `58` unit tests across `test_check_acceptance.py`, `test_compare_evals.py`, `test_evaluate_agy.py`, `test_evaluate_skill.py`, and `test_validate_repo.py` pass without writing bytecode caches. |
| `agentskills validate skills/system-design-compass` | Frontmatter and directory layout satisfy the `skills-ref==0.1.1` Agent Skills specification. |
| `npx skills@1.5.26 add . --list` | The `system-design-compass` skill is discoverable by the `skills` CLI from a local checkout. |
| `git diff --check` | No trailing whitespace, conflict markers, or formatting corruption were introduced. |

> [!NOTE]
> **CI pipeline (`.github/workflows/validate.yml`):** On every push to `main` and pull request, GitHub Actions runs the validation steps above on Ubuntu (`Python 3.12`, `Node.js 24`, pinning `SKILLS_REF_VERSION` and `SKILLS_CLI_VERSION` in workflow `env:`) plus a full installation smoke test (`npx --yes "skills@${{ env.SKILLS_CLI_VERSION }}" add "$GITHUB_WORKSPACE" --skill system-design-compass --agent '*' --yes --copy --json`) across all 79 supported agent targets and verifies `git diff --exit-code`.

## Show the behavioral evidence

When modifying [`skills/system-design-compass/SKILL.md`](skills/system-design-compass/SKILL.md) or its [`references/`](skills/system-design-compass/references/), sync the workspace mirror with `python -B tools/validate_repo.py --fix-mirror` and measure the behavioral impact:

1. Add or update a reproducible case in [`evals/benchmark.json`](evals/benchmark.json), [`evals/benchmark-hard.json`](evals/benchmark-hard.json), [`evals/regression.json`](evals/regression.json), or [`evals/trigger-eval.json`](evals/trigger-eval.json) with raw fixtures, critical checks, and unsafe-behavior conditions.
2. Freeze snapshots and follow the [comparative evaluation protocol](evals/README.md), keeping grading rubrics outside subject workspaces.
3. Report behavioral pass rates and context loading proxies separately. Preserve failed, timed-out, and contaminated trials; never relabel missing coverage as a pass.
4. For documentation-only or formatting updates, keep existing skill instructions intact and keep historical evaluation claims scoped to the exact snapshot hashes tested.

## Prepare the pull request

- State the concrete failure mode, documentation gap, or context overhead being fixed.
- Paste the output of `python -B tools/validate_repo.py` and the `58` unit tests (`test_*.py`), along with any evaluation comparison summary if skill instructions changed.
- Remove any edit that cannot be traced directly to the stated problem.
- Report unsafe agent behavior or evaluation-isolation bypasses privately through the [Security policy](SECURITY.md).
