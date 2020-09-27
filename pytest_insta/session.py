__all__ = ["SnapshotSession", "SnapshotContext"]


from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Set, Tuple, Type

from _pytest.terminal import TerminalReporter

from .snapshot import Snapshot
from .utils import is_ci


@dataclass
class SnapshotContext:
    path: Path
    counter: int
    strategy: str
    available: Set[Path]
    matching: Set[Path]
    differing: Dict[Path, Tuple[Type[Snapshot], Any]]

    def __post_init__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def created(self) -> Dict[Path, Tuple[Type[Snapshot], Any]]:
        if self.strategy not in ("all", "new"):
            return {}
        return {
            path: pair
            for path, pair in self.differing.items()
            if path not in self.available
        }

    @property
    def updated(self) -> Dict[Path, Tuple[Type[Snapshot], Any]]:
        if self.strategy != "all":
            return {}
        return {
            path: pair
            for path, pair in self.differing.items()
            if path in self.available
        }

    @property
    def deleted(self) -> Set[Path]:
        if self.strategy != "all":
            return set()
        return self.available - self.matching - self.differing.keys()

    def flush(self, session: "SnapshotSession"):
        differing = [(self.created, session.created), (self.updated, session.updated)]

        for source, target in differing:
            for path, (snapshot_type, value) in source.items():
                snapshot_type.update_value(value, path)
                target.add(path)

        for path in self.deleted:
            path.unlink()
            session.deleted.add(path)

        self.reset()

    def reset(self):
        self.counter = 0
        self.matching = set()
        self.differing = {}


@dataclass
class SnapshotSession(Dict[Path, SnapshotContext]):
    strategy: str
    created: Set[Path] = field(default_factory=set)
    updated: Set[Path] = field(default_factory=set)
    deleted: Set[Path] = field(default_factory=set)

    def __post_init__(self):
        if self.strategy == "auto":
            self.strategy = "none" if is_ci() else "new"

    def __missing__(self, path: Path) -> SnapshotContext:
        available = set(path.parent.glob(f"{path.name}__*"))
        ctx = SnapshotContext(path, 0, self.strategy, available, set(), {})
        self[path] = ctx
        return ctx

    def write_summary(self, tr: TerminalReporter):
        if not any([self.created, self.updated, self.deleted]):
            return

        tr.ensure_newline()
        tr.section("SNAPSHOTS", blue=True)

        report = {
            "CREATED": self.created,
            "UPDATED": self.updated,
            "DELETED": self.deleted,
        }

        for operation, snapshots in report.items():
            for snapshot in snapshots:
                tr.write_line(f"{operation} {snapshot}")
