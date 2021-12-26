"""
Contains common behave steps for schedule tags api
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring


import json
import requests

from behave import then, given
from schedule_tags_api.common_bdd import logger
from hamcrest import assert_that, equal_to


@given(u'{method} Schedule API exists')
def api_exists(context, method):
    logger.info(f"Formatting url for {method} Schedule API")
    api_endpoint = "v1/accounts/{account_id}/regions/{region}/{resource_type}/{resource_id}/schedule"
    context.url = f"{context.vpce_endpoint}/{api_endpoint}"
    logger.info(context.url)


@given(u'valid oauth2 token for API authorization generated')
def generate_valid_auth(context):
    logger.info("Generating valid oauth2 token for API")
    context.token = context.api_req.get_access_token(client_id=context.jenkins_client_id,
                                                     client_secret=context.jenkins_client_secret,
                                                     scope=context.application_scope)


@given(u'invalid oauth2 token for API authorization generated')
def generate_invalid_auth(context):
    logger.info("Generating invalid oauth2 token for API")
    context.token = 'invalid_token'


@given(u'VPCx account is valid')
def with_valid_account(context):
    logger.info("Updating url with valid account")
    context.url = context.url.format(account_id=context.instance_account, region="{region}",
                                     resource_type="{resource_type}", resource_id="{resource_id}")
    logger.info(context.url)


@given(u'VPCx account is not valid')
def with_invalid_account(context):
    logger.info("Updating url with invalid region")
    context.url = context.url.format(account_id="account", region="us-east-1", database="database",
                                     resource_type="resource_type", resource_id="resource_id")
    logger.info(context.url)


@given(u'Region is valid')
def with_region_valid(context):
    logger.info("Updating url with valid region")
    context.url = context.url.format(region=context.instance_region,
                                     resource_type="{resource_type}", resource_id="{resource_id}")
    logger.info(context.url)


@given(u'Region is not valid')
def with_region_invalid(context):
    logger.info("Updating url with invalid region")
    context.url = context.url.format(region="region", resource_type="resource_type",
                                     resource_id="resource_id")
    logger.info(context.url)


@given(u'Resource type is set to {res_type}')
def set_res_type(context, res_type):
    logger.info(f"Setting resource type to {res_type}")
    context.url = context.url.format(resource_type=str(res_type), resource_id="{resource_id}")
    logger.info(context.url)


@given(u'Resource type is not valid')
def with_res_type_invalid(context):
    logger.info("Updating url with invalid resource type")
    context.url = context.url.format(resource_type="resource_type",
                                     resource_id="resource_id")
    logger.info(context.url)


@given(u'{res_type} instance exists')
def db_exists(context, res_type):
    logger.info("Updating url with valid resource")
    if res_type == "ec2":
        context.resource_id = context.ec2_instance_id
        context.current_arn = context.ec2_arn
    else:
        context.resource_id = f"instance-{context.rds_instance_name}"
        context.current_arn = context.rds_arn
    context.url = context.url.format(resource_id=context.resource_id)
    logger.info(context.url)


@given(u'{res_type} Resource does not exist')
def resource_not_valid(context, res_type):
    if res_type == "ec2":
        context.url = context.url.format(resource_id="resource-id")
    else:
        context.url = context.url.format(resource_id="instance-resource-id")
    logger.info(context.url)


@given(u'instance has schedule tags')
def schedule_tags_exist(context):
    testing_tags = {
        "on-hours": "testing_on",
        "off-hours": "testing_off"
    }
    return schedule_tags_present(context, tags=testing_tags)


@given(u'instance does not have schedule tags')
def remove_schedule_tags(context):
    return schedule_tags_not_present(context)


@then(u'API returns a status of {status}')
def check_return_status(context, status):
    assert_that(int(context.status_code), equal_to(int(status)))


@then(u'schedule tag is not present')
def schedule_tags_not_present(context):
    filtered_tags = get_schedule_tags(context)
    return len(filtered_tags) == 0


def schedule_tags_present(context, tags):
    try:
        context.rgt_client.tag_resource_per_arn(context.current_arn, tags)
        return True
    except Exception as error:
        logger.error(error)
        return False


def schedule_tags_not_present(context):
    try:
        tag_keys = ["on-hours", "off-hours"]
        context.rgt_client.untag_resource_per_arn(context.current_arn, tag_keys)
        return True
    except Exception as error:
        logger.error(error)
        return False


def get_schedule_tags(context):
    tags = context.rgt_client.get_resource_tags_per_arn(context.current_arn)
    filtered_tags = [
        tags for tags in tags
        if tags.get('Key') in ("on-hours", 'off-hours')
    ]
    return filtered_tags


def invoke_api(context, method, extra={}):
    logger.info(f"Invoking API {context.url}")
    headers = {
        'authorization': context.token,
        'Host': context.api_host
    }
    kwargs = {
        'headers': headers
    }
    kwargs.update(extra)
    response = requests.request(method, context.url, **kwargs)
    context.response = response
    context.status_code = response.status_code
    context.response_data = json.loads(context.response.text)
    logger.info(context.response_data)
