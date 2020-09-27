# pylint: disable=misplaced-comparison-constant


def test_text(snapshot):
    assert "<p>Hello</p>" == snapshot(ext=".html")


def test_binary(snapshot):
    assert bytes(range(256)) == snapshot(fmt="binary", ext=".dat")


def test_hexdump(snapshot):
    assert bytes(range(256)) == snapshot(fmt="hexdump", ext=".dump")


def test_json(snapshot):
    assert {"a": {"b": "c"}} == snapshot(fmt="json", ext=".example")
