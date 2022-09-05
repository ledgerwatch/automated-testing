# How to configure the environment for the project:

1. You should have python (preferably the latest stable release) on your machine
To install python, checkout the [Python website](https://www.python.org/downloads/). 
It is recommended to use virtualenv to run.
Please refer to the [Python website](https://virtualenv.pypa.io/en/latest/) for more information.

2. Create your venv in console: `python3 -m venv venv`
3. Activate your venv in console: `source venv/bin/activate`
4. Run `pip3 install -r requirements.txt` in root directory of the project to install all dependencies.

# How to Run the tests:

1. Start your `erigon` DEV node and `rpcdaemon` node. There is a guide on how to do this in 
the [DEV_CHAIN](https://github.com/ledgerwatch/erigon/blob/devel/DEV_CHAIN.md). 
Please make sure you pull latest code before running the tests. 

2. Run tests either one by one, or all together:

### locally:

1. For all tests to execute: run `python3 -m pytest` when being in `erigon-automated-testing` directory. In order to run specific test to run you may execute: `python3 -m pytest tests/test_block_creation_mvp.py::TestMVPTestCase::test_valid_transactions`
2. In a case of failed tests results are printed on screen and detailed report is kept in result.xml
