# Incident and Postmortem Remediation

Use this reference when reviewing an outage, near-miss, or Correction of Error (COE) draft to turn root causes into durable architectural fixes and verification schedules. Skip it for greenfield designs with no incident history.

**Contents:** [Timeline and stopping rule](#build-a-single-timezone-timeline-and-halt-human-error-stops) · [Dark debt and strange loops](#audit-for-dark-debt-and-strange-loops) · [Six action classes](#assign-six-bounded-action-item-classes) · [Error budgets and fail-closed](#enforce-error-budget-freezes-and-fail-closed-boundaries) · [Fault-schedule oracles](#verify-fixes-with-fault-schedule-and-canary-oracles) · [Postmortem template](#portable-postmortem-remediation-template)

## Build a single-timezone timeline and halt human-error stops

Record every incident timeline in one timezone (**`UTC`**), starting from the **initial trigger** (`T0`, when the latent defect or bad change entered the system) rather than when the first customer alert fired. Break down **MTTD** (mean time to detect), **TTD** (time to detect), and **TTM** (time to mitigate), then state the concrete design change that cuts TTD and TTM in half.

**Apply the "human error" stopping rule:** never terminate causal analysis at "operator ran the wrong command" or "engineer pushed an empty config." Treat human action as an expected input and ask why the system failed to reject an irreversible or high-blast-radius operation **fail-closed**.

## Audit for dark debt and strange loops

Inspect incident mechanics for two compounding traps:

- **Dark debt:** hidden hazards accumulated during normal operation that surface only under rare combinations—such as an empty allowlist, selector, or tenant filter defaulting to a wildcard (`match-all` / fail-open) in a cleanup or routing job.
- **Strange loops:** recovery, rollback, or admin control paths that depend on the same data-plane component currently failing. **Counterexample:** a Redis or auth outage blocks the admin rollback console because the console authenticates or reads feature flags from that broken Redis/auth cluster. Break strange loops with an isolated control plane, static emergency overrides, or locally verified break-glass credentials.

## Assign six bounded action-item classes

Replace vague tasks ("add unit tests", "be more careful") with concrete items mapped to the six action classes:

- **`Investigate`:** resolve open causal questions or missing telemetry before locking a permanent fix.
- **`Mitigate-Now`:** immediate containment that stops ongoing customer harm.
- **`Repair`:** reconcile corrupted state, stuck queues, or inconsistent customer data.
- **`Detect-Future`:** reduce TTD via leading-indicator alerts, invariants, or anomaly thresholds.
- **`Mitigate-Future`:** reduce TTM and bound blast radius (automated pause, isolated recovery path, circuit breaker).
- **`Prevent-Future`:** remove the failure class structurally (fail-closed validation, schema guard, or decoupled control boundary).

Assign every item a **`P0`–`P3` priority**, **one named owner** (team or role, never a shared alias), a **measurable completion boundary**, and **sibling-workload propagation**: scan peer services, cron jobs, and queues for the same vulnerable pattern and apply the fix across siblings proactively.

## Enforce error budget freezes and fail-closed boundaries

Bind remediation priority to the service's **error budget (`1 - SLO`)**. When an incident exhausts the error budget, freeze non-reliability feature launches and allocate engineering capacity exclusively to `Prevent-Future` and `Mitigate-Future` work until SLO margin recovers.

Harden every configuration loader, CLI, and batch job with **fail-closed input boundaries**. Empty target lists, missing tenant scopes, or unparseable limits must abort execution with zero mutations unless an explicit, auditable override flag is validated.

## Verify fixes with fault-schedule and canary oracles

Do not write regression tests that only replay the exact fixed input from the outage. Build a **fault-schedule oracle**—following [decision validation](decision-validation.md#turn-a-claim-into-observable-evidence) and [overload rules](distributed-systems.md#overload-and-partial-failure)—that exercises execution schedules across:

- **Sub-timeout latency:** slow dependency responses just inside caller timeouts that trigger retry storms and worker-pool saturation.
- **Full timeout:** ambiguous remote outcomes that test reconciliation and fencing.
- **Fail-stop:** hard crashes of the data plane while verifying that isolated emergency controls still respond within budget.
- **5% blast-radius canary guard (`Proposed`):** automated rollback or job pause triggered when canary error, deletion rate, or latency exceeds bounds before reaching 100% of tenants.

## Portable postmortem remediation template

Use this structured summary when handing off postmortem findings to implementation or specification agents:

```markdown
**Postmortem Remediation Package**
- **Single-Timezone Summary (UTC):** `T0=<initial trigger>`, `TTD=<duration>`, `TTM=<duration>`
- **Halted Human-Error Assumption:** `<irreversible action the system must reject fail-closed>`
- **Dark Debt / Strange Loop Found:** `<fail-open default or recovery-plane dependency on broken data plane>`
- **Action Items:**
  | ID | Class | Priority | Owner | Bounded Surgical Change | Sibling Workload Scan |
  |---|---|---|---|---|---|
  | AI-1 | Prevent-Future | P0 | `<role/team>` | `<fail-closed boundary>` | `<peer jobs/services>` |
- **Error Budget and Canary Oracle:** `<sub-timeout latency, full timeout, fail-stop; 5% blast-radius guard (Proposed)>`
```
