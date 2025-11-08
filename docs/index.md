# JSON Tools Documentation

Command-line utilities for JSON file manipulation and analysis.

## Quick Links

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [API Reference](api.md)
- [Contributing](../CONTRIBUTING.md)

## Overview

JSON Tools provides a comprehensive suite of utilities for working with JSON files:

- Validation and formatting
- Schema verification
- Conversion utilities
- Query and filtering
- Diff and merge operations

## Features

- **Fast JSON validation** with detailed error reporting
- **Pretty printing** and formatting
- **Schema validation** support
- **Path-based queries** (JSONPath)
- **Diff** between JSON files
- **Merge** multiple JSON files
- **Conversion** to/from various formats

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Validate JSON file
json-tools validate file.json

# Pretty print
json-tools format file.json --indent 2

# Query with JSONPath
json-tools query file.json "$.users[*].name"

# Diff two files
json-tools diff file1.json file2.json
```

## Testing

```bash
pytest tests/ -v
```

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Author

Kris Armstrong
