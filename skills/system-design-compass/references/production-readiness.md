# Production readiness

> Use for production design, review, or migration in proportion to business criticality and lifecycle stage.

## Reliability and recovery

Anchor on user journeys, SLOs, RTO/RPO, and data-loss impact. A journey cannot exceed the availability or latency of its mandatory synchronous dependencies without redundancy, caching, degradation, or decoupling.

For every critical path specify:

- End-to-end deadline and per-hop timeout budget.
- Retry owner, retryable conditions, attempt/elapsed-time cap, and jitter.
- Ambiguous-completion handling: idempotency key, outcome query, or reconciliation with an owned repair path on retry exhaustion.
- Capacity during replica/zone loss and subsequent recovery load.
- Tenant, priority, and failure-domain isolation boundaries.
- Degraded mode and invariants that remain enforced.
- Quantitative intervention thresholds (circuit breaking, load shedding, failover) with detection, mitigation, restoration, and verification steps.

Evaluate process crash, network delay/partition, dependency failure, saturation, poison input, bad deployment, credential expiry, data corruption, operator error, and zone/region loss. Add multi-region active/active or failover only when RTO/RPO justifies the consistency and operational cost.

Backups require stated scope, RPO frequency, retention, encryption, access control, restore duration, and scheduled restore drills. **Redundant replicas are not independent backups.**

## Observability and operations

Instrument user-visible outcomes and operator decision signals:

- Request/event rate, success/error ratio, latency percentiles, and resource saturation.
- **Oldest uncompleted business backlog age**, queue lag, retry amplification, dropped work, reconciliation drift, and data freshness.
- Exhausted attempts / dead-letter arrivals awaiting owned repair.
- Dependency health, timeout rate, and error-budget burn.
- Business invariants (accepted versus completed work, ledger balance, reservation parity).
- Version, region/zone, tenant/cohort, and trace correlation IDs.

Use structured logs for diagnosis, bounded-cardinality metrics for trends and alerting, and distributed traces for cross-boundary latency and causality. Redact secrets and personal data at emission.

Every alert requires a user-impacting or invariant-violating condition, a **quantitative intervention threshold** (label proposed values), a named owner, and a bounded runbook action:

- Page on SLO burn, durable invariant drift, **uncompleted business backlog age exceeding the completion budget**, or **exhausted attempts accumulating without repair**.
- Never treat dead-letter enqueue or retry exhaustion as completed business work.
- Pair high-risk runbooks and automated mitigations with explicit stop conditions and audit trails.

## Security, privacy, and abuse resistance

Classify data and map actors, assets, trust boundaries, entry points, privileged actions, and third parties. Threat-model actual flows:

1. Decompose components and trust boundaries, then rank threats by likelihood and business impact.
2. Bind preventive, detective, and recovery controls to each high-risk path; record residual risk and verification tests.

Enforce resource-level authorization, tenant isolation, workload identity, secret rotation, encryption in transit/at rest, immutable audit logs, input validation, egress control, and break-glass auditing across boundaries.

Map supplied privacy or regulatory obligations (minimization, retention/deletion, residency, export, subject access) to concrete stores, flows, evidence, and owners without inventing compliance certifications.

Model abuse separately from unauthenticated access: valid credentials can still drive quota evasion, scraping, spam, fraud, amplification, poisoning, or noisy-neighbor exhaustion. Specify detection thresholds, rate/cost limits, progressive friction, quarantine, and appeals.

## Performance and capacity

Budget latency by journey and payload class. Identify serial hops, fan-out, lock contention, cache misses, unindexed scans, serialization overhead, cross-zone calls, and cold starts; optimize the measured bottleneck.

Size capacity for baseline peak, growth forecast, failure-domain loss, deployment overlap, compaction/maintenance, and backlog drain after outage. Specify autoscaling signal, reaction lag, min/max bounds, warm-up time, and behavior at cap. **Autoscaling does not replace admission control or backpressure.**

Validate with load, stress, soak, spike, and failover tests using production-like payload sizes and hot-key skew.

## Cost and sustainability

Model dominant unit drivers rather than a single monthly total:

- Compute/request execution, provisioned baseline, and accelerators.
- Storage bytes across primary, replicas, indexes, snapshots, logs, and backups.
- Ingest, scan volume, queue/message operations, and stream retention.
- Cross-zone, cross-region, cross-provider, and internet egress transfer.
- Third-party usage fees and on-call operational toil.

Normalize cost per business unit (active tenant, completed job, transaction, stored GB) across low/base/high scenarios and name the quantitative volume or cost thresholds that trigger architectural change. Match retention, replication, and batching to actual SLO and compliance requirements.

## Delivery and launch

Ship in small, independently verifiable slices. For each rollout phase define cohort, backward/forward compatibility, success metrics, observation window, **quantitative abort/rollback threshold** (labeled when proposed), rollback mechanics, and owner.

Before broad launch verify with evidence:

- Critical journeys, mixed-version compatibility, and business invariants pass automated tests.
- Peak load, failure-domain loss, and backlog-drain recovery meet targets.
- Dashboards, quantitative alerts, runbooks, and repair ownership are live.
- Backup restore, deployment rollback, and state reconciliation drills succeeded.
- Access, secrets, audit, retention, deletion, and cost guardrails are enforced.
- Residual risks have named owners, expiration dates, or explicit sign-off.

**An unexercised checklist is not production readiness evidence.**

## Primary references

Synthesized from public engineering guidance including [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html), [Azure Well-Architected](https://learn.microsoft.com/azure/well-architected/), [Google Cloud Well-Architected](https://cloud.google.com/architecture/framework), [Google SRE](https://sre.google/books/), and [OWASP threat modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html). Consult current official standards for regulated workloads.
