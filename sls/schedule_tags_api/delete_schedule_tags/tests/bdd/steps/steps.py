"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring

from schedule_tags_api.common_bdd import schedule_tags_com_steps

from behave import when


@when(u'we invoke the API')
def invoke_put_api(context):
    schedule_tags_com_steps.invoke_api(context, 'DELETE')