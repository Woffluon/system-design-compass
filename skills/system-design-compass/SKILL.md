---
name: system-design-compass
description: Design, review, and evolve production software systems through explicit requirements, capacity estimates, interfaces, data models, trade-offs, reliability, security, operability, cost, and rollout decisions. Use for architecture docs, RFCs, ADRs, architecture reviews, migration plans, scaling questions, or system design interviews. Do not use for routine code implementation that has no architectural decision.
license: MIT
metadata:
  author: Woffluon
  version: "1.0.0"
---

# System Design Compass

Guide architecture work from an ambiguous problem to a justified, operable decision. Prefer the simplest design that satisfies the stated constraints. The user's instructions and existing project decisions take precedence over this skill.

## Select the mode

Read exactly one mode guide first:

- New or substantially redesigned system: [design workflow](references/design.md).
- Assessment of an existing design or repository: [review workflow](references/review.md).
- Migration, scaling transition, or replacement: [evolution workflow](references/evolve.md).
- Time-boxed interview practice: [interview workflow](references/interview.md).

Then load only the references that affect the task:

- Requirements, SLOs, or quantitative sizing: [requirements and estimation](references/requirements-estimation.md).
- APIs, events, schemas, ownership, or data lifecycle: [interfaces and data](references/interfaces-data.md).
- Replication, partitioning, caching, queues, concurrency, or distributed coordination: [distributed systems patterns](references/distributed-systems.md).
- Reliability, observability, security, privacy, cost, sustainability, and launch readiness: [production readiness](references/production-readiness.md).
- RFC, ADR, review, migration-plan, or diagram output: [deliverables and diagrams](references/deliverables-diagrams.md).

For a familiar workload, load at most one archetype catalog initially; load another only when the system genuinely spans domains:

- Scaling, rate limiting, hashing, key-value storage, and identifiers: [foundations and platform](references/archetypes-foundations-platform.md).
- URL shortening, crawling, notifications, feeds, chat, autocomplete, video, file sync, and geo: [user-facing and realtime](references/archetypes-user-facing-realtime.md).
- Queues, monitoring, aggregation, email, and object storage: [data and infrastructure](references/archetypes-data-infrastructure.md).
- Reservations, leaderboards, payments, wallets, and exchanges: [transactional and financial](references/archetypes-transactional-financial.md).

## Shared operating rules

1. Inspect available repository, architecture, and operational evidence before asking for information that is already discoverable.
2. Ask one concise batch of questions only when missing answers could change system boundaries, correctness, criticality, or the primary technology class. Otherwise proceed with explicit assumptions.
3. Separate `Facts`, `Assumptions`, `Decisions`, and `Open questions`. Give confidence or a validation method for material assumptions.
4. Quantify important scale claims. Show units, formulas, peak factors, retention, replication overhead, and ranges; do not imply precision unsupported by inputs.
5. Define invariants and failure behavior before selecting products. Separate logical capabilities from vendor services.
6. Compare credible options against the prioritized requirements. Record why the chosen option wins and what would trigger reconsideration.
7. Cover degraded behavior, recovery, security boundaries, observability, ownership, cost drivers, rollout, and rollback—not only the happy path.
8. Match the requested artifact. Use a short ADR for a narrow decision and a full design document only when the scope warrants it.
9. Use the user's language for the response unless asked otherwise. Keep identifiers, protocols, and established technical terms precise.
10. Produce architecture and an implementation-ready plan. Do not modify application code or external systems unless the user separately asks for implementation.

## Product and evidence policy

Remain vendor-neutral by default. When the existing stack fixes a vendor, or the user requests a current product comparison, consult current official product documentation if browsing is available. Distinguish documented facts from inference, cite the decisive sources, and avoid version-sensitive claims that cannot be verified.

For reviews, attach every finding to repository evidence, an architecture artifact, telemetry, or an explicit assumption. Absence of evidence is an unknown, not proof of a defect.

## Completion check

Before finishing, confirm that the result answers the business goal, exposes consequential trade-offs, names the critical invariants, makes scale assumptions auditable, covers failure and recovery, and leaves implementation decisions only where the user intentionally deferred them.
