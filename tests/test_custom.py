from pathlib import Path
from typing import NamedTuple

from pytest_insta import ForwardedArgs, Snapshot


class Point(NamedTuple):
    x: int
    y: int


class SnapshotPoint(Snapshot, Point, fmt="point"):
    extension = ".pt"

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        return tuple(map(int, path.read_text().split())), {}

    @classmethod
    def update_value(cls, value: Point, path: Path):
        path.write_text(f"{value.x} {value.y}")


def test_point(snapshot):
    assert Point(4, 2) == snapshot(fmt="point")
