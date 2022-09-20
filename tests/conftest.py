from dataclasses import dataclass
import pytest
import _pytest.skipping

def pytest_addoption(parser):
    parser.addoption(
        "--url", action="store", default="http://localhost:8545", help="Erigon node url"
    )
    parser.addoption(
        "--datadir",
        action="store",
        default="",
        help="Directory to store log if tests failed",
    )
    parser.addoption(
        "--no-skips",
        action="store_true",
        default=False, help="disable skip marks")


@dataclass
class Option:
    pass


option = Option()


def pytest_configure(config):
    global option
    option = config.option


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_preparse(config, args):
    if "--no-skips" not in args:
        return

    def no_skip(*args, **kwargs):
        return

    _pytest.skipping.skip = no_skip