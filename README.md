<p align="center">
  <img src="assets/system-design-compass-logo.svg" alt="System Design Compass logo" width="128" height="128" />
</p>

# System Design Compass

A zero-dependency [Agent Skills](https://agentskills.io/specification) package that guides coding agents through production system design, architecture reviews, and migrations by naming the state invariant, constructing a concrete failure sequence, and specifying a pass/fail validation check.

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-0f172a)](https://agentskills.io/specification)
[![Version](https://img.shields.io/badge/version-1.2.0-0f172a)](skills/system-design-compass/SKILL.md)
[![Benchmark](https://img.shields.io/badge/Gemini_3.8_benchmark-8%2F8_passed-2ea44f)](#measured-results-and-current-limits)
[![Entrypoint](https://img.shields.io/badge/entrypoint-447_words-2563eb)](skills/system-design-compass/SKILL.md)
[![Dependencies](https://img.shields.io/badge/runtime_dependencies-0-0f172a)](#repository-structure-and-runtime-boundary)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f172a)](LICENSE)

[Quickstart](#quickstart-in-60-seconds) · [Why Compass](#why-compass-the-decision-lens) · [Routing architecture](#how-the-skill-routes-decisions) · [Workflow modes](#core-workflow-modes) · [Reference directory](#on-demand-reference-directory) · [Workload catalogs](#28-production-workload-archetypes) · [Project structure](#repository-structure-and-runtime-boundary) · [Evaluation evidence](#measured-results-and-current-limits) · [Verification and dev](#development-and-verification)

> [!IMPORTANT]
> **Frozen `1.1.0` benchmark status and `1.2.0` evaluation scope**
>
> On the frozen `667dc44` 397-word `1.1.0` snapshot (`sha256: 56723ba749e5...`, prior to `12b6def`/`29e988c` and the `1.2.0` updates), all 8/8 core benchmark cases passed (`40/44` rubric checks, `0` critical violations, `0` unsafe outcomes) on `gemini-3.8-flash-medium` under tool-free blind grading. The full two-model release gate (`tools/check_acceptance.py`), the 8-case regression suite, repeated hard-case confirmations, and a post-`1.2.0` behavioral re-run remain open. See [Measured results and current limits](#measured-results-and-current-limits) and the [evaluation report](evals/results/2026-10-01.md) for the exact scope boundary.

## Quickstart in 60 seconds

Install the skill from GitHub into your active workspace using the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add Woffluon/system-design-compass
```

From a local repository checkout, install directly from the root:

```bash
npx skills add .
```

### Invoke the skill in your coding agent

When your coding agent supports named skills, trigger it directly with a concrete architectural scenario:

```text
$system-design-compass Review this service's retry and timeout boundaries.
Use repository evidence. Preserve sound decisions. Give the smallest
correction and one experiment that could falsify the recommendation.
```

<details>
<summary><strong>Global installation, multi-agent targeting, and configuration</strong></summary>

Install globally across your user profile:

```bash
npx skills add Woffluon/system-design-compass --global
```

Target specific coding agents non-interactively:

```bash
npx skills add Woffluon/system-design-compass \
  --skill system-design-compass \
  --agent claude-code codex cursor gemini-cli github-copilot opencode \
  --global --yes
```

The skill requires no environment variables, API keys, MCP servers, or runtime scripts. During installation, the `skills` CLI copies the package into each target agent's skill directory (`79` supported agent targets across `55` directories, verified in CI with `skills@1.5.26`). The skill responds in the user's language while keeping reference terminology in English.

</details>

## Why Compass: the decision lens

Architecture advice becomes actionable when it states where a guarantee is enforced, which event sequence breaks it, and what observable test would disprove it.

| Familiar advice | The decision worth resolving |
|---|---|
| "Add idempotency." | What scopes the operation identity within its issuer contract, where are effect and result committed atomically, and what happens after a crash? |
| "Use a queue." | Does completion capacity exceed retry-amplified demand after worker loss, and who intervenes when backlog age rises? |
| "Roll back the deployment." | Can old code still read and write new data safely, and which external or unreplicated effects are already irreversible? |
| "Shard for scale." | Which measured bottleneck requires partitioning, and does the key distribute real skewed traffic? |
| "Modernize the architecture." | Which concrete invariant is failing today, and which sound existing decisions should remain untouched? |

> [!TIP]
> **Failure boundaries to check in every review**
> - When a remote call times out, resolve the external outcome before retrying or issuing a compensating action.
> - When a queue buffers a traffic spike or worker outage, verify that completion capacity exceeds normal arrivals plus retries so the backlog drains.
> - Before relying on binary rollback, verify that old code can both read and write data produced by the new version.

## How the skill routes decisions

The 447-word [entrypoint](skills/system-design-compass/SKILL.md) routes requests by the unresolved decision. Narrow Architectural Decision Records (ADRs) use the supplied facts and the entrypoint alone unless a decision-changing guarantee is missing. Broader requests open one workflow guide and only the specific boundary or workload sections that apply.

```mermaid
flowchart LR
    classDef navy fill:#0f172a,stroke:#090d16,color:#f8fafc,stroke-width:1.5px
    classDef cobalt fill:#2563eb,stroke:#1d4ed8,color:#ffffff,stroke-width:2px
    classDef slate fill:#f8fafc,stroke:#0f172a,color:#0f172a,stroke-width:1.5px

    Req["Architecture Request + Evidence"]:::slate --> Entry["SKILL.md Entrypoint (447 words)"]:::cobalt

    Entry -->|"Narrow ADR"| Narrow["Direct ADR Decision (Latency, Isolation, Retry Safety, Cost, Trigger)"]:::slate
    Entry -->|"Broad Workflow"| Modes["Mode Guides (design / review / evolve / interview)"]:::navy
    Entry -->|"Missing Boundary Guarantee"| Bounds["6 Boundary References (Estimation, Data/Identity, Distributed, Readiness, Formats, Validation)"]:::navy
    Entry -->|"Workload Unknowns"| Arch["4 Archetype Catalogs (28 Numbered Topics)"]:::navy

    Narrow & Modes & Bounds & Arch --> Gate["Proof & Falsification Gate (Invariant, Violating Sequence, Fault Schedule, Pass/Fail Oracle)"]:::cobalt
```

When evidence conflicts or correctness guarantees are uncertain, the skill runs a five-step check before recommending a design:

1. Name the critical invariant and its authoritative state owner.
2. Construct a concrete violating event sequence such as a concurrency race, crash between effect and record, timeout ambiguity, stale lease holder, or conflicting migration write.
3. Compare credible options against the simplest baseline using repository facts, arithmetic checks, and primary documentation.
4. State the enforcement mechanism, operational downside, and measurable reconsideration trigger.
5. Specify a concrete fault-injection schedule with an observable pass/fail oracle.

## Core workflow modes

| Mode | Example prompt | Deliverable |
|---|---|---|
| **Design** | "Design delivery semantics for customer webhook endpoints." | Authoritative ownership, state contracts, credible options, and explicit failure guarantees. |
| **Review** | "Assess this architecture's tail-latency and retry risks." | Repository evidence citations, concrete trigger, blast radius, smallest correction, and validation test. |
| **Evolve** | "Move this database while writers and old clients remain active." | Per-phase source of truth, version-guarded convergence evidence, cutover barrier, and rollback boundaries. |
| **Decide narrowly** | "Write an ADR for synchronous vs. queue-backed thumbnail rendering." | One scoped ADR (`~200–400` words) covering latency, failure isolation, retry safety, cost drivers, and reconsideration triggers. |
| **Practice** | "Run a 45-minute system design interview for search autocomplete." | Time-boxed scoping, capacity estimation, deep dives, failure analysis, and structured rubric feedback. |

Pass the artifacts you have, such as source code, schemas, configuration, SLOs, incident timelines, or existing ADRs. The skill records missing evidence as an explicit unknown or conditional assumption and separates it from confirmed defects. Harnesses with automatic skill discovery can also trigger the skill from natural-language prompts using the 16-query suite in [`evals/trigger-eval.json`](evals/trigger-eval.json); the behavioral benchmark suite evaluates explicit invocations rather than automatic activation accuracy.

## On-demand reference directory

The [entrypoint](skills/system-design-compass/SKILL.md) links directly to 14 reference files under `skills/system-design-compass/references/` (each capped at `2,500` words by `tools/validate_repo.py`). Agents search section headings and read only the section required by the active decision.

| Reference guide | When the agent loads it |
|---|---|
| [Design](skills/system-design-compass/references/design.md) · [Review](skills/system-design-compass/references/review.md) · [Evolution](skills/system-design-compass/references/evolve.md) | The task requires a full greenfield design, evidence-based audit, or phased migration workflow. |
| [Requirements and estimation](skills/system-design-compass/references/requirements-estimation.md) | SLOs, burst demand, retry amplification, or unit conversions drive capacity choices. |
| [Interfaces and data](skills/system-design-compass/references/interfaces-data.md) | Authorization, scoped retry identity, atomic effect/result, or external provider reconciliation is unresolved. |
| [Distributed systems](skills/system-design-compass/references/distributed-systems.md) | Queue backlog recovery, lease fencing, replication lag, sharding, or overload protection affects guarantees. |
| [Production readiness](skills/system-design-compass/references/production-readiness.md) | Disaster recovery drills, threat boundaries, observability signals, or cost drivers matter. |
| [Decision validation](skills/system-design-compass/references/decision-validation.md) | A proposed mechanism lacks a concrete fault schedule, pass/fail oracle, or owned repair path. |
| [Deliverables and diagrams](skills/system-design-compass/references/deliverables-diagrams.md) | The requester needs an ADR, RFC, review finding, migration phase table, interview feedback, or C4/sequence diagram. |
| [Interview](skills/system-design-compass/references/interview.md) | Mock interview facilitation or retrospective grading is explicitly requested. |

## 28 production workload archetypes

Organized into four domain catalogs under `skills/system-design-compass/references/`:

| Archetype catalog | Numbered topics (`1` to `28`) |
|---|---|
| [Foundations and platform](skills/system-design-compass/references/archetypes-foundations-platform.md) | `1` Scaling from one service to large traffic · `2` Back-of-the-envelope estimation · `3` System design framework · `4` Rate limiter · `5` Consistent placement and hashing · `6` Distributed key-value store · `7` Unique identifier generation |
| [User-facing and realtime](skills/system-design-compass/references/archetypes-user-facing-realtime.md) | `8` URL shortener · `9` Web crawler · `10` Notification delivery · `11` News feed · `12` Chat · `13` Search autocomplete · `14` Video platform · `15` File storage and synchronization · `16` Proximity search · `17` Nearby friends · `18` Map and navigation |
| [Data and infrastructure](skills/system-design-compass/references/archetypes-data-infrastructure.md) | `19` Distributed message queue · `20` Metrics, monitoring, and alerting · `21` Event aggregation and ad clicks · `22` Distributed email service · `23` Object storage |
| [Transactional and financial](skills/system-design-compass/references/archetypes-transactional-financial.md) | `24` Reservation system · `25` Real-time leaderboard · `26` Payment system · `27` Digital wallet and ledger · `28` Stock exchange and matching |

Each archetype entry lists the domain's failure modes, state invariants, and discriminating design questions so the agent can test a workload's actual bottlenecks.

## Repository structure and runtime boundary

The repository separates the distributable skill package ([Agent Skills specification](https://agentskills.io/specification)) from local evaluation and validation tooling:

```text
system-design-compass/
├── .gitattributes                         # Enforces LF line endings across platforms (* text=auto eol=lf)
├── skills/system-design-compass/          # Distributable skill package (zero runtime dependencies)
│   ├── SKILL.md                           # 447-word routing entrypoint and proof obligations
│   ├── agents/openai.yaml                 # Optional agent UI metadata ($system-design-compass)
│   └── references/                        # 14 on-demand Markdown guides (<= 2,500 words each)
├── .agents/skills/system-design-compass/  # Workspace skill mirror synced via validate_repo.py --fix-mirror
├── evals/                                 # Behavioral evaluation suites, protocol, and reports
│   ├── README.md                          # Blinded evaluation protocol and CLI reference
│   ├── cases.md                           # Human-readable release expectations for the 8 core cases
│   ├── benchmark.json                     # 8 core comparative evaluation fixtures and rubrics
│   ├── benchmark-hard.json                # 3 prospective hard-case extensions (wallet, queue, cutover)
│   ├── regression.json                    # 8 single-turn regression adaptations of cases.md
│   ├── trigger-eval.json                  # 16 automatic activation queries (8 positive, 8 near-miss negative)
│   ├── acceptance-2026-10-01.md           # Prospective stage ledger and protocol amendments
│   └── results/                           # Published evaluation reports (2026-09-30, 2026-10-01)
├── tools/                                 # Python 3.12 stdlib validators, evaluation runners, and 58 unit tests
│   ├── validate_repo.py                   # Enforces repo invariants, JSON/link/anchor checks, and mirror sync
│   ├── evaluate_skill.py                  # Isolated Codex CLI runner, blind packet builder, and grader prep
│   ├── evaluate_agy.py                    # Antigravity CLI fallback runner with trace normalization
│   ├── compare_evals.py                   # Unblinds, validates rubric coverage, and summarizes metrics
│   ├── check_acceptance.py                # Verifies multi-model coverage, repeated gains, and context reduction
│   └── test_*.py                          # 58 unit tests covering repo validation, grading, isolation, and acceptance
├── assets/                                # Square skill logos (SVG/PNG) and visual asset specifications
└── .github/workflows/validate.yml         # CI pipeline (repo invariants, unit tests, spec check, 79-agent smoke test)
```

## Measured results and current limits

The [evaluation report](evals/results/2026-10-01.md) separates behavioral quality, context loading proxies, and packaging checks across frozen skill snapshots (`original`, `rc.1` through `rc.10`, and the condensed `1.1.0` `667dc44` snapshot).

| Measurement or cohort | Evidence recorded in repository | Scope and interpretation |
|---|---|---|
| **Entrypoint size (`original` -> `1.1.0` -> `1.2.0`)** | `594` (`original`) -> `450` (`rc.9`) -> `469` (`rc.10`) -> `397` (`1.1.0`) -> **`447` words (`1.2.0`)**. | Meets the `<= 500`-word and `<= 300`-line limits enforced by `validate_repo.py`. |
| **Frozen `1.1.0` (`667dc44`) snapshot (`gemini-3.8-flash-medium`): `8/8` benchmark passed** | `40/44` rubric checks passed (`0` critical failures, `0` unsafe answers, `2,307` median read words, `1,052` words on `narrow-adr`). | Tool-free blind grading on the 8 core benchmark cases (`repeat 1`, frozen `667dc44` snapshot prior to `12b6def`/`29e988c` and `1.2.0` updates; `skill_digest: 56723ba...`). |
| **`rc.9` narrow-ADR read words (`3.6` / `3.8` Flash Medium)** | `1,248` -> `1,105` words (`-11.5%`) on `3.6`; `2,723` -> `789` words (`-71.0%`) on `3.8`. | Measures returned command-output words on paired narrow ADR runs as an approximate context proxy. |
| **`rc.9` full two-model comparison (`71` graded answers)** | `3.6` passed `6/8` core and `7/8` regression; `3.8` passed `7/8` core and `7/8` regression. | Did not pass the full two-model release gate (`check_acceptance.py`) due to webhook, wallet, and rollback omissions. |
| **`rc.10` early webhook gate (`469`-word snapshot)** | `0/2` candidate webhook answers passed all checks across `3.6` and `3.8` Flash Medium. | Stopped the full `rc.10` cohort early before the entrypoint was condensed to `397` words. |
| **Packaging and CLI installation (`skills@1.5.26`)** | `79` supported agent targets across `55` directories; `14/14` reference files match byte-for-byte under LF line endings (`.gitattributes`). | Verifies package format compatibility and CLI discovery layout across all 79 target directories. |

> [!NOTE]
> **Evidence boundaries:** Read-word counts measure returned tool output naming `SKILL.md` or `references/*.md` as an approximate context proxy; provider token totals are reported separately in the evaluation tables. The [September 30 report](evals/results/2026-09-30.md) records the earlier Codex (`gpt-5.6-sol` / `gpt-5.6-luna`) cohort for its frozen snapshot, and the [October 1 report](evals/results/2026-10-01.md) records `30` evaluation-helper unit tests from before `test_validate_repo.py` and subsequent validator/runner tests expanded the suite to `58` unit tests.

## Development and verification

Useful contributions start with an anonymized architecture prompt, raw repository fixtures, a consequential failure path, and a verifiable check. Read [Contributing](CONTRIBUTING.md) for repository invariants and validation rules, [Security](SECURITY.md) for vulnerability reporting and trust boundaries, [Behavioral evaluation cases](evals/cases.md) for the 8 release scenarios, or the [Comparative evaluation protocol](evals/README.md) to run a blinded comparison.

### Trigger verification prompts

Use these sample prompts (from the 16-query suite in [`evals/trigger-eval.json`](evals/trigger-eval.json)) to smoke-test automatic skill activation against near-miss non-architectural requests:

- **Should trigger (positive):**
  1. `"Write a concise Architecture Decision Record (ADR) choosing between synchronous thumbnail generation inside the 300ms upload API vs. offloading it to our existing worker queue with a 30s freshness SLA, including cost drivers and reconsideration triggers."`
  2. `"Our checkout service calls Stripe synchronously inside the order DB transaction and retries 3x on timeout. Inspect orders/service.py and payments/client.py to prevent duplicate charges and design the minimal outbox and reconciliation boundary."`
  3. `"We have 90-day active v1 mobile clients that only understand pending and completed statuses while v2 needs split shipments. Plan a zero-downtime expand-migrate-contract rollout with a cutover barrier and a safe rollback boundary."`
  4. `"Compare AWS SQS FIFO vs. Azure Service Bus Sessions for strict per-order ordering and 4-day outage replay. Verify current retention, throughput, and message-size limits from official vendor documentation before recommending one."`
  5. `"Run a 45-minute mock system design interview for a multi-region nearby-friends location service at 5M DAU. Push back on my capacity estimates and privacy boundaries, then grade my reasoning at the end."`
- **Should not trigger (near-miss negative):**
  1. `"We are migrating our UI design system from Tailwind v3 CSS variables to v4 @theme tokens. Review components/Button.tsx and styles/tokens.css, update the token mapping, and verify responsive spacing across breakpoints."`
  2. `"Migrate our CI pipeline in .github/workflows/*.yml from actions/checkout@v3 and Ubuntu 20.04 runners to v4 and Ubuntu 24.04, and review any deprecated Node 16 flags in the workflow scripts."`
  3. `"I have a senior engineer behavioral interview tomorrow. Review my STAR stories about a production outage I coordinated last year and help me tighten the 2-minute spoken summary."`
  4. `"Following our already-approved ADR-014 in docs/adr/014.md, implement the GET /v1/invoices pagination endpoint in routes/invoices.py and add unit tests matching our existing repository pattern."`
  5. `"Review this single PostgreSQL reporting query in reports/daily_totals.sql that scans 2M rows and suggest a composite CREATE INDEX with EXPLAIN ANALYZE without changing table ownership or service architecture."`

### Verification commands

Run the verification suite from the repository root (requires Python `3.10+` and Node.js `20+`; CI runs on Python `3.12` and Node.js `24`). After editing files under `skills/system-design-compass/`, sync the workspace mirror under `.agents/skills/system-design-compass/` with `python -B tools/validate_repo.py --fix-mirror`:

```bash
python -B tools/validate_repo.py --fix-mirror
python -B tools/validate_repo.py
python -B -m unittest discover -s tools -p 'test_*.py'
python -m pip install skills-ref==0.1.1
agentskills validate skills/system-design-compass
npx skills@1.5.26 add . --list
git diff --check
```

<details>
<summary><strong>Troubleshooting common setup and validation issues</strong></summary>

| Symptom or error | Cause | Resolution |
|---|---|---|
| `duplicate heading in <file>: <heading>` | `tools/validate_repo.py` enforces case-insensitive unique Markdown headings per file across the repository. | Rename repeated subheadings so every `#` through `######` heading in a single `.md` file is unique. |
| `unfinished placeholder in <file>` | A Markdown file contains bracketed placeholder markers or fix-me tokens. | Replace draft markers with verified prose before running `python -B tools/validate_repo.py`. |
| `broken local link` or `broken markdown anchor` | A relative Markdown link points to a missing file, escapes the repository root, or references a `#anchor` that does not match any heading slug in the target `.md` file. | Verify the target file path and check that the `#anchor` matches the target heading after lowercase and punctuation normalization. |
| `workspace mirror out of sync` or `line endings or bytes differ` | A file under `.agents/skills/system-design-compass/` differs from `skills/system-design-compass/`. | Run `python -B tools/validate_repo.py --fix-mirror` to mirror `skills/system-design-compass/` into `.agents/skills/system-design-compass/` with LF line endings. |
| `agentskills: command not found` | The optional specification validator (`skills-ref`) is not installed in the active Python environment. | Run `python -m pip install skills-ref==0.1.1` (development dependency only; not needed to use the skill). |
| PowerShell multiline `\` syntax error | Bash line continuations (`\`) in documentation examples are pasted directly into Windows PowerShell. | Join multiline arguments onto a single line or replace `\` with the PowerShell backtick (`` ` ``). |

</details>

## Sources and license

The 28-topic archetype catalog was inspired by the topic list in [`liquidslr/system-design-notes`](https://github.com/liquidslr/system-design-notes), which does not declare a redistribution license and notes that its material draws on commercial books. No prose, diagrams, tables, or images from that repository are included here.

All guidance is written independently from engineering first principles and primary sources: [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), [Azure Well-Architected](https://learn.microsoft.com/azure/well-architected/), [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework), [Google SRE Books](https://sre.google/books/), [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html), and the [C4 model](https://c4model.com/).

Original repository content is released under the [MIT License](LICENSE). See [Visual asset specifications](assets/README.md) for logo geometry, color palette, and artwork provenance.
