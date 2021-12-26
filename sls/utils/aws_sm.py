"""
Module to make secret manager calls
"""
# pylint: disable = import-error, wrong-import-position, wrong-import-order

import os
import boto3

region = os.environ.get('region_secret', "us-east-1")
default_client = boto3.client('secretsmanager', region_name=region)


def retrieve_secret(secret_name, client=None):
    """
    Retrieve secret from secret manager

    Args:
        secret_name:
        client: Secrets Manager client

    Returns:
        Value of the secret
    """
    secrets_client = client or default_client
    secret_value = secrets_client.get_secret_value(SecretId=secret_name)
    return secret_value.get("SecretString")
