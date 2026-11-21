# Interfaces and data

> Define system contracts, state ownership, correctness boundaries, and schema evolution.

**Contents:** [Invariants](#start-from-business-invariants) · [Authorization boundary](#authorization-is-part-of-the-state-boundary) · [Sync vs async](#choose-interaction-semantics) · [API contracts](#api-contract-checklist) · [Retry identity](#make-retry-identity-enforceable) · [External outcomes](#resolve-an-external-outcome-before-retry-or-correction) · [Event contracts](#event-contract-checklist) · [Data ownership](#model-data-around-ownership-and-access) · [Consistency](#state-consistency-explicitly) · [Lifecycle](#design-the-data-lifecycle) · [Validation](#validate-contracts)

## Start from business invariants

List properties that must hold under concurrency, retries, partial failure, and migration (e.g., one active reservation per resource/interval, ledger conservation, monotonic versions, tenant isolation, or at-most-one external effect per idempotent command).

For each invariant state:

- Authoritative owner and storage boundary.
- Mutating operations and serialization point.
- Violation detection and repair owner.
- Timeliness guarantee: immediate, bounded, or eventual.

### Authorization is part of the state boundary

Read this check for sensitive state mutations or external events. Identify the authenticated actor, tenant/resource ownership, permitted operation, and provider-event origin before choosing state transitions.

**Counterexample:** a balanced transfer debits another user's wallet, or a forged provider event finalizes a payment. Ledger conservation and deduplication do not prevent either violation.

Enforce resource authorization before mutation **and before returning an idempotently stored result**. Authenticate provider events and bind their provider account/object to the local tenant and operation; a valid schema is insufficient. Trusted upstream enforcement requires evidenced contract and bypass boundaries. Test an authenticated non-owner, a cross-tenant replay, and a forged event: deny access, disclose no stored result, and leave authoritative state unchanged.

## Choose interaction semantics

Use synchronous calls when callers need an immediate result within dependency latency and availability budgets. Use asynchronous work when buffering, independent scaling, fan-out, retries, or long execution outweigh immediate completion.

For asynchronous boundaries define acceptance, durability, ordering, duplicate handling, retry ownership, terminal failure, and user-visible status.

Avoid distributed transactions by default without weakening business invariants. Use a single transactional owner, conditional writes, an outbox, workflow state machines, reservation/confirmation, compensation, or reconciliation, and state accepted intermediate states.

## API contract checklist

For each command or query specify:

- Caller and authorization decision.
- Stable resource identity and tenant context.
- Request/response schema, size limits, and units.
- Success semantics and machine-readable errors.
- Idempotency key scope, retention, conflict rules, and stored result.
- Timeout and cancellation behavior.
- Pagination order, opaque cursor stability, filtering, and consistency.
- Concurrency control (version check or conditional write).
- Rate and quota dimensions.
- Compatibility and deprecation policy.

Separate transport acceptance from business completion for asynchronous work.

### Make retry identity enforceable

Open this check when client retries mutate valuable state. A bare ID without a namespace is incomplete: two tenants may pick the same ID, or one caller may reuse it across commands. Scope identity as `(tenant, caller, operation type, client key)` and enforce uniqueness at the authoritative store. Include only business-distinguishing dimensions; reuse the same key on retry.

Claim the scoped key, bind its request digest, mutate state, and persist the durable result in one atomic transaction. Concurrent duplicates wait for or read that result; conflicting payloads fail. After a committed write with a lost response, retries return the same authorized result. Retention must outlive supported retry and replay windows because key deletion permits duplicate effects. Test concurrent same-key calls, payload conflicts, cross-tenant collisions, and crashes before/after commit.

### Resolve an external outcome before retry or correction

Open this section for external side effects (payments, payouts, outbound HTTP webhooks), ambiguous provider attempts, or financial recovery. Required evidence: durable intent/provider identities, idempotency and query retention windows, authenticated callback origin, monotonic journal transitions, and settlement reconciliation records.

**Crash window (`crash after remote success before local record`):** the remote call (payment charge, payout, or HTTP webhook) succeeds at the external endpoint, and the worker crashes or times out before recording the local state transition or broker acknowledgement. Neither a local transaction nor an outbox atomically joins an independent provider's commit. Retrying under a new key duplicates the remote effect; marking the attempt failed releases funds or state already committed remotely.

Persist the authorized intent and stable provider idempotency key before invoking the external endpoint. Keep the outcome unknown (`IN_FLIGHT (pending_resolution)`) until resolved, and atomically bind the provider object and terminal status to a unique local posting:

1. **Out-of-order and duplicate webhooks:** verify provider signatures and account binding, then apply a monotonic state machine so delayed non-terminal events cannot regress settled state and duplicate callbacks become no-ops.
2. **External statement and settlement reconciliation (beyond API polling):** point-in-time API status polling alone is insufficient because provider query retention expires, callbacks drop or reorder, and asynchronous captures, settlement failures, or chargebacks occur after polling. Reconcile external settlement statements against the local ledger on a schedule, routing unmatched charges, missing settlements, or amount discrepancies to an owned repair queue.
3. **Settled transaction reversal, refund, and compensating ledger entry:** timeout sweeps only resolve ambiguous in-flight attempts; they cannot undo settled transactions. When an attempt settles remotely after local expiry, settles in error, or is refunded/disputed, execute an explicit settled-transaction reversal or refund backed by an append-only compensating ledger entry linked to the original intent and provider settlement ID—never mutate or delete settled postings in place.

When provider idempotency or query retention expires on an ambiguous attempt, hold and escalate to statement reconciliation or manual review rather than generating a new submission key. Attempt exhaustion is not settlement.

Test crashes before submission and in the crash window after remote success before local record, missing/reordered/duplicate webhooks, expired idempotency retention, statement reconciliation mismatches, and settled-transaction reversal with compensating ledger entries. Pass when remote effects and local postings match the intent without duplicate effects, unowned ambiguity, or premature fund release.

## Event contract checklist

An event envelope defines event ID, type, schema version, occurrence time, producer, subject/partition key, correlation/causation IDs, tenant, trace context, and payload. Include only consistently populated fields.

Classify the event as fact, command, notification, or state transfer, and specify:

- Delivery expectation: at-most-once, at-least-once, or proven effectively-once effect.
- Ordering scope (per entity or partition, not global).
- Consumer idempotency and deduplication horizon.
- Retry schedule, poison-message isolation, and replay policy.
- Schema compatibility and unknown-field handling.
- Sensitive-data classification and retention.

Claim "exactly once" only by naming the atomic boundary joining consumption, state mutation, and acknowledgement. Broker ordering or deduplication does not make external effects exactly-once. DLQ isolation and replay can reorder an entity's operations; preserve canonical entity version/state or hold dependent work when order is an invariant, and test poison-message isolation followed by replay. Resolve external effects via the [outcome mechanism](#resolve-an-external-outcome-before-retry-or-correction).

## Model data around ownership and access

For each entity define identity, authoritative owner, lifecycle, write paths, query patterns, cardinality, size, retention, deletion, and consistency. Choose indexes from concrete access patterns and budget for write/storage amplification.

Keep one authoritative owner per entity. Label representations as authoritative, derived, cached, or archival, and make derived views reconstructable or reconciled.

Design keys for distribution and lifecycle:

- **Partition key:** spreads sustained load, serves dominant reads, and supports rebalancing.
- **Sort key:** supports bounded range scans without unbounded partitions.
- **Generated ID:** defines uniqueness scope, ordering visibility, clock dependence, entropy, and leakage risk.
- **Tenant key:** enforces isolation, quota, deletion, export, and placement controls.

## State consistency explicitly

For each read-after-write, uniqueness, ordering, and aggregation path state the consistency model (strong, monotonic, bounded stale, causal, or eventual) and client behavior during lag or conflict.

For optimistic concurrency, specify the checked version and conflict retry/merge policy. For locks or leases, specify ownership, expiry, fencing tokens, and post-pause recovery. **Timeouts alone never prove that a remote operation failed.**

## Design the data lifecycle

Define creation, mutation, versioning, retention, archival, deletion, backup, restore, replay, migration, and legal hold. Propagate deletions across derived stores and backups per policy; encryption and access control do not replace minimization and retention limits.

Evolve schemas via expand-migrate-contract: widen compatibility, migrate producers/consumers and data, verify convergence, then remove legacy fields. Define defaults for old records and unknown fields.

## Validate contracts

Run schema contract tests, concurrent invariant tests, consumer replay/duplicate tests, mixed-version migration tests, conservation/uniqueness property checks, and restore/reconciliation drills. **A schema-valid message can still violate a business invariant;** test both.
