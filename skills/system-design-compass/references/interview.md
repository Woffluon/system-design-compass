# System design interview workflow

Use this secondary mode only for interview practice or an explicitly time-boxed design exercise. Optimize for clear reasoning and prioritization, not production-document completeness.

## Default 45-minute structure

- **0–5 minutes — Frame:** users, core journeys, scope, and the two or three most important quality attributes.
- **5–10 minutes — Estimate:** peak traffic, storage, bandwidth, and concurrency only where they drive design.
- **10–20 minutes — High level:** APIs, main data model, system boundary, write/read flows, and a simple diagram.
- **20–35 minutes — Deep dives:** choose the hardest two issues, such as partitioning, ranking, delivery semantics, consistency, or hot-key control.
- **35–42 minutes — Failures and scale:** bottlenecks, overload, redundancy, recovery, security, and observability.
- **42–45 minutes — Close:** decisions, trade-offs, remaining risks, and how the design evolves at the next scale threshold.

Adjust proportions to the interviewer's signals. Do not spend early time naming products, drawing every service, or calculating figures that cannot affect a decision.

## Candidate behavior

Ask a small number of high-leverage questions, state assumptions aloud, and keep a visible requirement list. Start with a coherent baseline and evolve it when a limit appears. Explain why each component exists and what simpler alternative was rejected.

When the prompt is underspecified, select reasonable interview assumptions instead of interrogating indefinitely. Invite correction. Maintain a short parking lot for secondary concerns.

## Evaluation rubric

Assess the result on:

- Requirement discovery and scope control.
- Quantitative reasoning with correct units and plausible peaks.
- Coherent contracts, data model, and end-to-end flows.
- Correct identification of invariants and consistency boundaries.
- Trade-off quality rather than technology-name density.
- Recognition of bottlenecks, partial failures, and operational needs.
- Clear communication, time management, and response to new constraints.

After the exercise, give specific feedback: one strength to preserve, the highest-impact missed decision, any incorrect assumption, and the next practice target. Distinguish interview simplifications from production requirements.
