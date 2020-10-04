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
        ],
        help="Set the snapshot strategy. "
        'Defaults to "auto" when the argument is not specified.',
    )


def pytest_sessionstart(session):
    session.config._snapshot_session = SnapshotSession(session)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    # pylint: disable=unused-argument
    config._snapshot_session.write_summary()
