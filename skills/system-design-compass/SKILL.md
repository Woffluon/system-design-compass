---
name: system-design-compass
description: Resolve architecture decisions in production system design, reviews, migrations, and scaling. Use for RFCs, ADRs, architecture assessments, migration plans, or system design interviews. Excludes routine implementation without an architectural decision.
license: MIT
metadata:
  author: Woffluon
  version: "1.1.0"
---

# System Design Compass

> Choose the simplest sufficient design, preserve sound decisions and respond in the user's language.

## Route by the unresolved decision

For narrow decisions, use supplied facts and this entrypoint. Read references only for a missing decision-changing guarantee, not supplied facts or familiar formats.

An ADR explains latency/isolation, visible completion, retry safety, operating cost/effort and a measurable reconsideration trigger, including reused infrastructure. Label proposed thresholds.

Broad work: open [design](references/design.md), [review](references/review.md), [evolution](references/evolve.md), or explicitly requested [interview](references/interview.md). Search headings, then decisive sections; avoid bulk reading or unchanged rereads.

Load technical support only for an unresolved boundary:

- SLOs, demand, units: [estimation](references/requirements-estimation.md).
- Authorization, retry identity, atomicity, external outcomes: [interfaces/data](references/interfaces-data.md).
- Provider-backed financial state: read the [resolution mechanism](references/interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction) for statement-to-journal reconciliation and linked refunds/reversals/stuck-intent repair.
- Replication, queues, leases, overload: [distributed systems](references/distributed-systems.md).
- Recovery, security, observability, cost: [production readiness](references/production-readiness.md).
- Unfamiliar formats: [deliverables](references/deliverables-diagrams.md).
- Missing falsification or owned repair: [decision validation](references/decision-validation.md).

Workload-specific unknowns: [platform](references/archetypes-foundations-platform.md), [realtime](references/archetypes-user-facing-realtime.md), [infrastructure](references/archetypes-data-infrastructure.md), [transactional](references/archetypes-transactional-financial.md).

## Break the proposal before committing

Deepen for conflicting evidence, unexplained guarantees, unclear atomicity, missing discriminating facts or stalled reasoning:

1. Narrow the decision; name the invariant and authoritative owner.
2. Construct an event sequence that could violate it: concurrency, crash, timeout, stale owner or incompatible write.
3. Gather evidence or an experiment separating credible options, including the simple baseline.
4. State the mechanism, enforcement boundary, downside and reconsideration trigger.

Apply these proofs to uncertain/changed correctness guarantees, even in narrow work; property names are insufficient:

- Sensitive state: actor/resource authorization, retry identity within its issuer's contract, atomic effect/result. Caller keys cannot become tenant-wide identities. Resolve external ambiguity, reconciliation and recovery.
- Ownership transfer: resolve admitted writes before capture; progress means durable apply. Drill old-code/client reads **and writes**. Any unreplicated target write can break fallback before irreversible feature effects.
- Ambiguity/backlog: repair owner, intervention condition and action; exhaustion is not completion.

Such guarantees require a concrete fault schedule and observable business pass/fail oracle; a counterexample alone is not validation. Queue capacity derives burst volume and retry/duplicate demand from supplied inputs; unknown throughput stays a variable requiring measurement. Test burst, worker loss and recovery. Migration tests restart/repair and mixed-version reads/writes. No mandatory visible template.

## Evidence discipline

Inspect artifacts before asking discoverable questions. Separate facts, assumptions and unknowns; missing evidence is not a defect. Tool-check arithmetic, units, scenario ranges and required versus executed work. Reconcile diagrams/estimates. Fetch primary sources for uncertain guarantees/limits; citations alone are insufficient. Disclose unavailable tools.

Stop research producing no new evidence or approach; state the missing experiment, information or user decision. Application/external changes require an implementation request.
