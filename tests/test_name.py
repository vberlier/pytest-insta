from typing import Any


def test_explicit(snapshot: Any):
    value = "foo"
    assert snapshot("my_snapshot.txt") == value
    assert snapshot("my_snapshot.txt") != value * 2


def test_explicit_json(snapshot: Any):
    value = ["foo"]
    assert snapshot("my_snapshot.json") == value
    assert snapshot("my_snapshot.json") != value * 2


def test_auto(snapshot: Any):
    for i in range(3):
        assert snapshot() == str(i)


def test_auto_json(snapshot: Any):
    for i in range(3):
        assert snapshot("json") == i
