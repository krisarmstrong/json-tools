"""JSON-specific operations such as formatting and comparisons."""

from __future__ import annotations

import difflib
import json
import logging
from pathlib import Path
from typing import Sequence

__all__ = [
    "compare_json_files",
    "pretty_print_json",
]


def pretty_print_json(input_path: Path, output_path: Path, indent: int = 2) -> None:
    """Format ``input_path`` with consistent indentation and write to ``output_path``."""

    payload = _read_json(input_path)
    with output_path.open("w", encoding="utf-8") as destination:
        json.dump(payload, destination, indent=indent, ensure_ascii=False)
        destination.write("\n")
    logging.info("Formatted %s -> %s", input_path, output_path)


def compare_json_files(file_paths: Sequence[Path]) -> list[str]:
    """Compare JSON files pairwise and return human readable diffs."""

    if len(file_paths) < 2:
        raise ValueError("At least two files are required to run a comparison.")

    payloads = [_read_json(path) for path in file_paths]
    rendered = [json.dumps(payload, indent=2, sort_keys=True).splitlines() for payload in payloads]

    diffs: list[str] = []
    for index in range(len(rendered) - 1):
        file_a = file_paths[index]
        file_b = file_paths[index + 1]
        logging.info("Comparing %s <-> %s", file_a, file_b)
        diff_lines = list(
            difflib.unified_diff(
                rendered[index], rendered[index + 1], fromfile=str(file_a), tofile=str(file_b)
            )
        )
        if diff_lines:
            diffs.extend(diff_lines)
        else:
            diffs.append(f"No differences detected between {file_a} and {file_b}.")
    return diffs


def _read_json(path: Path) -> dict | list:
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as source:
        return json.load(source)
