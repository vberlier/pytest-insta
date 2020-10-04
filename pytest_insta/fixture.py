__all__ = ["SnapshotFixture", "SnapshotRecorder", "SnapshotNotfound"]


from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _pytest import fixtures, python
from wrapt import ObjectProxy

from .format import Fmt
from .session import SnapshotContext, SnapshotSession
from .utils import normalize_node_name


@dataclass
class SnapshotNotfound:
    path: Path

    def __repr__(self) -> str:
        return f"<not found: {self.path.name!r}>"


class SnapshotRecorder(ObjectProxy):  # pylint: disable=abstract-method
    def __init__(self, path: Path, fmt: Fmt, ctx: SnapshotContext, current: Any):
        super().__init__(current)
        self._self_path = path
        self._self_fmt = fmt
        self._self_ctx = ctx

    def __eq__(self, other: Any) -> bool:
        if self.__wrapped__ == other:
            self._self_ctx.matching.add(self._self_path)
        else:
            self._self_ctx.differing[self._self_path] = self._self_fmt, other
        return True


@dataclass
class SnapshotFixture:
    ctx: SnapshotContext
    session: SnapshotSession

    @classmethod
    def from_request(cls, request: fixtures.FixtureRequest) -> "SnapshotFixture":
        current = request.node
        hierarchy = [normalize_node_name(current.name)]

        while not isinstance(current, python.Module):
            current = current.parent
            hierarchy.append(normalize_node_name(current.name))

        path = Path(current.fspath).relative_to(Path(".").resolve())
        path = path.with_name("snapshots") / "__".join(reversed(hierarchy))

        session: SnapshotSession = getattr(request.config, "_snapshot_session")
        return cls(session[path], session)

    def __call__(self, spec: str = ".txt") -> Any:
        __tracebackhide__ = True  # pylint: disable=unused-variable

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
            if self.session.strategy == "update"
            or self.session.strategy == "update-new"
            and isinstance(current, SnapshotNotfound)
            else current
        )

    def __enter__(self) -> "SnapshotFixture":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.flush(self.session)

    def __repr__(self) -> str:
        return "snapshot"
