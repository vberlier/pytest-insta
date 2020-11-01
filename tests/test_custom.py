from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from pytest_insta import Fmt


@dataclass
class Point:
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


class FmtTextPair(Fmt[Tuple[str, str]]):
    extension = ".textpair"

    def load(self, path: Path) -> Tuple[str, str]:
        return (path / "left.txt").read_text(), (path / "right.txt").read_text()

    def dump(self, path: Path, value: Tuple[str, str]):
        path.mkdir(exist_ok=True)
        (path / "left.txt").write_text(value[0])
        (path / "right.txt").write_text(value[1])


def test_text_dir(snapshot):
    assert snapshot("textpair") == ("hello", "world")
