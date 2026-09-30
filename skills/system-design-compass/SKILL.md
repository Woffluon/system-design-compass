---
name: system-design-compass
description: Resolve architecture decisions in production system design, reviews, migrations, and scaling. Use for RFCs, ADRs, architecture assessments, migration plans, or system design interviews. Excludes routine implementation without an architectural decision.
license: MIT
metadata:
  author: Woffluon
  version: "1.1.0-rc.1"
---

# System Design Compass

> Resolve the requested decision with the simplest sufficient design. User instructions and established project decisions take precedence. Inspect available evidence before asking discoverable questions. Respond in the user's language.

## Load only decision-relevant guidance

For a narrow question or ADR, answer directly when evidence suffices; no mode or template is mandatory. For broader work, select the relevant workflow:

- [Design](references/design.md), [review](references/review.md), [evolution](references/evolve.md), or explicitly requested [interview](references/interview.md).

**Open a reference only for a question it can resolve.** Prefer its relevant section when tools support selective reads. Avoid bulk reads and rereading unchanged material.

- SLOs, demand, units: [estimation](references/requirements-estimation.md).
- Ownership, contracts, state: [interfaces/data](references/interfaces-data.md).
- Replication, queues, leases, overload: [distributed systems](references/distributed-systems.md).
- Recovery, security, observability, cost: [production readiness](references/production-readiness.md).
- Requested document or diagram conventions: [deliverables](references/deliverables-diagrams.md).
- A mechanism lacks actionable recovery or proof: [decision validation](references/decision-validation.md).

For workload-specific unknowns, select the relevant archetype section:

- [Platform](references/archetypes-foundations-platform.md), [realtime](references/archetypes-user-facing-realtime.md), [infrastructure](references/archetypes-data-infrastructure.md), [transactional](references/archetypes-transactional-financial.md).

## Resolve a difficult decision

Deepen when evidence conflicts, a guarantee lacks an enforcement boundary, option selection depends on missing information, or reasoning repeats without progress:

1. Narrow the unresolved decision and name the invariant and authoritative owner.
2. Construct a concrete event sequence that could break the proposal: concurrent operation, crash, timeout, stale owner, or incompatible write.
3. Identify the smallest observation, calculation, primary-source check, or experiment that distinguishes credible options, including the simple baseline.
4. State the selected mechanism, enforcement boundary, accepted downside and measurable reconsideration trigger tied to the requirements.

Stop when evidence resolves the decision. If investigation produces no new evidence or approach, expose the missing input or experiment; do not repeat the recommendation with more certainty.

## Evidence and completion

Before finishing a consequential recommendation, give one falsifiable experiment: injected condition, observable business outcome and acceptance criterion. For ambiguous outcomes or backlog, also name the repair owner and intervention condition/action. If these are not concrete, read [decision validation](references/decision-validation.md) before answering; calculations and monitoring lists alone do not complete the recommendation. Keep this check compact, not a full test plan.

Distinguish facts, assumptions, decisions and unknowns without mandatory headings. **Missing evidence is not a defect.** Cite findings to actual artifacts. Quantify decision-driving claims with units and ranges. Prefer capabilities before products; verify changing product guarantees in current official documentation. If tools are unavailable, disclose uncertainty. Cover consequential failure, recovery and rollout risks proportionately. Keep output scoped to the requested artifact; do not change application code or external systems without an implementation request.
