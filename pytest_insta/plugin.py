import pytest

from .fixture import SnapshotFixture
from .session import SnapshotSession


def pytest_addoption(parser):
    group = parser.getgroup("snapshot options")
    group.addoption(
        "--update-snapshots",
        nargs="?",
        default="auto",
        const="all",
        choices=["auto", "all", "new", "none"],
        help="Update snapshots according to the specified strategy. "
        'Defaults to "auto" when the argument is not specified. '
        'Will be set to "all" if the argument is specified but without an explicit strategy.',
    )


def pytest_configure(config):
    config._snapshot_session = SnapshotSession(config.getoption("--update-snapshots"))


@pytest.fixture
def snapshot(request):
    with SnapshotFixture.from_request(request) as fixture:
        yield fixture


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    # pylint: disable=unused-argument
    session: SnapshotSession = getattr(config, "_snapshot_session")
    session.write_summary(terminalreporter)
