"""CLI entry point for the json-tools package."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable

from . import converters, json_ops

FormatPair = tuple[str, str]
FORMATS = ("csv", "json", "xml")
EXTENSION_MAP = {
    ".csv": "csv",
    ".tsv": "csv",
    ".json": "json",
    ".ndjson": "json",
    ".xml": "xml",
}
SHORTCUT_FLAGS = {
    "csv_to_json": ("csv", "json"),
    "json_to_csv": ("json", "csv"),
    "json_to_xml": ("json", "xml"),
    "xml_to_json": ("xml", "json"),
    "csv_to_xml": ("csv", "xml"),
    "xml_to_csv": ("xml", "csv"),
}


def setup_logging(verbose: bool, logfile: Path | None = None) -> None:
    """Initialise logging to stdout and optional file."""

    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(
        level=level, format="%(asctime)s [%(levelname)s] %(message)s", handlers=handlers
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Swiss‑army knife for JSON/CSV/XML files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument("-l", "--logfile", type=Path, help="Optional log file.")

    parser.add_argument(
        "-i", "--input", type=Path, help="Input file (required for convert/--pretty)."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (required for convert/--pretty, optional for --compare).",
    )
    parser.add_argument(
        "--from",
        dest="source_format",
        choices=FORMATS,
        help="Source format (auto-detected if omitted).",
    )
    parser.add_argument(
        "--to",
        dest="target_format",
        choices=FORMATS,
        help="Target format (auto-detected if omitted).",
    )
    parser.add_argument("-d", "--delimiter", default=",", help="CSV delimiter (where applicable).")
    parser.add_argument("-e", "--encoding", default="utf-8", help="Text encoding for all file IO.")
    parser.add_argument(
        "--root-element",
        default="rows",
        help="Root element name when generating XML from CSV.",
    )
    parser.add_argument(
        "--row-element",
        default="row",
        help="Repeated element name when generating XML from CSV.",
    )
    parser.add_argument(
        "--row-path",
        help="Dotted path to the repeating element when converting XML to CSV (auto-detected if omitted).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON input to output.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for --pretty (default: 2).",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        type=Path,
        help="Compare two or more JSON files and output a diff (stdout by default).",
    )

    shortcuts = parser.add_argument_group("conversion shortcuts")
    for flag, (src, dst) in SHORTCUT_FLAGS.items():
        shortcuts.add_argument(
            f"--{flag.replace('_', '-')}",
            action="store_true",
            help=f"Shortcut for --from {src} --to {dst}.",
        )

    return parser


def main() -> int:  # pragma: no cover - exercised via CLI tests
    """CLI entry point returning process exit code."""

    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose, args.logfile)

    try:
        _validate_mode(args)
        if args.compare:
            diffs = json_ops.compare_json_files(args.compare)
            _emit_diffs(diffs, args.output)
        elif args.pretty:
            _require_path(args.input, "--input/-i is required when using --pretty.")
            _require_path(args.output, "--output/-o is required when using --pretty.")
            json_ops.pretty_print_json(args.input, args.output, indent=args.indent)
        else:
            _apply_shortcuts(args)
            _require_path(args.input, "--input/-i is required when converting files.")
            _require_path(args.output, "--output/-o is required when converting files.")
            _handle_convert(args)
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user.")
        return 0
    except Exception as exc:
        logging.critical("Error: %s", exc)
        return 1
    return 0


def _handle_convert(args: argparse.Namespace) -> None:
    source_format = args.source_format or _infer_format(args.input)
    target_format = args.target_format or _infer_format(args.output, allow_missing=True)

    if not source_format:
        raise ValueError(
            "Unable to infer input format. Please use --from to specify it explicitly."
        )
    if not target_format:
        raise ValueError("Unable to infer output format. Please use --to to specify it explicitly.")

    pair: FormatPair = (source_format, target_format)
    handler = _CONVERSION_HANDLERS.get(pair)
    if handler is None:
        raise ValueError(f"Unsupported conversion from {source_format} to {target_format}.")
    handler(args)


def _emit_diffs(diffs: list[str], destination: Path | None) -> None:
    if destination:
        destination.write_text("\n".join(diffs) + "\n", encoding="utf-8")
        logging.info("Diff written to %s", destination)
    else:
        for line in diffs:
            print(line)


def _conversion_handler(
    func: Callable[[argparse.Namespace], None],
) -> Callable[[argparse.Namespace], None]:
    return func


_CONVERSION_HANDLERS: dict[FormatPair, Callable[[argparse.Namespace], None]] = {
    ("csv", "json"): _conversion_handler(
        lambda args: converters.convert_csv_to_json(
            args.input, args.output, args.delimiter, args.encoding
        )
    ),
    ("csv", "xml"): _conversion_handler(
        lambda args: converters.convert_csv_to_xml(
            args.input,
            args.output,
            args.delimiter,
            args.encoding,
            root_element=args.root_element,
            row_element=args.row_element,
        )
    ),
    ("csv", "csv"): _conversion_handler(
        lambda args: converters.convert_csv_to_csv(
            args.input, args.output, args.delimiter, args.encoding
        )
    ),
    ("json", "csv"): _conversion_handler(
        lambda args: converters.convert_json_to_csv(
            args.input, args.output, args.delimiter, args.encoding
        )
    ),
    ("json", "xml"): _conversion_handler(
        lambda args: converters.convert_json_to_xml(args.input, args.output, args.encoding)
    ),
    ("json", "json"): _conversion_handler(
        lambda args: converters.convert_json_to_json(args.input, args.output, args.encoding)
    ),
    ("xml", "json"): _conversion_handler(
        lambda args: converters.convert_xml_to_json(args.input, args.output, args.encoding)
    ),
    ("xml", "csv"): _conversion_handler(
        lambda args: converters.convert_xml_to_csv(
            args.input,
            args.output,
            args.delimiter,
            args.encoding,
            row_path=args.row_path,
        )
    ),
    ("xml", "xml"): _conversion_handler(
        lambda args: converters.convert_xml_to_xml(args.input, args.output, args.encoding)
    ),
}


def _infer_format(path: Path, *, allow_missing: bool = False) -> str | None:
    fmt = EXTENSION_MAP.get(path.suffix.lower())
    if fmt is None and not allow_missing:
        return None
    return fmt


def _apply_shortcuts(args: argparse.Namespace) -> None:
    active = [flag for flag in SHORTCUT_FLAGS if getattr(args, flag, False)]
    if len(active) > 1:
        raise ValueError("Please specify only one conversion shortcut option at a time.")
    if active:
        src, dst = SHORTCUT_FLAGS[active[0]]
        args.source_format = src
        args.target_format = dst


def _require_path(path: Path | None, message: str) -> None:
    if path is None:
        raise ValueError(message)


def _validate_mode(args: argparse.Namespace) -> None:
    modes_selected = sum(
        1
        for flag in (
            bool(args.compare),
            bool(args.pretty),
        )
        if flag
    )
    if modes_selected > 1:
        raise ValueError("Choose only one mode at a time (convert, --pretty, or --compare).")


if __name__ == "__main__":
    sys.exit(main())
