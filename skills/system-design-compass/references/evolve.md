# Evolution and migration workflow

Use this mode when a running system must change without losing correctness, availability, or reversibility.

## Establish current and target states

Describe the current architecture from evidence, the pressure forcing change, and the minimum target capability. Separate the desired end state from the next safe state. Record constraints such as release independence, client upgrade lag, data residency, maintenance windows, and maximum acceptable rollback loss.

Name the invariants that must hold throughout—not only after—the migration. Typical examples include no lost accepted writes, no double charge, stable identifiers, monotonic entitlement, bounded staleness, and continued authorization enforcement.

## Choose the migration shape

Prefer a sequence of reversible transitions. Use the least elaborate pattern that fits:

- **Expand–migrate–contract:** add compatible schema or interface, move traffic/data, then remove the old shape.
- **Strangler transition:** intercept a bounded capability and gradually route it to a replacement.
- **Parallel run or shadowing:** execute the new path without serving its result; compare outputs and resource behavior.
- **Backfill plus change capture:** copy history, then converge ongoing changes before cutover.
- **Dual read:** compare or fall back during a read-path transition; define which result is authoritative.
- **Dual write:** use only with an explicit failure model, idempotency, reconciliation, and ownership. Two independent writes are not atomic by default.
- **Versioned contract:** support old and new clients until measured usage permits retirement.
- **Cell, tenant, cohort, or region rollout:** bound blast radius and expose skew before broad migration.

Avoid a big-bang cutover unless coexistence is impossible and the accepted outage/data-loss envelope is explicit.

## Design data movement

Specify:

- Source of truth before, during, and after each phase.
- Stable identity mapping and schema/default conversion.
- Backfill ordering, checkpoints, rate limits, and restart behavior.
- Handling of late, duplicate, out-of-order, deleted, and malformed records.
- Reconciliation query, tolerated discrepancy, repair process, and audit retention.
- Cutover consistency boundary and how writes in flight are handled.
- Backup and restoration tests before irreversible contraction.

Never treat record counts alone as correctness proof. Compare business invariants, sampled content, aggregates, and boundary conditions.

## Make each phase executable

For every phase record:

1. Change and affected interfaces.
2. Preconditions and owner.
3. Compatibility window.
4. Traffic or data cohort.
5. Success metrics and observation period.
6. Abort threshold.
7. Rollback action and what cannot be rolled back.
8. Exit evidence required for the next phase.

Keep rollback within the tested compatibility window. A rollback that reintroduces code unable to read newly written data is not a rollback.

## Control operational risk

Budget migration traffic separately from user traffic. Apply backpressure and pause controls. Monitor correctness deltas, queue age, saturation, latency, errors, cost, and SLO burn by old/new path and cohort. Preserve correlation identifiers across both systems.

Assign a decision maker for cutover and abort. Schedule high-risk phases when the team can observe them, while respecting regional traffic and business cycles. Prefer automated stop conditions for measurable hazards.

## Contract the old system

Remove old reads, writes, credentials, routes, data, jobs, flags, dashboards, and alerts only after:

- No supported client or producer uses the old contract.
- The new path has met success criteria for the agreed observation window.
- Reconciliation is clean or discrepancies are accepted explicitly.
- Restore and rollback obligations have expired or moved to the new system.
- Retention, deletion, legal hold, and audit requirements are satisfied.

Finish with updated ownership and architecture records. Deferred decommissioning is operational debt; name an owner and deadline rather than calling the migration complete.
