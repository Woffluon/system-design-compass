# System Design Compass

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827)](https://agentskills.io)
[![Install with skills](https://img.shields.io/badge/install-npx%20skills%20add-0ea5e9)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

System Design Compass is a vendor-neutral Agent Skill for designing, reviewing, and evolving production software systems. It turns vague architecture requests into explicit requirements, auditable estimates, reasoned decisions, failure-aware designs, and safe rollout plans.

The skill is production-first. It also includes a compact, time-boxed system design interview mode.

## Install

Install interactively into any agent detected by the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add Woffluon/system-design-compass
```

Install globally:

```bash
npx skills add Woffluon/system-design-compass --global
```

Install non-interactively into selected agents:

```bash
npx skills add Woffluon/system-design-compass \
  --skill system-design-compass \
  --agent claude-code codex cursor gemini-cli github-copilot opencode \
  --global --yes
```

Before the GitHub repository is published, install from a local checkout:

```bash
npx skills add ./system-design-compass
```

## Use

Invoke it explicitly when the harness supports named skills:

```text
$system-design-compass design a multi-tenant webhook delivery platform.
$system-design-compass review this repository's architecture for reliability risks.
$system-design-compass plan a zero-downtime migration from the current database.
```

Natural-language activation also works in harnesses that discover skills automatically:

```text
Write an ADR comparing queue-backed and synchronous processing for this workflow.
Review this service's data ownership, failure modes, and scaling limits.
Run a 45-minute system design interview for a nearby-friends product.
```

## What it covers

- Greenfield and redesign workflows, architecture reviews, and evolutionary migrations.
- Functional requirements, quality attributes, SLI/SLO selection, and capacity estimation.
- APIs, events, schemas, data ownership, consistency, idempotency, and lifecycle decisions.
- Partitioning, replication, caching, messaging, concurrency, and coordination trade-offs.
- Reliability, recovery, observability, security, privacy, abuse resistance, cost, and sustainability.
- Adaptive RFC, ADR, review, migration-plan, and Mermaid/C4-style diagram output.
- Compact workload archetypes spanning all 28 topics in the inspiration repository.

The archetypes are decision prompts, not copy-paste reference architectures. Product recommendations are based on capabilities first; current vendor details must be checked against official documentation.

## Compatibility

The packaged skill follows the open [Agent Skills specification](https://agentskills.io/specification) and has no runtime scripts, MCP requirements, shell assumptions, or vendor-specific frontmatter. It is intended to work with every standards-compatible harness.

The installation path is delegated to the current `skills` CLI, which supports Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo Code, OpenCode, Kiro, Amp, Goose, OpenHands, and many other agents. Compatibility means the harness can discover and load Agent Skills; tool availability still varies by harness.

## Repository layout

```text
skills/system-design-compass/
├── SKILL.md
├── agents/openai.yaml
└── references/
evals/cases.md
tools/validate_repo.py
```

The entrypoint routes to focused references so an agent does not load the entire knowledge base for every request.

## Development

Run the repository checks:

```bash
python tools/validate_repo.py
python C:/Users/Efe/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/system-design-compass
npx skills@1.5.26 add . --list
```

The second command is a Codex maintainer check and is not required for contributors. CI validates the open specification independently.

Behavioral evaluation cases and their invariants live in [`evals/cases.md`](evals/cases.md). They intentionally test decisions rather than exact wording.

## Sources and clean-room policy

The topic map was inspired by [`liquidslr/system-design-notes`](https://github.com/liquidslr/system-design-notes). That repository does not declare a redistribution license and states that its notes are based on commercial books. No prose, diagrams, tables, or images from it are included here.

The guidance in this repository is independently written from generally applicable engineering principles and primary sources, including:

- [Agent Skills specification](https://agentskills.io/specification)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
- [Google Cloud Well-Architected Framework](https://cloud.google.com/architecture/framework)
- [Google Site Reliability Engineering](https://sre.google/books/)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [C4 model](https://c4model.com/)

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding sourced material.

## License

Released under the [MIT License](LICENSE). The license applies only to the original contents of this repository.
