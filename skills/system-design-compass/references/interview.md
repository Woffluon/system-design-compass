# System design interview workflow

> Use only for interview practice or time-boxed design exercises. Optimize for clear reasoning and prioritization over document length.

## Allocate the 45-minute decision budget

| Phase | Focus |
|---|---|
| **0–5 min — Frame** | users, core journeys, non-goals, invariants, and top two or three measurable quality attributes. |
| **5–10 min — Estimate** | peak read/write rates, storage, bandwidth, and concurrency only where they change a design boundary. |
| **10–20 min — Baseline and contracts** | APIs, data model, **authoritative state owner** per entity, write/read flows, and **simple baseline** diagram. |
| **20–35 min — Deep dives and failure proofs** | resolve the hardest two decisions via a **violating event sequence** (race, crash, timeout, stale owner, hot key) against the **simple baseline**. |
| **35–42 min — Bottlenecks and recovery** | overload shedding, fault isolation, reconciliation/repair, security boundary, and key SLIs. |
| **42–45 min — Close** | trade-offs, accepted downsides, and measurable triggers for the next scale threshold. |

Adapt pacing to interviewer signals. Skip early product naming, speculative microservices, and non-decisive math.

## Defend decisions against the simple baseline

Ask high-leverage questions, state assumptions aloud, and track requirements and invariants visibly. Start with a coherent **simple baseline** and add components only when quantitative demand or a **violating event sequence** proves it insufficient. Name the **authoritative state owner** for every critical write, justify rejecting simpler alternatives with evidence, and park secondary concerns.

## Grade reasoning and trade-off rigor

Assess:

- Requirement discovery, invariant clarity, and scope control.
- Decision-driving estimation with explicit units.
- Coherent contracts, data model, **authoritative state ownership**, and end-to-end flows.
- Stress-testing guarantees against concrete **violating event sequences**.
- Evidence-backed comparisons against the **simple baseline** over technology-name density.
- Bottleneck, partial-failure, overload, and recovery handling.
- Clear communication, time discipline, and adaptation to new constraints.

Give specific feedback: one strength to preserve, the highest-impact missed decision or broken invariant, any flawed assumption, and the next practice target, distinguishing interview simplifications from production requirements.
