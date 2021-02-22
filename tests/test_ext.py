from typing import Any

from pytest_insta import FmtBinary, FmtHexdump, FmtJson, FmtText


class FmtHtml(FmtText):
    extension = ".html"


def test_text(snapshot: Any):
    assert snapshot("foo.txt") == "Hello"
    assert snapshot("foo.html") == "<h1>Hello</h1>\n"
    assert snapshot("html") == "<h1>World</h1>\n"
    assert snapshot(".html") == "<h1>FooBar</h1>\n"


class FmtDat(FmtBinary):
    extension = ".dat"


def test_binary(snapshot: Any):
    assert snapshot("foo.bin") == bytes(range(256))
    assert snapshot("foo.dat") == bytes(range(256))
    assert snapshot(".dat") == bytes(range(256))
    assert snapshot("dat") == bytes(range(256))


class FmtDump(FmtHexdump):
    extension = ".dump"


def test_hexdump(snapshot: Any):
    assert snapshot("foo.hexdump") == bytes(range(256))
    assert snapshot("foo.dump") == bytes(range(256))
    assert snapshot(".dump") == bytes(range(256))
    assert snapshot("dump") == bytes(range(256))


class FmtExample(FmtJson):
    extension = ".example"


def test_json(snapshot: Any):
    assert snapshot("foo.json") == {"a": {"b": "c"}}
    assert snapshot("foo.example") == {"a": {"b": "c"}}
    assert snapshot(".example") == {"a": {"b": "c"}}
    assert snapshot("example") == {"a": {"b": "c"}}


class Fmt123(FmtText):
    extension = ".1.2.3"


def test_composite_ext(snapshot: Any):
    assert snapshot("foo.bar.0.1.2.3") == "hello"
    assert snapshot("foo.1.2.3") == "hello"
    assert snapshot(".1.2.3") == "hello"
    assert snapshot("1.2.3") == "hello"
