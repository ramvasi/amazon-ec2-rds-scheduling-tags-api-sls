import unittest

from unittest.mock import patch, Mock
from sls.utils.logger import Logger
from sls.utils.lambda_handler_helper import get_arn_generator, set_logger_context_id
from sls.utils.exceptions import InvalidParameter

logger = Logger()


class TestLambdaHelper(unittest.TestCase):
    def test_set_logger_context_id(self):
        event = {
            "headers":
                {
                    "request-context-id": "test_context_id"
                }
        }
        returned_logger = set_logger_context_id(event, logger)
        expected_logger_id = event.get("headers").get("request-context-id")
        self.assertEqual(returned_logger.get_uuid(), expected_logger_id)

    def test_invalid_res_type(self):
        event = {
            "pathParameters":
                {
                    "resource_type": "invalid"
                }
        }
        self.assertRaises(InvalidParameter, get_arn_generator, event, logger)

    def test_ec2_generator(self):
        with patch("sls.utils.lambda_handler_helper.Ec2InstanceArn", new=Mock) as mock_arn:
            event = {
                "pathParameters":
                    {
                        "resource_type": "ec2"
                    }
            }
            returned_generator = get_arn_generator(event, logger)
            self.assertIsInstance(returned_generator, mock_arn)

    def test_rds_cluster_generator(self):
        with patch("sls.utils.lambda_handler_helper.RdsClusterArn", new=Mock) as mock_arn:
            event = {
                "pathParameters":
                    {
                        "resource_type": "rds",
                        "resource_id": "cluster-test"
                    }
            }
            returned_generator = get_arn_generator(event, logger)
            self.assertIsInstance(returned_generator, mock_arn)

    def test_rds_instance_generator(self):
        with patch("sls.utils.lambda_handler_helper.RdsInstanceArn", new=Mock) as mock_arn:
            event = {
                "pathParameters":
                    {
                        "resource_type": "rds",
                        "resource_id": "instance-test"
                    }
            }
            returned_generator = get_arn_generator(event, logger)
            self.assertIsInstance(returned_generator, mock_arn)
