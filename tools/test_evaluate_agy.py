import argparse
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if __package__:
    from . import evaluate_agy
    from . import evaluate_skill as e
    from .evaluate_agy import normalized_events, provider_error
    from .evaluate_skill import metrics
else:
    import evaluate_agy
    import evaluate_skill as e
    from evaluate_agy import normalized_events, provider_error
    from evaluate_skill import metrics


class AntigravityTraceTests(unittest.TestCase):
    def test_quota_error_is_provider_failure_without_inferred_usage(self):
        error = provider_error('notice\nAGY_ERROR: {"status":"RESOURCE_EXHAUSTED","error_code":429}\n')
        self.assertEqual(error["error_code"], 429)
        self.assertNotIn("usage", error)
        self.assertIsNone(provider_error("ordinary stderr notice"))

    def test_only_successful_terminal_result_completes(self):
        events = normalized_events([{"event": "result", "result": {
            "status": "ERROR", "response": "partial", "usage": {"input_tokens": 12}}}])
        self.assertFalse(metrics(events)["completed"])
        self.assertEqual(metrics(events)["usage"]["input_tokens"], 12)

    def test_retains_real_command_output_and_usage(self):
        events = normalized_events([
            {"event": "step_update", "step_update": {
                "state": "DONE", "step_type": "tool", "tool_info": {
                    "parameters": {"CommandLine": "Get-Content skill/SKILL.md"},
                    "output": "three retained words"}}},
            {"event": "result", "result": {"status": "SUCCESS", "response": "answer",
                "usage": {"input_tokens": 50, "cache_read_tokens": 20}}}])
        result = metrics(events)
        self.assertEqual(result["observed_skill_reads"], ["SKILL.md"])
        self.assertEqual(result["observed_skill_read_output_words"], 3)
        self.assertEqual(result["usage"]["cached_input_tokens"], 20)

    def test_provider_error_handles_malformed_json(self):
        self.assertEqual(provider_error("AGY_ERROR: {broken"), {"raw": "{broken"})

    def test_cli_command_handles_windows_wrappers_and_missing_cli(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AGY_CLI_BIN", None)
            with patch.object(evaluate_agy.shutil, "which", return_value=None):
                with self.assertRaisesRegex(ValueError, "Antigravity CLI"):
                    evaluate_agy.cli_command()

            with patch.object(evaluate_agy.shutil, "which", side_effect=[r"C:\bin\agy.ps1", r"C:\pwsh\pwsh.exe"]):
                cmd = evaluate_agy.cli_command()
                self.assertEqual(cmd[0], r"C:\pwsh\pwsh.exe")
                self.assertEqual(cmd[-1], r"C:\bin\agy.ps1")

            with patch.dict(os.environ, {"COMSPEC": r"C:\Windows\System32\cmd.exe"}, clear=False), \
                 patch.object(evaluate_agy.shutil, "which", return_value=r"C:\bin\agy.cmd"):
                self.assertEqual(evaluate_agy.cli_command(), [r"C:\Windows\System32\cmd.exe", "/c", r"C:\bin\agy.cmd"])

    def test_run_suite_idempotent_resume_effort_grader_and_failure_status(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            suite = root / "suite.json"
            case = {"id": "c1", "setup": "s", "prompt": "p", "grading": True}
            e.write_json(suite, {"name": "s", "cases": [case]})
            output = root / "runs"
            args = argparse.Namespace(
                suite=suite, models=["m1"], condition="none", skill=None, output=output,
                cases=None, repeat=1, workers=1, timeout=30, limit=94, effort="high",
            )
            seen_commands = []
            seen_agent_files = []

            def fake_run(cmd, cwd=None, **kwargs):
                seen_commands.append(cmd)
                agent_file = Path(cwd) / ".agents" / "agents" / "sdc-grader.md"
                seen_agent_files.append(agent_file.read_text(encoding="utf-8") if agent_file.is_file() else "")
                stdout = "\n".join([
                    json.dumps({"event": "init", "init": {"model": "m1"}}),
                    json.dumps({"event": "result", "result": {"status": "SUCCESS", "response": "[]", "usage": {"input_tokens": 1}}}),
                ]) + "\n"
                return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")

            with patch.object(evaluate_agy, "cli_command", return_value=["agy"]), \
                 patch.object(evaluate_agy.subprocess, "run", side_effect=fake_run):
                evaluate_agy.run_suite(args)

            self.assertIn("--agent", seen_commands[0])
            self.assertEqual(seen_commands[0][seen_commands[0].index("--agent") + 1], "sdc-grader")
            self.assertEqual(seen_commands[0][seen_commands[0].index("--effort") + 1], "high")
            self.assertIn("name: sdc-grader", seen_agent_files[0])
            target = output / "s.c1.m1.none.1.json"
            self.assertEqual(e.read_json(target)["reasoning_effort"], "high")

            # Re-running with matching inputs skips cleanly without calling subprocess.
            with patch.object(evaluate_agy, "cli_command", return_value=["agy"]), \
                 patch.object(evaluate_agy.subprocess, "run", side_effect=AssertionError("should not rerun")):
                evaluate_agy.run_suite(args)

            # Re-running with changed effort raises ValueError.
            args.effort = "low"
            with self.assertRaisesRegex(ValueError, "immutable trial"):
                evaluate_agy.run_suite(args)

            # Uncaught exception in run() records failed status and error field instead of reserved.
            args.repeat = 2
            with patch.object(evaluate_agy, "cli_command", return_value=["agy"]), \
                 patch.object(evaluate_agy.subprocess, "run", side_effect=OSError("spawn failure")):
                evaluate_agy.run_suite(args)
            failed_rec = e.read_json(output / "s.c1.m1.none.2.json")
            self.assertEqual(failed_rec["status"], "failed")
            self.assertIn("spawn failure", failed_rec["error"])

    def test_other_skill_commands_are_not_duplicated_and_lock_writes_pid(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            suite = root / "suite.json"
            e.write_json(suite, {"name": "s", "cases": [{"id": "c1", "setup": "s", "prompt": "p"}]})
            output = root / "runs"
            args = argparse.Namespace(
                suite=suite, models=["m1"], condition="none", skill=None, output=output,
                cases=None, repeat=1, workers=1, timeout=30, limit=94, effort="medium",
            )
            seen_lock = []

            def fake_run(cmd, cwd=None, **kwargs):
                seen_lock.append((output / "run.lock").read_text(encoding="utf-8"))
                stdout = "\n".join([
                    json.dumps({"event": "init", "init": {"model": "m1"}}),
                    json.dumps({"event": "step_update", "step_update": {
                        "state": "DONE", "step_type": "tool", "tool_info": {
                            "parameters": {"CommandLine": "cat ~/.agents/skills/other/SKILL.md"},
                            "output": "x",
                        },
                    }}),
                    json.dumps({"event": "result", "result": {"status": "SUCCESS", "response": "ans"}}),
                ]) + "\n"
                return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")

            with patch.object(evaluate_agy, "cli_command", return_value=["agy"]), \
                 patch.object(evaluate_agy.subprocess, "run", side_effect=fake_run):
                evaluate_agy.run_suite(args)

            self.assertIn(f"pid={os.getpid()}", seen_lock[0])
            rec = e.read_json(output / "s.c1.m1.none.1.json")
            self.assertEqual(rec["status"], "contaminated")
            self.assertEqual(len(rec["other_skill_commands"]), 1)

            (output / "run.lock").write_text("pid=1\n", encoding="utf-8")
            args.repeat = 2
            with self.assertRaisesRegex(ValueError, "run\\.lock"):
                evaluate_agy.run_suite(args)


if __name__ == "__main__":
    unittest.main()
