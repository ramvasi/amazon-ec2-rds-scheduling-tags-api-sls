# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring
"""
Returns info for aws account
"""

import os
import json

from sls.utils.aws_sm import retrieve_secret
from sls.cloudx_appsync_helper.gql_utils import execute_gql, gql_query_get_ext_account_by_project_id
from sls.utils.exceptions import InvalidAccount


def get_aws_account_number(project_id):
    """
    This function retrieves aws account id from graph ql for the given project id.
    project id is the path param received in the request
    Args:
        project_id: Id representing the account. Example: itx-046

    Returns:
       String: AWS account id
    """
    appsync_secret_name = os.environ.get('appsync_secret', 'NextBot/AppSync')
    appsync_secrets = json.loads(retrieve_secret(appsync_secret_name))
    gql_endpoint = appsync_secrets['url']
    api_key = appsync_secrets['key']
    query_items = '''items {
                    aws_number
                    }, 
                    nextToken
                '''
    get_account_by_project_id = gql_query_get_ext_account_by_project_id(query_items)
    response = execute_gql(gql_endpoint, api_key,
                           get_account_by_project_id,
                           {'ProjectId': project_id})
    next_token = response['data']['GetAccountByProjectId']['nextToken']
    items = response['data']['GetAccountByProjectId']['items']
    if not items:
        raise InvalidAccount('No entry matches this project id')
    if len(items) != 1 or next_token is not None:
        raise InvalidAccount('More than one entry matches this project id')
    return items[0]['aws_number']
