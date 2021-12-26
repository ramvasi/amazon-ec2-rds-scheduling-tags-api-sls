# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
"""
Handler for Get schedule tags
"""
from sls.utils.lambda_handler_helper import process_api_request
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_resource_groups_tagging import ResourceGroupsTaggingClient
from sls.utils.lambda_handler_helper import get_arn_generator
from sls.utils.logger import Logger

logger = Logger()
SCHEDULE_TAGS = ["on-hours", "off-hours"]


def delete_schedule_tags(event):
    """
    Delete tags for keys on-hours & off-hours

    Args:
        event: API gateway proxy event

    Returns:
        """
    path_params = event.get('pathParameters', {})
    account_id = path_params.get('account_id')
    region = path_params.get('region')
    arn_generator = get_arn_generator(event, logger)
    resource_arn = arn_generator.generate_arn()

    logger.info(f"Account: {account_id}")
    logger.info(f"Region: {region}")
    logger.info(f"Resource ARN: {resource_arn}")
    aws_creds = AwsCreds(account_id, logger)
    rgt_client = ResourceGroupsTaggingClient(aws_creds, region, logger)
    rgt_client.untag_resource_per_arn(resource_arn, SCHEDULE_TAGS)
    return f"Schedule tags removed successfully for {resource_arn}"


def handler(event, context):
    """
    api entry function
    """
    output = process_api_request(event, delete_schedule_tags, logger)
    logger.info(output)
    return output
