# Architecture review workflow

> Assess a repository, design document, deployed system, or proposal for decision support rather than a generic checklist.

## Rank evidence and separate unknowns from defects

Define the review question, criticality, lifecycle stage, and evidence. Rank sources in order:

1. Executable code, configuration, schema, infrastructure, and tests.
2. Production telemetry, incidents, capacity data, and runbooks.
3. Architecture and decision documents.
4. Stakeholder statements.
5. Explicit reviewer assumptions.

Report source conflicts directly. Separate demonstrated facts, conditional assumptions, and explicit unknowns. Never treat a stale diagram as implementation truth, and **never report missing evidence or absent documentation as a fabricated defect**—classify it as an explicit unknown or conditional assumption.

## Trace critical paths and authoritative state owners

In large repositories (`500+` files), start with scoped search (`rg`) targeting entrypoints, schemas, retry/client wrappers, and deployment config rather than reading every file. Map the minimum flows answering the review question:

- External request from entry point to response.
- State mutation through persistence, authoritative ownership, and downstream effects.
- Asynchronous work through ack, retry, and terminal repair or dead-letter handling.
- Authentication to resource-level authorization at the enforcement boundary.
- Deployment, health gate, and rollback boundary.

Identify trust boundaries, **authoritative state owner** per entity, synchronous dependency depth, queues, caches, consistency boundaries, shared failure domains, and tenant/regional isolation.

## Evaluate consequential risks with violating event sequences

Apply only lenses matching criticality, stage, and constraints:

| Lens | Risk to examine |
|---|---|
| **Correctness** | invariants, authoritative state owner, concurrency, ordering, idempotency, reconciliation. |
| **Reliability** | SLO feasibility, dependency budgets, overload shedding, isolation, redundancy, recovery. |
| **Performance** | critical-path latency, fan-out, contention, hot keys, retry amplification, payload size, headroom. |
| **Security and privacy** | actor/resource authorization, secrets, trust boundaries, classification, retention, abuse, auditability. |
| **Data** | ownership, schema evolution, consistency, retention/deletion, backup restore, migration safety. |
| **Delivery** | coupling, mixed-version compatibility, testability, observability, rollout gates, rollback blast radius. |
| **Cost and sustainability** | dominant unit costs, idle baseline, growth multipliers, egress, retention, waste. |
| **Complexity** | components or abstractions not justified over a simpler baseline. |

Before declaring a correctness or reliability defect, construct the **violating event sequence** (race, crash, timeout, stale owner, or partial write) breaking the invariant.

## Pair each finding with the smallest surgical fix and a falsifiable experiment

Every finding requires:

| Field | Required content |
|---|---|
| **Title** | concrete failure mode or decision gap, not a category label. |
| **Priority** | `P0` imminent catastrophic exposure, `P1` high-impact blocker, `P2` material schedulable risk, `P3` minor improvement. |
| **Evidence** | file/line, artifact section, metric, incident, or labeled conditional assumption. |
| **Trigger** | violating event sequence, fault, or load condition producing the failure. |
| **Impact** | affected invariant, journey, SLO, security property, cost, or RTO/RPO. |
| **Recommendation** | **the smallest surgical fix** removing or bounding the risk without unnecessary components. |
| **Validation** | **a falsifiable experiment**—fault schedule, concurrency test, query, or load check with a pass/fail oracle. |

Consolidate findings sharing a root cause. Distinguish demonstrated defects from conditional risks and open unknowns. For narrow single-boundary reviews, report only applicable fields and omit unused template boilerplate.

- **Weak:** "Title: Retry bug. Fix: Introduce Temporal workflow. Validation: Add unit tests."
- **Surgical:** "Title: Post-charge crash duplicates Stripe debits (`orders/pay.py:42`). Fix: Persist `IN_FLIGHT` intent + deterministic `idempotency_key` before HTTP call. Validation: Drop socket after PSP `200 OK`, retry 3x; pass iff PSP charges = 1 and local postings = 1."

## Deliver a verdict that preserves sound decisions

Summarize:

- Current fitness for the stated goal, load, and constraints.
- **Sound existing decisions and simple boundaries to preserve**, protecting working components from churn.
- Blocking (`P0`/`P1`) risks and minimum surgical pre-launch or pre-migration fixes.
- Non-blocking follow-ups ordered by risk reduction per unit effort.
- Explicit unknowns and conditional assumptions requiring telemetry, stakeholder input, or falsifiable experiments.

When no actionable defect exists, state the design is sound and cite reviewed evidence. Never manufacture findings.

## Completion gate

A review is ready when every finding cites verified artifacts or labeled assumptions, every correctness/reliability defect includes a violating event sequence, each fix is the smallest surgical change with a pass/fail oracle, sound decisions are explicitly preserved, and missing documentation is labeled unknown rather than reported as a defect.
