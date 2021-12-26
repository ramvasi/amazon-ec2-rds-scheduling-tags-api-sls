import os
import json

from schedule_tags_api.common_bdd import logger
from sls.utils_bdd.api_host import set_api_host
from sls.utils import get_boto3_client, get_boto3_resource
from sls.utils.aws_sm import retrieve_secret
from sls.utils.aws_creds import AwsCreds
from sls.utils.api_request import ApiRequests
from sls.utils.aws_rds import RdsClient
from sls.utils.aws_resource_groups_tagging import ResourceGroupsTaggingClient


def set_common_before_all(context):
    with open(context.comm_config_file) as comm_config_file:
        comm_config = json.load(comm_config_file)

    with open(context.env_config_file) as env_config_file:
        env_config = json.load(env_config_file)

    logger.info("Setting up context and environment variables")
    set_env_variables(comm_config, env_config)
    set_context(context, comm_config, env_config, logger)
    logger.info("Setting Jenkins Secret")
    set_jenkins_secret(context)
    logger.info("Setting api host")
    set_api_host(context, logger, context.env)


def set_env_variables(config, env_config):
    os.environ['token_url'] = config['ENVIRONMENT']['TOKEN_URL']
    os.environ['vpcxiam_endpoint'] = env_config['VPCXIAM']['VPCXIAM_ENDPOINT']
    os.environ['vpcxiam_scope'] = env_config['VPCXIAM']['VPCXIAM_SCOPE']
    os.environ['vpcxiam_host'] = env_config['VPCXIAM']['VPCXIAM_HOST']
    os.environ['app_client_id'] = env_config['OAUTH2']['APP_CLIENT_ID']
    os.environ['db_account'] = env_config["MAIN"]["ACCOUNT"]


def set_context(context, config, env_config, logger):
    context.token_url = config['ENVIRONMENT']['TOKEN_URL']
    context.vpce_endpoint = env_config['VPCXIAM']['VPCXIAM_ENDPOINT']
    context.application_scope = env_config['OAUTH2']['APPLICATION_SCOPE']
    context.jenkins_client_id = env_config["BEHAVE"]["JENKINS_CLIENT_ID"]
    context.jenkins_secret_name = env_config["BEHAVE"]["JENKINS_SECRET_NAME"]
    context.admin_region = env_config['MAIN']['REGION']
    context.admin_account = env_config['MAIN']['ADMIN_ACCOUNT']
    context.instance_account = env_config["MAIN"]["ACCOUNT"]
    context.instance_region = env_config["BEHAVE"]["INSTANCE_REGION"]
    context.sg_name = env_config["BEHAVE"]["DB_VPC_SECURITY_GROUP_NAME"]
    context.subnet_name = env_config["BEHAVE"]["DB_SUBNET_GROUP_NAME"]
    context.subnet_id = env_config["BEHAVE"]["SUBNET_ID"]
    context.stack_name = f"{context.api_name}-{context.env}"
    context.admin_creds = AwsCreds(context.admin_account, logger)
    context.instance_creds = AwsCreds(context.instance_account, logger)
    context.api_req = ApiRequests()
    context.logger = logger


def set_jenkins_secret(context):
    credentials = context.admin_creds.get_creds()
    sm_client = get_boto3_client("secretsmanager", context.admin_region, credentials)
    context.jenkins_client_secret = retrieve_secret(
        context.jenkins_secret_name, sm_client
    )


def set_rds_client(context):
    """
     Set RDS Client
    """
    aws_creds = context.instance_creds
    rds_region = context.instance_region
    context.rds_client = RdsClient(aws_creds, rds_region, context.logger).client


def set_rgt_client(context):
    """
     Set RDS Client
    """
    aws_creds = context.instance_creds
    region = context.instance_region
    context.rgt_client = ResourceGroupsTaggingClient(aws_creds, region, context.logger)


def set_ec2_client_res(context):
    """
    Set EC2 Client and EC2 resource
    """
    aws_creds = context.instance_creds
    region = context.instance_region
    credentials = aws_creds.get_creds()
    context.ec2_client = get_boto3_client("ec2", region, credentials)
    context.ec2_resource = get_boto3_resource("ec2", region, credentials)
