# Multi-Tenant SaaS Isolation and Noisy-Neighbor Protection

Use this reference when designing or reviewing B2B SaaS tenant boundaries, Silo/Bridge/Pool placement, PostgreSQL Row-Level Security (RLS), noisy-neighbor throttling, regional data residency, or tenant offboarding and live migration. Skip it for single-tenant applications without cross-tenant isolation boundaries.

**Contents:** [Layer tenancy matrix](#choose-tenancy-models-by-layer) · [PostgreSQL RLS hardening](#harden-postgresql-rls-against-covert-channels) · [Queues and rate limits](#isolate-queues-storage-and-external-rate-limits) · [Residency and lifecycle](#bound-residency-recovery-and-live-tenant-migration) · [Isolation template](#portable-multi-tenant-isolation-template)

## Choose tenancy models by layer

Do not force a single tenancy model across the whole architecture. Select **Silo** (dedicated per tenant), **Bridge** (shared infrastructure with per-tenant logical/schema separation), or **Pool** (shared multi-tenant infrastructure) independently across **control plane, compute, data plane, and storage** based on compliance, blast radius, noisy-neighbor risk, and cost.

Bind tenant identity at every trust boundary with **STS + ABAC tenant-scoped authorization** so services mint short-lived credentials carrying explicit `tenant_id` claims rather than relying on ambient service-wide privileges—matching [state authorization](interfaces-data.md#authorization-is-part-of-the-state-boundary).

## Harden PostgreSQL RLS against covert channels

`ENABLE ROW LEVEL SECURITY` alone is insufficient and leaks data across owners, pooled connections, and constraint errors. When using a shared PostgreSQL pool with RLS, enforce all five controls:

- **`FORCE ROW LEVEL SECURITY` and `NOBYPASSRLS`:** ensure table owners cannot bypass policies, and run application traffic under a dedicated `NOBYPASSRLS` role.
- **`SET LOCAL` under PgBouncer transaction pooling:** set `SET LOCAL app.tenant_id = ...` inside each transaction rather than session-level `SET`, preventing tenant context bleed when connections return to the pool.
- **Composite `(tenant_id, id)` keys for PK, `UNIQUE`, and `FK`:** single-column global `UNIQUE(email)` or `FOREIGN KEY (parent_id)` constraints create existence and collision side channels where one tenant probes another tenant's records via constraint errors. Scope constraints as `(tenant_id, id)` or `(tenant_id, email)`.
- **`security_invoker = true` on views:** execute views under the calling role's RLS context instead of the view creator's privileges.
- **`row_security = off` for backups:** reserve bypass privileges strictly for controlled backup/restore roles so logical backups do not silently drop rows.

## Isolate queues, storage, and external rate limits

Protect benign tenants from bursty or throttled neighbors across compute, storage, and outbound dependencies:

- **WFQ + DRF scheduling:** combine Weighted Fair Queuing with **Dominant Resource Fairness (DRF)** so multi-resource workloads (CPU, memory, I/O, outbound slots) are throttled by each tenant's dominant share rather than raw request count.
- **Delta-fairness reservation for high-preemption storage:** in LSM/compaction or checkpoint-heavy engines (such as RocksDB or PostgreSQL checkpoints), heavy write bursts create hidden compaction debt that inflates benign tenants' p99 tail latency by orders of magnitude even under classic fair queuing. Reserve foreground capacity and charge compaction/checkpoint work back to heavy writers via **delta-fairness**.
- **Release worker slots on `429` backoff:** never sleep inside a worker slot waiting on an upstream `429` retry delay—holding slots turns one tenant's rate limit into a pool-wide self-inflicted DoS. Release the worker slot immediately and reschedule the attempt onto a **per-tenant durable timer**.
- **Shuffle sharding with client/router retry:** assign each tenant to a virtual shard of *k* workers or partitions out of *n* total, reducing multi-tenant fault overlap to `1 / C(n, k)`. Pair shuffle sharding with **client or router retries** across the tenant's *k* assigned endpoints so a single unhealthy endpoint does not break availability.

## Bound residency, recovery, and live tenant migration

Define regional placement and full tenant lifecycle guarantees before onboarding regulated customers:

- **Data residency router:** route requests at the edge or control boundary to region-pinned cells/shards so regulated tenant data never persists outside its mandated jurisdiction.
- **Per-tenant CMKs:** isolate encryption domains with customer-managed keys per tenant for independent key rotation, auditability, and access revocation.
- **Single-tenant PITR:** verify point-in-time recovery at single-tenant granularity (isolated restore plus selective reconciliation) so restoring one tenant never rolls back neighbors.
- **Crypto-shredding offboarding:** destroy or revoke the tenant's CMK alongside bounded deletion sweeps across primary, derived, and backup stores.
- **Zero-downtime live tenant migration:** when moving a tenant from Pool to Bridge/Silo or across regions, use capture plus in-flight write drain, commit fencing, and reconciliation per [ownership handoff](evolve.md#prove-the-ownership-handoff-and-in-flight-write-drain).

## Portable multi-tenant isolation template

Use this contract summary when handing off multi-tenant isolation requirements to implementation or specification workflows:

```markdown
**Multi-Tenant Isolation Contract**
- **Layer Matrix:** `Control=<Pool|Bridge>`, `Compute=<Pool+ShuffleShard|Silo>`, `Data=<Pool+RLS|Bridge|Silo>`, `Storage=<Shared+DeltaFairness|Dedicated>`
- **Auth and RLS Hardening:** `STS+ABAC tenant claims, FORCE ROW LEVEL SECURITY, NOBYPASSRLS role, SET LOCAL (PgBouncer), composite (tenant_id, id) PK/UNIQUE/FK, security_invoker = true, row_security = off backups`
- **Noisy-Neighbor and Backpressure:** `<WFQ+DRF / delta-fairness reservation; release worker slot to durable timer on 429; shuffle sharding (n, k) + client retry>`
- **Residency and Lifecycle:** `<region router, per-tenant CMK, single-tenant PITR, crypto-shredding offboarding, live migration drain boundary>`
- **Verification Oracle:** `<tenant B p99 latency under tenant A burst (Proposed) + cross-tenant query = 0 rows + 0 blocked worker slots on 429>`
```
