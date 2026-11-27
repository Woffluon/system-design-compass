# Architecture review workflow

> Assess a repository, design document, deployed system, or proposal for decision support rather than a generic checklist.

**Contents:** [Rank evidence](#rank-evidence-and-separate-unknowns-from-defects) · [Critical paths](#trace-critical-paths-and-authoritative-state-owners) · [Call graphs & blind spots](#trace-call-graphs-and-report-static-blind-spots) · [Consequential risks](#evaluate-consequential-risks-with-violating-event-sequences) · [Findings & experiments](#pair-each-finding-with-the-smallest-surgical-fix-and-a-falsifiable-experiment) · [Verdict](#deliver-a-verdict-that-preserves-sound-decisions) · [Completion gate](#completion-gate)

## Rank evidence and separate unknowns from defects

Define the review question, criticality, lifecycle stage, and evidence. Rank sources in order:

1. Executable code, configuration, schema, infrastructure, and tests.
2. Production telemetry, incidents, capacity data, and runbooks.
3. Architecture and decision documents.
4. Stakeholder statements.
5. Explicit reviewer assumptions.

Report source conflicts directly. Separate demonstrated facts, conditional assumptions, and explicit unknowns. Never treat a stale diagram as implementation truth, and **never report missing evidence or absent documentation as a fabricated defect**—classify it as an explicit unknown or conditional assumption.

## Trace critical paths and authoritative state owners

In large repositories (`500+` files), start with scoped search (`rg`) targeting entrypoints, schemas, retry/client wrappers, and deployment config rather than reading every file. Map the minimum flows answering the review question:

- External request from entry point to response.
- State mutation through persistence, authoritative ownership, and downstream effects.
- Asynchronous work through ack, retry, and terminal repair or dead-letter handling.
- Authentication to resource-level authorization at the enforcement boundary.
- Deployment, health gate, and rollback boundary.

Identify trust boundaries, **authoritative state owner** per entity, synchronous dependency depth, queues, caches, consistency boundaries, shared failure domains, and tenant/regional isolation.

## Trace call graphs and report static blind spots

In `500+`-file repositories, avoid full-file dumps or arbitrary sampling. Start with hybrid discovery using `rg` plus any available symbol or call-graph index (e.g., Tree-sitter or compiler graph) to pinpoint entry points (`HTTP` handlers, queue consumers, `cron` jobs) and mutation or egress sinks (`INSERT`/`UPDATE`, ledger writes, external API clients). Pull only the relevant symbol bodies and call edges along the path under review.

When LSP `callHierarchy` (`incomingCalls` / `outgoingCalls`) or an AST call graph is available, trace two ways: backward from sensitive sinks to verify auth and retry gates, and forward from entry points to uncover hidden side effects. Check resolution boundaries explicitly—TypeScript/JavaScript barrel `index.ts` re-exports can drop or misroute cross-package edges in large monorepos, and build-tagged files (`_linux.go`, `_windows.go`, or feature-gated targets) drop out of the active compile graph.

Expand the static blast set beyond function calls to include out-of-band runtime contracts: shared database tables and views, message queues and broker topics (matched by `topic`/`queue` name), and `YAML`, `Dockerfile`, or deployment manifests that wire routing, timeouts, retries, or privileges.

Static call graphs are soundy, not complete. Whenever paths cross dynamic dispatch (such as runtime handler maps), reflection, dependency-injection (DI) container bindings, framework lifecycle callbacks, or runtime feature flags, never claim full static coverage. Separate proven paths from unverified gaps under an explicit `[Blind Spot / Soundiness Boundary]` section, inspect dynamic registration sites manually where feasible, and never invent assumptions for unverified files or unresolved edges.

Format call-graph review findings so downstream coding or specification agents can act without re-deriving context:

```markdown
**[P0|P1|P2|P3] <Concrete failure mode or authorization gap>**
- **Evidence & Call Chain:** `<entrypoint symbol -> middleware/layer -> mutation file:line>`
- **Blind Spot / Soundiness Boundary:** `<dynamic dispatch, DI binding, reflection, inactive build tag, or YAML/DB coupling>`
- **Violating Sequence:** `<step-by-step race, retry, or auth-bypass sequence>`
- **Impact:** `<broken invariant, SLO, or security boundary>`
- **Smallest Surgical Fix:** `<minimum file/boundary change without adding new components>`
- **Pass/Fail Oracle:** `<fault or load injection schedule and deterministic pass/fail criterion>`
```

## Evaluate consequential risks with violating event sequences

Apply only lenses matching criticality, stage, and constraints:

| Lens | Risk to examine |
|---|---|
| **Correctness** | invariants, authoritative state owner, concurrency, ordering, idempotency, reconciliation. |
| **Reliability** | SLO feasibility, dependency budgets, overload shedding, isolation, redundancy, recovery. |
| **Performance** | critical-path latency, fan-out, contention, hot keys, retry amplification, payload size, headroom. |
| **Security and privacy** | actor/resource authorization, secrets, trust boundaries, classification, retention, abuse, auditability. |
| **Data** | ownership, schema evolution, consistency, retention/deletion, backup restore, migration safety. |
| **Delivery** | coupling, mixed-version compatibility, testability, observability, rollout gates, rollback blast radius. |
| **Cost and sustainability** | dominant unit costs, idle baseline, growth multipliers, egress, retention, waste. |
| **Complexity** | components or abstractions not justified over a simpler baseline. |

Before declaring a correctness or reliability defect, construct the **violating event sequence** (race, crash, timeout, stale owner, or partial write) breaking the invariant.

## Pair each finding with the smallest surgical fix and a falsifiable experiment

Every finding requires:

| Field | Required content |
|---|---|
| **Title** | concrete failure mode or decision gap, not a category label. |
| **Priority** | `P0` imminent catastrophic exposure, `P1` high-impact blocker, `P2` material schedulable risk, `P3` minor improvement. |
| **Evidence** | file/line, artifact section, metric, incident, or labeled conditional assumption. |
| **Trigger** | violating event sequence, fault, or load condition producing the failure. |
| **Impact** | affected invariant, journey, SLO, security property, cost, or RTO/RPO. |
| **Recommendation** | **the smallest surgical fix** removing or bounding the risk without unnecessary components. |
| **Validation** | **a falsifiable experiment**—fault schedule, concurrency test, query, or load check with a pass/fail oracle. |

Consolidate findings sharing a root cause. Distinguish demonstrated defects from conditional risks and open unknowns. For narrow single-boundary reviews, report only applicable fields and omit unused template boilerplate.

- **Weak:** "Title: Retry bug. Fix: Introduce Temporal workflow. Validation: Add unit tests."
- **Surgical:** "Title: Post-charge crash duplicates Stripe debits (`orders/pay.py:42`). Fix: Persist `IN_FLIGHT` intent + deterministic `idempotency_key` before HTTP call. Validation: Drop socket after PSP `200 OK`, retry 3x; pass iff PSP charges = 1 and local postings = 1."

## Deliver a verdict that preserves sound decisions

Summarize:

- Current fitness for the stated goal, load, and constraints.
- **Sound existing decisions and simple boundaries to preserve**, protecting working components from churn.
- Blocking (`P0`/`P1`) risks and minimum surgical pre-launch or pre-migration fixes.
- Non-blocking follow-ups ordered by risk reduction per unit effort.
- Explicit unknowns and conditional assumptions requiring telemetry, stakeholder input, or falsifiable experiments.

When no actionable defect exists, state the design is sound and cite reviewed evidence. Never manufacture findings.

## Completion gate

A review is ready when every finding cites verified artifacts or labeled assumptions, every correctness/reliability defect includes a violating event sequence, each fix is the smallest surgical change with a pass/fail oracle, sound decisions are explicitly preserved, and missing documentation is labeled unknown rather than reported as a defect.
