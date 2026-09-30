# Comparative evaluation

**Measure decisions and context together.** Compare frozen skill versions in equivalent sessions, grade without condition labels, and keep invalid attempts visible.

[Cases](#choose-the-cases) · [Run](#record-subjects) · [Grade](#grade-without-condition-labels) · [Accept](#apply-the-release-gate) · [Measurements](#interpret-the-measurements)

The [2026-09-30 report](results/2026-09-30.md) and [machine-readable results](results/2026-09-30.json) show the protocol's practical limitations. The candidate has not met the complete acceptance gate.

## Choose the cases

| Resource | Purpose | Coverage |
|---|---|---|
| [benchmark.json](benchmark.json) | Compare no skill, original and candidate. | Eight cases: two design, two review, two evolution, a narrow ADR and a sound-system control. |
| [regression.json](regression.json) | Preserve existing behavior. | Eight single-turn adaptations of [cases.md](cases.md). |
| [cases.md](cases.md) | Explain release expectations. | Required behaviors, critical conditions and unsafe outcomes. |

Rubrics measure behavior, not matching phrases or a required product. The interview regression is retrospective; it does not establish live dialogue quality.

Use one strong and one smaller model from the same provider through existing access. Freeze model IDs, reasoning effort, CLI version and skill snapshots. Do not add credentials or paid access to make a run succeed.

## Establish isolation before a batch

| Boundary | Required treatment |
|---|---|
| Session | Fresh temporary workspace; no prior answer or expected solution. |
| Evidence | Raw fixtures and the request only; rubric outside the subject workspace. |
| Skill | Explicit frozen copy; inspect actual loading traces. |
| Host configuration | Disable discovery, plugins, apps, hooks, memories, AGENTS.md and ambient rules per invocation. Do not edit global configuration. |
| Permissions | Equivalent across all compared conditions; verify real file access first. |
| Side effects | Check workspace digest before/after. Exclude mutations and unauthorized skill reads. |

Configuration switches do **not** prevent direct filesystem access to installed skills. Audit normalized command paths, including escaped Windows paths. Reading outside the frozen skill workspace contaminates a subject even if the installed copy has the same name/version. Exclude it and report the missing case.

Read-only execution is the default. Some Windows environments reject every shell process in that mode. For trusted authored fixtures, explicitly selecting `--sandbox danger-full-access` can match an unrestricted host, but it is not a security boundary. Workspace digests cannot prevent or detect every outside effect. Never use this alternative with untrusted workloads. There is no automatic escalation after rejection.

These evaluations test explicit invocation, not automatic activation quality.

## Record subjects

Run from the repository root. Examples use Bash continuation syntax; in PowerShell, put each continued command on one line. Replace `STRONG` and `SMALL` with verified IDs.

### 1. Freeze and measure the original

```bash
python tools/evaluate_skill.py snapshot --output evals/artifacts/current

python tools/evaluate_skill.py run \
  --suite evals/benchmark.json --models STRONG SMALL \
  --condition none --output evals/artifacts/runs

python tools/evaluate_skill.py run \
  --suite evals/benchmark.json --models STRONG SMALL \
  --condition current --skill evals/artifacts/current \
  --output evals/artifacts/runs
```

Inspect observed failures and loading traces **before changing content**. Add guidance only when it addresses a demonstrated gap.

### 2. Freeze and measure the candidate

```bash
python tools/evaluate_skill.py snapshot --output evals/artifacts/candidate

python tools/evaluate_skill.py run \
  --suite evals/benchmark.json --models STRONG SMALL \
  --condition candidate --skill evals/artifacts/candidate \
  --output evals/artifacts/runs

python tools/evaluate_skill.py run \
  --suite evals/regression.json --models STRONG SMALL \
  --condition candidate --skill evals/artifacts/candidate \
  --output evals/artifacts/runs
```

Do not overwrite a snapshot. A changed skill, case or protocol needs a distinct recorded attempt.

### Runner settings and budget

| Setting | Default or behavior |
|---|---|
| Reasoning | `medium`; freeze it for comparison. |
| Concurrency | Two processes; `--workers` supports 1–4. |
| Timeout | 600 seconds per attempt. |
| Budget | 94 total recorded attempts, including invalid, timeout and grader attempts. |
| Repetition | `--repeat` records a new attempt; existing runs are never silently retried. |
| Routing | `--base-url` preserves an existing router when user configuration is ignored; it does not add credentials. |
| Sandbox | `read-only`; alternatives require explicit protocol selection. |

Change `--limit` only for an explicitly authorized budget. Account for preflights outside the recorder separately. Preselect limited repeats for decisive wins or regressions; do not keep rerunning until a preferred answer appears.

## Grade without condition labels

### 3. Prepare a blinded packet

```bash
python tools/evaluate_skill.py blind \
  --output evals/artifacts/runs \
  --packet evals/artifacts/blind.json --key evals/artifacts/key.json

python tools/evaluate_skill.py prepare-grading \
  --packet evals/artifacts/blind.json \
  --suites evals/benchmark.json evals/regression.json \
  --output evals/artifacts/grading.json --name grading-final
```

Keep the key away from the assessor. The packet includes completed subjects, raw cases, rubrics, answers and available browsing traces; it withholds condition/model labels, skill content and previous scores. Answer wording may still reveal skill use.

### 4. Run the assessor or supply human grades

```bash
python tools/evaluate_skill.py run \
  --suite evals/artifacts/grading.json --models STRONG \
  --condition none --output evals/artifacts/runs
```

`--batch-size` in `prepare-grading` controls assessor workload. Grader calls consume the same attempt budget. Human grades can instead use the identical schema:

| Field | Requirement |
|---|---|
| `id` | The blinded answer ID. |
| `checks` | Every rubric check exactly once, with boolean `pass` and concrete `evidence`. |
| `unsafe_behavior` | Explicit boolean; an unsafe recommendation cannot pass. |
| `unsupported_findings` | A string list, including an empty list when none are found. |
| `unnecessary_components` | A string list, including an empty list when none are found. |

Grade each answer separately. Do not reward verbosity or a technology name. Distinguish labelled proposals from fabricated facts. For provider verification, plausible URLs do not establish page retrieval: inspect the retained trace and report missing evidence.

Combine the completed grader JSON arrays into `evals/artifacts/grades.json`. Do not extract grades from a failed or incomplete assessor run. Model-assisted grading is fallible; review decisive outcomes against the raw artifacts, preserve original scores and record any conservative audit adjustment separately.

### 5. Validate and summarize

```bash
python tools/compare_evals.py \
  --packet evals/artifacts/blind.json --key evals/artifacts/key.json \
  --grades evals/artifacts/grades.json \
  --suites evals/benchmark.json evals/regression.json \
  --runs evals/artifacts/runs --output evals/artifacts/comparison.json
```

If a later trace audit excludes a subject, preserve the original packet/grades and create a filtered comparison with matching packet, key and grades. Incomplete coverage remains unknown. Do not silently reuse an earlier candidate to fill a final-snapshot gap.

## Apply the release gate

A case passes only when **all critical checks**, at least **80% of all checks**, and **no unsafe behavior** are satisfied.

| Acceptance condition | Evidence needed |
|---|---|
| Quality gain | A corrected hard-case failure in each model, preserved in a clean confirmation. |
| No regression | Critical correctness, narrow tasks and the sound-system control remain sound. |
| Context benefit | Less irrelevant loading on narrow tasks; justified depth on hard decisions. |
| Existing behavior | Final-snapshot regression coverage, not a substitute from an older candidate. |
| Integrity | Valid links, discovery and dependency-free distribution. |

Missing grades, contaminated sessions and incomplete runs are **unknown, never passes**. Compare equivalent cases; different coverage counts are not comparable percentages. If baselines reach the ceiling, predeclare harder realistic variants before testing them. Never change the rubric after seeing candidate answers. If improvement is not demonstrated, do not claim it.

## Interpret the measurements

| Metric | Interpretation | Limit |
|---|---|---|
| Input/output/cache tokens | Actual CLI-reported totals across the run. | Includes harness overhead and repeated prefixes; not unique context or monetary cost. |
| Skill-read words/characters | Outputs of successful commands naming skill files. | Approximate proxy: mixed outputs can overcount and indirect reads can be missed. |
| References and rereads | Observed command-path counts. | Shares trace limitations; not guaranteed complete. |
| Case/check outcomes | Behavioral rubric results. | Depends on assessor accuracy and tested cases. |

Inspect raw JSONL before making a context claim. Keep failed attempts, snapshots and hashes under ignored `evals/artifacts/`; publish a dated report with clean cohort counts, exclusions, model settings, separate usage/loading measurements and a release verdict.

## Method references

The recorder follows the structured-trace approach in [OpenAI's skill evaluation guide](https://developers.openai.com/blog/eval-skills). Invocation isolation uses the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). These references explain the method; local traces determine whether the intended isolation actually held.
