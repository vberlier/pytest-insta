__all__ = ["SnapshotFixture"]


from dataclasses import dataclass
from pathlib import Path

from _pytest import fixtures, python

from .session import SnapshotContext, SnapshotSession
from .snapshot import Snapshot
from .utils import normalize_node_name


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

    def __call__(self, name: str = None, fmt: str = "text", ext: str = "") -> Snapshot:
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if not (cls := Snapshot.registry.get(fmt)):
            raise ValueError(f"invalid snapshot format {fmt!r}")

        if not name:
            name = str(self.ctx.counter)
            self.ctx.counter += 1

        ext = ext or cls.extension
        path = self.ctx.path.with_name(f"{self.ctx.path.name}__{name}{ext}")

        if path not in self.ctx.available:
            cls = cls.NotFound

        return cls.load_from(
            path=path,
            strategy=self.ctx.strategy,
            matching=self.ctx.matching,
            differing=self.ctx.differing,
        )

    def __enter__(self) -> "SnapshotFixture":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.flush(self.session)

    def __repr__(self) -> str:
        return "snapshot"
