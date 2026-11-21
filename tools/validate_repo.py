"""Validate repository invariants that the Agent Skills schema does not cover."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "system-design-compass"
WORKSPACE_SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "system-design-compass"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
MAX_REFERENCE_WORDS = 2500
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_PATTERN = re.compile(r"\[(?:TODO|PLACEHOLDER)[^\]]*\]|\bFIXME\b", re.IGNORECASE)


def heading_slug(heading: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 -]", "", heading.casefold()).strip()
    return re.sub(r"\s+", "-", cleaned)


def check_required_files(
    errors: list[str],
    repo_root: Path | None = None,
    skill_root: Path | None = None,
) -> None:
    root = repo_root if repo_root is not None else REPO_ROOT
    skill = (
        skill_root
        if skill_root is not None
        else (SKILL_ROOT if repo_root is None else root / "skills" / "system-design-compass")
    )
    skill_file = SKILL_FILE if (repo_root is None and skill_root is None) else skill / "SKILL.md"
    required = (
        root / "README.md",
        root / "LICENSE",
        root / "CONTRIBUTING.md",
        root / "SECURITY.md",
        root / ".github" / "workflows" / "validate.yml",
        root / "evals" / "cases.md",
        skill_file,
        skill / "agents" / "openai.yaml",
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(root)}")


def check_reference_budgets(
    errors: list[str],
    skill_root: Path | None = None,
    max_words: int = MAX_REFERENCE_WORDS,
) -> None:
    root = skill_root if skill_root is not None else SKILL_ROOT
    reference_dir = root / "references"
    for reference in sorted(reference_dir.glob("*.md")):
        rel_ref = reference.relative_to(root).as_posix()
        text = reference.read_text(encoding="utf-8")
        word_count = len(re.findall(r"\S+", text))
        if word_count == 0:
            errors.append(f"reference file is empty: {rel_ref}")
            continue
        if not re.search(r"^##\s+\S", text, re.MULTILINE):
            errors.append(
                f"reference must contain at least one '## ' section heading: {rel_ref}"
            )
        if word_count > max_words:
            errors.append(
                f"reference {rel_ref} has {word_count} words; maximum is {max_words}"
            )


def check_skill_entrypoint(
    errors: list[str],
    skill_root: Path | None = None,
) -> None:
    root = skill_root if skill_root is not None else SKILL_ROOT
    skill_file = SKILL_FILE if (skill_root is None and root == SKILL_ROOT) else root / "SKILL.md"
    if not skill_file.is_file():
        return

    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 300:
        errors.append(f"SKILL.md has {len(lines)} lines; maximum is 300")

    word_count = len(re.findall(r"\S+", text))
    if word_count > 500:
        errors.append(
            f"SKILL.md has {word_count} words; entrypoint maximum is 500"
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

    reference_dir = root / "references"
    references = sorted(reference_dir.glob("*.md"))
    linked = {unquote(target.split("#", 1)[0]) for target in LINK_PATTERN.findall(text)}
    for reference in references:
        expected_link = reference.relative_to(root).as_posix()
        if expected_link not in linked:
            errors.append(f"reference is not linked directly from SKILL.md: {expected_link}")

    check_reference_budgets(errors, root)

    archetype_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in reference_dir.glob("archetypes-*.md")
    )
    numbers = [int(value) for value in re.findall(r"^##\s+(\d+)\.", archetype_text, re.MULTILINE)]
    if sorted(numbers) != list(range(1, 29)):
        errors.append(
            "archetype catalogs must contain each numbered topic from 1 through 28 exactly once"
        )


def check_markdown(
    errors: list[str],
    repo_root: Path | None = None,
) -> None:
    root = (repo_root if repo_root is not None else REPO_ROOT).resolve()
    markdown_files = sorted(root.rglob("*.md"))
    slug_cache: dict[Path, set[str]] = {}

    def slugs_for(md_path: Path, fallback_text: str | None = None) -> set[str]:
        if md_path not in slug_cache:
            content = (
                fallback_text
                if fallback_text is not None
                else md_path.read_text(encoding="utf-8")
            )
            slug_cache[md_path] = {
                heading_slug(heading) for heading in HEADING_PATTERN.findall(content)
            }
        return slug_cache[md_path]

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_PATTERN.search(text):
            errors.append(f"unfinished placeholder in {path.relative_to(root)}")

        headings = [
            re.sub(r"\s+", " ", heading).strip().casefold()
            for heading in HEADING_PATTERN.findall(text)
        ]
        duplicates = [name for name, count in Counter(headings).items() if count > 1]
        if duplicates:
            errors.append(
                f"duplicate heading in {path.relative_to(root)}: {duplicates[0]}"
            )

        slugs_for(path, text)

        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split(" ", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part, has_anchor, anchor_part = target.partition("#")
            if path_part:
                relative_target = unquote(path_part)
                resolved = (path.parent / relative_target).resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    errors.append(
                        f"link escapes repository in {path.relative_to(root)}: {target}"
                    )
                    continue
                if not resolved.exists():
                    errors.append(
                        f"broken local link in {path.relative_to(root)}: {target}"
                    )
                    continue
            else:
                resolved = path

            if has_anchor and resolved.is_file() and resolved.suffix.lower() == ".md":
                anchor = unquote(anchor_part).strip().casefold()
                if not anchor or anchor not in slugs_for(resolved):
                    errors.append(
                        f"broken markdown anchor in {path.relative_to(root)}: {target}"
                    )


def check_runtime_surface(
    errors: list[str],
    skill_root: Path | None = None,
) -> None:
    root = skill_root if skill_root is not None else SKILL_ROOT
    if (root / "scripts").exists():
        errors.append("the distributable skill must not contain a scripts directory")

    allowed_suffixes = {".md", ".yaml", ".yml"}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() not in allowed_suffixes:
            errors.append(
                f"unexpected runtime file type: {path.relative_to(root)}"
            )

    metadata_file = root / "agents" / "openai.yaml"
    if metadata_file.is_file():
        metadata = metadata_file.read_text(encoding="utf-8")
        if "$system-design-compass" not in metadata:
            errors.append("agents/openai.yaml default prompt must name $system-design-compass")
        if "dependencies:" in metadata:
            errors.append("agents/openai.yaml must not declare runtime dependencies")


def check_workspace_mirror(
    errors: list[str],
    skill_root: Path | None = None,
    workspace_skill_root: Path | None = None,
) -> None:
    source_root = skill_root if skill_root is not None else SKILL_ROOT
    mirror_root = (
        workspace_skill_root
        if workspace_skill_root is not None
        else WORKSPACE_SKILL_ROOT
    )
    if not mirror_root.exists():
        return

    allowed_suffixes = {".md", ".yaml", ".yml"}
    source_files = {
        path.relative_to(source_root).as_posix(): path
        for path in sorted(source_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed_suffixes
    }
    mirror_files = {
        path.relative_to(mirror_root).as_posix(): path
        for path in sorted(mirror_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed_suffixes
    }

    for rel_path, source_path in source_files.items():
        mirror_path = mirror_files.get(rel_path)
        if mirror_path is None:
            errors.append(f"workspace mirror missing file: {rel_path}")
            continue
        source_text = source_path.read_text(encoding="utf-8").replace("\r\n", "\n")
        mirror_text = mirror_path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if source_text != mirror_text:
            errors.append(
                f"workspace mirror out of sync with skill source: {rel_path}"
            )

    for rel_path in sorted(set(mirror_files) - set(source_files)):
        errors.append(f"unexpected extra file in workspace mirror: {rel_path}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_skill_entrypoint(errors)
    check_markdown(errors)
    check_runtime_surface(errors)
    check_workspace_mirror(errors)

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
