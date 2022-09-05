from dataclasses import dataclass


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


@dataclass
class Option:
    pass


option = Option()


def pytest_configure(config):
    global option
    option = config.option
