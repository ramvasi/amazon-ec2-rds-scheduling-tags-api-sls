"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring

from schedule_tags_api.common_bdd import schedule_tags_com_steps

from behave import when, then
from hamcrest import assert_that, contains_inanyorder


@when(u'we invoke the API')
def invoke_put_api(context):
    schedule_tags_com_steps.invoke_api(context, 'GET')


@then(u'response contains {message}')
def response_contains_message(context, message):
    try:
        tags = context.response_data['message']
        if message == "empty list":
            assert_that(len(tags) == 0)
        else:
            assert_that([tags[0]["Key"], tags[1]["Key"]],
                        contains_inanyorder("on-hours", "off-hours"))
    except Exception as exc:
        context.logger.error(exc)
        assert False
