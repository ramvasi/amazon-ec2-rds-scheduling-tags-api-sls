import os
import sys

THISDIR = os.path.dirname(__file__)  # bdd/
TESTSDIR = os.path.dirname(THISDIR)  # tests/
LAMBDADIR = os.path.dirname(TESTSDIR)  # lambda_function/
SERVDIR = os.path.dirname(LAMBDADIR)  # schedule_tags_api/
SLSDIR = os.path.dirname(SERVDIR)  # sls/
APPDIR = os.path.dirname(SLSDIR)  # rds-scheduling/

sys.path.insert(0, THISDIR)
sys.path.insert(0, TESTSDIR)
sys.path.insert(0, LAMBDADIR)
sys.path.insert(0, SERVDIR)
sys.path.insert(0, SLSDIR)
sys.path.insert(0, APPDIR)

from schedule_tags_api.common_bdd.environment import common_before_all, common_after_all

def before_all(context):
    common_before_all(context)


def after_all(context):
    common_after_all(context)
