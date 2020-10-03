from dataclasses import asdict, dataclass

import pytest


def test_text(snapshot):
    assert snapshot() == "hello"


def test_binary(snapshot):
    assert snapshot(fmt="binary") == bytes(range(256))


def test_hexdump(snapshot):
    assert snapshot(fmt="hexdump") == bytes(range(256))


def test_json(snapshot):
    assert snapshot(fmt="json") == {"foo": "bar"}


def test_pickle(snapshot):
    assert snapshot(fmt="pickle") == {"hello": "world"}


@dataclass
class Point:
    x: int
    y: int


def test_json_dataclass(snapshot):
    assert snapshot(fmt="json") == asdict(Point(4, 5))


def test_pickle_dataclass(snapshot):
    assert snapshot(fmt="pickle") == Point(4, 5)


def test_invalid_format(snapshot):
    with pytest.raises(ValueError, match="invalid snapshot format"):
        snapshot(fmt="something")
