"""Validate repository invariants that the Agent Skills schema does not cover."""

from __future__ import annotations

import argparse
import json
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
MAX_SKILL_NAME_LENGTH = 64
MAX_SKILL_DESCRIPTION_LENGTH = 1024
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_TAG_PATTERN = re.compile(r"<[^>]+>")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_PATTERN = re.compile(r"\[(?:TODO|PLACEHOLDER)[^\]]*\]|\bFIXME\b", re.IGNORECASE)
BLOCK_SCALAR_PATTERN = re.compile(r"^(?:[|>][+-]?\d*|[|>]\d+[+-]?)$")


def heading_slug(heading: str) -> str:
    """Convert a Markdown heading to the repo's lowercase ASCII anchor slug.

    Retains only ASCII ``a-z``, ``0-9``, spaces, and hyphens, then collapses
    runs of whitespace to a single hyphen (GitHub's slugger keeps consecutive
    hyphens from removed punctuation; this helper normalizes separated tokens
    to a single hyphen).
    """
    cleaned = re.sub(r"[^a-z0-9 -]", "", heading.casefold()).strip()
    return re.sub(r"\s+", "-", cleaned)


def _strip_yaml_comment(raw: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or raw[idx - 1].isspace():
                return raw[:idx].rstrip()
    return raw.rstrip()


def _unquote_yaml_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        if value[0] == "'":
            return value[1:-1].replace("''", "'")
        try:
            parsed = json.loads(value)
            if isinstance(parsed, str):
                return parsed
        except json.JSONDecodeError:
            pass
        return value[1:-1]
    return value


def _line_indent(line: str) -> int:
    leading = line[:len(line) - len(line.lstrip(" \t"))]
    if "\t" in leading:
        raise ValueError("tabs are not allowed in YAML indentation")
    return len(leading)


def _parse_yaml_mapping(text: str) -> dict[str, object]:
    """Parse a minimal indentation- and comment-aware YAML mapping using stdlib only."""
    lines = text.splitlines()

    def next_content_index(start: int) -> int | None:
        idx = start
        while idx < len(lines):
            stripped = _strip_yaml_comment(lines[idx]).strip()
            if stripped:
                return idx
            idx += 1
        return None

    def parse_block_scalar(start: int, parent_indent: int, style: str) -> tuple[str, int]:
        idx = start
        block_indent: int | None = None
        collected: list[str] = []
        while idx < len(lines):
            raw = lines[idx]
            if not raw.strip():
                collected.append("")
                idx += 1
                continue
            indent = _line_indent(raw)
            if indent <= parent_indent:
                break
            if block_indent is None:
                block_indent = indent
            elif indent < block_indent:
                raise ValueError(f"inconsistent block scalar indentation on line {idx + 1}")
            collected.append(raw[block_indent:])
            idx += 1

        while collected and not collected[-1].strip():
            collected.pop()
        if not any(part.strip() for part in collected):
            return "", idx
        if style.startswith(">"):
            paragraphs: list[str] = []
            current: list[str] = []
            for part in collected:
                if not part.strip():
                    if current:
                        paragraphs.append(" ".join(current))
                        current = []
                else:
                    current.append(part.strip())
            if current:
                paragraphs.append(" ".join(current))
            return "\n".join(paragraphs), idx
        return "\n".join(collected), idx

    def parse_list(start: int, expected_indent: int) -> tuple[list[str], int]:
        items: list[str] = []
        idx = start
        while idx < len(lines):
            cleaned = _strip_yaml_comment(lines[idx])
            if not cleaned.strip():
                idx += 1
                continue
            indent = _line_indent(cleaned)
            if indent < expected_indent:
                break
            if indent != expected_indent:
                raise ValueError(f"unexpected list indentation on line {idx + 1}")
            stripped = cleaned.strip()
            if not stripped.startswith("- ") and stripped != "-":
                break
            items.append(_unquote_yaml_scalar(stripped[1:].strip()))
            idx += 1
        return items, idx

    def parse_map(start: int, expected_indent: int) -> tuple[dict[str, object], int]:
        mapping: dict[str, object] = {}
        idx = start
        while idx < len(lines):
            cleaned = _strip_yaml_comment(lines[idx])
            if not cleaned.strip():
                idx += 1
                continue
            indent = _line_indent(cleaned)
            if indent < expected_indent:
                break
            if indent != expected_indent:
                raise ValueError(f"unexpected indentation on line {idx + 1}")
            content = cleaned.strip()
            if ":" not in content:
                raise ValueError(f"expected key: value on line {idx + 1}")
            key, _, rest = content.partition(":")
            key = key.strip()
            if not key:
                raise ValueError(f"empty YAML key on line {idx + 1}")
            value = rest.strip()
            idx += 1
            if BLOCK_SCALAR_PATTERN.match(value):
                parsed_value, idx = parse_block_scalar(idx, expected_indent, value)
                mapping[key] = parsed_value
            elif value == "":
                nxt = next_content_index(idx)
                if nxt is None:
                    mapping[key] = ""
                else:
                    nxt_cleaned = _strip_yaml_comment(lines[nxt])
                    nxt_indent = _line_indent(nxt_cleaned)
                    if nxt_indent <= expected_indent:
                        mapping[key] = ""
                    elif nxt_cleaned.strip().startswith("- ") or nxt_cleaned.strip() == "-":
                        mapping[key], idx = parse_list(nxt, nxt_indent)
                    else:
                        mapping[key], idx = parse_map(nxt, nxt_indent)
            else:
                mapping[key] = _unquote_yaml_scalar(value)
        return mapping, idx

    first = next_content_index(0)
    if first is None:
        return {}
    first_indent = _line_indent(_strip_yaml_comment(lines[first]))
    result, _ = parse_map(first, first_indent)
    return result


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
        frontmatter_data: dict[str, object] = {}
    else:
        frontmatter = text[4:frontmatter_end]
        try:
            frontmatter_data = _parse_yaml_mapping(frontmatter)
        except ValueError as exc:
            errors.append(f"SKILL.md frontmatter has invalid YAML: {exc}")
            frontmatter_data = {}

    name = frontmatter_data.get("name")
    if not isinstance(name, str) or not name:
        errors.append("SKILL.md frontmatter must set name")
    else:
        if len(name) > MAX_SKILL_NAME_LENGTH or not SKILL_NAME_PATTERN.fullmatch(name):
            errors.append(
                f"SKILL.md frontmatter name violates Agent Skills identifier rules (<= {MAX_SKILL_NAME_LENGTH} chars)"
            )
        if name != root.name:
            errors.append(f"SKILL.md frontmatter name must match directory name: {root.name}")

    if frontmatter_data.get("license") != "MIT":
        errors.append("SKILL.md frontmatter must set license: MIT")

    description = frontmatter_data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md frontmatter requires a non-empty description")
    else:
        if len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
            errors.append(
                f"SKILL.md frontmatter description has {len(description)} chars; maximum is {MAX_SKILL_DESCRIPTION_LENGTH}"
            )
        if XML_TAG_PATTERN.search(description):
            errors.append("SKILL.md frontmatter description must not contain XML tags")

    if "allowed-tools" in frontmatter_data:
        errors.append("SKILL.md must not pre-approve tools")

    reference_dir = root / "references"
    references = sorted(reference_dir.glob("*.md"))
    linked = {unquote(target.split("#", 1)[0]) for target in LINK_PATTERN.findall(text)}
    for reference in references:
        expected_link = reference.relative_to(root).as_posix()
        if expected_link not in linked:
            errors.append(f"reference is not linked directly from SKILL.md: {expected_link}")

    check_reference_budgets(errors, root)

    all_numbers: list[int] = []
    for path in sorted(reference_dir.glob("archetypes-*.md")):
        file_numbers = [
            int(value)
            for value in re.findall(
                r"^##\s+(\d+)\.", path.read_text(encoding="utf-8"), re.MULTILINE
            )
        ]
        all_numbers.extend(file_numbers)
        if not file_numbers or file_numbers != list(
            range(file_numbers[0], file_numbers[0] + len(file_numbers))
        ):
            errors.append(
                f"archetype catalog {path.relative_to(root).as_posix()} topics must be consecutively numbered in ascending order"
            )
    if sorted(all_numbers) != list(range(1, 29)):
        errors.append(
            "archetype catalogs must contain each numbered topic from 1 through 28 exactly once"
        )


def _is_excluded_markdown(rel: Path) -> bool:
    parts = rel.parts
    if not parts:
        return False
    if any(part in {".venv", ".codegraph"} for part in parts):
        return True
    if parts[0] == "analizler":
        return True
    if parts[:2] == ("evals", "artifacts"):
        return True
    if parts[0] == ".agents" and parts[:3] != (".agents", "skills", "system-design-compass"):
        return True
    return False


def check_markdown(
    errors: list[str],
    repo_root: Path | None = None,
) -> None:
    root = (repo_root if repo_root is not None else REPO_ROOT).resolve()
    markdown_files = [
        path
        for path in sorted(root.rglob("*.md"))
        if not _is_excluded_markdown(path.relative_to(root))
    ]
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
        try:
            parsed = _parse_yaml_mapping(metadata)
        except ValueError as exc:
            errors.append(f"agents/openai.yaml has invalid YAML: {exc}")
            parsed = {}

        def _has_dependencies(node: object) -> bool:
            if isinstance(node, dict):
                return "dependencies" in node or any(_has_dependencies(v) for v in node.values())
            return False

        if _has_dependencies(parsed):
            errors.append("agents/openai.yaml must not declare runtime dependencies")

        interface = parsed.get("interface")
        if not isinstance(interface, dict):
            errors.append("agents/openai.yaml must define an interface mapping")
        else:
            for field in ("display_name", "short_description", "default_prompt"):
                val = interface.get(field)
                if not isinstance(val, str) or not val.strip():
                    errors.append(f"agents/openai.yaml interface.{field} must be a non-empty string")
            default_prompt = interface.get("default_prompt", "")
            if isinstance(default_prompt, str) and "$system-design-compass" not in default_prompt:
                errors.append("agents/openai.yaml default prompt must name $system-design-compass")


def check_eval_json(
    errors: list[str],
    repo_root: Path | None = None,
) -> None:
    """Verify every JSON file under evals/ (excluding evals/artifacts/) parses cleanly."""
    root = (repo_root if repo_root is not None else REPO_ROOT).resolve()
    evals_dir = root / "evals"
    if not evals_dir.is_dir():
        return
    for path in sorted(evals_dir.rglob("*.json")):
        rel = path.relative_to(root)
        if rel.parts[:2] == ("evals", "artifacts"):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON in {rel.as_posix()}: {exc}")


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

    check_runtime_surface(errors, skill_root=mirror_root)

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
        if source_path.read_bytes() != mirror_path.read_bytes():
            errors.append(
                f"workspace mirror out of sync with skill source: {rel_path}"
            )

    for rel_path in sorted(set(mirror_files) - set(source_files)):
        errors.append(f"unexpected extra file in workspace mirror: {rel_path}")


def fix_workspace_mirror(
    skill_root: Path | None = None,
    workspace_skill_root: Path | None = None,
) -> int:
    """Copy allowed skill files to the workspace mirror with LF endings and remove extras."""
    source_root = skill_root if skill_root is not None else SKILL_ROOT
    mirror_root = (
        workspace_skill_root
        if workspace_skill_root is not None
        else WORKSPACE_SKILL_ROOT
    )
    allowed_suffixes = {".md", ".yaml", ".yml"}
    source_files = {
        path.relative_to(source_root).as_posix(): path
        for path in sorted(source_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed_suffixes
    }
    mirror_root.mkdir(parents=True, exist_ok=True)
    for rel_path, source_path in source_files.items():
        dest_path = mirror_root / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(source_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n"))

    for path in sorted(mirror_root.rglob("*"), reverse=True):
        if path.is_file():
            if path.relative_to(mirror_root).as_posix() not in source_files:
                path.unlink()
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass
    return len(source_files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix-mirror",
        action="store_true",
        help="Sync allowed skill files to .agents/skills/system-design-compass with LF endings before validating.",
    )
    args = parser.parse_args(argv)
    if args.fix_mirror:
        synced = fix_workspace_mirror()
        print(f"Synced {synced} files to {WORKSPACE_SKILL_ROOT.relative_to(REPO_ROOT).as_posix()}.")

    errors: list[str] = []
    check_required_files(errors)
    check_skill_entrypoint(errors)
    check_markdown(errors)
    check_runtime_surface(errors)
    check_eval_json(errors)
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
