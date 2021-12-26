import unittest

from unittest.mock import patch
from sls.utils.logger import Logger
from sls.utils.aws_rds import RdsClient
from sls.utils.exceptions import DatabaseNotFound, ResourceNotFound
from botocore.exceptions import ClientError

TEST_METADATA_FILTER = "DBInstances[].{db_arn: DBInstanceArn, " \
                       "instance_id: DBInstanceIdentifier, " \
                       " engine: Engine, master_username: MasterUsername," \
                       "instance_status: DBInstanceStatus} "


def get_paginate():
    return [
        {
            "instance_id": "mydbinstancecf",
            "engine": "mysql",
            "master_username": "masterawsuser",
            "instance_status": "available",
            "db_arn": "arn:aws:rds:<region>:<account number>:<resourcetype>:<name>"
        }
    ]


def get_tags():
    return {
        'TagList': [
            {
                'Key': 'on-hours',
                'Value': 'M-F'
            },
        ]
    }


class TestRdsClient(unittest.TestCase):
    """
    Test for RdsClient
    """

    @patch("sls.utils.aws_rds.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def setUp(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        self.client = mock_boto3.return_value

        logger = Logger()
        region = "testing"
        self.rds_client = RdsClient(aws_creds, region, logger)

    def test_get_db_instance(self):
        instance_properties = {
            'DBInstances': [
                {
                    'Engine': 'test_engine'
                }
            ]
        }
        self.client.describe_db_instances.return_value = instance_properties
        returned_engine = self.rds_client.get_db_instance('test_db_identifier')
        self.assertEqual(instance_properties['DBInstances'][0], returned_engine)

    def test_get_db_instance_exception(self):
        error = {
            "Error": {
                "Code": "DBInstanceNotFound",
                "Message": "Client error",
            }
        }
        self.client.describe_db_instances.side_effect = ClientError(error, "db_exists")
        self.assertRaises(DatabaseNotFound, self.rds_client.get_db_instance, "test_region")

    def test_get_instance_arn(self):
        instance_properties = {
            'DBInstances': [
                {
                    'DBInstanceArn': 'test_arn'
                }
            ]
        }
        self.client.describe_db_instances.return_value = instance_properties
        returned_arn = self.rds_client.get_instance_arn('test_db_identifier')
        self.assertEqual("test_arn", returned_arn)

    def test_get_cluster_arn(self):
        cluster_properties = {
            'DBClusters': [
                {
                    'DBClusterArn': 'test_arn'
                }
            ]
        }
        self.client.describe_db_clusters.return_value = cluster_properties
        returned_arn = self.rds_client.get_cluster_arn('test_db_identifier')
        self.assertEqual("test_arn", returned_arn)

    def test_get_cluster_arn_exception(self):
        error = {
            "Error": {
                "Code": "DBClusterNotFound",
                "Message": "Client error",
            }
        }
        self.client.describe_db_clusters.side_effect = ClientError(error, "db_exists")
        self.assertRaises(ResourceNotFound, self.rds_client.get_cluster_arn, "test_region")
