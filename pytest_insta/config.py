__all__ = ["SnapshotConfig"]

from dataclasses import dataclass
from typing import Any


@dataclass
class SnapshotConfig:
    use_directories_for_snapshots: bool

    @staticmethod
    def from_node(node: Any) -> "SnapshotConfig":
        marker = node.get_closest_marker("pytest_insta")
        if marker is None:
            return SnapshotConfig(use_directories_for_snapshots=False)
        return marker.kwargs.get("config")
