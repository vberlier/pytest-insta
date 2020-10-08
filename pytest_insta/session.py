__all__ = ["SnapshotSession", "SnapshotContext"]


import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from _pytest.terminal import TerminalReporter
from pytest import Session

from .format import Fmt
from .review import ReviewTool
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
        if session.should_create:
            for path, (fmt, value) in self.created.items():
                fmt.dump(path, value)
                session.created.add(path)

        if session.should_record:
            record_dir = session.record_dir / self.path.parent.parent
            record_dir.mkdir(parents=True, exist_ok=True)

            for path, (fmt, value) in self.updated.items():
                path = record_dir / path.name
                fmt.dump(path, value)
                session.recorded.add(path)

        elif session.should_update:
            for path, (fmt, value) in self.updated.items():
                fmt.dump(path, value)
                session.updated.add(path)

        if session.should_delete:
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
    session: Session
    tr: TerminalReporter = field(init=False)
    record_dir: Path = field(init=False)
    strategy: str = "auto"
    recorded: Set[Path] = field(default_factory=set)
    rejected: Set[Path] = field(default_factory=set)
    created: Set[Path] = field(default_factory=set)
    updated: Set[Path] = field(default_factory=set)
    deleted: Set[Path] = field(default_factory=set)

    def __post_init__(self):
        record_dir = self.session.config.cache.makedir("insta")  # type: ignore

        self.tr = self.session.config.pluginmanager.getplugin("terminalreporter")
        self.record_dir = Path(record_dir).relative_to(Path(".").resolve())
        self.strategy = self.session.config.option.insta

        if self.strategy == "auto":
            self.strategy = "update-none" if is_ci() else "update-new"

    def __missing__(self, path: Path) -> SnapshotContext:
        available = set(path.parent.glob(f"{path.name}__*"))
        ctx = SnapshotContext(path, 0, available, set(), {})
        self[path] = ctx
        return ctx

    @property
    def should_record(self) -> bool:
        return self.strategy in ["record", "review"]

    @property
    def should_create(self) -> bool:
        return self.strategy in ["record", "review", "update", "update-new"]

    @property
    def should_update(self) -> bool:
        return self.strategy in ["record", "review", "update"]

    @property
    def should_delete(self) -> bool:
        return self.strategy in ["record", "review", "update"]

    @property
    def should_review(self) -> bool:
        return self.strategy in ["review-only", "review"]

    @property
    def should_skip_testloop(self) -> bool:
        return self.strategy in ["review-only"]

    def on_finish(self):
        if not self.should_review:
            return

        capture = self.session.config.pluginmanager.getplugin("capturemanager")
        capture.suspend_global_capture(True)

        review_tool = ReviewTool(self.tr, self.record_dir, self.session.items)

        for snapshot, destination in review_tool.collect():
            if destination:
                snapshot.rename(destination)
                self.updated.add(destination)
            else:
                snapshot.unlink()
                self.rejected.add(snapshot)
            self.recorded.discard(snapshot)

    def write_summary(self):
        notice_prefix = "\n"
        snapshots_to_review = self.count_snapshots_to_review()

        if not any(
            [self.recorded, self.rejected, self.created, self.updated, self.deleted]
        ):
            if snapshots_to_review:
                notice_prefix = ""
            else:
                return

        self.tr.ensure_newline()
        self.tr.section("SNAPSHOTS", blue=True)

        report = {
            "RECORD": self.recorded,
            "REJECT": self.rejected,
            "CREATE": self.created,
            "UPDATE": self.updated,
            "DELETE": self.deleted,
        }

        for operation, snapshots in report.items():
            for snapshot in snapshots:
                self.tr.write_line(f"{operation} {snapshot}")

        if snapshots_to_review:
            pluralized = "snapshot" + "s" * (snapshots_to_review > 1)
            self.tr.write(f"{notice_prefix}NOTICE", bold=True, yellow=True)
            self.tr.write_line(f" {snapshots_to_review} {pluralized} to review")

    def count_snapshots_to_review(self) -> int:
        return sum(len(entries[-1]) for entries in os.walk(self.record_dir))
