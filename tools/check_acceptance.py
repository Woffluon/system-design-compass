"""Check comparison coverage, repeated gains and context gates from validated grades."""

from __future__ import annotations

import argparse
from pathlib import Path

from evaluate_skill import read_json


def check(baseline: list[dict], candidate: list[dict], models: list[str], suites: list[dict]) -> list[str]:
    errors = []
    expected = {}
    for suite in suites:
        expected.setdefault(suite["name"], set()).update(case["id"] for case in suite["cases"])
    hard = expected["benchmark"] - {"narrow-adr", "sound-system"}
    for model in models:
        original = {r["case"]: r for r in baseline if r["model"] == model and r["condition"] == "current"}
        for condition in ("none", "current"):
            cases = [r["case"] for r in baseline if r["model"] == model and r["condition"] == condition]
            if len(cases) != len(expected["benchmark"]) or set(cases) != expected["benchmark"]:
                errors.append(f"{model}: incomplete or duplicate {condition} baseline")
        values = [r for r in candidate if r["model"] == model and r["condition"] == "candidate"]
        for suite, cases in expected.items():
            observed = {r["case"] for r in values if r["suite"] == suite}
            if observed != cases:
                errors.append(f"{model}: incomplete {suite} candidate")
        for r in values:
            if not r["grade"]["case_pass"]:
                errors.append(f"{model}: failed {r['suite']}/{r['case']}/{r['repeat']}")
        wins = []
        for case in hard:
            confirmations = [r for r in values if r["suite"] == "benchmark" and r["case"] == case]
            if (case in original and not original[case]["grade"]["case_pass"]
                    and len({r["repeat"] for r in confirmations}) >= 3
                    and all(r["grade"]["case_pass"] for r in confirmations)):
                wins.append(case)
        if not wins:
            errors.append(f"{model}: no hard-case correction with two clean confirmations")
        narrow = [r for r in values if r["suite"] == "benchmark" and r["case"] == "narrow-adr"]
        if (len(narrow) != 1 or "narrow-adr" not in original
                or narrow[0]["observed_skill_read_output_words"] >= original["narrow-adr"]["observed_skill_read_output_words"]):
            errors.append(f"{model}: narrow-task context reduction not established")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--suites", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    errors = check(read_json(args.baseline)["records"], read_json(args.candidate)["records"], args.models,
                   [read_json(path) for path in args.suites])
    if errors:
        raise SystemExit("\n".join(errors))
    print("Behavior, complete comparison coverage, repeated gains and narrow-context gates passed.")
    print("Source identity, trace integrity, justified depth and distribution checks require their separate evidence.")


if __name__ == "__main__":
    main()
