import os
import glob
import pytest
from easyInterface import logger, logging

logger.setLevel(logging.DEBUG)
logger.addSysOutput()
log = logger.getLogger(__name__)


@pytest.mark.parametrize('example', glob.glob(os.path.join('Examples', '*.py')))
def test_examples(example):
    example = example.replace(os.path.sep, '.')
    log.info('\033[1;35;49mStarting feature test: %s\033[0m', example)
    example = example.replace('.py', '')
    try:
        __import__(example)
        log.info('\033[1;35;49mSuccessful test: %s\033[0m', example)
    except:
        log.exception("\033[1;31;49mFatal error in test: {}\033[0m".format(example))
