from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "plugins/strato/skills/strato-verification-sync"
)
SPEC = importlib.util.spec_from_file_location(
    "verification_validator", ROOT / "scripts/validate_verification.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


@pytest.fixture
def artifacts(tmp_path: Path) -> tuple[Path, Path]:
    mapping = tmp_path / "mapping.json"
    results = tmp_path / "results.json"
    mapping.write_bytes((ROOT / "assets/test-mapping.example.json").read_bytes())
    results.write_bytes((ROOT / "assets/test-results.example.json").read_bytes())
    return mapping, results


def _change(path: Path, mutate: Any) -> None:
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data))


def test_examples_bind_results_to_exact_mapping(artifacts: tuple[Path, Path]) -> None:
    VALIDATOR.validate(*artifacts)


@pytest.mark.parametrize(
    "field,value",
    [
        ("test_case_revision", 99),
        ("step_id", "unknown-step"),
        ("test_selector", "renamed-test"),
    ],
)
def test_stale_or_unmapped_results_are_rejected(
    artifacts: tuple[Path, Path], field: str, value: object
) -> None:
    _change(artifacts[1], lambda data: data["results"][0].update({field: value}))
    with pytest.raises(ValueError, match="unmapped"):
        VALIDATOR.validate(*artifacts)


@pytest.mark.parametrize(
    "field,value",
    [("product_slug", "other-product"), ("tenant_origin", "https://other.example")],
)
def test_product_identity_must_match(
    artifacts: tuple[Path, Path], field: str, value: str
) -> None:
    _change(artifacts[1], lambda data: data["strato"].update({field: value}))
    with pytest.raises(ValueError, match="strato"):
        VALIDATOR.validate(*artifacts)


def test_changed_mapping_bytes_require_new_hash(artifacts: tuple[Path, Path]) -> None:
    artifacts[0].write_bytes(artifacts[0].read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash"):
        VALIDATOR.validate(*artifacts)


@pytest.mark.parametrize("duplicate", ["case", "step"])
def test_duplicate_mapping_is_rejected(
    artifacts: tuple[Path, Path], duplicate: str
) -> None:
    def change(data: dict[str, Any]) -> None:
        entries = data["cases"] if duplicate == "case" else data["cases"][0]["steps"]
        entries.append(copy.deepcopy(entries[0]))

    _change(artifacts[0], change)
    with pytest.raises(ValueError, match="Duplicate"):
        VALIDATOR.validate(artifacts[0])


def test_missing_step_id_is_rejected(artifacts: tuple[Path, Path]) -> None:
    _change(artifacts[0], lambda data: data["cases"][0]["steps"][0].pop("step_id"))
    with pytest.raises(jsonschema.ValidationError):
        VALIDATOR.validate(artifacts[0])


@pytest.mark.parametrize(
    "outcome", ["passed", "failed", "errored", "skipped", "not_run", "unknown"]
)
def test_native_outcomes_are_preserved(
    artifacts: tuple[Path, Path], outcome: str
) -> None:
    _change(
        artifacts[1],
        lambda data: data["results"][0].update(outcome=outcome, native_outcome=outcome),
    )
    VALIDATOR.validate(*artifacts)


def test_pass_requires_observed_native_outcome(artifacts: tuple[Path, Path]) -> None:
    _change(artifacts[1], lambda data: data["results"][0].update(native_outcome=None))
    with pytest.raises(jsonschema.ValidationError):
        VALIDATOR.validate(*artifacts)


def test_parameter_instances_and_retries_remain_separate(
    artifacts: tuple[Path, Path],
) -> None:
    def change(data: dict[str, Any]) -> None:
        first = data["results"][0]
        first.update(outcome="failed", native_outcome="failed")
        retry = {**first, "attempt": 2, "outcome": "passed", "native_outcome": "passed"}
        parameter = {
            **retry,
            "execution_id": "test_limit[high]",
            "parameters": {"limit": "high"},
            "attempt": 1,
        }
        data["results"].extend([retry, parameter])

    _change(artifacts[1], change)
    VALIDATOR.validate(*artifacts)


def test_duplicate_attempt_is_rejected(artifacts: tuple[Path, Path]) -> None:
    _change(
        artifacts[1],
        lambda data: data["results"].append(copy.deepcopy(data["results"][0])),
    )
    with pytest.raises(ValueError, match="Duplicate execution"):
        VALIDATOR.validate(*artifacts)


def test_incomplete_collection_requires_explanation(
    artifacts: tuple[Path, Path],
) -> None:
    _change(
        artifacts[1],
        lambda data: data.update(
            results=[], collection={"status": "unavailable", "notes": []}
        ),
    )
    with pytest.raises(ValueError, match="missing evidence"):
        VALIDATOR.validate(*artifacts)
    _change(
        artifacts[1],
        lambda data: data["collection"].update(
            notes=["Runner terminated before report creation"]
        ),
    )
    VALIDATOR.validate(*artifacts)


def test_case_revision_change_requires_corresponding_result_change(
    artifacts: tuple[Path, Path],
) -> None:
    _change(artifacts[0], lambda data: data["cases"][0].update(test_case_revision=4))
    _change(
        artifacts[1],
        lambda data: data.update(
            mapping_sha256=hashlib.sha256(artifacts[0].read_bytes()).hexdigest()
        ),
    )
    with pytest.raises(ValueError, match="stale case revision"):
        VALIDATOR.validate(*artifacts)
