__all__ = ["Fmt", "FmtText", "FmtBinary", "FmtHexdump", "FmtJson", "FmtPickle"]


import json
import pickle
from pathlib import Path
from typing import Any, ClassVar, Dict, Generic, Type, TypeVar

from .utils import hexdump, hexload

T = TypeVar("T")


class Fmt(Generic[T]):
    registry: ClassVar[Dict[str, Type["Fmt"]]] = {}
    extension: ClassVar[str] = ""

    def __init_subclass__(cls, name: str = None):
        if name:
            cls.registry[name] = cls

    def load(self, path: Path) -> T:
        pass

    def dump(self, path: Path, value: T):
        pass


class FmtText(Fmt[str], name="text"):
    extension = ".txt"

    def load(self, path: Path) -> str:
        return path.read_text()

    def dump(self, path: Path, value: str):
        path.write_text(value)


class FmtBinary(Fmt[bytes], name="binary"):
    extension = ".bin"

    def load(self, path: Path) -> bytes:
        return path.read_bytes()

    def dump(self, path: Path, value: bytes):
        path.write_bytes(value)


class FmtHexdump(Fmt[bytes], name="hexdump"):
    extension = ".hexdump"

    def load(self, path: Path) -> bytes:
        return hexload(path.read_text())

    def dump(self, path: Path, value: bytes):
        path.write_text("\n".join(hexdump(value)) + "\n")


class FmtJson(Fmt[Any], name="json"):
    extension = ".json"

    def load(self, path: Path) -> Any:
        return json.loads(path.read_text())

    def dump(self, path: Path, value: Any):
        path.write_text(json.dumps(value, indent=2) + "\n")


class FmtPickle(Fmt[Any], name="pickle"):
    extension = ".pickle"

    def load(self, path: Path) -> Any:
        return pickle.loads(path.read_bytes())

    def dump(self, path: Path, value: Any):
        path.write_bytes(pickle.dumps(value))
