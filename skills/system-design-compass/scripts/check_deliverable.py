#!/usr/bin/env python3
"""Check architectural deliverables against structural contract rules."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REQUIRED_CHECKS = {
    "adr": {
        "state_owner": r"(?i)\b(authoritative\s+(?:state\s+)?owner|state\s+owner|durum\s+sahibi)\b",
        "violating_sequence": r"(?i)\b(violating\s+(?:event\s+)?sequence|bozucu\s+(?:olay\s+)?dizisi|race|crash)\b",
        "fault_schedule": r"(?i)\b(fault\s+schedule|hata\s+çizelgesi|hata\s+takvimi|timeout|burst)\b",
        "oracle": r"(?i)\b(pass/fail\s+oracle|oracle|geçer/kalır|gecer/kalir)\b",
        "proposed_tag": r"\bProposed\b",
    },
    "review": {
        "state_owner": r"(?i)\b(authoritative\s+(?:state\s+)?owner|state\s+owner|durum\s+sahibi)\b",
        "violating_sequence": r"(?i)\b(violating\s+(?:event\s+)?sequence|bozucu\s+(?:olay\s+)?dizisi|trigger)\b",
        "oracle": r"(?i)\b(pass/fail\s+oracle|oracle|validation|doğrulama)\b",
        "sound_decisions": r"(?i)\b(sound\s+(?:existing\s+)?decisions|preserve|korunacak\s+karar)\b",
    },
    "migration": {
        "state_owner": r"(?i)\b(authoritative\s+(?:state\s+)?owner|state\s+owner|durum\s+sahibi)\b",
        "drill": r"(?i)\b(mixed-version|restart|repair|geri\s+alma|rollback)\b",
        "oracle": r"(?i)\b(pass/fail\s+oracle|oracle|zero\s+legacy\s+traffic|sıfır\s+eski\s+trafik)\b",
        "proposed_tag": r"\bProposed\b",
    },
    "postmortem": {
        "timeline": r"(?i)\b(UTC|timeline|zaman\s+çizelgesi|TTD|TTM|MTTD)\b",
        "action_class": r"\b(Investigate|Mitigate-Now|Repair|Detect-Future|Mitigate-Future|Prevent-Future)\b",
        "fault_schedule": r"(?i)\b(fault\s+schedule|hata\s+çizelgesi|sub-timeout|blast[- ]radius)\b",
        "oracle": r"(?i)\b(pass/fail\s+oracle|oracle|geçer/kalır)\b",
    },
}

DATE_BASED_ROLLBACK_RE = re.compile(
    r"(?i)(?:rollback|cutover|contract|daralt|geri\s+al)[^\n.]{0,60}\b(?:after\s+\d+\s+days?|\d+\s+gün\s+sonra)\b"
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for deliverable contract checks."""
    parser = argparse.ArgumentParser(description="Validate deliverable Markdown against contract rules.")
    parser.add_argument("--kind", choices=tuple(REQUIRED_CHECKS), required=True)
    parser.add_argument("--input", default="-")
    parser.add_argument("--strict-adr-words", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def read_input(source: str) -> str:
    """Read Markdown deliverable text from stdin ('-') or a local UTF-8 file."""
    if source == "-":
        return sys.stdin.read()
    path = pathlib.Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"input file not found: {source}")
    return path.read_text(encoding="utf-8")


def inspect_deliverable(kind: str, text: str, strict_adr_words: bool) -> dict[str, object]:
    """Validate required sections, migration rollback gating, and ADR word bounds."""
    failures: list[str] = []
    warnings: list[str] = []

    for label, pattern in REQUIRED_CHECKS[kind].items():
        if not re.search(pattern, text):
            failures.append(f"missing required contract element: {label}")

    if kind == "migration" and DATE_BASED_ROLLBACK_RE.search(text):
        failures.append("invalid date/day-based cutover or rollback gate detected; gate on zero legacy traffic/metrics")

    word_count = len(re.findall(r"\S+", text))
    if kind == "adr" and (word_count < 120 or word_count > 450):
        msg = f"ADR word count {word_count} is outside target band (200-400 words)"
        if strict_adr_words:
            failures.append(msg)
        else:
            warnings.append(msg)

    return {
        "kind": kind,
        "word_count": word_count,
        "passed": len(failures) == 0,
        "failures": failures,
        "warnings": warnings,
    }


def format_text(report: dict[str, object]) -> str:
    """Render the contract check report as human-readable text."""
    status = "PASS" if report["passed"] else "FAIL"
    lines = [f"[{status}] kind={report['kind']} words={report['word_count']}"]
    for item in report["failures"]:
        lines.append(f"  FAIL: {item}")
    for item in report["warnings"]:
        lines.append(f"  WARN: {item}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run CLI argument parsing, deliverable inspection, and reporting."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        content = read_input(args.input)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not content.strip():
        print("ERROR: input deliverable is empty", file=sys.stderr)
        return 2

    report = inspect_deliverable(args.kind, content, args.strict_adr_words)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
