"""Unit tests for repository invariant checks in validate_repo."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if __package__:
    from . import validate_repo
    from .validate_repo import (
        MAX_REFERENCE_WORDS,
        check_markdown,
        check_reference_budgets,
        check_runtime_surface,
        check_skill_entrypoint,
        check_workspace_mirror,
        heading_slug,
    )
else:
    import validate_repo
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
    (skill_root / "SKILL.md").write_text(VALID_SKILL_MD, encoding="utf-8", newline="\n")
    (skill_root / "agents" / "openai.yaml").write_text(
        "interface:\n"
        '  display_name: "System Design Compass"\n'
        '  short_description: "Design, review, and evolve production systems"\n'
        '  default_prompt: "Use $system-design-compass to design, review, or evolve this production system."\n',
        encoding="utf-8",
        newline="\n",
    )
    (skill_root / "references" / "interfaces-data.md").write_text(
        "# Interfaces and Data\n\n"
        "## Resolve an external outcome before retry or correction\n\n"
        "Verify provider state before issuing compensating actions.\n",
        encoding="utf-8",
        newline="\n",
    )
    topics = "\n\n".join(f"## {i}. Topic {i}\n\nDecision guidance." for i in range(1, 29))
    (skill_root / "references" / "archetypes-foundations-platform.md").write_text(
        f"# Archetypes\n\n{topics}\n",
        encoding="utf-8",
        newline="\n",
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

            # Identical LF mirror passes.
            build_valid_skill_tree(mirror_root)
            check_workspace_mirror(errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertEqual(errors, [])

            # CRLF line-ending mismatch is detected by raw byte comparison.
            skill_md = mirror_root / "SKILL.md"
            skill_md.write_bytes(skill_md.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
            crlf_errors: list[str] = []
            check_workspace_mirror(crlf_errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertTrue(any("out of sync" in e and "SKILL.md" in e for e in crlf_errors), crlf_errors)
            skill_md.write_bytes(skill_md.read_bytes().replace(b"\r\n", b"\n"))

            # Non-allowed runtime file in mirror is detected via check_runtime_surface.
            (mirror_root / "helper.py").write_text("print('hi')\n", encoding="utf-8")
            surface_errors: list[str] = []
            check_workspace_mirror(surface_errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertTrue(any("unexpected runtime file type" in e for e in surface_errors), surface_errors)
            (mirror_root / "helper.py").unlink()

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

    def test_frontmatter_rejects_invalid_name_long_description_xml_and_empty_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            long_name = "a" * 65
            skill_root = Path(tmp) / "skills" / long_name
            build_valid_skill_tree(skill_root)
            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD.replace("name: system-design-compass", f"name: {long_name}"),
                encoding="utf-8",
            )
            errors: list[str] = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertTrue(any("name" in e for e in errors), errors)

        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD.replace(
                    "description: Resolve architecture decisions in production system design.",
                    "description: " + ("x" * 1025),
                ),
                encoding="utf-8",
            )
            errors = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertTrue(any("1024" in e for e in errors), errors)

            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD.replace(
                    "description: Resolve architecture decisions in production system design.",
                    "description: Resolve <unsafe>tag</unsafe> decisions.",
                ),
                encoding="utf-8",
            )
            errors = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertTrue(any("XML" in e for e in errors), errors)

            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD.replace(
                    "description: Resolve architecture decisions in production system design.",
                    "description: >-\n\n",
                ),
                encoding="utf-8",
            )
            errors = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertTrue(any("non-empty description" in e for e in errors), errors)

            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD.replace(
                    "description: Resolve architecture decisions in production system design.",
                    "description: >-\n  Resolve architecture decisions\n  in production systems.",
                ),
                encoding="utf-8",
            )
            errors = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertEqual(errors, [])

    def test_archetype_catalogs_reject_gaps_within_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            (skill_root / "references" / "archetypes-foundations-platform.md").write_text(
                "# Foundations\n\n" + "\n\n".join(f"## {i}. Topic {i}\n\nGuidance." for i in range(1, 19)),
                encoding="utf-8",
            )
            (skill_root / "references" / "archetypes-data-infrastructure.md").write_text(
                "# Data\n\n" + "\n\n".join(f"## {i}. Topic {i}\n\nGuidance." for i in (19, 20, 21, 23, 24)),
                encoding="utf-8",
            )
            (skill_root / "references" / "archetypes-transactional-financial.md").write_text(
                "# Financial\n\n" + "\n\n".join(f"## {i}. Topic {i}\n\nGuidance." for i in (22, 25, 26, 27, 28)),
                encoding="utf-8",
            )
            (skill_root / "SKILL.md").write_text(
                VALID_SKILL_MD
                + "\nRead [data](references/archetypes-data-infrastructure.md) and "
                "[fin](references/archetypes-transactional-financial.md).\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_skill_entrypoint(errors, skill_root=skill_root)
            self.assertTrue(any("consecutively" in e or "ascending" in e for e in errors), errors)

    def test_openai_yaml_ignores_commented_dependencies_and_requires_interface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            (skill_root / "agents" / "openai.yaml").write_text(
                "# No runtime dependencies: none\n"
                "interface:\n"
                '  display_name: "System Design Compass"\n'
                '  short_description: "Design, review, and evolve production systems"\n'
                '  default_prompt: "Use $system-design-compass"\n',
                encoding="utf-8",
            )
            errors: list[str] = []
            check_runtime_surface(errors, skill_root=skill_root)
            self.assertEqual(errors, [])

            (skill_root / "agents" / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "System Design Compass"\n'
                '  short_description: "Design, review, and evolve production systems"\n'
                '  default_prompt: "Use $system-design-compass"\n'
                "dependencies:\n"
                "  - foo\n",
                encoding="utf-8",
            )
            errors = []
            check_runtime_surface(errors, skill_root=skill_root)
            self.assertTrue(any("dependencies" in e for e in errors), errors)

            (skill_root / "agents" / "openai.yaml").write_text(
                'default_prompt: "Use $system-design-compass"\n',
                encoding="utf-8",
            )
            errors = []
            check_runtime_surface(errors, skill_root=skill_root)
            self.assertTrue(any("interface" in e for e in errors), errors)

    def test_check_markdown_excludes_external_agent_and_local_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            skill_root = repo_root / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            dup = "# Doc\n\n## Repeated\n\n## Repeated\n"
            for rel in (
                ".venv/pkg/README.md",
                ".codegraph/info.md",
                "analizler/report.md",
                "evals/artifacts/run/out.md",
                ".agents/skills/other-skill/SKILL.md",
            ):
                p = repo_root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(dup, encoding="utf-8")

            errors: list[str] = []
            check_markdown(errors, repo_root=repo_root)
            self.assertEqual(errors, [])

    def test_check_eval_json_validates_evals_and_skips_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "evals" / "results").mkdir(parents=True)
            (repo_root / "evals" / "artifacts").mkdir(parents=True)
            (repo_root / "evals" / "benchmark.json").write_text('{"cases": []}\n', encoding="utf-8")
            (repo_root / "evals" / "results" / "ok.json").write_text('{"ok": true}\n', encoding="utf-8")
            (repo_root / "evals" / "artifacts" / "ignored.json").write_text("{broken", encoding="utf-8")

            errors: list[str] = []
            validate_repo.check_eval_json(errors, repo_root=repo_root)
            self.assertEqual(errors, [])

            (repo_root / "evals" / "results" / "bad.json").write_text('{"ok": true}\n\\n', encoding="utf-8")
            validate_repo.check_eval_json(errors, repo_root=repo_root)
            self.assertTrue(any("bad.json" in e for e in errors), errors)

    def test_fix_mirror_syncs_lf_bytes_and_cleans_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_root = root / "skills" / "system-design-compass"
            mirror_root = root / ".agents" / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            # Put CRLF in source SKILL.md to confirm mirror gets LF.
            src_skill = skill_root / "SKILL.md"
            src_skill.write_bytes(src_skill.read_bytes().replace(b"\n", b"\r\n"))

            (mirror_root / "references").mkdir(parents=True)
            (mirror_root / "references" / "stale.md").write_text("## Stale\n", encoding="utf-8")
            (mirror_root / "stray.py").write_text("x = 1\n", encoding="utf-8")

            validate_repo.fix_workspace_mirror(skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertFalse((mirror_root / "references" / "stale.md").exists())
            self.assertFalse((mirror_root / "stray.py").exists())
            self.assertNotIn(b"\r\n", (mirror_root / "SKILL.md").read_bytes())

            # When source is LF too, check_workspace_mirror passes completely.
            src_skill.write_bytes(src_skill.read_bytes().replace(b"\r\n", b"\n"))
            errors: list[str] = []
            check_workspace_mirror(errors, skill_root=skill_root, workspace_skill_root=mirror_root)
            self.assertEqual(errors, [])

    def test_main_fix_mirror_flag_syncs_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_root = root / "skills" / "system-design-compass"
            mirror_root = root / ".agents" / "skills" / "system-design-compass"
            build_valid_skill_tree(skill_root)
            for rel in (
                "README.md",
                "LICENSE",
                "CONTRIBUTING.md",
                "SECURITY.md",
                ".github/workflows/validate.yml",
                "evals/cases.md",
            ):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("# Doc\n", encoding="utf-8", newline="\n")

            with patch.object(validate_repo, "REPO_ROOT", root), \
                 patch.object(validate_repo, "SKILL_ROOT", skill_root), \
                 patch.object(validate_repo, "WORKSPACE_SKILL_ROOT", mirror_root), \
                 patch.object(validate_repo, "SKILL_FILE", skill_root / "SKILL.md"):
                exit_code = validate_repo.main(["--fix-mirror"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((mirror_root / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
