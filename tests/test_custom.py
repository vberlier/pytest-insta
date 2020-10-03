from pathlib import Path
from typing import NamedTuple

from pytest_insta import Fmt


class Point(NamedTuple):
    x: int
    y: int


class FmtPoint(Fmt[Point]):
    extension = ".pt"

    def load(self, path: Path) -> Point:
        return Point(*map(int, path.read_text().split()))

    def dump(self, path: Path, value: Point):
        path.write_text(f"{value.x} {value.y}")


def test_point(snapshot):
    assert snapshot("pt") == Point(4, 2)
    assert snapshot(".pt") == Point(4, 5)
