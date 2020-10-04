__all__ = ["SnapshotSession", "SnapshotContext"]


from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from _pytest.terminal import TerminalReporter
from pytest import Session

from .format import Fmt
from .utils import is_ci


@dataclass
class SnapshotContext:
    path: Path
    counter: int
    available: Set[Path]
    matching: Set[Path]
    differing: Dict[Path, Tuple[Fmt, Any]]

    def __post_init__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def created(self) -> Dict[Path, Tuple[Fmt, Any]]:
        return {
            path: pair
            for path, pair in self.differing.items()
            if path not in self.available
        }

    @property
    def updated(self) -> Dict[Path, Tuple[Fmt, Any]]:
        return {
            path: pair
            for path, pair in self.differing.items()
            if path in self.available
        }

    @property
    def deleted(self) -> Set[Path]:
        return self.available - self.matching - self.differing.keys()

    def flush(self, session: "SnapshotSession"):
        created, updated, deleted = (
            self.created if session.strategy in ["update", "update-new"] else {},
            self.updated if session.strategy == "update" else {},
            self.deleted if session.strategy == "update" else set(),
        )

        for source, target in [(created, session.created), (updated, session.updated)]:
            for path, (fmt, value) in source.items():
                fmt.dump(path, value)
                target.add(path)

        for path in deleted:
            path.unlink()
            session.deleted.add(path)

        self.reset()

    def reset(self):
        self.counter = 0
        self.matching = set()
        self.differing = {}


@dataclass
class SnapshotSession(Dict[Path, SnapshotContext]):
    session: Session
    tr: TerminalReporter = field(init=False)
    strategy: str = "auto"
    created: Set[Path] = field(default_factory=set)
    updated: Set[Path] = field(default_factory=set)
    deleted: Set[Path] = field(default_factory=set)

    def __post_init__(self):
        self.tr = self.session.config.pluginmanager.getplugin("terminalreporter")
        self.strategy = self.session.config.option.insta

        if self.strategy == "auto":
            self.strategy = "update-none" if is_ci() else "update-new"

    def __missing__(self, path: Path) -> SnapshotContext:
        available = set(path.parent.glob(f"{path.name}__*"))
        ctx = SnapshotContext(path, 0, available, set(), {})
        self[path] = ctx
        return ctx

    def write_summary(self):
        if not any([self.created, self.updated, self.deleted]):
            return

        self.tr.ensure_newline()
        self.tr.section("SNAPSHOTS", blue=True)

        report = {
            "CREATED": self.created,
            "UPDATED": self.updated,
            "DELETED": self.deleted,
        }

        for operation, snapshots in report.items():
            for snapshot in snapshots:
                self.tr.write_line(f"{operation} {snapshot}")
