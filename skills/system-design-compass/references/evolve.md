# Evolution and migration workflow

> Use when a running system must change without losing correctness, availability, or reversibility.

**Contents:** [Invariants](#bound-current-state-target-state-and-migration-invariants) · [Migration shapes](#select-a-reversible-migration-shape) · [Data movement & repair](#design-data-movement-reconciliation-and-repair) · [Phases & rollback](#define-executable-phases-quantitative-abort-thresholds-and-rollback-boundaries) · [Blast radius](#control-operational-risk-and-blast-radius) · [Contraction gate](#gate-schema-and-system-contraction-on-zero-legacy-traffic-and-durable-apply) · [Completion gate](#completion-gate)

## Bound current state, target state, and migration invariants

Describe the current architecture from evidence, pressure forcing change, and minimum target capability. Separate the end state from the next safe step. Record release independence, client upgrade lag, data residency, maintenance windows, and maximum acceptable rollback loss.

Name invariants holding throughout—not only after—migration: no lost accepted writes, no double charge, stable identifiers, monotonic entitlement, bounded staleness, and continuous authorization enforcement.

## Select a reversible migration shape

Prefer reversible transitions using the simplest fitting pattern:

| Pattern | Decision boundary |
|---|---|
| **Expand–migrate–contract** | add compatible schema/interface, move traffic and data, then contract old shape after verification gates pass. |
| **Strangler transition** | intercept a bounded capability and incrementally route traffic to the replacement. |
| **Parallel run or shadowing** | execute the new path without serving its result; compare outputs and resource behavior. |
| **Backfill plus change capture** | copy history, then converge ongoing mutations before cutover. |
| **Dual read** | compare or fall back during a read transition; define which store is authoritative. |
| **Dual write** | require an explicit failure model, idempotency, reconciliation, and single authoritative owner; two writes are not atomic. |
| **Versioned contract** | support old and new clients until measured legacy traffic reaches zero. |
| **Cell, tenant, cohort, or region rollout** | bound blast radius and expose skew before broad cutover. |

Avoid big-bang cutover unless coexistence is impossible and the outage/data-loss envelope is explicit.

## Design data movement, reconciliation, and repair

Specify:

- Authoritative source of truth before, during, and after each phase.
- Stable identity mapping and schema/default conversion.
- Backfill ordering, checkpoints, rate limits, and restart idempotency.
- Handling of late, duplicate, out-of-order, deleted, and malformed records.
- Reconciliation query, tolerated discrepancy, repair owner, escalation threshold, and audit retention.
- Cutover consistency boundary and in-flight write handling.
- Backup and restore verification before irreversible contraction.

Row counts alone do not prove correctness; reconcile business invariants, sampled content, aggregates, and boundaries.

For discrepancy repair, read the authoritative row or deletion tombstone at its version, apply it through the same atomic version guard as capture/backfill, and re-reconcile. Never repair from an unversioned stale scan. Unrepaired mismatches outside the correctness envelope block cutover.

### Prove the ownership handoff and in-flight write drain

For writable-source copy or capture migrations, start replayable capture before scanning and retain versioned deletion evidence. At cutover, block new source writes **and resolve transactions already in flight** by draining or aborting them. Only then record the final committed capture boundary, **durably apply all captured in-flight writes** through that boundary at the target, reconcile, and enable the target writer. An admission flag cannot stop a transaction already past admission; fence stale writers at their commit boundary so post-boundary commits cannot vanish.

Exercise delayed stale scan reads, pre-scan deletions, duplicate/out-of-order capture, and restarts. Require newest version/deletion preservation, zero lost accepted writes, and one authoritative writer before cutover.

## Define executable phases, quantitative abort thresholds, and rollback boundaries

For every phase record:

1. Change, affected contracts, preconditions, and owner.
2. Compatibility window and traffic/data cohort.
3. Success metrics and observation duration.
4. **Quantitative abort thresholds** (explicit error-rate, latency, capture-lag, or discrepancy limits triggering immediate halt or rollback).
5. **Executable rollback action and last safe rollback point** (exact state boundary before unreplicated writes or irreversible external effects occur, plus forward-repair or reverse-sync actions past that boundary).
6. Exit evidence required for the next phase.

Keep rollback within the verified compatibility window. Returning to old code unable to both **read and write** data mutated during the phase is not a rollback.

- **Weak:** "Phase 2: Migrate writes; roll back on Day 7 if errors rise."
- **Executable:** "Phase 2 (10% cohort, 48h): abort if error rate > 0.5% or capture lag > 30s (`Proposed`); roll back via old-binary read/write routing before irreversible PSP capture; contract old column only after 0 legacy reads/writes."

### Drill mixed-version reads and writes before promotion

Before promoting a stateful phase, verify old binaries read **and write** new-format records cleanly and state the point of no return (forward repair or reverse sync beyond irreversible external effects) per the canonical [mixed-version rollback drill](decision-validation.md#migration-restart-repair-and-mixed-version-drills).

## Control operational risk and blast radius

Separate migration traffic budgets from user traffic with backpressure and pause controls. Monitor correctness deltas, queue age, saturation, latency, errors, cost, and SLO burn by path and cohort while preserving correlation IDs. Assign a cutover/abort owner and wire automated stops to quantitative abort thresholds.

## Gate schema and system contraction on zero legacy traffic and durable apply

**Never trigger schema/column drop or contraction on a calendar date (such as "Day 7").** Dates are schedule checkpoints, not safety evidence.

Drop old columns, schemas, reads, writes, credentials, routes, jobs, flags, or storage only after proving:

- **Measured zero legacy read and write traffic** from supported clients, workers, and producers across the observation window.
- **Durable apply of all captured in-flight writes** through the fenced cutover boundary, verified by clean invariant and content reconciliation.
- Proved translation of remaining supported reads **and writes**, plus explicit closure of old-binary rollback before retiring storage separately from public contracts.
- Quarantine installed before old workers touch new-only states (such as a readable `pending` projection that could duplicate an external effect).
- Satisfied backup restore, retention, deletion, legal-hold, and audit obligations.

Finish by updating ownership and architecture records, naming an owner and deadline for deferred cleanup.

## Completion gate

A migration plan is ready when invariants hold throughout every phase, cutover drains in-flight writes before enabling target writes, abort thresholds are quantitative (`Proposed` if unsupplied), the last safe rollback point precedes irreversible effects (with forward repair beyond it), and schema/system contraction gates on measured zero legacy traffic rather than a calendar date.
