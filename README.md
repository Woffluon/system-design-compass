# System Design Compass

### Architecture decisions that survive the failure path.

![A precision compass on a navy architectural map, with a copper route connecting the chosen system boundaries.](assets/system-design-compass-hero.png)

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-172b3a)](https://agentskills.io)
[![Status](https://img.shields.io/badge/status-research_preview-c47a3b)](evals/results/2026-09-30.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-172b3a)](LICENSE)

Give your coding agent a better way to reason about **system design, architecture reviews and safe migrations**. Start with the decision, find the invariant, challenge the failure path, and collect the evidence that separates credible options.

**Small entrypoint. Guidance on demand. No runtime dependencies.**

[Get started](#get-started) · [See the decision lens](#a-better-question-changes-the-design) · [Browse the guides](#find-the-right-guide) · [Read the evidence](#measured-results-and-current-limits)

> **Research preview · `1.1.0-rc.1`**
>
> The complete two-model acceptance gate is still open. Tested improvements, excluded runs and remaining failures are published—not hidden behind a benchmark badge.

## A better question changes the design

Architecture advice becomes useful when it explains **where a guarantee is enforced** and **what would disprove it**.

| Familiar advice | The decision worth resolving |
|---|---|
| “Add idempotency.” | What identifies the operation, where are effect and result committed, and what happens after a crash? |
| “Use a queue.” | Does completion capacity exceed retry-amplified demand after worker loss, and who acts when age rises? |
| “Roll back the deployment.” | Can old code still read new data, and which external effects are irreversible? |
| “Shard for scale.” | Which measured bottleneck requires it, and does the key distribute real traffic? |
| “Modernize the architecture.” | What is actually broken—and which sound decisions should remain? |

Three useful reminders to take into a design review:

> A timeout is an unknown outcome.
>
> Queue storage is not recovery capacity.
>
> Restoring old binaries does not undo incompatible writes.

These are prompts for investigation, not substitutes for evidence.

## Get started

Install from the repository with the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add Woffluon/system-design-compass
```

From a local checkout, run this at the repository root:

```bash
npx skills add .
```

Invoke the skill explicitly when your agent supports named skills:

```text
$system-design-compass Review this service's retry and timeout boundaries.
Use repository evidence. Preserve sound decisions. Give the smallest
correction and one experiment that could falsify the recommendation.
```

<details>
<summary><strong>Global installation and selected agents</strong></summary>

Install globally:

```bash
npx skills add Woffluon/system-design-compass --global
```

Select agents without an interactive prompt:

```bash
npx skills add Woffluon/system-design-compass \
  --skill system-design-compass \
  --agent claude-code codex cursor gemini-cli github-copilot opencode \
  --global --yes
```

The CLI handles each agent's installation path. Available tools and automatic skill selection depend on the harness.

</details>

## Bring a decision, not a technology shopping list

| Work | Example request | Useful result |
|---|---|---|
| **Design** | “Design delivery semantics for customer webhook endpoints.” | Ownership, contracts, credible options and explicit failure guarantees. |
| **Review** | “Assess this architecture's tail-latency and retry risks.” | Evidence, trigger, impact, smallest correction and validation. |
| **Evolve** | “Move this database while writers and old clients remain active.” | Phase authority, convergence evidence and rollback boundaries. |
| **Decide narrowly** | “Write an ADR for asynchronous thumbnail rendering.” | One scoped decision; no mandatory full RFC. |
| **Practice** | “Run a 45-minute system design interview for autocomplete.” | Focused reasoning, deep dives and concrete feedback. |

Supply the artifacts you have: code, schemas, configuration, SLOs, incident records or existing ADRs. Unknowns should remain visible. The response follows your language; the maintained guidance is English.

Natural-language requests can activate the skill in harnesses that discover skills automatically. Automatic activation has not been established by the current evaluation.

## Find the right guide

The [entrypoint](skills/system-design-compass/SKILL.md) routes by the decision at hand. A narrow question can be answered directly; broader work loads the relevant mode, then only the references needed to resolve it.

| Decision area | Read when |
|---|---|
| [Design](skills/system-design-compass/references/design.md) · [Review](skills/system-design-compass/references/review.md) · [Evolution](skills/system-design-compass/references/evolve.md) | The task needs a broader workflow. |
| [Requirements and estimation](skills/system-design-compass/references/requirements-estimation.md) | SLOs, demand, units or capacity change the choice. |
| [Interfaces and data](skills/system-design-compass/references/interfaces-data.md) | Ownership, identity, contracts or consistency need definition. |
| [Distributed systems](skills/system-design-compass/references/distributed-systems.md) | Queues, leases, replication, placement or overload affect guarantees. |
| [Production readiness](skills/system-design-compass/references/production-readiness.md) | Recovery, security, observability, cost or launch evidence matters. |
| [Decision validation](skills/system-design-compass/references/decision-validation.md) | A plausible mechanism lacks a falsifiable experiment or owned repair. |
| [Deliverables and diagrams](skills/system-design-compass/references/deliverables-diagrams.md) | The requested audience needs an ADR, RFC, phase plan or diagram. |
| [Interview](skills/system-design-compass/references/interview.md) | Interview practice is explicitly requested. |

**28 workload topics**, organized into four selective catalogs:

| Catalog | Examples |
|---|---|
| [Foundations and platform](skills/system-design-compass/references/archetypes-foundations-platform.md) | Scaling, estimation, rate limiting, hashing, key-value stores, IDs. |
| [User-facing and realtime](skills/system-design-compass/references/archetypes-user-facing-realtime.md) | Feeds, chat, autocomplete, video, file sync, maps, proximity. |
| [Data and infrastructure](skills/system-design-compass/references/archetypes-data-infrastructure.md) | Queues, metrics, aggregation, email, object storage. |
| [Transactional and financial](skills/system-design-compass/references/archetypes-transactional-financial.md) | Reservations, leaderboards, payments, wallets, matching. |

Catalogs expose questions and failure cases; they are not prebuilt architectures or a prescribed vendor stack.

## Measured results and current limits

The [2026-09-30 evaluation](evals/results/2026-09-30.md) tested `gpt-5.6-sol` and `gpt-5.6-luna` at medium reasoning using authored cases and frozen snapshots.

| Observation | What the evidence supports |
|---|---|
| **594 → 448 entrypoint words** | The evaluated candidate's entrypoint was 24.6% smaller. |
| **Repeated queue-recovery correction** | The strong model added actionable recovery validation; two clean confirmations preserved the result. |
| **3,372 → 448 read words in a narrow ADR** | The strong model's observed skill-read proxy fell 86.7% in this paired case. This is not a token or universal savings claim. |
| **Acceptance remains open** | Smaller-model coverage is incomplete; provider verification and narrow-ADR completeness still have failures. |

The evaluation recorded 138 attempts plus nine earlier preflights. Thirty-six protocol failures and 16 contaminated subjects were excluded. Raw trace proxies, real CLI token totals, blinded grades and conservative artifact reviews are reported separately.

Subsequent documentation formatting does not constitute a new behavioral evaluation. Historical scores and hashes refer to the evaluated snapshots.

## Portable by construction

The distributed folder follows the [Agent Skills specification](https://agentskills.io/specification): Markdown references and optional agent UI metadata, with **no runtime scripts, MCP requirements, credentials or network dependency**. Standards-compatible harnesses can load it; tools and permission enforcement remain the harness's responsibility.

Repository evaluation utilities are development tooling, not part of the skill's runtime. The cover image is also outside the distributable folder.

## Contribute a failure worth catching

A useful contribution starts with an anonymized prompt, raw evidence, a consequential failure and a verifiable outcome. If this helps surface a problem before production, share the decision and the smallest reproducible case.

Read [Contributing](CONTRIBUTING.md) for content rules and checks, [Security](SECURITY.md) for private reporting, or the [evaluation protocol](evals/README.md) to reproduce a comparison. The original [behavioral cases](evals/cases.md) describe the release expectations.

<details>
<summary><strong>Development checks</strong></summary>

```bash
python tools/validate_repo.py
python -m unittest discover -s tools -p 'test_*.py'
python -m pip install skills-ref==0.1.1
agentskills validate skills/system-design-compass
npx skills@1.5.26 add . --list
```

The specification validator is a development dependency. These checks establish repository and format integrity; behavioral acceptance needs the separate evaluation protocol.

</details>

## Sources and license

The topic map was inspired by [`liquidslr/system-design-notes`](https://github.com/liquidslr/system-design-notes). It does not declare a redistribution license and states its notes draw on commercial books. No prose, diagrams, tables or images from it are included here.

Guidance is independently written from engineering principles and primary sources: [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), [Azure Well-Architected](https://learn.microsoft.com/azure/well-architected/), [Google Cloud Well-Architected](https://cloud.google.com/architecture/framework), [Google SRE](https://sre.google/books/), [OWASP threat modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) and [C4](https://c4model.com/).

Original repository content is [MIT licensed](LICENSE). [Cover provenance and generation prompt](assets/README.md) are recorded alongside the asset.
