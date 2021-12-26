"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring

from schedule_tags_api.common_bdd import schedule_tags_com_steps

from behave import given, when, then
from hamcrest import assert_that, contains_string

VALID_PAYLOAD = {
    'timezone': 'America/Chicago',
    'type': 'on-hours',
    'frequency': 'M-F',
    'time': 20
}

INVALID_PAYLOAD = {
    'timezone': 'America/Chicago',
    'type': 'on-hours',
    'frequency': 'M',
    'time': 30
}


@given(u'Resource is a cluster')
def resource_cluster(context):
    context.url = context.url.format(resource_id="cluster-resource-id")
    context.logger.info(context.url)


@when(u'we invoke the API')
def invoke_put_api(context):
    schedule_tags_com_steps.invoke_api(context, 'PUT', extra={'json': VALID_PAYLOAD})


@when(u'we invoke the api with invalid payload')
def invoke_put_api_invalid(context):
    schedule_tags_com_steps.invoke_api(context, 'PUT', extra={'json': INVALID_PAYLOAD})


@then(u'Valid schedule tag present for {res_type} instance')
def schedule_tags_is_updated_or_created(context, res_type):
    tags = schedule_tags_com_steps.get_schedule_tags(context)
    if res_type == "rds":
        formatted_tag = "M-F/1:tz=utc:"
    else:
        formatted_tag = "(M-F,1);tz=utc;"
    valid_tags = {
        "on-hours": f"{formatted_tag}"
    }
    return tags[0] == valid_tags


@then(u'error contains {message}')
def error_contains_message(context, message):
    try:
        error = context.response_data['error']
        assert_that(error, contains_string(message))
    except Exception as exc:
        context.logger.error(exc)
        assert False
