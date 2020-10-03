# pylint: disable=misplaced-comparison-constant


def test_text(snapshot):
    assert snapshot(ext=".html") == "<h1>Hello</h1>\n"


def test_binary(snapshot):
    assert snapshot(fmt="binary", ext=".dat") == bytes(range(256))


def test_hexdump(snapshot):
    assert snapshot(fmt="hexdump", ext=".dump") == bytes(range(256))


def test_json(snapshot):
    assert snapshot(fmt="json", ext=".example") == {"a": {"b": "c"}}
