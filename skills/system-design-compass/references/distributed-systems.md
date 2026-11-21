# Distributed systems patterns

> Use this reference when state crosses processes, machines, zones, or regions. Choose mechanisms from required semantics and failure behavior rather than popularity.

## Partitioning and placement

Partition to address a proven load or fault-isolation limit. Define partition key, routing owner, replication unit, rebalancing procedure, and maximum partition size.

- **Hash partitioning:** spreads random keys evenly, weakens range scans, and remains exposed to single-key hotspots.
- **Range partitioning:** serves ordered scans, concentrating sequential writes unless ranges split and move.
- **Directory routing:** enables custom placement at the cost of metadata consistency and availability.
- **Consistent/rendezvous hashing:** reduces movement on membership change; virtual nodes handle heterogeneous node capacity, not hot keys.

Check skew by tenant, celebrity entity, time bucket, geography, and workload class. Mitigate with key salting plus read aggregation, tenant isolation, hierarchical aggregation, request coalescing, dedicated partitions, and admission control.

## Replication and consistency

State replication purpose: availability, durability, read locality, disaster recovery, analytics, or migration. Define synchronous acknowledgement scope, leader/quorum rules, lag visibility, failover authority, split-brain prevention, and divergence repair.

**Quorum counts alone do not guarantee linearizability or durability;** topology, versioning, read repair, failure detection, and membership changes govern outcomes. For multi-region writes, state the per-operation latency/consistency trade-off and keep irreversible or financial writes on a single serialization path unless conflict resolution is explicitly acceptable.

## Caching

Add a cache only with a named source of truth, key schema, value size, reuse ratio, freshness bound, miss path, invalidation owner, and failure policy.

- **Cache-aside:** simple, permits stale reads and miss storms.
- **Read/write-through:** centralizes policy while coupling write availability to the cache.
- **Write-behind:** lowers write latency at the risk of loss and reordering.
- **Local cache:** cuts network latency while multiplying memory and invalidation skew.

Protect hot or cold keys with request coalescing, bounded concurrency, jittered TTLs, justified prewarming, and stale-while-revalidate where staleness is safe. Prevent cache failures from sending an unbounded surge to the system of record.

## Messaging and stream processing

Specify producer acknowledgement point, durability, partitioning, ordering scope, consumer group semantics, retry budget, backpressure, and retention/replay rules. Make at-least-once consumers idempotent or deduplicated within the state-mutation transaction. Pair state writes with a transactional outbox or log-based change capture, and retain inbox deduplication keys beyond maximum replay age.

For windowed stream aggregation, define event time versus processing time, allowed lateness, watermarks, retractions, and deterministic replay. Use [decision validation](decision-validation.md) to turn delivery and queue claims into fault schedules and pass/fail oracles.

### Worker crashes, lease expiry overlap, and retry amplification

Queue consumers and outbound webhook workers face three compounding faults:

1. **Worker crash after remote effect before ack/record:** a worker invokes an external HTTP webhook or payment API, the remote side commits, and the worker crashes before recording local completion or acknowledging the broker message. Redelivery repeats the call unless durable pre-call intent and provider/idempotency identity are recorded first.
2. **Lease expiry and worker overlap with fencing tokens:** a stalled worker (GC pause, network hang, slow downstream) outlives its broker visibility timeout or lease expiry while still running. The broker hands the job to a second worker, creating concurrent overlapping execution. Require a monotonically increasing **fencing token** (or version check) enforced at the authoritative store/effect boundary so a stale lease owner cannot overwrite newer state or emit duplicate webhooks.
3. **Retry amplification:** when downstream latency approaches the call timeout or lease duration, leases expire mid-flight while callers and consumers retry concurrently. Overlapping workers plus multi-layer retries multiply in-flight load (`retry amplification`), saturating worker pools even at flat arrival rates. Enforce `lease_duration > call_timeout + local_record_margin`, assign one retry owner per boundary, use jittered exponential backoff, and cap retry concurrency.

### Backlog drain capacity and age-triggered intervention

**Storage capacity is not recovery capacity:** deep queue retention buffers messages without draining them. Backlog recovery requires degraded completion throughput to exceed normal arrivals plus retries:

```text
completion_rate > arrival_rate + retry_rate
net_drain_rate = completion_rate - (arrival_rate + retry_rate)
```

When retries or worker losses push `completion_rate <= arrival_rate + retry_rate`, backlog grows unboundedly regardless of disk space.

Monitor **backlog age** (oldest-item latency) alongside depth. Define an age threshold, an authoritative **intervention owner**, and the concrete **intervention action** when backlog age rises: throttle non-critical producers, shed optional load, clamp retries, isolate slow or poison tenants/endpoints into separate queues, or scale verified bottleneck capacity. **A dead-letter queue without an owner, alerts, replay safety, and retention is hidden backlog.**

## Coordination, time, and identity

Keep coordination off hot paths. When leader election, leases, locks, or consensus are required, name the protected invariant and validate fencing tokens at the storage boundary so a paused owner cannot act after lease expiry.

Wall clocks drift and jump backward; measure elapsed time with monotonic clocks. When IDs or ordering depend on wall clocks, define rollback handling and whether values leak timestamp, topology, or volume. Prefer entity- or partition-scoped order over global order.

## Overload and partial failure

Remote calls can succeed after a caller timeout; reconcile ambiguous outcomes before re-running side effects. Enforce:

- End-to-end deadline propagation.
- Per-dependency timeout and retry budgets with a single retry owner per boundary.
- Bounded queues, worker pools, and connection pools.
- Circuit breaking for unhealthy dependencies.
- Admission control, tenant quotas, and load shedding before saturation.
- Bulkheads across tenants, priorities, dependencies, and workload classes.
- Degraded responses preserving core correctness invariants.

## Rebalancing and recovery

Budget membership changes, failover, replica catch-up, compaction, backup, and rebalancing as active workloads. Throttle background repair before it breaches foreground SLOs while bounding degraded-redundancy duration.

Exercise full restoration—credentials, metadata, schema, indexes, and downstream reconciliation—because replication copies corruption and never replaces versioned backups.
