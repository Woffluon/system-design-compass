# Prove a consequential decision

> Read when a proposed mechanism appears correct but its recovery, validation or operator response is still unspecified. Reuse the actual system's invariants and constraints; do not introduce a new architecture to make testing easier.

## Turn a claim into observable evidence

Choose the event sequence that could falsify the guarantee. State the initial data, injected fault or competing operation, observation boundary and expected outcome. Check durable business state or externally visible effects, not merely a successful API response or lock acquisition. Identify which assumption the result settles. A suggested experiment is not evidence that it passed.

## Ambiguous delivery and terminal repair

**Evidence needed:** durable operation identity, remote deduplication capability, retry horizon, outcome query and repair owner. Use [interfaces/data](interfaces-data.md) for contract semantics.

> **Counterexample:** the receiver applies an effect; its response is lost; the worker crashes before recording completion; a replacement retries. Local deduplication cannot prove a single remote effect.

**Experiment:** repeat that sequence with overlapping workers and the same identity. With cooperative receiver deduplication, assert one visible effect and convergence of local status. Without it, measure the permitted duplicates and preserve ambiguity; do not claim exactly-once behavior.

**Recovery:** exhaustion must expose an actionable record, not hide work in a dead-letter queue. Name the responsible role, evidence needed to reconcile and when replay is permitted. Unknown outcomes must not be treated as proven failures; replay of a non-deduplicating effect may repeat it.

## Queue recovery and operator action

**Evidence needed:** job arrival rate, attempt capacity at the actual payload distribution, retry work, failed-worker capacity, backlog age and completion/drain objective. Keep jobs and attempts in consistent units; use [estimation](requirements-estimation.md) for the demand model.

> **Counterexample:** a healthy queue grows indefinitely after worker loss even though storage remains available. Buffer size does not establish positive drain capacity.

**Experiment:** inject a finite burst, transient failures and worker loss together; restore the worker and measure sustained completions, attempt rate, oldest age and time to drain while normal arrivals continue. Accept only the stated recovery objective with headroom; do not stop measurement at the end of the burst.

**Action:** alert when oldest age exceeds the agreed completion budget, or when measured capacity cannot drain arrivals. Name an owner and a bounded action: restore capacity, throttle admission or defer optional work. If the budget is absent, expose it as a decision input or label a provisional target; never invent an established SLO.
