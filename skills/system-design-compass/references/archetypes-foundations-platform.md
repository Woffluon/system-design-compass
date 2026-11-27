# Archetypes: foundations and platform

> Expose decisions, authoritative state owners, and failure boundaries before selecting products.

**Contents:** [1. Scaling](#1-scaling-from-one-service-to-large-traffic) · [2. Estimation](#2-back-of-the-envelope-estimation) · [3. Framework](#3-system-design-framework) · [4. Rate limiter](#4-rate-limiter) · [5. Consistent hashing](#5-consistent-placement-and-hashing) · [6. Distributed KV](#6-distributed-key-value-store) · [7. Unique IDs](#7-unique-identifier-generation)

---

## 1. Scaling from one service to large traffic

**Use when:** evolving a deployment under growing traffic, state, or tenant isolation demands.

**Decisive questions:** What saturates first? Which authoritative state blocks horizontal replication? Is load read-, write-, compute-, storage-, or connection-bound? What are failure domain and recovery targets?

> **Invariant:** request correctness and single authoritative state ownership hold across capacity, cache, or placement changes.

**Scale axes:** QPS, connections, working-set bytes, background jobs, tenants, regions, release cadence.

**Failure prompts:** cache stampede, DB connection exhaustion, shared-state lock contention, retry storm, health-check cascade, replica lag stale reads, hot tenant, rebalance overload.

**Trade-offs:** vertical scale vs partitioning; stateless compute vs pinned state; read replicas vs cache invalidation; synchronous work vs bounded queues; shared cluster vs cellular isolation. Add tiers only when a measured or requirement-derived limit justifies operational cost.

---

## 2. Back-of-the-envelope estimation

**Use when:** capacity, feasibility, cost, or architecture boundaries depend on magnitude.

**Decisive questions:** Which threshold changes architecture? What are low/base/high input ranges, peak multipliers, and growth horizons? What amplification comes from fan-out, retries, replication, indexes, or compaction?

> **Invariant:** units, inputs, and amplification multipliers remain explicit and verifiable against telemetry.

**Scale axes:** ops/s, concurrency, storage growth, bandwidth, queue drain capacity, working set, failover headroom.

**Failure prompts:** average-only sizing, unit mismatch, false precision, unmodeled retry/recovery amplification, undersized downstream bottleneck.

**Trade-offs:** range model vs simulation. Derive queue and compute capacity from peak input plus retry and recovery drain multipliers per [peak attempt demand and backlog drain](requirements-estimation.md#derive-peak-attempt-demand-and-backlog-drain-under-duplicates-and-retries) rather than invented point estimates.

---

## 3. System design framework

**Use when:** a request is broad, ambiguous, or risks becoming an ungrounded component list. Follow the full [design workflow](design.md): trace every component to a requirement, invariant, authoritative state owner, violating event sequence, and fault oracle rather than listing products.

---

## 4. Rate limiter

**Use when:** protecting capacity, enforcing entitlements, curbing abuse, or isolating noisy neighbors.

**Decisive questions:** What authenticated actor and resource scope define the key? Hard entitlement cap or load shedding? Where lives the authoritative counter? Behavior on limiter or clock failure?

> **Invariant:** an authenticated principal cannot exceed policy beyond a bounded sync tolerance; noisy neighbors cannot starve protected traffic.

**Scale axes:** checks/s, active keys, policy churn, edge POPs, dimension cardinality.

**Failure prompts:** spoofed identity, hot-key contention, counter outage, clock skew drift, split edge counters exceeding global cap, retry storm on `429`.

**Trade-offs:** token bucket (burst control) vs fixed window (simple, boundary double-burst) vs sliding log (exact, high memory); local edge batching vs centralized atomic counters. Bind keys to verified identity within the issuer contract; define fail-open vs fail-closed per endpoint.

---

## 5. Consistent placement and hashing

**Use when:** membership changes must minimize state movement or route keys deterministically to live owners.

**Decisive questions:** Stateless routing, soft cache, or authoritative partition ownership? Who is the membership authority? How are skewed keys and failure domains weighted? When can a new owner serve traffic?

> **Invariant:** each key resolves to one authoritative owner (or zone-diverse replica set) under a monotonically versioned membership epoch.

**Scale axes:** nodes, keys, replicas, membership churn, state transfer bytes/s.

**Failure prompts:** dual owners under stale epoch, correlated rack/zone placement, hot key overloading one ring segment, cold-cache stampede on topology change, rebalance saturating foreground I/O.

**Trade-offs:** virtual-node ring vs rendezvous hashing vs directory/range coordinator. Hashing reduces movement; authoritative state requires epoch fencing and completed state transfer before activating a new owner.

---

## 6. Distributed key-value store

**Use when:** key access outgrows one node in throughput, footprint, fault tolerance, or geography.

**Decisive questions:** Read/write consistency and durability contract? Who arbitrates write order per partition? Conflict, secondary lookup, and scan policy? What bounds repair and compaction impact?

> **Invariant:** acknowledged writes survive promised fault domains; conflict resolution or leader fencing never silently drops committed state.

**Scale axes:** keys, bytes, ops/s, partitions, replicas, tombstones, compaction and repair bandwidth.

**Failure prompts:** split-brain leaders, stale replica reads, hinted-handoff backlog, tombstone resurrection after delayed repair, compaction stall, hot partition skew, bit rot.

**Trade-offs:** single-leader lease/epoch replication vs leaderless quorum + conflict resolution (LWW/CRDT); LSM write throughput vs B-tree read predictability; hash vs range partitioning. Enforce single-owner serialization when domain invariants forbid concurrent merge.

---

## 7. Unique identifier generation

**Use when:** generating unique IDs across distributed nodes, regions, or offline clients.

**Decisive questions:** Uniqueness scope and lifetime? Time-sortable, non-enumerable, or offline-generatable? Bit budget? Can generation block when clocks regress or leases expire?

> **Invariant:** no two issued IDs collide within the namespace; ordering holds only within one issuing authority or bounded clock window.

**Scale axes:** IDs/s per node, generator nodes/regions, bit length, clock resolution, lease renewal rate.

**Failure prompts:** NTP clock rollback duplicates, worker-ID reuse after crash, per-tick sequence overflow, coordinator outage, sequential ID enumeration leak, B-tree right-edge hotspot.

**Trade-offs:** random UUID (decentralized, poor index locality) vs time-prefixed Snowflake/ULID (locality, requires worker-ID lease + clock-rollback fence) vs DB/range allocator. Fence clock regression by stalling or advancing a persisted epoch counter; never equate timestamp prefix order with causal or transactional order.
