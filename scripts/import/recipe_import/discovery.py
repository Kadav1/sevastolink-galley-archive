from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from .models import FileSelection, ImporterFailure


def is_recipe_source_file(path: Path) -> bool:
    lowered_name = path.name.lower()
    if lowered_name in {"readme.md", "readme.txt"}:
        return False
    if lowered_name.startswith("."):
        return False
    if any(part.startswith(".") or part.startswith("_") for part in path.parts):
        return False
    return True


def iter_recipe_files(input_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("**/*.txt", "**/*.md"):
        files.extend(input_dir.glob(pattern))
    return sorted(path for path in files if path.is_file() and is_recipe_source_file(path))


def _normalize_explicit_files(paths: list[Path]) -> list[Path]:
    normalized: list[Path] = []
    seen: set[Path] = set()
    for source_path in paths:
        resolved = source_path.resolve()
        if not source_path.exists() or not source_path.is_file():
            raise ImporterFailure("discover", f"Input file does not exist or is not a file: {source_path}")
        if not is_recipe_source_file(source_path):
            raise ImporterFailure("discover", f"Input file is not treated as a recipe source: {source_path}")
        if resolved in seen:
            continue
        seen.add(resolved)
        normalized.append(source_path)
    return normalized


def resolve_file_selection(args: Namespace) -> FileSelection:
    explicit_files: list[Path] = args.input_files or []
    normalized_explicit = _normalize_explicit_files(explicit_files)

    discovered: list[Path] = []
    if args.input_dir is not None:
        input_dir = args.input_dir
        if not input_dir.exists() or not input_dir.is_dir():
            raise ImporterFailure("discover", f"Input directory does not exist or is not a directory: {input_dir}")
        input_dir_resolved = input_dir.resolve()
        for source_path in normalized_explicit:
            try:
                source_path.resolve().relative_to(input_dir_resolved)
            except ValueError as exc:
                raise ImporterFailure(
                    "discover",
                    f"Explicit file is outside input directory and cannot be combined in the same run: {source_path}",
                ) from exc
        discovered = iter_recipe_files(input_dir)
        if not discovered:
            raise ImporterFailure("discover", f"No .txt or .md files found in {input_dir}")
    else:
        input_dir = None

    ordered: list[Path] = []
    seen: set[Path] = set()
    for source_path in [*normalized_explicit, *discovered]:
        resolved = source_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(source_path)

    if not ordered:
        raise ImporterFailure("discover", "Provide an input directory and/or one or more --file arguments.")

    return FileSelection(source_paths=ordered, input_dir=input_dir)
