"""Validate blinded behavioral grades and summarize measured runs; no word matching."""

from __future__ import annotations

import argparse
import math
import statistics
from collections import defaultdict
from pathlib import Path

from evaluate_skill import read_json, safe_path, write_json


def validate_grade(entry: dict, grade: dict, case: dict) -> dict:
    expected = {check["id"]: check for check in case["checks"]}
    checks = grade.get("checks", [])
    if len(checks) != len(expected) or {check.get("id") for check in checks} != set(expected):
        raise ValueError(f"incomplete or duplicate checks for {entry['id']}")
    for check in checks:
        if type(check.get("pass")) is not bool or not check.get("evidence", "").strip():
            raise ValueError(f"boolean outcome and evidence required for {entry['id']}/{check.get('id')}")
    if type(grade.get("unsafe_behavior")) is not bool:
        raise ValueError(f"explicit unsafe_behavior required for {entry['id']}")
    for field in ("unsupported_findings", "unnecessary_components"):
        if not isinstance(grade.get(field), list) or any(not isinstance(item, str) for item in grade[field]):
            raise ValueError(f"explicit string list {field} required for {entry['id']}")
    critical_failures = [check["id"] for check in checks if expected[check["id"]]["critical"] and not check["pass"]]
    passed = sum(check["pass"] for check in checks)
    return {
        **grade,
        "critical_failures": critical_failures,
        "passed_checks": passed,
        "total_checks": len(checks),
        "case_pass": not critical_failures and not grade["unsafe_behavior"] and passed >= math.ceil(0.8 * len(checks)),
    }


def combine(packet: list[dict], key: dict, grades: list[dict], suites: list[dict], runs: Path) -> list[dict]:
    cases = {(suite["name"], case["id"]): case for suite in suites for case in suite["cases"]}
    grade_map = {grade["id"]: grade for grade in grades}
    if len(grade_map) != len(grades) or set(grade_map) != {entry["id"] for entry in packet}:
        raise ValueError("grades must cover the blind packet exactly once")
    if set(key) != set(grade_map):
        raise ValueError("blind key does not match packet")
    result = []
    for entry in packet:
        run = read_json(safe_path(runs, f"{key[entry['id']]}.json"))
        if run.get("status") != "completed" or run["answer"] != entry["answer"]:
            raise ValueError("grade does not match a completed immutable answer")
        if (run["suite"], run["case"]) != (entry["suite"], entry["case"]):
            raise ValueError("blind mapping changed the case")
        case = cases[(entry["suite"], entry["case"])]
        result.append({**run, "grade": validate_grade(entry, grade_map[entry["id"]], case)})
    return result


def summarize(records: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for record in records:
        groups[(record["suite"], record["model"], record["condition"], record["repeat"])].append(record)
    result = []
    for (suite, model, condition, repeat), values in sorted(groups.items()):
        usage = [v["usage"] for v in values if v.get("usage") is not None]
        result.append({
            "suite": suite, "model": model, "condition": condition, "repeat": repeat,
            "cases": len(values), "passed": sum(v["grade"]["case_pass"] for v in values),
            "critical_failures": sum(len(v["grade"]["critical_failures"]) for v in values),
            "unsafe_answers": sum(v["grade"]["unsafe_behavior"] for v in values),
            "unsupported_findings": sum(len(v["grade"]["unsupported_findings"]) for v in values),
            "unnecessary_components": sum(len(v["grade"]["unnecessary_components"]) for v in values),
            "passed_checks": sum(v["grade"]["passed_checks"] for v in values),
            "total_checks": sum(v["grade"]["total_checks"] for v in values),
            "median_observed_skill_read_output_words": statistics.median(v["observed_skill_read_output_words"] for v in values),
            "median_observed_references": statistics.median(v["observed_reference_count"] for v in values),
            "repeated_skill_reads": sum(v["repeated_skill_reads"] for v in values),
            "usage_records": len(usage),
            "input_tokens": sum(u["input_tokens"] for u in usage) if len(usage) == len(values) else None,
            "output_tokens": sum(u["output_tokens"] for u in usage) if len(usage) == len(values) else None,
            "cached_input_tokens": sum(u.get("cached_input_tokens", 0) for u in usage) if len(usage) == len(values) else None,
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--grades", type=Path, required=True)
    parser.add_argument("--suites", type=Path, nargs="+", required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = combine(read_json(args.packet), read_json(args.key), read_json(args.grades), [read_json(p) for p in args.suites], args.runs)
    write_json(args.output, {"records": records, "summary": summarize(records)})
    for row in summarize(records):
        print(f"{row['suite']} {row['model']} {row['condition']} repeat {row['repeat']}: {row['passed']}/{row['cases']}, critical failures {row['critical_failures']}, skill-output words median {row['median_observed_skill_read_output_words']}")


if __name__ == "__main__":
    main()
