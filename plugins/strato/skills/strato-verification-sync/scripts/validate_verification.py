# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.23,<5", "typer>=0.12,<1"]
# ///
"""Validate Strato automation mappings and optional result artifacts without running tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import typer

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def _read_validated(path: Path, schema_name: str) -> dict[str, Any]:
    value = json.loads(path.read_text())
    schema = json.loads((ASSETS / schema_name).read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(value)
    return value


def validate(mapping_path: Path, results_path: Path | None = None) -> None:
    mapping = _read_validated(mapping_path, "test-mapping.schema.json")
    suites: set[tuple[str, str]] = set()
    cases: set[str] = set()
    selectors: set[tuple[str, str]] = set()
    steps: dict[tuple[str, int, str], tuple[str, str, str]] = {}
    for case in mapping["cases"]:
        suite = (case["framework"], case["suite_selector"])
        if suite in suites or case["test_case_id"] in cases:
            raise ValueError("Duplicate suite or competing mappings for one Test Case")
        suites.add(suite)
        cases.add(case["test_case_id"])
        source_path = Path(case["source_path"])
        if source_path.is_absolute() or ".." in source_path.parts:
            raise ValueError("Source paths must stay within the repository")
        for step in case["steps"]:
            key = (case["test_case_id"], case["test_case_revision"], step["step_id"])
            selector = (case["framework"], step["selector"])
            if key in steps or selector in selectors:
                raise ValueError("Duplicate step identity or automated test selector")
            selectors.add(selector)
            steps[key] = (*suite, step["selector"])
    if results_path is None:
        return
    results = _read_validated(results_path, "test-results.schema.json")
    for field in ("mapping_revision", "strato", "repository"):
        if results[field] != mapping[field]:
            raise ValueError(f"Result {field} does not match the mapping")
    if (
        results["mapping_sha256"]
        != hashlib.sha256(mapping_path.read_bytes()).hexdigest()
    ):
        raise ValueError("Result mapping hash does not match the exact mapping bytes")
    executions: set[tuple[str, str, int]] = set()
    for result in results["results"]:
        key = (result["test_case_id"], result["test_case_revision"], result["step_id"])
        if steps.get(key) != (
            result["framework"],
            result["suite_selector"],
            result["test_selector"],
        ):
            raise ValueError(
                "Result references an unmapped test, stale case revision, or unknown step"
            )
        execution = (result["framework"], result["execution_id"], result["attempt"])
        if execution in executions:
            raise ValueError("Duplicate execution and attempt")
        executions.add(execution)
    if (
        results["collection"]["status"] != "complete"
        and not results["collection"]["notes"]
    ):
        raise ValueError("Incomplete collection must explain the missing evidence")


def main(mapping: Path, results: Path | None = None) -> None:
    """Validate MAPPING and optionally --results PATH; never execute test code."""
    try:
        validate(mapping, results)
    except (
        OSError,
        ValueError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
    ) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    typer.echo(
        "Mapping and supplied result contract are valid; execution coverage and Strato acceptance are not asserted."
    )


if __name__ == "__main__":
    typer.run(main)
