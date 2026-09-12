# Distributed systems patterns

Use this reference when state crosses processes, machines, zones, or regions. Choose mechanisms from required semantics and failure behavior rather than popularity.

## Partitioning and placement

Partition to distribute a proven load or failure-isolation need. Define the partition key, routing owner, replication unit, rebalancing process, and maximum practical partition size.

- **Hash partitioning:** distributes random keys well but weakens range scans and can still suffer hot keys.
- **Range partitioning:** supports ordered scans but concentrates sequential or skewed traffic unless ranges split and move.
- **Directory-based routing:** supports custom placement and moves but introduces metadata consistency and availability requirements.
- **Consistent/rendezvous hashing:** reduces movement as membership changes; virtual nodes or weights address heterogeneous capacity, not single-key hotspots.

Analyze skew by tenant, celebrity entity, time bucket, geography, and workload type. Mitigations include key salting with read aggregation, tenant isolation, hierarchical aggregation, request coalescing, dedicated partitions, and admission control.

## Replication and consistency

State the replication purpose: availability, durability, read locality, disaster recovery, analytics, or migration. Identify synchronous acknowledgement scope, leader or quorum behavior, lag visibility, failover authority, split-brain prevention, and repair.

Quorum counts alone do not guarantee desired semantics; topology, versioning, read repair, failure detection, and membership changes matter. For multi-region designs, make the latency/consistency trade-off per operation. Keep irreversible or financially material writes on a clearly owned serialization path unless the business explicitly accepts conflict resolution.

## Caching

Use a cache only with a defined source of truth, key, value size, expected reuse, freshness tolerance, miss behavior, invalidation owner, and failure policy.

- Cache-aside is simple but permits stale reads and miss storms.
- Read-through/write-through centralize policy but add dependency coupling.
- Write-behind improves write latency but risks loss and reordering.
- Local caches reduce latency but multiply invalidation and memory use.

Protect cold or hot keys with request coalescing, bounded concurrency, jittered expiry, prewarming only when justified, and stale-while-revalidate where stale data is safe. Never let cache failure produce an unbounded surge into the system of record.

## Messaging and stream processing

Define the producer acknowledgement point, durability, partitioning, ordering scope, consumer group behavior, retry policy, backpressure, and retention/replay needs.

At-least-once delivery is common: make consumer effects idempotent or deduplicated at the same durable boundary as the effect. Use an outbox or log-coupled change capture when state mutation and event publication must not diverge. An inbox/deduplication record needs a scope and retention horizon.

Retries require a budget. Use exponential delay and jitter for transient failure, cap attempts or elapsed time, and route terminal failures to a visible repair workflow. A dead-letter queue without ownership, alerts, replay safety, and retention is only hidden backlog.

Monitor queue age and oldest-item latency, not only depth. Bound producer admission or shed optional work when consumption cannot catch up.

For windowed aggregation define event time versus processing time, allowed lateness, watermark policy, corrections/retractions, and replay determinism. Reconciliation is part of correctness when late or duplicated events are possible.

## Coordination, time, and identity

Minimize coordination on hot paths. When leader election, leases, locks, or consensus are necessary, define the protected invariant and use fencing/version tokens so an expired owner cannot act after a pause.

Wall clocks can move and machines disagree. Use monotonic time for elapsed durations. If IDs or ordering depend on clocks, define rollback handling and whether generated values expose time, topology, or traffic.

Global order is expensive and often unnecessary. Prefer ordering within the smallest business scope that preserves correctness.

## Overload and partial failure

Distributed calls can complete after a caller times out. Design operations so retries are safe and ambiguous outcomes can be queried or reconciled.

Apply:

- Deadlines propagated through the call chain.
- Per-dependency timeout and retry budgets.
- Bounded queues, worker pools, and connection pools.
- Circuit breaking for persistently unhealthy dependencies.
- Admission control, fair quotas, and load shedding before saturation.
- Bulkheads by tenant, priority, dependency, or workload class.
- Degraded responses that preserve critical invariants.

Avoid retry multiplication across layers. Choose one retry owner for each failure boundary and ensure the expected extra load fits capacity during incidents.

## Rebalancing and recovery

Treat membership change, failover, replica catch-up, compaction, backup, and rebalancing as workloads with resource budgets. Throttle background repair before it harms foreground SLOs, but retain a bound on how long redundancy may remain reduced.

Test the actual restoration path, including credentials, metadata, schema, indexes, and downstream reconciliation. Replication can copy corruption; it is not a substitute for versioned backups and recovery exercises.
