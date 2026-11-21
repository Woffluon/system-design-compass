---
name: system-design-compass
description: Resolves architecture decisions for new or production system design, code-backed reviews, zero-downtime migrations, and scaling. Use when asked to write an RFC or decision record (ADR), compare async queues vs. sync calls, design idempotency, payment/ledger or lease boundaries, plan cutover/rollback phases, review reliability/tail-latency risks, or run a system design interview. Excludes routine coding, UI/UX design systems, local refactoring, CI/tooling bumps, or pure SQL/algorithm tuning without an architectural boundary.
license: MIT
metadata:
  author: Woffluon
  version: "1.2.0"
---

# System Design Compass

> Simplest sufficient design; preserve sound decisions; respond in user's language while keeping canonical engineering terms clear.

## When not to use

Skip for single-file bug fixes, UI/CSS, syntax, CI bumps, or settled CRUD; answer directly.

## Route by the unresolved decision

Narrow decisions (default ADR, ~200–400 words): use supplied facts; open references only for missing guarantees. Record latency/isolation, completion, retry safety, cost, `Proposed` triggers.

Broad/mixed work: **Review -> Design -> Evolve** via [review](references/review.md), [design](references/design.md), [evolution](references/evolve.md), or [interview](references/interview.md). Scan `##` headings first; read matching sections (>50% for full read):

- Demand/SLOs: [estimation](references/requirements-estimation.md); readiness: [production readiness](references/production-readiness.md).
- Auth, retry, external outcomes: [interfaces/data](references/interfaces-data.md) ([auth](references/interfaces-data.md#authorization-is-part-of-the-state-boundary), [reconcile](references/interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction)).
- Queues/overload: [distributed systems](references/distributed-systems.md#backlog-drain-capacity-and-age-triggered-intervention); drills: [decision validation](references/decision-validation.md#migration-restart-repair-and-mixed-version-drills).
- Full RFC/review/migration/diagram formats (skip for narrow ADRs): [deliverables](references/deliverables-diagrams.md).
- Workloads: [platform](references/archetypes-foundations-platform.md) (scale, limit, hash, KV, IDs), [realtime](references/archetypes-user-facing-realtime.md) (feed, chat, notify, search, video, sync, geo/nearby), [infrastructure](references/archetypes-data-infrastructure.md) (queues, metrics, clicks, email, object), [transactional](references/archetypes-transactional-financial.md) (reserve, rank, pay, wallet, exchange).

## Break the proposal before committing

1. Narrow decision; name invariant and authoritative owner.
2. Build violating sequence (race, crash-after-effect, timeout, stale owner, conflict).
3. Compare options vs. baseline with evidence.
4. State mechanism, boundary, downside, trigger.
5. Add fault schedule + pass/fail oracle (queues: burst/loss/drain; side effects: crash/timeout/overlap; migrations: restart/repair, mixed-version reads/writes), because names leave bugs untested.

- Sensitive state: enforce auth + scoped retry ID before mutating/returning (avoids collisions); reconcile external outcomes.
- Ownership: drain admitted writes and drill old reads/writes before irreversible effects; gate contraction on zero legacy traffic, not dates (avoids split corruption).
- Backlog: size completion > arrivals + retries with owned repair (storage/exhaustion never drains).

## Evidence and pre-output check

Inspect user code/schemas/config/docs before asking (exclude harness/skill metadata); trust running code over docs and report mismatches. Ask <=3 questions only for missing boundary facts; without interaction, use labeled `[Assumption]`s/unknowns (omit on complete narrow inputs).

Tool-check math; verify limits via primary docs—if offline/failing, mark `[Unverified — requires primary doc check]`, avoid guessing quotas/TTLs, list claims to verify. Reply in chat unless asked for a file; cite user artifacts/primary sources, never skill paths.

Pre-output check (fix gaps): (1) math/units match, gaps labeled unknown; (2) thresholds `Proposed`, guarantees state owner, violating sequence, fault schedule, oracle, trigger; (3) no skill paths or unverified limits.
