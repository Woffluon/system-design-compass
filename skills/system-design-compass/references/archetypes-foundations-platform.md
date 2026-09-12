# Archetypes: foundations and platform

Use these compact prompts to expose the decisions behind a workload. They are not complete architectures and do not prescribe products.

## 1. Scaling from one service to large traffic

**Use when:** a workload must evolve from a simple deployment or the user asks how to scale an existing application.

**Decisive questions:** What resource saturates first? Which state prevents horizontal replication? Is traffic read-, write-, compute-, storage-, or connection-heavy? Which failure domains and recovery targets matter now?

**Invariants:** preserve request correctness and authoritative data while capacity or placement changes.

**Scale axes:** request rate, concurrent connections, data set and working-set size, background work, tenants, regions, and release frequency.

**Failure prompts:** cache stampede, database connection exhaustion, shared-state bottleneck, retry storm, load-balancer health error, replica lag, hot tenant, and rebalancing load.

**Trade-offs:** vertical scale versus partitioning; stateful versus stateless compute; read replicas versus caching; synchronous versus queued work; shared platform versus cells. Add a component only after a measured or requirement-driven limit justifies its operational cost.

## 2. Back-of-the-envelope estimation

**Use when:** capacity, feasibility, cost, or a technology threshold depends on magnitude.

**Decisive questions:** Which result could change the architecture? What are low/base/high input ranges? What is the peak factor and growth horizon? What amplification comes from fan-out, retries, replicas, indexes, or versions?

**Invariant:** units and assumptions remain visible and replaceable by telemetry.

**Scale axes:** operations per second, concurrency, storage growth, bandwidth, queue drain, memory working set, and failure headroom.

**Failure prompts:** average-only sizing, inconsistent units, false precision, missing peaks, undersized downstream stage, and ignoring recovery traffic.

**Trade-offs:** model complexity versus decision value. Prefer a transparent range to an elaborate calculation built on invented inputs.

## 3. System design framework

**Use when:** an architecture request is broad, ambiguous, or at risk of becoming a technology inventory.

**Decisive questions:** What decision and audience does the artifact serve? Which user journeys and quality attributes dominate? What must never be violated? Which constraints are fixed versus assumed?

**Invariant:** every material component and decision traces to a requirement or accepted risk.

**Scale axes:** organizational as well as technical—teams, ownership, release cadence, operating capacity, and migration horizon.

**Failure prompts:** premature decomposition, unprioritized NFR lists, no end-to-end flow, absent alternatives, happy-path-only diagrams, and no launch evidence.

**Trade-offs:** completeness versus focus. Cover the whole lifecycle but deepen only the decisions that can change the outcome.

## 4. Rate limiter

**Use when:** protect capacity, enforce entitlement, control abuse, or provide fairness.

**Decisive questions:** What identity and resource are limited? Is the policy a hard entitlement or protective control? Where must it be enforced? How much burst is allowed? What happens during limiter or clock failure?

**Invariants:** a principal cannot exceed the defined policy beyond an explicit tolerance; critical traffic is not starved by noisy neighbors.

**Scale axes:** checks per second, number of active keys, policy update rate, geographic distribution, and cardinality of dimensions.

**Failure prompts:** spoofed identity, hot keys, counter loss, clock skew, inconsistent edge decisions, limiter dependency outage, memory growth, and retry amplification after rejection.

**Trade-offs:** token bucket for controlled bursts; fixed windows for simplicity but boundary spikes; sliding logs for precision at high storage cost; approximate counters for scale. Define fail-open/fail-closed per operation and expose remaining quota/reset semantics only when useful and safe.

## 5. Consistent placement and hashing

**Use when:** membership changes must move less state or requests need deterministic placement.

**Decisive questions:** Is this routing, ownership, cache placement, or replica placement? What is the failure domain? How skewed are key and node weights? Who publishes membership and at what consistency?

**Invariants:** a key resolves to the intended live owners under a known membership version; replicas span required failure domains.

**Scale axes:** nodes, keys, replicas, membership churn, and state transferred per change.

**Failure prompts:** stale membership, correlated replica placement, single hot key, uneven virtual nodes, thundering rewarm, and simultaneous recovery/rebalance.

**Trade-offs:** ring hashing, rendezvous hashing, directory routing, or static ranges. Hashing reduces movement; it does not solve hot entities, metadata authority, or state-transfer correctness.

## 6. Distributed key-value store

**Use when:** access is primarily by key and availability, latency, data size, or geographic placement exceeds a single-node store.

**Decisive questions:** Key and value limits? Required read/write consistency? Conflict policy? Scan or secondary-index needs? Durability and recovery scope? Tenant and hotspot distribution?

**Invariants:** acknowledged-write semantics are explicit; version/conflict resolution never silently violates domain correctness.

**Scale axes:** keys, bytes, operations, partitions, replicas, tombstones, compaction, and repair bandwidth.

**Failure prompts:** split brain, replica lag, hinted-handoff backlog, tombstone resurrection, read-repair surge, compaction stalls, hot partitions, disk loss, and corrupted replicas.

**Trade-offs:** leader-based versus leaderless replication; strong versus tunable/eventual reads; LSM versus B-tree-style write/read amplification; range versus hash partitioning. Domain-level conflicts may require a single owner even when the storage engine can merge versions.

## 7. Unique identifier generation

**Use when:** IDs must be generated across nodes, regions, or disconnected clients.

**Decisive questions:** Uniqueness scope and lifetime? Sortability? Offline generation? Predictability or enumeration risk? Length and representation? Can generation pause during clock or coordination failure?

**Invariants:** no duplicate within the promised scope; ordering is promised only within the defined boundary.

**Scale axes:** IDs per second, generator nodes/regions, lifetime, clock resolution, and namespace count.

**Failure prompts:** clock rollback, node-ID reuse, sequence overflow, coordinator outage, information leakage, hot ordered index, and format migration.

**Trade-offs:** random IDs favor decentralization; time-sortable IDs improve locality but reveal time and require rollback handling; database sequences are simple within one authority; range allocation improves availability but creates unused gaps. Do not equate approximate chronological order with causal or transactional order.
