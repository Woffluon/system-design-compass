# Archetypes: data and infrastructure systems

> Expose durability, delivery invariants, authoritative owners, and repair boundaries before selecting products.

---

## 19. Distributed message queue

**Critical questions:** point-to-point vs pub/sub, ordering scope, delivery guarantee, retention/replay, ack durability point, payload limit, consumer isolation, retry amplification budget.

> **Invariant:** partition log authority persists acknowledged messages across fault domains; consumer effects obey ordering and idempotency bounds until completed or moved to an owned repair path.

**Scale axes:** messages/bytes/s, partitions, producers, consumer groups, retry multiplier under faults, backlog drain rate, replication.

**Failure prompts:** broker/leader loss, unclean election, producer duplicate, **crash after remote side-effect or delivery success before local offset/record commit**, poison loop, slow consumer head-of-line block, rebalance storm, unowned DLQ exhaustion.

**Trade-offs:** append log (offset replay, partition order) vs work queue (visibility lease/ack); quorum vs leader ack. Close the **crash-after-remote-success-before-record** window by persisting pre-call intent state and enforcing downstream idempotency keys or outcome queries before retry. Size **completion capacity for peak ingress times retry multiplier** plus backlog drain, and define an **owned DLQ/exhaustion repair path** (owner, alert threshold, replay/purge action—exhaustion is not completion).

---

## 20. Metrics, monitoring, and alerting

**Critical questions:** metric types, resolution, cardinality bounds, retention tiers, query patterns, freshness, multi-tenancy, alert latency, loss tolerance.

> **Invariant:** accepted telemetry attaches to an authenticated tenant/series authority and is queryable within declared lag; paging rules evaluate independently of dashboard load.

**Scale axes:** samples/s, active series (cardinality), bytes/sample, retention tiers, queries, rule evaluations/s.

**Failure prompts:** cardinality explosion OOM, out-of-order/late samples, collector drop, duplicate ingest, compaction stall, ad-hoc query starving alerts, notification storm, meta-monitoring blind spot.

**Trade-offs:** push vs pull collection; edge aggregation; TSDB block compaction; raw vs downsampled tiers. Enforce tenant cardinality quotas at ingress, isolate alert evaluation from ad-hoc queries, and monitor alerting via an independent watchdog.

---

## 21. Event aggregation and ad clicks

**Critical questions:** authoritative billable event contract, dedup scope, event vs processing time watermark, lateness, correction policy, fraud quarantine, real-time vs finalized cutoffs.

> **Invariant:** finalized aggregates reconcile deterministically to the immutable raw event ledger within declared lateness and fraud-adjustment windows.

**Scale axes:** events/s, campaign keys, window state bytes, hot-key skew, retained raw events, replay throughput.

**Failure prompts:** duplicate/fabricated clicks, **worker crash after external sink write before checkpoint commit**, hot campaign skew, late batch after window close, partial checkpoint, double-applied correction.

**Trade-offs:** immutable raw log plus idempotent stream checkpointing (atomic state + offset commit or deterministic window-ID overwrite) vs batch recalculation; exact distinct sets vs sketches for non-billing views. Preserve raw events and emit adjustment ledger entries rather than mutating closed windows.

---

## 23. Distributed email service

**Critical questions:** send/receive scope, DKIM/SPF/DMARC authority, IP reputation, mailbox model, attachments, search, spam/bounce suppression, retention.

> **Invariant:** each accepted message records traceable per-recipient state under sender auth and suppression authority without duplicate transmission on crash.

**Scale axes:** messages/s, recipient fan-out, attachment bytes, domains/IP pools, mailbox sessions, search shards, retry queue depth.

**Failure prompts:** **crash after remote SMTP `250 OK` before local delivery record commit** causing duplicate send, ambiguous SMTP timeout, bounce loop, shared-IP blacklist contamination, malicious attachment, mailbox/index drift, unowned DLQ backlog.

**Trade-offs:** durable pre-send record (`IN_FLIGHT` with deterministic `Message-ID`) before remote SMTP send; transactional vs bulk IP pool isolation; blob attachments with metadata log; derived search. Size workers for **completion capacity under SMTP retry multipliers**, and assign an **owned DLQ/exhaustion repair path** for terminal failures.

---

## 24. Object storage

**Critical questions:** size distribution, immutability/versioning, consistency, multipart commit contract, listing, durability target, legal hold, erasure coding vs replication.

> **Invariant:** metadata authority exposes an object version only after erasure fragments or replicas pass end-to-end checksum durability across failure domains.

**Scale axes:** objects, bytes, PUT/GET QPS, multipart parts, list ops, replicas/fragments, scrub/repair bandwidth.

**Failure prompts:** partial upload, metadata/data mismatch, bit rot, rack/AZ loss during rebuild, repair starving foreground I/O, premature GC of live blocks, mass deletion.

**Trade-offs:** replication vs erasure coding; consistent metadata authority with immutable data extents; checksums at ingress, rest, transfer, and scrub. Throttle repair below foreground SLOs and use two-phase GC with grace windows.
