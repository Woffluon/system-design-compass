# Architecture review workflow

Use this mode to assess an existing repository, design document, deployed system, or proposed architecture. The objective is decision support, not a generic best-practices checklist.

## Define the review

Establish the review question, business criticality, lifecycle stage, and evidence available. A pre-launch design review, incident-driven review, cost review, and modernization assessment require different depth.

Treat evidence in this order:

1. Executable behavior, configuration, schema, infrastructure, and tests.
2. Production telemetry, incident records, capacity data, and runbooks.
3. Current architecture and decision documents.
4. Stakeholder statements.
5. Explicit reviewer assumptions.

When sources conflict, report the conflict. Do not treat a stale diagram as implementation truth or missing documentation as proof that a control is absent.

## Trace the system before judging it

Map the smallest set of flows needed to answer the review question:

- An externally initiated request from entry point to response.
- A state-changing operation through persistence and downstream effects.
- An asynchronous job or event through acknowledgement, retry, and terminal failure.
- Authentication to authorization at the protected resource.
- Deployment and rollback through health evaluation.

Identify trust boundaries, data ownership, synchronous dependency depth, queues, caches, consistency boundaries, shared failure domains, and operational owners. Confirm what is shared across tenants, regions, or critical workloads.

## Evaluate consequential risks

Apply only relevant lenses:

- **Correctness:** invariants, concurrency control, ordering, duplicate handling, reconciliation, and source of truth.
- **Reliability:** SLO feasibility, dependency budgets, overload behavior, isolation, redundancy, recovery, and operability.
- **Performance:** critical path, fan-out, contention, hot keys, amplification, payload size, and capacity headroom.
- **Security and privacy:** identity, authorization, secrets, trust boundaries, data classification, retention, abuse, and auditability.
- **Data:** ownership, schema evolution, consistency, retention/deletion, backup restoration, and migration safety.
- **Delivery:** coupling, compatibility, testability, observability, rollout, rollback, and blast radius.
- **Cost and sustainability:** dominant unit costs, idle baseline, growth multipliers, egress, retention, and waste.
- **Complexity:** components or abstractions whose operational cost is not justified by a requirement.

Do not demand maximum maturity in every dimension. Judge the design against its actual criticality, stage, and constraints.

## Write actionable findings

Every finding must contain:

- **Title:** concrete failure or decision gap, not a category label.
- **Priority:** `P0` imminent catastrophic exposure, `P1` high-probability or high-impact blocker, `P2` material but schedulable risk, or `P3` improvement.
- **Evidence:** file/line, artifact section, metric, incident, or named assumption.
- **Trigger:** the condition under which the problem occurs.
- **Impact:** affected invariant, user journey, SLO, security property, cost, or recovery objective.
- **Recommendation:** the smallest change that removes or measures the risk.
- **Validation:** a test, query, load experiment, failure exercise, or rollout signal.

Use calibrated language. Distinguish demonstrated defects from plausible risks and missing evidence. Consolidate findings with the same cause instead of inflating the count.

## Finish with a verdict

Summarize:

- The architecture's current fitness for the stated goal.
- The strongest existing decisions worth preserving.
- Blocking risks and the minimum pre-launch or pre-migration actions.
- Non-blocking follow-ups ordered by risk reduction per unit effort.
- Unknowns that require telemetry, stakeholder input, or experiments.

When no actionable finding exists, say so and describe the evidence reviewed. Do not manufacture recommendations to make the review appear thorough.
