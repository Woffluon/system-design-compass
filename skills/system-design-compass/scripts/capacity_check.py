#!/usr/bin/env python3
"""Deterministic capacity and backlog drain check using Python 3 stdlib only."""

from __future__ import annotations

import argparse
import json
import math
import sys

UNIT_TO_SECONDS = {"s": 1.0, "min": 60.0, "h": 3600.0}


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for capacity and drain checks."""
    parser = argparse.ArgumentParser(description="Verify queue drain inequality and capacity.")
    parser.add_argument("--arrival-rate", type=float, required=True)
    parser.add_argument("--unit", choices=tuple(UNIT_TO_SECONDS), default="s")
    parser.add_argument("--duplicate-fraction", type=float, default=0.0)
    parser.add_argument("--retry-factor", type=float, default=0.0)
    parser.add_argument("--workers", type=float, required=True)
    parser.add_argument("--failure-allowance", type=float, default=0.0)
    parser.add_argument("--worker-rate", type=float, required=True)
    parser.add_argument("--backlog", type=float, default=0.0)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate numeric bounds and finiteness for all capacity inputs."""
    for name, value in (
        ("arrival-rate", args.arrival_rate),
        ("duplicate-fraction", args.duplicate_fraction),
        ("retry-factor", args.retry_factor),
        ("backlog", args.backlog),
    ):
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and >= 0 (got {value})")

    if not math.isfinite(args.workers) or args.workers <= 0.0:
        raise ValueError(f"workers must be finite and > 0 (got {args.workers})")
    if not math.isfinite(args.worker_rate) or args.worker_rate <= 0.0:
        raise ValueError(f"worker-rate must be finite and > 0 (got {args.worker_rate})")
    if not math.isfinite(args.failure_allowance) or not (0.0 <= args.failure_allowance < 1.0):
        raise ValueError(f"failure-allowance must be in [0, 1) (got {args.failure_allowance})")


def compute_capacity(args: argparse.Namespace) -> dict[str, object]:
    """Compute normalized attempt demand, degraded capacity, and drain time."""
    validate_inputs(args)

    scale = UNIT_TO_SECONDS[args.unit]
    unique_arrival_per_s = args.arrival_rate / scale
    worker_rate_per_s = args.worker_rate / scale

    accepted_per_s = unique_arrival_per_s * (1.0 + args.duplicate_fraction)
    peak_attempt_demand_per_s = accepted_per_s * (1.0 + args.retry_factor)
    available_workers = args.workers * (1.0 - args.failure_allowance)
    degraded_capacity_per_s = available_workers * worker_rate_per_s
    net_drain_per_s = degraded_capacity_per_s - peak_attempt_demand_per_s

    drains = net_drain_per_s > 0.0
    if drains:
        clear_seconds: float | None = (args.backlog / net_drain_per_s) if args.backlog > 0.0 else 0.0
    else:
        clear_seconds = None

    return {
        "drains": drains,
        "unique_arrival_per_s": round(unique_arrival_per_s, 4),
        "accepted_per_s": round(accepted_per_s, 4),
        "peak_attempt_demand_per_s": round(peak_attempt_demand_per_s, 4),
        "available_workers": round(available_workers, 4),
        "degraded_attempt_capacity_per_s": round(degraded_capacity_per_s, 4),
        "net_attempt_drain_per_s": round(net_drain_per_s, 4),
        "time_to_clear_backlog_s": round(clear_seconds, 2) if clear_seconds is not None else None,
    }


def format_markdown(result: dict[str, object]) -> str:
    """Render capacity check output as a compact Markdown table."""
    clear_time = result["time_to_clear_backlog_s"]
    clear_text = (
        f"{clear_time}s"
        if clear_time is not None
        else "UNBOUNDED (degraded_capacity <= peak_demand)"
    )
    return (
        "| Metric | Value |\n"
        "|---|---|\n"
        f"| Peak attempt demand | {result['peak_attempt_demand_per_s']}/s |\n"
        f"| Degraded capacity | {result['degraded_attempt_capacity_per_s']}/s |\n"
        f"| Net drain rate | {result['net_attempt_drain_per_s']}/s |\n"
        f"| Backlog clear time | {clear_text} |"
    )


def main(argv: list[str] | None = None) -> int:
    """Run CLI argument parsing, calculation, and output formatting."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = compute_capacity(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown(result))
    return 0 if result["drains"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
