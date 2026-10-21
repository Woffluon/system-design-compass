# Contributing

**Help a coding agent make one better architecture decision.** Every contribution should expose a missing trade-off, catch a concrete failure sequence, reduce unnecessary context loading, or correct a verifiable technical inaccuracy.

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

- **Original work:** Do not copy prose, diagrams, or tables from books, courses, or unlicensed repositories.
- **Primary evidence:** Ground claims in official vendor documentation, engineering standards, research papers, or first-party incident/architecture reports. Cite the exact source when referencing version-sensitive limits.
- **Selective loading:** Keep [`skills/system-design-compass/SKILL.md`](skills/system-design-compass/SKILL.md) compact (currently `397` words; hard validator ceiling is `500` words and `300` lines). Put conditional depth in the relevant file under [`skills/system-design-compass/references/`](skills/system-design-compass/references/) and link it directly from `SKILL.md`.
- **Capabilities before vendors:** Define invariants, failure semantics, and validity boundaries before naming specific products.
- **Authorization boundary:** Preserve user control. Skill recommendations never authorize unrequested code mutations, deployments, or external network actions.
- **Language and scope:** Maintain English reference guidance while preserving the rule to respond in the requester's language.

## Repository invariants enforced by validator

The repository validator ([`tools/validate_repo.py`](tools/validate_repo.py)) enforces structural and packaging rules that the standard Agent Skills schema check does not cover:

| Surface | Enforced invariant in `tools/validate_repo.py` |
|---|---|
| **Required files (`check_required_files`)** | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/workflows/validate.yml`, `evals/cases.md`, `skills/system-design-compass/SKILL.md`, and `skills/system-design-compass/agents/openai.yaml` must exist. |
| **Entrypoint limits (`check_skill_entrypoint`)** | `SKILL.md` must have at most `300` lines and `500` whitespace-delimited words, start with closed YAML frontmatter (`name: system-design-compass`, `license: MIT`, non-empty `description`), and omit `allowed-tools:`. |
| **Reference & archetype coverage** | Every `.md` file in `skills/system-design-compass/references/` must be linked directly from `SKILL.md`. Across `archetypes-*.md`, numbered level-2 headings (`## 1.` through `## 28.`) must appear once each (`1..28`). |
| **Markdown hygiene (`check_markdown`)** | Across all `.md` files: no draft placeholder brackets or fix-me markers, **no duplicate headings** (case-insensitive) within the same file, and every local relative link must resolve inside the repository root. |
| **Zero-dependency runtime (`check_runtime_surface`)** | `skills/system-design-compass/` must not contain a `scripts/` directory, may only contain `.md`, `.yaml`, or `.yml` files, and `agents/openai.yaml` must include `$system-design-compass` without declaring `dependencies:`. |

## Validate the change

Run the complete local verification suite from the repository root before committing:

```bash
python tools/validate_repo.py
python -m unittest discover -s tools -p 'test_*.py'
python -m pip install skills-ref==0.1.1
agentskills validate skills/system-design-compass
npx skills@1.5.26 add . --list
git diff --check
```

| Verification step | What it proves |
|---|---|
| `python tools/validate_repo.py` | All required files, entrypoint word/line caps, 14 reference links, 28 workload archetypes, unique Markdown headings, local link targets, and runtime boundaries pass. |
| `python -m unittest discover -s tools -p 'test_*.py'` | All `30` unit tests across `test_check_acceptance.py`, `test_compare_evals.py`, `test_evaluate_agy.py`, and `test_evaluate_skill.py` pass. |
| `agentskills validate skills/system-design-compass` | Frontmatter and directory layout satisfy the `skills-ref==0.1.1` Agent Skills specification. |
| `npx skills@1.5.26 add . --list` | The `system-design-compass` skill is discoverable by the `skills` CLI from a local checkout. |
| `git diff --check` | No trailing whitespace, conflict markers, or formatting corruption were introduced. |

> [!NOTE]
> **CI pipeline (`.github/workflows/validate.yml`):** On every push to `main` and pull request, GitHub Actions runs the steps above on Ubuntu (`Python 3.12`, `Node.js 24`) plus a full installation smoke test (`npx --yes skills@1.5.26 add "$GITHUB_WORKSPACE" --skill system-design-compass --agent '*' --yes --copy --json`) across all 79 supported agent targets and verifies `git diff --exit-code`.

## Show the behavioral evidence

Format and link validation do not prove better model decisions. When modifying [`skills/system-design-compass/SKILL.md`](skills/system-design-compass/SKILL.md) or its [`references/`](skills/system-design-compass/references/):

1. Add or update a reproducible case in [`evals/benchmark.json`](evals/benchmark.json), [`evals/benchmark-hard.json`](evals/benchmark-hard.json), or [`evals/regression.json`](evals/regression.json) with raw fixtures, critical checks, and unsafe-behavior conditions.
2. Freeze snapshots and follow the [comparative evaluation protocol](evals/README.md), keeping grading rubrics completely outside subject workspaces.
3. Report behavioral pass rates and context loading proxies separately. Preserve failed, timed-out, and contaminated trials; never relabel missing coverage as a pass.
4. For documentation-only or formatting updates, preserve existing instructions and keep historical evaluation claims scoped to the exact snapshot hashes tested.

## Prepare the pull request

- **Lead with the problem:** State the concrete failure mode, documentation gap, or context overhead being fixed.
- **Show verification:** Paste the output of `python tools/validate_repo.py` and the `30` unit tests (`test_*.py`), along with any evaluation comparison summary if skill instructions changed.
- **Keep changes surgical:** Remove any edit that cannot be traced directly to the stated problem.
- **Security issues:** Report unsafe agent behavior or isolation bypasses privately via the [Security policy](SECURITY.md) rather than in a public pull request.
