__all__ = ["SnapshotFixture", "SnapshotRecorder", "SnapshotNotfound"]


from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _pytest import fixtures
from wrapt import ObjectProxy

from .format import Fmt
from .session import SnapshotContext, SnapshotSession
from .utils import node_path_name


@dataclass
class SnapshotNotfound:
    path: Path

    def __repr__(self) -> str:
        return f"<not found: {self.path.name!r}>"


class SnapshotRecorder(ObjectProxy):
    __wrapped__: Any

    def __init__(self, path: Path, fmt: Fmt[Any], ctx: SnapshotContext, current: Any):
        super().__init__(current)  # type: ignore
        self._self_path = path
        self._self_fmt = fmt
        self._self_ctx = ctx

    def __eq__(self, other: Any) -> bool:
        if self.__wrapped__ == other:
            self._self_ctx.matching.add(self._self_path)
        else:
            self._self_ctx.differing[self._self_path] = self._self_fmt, other
            self.__wrapped__ = other
        return True


@dataclass
class SnapshotFixture:
    ctx: SnapshotContext
    session: SnapshotSession

    @classmethod
    def from_request(cls, request: fixtures.FixtureRequest) -> "SnapshotFixture":
        path, name = node_path_name(request.node)
        path = path.with_name("snapshots") / name
        session: SnapshotSession = getattr(request.config, "_snapshot_session")
        return cls(session[path], session)

    def __call__(self, spec: str = ".txt") -> Any:
        __tracebackhide__ = True

        name, fmt = Fmt.from_spec(spec)

        if not fmt:
            raise ValueError(f"invalid snapshot format {spec!r}")
        if not name:
            name = f"{self.ctx.counter}{fmt.extension}"
            self.ctx.counter += 1

        path = self.ctx.path.with_name(f"{self.ctx.path.name}__{name}")

        current = (
            fmt.load(path) if path in self.ctx.available else SnapshotNotfound(path)
        )

        return (
            SnapshotRecorder(path, fmt, self.ctx, current)
            if self.session.should_update
            or (self.session.should_create and isinstance(current, SnapshotNotfound))
            else current
        )

    def __enter__(self) -> "SnapshotFixture":
        return self

    def __exit__(self, *_):
        self.ctx.flush(self.session)

    def __repr__(self) -> str:
        return "snapshot"
