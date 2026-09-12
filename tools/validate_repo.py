"""Validate repository invariants that the Agent Skills schema does not cover."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "system-design-compass"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_PATTERN = re.compile(r"\[(?:TODO|PLACEHOLDER)[^\]]*\]|\bFIXME\b", re.IGNORECASE)


def check_required_files(errors: list[str]) -> None:
    required = (
        REPO_ROOT / "README.md",
        REPO_ROOT / "LICENSE",
        REPO_ROOT / "CONTRIBUTING.md",
        REPO_ROOT / "SECURITY.md",
        REPO_ROOT / ".github" / "workflows" / "validate.yml",
        REPO_ROOT / "evals" / "cases.md",
        SKILL_FILE,
        SKILL_ROOT / "agents" / "openai.yaml",
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(REPO_ROOT)}")


def check_skill_entrypoint(errors: list[str]) -> None:
    if not SKILL_FILE.is_file():
        return

    text = SKILL_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 300:
        errors.append(f"SKILL.md has {len(lines)} lines; maximum is 300")

    word_count = len(re.findall(r"\S+", text))
    if word_count > 2_200:
        errors.append(
            f"SKILL.md has {word_count} words; context-friendly maximum is 2200"
        )

    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end == -1:
        errors.append("SKILL.md frontmatter is not closed")
        frontmatter = ""
    else:
        frontmatter = text[4:frontmatter_end]

    expected_fields = {
        "name": "system-design-compass",
        "license": "MIT",
    }
    for key, expected in expected_fields.items():
        match = re.search(rf"^{re.escape(key)}:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
        if not match or match.group(1).strip() != expected:
            errors.append(f"SKILL.md frontmatter must set {key}: {expected}")

    if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
        errors.append("SKILL.md frontmatter requires a non-empty description")
    if re.search(r"^allowed-tools:", frontmatter, re.MULTILINE):
        errors.append("SKILL.md must not pre-approve tools")

    reference_dir = SKILL_ROOT / "references"
    references = sorted(reference_dir.glob("*.md"))
    linked = {unquote(target.split("#", 1)[0]) for target in LINK_PATTERN.findall(text)}
    for reference in references:
        expected_link = reference.relative_to(SKILL_ROOT).as_posix()
        if expected_link not in linked:
            errors.append(f"reference is not linked directly from SKILL.md: {expected_link}")

    archetype_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in reference_dir.glob("archetypes-*.md")
    )
    numbers = [int(value) for value in re.findall(r"^##\s+(\d+)\.", archetype_text, re.MULTILINE)]
    if sorted(numbers) != list(range(1, 29)):
        errors.append(
            "archetype catalogs must contain each numbered topic from 1 through 28 exactly once"
        )


def check_markdown(errors: list[str]) -> None:
    markdown_files = sorted(REPO_ROOT.rglob("*.md"))
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_PATTERN.search(text):
            errors.append(f"unfinished placeholder in {path.relative_to(REPO_ROOT)}")

        headings = [
            re.sub(r"\s+", " ", heading).strip().casefold()
            for heading in HEADING_PATTERN.findall(text)
        ]
        duplicates = [name for name, count in Counter(headings).items() if count > 1]
        if duplicates:
            errors.append(
                f"duplicate heading in {path.relative_to(REPO_ROOT)}: {duplicates[0]}"
            )

        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split(" ", 1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative_target = unquote(target.split("#", 1)[0])
            resolved = (path.parent / relative_target).resolve()
            try:
                resolved.relative_to(REPO_ROOT)
            except ValueError:
                errors.append(
                    f"link escapes repository in {path.relative_to(REPO_ROOT)}: {target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"broken local link in {path.relative_to(REPO_ROOT)}: {target}"
                )


def check_runtime_surface(errors: list[str]) -> None:
    if (SKILL_ROOT / "scripts").exists():
        errors.append("the distributable skill must not contain a scripts directory")

    allowed_suffixes = {".md", ".yaml", ".yml"}
    for path in SKILL_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() not in allowed_suffixes:
            errors.append(
                f"unexpected runtime file type: {path.relative_to(SKILL_ROOT)}"
            )

    metadata_file = SKILL_ROOT / "agents" / "openai.yaml"
    if metadata_file.is_file():
        metadata = metadata_file.read_text(encoding="utf-8")
        if "$system-design-compass" not in metadata:
            errors.append("agents/openai.yaml default prompt must name $system-design-compass")
        if "dependencies:" in metadata:
            errors.append("agents/openai.yaml must not declare runtime dependencies")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_skill_entrypoint(errors)
    check_markdown(errors)
    check_runtime_surface(errors)

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    reference_count = len(list((SKILL_ROOT / "references").glob("*.md")))
    print(
        "Repository validation passed: "
        f"1 skill, {reference_count} references, 28 workload topics."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
