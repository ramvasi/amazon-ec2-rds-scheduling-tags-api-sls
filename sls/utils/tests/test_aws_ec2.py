import logging
import unittest

from unittest.mock import patch
from sls.utils.aws_ec2 import is_region_valid, get_instance_memory, Ec2Client
from sls.utils.exceptions import ResourceNotFound
from botocore.exceptions import ClientError


class TestAwsEc2(unittest.TestCase):
    """
    Test for RdsClient
    """

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_is_region_valid(self, mock_client):
        mock_client.describe_regions.return_value = {
            "Regions": [
                {
                    "RegionName": "test_region"
                }
            ]
        }
        return_result = is_region_valid("test_region", logging.getLogger())
        self.assertTrue(return_result)

    def test_invalid_parameter(self):
        self.assertFalse(is_region_valid(None, logging.getLogger()))

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_client_error(self, mock_client):
        error = {
            "Error": {
                "Code": "InvalidParameterValue",
                "Message": "Invalid region",
            }
        }
        mock_client.side_effect = ClientError(error, "is_region_valid")
        return_result = is_region_valid("test_region", logging.getLogger())
        self.assertFalse(return_result)

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_exception(self, mock_client):
        error = {
            "Error": {
                "Code": "OtherClientError",
                "Message": "Client error",
            }
        }
        mock_client.describe_regions.side_effect = ClientError(error, "is_region_valid")
        self.assertRaises(ClientError, is_region_valid, "test_region", logging.getLogger())

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_get_instance_memory(self, mock_client):
        mock_client.describe_instance_types.return_value = {
            "InstanceTypes": [
                {
                    "MemoryInfo": {
                        "SizeInMiB": 123
                    }
                }
            ]
        }
        return_result = get_instance_memory("test_instance_type", logging.getLogger())
        self.assertEqual(return_result, 123)

    @patch("sls.utils.aws_ec2.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_instance_exists(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        client = mock_boto3.return_value
        instance = {"Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "testing"
                    }
                ]
            }
        ]
        }
        client.describe_instances.return_value = instance
        ec2_client = Ec2Client(aws_creds, "region_testing", logging.getLogger())
        self.assertTrue(ec2_client.instance_exists("testing"))

    @patch("sls.utils.aws_ec2.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_instance_exists_exception(self, mock_creds, mock_client):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}
        error = {
            "Error": {
                "Code": "InvalidInstanceID.NotFound",
                "Message": "Client error",
            }
        }
        client = mock_client.return_value
        client.describe_instances.side_effect = ClientError(error, "db_exists")
        ec2_client = Ec2Client(aws_creds, "region_testing", logging.getLogger())
        self.assertRaises(ResourceNotFound, ec2_client.instance_exists, "test_id")
