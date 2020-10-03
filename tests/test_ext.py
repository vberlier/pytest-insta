from pytest_insta import FmtBinary, FmtHexdump, FmtJson, FmtText


class FmtHtml(FmtText):
    extension = ".html"


def test_text(snapshot):
    assert snapshot("foo.txt") == "Hello"
    assert snapshot("foo.html") == "<h1>Hello</h1>\n"
    assert snapshot("html") == "<h1>World</h1>\n"
    assert snapshot(".html") == "<h1>FooBar</h1>\n"


class FmtDat(FmtBinary):
    extension = ".dat"


def test_binary(snapshot):
    assert snapshot("foo.bin") == bytes(range(256))
    assert snapshot("foo.dat") == bytes(range(256))
    assert snapshot(".dat") == bytes(range(256))
    assert snapshot("dat") == bytes(range(256))


class FmtDump(FmtHexdump):
    extension = ".dump"


def test_hexdump(snapshot):
    assert snapshot("foo.hexdump") == bytes(range(256))
    assert snapshot("foo.dump") == bytes(range(256))
    assert snapshot(".dump") == bytes(range(256))
    assert snapshot("dump") == bytes(range(256))


class FmtExample(FmtJson):
    extension = ".example"


def test_json(snapshot):
    assert snapshot("foo.json") == {"a": {"b": "c"}}
    assert snapshot("foo.example") == {"a": {"b": "c"}}
    assert snapshot(".example") == {"a": {"b": "c"}}
    assert snapshot("example") == {"a": {"b": "c"}}
