__all__ = ["Fmt", "FmtText", "FmtBinary", "FmtHexdump", "FmtJson", "FmtPickle"]


import json
import pickle
from itertools import accumulate
from pathlib import Path
from typing import Any, ClassVar, Dict, Generic, Optional, Tuple, Type, TypeVar

from .utils import hexdump, hexload

T = TypeVar("T")


class Fmt(Generic[T]):
    extension: ClassVar[str] = ""
    registry: ClassVar[Dict[str, Type["Fmt[Any]"]]] = {}

    def __init_subclass__(cls):
        if cls.extension:
            cls.registry[cls.extension] = cls

    @classmethod
    def from_spec(cls, spec: str) -> Tuple[Optional[str], Optional["Fmt[Any]"]]:
        for name, key in [
            (None, spec),
            (None, f".{spec}"),
            *reversed(
                [
                    (spec, suffix)
                    for suffix in accumulate(
                        reversed(Path(spec).suffixes), lambda a, b: b + a, initial=""
                    )
                ]
            ),
        ]:
            if format_cls := cls.registry.get(key):
                return name, format_cls()
        return None, None

    def load(self, path: Path) -> T:
        raise NotImplementedError()

    def dump(self, path: Path, value: T) -> None:
        raise NotImplementedError()


class FmtText(Fmt[str]):
    extension = ".txt"

    def load(self, path: Path) -> str:
        return path.read_text()

    def dump(self, path: Path, value: str):
        path.write_text(value)


class FmtBinary(Fmt[bytes]):
    extension = ".bin"

    def load(self, path: Path) -> bytes:
        return path.read_bytes()

    def dump(self, path: Path, value: bytes):
        path.write_bytes(value)


class FmtHexdump(Fmt[bytes]):
    extension = ".hexdump"

    def load(self, path: Path) -> bytes:
        return hexload(path.read_text())

    def dump(self, path: Path, value: bytes):
        path.write_text("\n".join(hexdump(value)) + "\n")


class FmtJson(Fmt[Any]):
    extension = ".json"

    def load(self, path: Path) -> Any:
        return json.loads(path.read_text())

    def dump(self, path: Path, value: Any):
        path.write_text(json.dumps(value, indent=2) + "\n")


class FmtPickle(Fmt[Any]):
    extension = ".pickle"

    def load(self, path: Path) -> Any:
        return pickle.loads(path.read_bytes())

    def dump(self, path: Path, value: Any):
        path.write_bytes(pickle.dumps(value))
