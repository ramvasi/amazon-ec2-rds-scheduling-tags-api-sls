"""
This module contains behave framework function implementation
"""
# pylint:disable=no-name-in-module,import-error,wrong-import-position,missing-function-docstring

import os
import sys

THISDIR = os.path.dirname(__file__)  # common_bdd/
SERVDIR = os.path.dirname(THISDIR)  # schedule_tags_api/
SLSDIR = os.path.dirname(SERVDIR)  # sls/
APPDIR = os.path.dirname(SLSDIR)  # rds_scheduling/

sys.path.insert(0, THISDIR)
sys.path.insert(0, SERVDIR)
sys.path.insert(0, SLSDIR)
sys.path.insert(0, APPDIR)

from schedule_tags_api.common_bdd import logger
from schedule_tags_api.common_bdd.instance_setup import create_instances, delete_instances
from sls.utils.resource_arn import RdsInstanceArn, Ec2InstanceArn
from sls.utils_bdd.common_env import (set_common_before_all, set_rds_client,
                                      set_ec2_client_res, set_rgt_client)


def common_before_all(context):
    """
    This method runs before all

    Args:
        context:

    Returns:

    """
    logger.info("======================")
    logger.info("IN BEFORE ALL")
    logger.info("======================")
    env = os.environ["ENV"]
    context.env = env
    context.api_name = "schedule-tags-api"
    context.comm_config_file = f"{APPDIR}/config/config.common.json"
    context.env_config_file = f"{APPDIR}/config/config.{env}.json"
    set_common_before_all(context)
    logger.info("Setting RDS/EC2/ResourceGroupsTagging clients and EC2 resource")
    set_rds_client(context)
    set_ec2_client_res(context)
    set_rgt_client(context)
    logger.info("Creating testing instances")
    create_instances(context)
    context.rds_instance_name = "mysql80-8151"
    set_ec2_arn(context)
    set_rds_arn(context)
    context.resource_id = None
    context.current_arn = None


def set_ec2_arn(context):
    arn_generator = Ec2InstanceArn(context.instance_region, context.instance_account, context.ec2_instance_id)
    context.ec2_arn = arn_generator.generate_arn()


def set_rds_arn(context):
    arn_generator = RdsInstanceArn(context.instance_region, context.instance_account, context.rds_instance_name)
    context.rds_arn = arn_generator.generate_arn()


def common_after_all(context):
    delete_instances(context)
