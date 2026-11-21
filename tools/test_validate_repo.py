"""Unit tests for repository invariant checks in validate_repo."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_repo import (
    MAX_REFERENCE_WORDS,
    check_markdown,
    check_reference_budgets,
    check_runtime_surface,
    check_skill_entrypoint,
    check_workspace_mirror,
    heading_slug,
)


VALID_SKILL_MD = """---
name: system-design-compass
description: Resolve architecture decisions in production system design.
license: MIT
---

# System Design Compass

Read [interfaces](references/interfaces-data.md#resolve-an-external-outcome-before-retry-or-correction) and [catalog](references/archetypes-foundations-platform.md).
"""


def build_valid_skill_tree(skill_root: Path) -> None:
    (skill_root / "references").mkdir(parents=True, exist_ok=True)
    (skill_root / "agents").mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text(VALID_SKILL_MD, encoding="utf-8")
    (skill_root / "agents" / "openai.yaml").write_text(
        "default_prompt: Use $system-design-compass\n",
        encoding="utf-8",
    )
    (skill_root / "references" / "interfaces-data.md").write_text(
        "# Interfaces and Data\n\n"
        "## Resolve an external outcome before retry or correction\n\n"
        "Verify provider state before issuing compensating actions.\n",
        encoding="utf-8",
    )
    topics = "\n\n".join(f"## {i}. Topic {i}\n\nDecision guidance." for i in range(1, 29))
    (skill_root / "references" / "archetypes-foundations-platform.md").write_text(
        f"# Archetypes\n\n{topics}\n",
        encoding="utf-8",
    )


class ValidateRepoTests(unittest.TestCase):
    def test_heading_slug_normalizes_case_punctuation_and_spaces(self) -> None:
        self.assertEqual(
            heading_slug("Resolve an external outcome before retry or correction"),
            "resolve-an-external-outcome-before-retry-or-correction",
        )
        self.assertEqual(
            heading_slug("Why Compass:  The Decision / Lens?"),
            "why-compass-the-decision-lens",
        )

    def test_valid_skill_entrypoint_and_references_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            errors: list[str] = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertEqual(errors, [])

    def test_reference_word_budget_overflow_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            over_budget = " ".join(["word"] * (MAX_REFERENCE_WORDS + 1))
            (skill_root / "references" / "interfaces-data.md").write_text(
                f"# Interfaces\n\n## Section\n\n{over_budget}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_reference_budgets(errors, skill_root=skill_root)
            self.assertTrue(
                any("maximum is 2500" in error for error in errors),
                errors,
            )

    def test_empty_or_sectionless_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            (skill_root / "references" / "empty.md").write_text("   \n", encoding="utf-8")
            (skill_root / "references" / "no-subheading.md").write_text(
                "# Only Title\n\nBody text without level-two headings.\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_reference_budgets(errors, skill_root=skill_root)
            self.assertTrue(any("reference file is empty" in e for e in errors), errors)
            self.assertTrue(
                any("at least one '## ' section heading" in e for e in errors),
                errors,
            )

    def test_markdown_valid_and_broken_anchors_and_duplicate_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            skill_root = repo_root / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)

            errors: list[str] = []
            check_markdown(errors, repo_root=repo_root)
            self.assertEqual(errors, [])

            (repo_root / "NOTES.md").write_text(
                "# Notes\n\n"
                "## Duplicate Heading\n\n"
                "## duplicate   heading\n\n"
                "See [broken cross](skills/system-design-compass/references/interfaces-data.md#non-existent-anchor) "
                "and [broken local](#missing-local).\n",
                encoding="utf-8",
            )
            check_markdown(errors, repo_root=repo_root)
            self.assertTrue(
                any("duplicate heading" in e for e in errors),
                errors,
            )
            self.assertTrue(
                any("broken markdown anchor" in e and "#non-existent-anchor" in e for e in errors),
                errors,
            )
            self.assertTrue(
                any("broken markdown anchor" in e and "#missing-local" in e for e in errors),
                errors,
            )

    def test_workspace_mirror_detects_drift_missing_and_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_root = root / "skills" / "system-design-compass"
            mirror_root = root / ".agents" / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)

            # Non-existent mirror directory is allowed.
            errors: list[str] = []
            check_workspace_mirror(errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertEqual(errors, [])

            # Identical mirror with CRLF normalization passes.
            build_valid_skill_tree(mirror_root)
            skill_md = mirror_root / "SKILL.md"
            skill_md.write_bytes(skill_md.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
            check_workspace_mirror(errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertEqual(errors, [])

            # Content drift is detected.
            (mirror_root / "references" / "interfaces-data.md").write_text(
                "# Interfaces and Data\n\n## Drifted heading\n",
                encoding="utf-8",
            )
            # Missing file in mirror is detected.
            (mirror_root / "agents" / "openai.yaml").unlink()
            # Extra file in mirror is detected.
            (mirror_root / "references" / "extra.md").write_text("## Extra\n", encoding="utf-8")

            check_workspace_mirror(errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertTrue(any("out of sync" in e and "interfaces-data.md" in e for e in errors), errors)
            self.assertTrue(any("missing file: agents/openai.yaml" in e for e in errors), errors)
            self.assertTrue(any("unexpected extra file" in e and "extra.md" in e for e in errors), errors)

    def test_runtime_surface_rejects_scripts_and_non_markdown_or_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            (skill_root / "scripts").mkdir()
            (skill_root / "helper.py").write_text("print('hi')\n", encoding="utf-8")
            errors: list[str] = []
            check_runtime_surface(errors, skill_root=skill_root)
            self.assertTrue(any("scripts directory" in e for e in errors), errors)
            self.assertTrue(any("unexpected runtime file type" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
