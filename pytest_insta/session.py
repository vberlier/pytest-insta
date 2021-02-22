__all__ = ["SnapshotSession", "SnapshotContext"]


import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

from _pytest.terminal import TerminalReporter
from pytest import Session

from .format import Fmt
from .review import ReviewTool
from .utils import is_ci, pluralize, remove_path, rename_path


@dataclass
class SnapshotContext:
    path: Path
    counter: int
    available: Set[Path]
    matching: Set[Path]
    differing: Dict[Path, Tuple[Fmt[Any], Any]]

    def __post_init__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def created(self) -> Dict[Path, Tuple[Fmt[Any], Any]]:
        return {
            path: pair
            for path, pair in self.differing.items()
            if path not in self.available
        }

    @property
    def updated(self) -> Dict[Path, Tuple[Fmt[Any], Any]]:
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
                remove_path(path)
                session.deleted.add(path)

        self.reset()

    def reset(self):
        self.counter = 0
        self.matching = set()
        self.differing = {}


@dataclass
class SnapshotSession(Dict[Path, SnapshotContext]):
    session: Session
    config: Any = field(init=False)
    tr: TerminalReporter = field(init=False)
    record_dir: Path = field(init=False)
    strategy: str = "auto"
    recorded: Set[Path] = field(default_factory=set)
    rejected: Set[Path] = field(default_factory=set)
    created: Set[Path] = field(default_factory=set)
    updated: Set[Path] = field(default_factory=set)
    deleted: Set[Path] = field(default_factory=set)
    notices: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.config = self.session.config
        record_dir = self.config.cache.makedir("insta")

        self.tr = self.config.pluginmanager.getplugin("terminalreporter")
        self.record_dir = Path(record_dir).relative_to(Path(".").resolve())
        self.strategy = self.config.option.insta

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
        return self.strategy in ["review-only", "clear"]

    @property
    def should_clear_recorded(self) -> bool:
        return self.strategy in ["update", "clear"]

    def on_finish(self, status: int = 0):
        if not status:
            self.on_success()

        if snapshots_to_review := self.count_snapshots_to_review():
            self.notices.append(
                pluralize("snapshot", snapshots_to_review) + " to review"
            )

    def on_success(self):
        if self.should_review:
            capture = self.config.pluginmanager.getplugin("capturemanager")
            capture.suspend_global_capture(True)

            review_tool = ReviewTool(
                self.tr, self.config, self.record_dir, self.session.items
            )

            for snapshot, destination in review_tool.collect():
                if destination:
                    rename_path(snapshot, destination)
                    self.updated.add(destination)
                else:
                    remove_path(snapshot)
                    self.rejected.add(snapshot)
                self.recorded.discard(snapshot)

        if self.should_clear_recorded and (
            snapshots_to_clear := self.count_snapshots_to_review()
        ):
            shutil.rmtree(self.record_dir)
            self.notices.append(
                pluralize("recorded snapshot", snapshots_to_clear) + " cleared"
            )

    def write_summary(self):
        report = {
            "RECORD": self.recorded,
            "REJECT": self.rejected,
            "CREATE": self.created,
            "UPDATE": self.updated,
            "DELETE": self.deleted,
        }

        if not any(report.values()) and not self.notices:
            return

        self.tr.ensure_newline()
        self.tr.section("SNAPSHOTS", blue=True)

        for operation, snapshots in report.items():
            for snapshot in sorted(snapshots):
                self.tr.write_line(f"{operation} {snapshot}")

        if self.notices:
            if any(report.values()):
                self.tr.write_line("")

            for notice in self.notices:
                self.tr.write("NOTICE ", bold=True, yellow=True)
                self.tr.write_line(notice)

    def count_snapshots_to_review(self) -> int:
        return len(list(self.collect_snapshots_to_review()))

    def collect_snapshots_to_review(self) -> Iterable[str]:
        for _, dirs, files in os.walk(self.record_dir):
            directory_snapshots = {
                directory
                for directory in dirs
                if any(directory.endswith(extension) for extension in Fmt.registry)
            }
            dirs[:] = set(dirs) - directory_snapshots
            yield from directory_snapshots
            yield from files
