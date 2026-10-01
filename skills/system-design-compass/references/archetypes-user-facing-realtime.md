# Archetypes: user-facing and realtime systems

> Use these prompts to identify workload-specific invariants, scale axes, and failure behavior. Combine with the shared design references; do not treat an archetype as a reference architecture.

---

## 8. URL shortener

**Critical questions:** custom aliases, expiry, update/delete, abuse screening, redirect latency, analytics freshness, and geographic reach.

> **Invariant:** a live short code resolves deterministically to the authorized destination version; custom codes are unique.

**Scale axes:** create rate, redirect rate, active codes, cache working set, analytics events, and malicious scans.

**Failure prompts:** code collision, stale redirect cache, malicious destination, hot/viral code, enumeration, expired-link resurrection, analytics loss, and redirect loops.

**Trade-offs:** random versus sequence-derived codes; immutable versus editable targets; synchronous safety checks versus asynchronous moderation; strong primary mapping with derived analytics. Treat redirect serving and analytics as different criticality paths.

---

## 9. Web crawler

**Critical questions:** allowed scope, freshness, politeness, robots handling, rendering, deduplication, content types, prioritization, and legal/safety constraints.

> **Invariant:** fetch behavior respects per-origin policy and does not create unbounded duplicate work.

**Scale axes:** discovered URLs, fetches per second, origins, content bytes, render cost, recrawl frequency, and frontier size.

**Failure prompts:** crawler traps, URL canonicalization errors, duplicate content, DNS/redirect abuse, slow origins, poison documents, frontier starvation, renderer exhaustion, and uncontrolled egress.

**Trade-offs:** breadth versus freshness; per-host queues versus global priority; raw URL versus content deduplication; static fetch versus rendering. Isolate untrusted parsing and make the frontier durable, bounded, and replay-aware.

---

## 10. Notification delivery

**Critical questions:** channels, urgency, user preferences, provider limits, scheduling, deduplication, ordering, localization, and delivery-versus-read semantics.

> **Invariant:** accepted notifications follow consent/preferences and produce no more than the allowed visible effects.

**Scale axes:** recipients, fan-out, channel mix, scheduled bursts, templates, tokens/endpoints, retries, and provider quotas.

**Failure prompts:** duplicate send, stale device token, provider outage, preference race, template/config error, thundering retry, quiet-hours violation, and unbounded dead letters.

**Trade-offs:** synchronous acceptance with asynchronous delivery; per-recipient/channel idempotency; priority queues; provider isolation; delivery receipts as evidence rather than proof of user consumption. Separate critical transactional messages from bulk engagement traffic.

---

## 11. News feed

**Critical questions:** ranking freshness, follow graph, privacy, fan-out latency, celebrity skew, deletes, pagination stability, and recommendation explainability.

> **Invariant:** viewers see only authorized items; ordering and cursor semantics remain defined as the feed changes.

**Scale axes:** posts, followers, feed reads, candidate set, ranking features, fan-out amplification, and media references.

**Failure prompts:** celebrity fan-out, stale authorization, duplicate/missing pagination items, ranking dependency failure, deleted-content leakage, cache stampede, and backfill overload.

**Trade-offs:** fan-out on write, fan-out on read, or hybrid by author class; precomputed versus query-time ranking; stable snapshot versus live cursor. Keep content authority separate from derived feed materializations and support repair/rebuild.

---

## 12. Chat

**Critical questions:** one-to-one/groups, devices, delivery/read semantics, offline history, attachment handling, ordering scope, presence accuracy, encryption, moderation, and retention.

> **Invariant:** a message has stable identity and membership authorization; promised ordering holds within the stated conversation boundary.

**Scale axes:** concurrent connections, messages, groups, group fan-out, device sessions, history bytes, and presence updates.

**Failure prompts:** reconnect storms, duplicate/out-of-order delivery, split membership view, hot large group, presence flapping, lost acknowledgements, attachment abuse, and region failover.

**Trade-offs:** stateful gateways with external session directory; per-conversation partitioning; server sequence versus client IDs; push delivery plus sync cursor; precise versus approximate presence. Define server accepted, delivered to device, and read as separate states.

---

## 13. Search autocomplete

**Critical questions:** prefix/fuzzy behavior, locale, personalization, freshness, safety filtering, latency, top-k quality, and deletion obligations.

> **Invariant:** suggestions respect policy and tenant/user visibility; ranking version and freshness are observable.

**Scale axes:** queries per second, prefixes, vocabulary, update stream, languages, model/index size, and personalization dimensions.

**Failure prompts:** unsafe suggestion, stale deletion, hot prefixes, cache pollution, index rebuild gap, feedback poisoning, and rank instability.

**Trade-offs:** trie/FST/search index; offline aggregation plus streaming deltas; edge cache for common prefixes; global versus personalized ranking. Use bounded candidate generation before expensive ranking and keep a safe fallback.

---

## 14. Video platform

**Critical questions:** upload limits, formats, playback startup, quality adaptation, rights/privacy, moderation, geographic distribution, and processing deadline.

> **Invariant:** authorized viewers receive the intended asset/version; source and derivatives retain traceable identity and lifecycle.

**Scale axes:** uploads, source bytes, rendition amplification, transcode compute, watch bandwidth, catalog metadata, and viral skew.

**Failure prompts:** incomplete multipart upload, duplicate transcode, poisoned media, orphaned derivatives, CDN miss storm, manifest inconsistency, rights change lag, and regional egress spike.

**Trade-offs:** direct object upload via scoped URLs; asynchronous idempotent DAG processing; immutable derivatives; metadata authority separate from blob storage; CDN and adaptive bitrate. Design deletion and policy propagation across every derivative and cache.

---

## 15. File storage and synchronization

**Critical questions:** file/folder semantics, block or whole-file upload, offline edits, conflict policy, sharing, versioning, deduplication, retention, and device count.

> **Invariant:** metadata references durable content; access decisions and version lineage remain consistent across sync.

**Scale axes:** files, bytes, versions, chunks, devices, change events, sharing edges, and sync fan-out.

**Failure prompts:** interrupted upload, metadata/blob divergence, conflicting offline edits, duplicate chunks, stale share permission, notification loss, mass-delete propagation, and ransomware-like updates.

**Trade-offs:** content-addressed chunks versus simple objects; optimistic versioning; per-namespace change cursor; server conflict copies versus domain merge; direct blob transfer with metadata commit. Make large operations resumable and protect destructive propagation.

---

## 16. Proximity search

**Critical questions:** point versus area, radius, result count, freshness, update frequency, ranking, boundary correctness, and privacy.

> **Invariant:** returned entities satisfy authorization and documented distance/region semantics within a known freshness bound.

**Scale axes:** indexed entities, location updates, queries, radius, density skew, precision levels, and geographic distribution.

**Failure prompts:** cell-boundary miss, dense-cell explosion, stale location, polar/dateline error, hot city, privacy leakage, and expensive exact-distance filtering.

**Trade-offs:** geohash/grid, quadtree, R-tree, or search index; coarse candidate cells followed by exact filtering; adaptive precision by density. Do not expose precision greater than the product requires.

---

## 17. Nearby friends

**Critical questions:** opt-in, visibility relationships, location precision/freshness, background update policy, notification cadence, block semantics, and battery/network limits.

> **Invariant:** only mutually authorized viewers can learn permitted proximity; revocation propagates within a defined bound.

**Scale axes:** active users, update frequency, friendship edges, nearby density, subscriptions, and fan-out.

**Failure prompts:** stale authorization, rapid boundary churn, celebrity/high-degree user, location replay, region handoff, inference from update timing, and reconnect burst. An authorized viewer can combine repeated distance-band queries with their own changing position to infer finer location; removing coordinates alone does not bound disclosure.

**Trade-offs:** compare actual mechanisms. Pull reads authorized friends' latest state; work follows active queries and friend degree. Geocell pub/sub routes updates to active cell subscribers, then enforces relationship authorization; work follows updates and cell occupancy, with dense-cell hotspots. A hybrid sends bounded invalidations to active viewers and pulls current authorized state, trading extra coordination for fewer repeated reads. Choose from measured cadence, degree/density skew, freshness and revocation budgets; do not install all three.

**Decision evidence:** explain these alternatives in the recommendation; naming an alternative only as a future trigger does not compare its cost or failure boundary. Explain how a moving authorized viewer could infer location through repeated queries. Select a permitted disclosure policy and enforcement mechanism, such as stable subject coarsening plus bounded refresh/query budgets; distance bands or rate limits alone do not prove privacy. Test probing from multiple positions against that policy and disclose residual inference rather than asserting that coordinates being absent prevents it.

**Validation:** inject a crowded cell, many simultaneous reconnects, stale presence and revocation. State the bounded response: partition or suppress optional cell fan-out, jitter/rate-limit reconnects, reject expired locations and fail closed on authorization uncertainty. Measure client transmissions and radio wakes as well as server load; coalesce movement updates and bound foreground/background refresh. Repeat probing from multiple positions to test the allowed precision/freshness policy, not merely the absence of coordinate fields. Use short retention and explicit deletion, and treat cached or previously observed locations as a disclosure boundary rather than data that can be recalled.

---

## 18. Map and navigation

**Critical questions:** static browsing versus turn-by-turn navigation, offline use, map freshness, traffic freshness, route quality, ETA accuracy, and supported geography.

> **Invariant:** map/version dependencies used for a route are traceable; navigation updates do not silently mix incompatible graph data.

**Scale axes:** map graph, tiles, location updates, route queries, traffic events, zoom levels, and geographic hot spots.

**Failure prompts:** stale closure, tile miss storm, GPS noise, route service timeout, map-version skew, traffic-feed loss, and reroute oscillation.

**Trade-offs:** precomputed raster/vector tiles; hierarchical graph partitioning and precomputation; online traffic overlays; client caching/offline packages; approximate ETA models. Provide last-known/static fallbacks and expose freshness where it changes safety or trust.
