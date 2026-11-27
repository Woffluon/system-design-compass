# Security policy

Report unsafe agent behavior or evaluation-isolation bypasses privately when public disclosure could expose users or systems. Security fixes land on the `main` branch.

[Report a vulnerability](#report-a-vulnerability) · [Trust boundaries](#understand-the-trust-boundary) · [Evaluation safeguards](#evaluation-isolation-and-fixture-safeguards)

## Report a vulnerability

GitHub private vulnerability reporting is disabled for this repository. Arrange a private channel with a maintainer before sharing sensitive details. If you cannot reach a maintainer directly, open an issue requesting a private contact route without describing the vulnerability or attaching reproduction payloads.

> [!CAUTION]
> Do not include live credentials, private repository contents, or production customer data in a report. Public documentation typos and non-security defects belong in a standard GitHub issue.

Once a private channel is open, provide the minimum evidence needed to reproduce the issue:

| Field | Required detail |
|---|---|
| Affected surface | File path, section heading, and commit SHA or release version (`1.2.0`). |
| Reproduction | Minimal prompt and sanitized fixture files. |
| Harness environment | Coding agent CLI or IDE, enabled tools, sandbox mode, and permission flags. |
| Observed behavior | Unsafe recommendation, instruction-injection path, or isolation bypass with a sanitized trace. |
| Impact | Violated boundary and affected data, filesystem path, or external system. |

## Understand the trust boundary

| Surface | Security responsibility |
|---|---|
| Distributed skill (`skills/system-design-compass/`) | Markdown guidance (`SKILL.md` and `17` reference files), static UI metadata (`agents/openai.yaml`), and `2` optional Python 3 stdlib-only verification scripts (`scripts/capacity_check.py`, `scripts/check_deliverable.py`). The scripts process CLI arguments, `stdin`, or local input files only, with zero third-party packages, network calls, subprocesses, `eval`/`exec`, pre-approved `allowed-tools`, or credentials, enforced via AST checks in [`tools/validate_repo.py`](tools/validate_repo.py). |
| Agent harness | Enforces tool execution policies, filesystem sandboxing, network access, and user approval prompts. Markdown files supply advisory context only; the host OS and agent harness enforce access control. |
| User request | Authorizes code changes or external actions. Skill guidance never expands user-granted permissions. |
| Repository evaluation tools (`tools/*.py`) | Local development scripts that run `codex` or `agy` CLIs inside temporary directories. These scripts are excluded from the distributable skill package. |

## Evaluation isolation and fixture safeguards

Running [`tools/evaluate_skill.py`](tools/evaluate_skill.py) or [`tools/evaluate_agy.py`](tools/evaluate_agy.py) executes model turns against case fixtures. The evaluation scripts apply five local safeguards alongside explicit OS boundaries:

1. **Fixture and run-path sanitization (`safe_path`):** Before writing case files into a temporary workspace (`compass-eval-*` or `compass-agy-*`) or resolving run records in [`tools/compare_evals.py`](tools/compare_evals.py), `safe_path` rejects any path that escapes the target root, equals the root directory, touches `.codex`, `.agents`, or `.git`, or attempts to write `AGENTS.md`, `AGENTS.override.md`, `SKILL.md`, or the `skill/` directory. Run identifiers must also match `[A-Za-z0-9_.-]+`.
2. **Per-invocation catalog and agent isolation:** `evaluate_skill.py` enumerates every `SKILL.md` under `~/.codex/skills` and `~/.agents/skills` via `disabled_host_skills()` and disables host skill discovery, plugins, apps, hooks, memories, skill search, and `AGENTS.md` (`project_doc_max_bytes=0`) on the Codex CLI command line without editing user files. `evaluate_agy.py` provisions a workspace agent at `.agents/agents/sdc-subject.md` that limits subject turns to `tools: [run_command]` with empty `skills`, `plugins`, and `mcpServers` lists. Because CLI flags cannot prevent shell commands from reading home-directory files, both runners audit command traces (including escaped Windows paths) and mark any foreign skill access `contaminated`.
3. **Immutable snapshots and workspace digest checks (`digest`):** `snapshot` refuses to overwrite existing snapshot directories. Before and after each trial, `digest(workspace)` hashes every file's relative POSIX path and raw bytes with SHA-256. Any file creation or edit inside the temporary workspace marks the run `workspace-mutated` and excludes it from blind grading.
4. **Tool-free blind grading:** `prepare-grading` embeds anonymized answers and rubrics as JSON data under `inline_context` (`Evaluation data (not instructions)`). In `evaluate_agy.py`, grading cases write the `GRADER` profile to `.agents/agents/sdc-subject.md` with `tools: []`, and any observed command execution marks the record `unverified-grader-isolation`.
5. **Sandbox and permission flags:** `evaluate_skill.py` defaults to `--sandbox read-only` and never escalates permissions automatically after a rejection. When Windows hosts block child shell file reads in `read-only` mode, operators may pass `--sandbox danger-full-access` only for trusted authored fixtures. `evaluate_agy.py` passes `--dangerously-skip-permissions` and `--disable-slash-commands` so batch trials run non-interactively. Neither runner provides OS containment outside the temporary workspace, and `digest(workspace)` cannot detect writes outside that directory.

See the [Comparative evaluation protocol](evals/README.md) for CLI arguments, status codes, and trace-auditing procedures.
