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

For narrow decisions, use supplied facts and this entrypoint. Read references only for missing decision-changing guarantees.

An ADR records latency/isolation, visible completion, retry safety, cost, and reconsideration triggers. Label proposed thresholds.

Broad work: open [design](references/design.md), [review](references/review.md), [evolution](references/evolve.md), or requested [interview](references/interview.md). Search decisive sections; avoid bulk rereads.

Unresolved boundary references:

- SLOs, demand, units: [estimation](references/requirements-estimation.md).
- Authorization, retry identity, atomicity, external outcomes: [interfaces/data](references/interfaces-data.md).
- Provider-backed financial state: read the [resolution mechanism](references/interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction) for reconciliation and stuck-intent repair.
- Replication, queues, leases, overload: [distributed systems](references/distributed-systems.md).
- Recovery, security, observability, cost: [production readiness](references/production-readiness.md).
- Formats: [deliverables](references/deliverables-diagrams.md).
- Falsification, repair: [decision validation](references/decision-validation.md).

Workload unknowns: [platform](references/archetypes-foundations-platform.md), [realtime](references/archetypes-user-facing-realtime.md), [infrastructure](references/archetypes-data-infrastructure.md), [transactional](references/archetypes-transactional-financial.md).

## Break the proposal before committing

Deepen for conflicting evidence, unexplained guarantees, unclear atomicity, or stalled reasoning:

1. Narrow the decision; name the invariant and authoritative owner.
2. Construct a violating event sequence: concurrency, crash, timeout, stale owner, or conflicting write.
3. Compare credible options against the simple baseline with evidence.
4. State mechanism, enforcement boundary, downside, and reconsideration trigger.

Apply proofs to uncertain correctness guarantees; property names are insufficient:

- Sensitive state: actor/resource authorization, retry identity within issuer contract, atomic effect/result. Caller keys cannot become tenant-wide identities. Resolve external ambiguity and recovery.
- Ownership transfer: resolve admitted writes before capture; progress means durable apply. Drill old-code reads **and writes**. Unreplicated writes break fallback before irreversible feature effects.
- Ambiguity/backlog: repair owner, intervention condition, and action; exhaustion is not completion.

Guarantees require a concrete fault schedule and observable pass/fail oracle; counterexamples are not validation. Queue burst/retry capacity variables derive from inputs; unknown throughput requires measurement. Test burst, worker loss, and recovery. Migration tests restart/repair and mixed-version reads/writes.

## Evidence discipline

Inspect artifacts before asking discoverable questions. Separate facts, assumptions, and unknowns; missing evidence is not a defect. Tool-check arithmetic, units, scenarios, and executed work. Reconcile diagrams with estimates. Primary sources verify uncertain limits; citations are insufficient. Disclose unavailable tools.

Stop research yielding no new evidence; state missing experiments, data, or decisions. External changes require an implementation request.
