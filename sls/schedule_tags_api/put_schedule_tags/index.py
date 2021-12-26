# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
"""
Handler for Get schedule tags
"""
import datetime
import pytz
import json
import re

from sls.utils.lambda_handler_helper import process_api_request
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_resource_groups_tagging import ResourceGroupsTaggingClient
from sls.utils.lambda_handler_helper import get_arn_generator
from sls.utils.logger import Logger
from sls.utils.db_helper import get_rds_name_type
from sls.utils.exceptions import InvalidParameter

logger = Logger()


def is_frequency_valid(frequency):
    if not frequency:
        return False
    pattern = re.compile('^[MTWHFSU](-[MTWHFSU])?$', re.IGNORECASE)
    if pattern.match(frequency):
        return True
    else:
        return False


def get_utc_hour(hour, local_timezone):
    """
        Convert hour to UTC from local_timezone

        Args:
            hour: integer between [0-23] representing the hour
            local_timezone: local timezone of the hour

        Returns:
            Integer: hour in utc

        Raises:
             InvalidParameter
    """
    try:
        today = datetime.date.today()
        naive_local_datetime = datetime.datetime(today.year, today.month, today.day, hour)

        local = pytz.timezone(local_timezone)
        aware_local_datetime = local.localize(naive_local_datetime, is_dst=None)
        utc_datetime = aware_local_datetime.astimezone(pytz.utc)
        return utc_datetime.hour
    except pytz.exceptions.UnknownTimeZoneError as invalid_timezone:
        raise InvalidParameter("Invalid timezone") from invalid_timezone
    except ValueError as error:
        if "hour must be" in str(error):
            raise InvalidParameter("Invalid. Hour must be between 0...23") from error
    except TypeError as error:
        raise InvalidParameter("Invalid. time should be provided in payload as integer") from error


def format_tags(time, tag_key, frequency, resource_type):
    """
    Format the tags for ec2 and rds
    Args:
        time: integer representing hour in utc
        tag_key: tag key on-hours or off-hours
        frequency: day from M, T, W, H, F, S, U. Can be range M-F
        resource_type: ec2 or rds
    """
    if resource_type == "rds":
        tag_value = f"{frequency}/{time}:tz=utc:"
    else:
        tag_value = f"({frequency},{time});tz=utc;"
    return {f"{tag_key}": f"{tag_value}"}


def put_schedule_tags(event):
    """
    Put on-hours and off-hours tags

    Args:
        event: API gateway proxy event

    Returns:
    """
    path_params = event.get('pathParameters', {})
    account_id = path_params.get('account_id')
    region = path_params.get('region')
    resource_type = path_params.get('resource_type')
    resource_identifier = path_params.get('resource_id')
    body = json.loads(event.get('body', '{}'))
    timezone = body.get("timezone")
    tag_key = body.get('type')
    time = body.get('time')
    frequency = body.get('frequency')

    if resource_type not in ["ec2", "rds"]:
        raise InvalidParameter("Not Supported. Only ec2 and rds supported for resource_type")

    if tag_key not in ["on-hours", "off-hours"]:
        raise InvalidParameter("Type of schedule tags can be on-hours or off-hours")

    if not is_frequency_valid(frequency):
        raise InvalidParameter("Frequency should be a value or a range in [M, T, W, H, F, S, U]")

    if resource_type == "rds":
        rds_name, rds_type = get_rds_name_type(resource_identifier)
        if rds_type == "cluster":
            raise InvalidParameter("Cluster cannot be scheduled for start or stop")

    utc_time = get_utc_hour(time, timezone)
    arn_generator = get_arn_generator(event, logger)
    resource_arn = arn_generator.generate_arn()
    formatted_tags = format_tags(utc_time, tag_key, frequency.upper(), resource_type)

    logger.info(f"Account: {account_id}")
    logger.info(f"Region: {region}")
    logger.info(f"Converted local_time: {time} to utc: {utc_time}")
    logger.info(f"Resource ARN: {resource_arn}")
    logger.info(f"Tags: {formatted_tags}")
    print(formatted_tags)
    aws_creds = AwsCreds(account_id, logger)
    rgt_client = ResourceGroupsTaggingClient(aws_creds, region, logger)
    rgt_client.tag_resource_per_arn(resource_arn, formatted_tags)
    return f"Tags {formatted_tags} applied successfully to {resource_arn}"


def handler(event, context):
    """
    api entry function
    """
    output = process_api_request(event, put_schedule_tags, logger)
    logger.info(output)
    return output
