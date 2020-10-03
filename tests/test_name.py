def test_explicit(snapshot):
    value = "foo"
    assert snapshot("my_snapshot") == value

    value *= 2
    assert snapshot("my_snapshot") != value
    assert snapshot("my_snapshot") * 2 == value


def test_auto(snapshot):
    for i in range(3):
        assert snapshot() == str(i)
