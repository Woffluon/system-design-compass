# Contributing

**Help an agent make one better architecture decision.** A contribution should expose a missing trade-off, resolve an observed failure or correct a verifiable technical error.

[Content standards](#content-standards) · [Validation](#validate-the-change) · [Evidence](#show-the-behavioral-evidence)

## Choose the smallest useful change

| Contribution | Include |
|---|---|
| Incorrect guarantee | Raw evidence, the violating event sequence and the corrected enforcement boundary. |
| Missing decision support | A realistic request, the observed omission and the smallest guidance that addresses it. |
| Context overhead | Loading traces, the irrelevant or repeated material and a scoped reduction. |
| Documentation or presentation | The reader's difficulty and a clearer structure that preserves the technical meaning. |

Generic tutorials, speculative rules and product catalogs increase maintenance and context without necessarily improving a decision. Keep the change tied to evidence.

## Content standards

- **Original work:** do not copy prose, diagrams or tables from books, courses or repositories without a compatible license and explicit attribution.
- **Primary evidence:** prefer standards, research papers, official documentation and first-party incident or architecture reports. Link the source used for time-sensitive facts.
- **Selective loading:** keep `SKILL.md` concise. Place conditional detail in a focused reference and link it directly from the entrypoint; do not duplicate shared guidance.
- **Capabilities first:** explain decision criteria and validity boundaries before naming vendor products.
- **Authorization:** preserve user choice. Recommendations do not authorize application changes or external actions.
- **Language and scope:** maintain English guidance and the user's response-language rule. Keep this a system-design skill.

## Validate the change

Run from the repository root:

```bash
python tools/validate_repo.py
python -m unittest discover -s tools -p 'test_*.py'
python -m pip install skills-ref==0.1.1
agentskills validate skills/system-design-compass
npx skills@1.5.26 add . --list
git diff --check
```

| Check | Establishes |
|---|---|
| Repository validator | Required files, reference links, topic coverage and runtime boundaries. |
| Helper tests | Evaluation accounting, isolation detection and grade handling. |
| Specification validator | Agent Skills format compatibility. |
| CLI discovery | The skill is discoverable from this checkout. |
| Diff review | Changes are necessary, scoped and free of accidental edits. |

The validator is a development dependency; skill users do not need it. CI also runs an installation smoke test. A passing format check does not prove better model behavior.

## Show the behavioral evidence

For behavior changes, add or update a case with raw artifacts, critical invariants and observable checks. Keep the rubric away from the subject, freeze the compared snapshots, and follow the [evaluation protocol](evals/README.md).

Report quality and loading cost separately. Preserve failed and contaminated attempts; do not label missing coverage as a pass. Formatting changes should preserve instructions and explicitly retain the scope of historical evaluation claims.

## Prepare the pull request

Lead with the concrete problem and resulting behavior. Include the affected decision, evidence or reproduction, checks run and any remaining uncertainty. For visual changes, include a rendered preview and accessible text.

Review every changed instruction before submission. If it cannot be traced to the problem, remove it. Report security-sensitive behavior through the [private reporting path](SECURITY.md).
