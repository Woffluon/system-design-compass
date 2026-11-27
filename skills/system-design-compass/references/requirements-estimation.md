# Requirements and estimation

> Use this reference when requirements are vague, quality attributes drive architecture, or scale must be quantified.

**Contents:** [Requirements](#turn-goals-into-requirements) · [Service objectives](#define-service-objectives-from-user-experience) · [Estimation & capacity](#estimate-only-decision-driving-quantities) · [Sanity checks](#sanity-check-the-model)

## Turn goals into requirements

Prioritize functional journeys, measurable quality attributes, fixed constraints, and explicit non-goals as critical, important, or optional; if everything is highest priority, no trade-off can be made. Express critical quality attributes as a six-field scenario:

| Field | Question |
|---|---|
| Source | Who or what triggers the stimulus? |
| Stimulus | Request, load spike, fault, attack, or change? |
| Environment | Normal, peak, degraded dependency, recovery, or deploy? |
| Artifact | Which service, store, interface, or journey is affected? |
| Response | What action must the system take? |
| Measure | What observable threshold proves success? |

## Define service objectives from user experience

Measure SLIs at the user-experienced boundary:

- Availability or success ratio for eligible requests.
- Latency percentiles by operation and payload class.
- Freshness or propagation lag.
- Durability or accepted-write loss.
- Correctness, reconciliation discrepancy, or duplicate-effect rate.
- Throughput or deadline completion for batch and stream workloads.

For each SLO state population, success condition, threshold, window, exclusions, and measurement point. Set stricter internal component targets only when an end-to-end dependency budget requires them.

Availability error budget:

```text
allowed_bad_fraction = 1 - SLO
allowed_bad_events = eligible_events × allowed_bad_fraction
```

Ground SLOs in user harm, business cost, dependency limits, and staffing rather than habit.

State stateful RTO and RPO targets per failure scope (process, node, zone, region, provider, corruption, operator error).

## Estimate only decision-driving quantities

State input variables explicitly, apply dimensional analysis, and separate average from peak.

### Derive peak attempt demand and backlog drain under duplicates and retries

Derive queue and worker math from supplied input variables. **Do not invent unmeasured worker concurrency, service latency, or per-worker throughput:** when a numeric drain time or worker count depends on an unmeasured latency, timeout, or concurrency limit, keep the formula symbolic in terms of the unknown variable, bound it as an explicit assumption range, or require measurement before claiming capacity sufficiency.

When a stated worker rate is ambiguous between raw attempts and successful completions while failed attempts consume full worker time, treat the rate as **raw attempt capacity** (conservative primary baseline) and note the optimistic alternative in one line instead of duplicating full calculations.

Expand unique arrivals by duplicate deliveries and retry amplification:

```text
accepted_rate = unique_arrival_rate × (1 + duplicate_fraction)
peak_accepted_rate = peak_unique_arrival_rate × (1 + duplicate_fraction)
peak_attempt_demand = peak_accepted_rate × (1 + retry_amplification_factor)
                    = peak_unique_arrival_rate + peak_duplicate_rate + peak_retry_rate
```

Keep unique unfinished jobs separate from attempt-queue entries over any interval:

```text
unfinished_job_growth = new_job_arrivals - successful_job_completions
attempt_queue_growth = new_job_arrivals + duplicate_arrivals + retry_returns - attempt_departures
```

Do not add retry returns after already discounting attempt capacity to net successful completions; that counts failures twice. During overload, demanded attempts exceed executed attempts.

Subtract the stated worker/zone failure allowance before computing degraded drain capacity (canonical recovery inequality: `completion_rate > arrival_rate + retry_rate`):

```text
available_workers = provisioned_workers × (1 - failure_allowance)
degraded_attempt_capacity = available_workers × per_worker_attempt_rate
completion_rate > arrival_rate + retry_rate
net_drain_rate = completion_rate - (arrival_rate + retry_rate)
net_attempt_drain_rate = degraded_attempt_capacity - (arrival_rate + duplicate_rate + retry_rate)
time_to_clear_backlog = attempt_backlog / net_attempt_drain_rate
```

When CLI tools are available, run `scripts/capacity_check.py` (stdlib) with
explicit parameters (`--arrival-rate`, `--unit`, `--duplicate-fraction`,
`--retry-factor`, `--workers`, `--failure-allowance`, `--worker-rate`,
`--backlog`, `--format`) to verify degraded attempt capacity, demand, and
drain time. In tool-free chats, show each substitution step explicitly using
`peak_attempt_demand = peak_unique_arrival_rate * (1 + dup) * (1 + retry)`
and `degraded_attempt_capacity = provisioned_workers * (1 - loss) * rate`,
keeping unmeasured variables symbolic rather than inventing numbers.

(Equivalently, in unique-job terms: `net_job_drain_rate = degraded_success_capacity - unique_arrival_rate` and `time_to_clear_backlog = unique_job_backlog / net_job_drain_rate`.) Drain time is unbounded whenever degraded completion capacity does not strictly exceed sustained arrivals plus retries. Recompute proposed remedies under the same degraded failure scenario and reconcile summary totals with this flow balance.

Include in capacity models:

- Active users, operations per journey, and read/write/event fan-out.
- Payload size distributions (p50/p99), not only averages.
- Daily/seasonal peaks, burst duration, and growth horizon.
- Online/batch concurrency, retention, replicas, indexes, logs, backups, and compaction overhead.
- Cache hit/miss ratios, invalidation amplification, and cross-zone/region egress.
- Headroom for failures, deploys, rebalancing, and noisy neighbors.

Use low/base/high ranges for uncertain inputs, name the dominant variable, and round to architecture-scale precision.

## Sanity-check the model

- Cross-check from an independent dimension (e.g., active users × actions versus measured RPS).
- Compare peak attempt demand against the slowest mandatory stage, not just the edge tier.
- Verify units at every step and label decimal (`GB`, `MB/s`) versus binary (`GiB`, `MiB/s`).
- Include replication, duplicate, retry, fan-out, metadata, and index amplification.
- Confirm latency budgets cover network hops, queuing, and serialization as well as storage.
- Check availability against synchronous dependency depth and shared failure domains.
- State the load or data threshold that forces a new partitioning, storage, or delivery strategy.

Present estimates as a decision model ready for telemetry calibration, not as arithmetic certainty.
