# pylint: disable=misplaced-comparison-constant


def test_explicit(snapshot):
    value = "foo"
    assert value == snapshot("my_snapshot")

    value *= 2
    assert value != snapshot("my_snapshot")
    assert value[:3] == snapshot("my_snapshot")


def test_auto(snapshot):
    for i in range(3):
        assert str(i) == snapshot()
