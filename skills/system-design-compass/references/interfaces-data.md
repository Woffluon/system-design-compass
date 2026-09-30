# Interfaces and data

> Use this reference to define system contracts, state ownership, correctness boundaries, and schema evolution.

## Start from business invariants

List properties that must remain true despite concurrency, retries, partial failure, and migration. Examples include one active reservation per resource and interval, conservation of ledger value, monotonic version numbers, tenant isolation, or at-most-one externally visible effect for an idempotent command.

For each invariant identify:

- Authoritative owner and storage boundary.
- Operations that may change it.
- Concurrency control or serialization point.
- How a violation is detected and repaired.
- Whether the guarantee is immediate, bounded, or eventual.

## Choose interaction semantics

Use synchronous calls when the caller needs an immediate result and the dependency can fit the latency and availability budget. Use asynchronous work when buffering, independent scaling, fan-out, retries, or long processing is more important than immediate completion.

An asynchronous boundary does not remove failure; define acceptance, durability, ordering, duplicate behavior, retry ownership, terminal failure, and user-visible status.

Avoid distributed transactions by default, but do not weaken a real business invariant merely to avoid them. Options include a single transactional owner, conditional writes, an outbox, workflow state machines, reservation/confirmation, compensation, or reconciliation. Explain the accepted intermediate states.

## API contract checklist

For each command or query specify:

- Caller and authorization decision.
- Stable resource identity and tenant context.
- Request/response fields, validation, size limits, and units.
- Success semantics and machine-readable error categories.
- Idempotency key scope, retention, conflict behavior, and stored result.
- Timeout and cancellation behavior.
- Pagination order, cursor stability, filtering, and consistency.
- Concurrency control such as expected version or conditional update.
- Rate and quota dimensions.
- Compatibility and deprecation policy.

Use opaque cursors when offset pagination becomes unstable or expensive under concurrent writes. Keep transport success separate from business completion for accepted asynchronous work.

## Event contract checklist

An event envelope commonly needs an event ID, event type, schema version, occurrence time, producer, subject or partition key, correlation/causation IDs, tenant, trace context, and payload. Include only fields the system can define consistently.

State whether the event is a fact, command, notification, or state transfer. Define:

- Delivery expectation: at-most-once, at-least-once, or an explicitly proven effectively-once effect.
- Ordering scope, usually per entity or partition rather than global.
- Consumer idempotency and deduplication horizon.
- Retry schedule, poison-message handling, and replay policy.
- Schema compatibility and unknown-field behavior.
- Sensitive-data classification and retention.

Do not promise "exactly once" without naming the atomic boundary that joins consumption, state mutation, and acknowledgement.

## Model data around ownership and access

For each entity or aggregate capture identity, owner, lifecycle, write paths, query patterns, expected cardinality, size, retention, deletion, and consistency needs. Select indexes from concrete access patterns and account for write/storage amplification.

Prefer one authoritative owner. Derived indexes, caches, search documents, analytics tables, and materialized views should be reconstructable or have an explicit reconciliation process. Label each representation as authoritative, derived, cached, or archival.

Choose keys with distribution and lifecycle in mind:

- A partition key should distribute sustained load, support dominant access, and permit rebalancing.
- A sort key should make required ranges efficient without creating unbounded partitions.
- Generated IDs should state uniqueness scope, order visibility, clock dependence, entropy, and information leakage.
- Tenant keys should preserve isolation and allow quota, deletion, export, and placement controls.

## State consistency explicitly

For each read-after-write, uniqueness, ordering, and aggregation path state the required model: strong, monotonic, bounded stale, causal where available, or eventual. Describe client behavior during lag or conflict.

When using optimistic concurrency, define the version checked and the retry/merge policy. When using locks or leases, define ownership, expiry, fencing, and recovery after pauses. **Timeouts alone do not prove that a remote operation failed.**

## Design the data lifecycle

Cover creation, mutation, versioning, retention, archival, deletion, backup, restore, replay, migration, and legal hold where relevant. Deletion must propagate to derived stores and backups according to the stated policy. Encryption and access control do not replace minimization and retention limits.

Schema changes should normally expand compatibility first, migrate producers/consumers and data, observe convergence, then contract. Record defaulting behavior for old data and unknown fields.

## Validate contracts

Use contract tests, concurrency tests around invariants, replay and duplicate tests for consumers, migration tests across mixed versions, property checks for conservation/uniqueness, and restore/reconciliation exercises. **A schema-valid message can still violate a business invariant;** test both.
