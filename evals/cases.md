# Behavioral evaluation cases

These cases evaluate decisions and observable behavior, not exact wording. Run each case in an isolated project with `system-design-compass` installed. Give the agent only the setup and prompt; do not reveal the rubric until after it answers.

Score each required behavior as pass or fail. A case passes when every **critical** behavior and at least 80% of all listed behaviors pass. A release passes when all eight cases pass and no unsafe behavior appears.

The runnable single-turn adaptations are in [regression.json](regression.json), with the comparative protocol in [README.md](README.md). The [2026-10-01 follow-up](results/2026-10-01.md) reports the current comparison and its boundaries. The [2026-09-30 results](results/2026-09-30.md) document incomplete coverage and failures; they do not certify a release.

## Scenario index

| Case | Decision under test |
|---|---|
| 1 | [Ambiguous greenfield system](#case-1-ambiguous-greenfield-system) |
| 2 | [Evidence-based architecture review](#case-2-evidence-based-architecture-review) |
| 3 | [Monolith evolution](#case-3-monolith-evolution) |
| 4 | [Payment and wallet correctness](#case-4-payment-and-wallet-correctness) |
| 5 | [Realtime location privacy](#case-5-realtime-location-privacy) |
| 6 | [Narrow ADR](#case-6-narrow-adr) |
| 7 | [Current provider comparison](#case-7-current-provider-comparison) |
| 8 | [Time-boxed interview](#case-8-time-boxed-interview) |

## Case 1: Ambiguous greenfield system

**Setup:** No repository. The requester says the product is important but supplies no scale or criticality.

**Prompt**

```text
Design a multi-tenant webhook delivery platform.
```

**Required behavior:**

- **Critical:** asks one compact batch about delivery semantics, tenant isolation, scale, latency, retention, endpoint security, and failure tolerance, or clearly labels reasonable assumptions when interaction is unavailable.
- Defines accepted-versus-delivered state, idempotency, retry ownership, terminal failure, and per-tenant fairness.
- Shows auditable low/base/high throughput and storage estimates rather than invented exact figures.
- Starts with a minimal capability architecture and explains when partitioning or cells become necessary.
- Covers endpoint abuse, secret handling, observability, replay, rollout, rollback, and cost drivers.

> **Unsafe behavior:** claims exactly-once delivery without an atomic boundary; picks vendor products before requirements.

## Case 2: Evidence-based architecture review

**Setup:** Provide a small repository where every tenant is routed by creation month and a single synchronous request fans out to six dependencies. Provide no production telemetry.

**Prompt**

```text
Review this architecture for scale and reliability risks.
```

**Required behavior:**

- **Critical:** cites exact repository evidence for demonstrated findings.
- Separates missing telemetry from a proven defect.
- Identifies temporal partition hotspot risk and synchronous dependency-budget risk with concrete triggers and impacts.
- Prioritizes findings and recommends the smallest useful correction or experiment.
- Preserves sound existing decisions instead of proposing a wholesale rewrite.

> **Unsafe behavior:** asserts an outage or compliance breach without evidence.

## Case 3: Monolith evolution

**Setup:** A monolith owns orders and sends email synchronously. The goal is asynchronous fulfillment without downtime; old mobile clients can remain active for 90 days.

**Prompt**

```text
Create an implementation-ready migration plan.
```

**Required behavior:**

- **Critical:** states throughout-migration invariants and the source of truth for every phase.
- Uses compatible expand-migrate-contract steps and accounts for old clients.
- Defines an outbox or another justified atomic publication boundary.
- Includes cohorting, observation windows, abort thresholds, reconciliation, and tested rollback.
- Does not remove the old contract before usage and compatibility evidence permit it.

> **Unsafe behavior:** proposes unguarded dual writes or calls deployment rollback sufficient after incompatible data writes.

## Case 4: Payment and wallet correctness

**Setup:** A user may retry transfers after timeouts; an external payment provider sends duplicate and out-of-order webhooks.

**Prompt**

```text
Design the payment and wallet state model.
```

**Required behavior:**

- **Critical:** defines authorization, idempotency scope, stable operation identity, monetary units, and balanced ledger invariants.
- Models provider timeout as ambiguous rather than failed.
- Uses explicit state transitions and immutable postings or an equally auditable model.
- Includes duplicate/out-of-order webhook handling and reconciliation to provider statements.
- Covers concurrency, reversals/refunds, audit, security, and recovery.

> **Unsafe behavior:** uses binary floating point for money or mutates historical ledger entries.

## Case 5: Realtime location privacy

**Setup:** Users can opt in to share proximity with friends. Exact coordinates are not required in the UI.

**Prompt**

```text
Design nearby-friends updates for five million daily users.
```

**Required behavior:**

- **Critical:** treats location and relationship authorization as sensitive, revocable data.
- Defines precision, freshness, retention, block/revocation propagation, and inference risks.
- Estimates update and fan-out shape with peak and density skew.
- Compares pull, geocell pub/sub, and a reasonable hybrid without pretending there is one universal answer.
- Covers hot cells, reconnect storms, stale presence, battery/network cost, and degraded behavior.

> **Unsafe behavior:** retains exact location indefinitely without a supplied requirement.

## Case 6: Narrow ADR

**Setup:** A team needs to decide whether thumbnail generation belongs in an upload request or an asynchronous worker. Inputs are already durable before processing.

**Prompt**

```text
Should thumbnail generation be synchronous or queue-backed? Write the decision.
```

**Required behavior:**

- **Critical:** produces a concise ADR rather than a full system RFC.
- States latency, failure isolation, completion visibility, retry/idempotency, and operating-cost drivers.
- Chooses an option under explicit assumptions and records consequences.
- Gives a measurable reconsideration trigger.

> **Unsafe behavior:** adds unrelated microservices or infrastructure.

## Case 7: Current provider comparison

**Setup:** Browsing is available. The requester names two current managed queue products and asks which supports a specific ordering and retention requirement.

**Prompt**

```text
Compare the current managed options and recommend one for these requirements.
```

**Required behavior:**

- **Critical:** verifies version-sensitive limits in current official vendor documentation and cites the decisive pages.
- Separates documented facts, inference, and unknown account/region constraints.
- Compares required capabilities and failure semantics before price or popularity.
- Avoids claiming universal superiority and states a reconsideration trigger.

> **Unsafe behavior:** relies on memory, secondary comparison blogs, or uncited exact limits.

## Case 8: Time-boxed interview

**Setup:** A 45-minute interview practice session; no real implementation will follow.

**Prompt**

```text
Run a system design interview for search autocomplete, then grade my approach.
```

**Required behavior:**

- **Critical:** uses a time-boxed interview flow and asks only high-leverage scoping questions.
- Guides requirement, estimation, high-level design, focused deep dives, and failure analysis.
- Distinguishes acceptable interview simplifications from production obligations.
- Grades reasoning, invariants, trade-offs, and communication rather than technology-name count.
- Ends with one concrete strength, highest-impact gap, and next practice target.

> **Unsafe behavior:** reveals the entire target answer before allowing the candidate to reason.

## Release review

After running the cases, also inspect:

- Whether the skill loaded only relevant references.
- Whether output language followed the user.
- Whether facts, assumptions, decisions, and open questions were distinguishable.
- Whether diagrams added information and had a readable text explanation.
- Whether any instruction authorized code or external changes that the prompt did not request.
