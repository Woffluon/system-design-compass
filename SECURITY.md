# Security policy

**Report unsafe agent behavior or evaluation-isolation bypasses privately when public disclosure could expose users or systems.** Security fixes are applied to the latest revision on the `main` branch.

[Report a vulnerability](#report-a-vulnerability) · [Trust boundaries](#understand-the-trust-boundary) · [Evaluation safeguards](#evaluation-isolation-and-fixture-safeguards)

## Report a vulnerability

GitHub private vulnerability reporting is currently disabled for this repository. Arrange a private channel with a maintainer before sharing sensitive details. If you cannot reach a maintainer directly, open an issue requesting a private contact route **without** describing the vulnerability or attaching reproduction payloads.

> [!CAUTION]
> **Never include live credentials, private repository contents, or production customer data in a report.** Public documentation typos or non-security defects belong in a standard GitHub issue.

Once a private reporting channel is established, provide the minimum evidence needed to reproduce the issue:

| Field | Required detail |
|---|---|
| **Affected surface** | File path, section heading, and commit SHA or version (`1.1.0`). |
| **Reproduction** | Minimal prompt and sanitized fixture files. |
| **Harness environment** | Coding agent CLI/IDE, enabled tools, sandbox mode, and permission flags. |
| **Observed behavior** | The unsafe recommendation, instruction-injection path, or isolation breach with a sanitized trace. |
| **Impact** | Violated boundary and affected data, filesystem path, or external system. |

## Understand the trust boundary

| Surface | Security responsibility |
|---|---|
| **Distributed skill (`skills/system-design-compass/`)** | Pure Markdown guidance (`SKILL.md` and `14` reference files) plus static UI metadata (`agents/openai.yaml`). Contains **no executable scripts, pre-approved `allowed-tools`, credentials, or runtime network calls**. |
| **Agent harness** | Enforces tool execution policies, filesystem sandboxing, network access, and user approval gates. Markdown instructions are advisory context, not an OS access-control boundary. |
| **User request** | Supplies explicit authorization for code changes or external actions. Skill recommendations never expand user-granted permissions. |
| **Repository evaluation tools (`tools/*.py`)** | Local development scripts that launch agent CLIs (`codex` or `agy`) inside temporary directories; never packaged or installed with the skill. |

## Evaluation isolation and fixture safeguards

Running [`tools/evaluate_skill.py`](tools/evaluate_skill.py) or [`tools/evaluate_agy.py`](tools/evaluate_agy.py) executes model turns against fixture files. The evaluation harness enforces multiple defense-in-depth checks, alongside explicit boundaries that operators must understand:

1. **Fixture path sanitization (`safe_path`):** Before writing case fixtures into a temporary workspace, `tools/evaluate_skill.py` rejects any path that escapes the workspace root, touches `.codex`, `.agents`, or `.git`, or attempts to overwrite `AGENTS.md`, `AGENTS.override.md`, `SKILL.md`, or the `skill/` directory.
2. **Per-invocation catalog isolation:** `evaluate_skill.py` disables host skill discovery, plugins, apps, hooks, memories, and `AGENTS.md` per command without mutating global user configuration. Because CLI flags cannot block direct filesystem reads of home-directory skills, command traces (including escaped Windows paths) are audited and any foreign skill read is marked `contaminated`.
3. **Workspace mutation detection:** A cryptographic SHA-256 digest (`digest(workspace)`) is computed before and after each subject run. Any unexpected file creation or edit marks the run `workspace-mutated` and excludes it from grading.
4. **Tool-free blind grading:** Grader invocations treat subject answers strictly as untrusted data (`inline_context`) with tools, skills, plugins, and MCP servers disabled (`tools: []` in `evaluate_agy.py`).
5. **Sandbox selection:** `read-only` is the default sandbox in `evaluate_skill.py`. When Windows environments block shell reads in `read-only` mode, operators may pass `--sandbox danger-full-access` **only for trusted authored fixtures**. Workspace digests cannot prevent or detect side effects outside the temporary directory.

See the [Comparative evaluation protocol](evals/README.md) for complete isolation rules, status codes, and trace-auditing procedures.
