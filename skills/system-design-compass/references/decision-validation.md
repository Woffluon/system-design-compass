# Prove a consequential decision

> Read when recovery, falsification, or operator response is unverified. Test actual system invariants without a test-only architecture.

**Contents:** [Observable evidence](#turn-a-claim-into-observable-evidence) · [Ambiguous delivery](#ambiguous-delivery-and-terminal-repair) · [Queue recovery](#queue-recovery-and-operator-action) · [Migration drills](#migration-restart-repair-and-mixed-version-drills)

## Turn a claim into observable evidence

Replace vague wishes ("test retries") with a **concrete fault schedule** (initial state, exact injection point, competing operations, recovery trigger) and an **observable pass/fail business oracle** (durable business state and external effects at a named boundary, not just HTTP 200 or lock acquisition). Name the settled assumption; counterexamples or proposed tests are not passing evidence.

- **Weak (vague wish):** "Test retries and webhook failures under load."
- **Falsifiable:** "Inject socket drop after PSP `200 OK` before local DB commit; run 3 worker retries; pass iff PSP ledger = 1 charge, local postings = 1, orphan `IN_FLIGHT` = 0."

## Ambiguous delivery and terminal repair

Use [external-outcome resolution](interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction) for pre-call intent, remote deduplication, and settlement reconciliation; validate those boundaries with the fault schedule and oracle below.

**Fault schedule (combine for external side effects, queues, and leases):**
1. **Crash after remote success before local record:** commit remote effect, kill worker before local record persists, let replacement retry.
2. **Ambiguous timeout:** drop response past deadline while remote outcome is unknown.
3. **Lease expiry / worker overlap:** stall worker past lease TTL while a replacement claims the same identity concurrently.

**Pass/fail business oracle:** with remote deduplication or fencing, assert one external effect and one converged local status across all three faults. Otherwise, assert ambiguous/overlapping attempts halt into outcome query or reconciliation with zero silent duplicates; never claim exactly-once.

**Recovery oracle:** assert retry exhaustion halts without auto-replaying unknown outcomes as failures and routes records to a named repair owner with reconciliation evidence.

## Queue recovery and operator action

Derive recovery capacity from [peak attempt demand and backlog drain](requirements-estimation.md#derive-peak-attempt-demand-and-backlog-drain-under-duplicates-and-retries) and define age thresholds and intervention owners per [backlog drain intervention](distributed-systems.md#backlog-drain-capacity-and-age-triggered-intervention); verify both with the drill below.

**Fault schedule and oracle:** inject burst, transient errors, and worker loss under continuing normal arrivals; restore workers and measure completions, attempt rate, oldest uncompleted business backlog age, and drain time to steady state. Pass only if drain time and backlog age meet the recovery target with headroom (free storage never proves positive drain capacity).

**Action:** verify alerting fires when oldest uncompleted backlog age breaches completion budget or drain capacity trails arrivals, triggering an owned threshold to restore capacity, throttle admission, or shed optional work (label provisional targets when no SLO exists).

## Migration restart, repair, and mixed-version drills

**Fault schedule:** kill and restart backfill/replication workers mid-flight under concurrent traffic across old and new code (`mixed-version reads and writes`).

**Pass/fail business oracle:**
- **Restart/repair:** resumed checkpoints and repair converge to zero missing, duplicate, or drifted records.
- **Mixed-version reads and writes:** old code reading new/migrated data and **old code writing** alongside new code preserve invariants without silent field loss, schema errors, or unreplicated fallback writes that break rollback.
