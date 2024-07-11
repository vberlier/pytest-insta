from collections.abc import Callable
from typing import Any

import pytest

from pytest_insta.config import SnapshotConfig


def config(
    config: SnapshotConfig,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return pytest.mark.pytest_insta(config=config)(func)

    return decorator
