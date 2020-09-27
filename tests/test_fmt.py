from contextlib import nullcontext
from dataclasses import asdict, dataclass
from typing import ContextManager

import pytest

from pytest_insta import Snapshot

# pylint: disable=misplaced-comparison-constant


def test_text(snapshot):
    assert "hello" == snapshot()


def test_binary(snapshot):
    assert bytes(range(256)) == snapshot(fmt="binary")


def test_hexdump(snapshot):
    assert bytes(range(256)) == snapshot(fmt="hexdump")


def test_json(snapshot):
    assert {"foo": "bar"} == snapshot(fmt="json")


@dataclass
class Point:
    x: int
    y: int


def test_json_dataclass(snapshot):
    assert asdict(Point(4, 2)) == snapshot(fmt="json")


def test_invalid_format(snapshot):
    with pytest.raises(ValueError, match="invalid snapshot format"):
        snapshot(fmt="something")


@pytest.mark.parametrize("fmt", list(Snapshot.registry))
@pytest.mark.parametrize(
    "value",
    ["hello", bytes(range(256)), {"a": {"b": 42}}],
    ids=[None, "bytes", None],
)
def test_incompatible_format(snapshot, fmt, value):
    expectation: ContextManager = pytest.raises(TypeError, match="expected instance of")

    if isinstance(value, Snapshot.registry[fmt].BaseType):
        expectation = nullcontext()

    with expectation:
        assert value == snapshot(fmt=fmt)
