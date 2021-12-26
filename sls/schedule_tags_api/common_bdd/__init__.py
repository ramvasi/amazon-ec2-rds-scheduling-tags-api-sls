"""
base init file
"""
# pylint:disable=wrong-import-position,wrong-import-order, import-error, W0703
import os
import sys

THISDIR = os.path.dirname(__file__)  # common_bdd/
APPDIR = os.path.dirname(THISDIR)  # schedule_tags_api/

sys.path.insert(0, THISDIR)
sys.path.insert(0, APPDIR)


from sls.utils.logger import Logger


logger = Logger()
