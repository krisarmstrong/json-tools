# json-tools

`json-tools` is a single CLI/SDK for every JSON/CSV/XML workflow that used to be split
across `csv_to_json_converter`, `json_to_xml`, `json_toolkit`, `json_pretty_printer`,
and `json_comparator`. It ships one binary with pluggable subcommands so conversions,
diffs, and formatters all share the same logging, error handling, and tests.

## Features

- Convert between any combination of CSV, JSON, and XML (`csv↔json`, `json↔xml`, `csv↔xml`)
  with selectable delimiter/encoding plus XML root/row controls.
- Pretty-print JSON with configurable indentation.
- Pairwise JSON comparison with unified diffs written to stdout or a file.
- Drop-in Python helpers (`json_tools.converters` and `json_tools.json_ops`) for library use.

## Installation

```bash
pip install .
```

## CLI Usage

### Convert data (auto-detected formats)

```bash
json-tools -i data/devices.json -o export/devices.csv
```

`json-tools` infers formats from file extensions (`.json`, `.csv`, `.xml`, `.tsv`, `.ndjson`). Override with
`--from`/`--to` if the extensions are missing or ambiguous.

Use shortcut switches if you prefer explicit intent:

```
json-tools --csv-to-json -i data.csv  -o data.json
json-tools --json-to-csv -i data.json -o data.csv
json-tools --json-to-xml -i data.json -o data.xml
json-tools --xml-to-json -i data.xml  -o data.json
json-tools --csv-to-xml  -i data.csv  -o data.xml
json-tools --xml-to-csv  -i data.xml  -o data.csv
```

Every conversion also accepts:

- `-d / --delimiter` – CSV delimiter (default `,`)
- `-e / --encoding` – Text encoding (default `utf-8`)
- `--root-element` / `--row-element` – XML tag names when generating XML
- `--row-path` – Dotted path to the repeating element when converting XML → CSV (auto-detected otherwise)

Need an identity copy to normalize formatting? Set `--from`/`--to` (or extensions) to the same format (JSON→JSON, CSV→CSV, etc.).

### Pretty-print JSON

```bash
json-tools --pretty -i configs/raw.json -o configs/formatted.json --indent 4
```

### Compare JSON files

```bash
json-tools --compare configs/prod.json configs/staging.json --output diff.txt
```

Diffs are printed to stdout unless `--output` is supplied.

## Library API

```python
from pathlib import Path
from json_tools import converters, json_ops

converters.convert_csv_to_json(Path("in.csv"), Path("out.json"), ",", "utf-8")
json_ops.pretty_print_json(Path("raw.json"), Path("formatted.json"))
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m pytest
```

### Automated testing

Use the bundled Nox session (also used by CI):

```bash
pip install nox
nox -s tests
```

### Continuous Integration

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs `nox -s tests` on every push, PR, and tag so regressions are caught before release.

### Release & Versioning

Versions are derived from annotated git tags via `setuptools_scm`. To cut a release:

1. Ensure `main` is green in CI.
2. Create an annotated tag such as `git tag -a v2.1.0 -m "v2.1.0"`.
3. Push the tag (`git push origin v2.1.0`). The CI workflow runs automatically and downstream builds/installations will report the new version.

## License

MIT © Kris Armstrong
