from typing import Any

import pytest

import pytest_insta.mark
from pytest_insta.config import SnapshotConfig


@pytest_insta.mark.config(config=SnapshotConfig(use_directories_for_snapshots=True))
def test_use_directories_for_snapshots(snapshot: Any):
    assert snapshot(".txt") == "simple_test"


@pytest_insta.mark.config(config=SnapshotConfig(use_directories_for_snapshots=True))
@pytest.mark.parametrize("case", ["test_case_1", "test_case_2"])
def test_use_directories_for_snapshots_with_cases(snapshot: Any, case: str):
    assert snapshot(".txt") == case


@pytest_insta.mark.config(config=SnapshotConfig(use_directories_for_snapshots=False))
@pytest.mark.parametrize("case", ["test_case_1", "test_case_2"])
def test_not_use_directories_for_snapshots(snapshot: Any, case: str):
    assert snapshot(".txt") == case
