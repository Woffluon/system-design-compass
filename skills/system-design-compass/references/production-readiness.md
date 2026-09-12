# Production readiness

Use this reference for a full production design, review, or migration. Apply each lens in proportion to the workload's business criticality and lifecycle stage.

## Reliability and recovery

Start from user journeys, SLOs, RTO/RPO, and data-loss impact. Build a dependency budget: a journey cannot be more available or faster than mandatory synchronous dependencies allow without redundancy, caching, degradation, or decoupling.

For every critical path define:

- Deadline and per-hop timeout budget.
- Retry owner, retryable errors, attempt/elapsed-time cap, and jitter.
- Idempotency or reconciliation for ambiguous completion.
- Capacity during a replica/zone loss and during recovery work.
- Isolation boundary for tenants, priorities, and failure domains.
- Degraded behavior and which invariants still hold.
- Detection, mitigation, restoration, and verification.

Evaluate process crash, network delay/partition, dependency failure, saturation, bad input, bad deployment, credential loss, data corruption, operator error, and relevant zone/region loss. Do not add multi-region complexity without a recovery requirement and a tested consistency/failover model.

Backups need stated scope, frequency, retention, encryption, access, restore time, and restore tests. Redundant replicas are not independent backups.

## Observability and operations

Instrument what the user experiences and what operators can act on:

- Request/event volume, success/error ratio, latency distributions, and saturation.
- Queue age, lag, retries, drops, reconciliation discrepancies, and freshness.
- Dependency health and budget consumption.
- Business invariants such as accepted-versus-completed work or ledger imbalance.
- Deploy version, region/zone, tenant/cohort, and correlation context.

Use structured logs for investigation, metrics for trends and alerting, and traces for cross-boundary causality. Control label cardinality and sensitive data.

Alerts should identify a user-impacting or imminent condition, have an owner and response, and avoid paging on symptoms that require no action. Prefer SLO burn or durable invariant violation over raw component noise. Provide dashboards for launch, steady state, capacity, and recovery.

Record operational ownership, escalation, runbooks for high-risk actions, access needed during incidents, dependency contacts, and post-incident learning. Automate common safe actions but preserve auditability and stop conditions.

## Security, privacy, and abuse resistance

Classify data and identify actors, assets, trust boundaries, entry points, privileged operations, and third parties. Threat-model the actual data flows:

1. Decompose the system and trust boundaries.
2. Identify threats such as spoofing, tampering, repudiation gaps, information disclosure, denial of service, and privilege escalation.
3. Rank by plausible likelihood and business impact.
4. Select preventive, detective, and recovery controls; name residual risk and validation.

Cover identity proof, authentication, authorization at the resource, tenant isolation, service identity, secret/key lifecycle, encryption in transit/at rest, audit events, dependency provenance, input validation, egress, administrative paths, and incident response.

Apply data minimization, purpose limitation, retention/deletion, residency, export, consent, and subject-access requirements only as relevant. Do not invent compliance claims. Map supplied obligations to concrete data flows, controls, evidence, and owners.

Consider abuse separately from unauthorized access: quota evasion, scraping, spam, fraud, resource exhaustion, amplification, poisoning, and malicious tenants may use valid credentials. Define detection, rate limits, friction, appeals, and safe failure behavior.

## Performance and capacity

Set latency budgets by journey and payload class. Locate serial work, fan-out, contention, cache misses, data scans, serialization, network crossings, and cold starts. Optimize after a model or measurement identifies the limiting resource.

Capacity plans should include normal peak, forecast growth, loss of a failure domain, deployment overlap, background maintenance, and recovery. State autoscaling signal, delay, minimum/maximum, warm-up, and behavior at the cap. Autoscaling does not replace admission control.

Define load, stress, soak, spike, and failover tests where material. Production-like data shape and key skew often matter more than aggregate request count.

## Cost and sustainability

Model dominant units rather than a single monthly total:

- Requests, compute time, provisioned idle baseline, and accelerators.
- Stored bytes including replicas, indexes, versions, logs, and backups.
- Ingest, query scans, message operations, and retained streams.
- Cross-zone/region/provider transfer and internet egress.
- Licenses, support, and human operational load.

Relate cost to a business unit such as active tenant, completed job, stored object, or transaction. Show fixed versus variable costs, low/base/high scenarios, and thresholds that change the architecture.

Reduce waste by matching retention and redundancy to requirements, batching appropriate work, scaling idle resources, using efficient data layouts, and deleting unused copies. Sustainability usually improves with utilization and reduced transfer/storage, but reliability and regulatory obligations may justify redundancy; record the trade-off.

## Delivery and launch

Define the smallest independently verifiable slices. For each rollout phase state cohort, compatibility, success metrics, observation window, abort threshold, rollback, and owner. Use flags, canaries, shadowing, or cells only when they reduce a named risk.

Before broad launch confirm:

- Critical journeys and invariants have tests.
- Capacity and failure tests cover expected peaks and loss scenarios.
- Dashboards, alerts, traces, runbooks, and ownership exist.
- Restore, rollback, and reconciliation have been exercised.
- Access, secrets, audit, retention, and deletion controls are verified.
- Cost limits and anomaly detection are configured where appropriate.
- Known risks have owners, deadlines, or explicit acceptance.

Production readiness is an evidence-backed decision. A checklist with unverified boxes is not evidence.

## Primary references

This guidance is independently synthesized from public engineering practices including [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html), [Azure Well-Architected](https://learn.microsoft.com/azure/well-architected/), [Google Cloud Well-Architected](https://cloud.google.com/architecture/framework), [Google SRE](https://sre.google/books/), and [OWASP threat modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html). Consult current official guidance for regulated or provider-specific decisions.
