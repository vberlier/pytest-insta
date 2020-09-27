__all__ = [
    "Snapshot",
    "SnapshotNotFound",
    "SnapshotText",
    "SnapshotBinary",
    "SnapshotHexdump",
    "SnapshotJson",
]


import json
from pathlib import Path
from typing import Any, ClassVar, Dict, Set, Tuple, Type

from .utils import ForwardedArgs, hexdump, hexload


class Snapshot:
    path: Path
    strategy: str
    matching: Set[Path]
    differing: Dict[Path, Tuple[Type["Snapshot"], Any]]

    registry: ClassVar[Dict[str, Type["Snapshot"]]] = {}
    extension: ClassVar[str] = ""
    BaseType: ClassVar[Type] = object
    NotFound: ClassVar[Type["Snapshot"]]

    def __init_subclass__(cls: Type["Snapshot"], fmt: str = None):
        if fmt:
            cls.registry[fmt] = cls

            mro = cls.mro()
            cls.BaseType = mro[mro.index(Snapshot) + 1]

            dct = {"fmt": fmt, "BaseType": cls.BaseType}
            cls.NotFound = type(f"{cls.__name__}.NotFound", (SnapshotNotFound,), dct)

    @classmethod
    def load_from(
        cls,
        path: Path,
        strategy: str,
        matching: Set[Path],
        differing: Dict[Path, Any],
    ) -> "Snapshot":
        args, kwargs = cls.get_args(path)

        instance = cls(*args, **kwargs)  # type: ignore
        instance.path = path
        instance.strategy = strategy
        instance.matching = matching
        instance.differing = differing

        return instance

    def __eq__(self, other: Any) -> bool:
        __tracebackhide__ = True  # pylint: disable=unused-variable
        other = self.validate(other)

        result = super().__eq__(other) is True  # Handle NotImplemented

        if result:
            self.matching.add(self.path)
        else:
            self.differing[self.path] = type(self), other

        return result or self.strategy == "all"

    def __ne__(self, other: Any) -> bool:
        __tracebackhide__ = True  # pylint: disable=unused-variable
        other = self.validate(other)
        return super().__eq__(other) is not True  # Handle NotImplemented

    def validate(self, value: Any) -> Any:
        __tracebackhide__ = True  # pylint: disable=unused-variable
        if isinstance(value, self.BaseType):
            return value
        raise TypeError(f"expected instance of {self.BaseType}, not {type(value)}")

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        # pylint: disable=unused-argument
        return (), {}

    @classmethod
    def update_value(cls, value: Any, path: Path):
        # pylint: disable=unused-argument
        pass


class SnapshotNotFound(Snapshot):
    fmt: ClassVar[str]

    def __eq__(self, other: Any) -> bool:
        __tracebackhide__ = True  # pylint: disable=unused-variable
        return super().__eq__(other) or self.strategy == "new"

    @classmethod
    def update_value(cls, value: Any, path: Path):
        cls.registry[cls.fmt].update_value(value, path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: {self.path.stem!r}>"


class SnapshotText(Snapshot, str, fmt="text"):
    extension = ".txt"

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        return (path.read_text(),), {}

    @classmethod
    def update_value(cls, value: str, path: Path):
        path.write_text(value)


class SnapshotBinary(Snapshot, bytes, fmt="binary"):
    extension = ".bin"

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        return (path.read_bytes(),), {}

    @classmethod
    def update_value(cls, value: bytes, path: Path):
        path.write_bytes(value)


class SnapshotHexdump(Snapshot, bytes, fmt="hexdump"):
    extension = ".hexdump"

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        return (hexload(path.read_text()),), {}

    @classmethod
    def update_value(cls, value: bytes, path: Path):
        path.write_text("\n".join(hexdump(value)) + "\n")


class SnapshotJson(Snapshot, dict, fmt="json"):
    extension = ".json"

    @classmethod
    def get_args(cls, path: Path) -> ForwardedArgs:
        return (json.loads(path.read_text()),), {}

    @classmethod
    def update_value(cls, value: dict, path: Path):
        path.write_text(json.dumps(value, indent=2) + "\n")
