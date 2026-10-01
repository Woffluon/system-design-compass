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

### Authorization is part of the state boundary

Read this check for sensitive state mutations or externally supplied events. Identify the authenticated actor, tenant/resource ownership, permitted operation and provider-event origin before choosing state transitions.

**Counterexample:** a valid, balanced transfer debits someone else's wallet, or a forged provider event finalizes a payment. Ledger conservation and event deduplication do not prevent either violation.

Enforce resource authorization before mutation **and before returning an idempotently stored result**. Authenticate provider events and bind their provider account/object to the local tenant and operation; a valid payload schema is insufficient. Trusted upstream enforcement is a valid boundary only when its contract and bypass paths are evidenced. Test an authenticated non-owner, a cross-tenant replay and a forged event: deny access, disclose no stored result and leave authoritative state unchanged.

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

### Make retry identity enforceable

Open this check when client retries can mutate valuable state. A stable ID without a namespace is incomplete: two tenants may choose the same ID, or one caller may reuse it for a different command. Specify the identity scope, such as `(tenant, caller, operation type, client key)`, and enforce uniqueness at the authoritative store. Include only dimensions that distinguish business operations; do not generate a new key on retry.

Claim the scoped key, bind its request digest, mutate state and persist the durable result in one transaction or an equivalent atomic boundary. A concurrent duplicate waits for or reads that result; conflicting payload reuse fails. After commit followed by a lost response, retry returns the same authorized result. Test concurrent same-key calls, payload conflicts, cross-tenant collisions and crashes before/after commit. Retention must cover supported retries and replay; deleting the identity can permit a new effect.

### Resolve an external outcome before retry or correction

Open this section for valuable external effects, ambiguous provider attempts or payment recovery. Required evidence: durable intent/provider identities, idempotency and query retention, callback origin, journal transitions and reconciliation records.

**Failure sequence:** the provider commits, then the worker crashes before local acknowledgement or the reply times out. Retrying under a new identity duplicates the effect; declaring failure can release funds already spent remotely. A local transaction or outbox cannot atomically join an independent provider's commit.

Persist the authorized intent and stable provider identity before submission. Keep the outcome unknown until a canonical query, authenticated callback or statement reconciliation resolves it. Atomically bind the provider object and terminal outcome to a unique local posting/result. When provider idempotency or query retention no longer covers the attempt, hold and escalate rather than inventing a safe new submission.

Give stuck intents an owner and intervention threshold: query/reconcile, retry the existing identity when safe, or route to manual resolution. Attempt exhaustion is not settlement. Refunds and reversals are new authorized postings linked to the original; reconcile provider statements to the journal and route unmatched items to an owned repair queue.

Test crashes before submission and after remote commit/before local acknowledgement, missing or reordered callbacks, expired identity retention, stuck-intent recovery and reversal. Pass when observed provider effects and local postings agree with the intent; ambiguity remains owned without duplicate effects, unauthorized corrections or premature fund release.

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

A broker's ordering or deduplication does not establish exactly-once external processing. DLQ isolation and replay can reorder an entity's business operations. Preserve canonical entity state or hold later work when order is an invariant; test poison-message isolation followed by replay. Resolve external effects with the [outcome mechanism](#resolve-an-external-outcome-before-retry-or-correction).

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
