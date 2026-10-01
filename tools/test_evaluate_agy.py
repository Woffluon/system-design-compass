import unittest

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


if __name__ == "__main__":
    unittest.main()
