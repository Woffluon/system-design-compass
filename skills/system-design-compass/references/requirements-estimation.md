# Requirements and estimation

> Use this reference when requirements are vague, quality attributes drive architecture, or scale must be quantified.

## Turn goals into requirements

Start from user and business outcomes. Separate:

- **Functional requirements:** observable journeys, commands, queries, integrations, and administrative operations.
- **Quality attributes:** measurable behavior under a stated condition.
- **Constraints:** fixed deadlines, skills, vendors, protocols, jurisdictions, budgets, and legacy contracts.
- **Non-goals:** plausible work intentionally excluded.

Prioritize each item as critical, important, or optional. If every attribute is highest priority, no trade-off can be made.

Write a quality-attribute scenario with six fields when precision matters:

| Field | Question |
|---|---|
| Source | Who or what creates the stimulus? |
| Stimulus | What happens: request, load spike, fault, attack, or change? |
| Environment | Normal operation, peak, degraded dependency, recovery, or deployment? |
| Artifact | Which service, data set, interface, or journey is affected? |
| Response | What should the system do? |
| Measure | What observable threshold proves success? |

## Define service objectives from user experience

Choose indicators that represent successful user journeys, preferably measured at the boundary the user experiences. Common indicators include:

- Availability or success ratio for eligible requests.
- Latency distribution by operation and payload class.
- Freshness or propagation delay.
- Durability or accepted-write loss.
- Correctness, reconciliation discrepancy, or duplicate-effect rate.
- Throughput or deadline completion for batch and streaming work.

For each SLO state the population, success condition, threshold, window, exclusions, and measurement point. Keep internal component targets stricter only when an end-to-end dependency budget requires it.

Error budget for an availability target:

```text
allowed_bad_fraction = 1 - SLO
allowed_bad_events = eligible_events × allowed_bad_fraction
```

Do not choose an SLO from habit or current performance. Tie it to user harm, business cost, dependency limits, staffing, and the cost of improvement.

Set recovery targets for stateful or critical systems:

| Recovery objective | Definition |
|---|---|
| **RTO** | maximum acceptable time to restore the capability. |
| **RPO** | maximum acceptable interval of data loss measured from the disruption. |

Define which failure scope they apply to: process, node, zone, region, provider, corruption, or operator error.

## Estimate only decision-driving quantities

State inputs and use dimensional analysis. Keep average and peak separate.

```text
average_rate_per_second = events_per_period / seconds_per_period
peak_rate = average_rate × peak_factor
concurrency ≈ arrival_rate_per_second × average_time_in_system_seconds
raw_storage = records × average_record_bytes
retained_storage = ingest_rate_bytes_per_second × retention_seconds
effective_storage = raw_storage × replication_or_erasure_overhead × index_factor
network_rate = messages_per_second × average_payload_bytes
```

For queues:

```text
net_drain_rate = consumer_capacity - producer_rate
time_to_clear_backlog = backlog / net_drain_rate
```

The result is unbounded when consumer capacity does not exceed sustained producer rate. Use peak duration and burst absorption to size buffers; do not hide permanent under-capacity behind a large queue.

Distinguish provisioned workers from available workers: subtract the stated failure allowance before multiplying per-worker capacity. Recompute the proposed remedy under the same failure scenario; healthy-state sizing cannot prove degraded recovery.

Keep unique unfinished jobs separate from attempt-queue entries. With immediate retries, reconcile either accounting model over the same interval:

```text
unfinished_job_growth = new_job_arrivals - successful_job_completions
attempt_queue_growth = new_job_arrivals + retry_returns - attempt_departures
```

Do not add retry returns after already discounting attempt capacity to successful completions: that counts failures twice. During overload, required attempts are not attempts actually executed. Cross-check decision-driving totals against this flow balance and reconcile introductory estimates with the detailed calculation before recommending capacity.

Estimate:

- Active users and operations per journey.
- Read/write/event mix and fan-out amplification.
- Payload and object-size distributions, not only averages.
- Daily/seasonal peaks and growth horizon.
- Online and batch concurrency.
- Retention, replicas, indexes, versions, logs, backups, and compaction overhead.
- Cache hit/miss traffic and invalidation amplification.
- Cross-zone or cross-region bandwidth and egress.
- Headroom for failure, deployments, rebalancing, and noisy neighbors.

Use low/base/high ranges for uncertain inputs and show which variable dominates. Round results to architecture-scale precision.

## Sanity-check the model

- Recalculate using an independent dimension, such as users × actions and measured requests per second.
- Compare peak throughput to the slowest mandatory stage, not just the edge tier.
- Check units at every step and label decimal versus binary storage units.
- Include replication, retry, fan-out, metadata, and index amplification.
- Check that latency budgets leave time for network and serialization, not only storage.
- Check availability against synchronous dependency depth and common failure domains.
- Identify the threshold that would force a different partitioning, storage, or delivery strategy.

Present estimates as a decision model that maintainers can replace with telemetry, not as forecasts guaranteed by arithmetic.
