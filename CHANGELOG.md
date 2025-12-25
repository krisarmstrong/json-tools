# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.3] - 2024-12-23

### Changed
- Standardized tooling configuration
- Version bump with tooling updates

## [2.0.2] - 2024-12-22

### Changed
- Version bump

## [2.0.1] - 2024-12-22

### Changed
- Version bump with configuration fixes

## [2.0.0] - 2024-12-21

### Added
- Unified CLI for all JSON/CSV/XML conversions
- Auto-format detection from file extensions
- Bidirectional conversions: CSV↔JSON, JSON↔XML, CSV↔XML
- JSON pretty-printing with configurable indentation
- JSON comparison with unified diff output
- Python library API (`json_tools.converters`, `json_tools.json_ops`)
- CI/CD workflow with automatic releases
- GitHub best practices infrastructure

### Changed
- Consolidated from multiple separate tools:
  - csv_to_json_converter
  - json_to_xml
  - json_toolkit
  - json_pretty_printer
  - json_comparator

## [1.0.0] - 2024-12-20

### Added
- Initial release with basic JSON operations
- CSV to JSON conversion
- JSON formatting

[Unreleased]: https://github.com/krisarmstrong/json-tools/compare/v2.0.3...HEAD
[2.0.3]: https://github.com/krisarmstrong/json-tools/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/krisarmstrong/json-tools/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/krisarmstrong/json-tools/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/krisarmstrong/json-tools/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/krisarmstrong/json-tools/releases/tag/v1.0.0
