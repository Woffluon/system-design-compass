"""Checks for evaluation isolation, accounting and context measurement."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if __package__:
    from . import evaluate_skill as evaluation
else:
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

    def test_browsing_retain_source_content_emits_single_developer_instructions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            suite = root / "suite.json"
            evaluation.write_json(suite, {
                "name": "test",
                "cases": [{"id": "browse", "setup": "s", "prompt": "p", "browsing": True}],
            })
            output = root / "runs"
            args = argparse.Namespace(
                suite=suite, cases=None, condition="none", skill=None, output=output,
                models=["m1"], repeat=1, effort="medium", sandbox="read-only",
                limit=94, workers=1, timeout=30, base_url=None,
                inline_fixtures=False, retain_source_content=True,
            )
            captured = []

            def fake_run(cmd, **kwargs):
                captured.append(cmd)
                return subprocess.CompletedProcess(
                    cmd, 0,
                    stdout=json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}})
                    + "\n" + json.dumps({"type": "turn.completed", "usage": None}) + "\n",
                    stderr="",
                )

            with patch.object(evaluation, "cli_command", return_value=["codex"]), \
                 patch.object(evaluation, "disabled_host_skills", return_value=[]), \
                 patch.object(evaluation.subprocess, "run", side_effect=fake_run):
                evaluation.run_suite(args)

            dev_args = [arg for arg in captured[0] if isinstance(arg, str) and arg.startswith("developer_instructions=")]
            self.assertEqual(len(dev_args), 1)
            self.assertIn("skill/SKILL.md", dev_args[0])
            self.assertIn("Retrieval instrumentation:", dev_args[0])

    def test_listing_commands_without_content_reads_do_not_count(self):
        for cmd in (
            "ls skill/SKILL.md",
            "dir skill\\SKILL.md",
            "find skill -name SKILL.md",
            "Test-Path skill/SKILL.md",
            "stat skill/SKILL.md",
            "wc -l skill/SKILL.md",
        ):
            with self.subTest(cmd=cmd):
                result = evaluation.metrics([{
                    "type": "item.completed",
                    "item": {"type": "command_execution", "command": cmd, "exit_code": 0, "aggregated_output": "skill/SKILL.md\n"},
                }])
                self.assertEqual(result["observed_skill_reads"], [])
                self.assertEqual(result["observed_skill_read_output_words"], 0)

    def test_gemini_contamination_detected_by_shared_pattern(self):
        result = evaluation.metrics([{
            "type": "item.completed",
            "item": {"type": "command_execution", "command": "cat ~/.gemini/skills/other/SKILL.md", "exit_code": 0, "aggregated_output": "x"},
        }])
        self.assertEqual(len(result["other_skill_commands"]), 1)

    def test_disabled_host_skills_includes_codex_home_and_cli_override(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            home = root / "home"
            home.mkdir()
            codex_home = root / "custom-codex"
            skill = codex_home / "skills" / "extra" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("Custom", encoding="utf-8")
            with patch.object(evaluation.Path, "home", return_value=home), \
                 patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=False):
                disabled = evaluation.disabled_host_skills()
            self.assertEqual(disabled, [{"path": skill.resolve().as_posix(), "enabled": False}])

            fake_bin = root / "codex-bin"
            fake_bin.write_text("", encoding="utf-8")
            with patch.dict(os.environ, {"CODEX_CLI_BIN": str(fake_bin)}, clear=False):
                self.assertEqual(evaluation.cli_command(), [str(fake_bin)])

            cmd_shim = root / "codex.cmd"
            cmd_shim.write_text("", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CODEX_CLI_BIN", None)
                with patch.object(evaluation.shutil, "which", side_effect=[str(cmd_shim), "node"]):
                    with self.assertRaisesRegex(ValueError, "CODEX_CLI_BIN"):
                        evaluation.cli_command()

    def test_run_lock_writes_pid_and_rejects_existing_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            suite = root / "suite.json"
            evaluation.write_json(suite, {"name": "test", "cases": [{"id": "one", "setup": "", "prompt": ""}]})
            output = root / "runs"
            output.mkdir()
            lock = output / "run.lock"
            lock.write_text("pid=99999\n", encoding="utf-8")
            args = argparse.Namespace(
                suite=suite, cases=None, condition="none", skill=None, output=output,
                models=["m"], repeat=1, effort="medium", sandbox="read-only", limit=94,
            )
            with self.assertRaisesRegex(ValueError, "run\\.lock"):
                evaluation.run_suite(args)
            self.assertTrue(lock.exists())

            lock.unlink()
            seen_lock_text = []

            def fake_run(cmd, **kwargs):
                seen_lock_text.append(lock.read_text(encoding="utf-8"))
                return subprocess.CompletedProcess(
                    cmd, 0,
                    stdout=json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}})
                    + "\n" + json.dumps({"type": "turn.completed", "usage": None}) + "\n",
                    stderr="",
                )

            args.workers = 1
            args.timeout = 30
            args.base_url = None
            args.inline_fixtures = False
            args.retain_source_content = False
            with patch.object(evaluation, "cli_command", return_value=["codex"]), \
                 patch.object(evaluation, "disabled_host_skills", return_value=[]), \
                 patch.object(evaluation.subprocess, "run", side_effect=fake_run):
                evaluation.run_suite(args)
            self.assertIn(f"pid={os.getpid()}", seen_lock_text[0])

    def test_blind_respects_custom_seed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runs = root / "runs"
            for i in range(1, 5):
                evaluation.write_json(runs / f"r{i}.json", {
                    "status": "completed", "run_id": f"r{i}", "suite": "test", "case": f"c{i}", "answer": f"A{i}",
                })
            evaluation.blind(runs, root / "p1.json", root / "k1.json", seed=111)
            evaluation.blind(runs, root / "p2.json", root / "k2.json", seed=222)
            self.assertNotEqual(evaluation.read_json(root / "k1.json"), evaluation.read_json(root / "k2.json"))


if __name__ == "__main__":
    unittest.main()
