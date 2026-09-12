# Design workflow

Use this mode for a new system, a major redesign, or a request whose architecture has not been established.

## Establish the decision frame

Start with the business outcome and the decisions the artifact must enable. Identify the primary readers, delivery horizon, team and operational constraints, current platform commitments, and the cost of failure.

Inspect supplied repositories and documents before asking questions. Ask a concise batch only for unknowns that could change a major boundary or technology class, usually:

- Which user journeys are essential and which are explicitly out of scope?
- What scale, geography, growth, latency, availability, durability, and recovery targets matter?
- What data is sensitive, regulated, financially material, or impossible to recreate?
- What ordering, uniqueness, freshness, or consistency guarantees are business invariants?
- Which existing systems, providers, skills, deadlines, or budgets constrain the design?

If answers are unavailable, choose conservative but reversible assumptions, label them, and state how to validate them. Never invent a compliance regime, an exact load, or a business-critical guarantee.

## Build the design in decision order

### 1. Bound the system

Describe actors, external systems, trust boundaries, ownership, core journeys, and non-goals. Name the system of record for each important entity. Avoid decomposing into services before boundaries and ownership justify it.

### 2. Make quality attributes measurable

Prioritize rather than merely list them. Translate words such as "fast," "reliable," and "real time" into indicators, targets, measurement points, and windows. Capture RTO/RPO when recovery matters. Use [requirements and estimation](requirements-estimation.md) for the full method.

### 3. Estimate the shape of demand

Estimate peak read/write/event rates, concurrency, object or message size, retention, storage growth, bandwidth, and background amplification. Use ranges when the inputs are uncertain. Calculate only figures that can influence a decision.

### 4. Define contracts and invariants

Specify the commands, queries, events, data ownership, lifecycle, and idempotency model that make the primary journeys work. State where consistency is required and where staleness is acceptable. Use [interfaces and data](interfaces-data.md).

### 5. Propose the minimum viable architecture

Start with the fewest independently operated components that satisfy the current requirements. Describe capabilities before products: request routing, durable state, asynchronous work, caching, search, object storage, or stream processing. Split components only for a concrete reason such as distinct ownership, scaling, isolation, security, data semantics, or release cadence.

Trace at least one write path and one read path end to end. Include authentication/authorization points, persistence boundaries, asynchronous handoffs, and response behavior.

### 6. Resolve the hard decisions

For each consequential choice:

1. State the decision and the requirement it serves.
2. Compare at least two credible options, including keeping the simpler baseline when credible.
3. Evaluate correctness, latency, throughput, availability, recovery, operability, cost, security, and migration impact as relevant.
4. Record the chosen option, accepted downside, and a measurable reconsideration trigger.

Do not list technologies without connecting them to a requirement. Do not claim horizontal scalability without identifying the partition key, coordination point, and state movement behavior.

### 7. Design for production

Walk through dependency timeout, overload, partial failure, data corruption, region or zone loss when relevant, bad deployment, credential compromise, and operator error. Define degraded behavior, retry ownership, backpressure or shedding, recovery, observability, and escalation. Use [production readiness](production-readiness.md).

### 8. Make delivery safe

Describe implementation slices, interface compatibility, data migration, shadow or canary validation, rollback boundaries, and success metrics. Separate the target architecture from the smallest safe next step.

## Choose the output size

- Use an ADR when one narrow decision is the point.
- Use a concise architecture note for a bounded component or integration.
- Use a full RFC when several interfaces, data boundaries, quality attributes, or teams are involved.
- Use a decision-complete implementation plan when the user needs execution handoff.

See [deliverables and diagrams](deliverables-diagrams.md) for contracts. Omit sections that do not affect the decision; never omit a critical invariant, major risk, or verification method merely to be brief.

## Completion gate

A design is ready for review when a reader can answer:

- What problem and load is this built for?
- What must never be violated?
- Where does data live, move, and become authoritative?
- Why is this architecture simpler or safer than the credible alternatives?
- What happens during overload, dependency failure, and recovery?
- How will the team observe, launch, roll back, and pay for it?
- Which assumptions still need evidence before implementation?
