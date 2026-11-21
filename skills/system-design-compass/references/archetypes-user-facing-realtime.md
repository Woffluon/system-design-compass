# Archetypes: user-facing and realtime systems

> Identify invariants, authoritative owners, scale axes, and failure boundaries. Combine with shared references.

---

## 8. URL shortener

**Critical questions:** custom aliases, TTL/expiry, target mutation/deletion, abuse screening, redirect latency, analytics freshness, regional reads.

> **Invariant:** mapping authority resolves each live code deterministically to one authorized target version; custom aliases enforce strict uniqueness.

**Scale axes:** create QPS, redirect QPS, active aliases, cache working set, click events, enumeration scans.

**Failure prompts:** alias collision on concurrent create, stale edge cache serving revoked/malicious URL, viral hot key, sequential enumeration, expired-code reuse race, redirect loop.

**Trade-offs:** pre-allocated counter ranges vs random token with collision retry; immutable vs versioned targets; synchronous safe-browsing gate vs async takedown invalidation. Isolate redirect serving from async click analytics.

---

## 9. Web crawler

**Critical questions:** crawl scope, freshness vs coverage, politeness (`robots.txt`, per-host rate), JS rendering, URL vs content dedup, poison defense.

> **Invariant:** per-origin scheduler authority enforces politeness leases and bounded frontier dedup without unbounded re-fetch loops.

**Scale axes:** discovered URLs, fetches/s, origins, downloaded bytes, render slots, frontier size.

**Failure prompts:** infinite URL traps, canonicalization mismatch, DNS/redirect SSRF abuse, slow origins tying up workers, parser crash on poison payload, renderer OOM, frontier starvation.

**Trade-offs:** BFS coverage vs priority/freshness scoring; per-host leased queues vs global priority heap; URL fingerprint vs SimHash content dedup; static fetch vs selective rendering. Sandbox parsers and persist a replay-safe frontier.

---

## 10. Notification delivery

**Critical questions:** channels, urgency tiers, consent/quiet hours, provider quotas, scheduling, dedup key scope, ordering, delivery vs read state.

> **Invariant:** accepted notifications obey consent/preference authority and execute bounded sends per scoped `(notification_id, recipient, channel)` identity.

**Scale axes:** recipients, fan-out, channel mix, scheduled bursts, retry multiplier under provider degradation, active tokens.

**Failure prompts:** **crash after remote provider success before local delivery record commit** causing duplicate resend, stale token, provider outage/throttling, preference race, thundering retry, quiet-hours breach, unowned DLQ growth.

**Trade-offs:** durable outbox acceptance before async dispatch; pre-send `IN_FLIGHT` record plus provider idempotency key (or provider status query before retry) to close the post-send crash window; transactional vs bulk queues. Size completion capacity for peak input times retry multiplier, and define an owned DLQ/exhaustion repair path (owner, alert threshold, replay/suppress action—exhaustion is not completion).

---

## 11. News feed

**Critical questions:** ranking freshness, follow/block graph authority, privacy, fan-out latency, celebrity skew, deletes, cursor stability.

> **Invariant:** viewers receive only items authorized by current graph/privacy authority, with deterministic cursor pagination across inserts and deletes.

**Scale axes:** write QPS, follower degree skew, read QPS, candidate pool, ranking features, media hydration.

**Failure prompts:** celebrity write fan-out stalling queues, stale block/privacy cache exposing revoked posts, duplicate/skipped pagination items, ranking timeout, deleted post remaining in timelines, cache stampede.

**Trade-offs:** push fan-out on write vs pull on read vs hybrid by follower degree; materialized inbox IDs vs post authority store; snapshot cursor vs monotonic `(score, post_id)` token. Enforce authorization at read hydration and support timeline rebuild from authoritative stores.

---

## 12. Chat

**Critical questions:** 1:1 vs large groups, multi-device sync, delivery/read receipts, offline history, attachments, ordering scope, presence fidelity, E2EE.

> **Invariant:** conversation partition owner assigns stable identity and monotonic per-conversation sequence to each authorized message.

**Scale axes:** concurrent sessions, messages/s, group fan-out, devices/user, history bytes, presence churn.

**Failure prompts:** reconnect storm, duplicate/out-of-order frames, stale membership admitting removed user, hot mega-group fan-out, presence flapping, lost acks, region failover split.

**Trade-offs:** stateful gateways with leased session directory; single-writer conversation sequencing vs client UUID + causal order; push wakeup plus pull cursor sync (`last_seen_seq`); exact vs lazy presence. Separate server-persisted, device-delivered, and user-read states.

---

## 13. Search autocomplete

**Critical questions:** prefix/fuzzy match, locale/tenant scope, personalization, freshness, safety blocklists, latency, takedown removal.

> **Invariant:** completions obey tenant visibility and active safety/suppression rules, with observable index version and bounded suppression delay.

**Scale axes:** keystroke QPS, prefixes, vocabulary, query-log ingest, locales, edge cache size.

**Failure prompts:** unsafe/PII suggestion leak, blocked term surviving in cache, hot prefix overload, query-log poisoning, rebuild gap.

**Trade-offs:** compiled FST/trie snapshot vs inverted prefix index; batch build plus real-time suppression/delta overlay; client debouncing and prefix caching; global vs personalized re-rank. Enforce a real-time serving deny-list independent of batch rebuilds.

---

## 14. Video platform

**Critical questions:** upload limits/resumability, rendition ladder, startup latency, ABR, DRM/rights, moderation gate, CDN offload, transcode SLA.

> **Invariant:** asset metadata authority exposes a video only after moderation and manifest readiness; derivatives trace to an immutable source version.

**Scale axes:** uploads, source bytes, transcode compute, renditions, egress bandwidth, viral skew.

**Failure prompts:** abandoned multipart upload, duplicate chunk transcode on crash, poison media exploit, orphaned blobs, CDN miss storm, manifest referencing missing segment, rights revocation lag.

**Trade-offs:** pre-signed resumable direct upload; idempotent chunked transcode DAG with deterministic keys; immutable segments/manifests; short-TTL signed CDN tokens. Propagate takedowns across metadata authority, manifests, and CDN purge.

---

## 15. File storage and synchronization

**Critical questions:** file/folder semantics, chunked delta vs whole-file upload, offline edits, conflict policy, ACL sharing, version retention, dedup scope.

> **Invariant:** namespace metadata authority commits a version only after all content-addressed chunks are durably verified; devices converge on identical version lineage.

**Scale axes:** files, chunk bytes, versions, devices/namespace, ACL edges, change-feed fan-out.

**Failure prompts:** crash between blob upload and metadata commit, orphan chunks, concurrent offline overwrite, cross-tenant hash-dedup side-channel leak, stale share ACL, ransomware mass-delete propagation.

**Trade-offs:** content-addressed chunking vs whole-object overwrite; CAS (`expected_version`) metadata commit forking conflict copies vs domain merge; per-namespace journal cursor (`revision_id`) for delta sync. Require proof-of-possession before cross-user dedup and keep soft-delete recovery windows.

---

## 16. Proximity search

**Critical questions:** point vs area, radius, top-k ranking, update cadence, cell-boundary exactness, location privacy.

> **Invariant:** queries return only authorized entities whose authoritative coordinates fall within the region and declared staleness bound.

**Scale axes:** entities, location writes/s, spatial queries/s, radius, urban density skew.

**Failure prompts:** cell-boundary miss, dense-cell scan explosion, stale coordinates, antimeridian/polar wrap error, unbounded exact-distance post-filter.

**Trade-offs:** Geohash/S2/H3 cells vs quadtree vs R-tree; covering-cell union plus exact distance filter; read replica index vs mutable grid. Cap candidates per cell and coarsen precision to product needs.

---

## 17. Nearby friends

**Critical questions:** mutual opt-in authority, visibility graph, precision/freshness, background wakeup budget, revocation latency, battery/radio limits.

> **Invariant:** only mutually authorized peers learn permitted proximity within the revocation SLA; repeated queries cannot narrow location beyond the disclosure policy.

**Scale axes:** active users, update cadence, friend degree, cell density, subscriptions, fan-out.

**Failure prompts:** stale auth/block cache leaking location after revocation, cell-boundary flapping, high-degree fan-out spike, location replay, region handoff, reconnect burst. A moving authorized viewer can triangulate finer coordinates by combining repeated distance-band queries from changing positions; stripping coordinates alone does not bound disclosure.

**Trade-offs:** compare mechanisms against measured cadence, degree/density skew, and revocation budgets (do not install all three):
- **Pull:** queries authorized friends' latest state; scales with active polls and friend degree.
- **Geocell pub/sub:** routes updates to cell subscribers then filters by friendship authority; scales with movement writes and cell occupancy.
- **Hybrid:** sends bounded invalidations to active viewers who pull current state, trading session coordination for fewer polls.

**Decision evidence:** compare mechanism cost and failure boundaries in the recommendation rather than deferring alternatives to future triggers. Explain moving-viewer inference via repeated distance-band queries. Select a disclosure policy and enforcement mechanism—such as stable subject coarsening plus bounded query/refresh budgets—because distance bands or rate limits alone fail under multi-position probing. Disclose residual inference.

**Validation:** inject crowded cells, simultaneous reconnects, stale presence, and revocation. State bounded responses: partition/suppress optional cell fan-out, jitter/rate-limit reconnects, reject expired locations, and fail closed on auth uncertainty. Measure client radio wakes and server load; coalesce movements and cap refresh. Probe from multiple positions to test the coarsening/budget policy. Use short retention, explicit deletion, and treat previously observed locations as an irreversible disclosure boundary.

---

## 18. Map and navigation

**Critical questions:** static browsing vs turn-by-turn routing, offline packs, road-graph vs traffic freshness, ETA accuracy, dispatch matching.

> **Invariant:** route computation binds to a traceable road-graph version and traffic epoch without mixing incompatible segment IDs.

**Scale axes:** graph nodes/edges, vector tiles, GPS stream, route/ETA QPS, traffic incidents, urban hotspots.

**Failure prompts:** unindexed closure routing into hazard, tile miss storm, GPS canyon noise snapping to wrong road, route timeout, client/server graph-version skew, reroute oscillation.

**Trade-offs:** precomputed vector tiles; hierarchical routing graphs (contraction hierarchies / cells) with dynamic traffic weights; offline regional bundles; HMM map-matching. Fall back to static weights on traffic loss and surface staleness on safety-critical routes.
