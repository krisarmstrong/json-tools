"""Tests for the json-tools converters and JSON helpers."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from json_tools import converters, json_ops
from json_tools import __main__ as cli
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring


class JsonToolsTestCase(unittest.TestCase):
    """Integration tests covering conversions and JSON helpers."""

    def setUp(self):
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)

        self.csv_file = self.test_dir / "people.csv"
        with self.csv_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["name", "age"])
            writer.writerow(["Alice", "30"])
            writer.writerow(["Bob", "25"])

        self.json_list_file = self.test_dir / "people.json"
        with self.json_list_file.open("w", encoding="utf-8") as handle:
            json.dump([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], handle)

        self.json_nested_file = self.test_dir / "nested.json"
        with self.json_nested_file.open("w", encoding="utf-8") as handle:
            json.dump(
                {"rows": {"row": [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]}},
                handle,
            )

        self.xml_file = self.test_dir / "people.xml"
        self.xml_file.write_text(
            "<rows><row><name>Alice</name><age>30</age></row><row><name>Bob</name><age>25</age></row></rows>",
            encoding="utf-8",
        )

    def tearDown(self):
        for file in self.test_dir.glob("*"):
            file.unlink()
        self.test_dir.rmdir()

    def test_convert_csv_to_json(self):
        target = self.test_dir / "people_from_csv.json"
        converters.convert_csv_to_json(self.csv_file, target, ",", "utf-8")
        self.assertTrue(target.exists())
        with target.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(data, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])

    def test_convert_json_to_csv(self):
        target = self.test_dir / "people_from_json.csv"
        converters.convert_json_to_csv(self.json_list_file, target, ",", "utf-8")
        with target.open("r", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["name", "age"])
        self.assertEqual(rows[1:], [["Alice", "30"], ["Bob", "25"]])

    def test_convert_json_to_xml(self):
        target = self.test_dir / "from_json.xml"
        converters.convert_json_to_xml(self.json_nested_file, target, "utf-8")
        parsed = fromstring(target.read_text(encoding="utf-8"))
        self.assertEqual(parsed.tag, "rows")

    def test_convert_xml_to_json(self):
        target = self.test_dir / "from_xml.json"
        converters.convert_xml_to_json(self.xml_file, target, "utf-8")
        payload = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(payload["rows"]["row"][0]["name"], "Alice")

    def test_convert_csv_to_xml_and_back(self):
        xml_target = self.test_dir / "roundtrip.xml"
        csv_target = self.test_dir / "roundtrip.csv"

        converters.convert_csv_to_xml(
            self.csv_file,
            xml_target,
            ",",
            "utf-8",
            root_element="people",
            row_element="person",
        )
        parsed = fromstring(xml_target.read_text(encoding="utf-8"))
        self.assertEqual(parsed.tag, "people")
        self.assertEqual(len(list(parsed)), 2)

        converters.convert_xml_to_csv(
            xml_target, csv_target, ",", "utf-8", row_path="people.person"
        )
        with csv_target.open("r", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["name", "age"])
        self.assertEqual(rows[1], ["Alice", "30"])

    def test_pretty_print_json(self):
        messy = self.test_dir / "messy.json"
        messy.write_text('{"z":1,"a":{"nested":true}}', encoding="utf-8")
        target = self.test_dir / "pretty.json"

        json_ops.pretty_print_json(messy, target, indent=4)
        content = target.read_text(encoding="utf-8").splitlines()
        self.assertTrue(content[1].startswith("    "))

    def test_compare_json_files(self):
        other = self.test_dir / "other.json"
        other.write_text('[{"name": "Alice"}]', encoding="utf-8")
        diffs = json_ops.compare_json_files([self.json_list_file, other])
        self.assertTrue(diffs)
        self.assertTrue(any(line.startswith("@@") for line in diffs))

    def test_infer_format_from_extension(self):
        path = self.test_dir / "data.JSON"
        path.write_text("{}", encoding="utf-8")
        self.assertEqual(cli._infer_format(path), "json")

    def test_handle_convert_with_auto_detection(self):
        target = self.test_dir / "auto.csv"
        args = SimpleNamespace(
            input=self.json_list_file,
            output=target,
            delimiter=",",
            encoding="utf-8",
            root_element="rows",
            row_element="row",
            row_path=None,
            source_format=None,
            target_format=None,
        )
        cli._handle_convert(args)
        with target.open("r", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["name", "age"])

    def test_apply_shortcuts_sets_formats(self):
        args = SimpleNamespace(
            csv_to_json=True,
            json_to_csv=False,
            json_to_xml=False,
            xml_to_json=False,
            csv_to_xml=False,
            xml_to_csv=False,
            source_format=None,
            target_format=None,
        )
        cli._apply_shortcuts(args)
        self.assertEqual(args.source_format, "csv")
        self.assertEqual(args.target_format, "json")

    def test_validate_mode_rejects_multiple_flags(self):
        args = SimpleNamespace(compare=[Path("a.json"), Path("b.json")], pretty=True)
        with self.assertRaises(ValueError):
            cli._validate_mode(args)


if __name__ == "__main__":
    unittest.main()
