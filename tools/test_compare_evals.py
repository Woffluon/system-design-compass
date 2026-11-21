"""Tests for behavioral release gating and missing-data handling."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if __package__:
    from . import compare_evals
    from .compare_evals import summarize, validate_grade
else:
    import compare_evals
    from compare_evals import summarize, validate_grade


class GradeTests(unittest.TestCase):
    def setUp(self):
        self.entry = {"id": "answer-001"}
        self.case = {"checks": [{"id": "boundary", "critical": True}, {"id": "validation", "critical": False}]}
        self.grade = {"checks": [{"id": "boundary", "pass": True, "evidence": "Atomic write boundary described"}, {"id": "validation", "pass": True, "evidence": "Crash test specified"}], "unsafe_behavior": False, "unsupported_findings": [], "unnecessary_components": []}

    def test_all_checks_and_no_unsafe_behavior_pass(self):
        self.assertTrue(validate_grade(self.entry, self.grade, self.case)["case_pass"])

    def test_critical_failure_cannot_be_hidden_by_score(self):
        self.grade["checks"][0]["pass"] = False
        result = validate_grade(self.entry, self.grade, self.case)
        self.assertFalse(result["case_pass"])
        self.assertEqual(result["critical_failures"], ["boundary"])

    def test_unsafe_behavior_blocks_an_otherwise_passing_answer(self):
        self.grade["unsafe_behavior"] = True
        self.assertFalse(validate_grade(self.entry, self.grade, self.case)["case_pass"])

    def test_missing_duplicate_or_unsubstantiated_grades_are_rejected(self):
        for checks in ([self.grade["checks"][0]], [self.grade["checks"][0]] * 2, [{"id": "boundary", "pass": True, "evidence": ""}, self.grade["checks"][1]]):
            with self.assertRaises(ValueError):
                validate_grade(self.entry, {**self.grade, "checks": checks}, self.case)

    def test_missing_findings_cannot_silently_be_reported_as_zero(self):
        for field in ("unsupported_findings", "unnecessary_components"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_grade(self.entry, {key: value for key, value in self.grade.items() if key != field}, self.case)

    def test_missing_usage_remains_unknown_in_group_totals(self):
        record = {"suite": "benchmark", "model": "model", "condition": "candidate", "repeat": 1, "usage": None, "grade": {"case_pass": True, "critical_failures": [], "unsafe_behavior": False, "passed_checks": 2, "total_checks": 2, "unsupported_findings": [], "unnecessary_components": []}, "observed_skill_read_output_words": 400, "observed_reference_count": 1, "repeated_skill_reads": 0}
        summary = summarize([record])[0]
        self.assertIsNone(summary["input_tokens"])
        self.assertEqual(summary["usage_records"], 0)

    def test_pass_check_ratio_constant_and_threshold(self):
        self.assertEqual(compare_evals.PASS_CHECK_RATIO, 0.8)
        case = {"checks": [{"id": f"c{i}", "critical": False} for i in range(5)]}
        four_pass = {
            "checks": [{"id": f"c{i}", "pass": i < 4, "evidence": "ok"} for i in range(5)],
            "unsafe_behavior": False, "unsupported_findings": [], "unnecessary_components": [],
        }
        three_pass = {
            "checks": [{"id": f"c{i}", "pass": i < 3, "evidence": "ok"} for i in range(5)],
            "unsafe_behavior": False, "unsupported_findings": [], "unnecessary_components": [],
        }
        self.assertTrue(validate_grade(self.entry, four_pass, case)["case_pass"])
        self.assertFalse(validate_grade(self.entry, three_pass, case)["case_pass"])

    def test_main_calls_summarize_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runs = root / "runs"
            runs.mkdir()
            (runs / "run-1.json").write_text(json.dumps({
                "status": "completed", "run_id": "run-1", "suite": "benchmark", "case": "c1",
                "model": "m1", "condition": "candidate", "repeat": 1, "answer": "Ans",
                "observed_skill_read_output_words": 10, "observed_reference_count": 0, "repeated_skill_reads": 0,
            }), encoding="utf-8")
            (root / "packet.json").write_text(json.dumps([
                {"id": "answer-001", "suite": "benchmark", "case": "c1", "answer": "Ans"},
            ]), encoding="utf-8")
            (root / "key.json").write_text(json.dumps({"answer-001": "run-1"}), encoding="utf-8")
            (root / "grades.json").write_text(json.dumps([{
                "id": "answer-001",
                "checks": [{"id": "boundary", "pass": True, "evidence": "done"}],
                "unsafe_behavior": False, "unsupported_findings": [], "unnecessary_components": [],
            }]), encoding="utf-8")
            (root / "suite.json").write_text(json.dumps({
                "name": "benchmark",
                "cases": [{"id": "c1", "checks": [{"id": "boundary", "critical": True}]}],
            }), encoding="utf-8")
            out = root / "out.json"
            argv = [
                "compare_evals.py", "--packet", str(root / "packet.json"),
                "--key", str(root / "key.json"), "--grades", str(root / "grades.json"),
                "--suites", str(root / "suite.json"), "--runs", str(runs), "--output", str(out),
            ]
            with patch.object(sys, "argv", argv), \
                 patch.object(compare_evals, "summarize", wraps=compare_evals.summarize) as spy:
                compare_evals.main()
            spy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
