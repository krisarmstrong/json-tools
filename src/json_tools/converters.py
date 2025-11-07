"""Conversion helpers shared by the ``json-tools`` CLI."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Iterable, Sequence

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, fromstring, tostring

__all__ = [
    "convert_csv_to_csv",
    "convert_csv_to_json",
    "convert_csv_to_xml",
    "convert_json_to_csv",
    "convert_json_to_json",
    "convert_json_to_xml",
    "convert_xml_to_csv",
    "convert_xml_to_json",
    "convert_xml_to_xml",
]


def convert_csv_to_json(input_path: Path, output_path: Path, delimiter: str, encoding: str) -> None:
    """Convert ``input_path`` CSV rows into a JSON array written to ``output_path``."""

    rows = _read_csv_rows(input_path, delimiter=delimiter, encoding=encoding)
    _write_json(output_path, rows, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_json_to_xml(input_path: Path, output_path: Path, encoding: str) -> None:
    """Convert a JSON document into XML."""

    json_data = _read_json(input_path, encoding=encoding)
    logging.debug("Converting JSON to XML for %s", input_path)
    xml_data = _dict_to_xml_string(json_data)
    output_path.write_text(xml_data, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_json_to_csv(input_path: Path, output_path: Path, delimiter: str, encoding: str) -> None:
    """Convert a JSON array (list of objects) into a CSV file."""

    json_data = _read_json(input_path, encoding=encoding)
    if not isinstance(json_data, list) or not all(isinstance(item, dict) for item in json_data):
        raise ValueError("Input JSON must be a list of objects for CSV conversion.")

    _write_csv(output_path, json_data, delimiter=delimiter, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_xml_to_json(input_path: Path, output_path: Path, encoding: str) -> None:
    """Convert an XML document into JSON."""

    logging.debug("Reading XML from %s", input_path)
    xml_payload = input_path.read_text(encoding=encoding)
    json_data = _xml_to_dict(xml_payload)
    _write_json(output_path, json_data, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_csv_to_xml(
    input_path: Path,
    output_path: Path,
    delimiter: str,
    encoding: str,
    *,
    root_element: str = "rows",
    row_element: str = "row",
) -> None:
    """Convert CSV rows into an XML document with configurable element names."""

    rows = _read_csv_rows(input_path, delimiter=delimiter, encoding=encoding)
    payload = {root_element: {row_element: rows}}
    xml_data = _dict_to_xml_string(payload)
    output_path.write_text(xml_data, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_xml_to_csv(
    input_path: Path,
    output_path: Path,
    delimiter: str,
    encoding: str,
    *,
    row_path: str | None = None,
) -> None:
    """Convert XML data into CSV.

    Args:
        input_path: XML file to read.
        output_path: Target CSV file.
        delimiter: CSV delimiter.
        encoding: Text encoding to use.
        row_path: Optional dotted path to the array of row objects inside the XML structure.
    """

    xml_payload = input_path.read_text(encoding=encoding)
    xml_data = _xml_to_dict(xml_payload)

    rows: Sequence[dict[str, Any]] | None
    if row_path:
        rows = _follow_row_path(xml_data, row_path)
    else:
        rows = _find_first_row_list(xml_data)

    if rows is None:
        raise ValueError(
            "Unable to locate a list of row objects inside the XML. "
            "Provide --row-element when invoking the CLI to point to the list."
        )

    normalized_rows = [_normalise_row(row) for row in rows]
    _write_csv(output_path, normalized_rows, delimiter=delimiter, encoding=encoding)
    logging.info("Converted %s to %s", input_path, output_path)


def convert_csv_to_csv(input_path: Path, output_path: Path, delimiter: str, encoding: str) -> None:
    """Copy a CSV file while allowing delimiter/encoding normalisation."""

    rows = _read_csv_rows(input_path, delimiter=delimiter, encoding=encoding)
    _write_csv(output_path, rows, delimiter=delimiter, encoding=encoding)
    logging.info("Copied %s to %s", input_path, output_path)


def convert_json_to_json(input_path: Path, output_path: Path, encoding: str) -> None:
    """Copy a JSON document verbatim (primarily for API symmetry)."""

    data = _read_json(input_path, encoding=encoding)
    _write_json(output_path, data, encoding=encoding)
    logging.info("Copied %s to %s", input_path, output_path)


def convert_xml_to_xml(input_path: Path, output_path: Path, encoding: str) -> None:
    """Copy an XML document verbatim (primarily for API symmetry)."""

    payload = input_path.read_text(encoding=encoding)
    output_path.write_text(payload, encoding=encoding)
    logging.info("Copied %s to %s", input_path, output_path)


def _read_csv_rows(input_path: Path, *, delimiter: str, encoding: str) -> list[dict[str, str]]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with input_path.open("r", newline="", encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        rows = list(reader)

    if not rows:
        logging.warning("CSV %s is empty.", input_path)
    return rows


def _write_csv(output_path: Path, rows: Sequence[dict[str, Any]], *, delimiter: str, encoding: str) -> None:
    fieldnames = _collect_fieldnames(rows)
    with output_path.open("w", newline="", encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _collect_fieldnames(rows: Sequence[dict[str, Any]]) -> list[str]:
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    return fieldnames


def _write_json(output_path: Path, payload: Any, *, encoding: str) -> None:
    with output_path.open("w", encoding=encoding) as jsonfile:
        json.dump(payload, jsonfile, indent=2)


def _read_json(input_path: Path, *, encoding: str) -> Any:
    if not input_path.is_file():
        raise FileNotFoundError(f"Input JSON not found: {input_path}")

    with input_path.open("r", encoding=encoding) as jsonfile:
        return json.load(jsonfile)


def _follow_row_path(data: Any, dotted_path: str) -> Sequence[dict[str, Any]] | None:
    current: Any = data
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = None
        if current is None:
            break

    if current is None:
        return None

    if isinstance(current, list):
        return _ensure_list_of_dicts(current)
    if isinstance(current, dict):
        return _ensure_list_of_dicts([current])
    return None


def _find_first_row_list(obj: Any) -> Sequence[dict[str, Any]] | None:
    if isinstance(obj, list):
        return _ensure_list_of_dicts(obj)
    if isinstance(obj, dict):
        for value in obj.values():
            rows = _find_first_row_list(value)
            if rows is not None:
                return rows
    return None


def _ensure_list_of_dicts(value: Iterable[Any]) -> list[dict[str, Any]] | None:
    rows: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            rows.append(item)
        else:
            return None
    return rows if rows else None


def _normalise_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _coerce_value(value) for key, value in row.items()}


def _coerce_value(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return str(value)


def _dict_to_xml_string(payload: dict[str, Any]) -> str:
    if len(payload) != 1:
        raise ValueError("XML conversion expects a single root element.")
    root_name, root_value = next(iter(payload.items()))
    root = Element(root_name)
    _populate_xml(root, root_value)
    raw = tostring(root, encoding="unicode")
    parsed = minidom.parseString(raw)
    return parsed.toprettyxml(indent="  ")


def _populate_xml(element: Element, value: Any) -> None:
    if isinstance(value, dict):
        for key, child_value in value.items():
            if isinstance(child_value, list):
                for item in child_value:
                    child = SubElement(element, str(key))
                    _populate_xml(child, item)
            else:
                child = SubElement(element, str(key))
                _populate_xml(child, child_value)
    elif isinstance(value, list):
        for item in value:
            child = SubElement(element, element.tag)
            _populate_xml(child, item)
    else:
        element.text = "" if value is None else str(value)


def _xml_to_dict(xml_payload: str) -> dict[str, Any]:
    root = fromstring(xml_payload)
    return {root.tag: _element_to_data(root)}


def _element_to_data(element: Element) -> Any:
    children = list(element)
    if not children:
        text = (element.text or "").strip()
        return text

    result: dict[str, Any] = {}
    for child in children:
        value = _element_to_data(child)
        if child.tag in result:
            existing = result[child.tag]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[child.tag] = [existing, value]
        else:
            result[child.tag] = value
    return result
