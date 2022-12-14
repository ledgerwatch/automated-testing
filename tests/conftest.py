import logging
from dataclasses import dataclass

import _pytest.skipping
import pytest


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
    logging.basicConfig(level=logging.INFO)
    global option
    option = config.option


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_preparse(config, args):
    if "--no-skips" not in args:
        return

    def no_skip(*args, **kwargs):
        return

    _pytest.skipping.skip = no_skip


def pytest_collection_modifyitems(items):
    api_tests, other_tests = list(), list()
    for item in items:
        if 'api' in [i.name for i in item.own_markers]:
            api_tests.append(item)
        else:
            other_tests.append(item)
    items[:] = other_tests + api_tests
