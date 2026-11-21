# Archetypes: transactional and financial systems

> Prioritize invariants, authoritative owners, auditability, and deterministic recovery before throughput.

---

## 24. Reservation system

**Critical questions:** bucket granularity, hold TTL vs confirmed booking, overbooking cap, payment boundary, cancellation/refund policy, authoritative inventory owner, retry identity scope.

> **Invariant:** the **authoritative inventory/reservation owner** enforces `confirmed_bookings + active_holds <= permitted_capacity` per `(resource_id, time_bucket)`; **scoped retry identity within the issuer contract** `(actor_id, resource_scope, idempotency_key, payload_hash)` prevents duplicate bookings/charges and caller keys becoming tenant-wide identities.

**Scale axes:** resources, date-bucket rows, search-to-book ratio, hold concurrency, flash-sale skew.

**Failure prompts:** **concurrent double-consumption race** on last unit, late payment after hold expiry, crash after payment capture before booking commit, caller-key collision across actors/tenants, stale search cache.

**Trade-offs:** serial partition owner or conditional update (`UPDATE ... WHERE available >= qty`) on `(resource_id, date_bucket)` committed with hold row + scoped idempotency record; derived caches for search only. Reject reused keys with altered payloads. **Concrete crash/race test oracle:** fire $N$ concurrent last-unit holds/confirms, replay retries (matching vs altered actor/payload), and crash workers between payment capture and booking commit; pass requires zero over-allocation, one booking/refund per scoped retry identity, and zero cross-actor collisions.

---

## 25. Real-time leaderboard

**Critical questions:** global vs segmented boards, scoring rule, tie policy, top-N vs rank-around-user, season reset, anti-cheat, audit.

> **Invariant:** score-event ledger authority applies each scoped `(season_id, event_id, player_id)` transition at most once; ranking views resolve ties deterministically.

**Scale axes:** score events/s, active players, segments, top-N/rank queries, hot competitions.

**Failure prompts:** duplicate replay, out-of-order revocation, hot board contention, $O(N)$ global rank scan, season-boundary race, cache/ledger drift.

**Trade-offs:** append-only score log authority plus sorted set (or partitioned segment trees); exact order-statistic rank vs approximate buckets. Separate score authority from rebuildable views.

---

## 26. Payment system

**Critical questions:** pay-in/pay-out, auth vs capture, refunds/reversals, splits, minor units, PSP boundary, T+N settlement, disputes.

> **Invariant:** every monetary transition is authorized, guarded by scoped retry identity and monotonic intent state, booked in an immutable balanced double-entry ledger, and reconciled against external settlement statements.

**Scale axes:** intents/s, PSP calls, webhooks, ledger postings, settlement files, merchants, disputes.

**Failure prompts:** timeout after PSP success, **duplicate or out-of-order provider webhooks** (`AUTHORIZED` after `CAPTURED`/`REFUNDED`), crash between PSP response and local commit, partial refund race, settlement drift missed by API polling.

**Trade-offs:** persisted intent state machine (`CREATED -> IN_FLIGHT -> AUTHORIZED -> CAPTURED -> SETTLED`) with deterministic per-attempt PSP keys, monotonic webhook guards, `IN_FLIGHT` outcome sweeps, T+N settlement statement reconciliation, and compensating double-entry reversal/refund postings—see [external-outcome mechanism](interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction) for the crash-window and reconciliation protocol.

---

## 27. Digital wallet and ledger

**Critical questions:** stored value vs pass-through view, account partitions, holds, finality, overdraft, hot accounts, funding/payout boundary.

> **Invariant:** ledger journal authority conserves value across zero-sum double-entry postings, forbids spending beyond available balance (`posted - active_holds >= 0`), and produces one durable outcome per scoped command identity.

**Scale axes:** accounts, transfers/s, postings/s, hot accounts, balance reads, reconciliation volume.

**Failure prompts:** concurrent double-spend race, partial cross-shard posting, **duplicate or out-of-order funding/payout webhooks**, stuck cross-shard hold, row mutation, snapshot/journal drift.

**Trade-offs:** single-writer account partition or serializable ledger transaction; hold-then-capture for cross-shard/external transfers; monotonic funding/payout webhook guards, custodian settlement reconciliation, and immutable contra-postings for settled reversals—resolve provider events via [external-outcome mechanism](interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction).

---

## 28. Stock exchange and matching

**Critical questions:** order types, price-time priority, amend/cancel atomicity, risk limits, L1/L2/L3 market data, determinism, failover, audit.

> **Invariant:** each instrument's authoritative sequencer assigns one deterministic total order to commands; matching conserves quantity under strict priority and emits reproducible executions.

**Scale axes:** instruments, orders/cancels/s, burst skew, book depth, subscribers.

**Failure prompts:** duplicate order on retry, sequencer split-brain on failover, nondeterministic clock/float in matching loop, slow subscriber stalling execution, risk bypass.

**Trade-offs:** partition by instrument with single-threaded deterministic matching loop; replicated command log with epoch-fenced failover; in-memory book with snapshots + replay; decoupled ring-buffer broadcast for market data and clearing.
