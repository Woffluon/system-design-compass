# Archetypes: transactional and financial systems

> These workloads are dominated by correctness, auditability, and recovery. State business invariants before optimizing throughput. Do not treat these prompts as financial, legal, or regulatory advice.

---

## 22. Reservation system

**Critical questions:** resource and time granularity, hold versus confirmed booking, overbooking policy, payment boundary, cancellation, inventory source of truth, search freshness, and peak release events.

> **Invariant:** confirmed allocation never exceeds the permitted inventory for the resource/time bucket; retries do not create duplicate bookings or charges.

**Scale axes:** properties/resources, availability rows, searches, holds, bookings, date ranges, and hotspot events.

**Failure prompts:** concurrent last-item booking, expired hold race, payment succeeds after hold expiry, stale search cache, duplicate request, cancellation/refund divergence, and shard hotspot.

**Trade-offs:** optimistic conditional update, pessimistic lock, serial inventory owner, or intentional overbooking; precomputed availability versus authoritative confirmation; saga/compensation across payment. Make hold expiry and state transitions explicit and reconcile external payment outcomes.

---

## 25. Real-time leaderboard

**Critical questions:** global or segmented boards, ranking function, ties, update freshness, top-N versus rank-around-user, season reset, cheating, and historical audit.

> **Invariant:** a score event affects the intended player/season at most once and ranking uses a deterministic tie policy.

**Scale axes:** score events, active players, boards/segments, top-N reads, rank queries, season history, and hot competitions.

**Failure prompts:** duplicate score, out-of-order correction, hot board, expensive global rank, season-boundary race, cache divergence, and malicious score submission.

**Trade-offs:** ordered set/index for active boards; partitioned boards with merge for global top-N; event log plus materialized rank; exact versus approximate rank; synchronous versus bounded-lag update. Keep authoritative scoring evidence separate from rebuildable ranking views.

---

## 26. Payment system

**Critical questions:** pay-in, pay-out, refund, reversal, capture, multi-party split, currencies, provider boundary, settlement, dispute, and audit obligations.

> **Invariant:** every monetary state transition is authorized, idempotent, balanced where a ledger applies, attributable, and reconcilable to external statements.

**Scale axes:** attempts, successful transactions, provider calls, webhooks, ledger entries, settlement files, currencies, merchants, and disputes.

**Failure prompts:** client retry, timeout after provider success, duplicate/out-of-order webhook, partial capture/refund, credential compromise, provider outage, rounding error, settlement mismatch, and replayed request.

**Trade-offs:** hosted provider surface versus direct handling; payment intent state machine; idempotency record and result retention; append-only double-entry ledger; asynchronous provider events; reconciliation as a control loop. Never infer failure from timeout, mutate historical ledger entries, or use floating point for monetary amounts.

---

## 27. Digital wallet and ledger

**Critical questions:** stored value or view over external funds, account model, transfer finality, overdraft, holds, currencies, offline behavior, throughput per account, and regulatory boundary.

> **Invariant:** value is conserved across balanced postings; an account cannot spend beyond the defined available balance; each command has one durable outcome.

**Scale axes:** accounts, transfers, postings, hot accounts, balance reads, audit history, reconciliation, and snapshots.

**Failure prompts:** concurrent spend, duplicate transfer, partial cross-shard posting, stale balance, out-of-order reversal, unbalanced recovery, and snapshot/log divergence.

**Trade-offs:** single-writer account partitions; append-only double-entry journal; cached/materialized balances verified against postings; reservation/hold workflow; deterministic command ordering; cross-partition coordination versus asynchronous settlement. Treat event sourcing, CQRS, consensus, or two-phase protocols as mechanisms with operational costs, not correctness slogans.

---

## 28. Stock exchange and matching

**Critical questions:** order types, price-time or other priority, amend/cancel semantics, market sessions, risk checks, market-data levels, determinism, throughput/latency, and regulatory audit.

> **Invariant:** each instrument's accepted commands have one deterministic total order; executions obey matching priority and conserve quantity; published results are traceable to the command sequence.

**Scale axes:** instruments, orders/messages per second, burst per instrument, order-book depth, market-data subscribers, and audit retention.

**Failure prompts:** duplicate order, sequencer failover, leader split, nondeterministic replay, slow consumer, market-data gap, risk-service delay, hot instrument, and clock disagreement.

**Trade-offs:** partition by instrument; single-threaded deterministic matching loop per partition; replicated ordered command log; snapshots plus replay; binary versus general protocols; in-memory book with durable journal; separate execution and market-data paths. Keep consensus and storage off the inner loop only when acknowledgement and failover semantics remain explicit. Prefer deterministic recovery over active-active conflict resolution for one order book.
