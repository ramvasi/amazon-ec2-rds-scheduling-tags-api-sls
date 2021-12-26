# pylint: disable=logging-format-interpolation, redefined-outer-name, redefined-builtin, bad-option-value, import-error
"""
Module for retrieving LDAP credential
"""
import logging
import json
import os
import boto3

#from cloudx_sls_authorization import lambda_auth
from sls.utils.exceptions import Unauthorized

# Initialize Logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Define secrets client
SECRETS_CLIENT = boto3.client('secretsmanager', 'us-east-1')

# Retrieve auth environment variables
AZURE_AUTH_CLIENT_ID = os.environ.get('AZURE_AUTH_CLIENT_ID')
AZURE_AUTH_SECRET_NAME = os.environ.get('AZURE_AUTH_SECRET_NAME')
MSFT_IDP_TENANT_ID = os.environ.get('MSFT_IDP_TENANT_ID')
MSFT_IDP_APP_ID = os.environ.get('MSFT_IDP_APP_ID', "").split(',')
MSFT_IDP_CLIENT_ROLES = os.environ.get('MSFT_IDP_CLIENT_ROLES', "").split(',')
LDAP_GROUP_NAME = os.environ.get('LDAP_GROUP_NAME')


def retrieve_azure_auth_credentials():
    """
    Retrieve password from secrets manager

    Args:

    Returns:
         string: password
    """
    secret_response = SECRETS_CLIENT.get_secret_value(
        SecretId=AZURE_AUTH_SECRET_NAME
    )
    secret = json.loads(secret_response['SecretString'])
    return secret['client_secret']


def format_ldap_group_names(event):
    """
       Replace account_id value in LDAP_GROUP_NAME

       Args:
            event: Event from Lambda proxy input

       Returns:
           List: formatted ldap groups
       """
    path_params = event.get('pathParameters', {})
    account_id = path_params.get('account_id')
    if account_id:
        formatted_group_names = LDAP_GROUP_NAME.format(project_id=account_id)
    return formatted_group_names.split(',')


def authorize_lambda(event):
    """
    Verifies token signature and returns token information.

    Args:
        event: Lambda event from API Gateway

    Returns:
        bool: is request allowed
    """
    group_names = format_ldap_group_names(event)
    azure_auth_secret = retrieve_azure_auth_credentials()

    try:
        # return lambda_auth.authorize_lambda_request_v2(event, MSFT_IDP_TENANT_ID, MSFT_IDP_APP_ID,
        #                                                MSFT_IDP_CLIENT_ROLES, AZURE_AUTH_CLIENT_ID,
        #                                                azure_auth_secret, group_names)
        pass
    except Exception as exc:
        raise Unauthorized(f"UNAUTHORIZED (User/App Token Unauthorized):{exc}") from exc
