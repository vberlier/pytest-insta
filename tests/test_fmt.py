from dataclasses import asdict, dataclass

import pytest


def test_text(snapshot):
    assert snapshot() == "hello"
    assert snapshot("txt") == "hello"
    assert snapshot(".txt") == "hello"


def test_binary(snapshot):
    assert snapshot("bin") == bytes(range(256))
    assert snapshot(".bin") == bytes(range(256))


def test_hexdump(snapshot):
    assert snapshot("hexdump") == bytes(range(256))
    assert snapshot(".hexdump") == bytes(range(256))


def test_json(snapshot):
    assert snapshot("json") == {"foo": "yeah"}
    assert snapshot(".json") == {"foo": "yeah"}


def test_pickle(snapshot):
    assert snapshot("pickle") == {"hello": "world"}
    assert snapshot(".pickle") == {"hello": "world"}


@dataclass
class Point:
    x: int
    y: int


def test_json_dataclass(snapshot):
    assert snapshot("json") == asdict(Point(4, 5))
    assert snapshot(".json") == asdict(Point(4, 5))


def test_pickle_dataclass(snapshot):
    assert snapshot("pickle") == Point(4, 5)
    assert snapshot(".pickle") == Point(4, 5)


@pytest.mark.parametrize("spec", ["something", ".something", "foo.something"])
def test_invalid_format(snapshot, spec):
    with pytest.raises(ValueError, match="invalid snapshot format"):
        snapshot(spec)
