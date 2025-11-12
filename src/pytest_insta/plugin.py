# type: ignore


import pytest

from .fixture import SnapshotFixture
from .session import SnapshotSession


@pytest.fixture
def snapshot(request):
    with SnapshotFixture.from_request(request) as fixture:
        yield fixture


def pytest_addoption(parser):
    group = parser.getgroup("snapshot options")
    group.addoption(
        "--insta",
        default="auto",
        choices=[
            "auto",
            "update",
            "update-new",
            "update-none",
            "record",
            "review",
            "review-only",
            "clear",
        ],
        help="Set the snapshot strategy. "
        'Defaults to "auto" when the argument is not specified.',
    )


def pytest_sessionstart(session):
    session.config._snapshot_session = SnapshotSession(session)


def pytest_runtestloop(session):
    return session.config._snapshot_session.should_skip_testloop or None


def pytest_sessionfinish(session, exitstatus):
    session.config._snapshot_session.on_finish(exitstatus)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    config._snapshot_session.write_summary()
