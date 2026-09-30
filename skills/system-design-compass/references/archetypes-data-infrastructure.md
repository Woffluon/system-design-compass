# Archetypes: data and infrastructure systems

> Use these prompts with the common interface, distributed-systems, and production-readiness references. The goal is to expose semantics and failure behavior before choosing infrastructure products.

---

## 19. Distributed message queue

**Critical questions:** point-to-point or publish/subscribe, ordering scope, delivery expectation, retention/replay, acknowledgement point, payload limits, consumer isolation, and latency/throughput targets.

> **Invariant:** an acknowledged message has the promised durability and remains processable under the stated retention; consumer effects follow the declared duplicate/ordering semantics.

**Scale axes:** messages and bytes per second, partitions, producers, consumer groups, backlog age, retention, replication, and fan-out.

**Failure prompts:** broker/leader loss, unclean election, producer retry duplicate, poison message, slow consumer, partition skew, group rebalance storm, disk exhaustion, replica catch-up, and control-plane outage.

**Trade-offs:** append log versus work queue; broker-side routing versus producer routing; partition order versus parallelism; push versus pull; acknowledgement durability versus latency; fixed retention versus per-message deletion. Define backpressure, quota, replay, terminal failure ownership, and rebalancing as first-class behavior.

---

## 20. Metrics, monitoring, and alerting

**Critical questions:** metric types, resolution, cardinality, retention, query patterns, freshness, multi-tenancy, alert latency, and loss tolerance.

> **Invariant:** accepted telemetry is attributable to a tenant/source and queryable with defined delay and accuracy; paging rules represent actionable conditions.

**Scale axes:** samples per second, active time series, label cardinality, bytes per sample, retention tiers, queries, rule evaluations, and dashboard fan-out.

**Failure prompts:** cardinality explosion, out-of-order/late samples, collector outage, duplicate ingest, compaction backlog, query hotspot, alert evaluation gap, notification storm, and monitoring-system dependency during an incident.

**Trade-offs:** push versus pull collection; local aggregation; time partitioning; compression/downsampling; exact versus approximate queries; raw versus tiered retention. Separate ingestion, durable storage, query, rule evaluation, and notification failure domains. Monitor the monitoring system from an independent path.

---

## 21. Event aggregation and ad clicks

**Critical questions:** authoritative event definition, deduplication scope, event versus processing time, lateness, correction policy, attribution window, fraud filtering, and real-time versus finalized results.

> **Invariant:** aggregate results reconcile to accepted authoritative events within a stated tolerance and finalization window.

**Scale axes:** events per second, keys/campaigns, window count, skew, retained raw events, state per partition, query dimensions, and replay volume.

**Failure prompts:** duplicate or fabricated events, hot campaign, clock skew, late arrival after window close, consumer restart, partial checkpoint, code-version replay difference, and correction double-apply.

**Trade-offs:** streaming versus batch; lambda-like dual paths versus one replayable log; exact distinct counts versus sketches; pre-aggregation versus flexible queries. Preserve raw or reconstructable evidence for reconciliation when financial or billing decisions depend on aggregates.

---

## 23. Distributed email service

**Critical questions:** sending, receiving, or both; domain/DNS responsibility; deliverability; mailbox semantics; attachments; search; spam/abuse; retention; and provider interoperability.

> **Invariant:** each accepted message has traceable delivery state; mailbox access, sender authorization, and suppression policy remain enforceable.

**Scale axes:** messages, recipients, recipient fan-out, bytes/attachments, domains, concurrent mailbox sessions, search index, and retries.

**Failure prompts:** duplicate send, retry after ambiguous SMTP result, bounce loop, provider throttling, spam campaign, malicious attachment, mailbox/index divergence, DNS change, and queue backlog.

**Trade-offs:** durable acceptance before asynchronous delivery; per-recipient state; blob attachments with metadata references; mailbox log versus mutable rows; derived search; provider/IP pool isolation. Model accepted, attempted, delivered to remote server, bounced, and read as distinct states—remote acceptance is not human receipt.

---

## 24. Object storage

**Critical questions:** object size distribution, immutability/versioning, consistency, multipart upload, metadata and listing, durability target, retention/legal hold, geographic placement, and access model.

> **Invariant:** an acknowledged object version can be retrieved byte-correct under the promised durability and authorization semantics until lifecycle deletion permits removal.

**Scale axes:** objects, total bytes, request rate, multipart parts, metadata/list operations, replicas or erasure fragments, versions, and repair bandwidth.

**Failure prompts:** partial upload, metadata/data mismatch, bit corruption, disk/rack/zone loss, stale listing, orphaned fragments, failed compaction, repair backlog, accidental mass deletion, and credential leakage.

**Trade-offs:** replication versus erasure coding; strong metadata authority with distributed blobs; immutable versions; write-ahead metadata transitions; checksums at ingress, rest, transfer, and repair; placement across failure domains. Define repair priority and capacity so recovery traffic does not destroy foreground service.
