"""Checks for evaluation isolation, accounting and context measurement."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import evaluate_skill as evaluation


class EvaluationTests(unittest.TestCase):
    def test_host_disablements_are_local_configuration_not_file_mutations(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / ".agents/skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("Unchanged", encoding="utf-8")
            with patch.object(evaluation.Path, "home", return_value=root):
                self.assertEqual(evaluation.disabled_host_skills(),
                                 [{"path": skill.as_posix(), "enabled": False}])
            self.assertEqual(skill.read_text(), "Unchanged")

    def test_blind_packet_retains_successful_http_evidence_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runs = root / "runs"
            evaluation.write_json(runs / "one.json", {"status": "completed", "run_id": "private", "suite": "test", "case": "one", "answer": "Decision"})
            items = [{"type": "command_execution", "command": "curl https://official.example/page", "exit_code": code, "aggregated_output": text}
                     for code, text in [(0, "Documented retention"), (1, "Failed"), (0, "")]]
            (runs / "private.jsonl").write_text("\n".join(json.dumps({"type": "item.completed", "item": item}) for item in items))
            evaluation.blind(runs, root / "packet.json", root / "key.json")
            trace = evaluation.read_json(root / "packet.json")[0]["verification_trace"]
            self.assertEqual(len(trace), 1)
            self.assertEqual(trace[0]["aggregated_output"], "Documented retention")

    def test_truncated_http_command_retains_page_body_for_grader(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runs = root / "runs"
            evaluation.write_json(runs / "one.json", {"status": "completed", "run_id": "private", "suite": "test", "case": "one", "answer": "Decision"})
            item = {"type": "command_execution", "command": "python -c import urllib.request; ...",
                    "exit_code": 0, "aggregated_output": "https://official.example/quotas\nMessage retention: 14 days"}
            (runs / "private.jsonl").write_text(json.dumps({"type": "item.completed", "item": item}))
            evaluation.blind(runs, root / "packet.json", root / "key.json")
            self.assertEqual(evaluation.read_json(root / "packet.json")[0]["verification_trace"], [item])

    def test_fixture_paths_cannot_escape_or_configure_the_harness(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ("../outside.txt", ".codex/config.toml", ".agents/skills/x/SKILL.md", "AGENTS.md", "skill/override.txt"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    evaluation.safe_path(Path(folder), name)

    def test_prompt_does_not_expose_rubric(self):
        case = {"setup": "Raw evidence", "prompt": "Decide", "checks": [{"requirement": "SECRET RUBRIC"}]}
        self.assertNotIn("SECRET RUBRIC", evaluation.make_prompt(case, "current"))
        self.assertNotIn("skill/SKILL.md", evaluation.make_prompt(case, "none"))

    def test_context_proxy_counts_repeated_reads_and_preserves_actual_usage(self):
        events = [
            {"type": "item.started", "item": {"type": "command_execution", "command": "cat skill/SKILL.md"}},
            {"type": "item.completed", "item": {"type": "command_execution", "command": "cat skill/SKILL.md", "exit_code": 0, "aggregated_output": "three input words"}},
            {"type": "item.completed", "item": {"type": "command_execution", "command": "cat skill/SKILL.md skill/references/evolve.md", "exit_code": 0, "aggregated_output": "two words"}},
            {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 9}},
        ]
        result = evaluation.metrics(events)
        self.assertEqual(result["repeated_skill_reads"], 1)
        self.assertEqual(result["observed_reference_count"], 1)
        self.assertEqual(result["observed_skill_read_output_words"], 5)
        self.assertEqual(result["usage"]["input_tokens"], 100)

    def test_failed_reads_do_not_count_as_loaded_and_missing_usage_is_not_zero(self):
        result = evaluation.metrics([{"type": "item.completed", "item": {"type": "command_execution", "command": "cat skill/SKILL.md", "exit_code": 1, "aggregated_output": "not found"}}])
        self.assertEqual(result["observed_skill_reads"], [])
        self.assertIsNone(result["usage"])
        self.assertFalse(result["completed"])

    def test_empty_conditional_read_does_not_count_as_skill_loading(self):
        result = evaluation.metrics([{"type": "item.completed", "item": {
            "type": "command_execution", "command": "if (Test-Path skill/SKILL.md) { Get-Content skill/SKILL.md }",
            "exit_code": 0, "aggregated_output": ""}}])
        self.assertEqual(result["observed_skill_reads"], [])

    def test_discovery_glob_does_not_count_as_content_loading(self):
        result = evaluation.metrics([{"type": "item.completed", "item": {
            "type": "command_execution", "command": "Get-ChildItem; rg --files -g 'skill/SKILL.md' -g '*.py'",
            "exit_code": 0, "aggregated_output": "service.py\n"}}])
        self.assertEqual(result["observed_skill_reads"], [])
        self.assertEqual(result["observed_skill_read_output_words"], 0)

    def test_discovery_followed_by_content_read_still_counts(self):
        result = evaluation.metrics([{"type": "item.completed", "item": {
            "type": "command_execution", "command": "Get-ChildItem; Get-Content skill/SKILL.md",
            "exit_code": 0, "aggregated_output": "Actual guidance"}}])
        self.assertEqual(result["observed_skill_reads"], ["SKILL.md"])

    def test_escaped_windows_paths_are_counted_and_other_skills_detected(self):
        result = evaluation.metrics([{"type": "item.completed", "item": {"type": "command_execution", "command": r"Get-Content skill\\references\\evolve.md C:\\Users\\someone\\.agents\\skills\\other\\SKILL.md", "exit_code": 0, "aggregated_output": "Guidance"}}])
        self.assertIn("references/evolve.md", result["observed_skill_reads"])
        self.assertEqual(len(result["other_skill_commands"]), 1)

    def test_an_existing_record_with_a_changed_protocol_cannot_be_silently_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            suite = root / "suite.json"
            evaluation.write_json(suite, {"name": "test", "cases": [{"id": "one", "setup": "", "prompt": ""}]})
            output = root / "runs"
            evaluation.write_json(output / "test.one.model.none.1.json", {"skill_digest": None, "reasoning_effort": "medium", "sandbox": "read-only", "case_digest": "changed"})
            args = argparse.Namespace(suite=suite, cases=None, condition="none", skill=None, output=output, models=["model"], repeat=1, effort="medium", sandbox="read-only", limit=94)
            with self.assertRaisesRegex(ValueError, "different inputs"):
                evaluation.run_suite(args)
            self.assertFalse((output / "run.lock").exists())

    def test_budget_rejection_does_not_launch_a_model_and_releases_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            evaluation.write_json(root / "suite.json", {"name": "test", "cases": [{"id": "one", "setup": "", "prompt": ""}]})
            output = root / "runs"
            output.mkdir()
            evaluation.write_json(output / "existing.json", {"status": "failed"})
            args = argparse.Namespace(suite=root / "suite.json", cases=None, condition="none", skill=None, output=output, models=["model"], repeat=1, effort="medium", sandbox="read-only", limit=1)
            with patch.object(evaluation, "MAX_RUNS", 1), patch.object(evaluation, "cli_command") as cli:
                with self.assertRaisesRegex(ValueError, "run cap"):
                    evaluation.run_suite(args)
                cli.assert_not_called()
            self.assertFalse((output / "run.lock").exists())

    def test_blind_packet_omits_model_condition_and_usage(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runs = root / "runs"
            evaluation.write_json(runs / "one.json", {"status": "completed", "run_id": "private", "suite": "test", "case": "one", "answer": "Decision", "model": "hidden-model", "condition": "candidate", "usage": {"input_tokens": 999}})
            evaluation.blind(runs, root / "packet.json", root / "key.json")
            packet = json.loads((root / "packet.json").read_text())
            self.assertEqual(set(packet[0]), {"id", "suite", "case", "answer"})
            self.assertEqual(evaluation.read_json(root / "key.json"), {"answer-001": "private"})

    def test_snapshot_is_immutable_and_digest_tracks_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            (source / "SKILL.md").write_text("Before", encoding="utf-8")
            evaluation.snapshot(source, root / "snapshot")
            before = evaluation.digest(root / "snapshot")
            (source / "SKILL.md").write_text("After", encoding="utf-8")
            self.assertEqual(before, evaluation.digest(root / "snapshot"))
            self.assertNotEqual(before, evaluation.digest(source))
            with self.assertRaises(ValueError):
                evaluation.snapshot(source, root / "snapshot")


if __name__ == "__main__":
    unittest.main()
