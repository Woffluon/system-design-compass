# Design workflow

> Use this mode for a new system, a major redesign, or a request whose architecture has not been established.

## Establish the decision frame and explicit assumptions

Start with the business outcome, primary readers, delivery horizon, team and operational constraints, platform commitments, and cost of failure.

Inspect supplied repositories and documents before asking questions. Ask a concise batch only for unknowns that change a major boundary or technology class:

- Essential user journeys and explicit non-goals.
- Scale, geography, growth, latency, availability, durability, and RTO/RPO targets.
- Sensitive, regulated, financially material, or irreplaceable data.
- Business invariants for ordering, uniqueness, freshness, and consistency.
- Existing systems, providers, team skills, deadlines, and budgets.

When answers are unavailable, choose conservative reversible assumptions, label them, and state how to validate them. Never invent a compliance regime, exact load, or business-critical guarantee.

## Build the architecture in decision order

### 1. Bound the system and name authoritative state owners

Define actors, external systems, trust boundaries, core journeys, and non-goals. Name the single **authoritative state owner** (system of record) for each critical entity and state transition. Do not decompose into services before ownership and failure boundaries justify it.

### 2. Make quality attributes measurable

Prioritize quality attributes and translate vague terms ("fast," "reliable," "real time") into SLIs, targets, measurement points, windows, and RTO/RPO using [requirements and estimation](requirements-estimation.md).

### 3. Estimate decision-driving demand

Estimate peak read/write/event rates, concurrency, payload size, retention, storage growth, bandwidth, and retry or background amplification. Use ranges for uncertain inputs and **calculate only figures that can change a boundary or technology choice.**

### 4. Define contracts, invariants, and consistency boundaries

Specify commands, queries, events, lifecycle transitions, authorization scope, and idempotency identity. State which transitions require atomic or strong enforcement by the authoritative state owner and where bounded staleness is acceptable. Use [interfaces and data](interfaces-data.md).

### 5. Start from the simplest sufficient baseline

Propose the fewest independently operated components that satisfy current requirements. Specify capabilities before products: routing, durable state, asynchronous work, caching, search, object storage, or stream processing. Commit to one **simple baseline** flow and justify any extra component by a required guarantee, isolation boundary, or measured limit the existing authoritative owner cannot provide—never by speculative scale alone.

Trace at least one write path and one read path end to end across authentication/authorization checks, persistence boundaries, asynchronous handoffs, and client responses.

### 6. Stress-test hard decisions with violating sequences and baseline evidence

For each consequential choice:

1. State the decision, the invariant, the **authoritative state owner**, and the requirement served.
2. Construct a concrete **violating event sequence** (concurrent duplicate requests, crash between local commit and external effect, timeout with ambiguous outcome, stale owner write, or conflicting update) that breaks a naive design.
3. Compare at least two credible options against the **simple baseline** with quantitative or mechanistic evidence across correctness, latency, throughput, availability, recovery, operability, cost, security, and migration impact.
4. Record the chosen mechanism, enforcement boundary, accepted downside, and measurable reconsideration trigger.

Connect every technology choice to a requirement. Never claim horizontal scalability without naming the partition key, coordination point, and state movement behavior.

### 7. Design for failure, overload, and recovery

Walk through dependency timeouts, overload, partial failure, data corruption, zone/region loss, bad deployment, credential compromise, and operator error. Define degraded behavior, retry ownership, backpressure or shedding, repair ownership, observability, and escalation using [production readiness](production-readiness.md).

### 8. Define safe delivery and rollback boundaries

Separate the target architecture from the smallest safe next slice. Specify interface compatibility, data migration, shadow or canary verification, quantitative abort thresholds, and an executable rollback action using [evolution](evolve.md). A feature flag or canary without a verified state and external-effect rollback boundary does not explain recovery from a bad deployment.

## Match deliverable format to decision scope

- **ADR**: one narrow architectural decision.
- **Concise architecture note**: a bounded component or integration.
- **Full RFC**: multiple interfaces, data boundaries, quality attributes, or teams.
- **Decision-complete implementation plan**: execution handoff.

See [deliverables and diagrams](deliverables-diagrams.md) for contracts. Omit sections that do not change a decision; never omit a critical invariant, violating sequence, major risk, or verification method for brevity.

## Completion gate

A design is ready for review when a reader can answer:

- What problem, invariant, and load is this built for?
- Who is the authoritative state owner for each critical entity, and what violating event sequences are prevented?
- Why does this architecture beat the simple baseline or other credible options with evidence?
- What happens during overload, dependency failure, ambiguous external outcomes, and recovery?
- How will the team observe, launch, roll back within safe state boundaries, and pay for it?
- Which labeled assumptions still require experimental or production evidence?
