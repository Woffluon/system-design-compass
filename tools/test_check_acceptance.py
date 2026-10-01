"""Acceptance cannot be manufactured from incomplete coverage or one lucky correction."""

import unittest

from check_acceptance import check


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.suites = [{"name": "benchmark", "cases": [{"id": x} for x in ("hard", "narrow-adr", "sound-system")]},
                       {"name": "regression", "cases": [{"id": "existing"}]}]
        self.baseline = [self.record("benchmark", c, condition, 1, not (c == "hard" and condition == "current"), 100)
                         for condition in ("none", "current") for c in ("hard", "narrow-adr", "sound-system")]
        self.candidate = [self.record("benchmark", c, "candidate", 1, True, 50)
                          for c in ("hard", "narrow-adr", "sound-system")]
        self.candidate += [self.record("regression", "existing", "candidate", 1, True, 50)]
        self.candidate += [self.record("benchmark", "hard", "candidate", n, True, 50) for n in (2, 3)]

    @staticmethod
    def record(suite, case, condition, repeat, passed, words):
        return {"model": "model", "suite": suite, "case": case, "condition": condition, "repeat": repeat,
                "grade": {"case_pass": passed}, "observed_skill_read_output_words": words}

    def test_complete_repeated_improvement_passes(self):
        self.assertEqual(check(self.baseline, self.candidate, ["model"], self.suites), [])

    def test_missing_model_cannot_pass(self):
        self.assertTrue(check(self.baseline, self.candidate, ["model", "missing"], self.suites))

    def test_single_confirmation_is_insufficient(self):
        self.assertTrue(check(self.baseline, self.candidate[:-1], ["model"], self.suites))

    def test_failed_confirmation_cannot_be_averaged_away(self):
        self.candidate[-1]["grade"]["case_pass"] = False
        self.assertTrue(check(self.baseline, self.candidate, ["model"], self.suites))

    def test_context_increase_cannot_pass(self):
        self.candidate[1]["observed_skill_read_output_words"] = 101
        self.assertTrue(check(self.baseline, self.candidate, ["model"], self.suites))

    def test_harder_cases_extend_instead_of_replace_benchmark_coverage(self):
        self.suites.append({"name": "benchmark", "cases": [{"id": "harder"}]})
        self.baseline += [self.record("benchmark", "harder", c, 1, True, 100) for c in ("none", "current")]
        self.assertTrue(check(self.baseline, self.candidate, ["model"], self.suites))
        self.candidate.append(self.record("benchmark", "harder", "candidate", 1, True, 50))
        self.assertEqual(check(self.baseline, self.candidate, ["model"], self.suites), [])


if __name__ == "__main__":
    unittest.main()
