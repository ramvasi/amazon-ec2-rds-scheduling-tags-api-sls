import unittest

from unittest.mock import patch
from sls.utils.resource_arn import Ec2InstanceArn, RdsClusterArn, RdsInstanceArn


class TestResourceArn(unittest.TestCase):
    def setUp(self):
        self.account_id = "testing_account_id"
        self.resource_id = "testing_id"
        self.region = "region"
        self.account_number = "test_account_number"

    @patch("sls.utils.api_request.get_secret_value", return_value="")
    @patch("sls.utils.resource_arn.Ec2Client")
    @patch("sls.utils.resource_arn.get_aws_account_number")
    def test_generate_ec2_arn(self, mock_account, mock_client, mock_secret):
        ec2_client = mock_client.return_value
        ec2_client.instance_exists.return_value = True
        mock_account.return_value = self.account_number
        ec2_res_arn = Ec2InstanceArn(self.region, self.account_id, self.resource_id)
        expected_arn = f"arn:aws:ec2:{self.region}:{self.account_number}:instance/{self.resource_id}"
        returned_arn = ec2_res_arn.generate_arn()
        self.assertEqual(expected_arn, returned_arn)

    @patch("sls.utils.api_request.get_secret_value", return_value="")
    @patch("sls.utils.resource_arn.RdsClient")
    @patch("sls.utils.resource_arn.get_aws_account_number")
    def test_generate_rds_cluster_arn(self, mock_account, mock_client, mock_secret):
        mock_account.return_value = self.account_number
        rds_client = mock_client.return_value
        expected_arn = f"arn:aws:rds:{self.region}:{self.account_number}:cluster:{self.resource_id}"
        rds_client.get_cluster_arn.return_value = expected_arn
        res_arn = RdsClusterArn(self.region, self.account_id, self.resource_id)
        returned_arn = res_arn.generate_arn()
        self.assertEqual(expected_arn, returned_arn)

    @patch("sls.utils.api_request.get_secret_value", return_value="")
    @patch("sls.utils.resource_arn.RdsClient")
    @patch("sls.utils.resource_arn.get_aws_account_number")
    def test_generate_rds_instance_arn(self, mock_account, mock_client, mock_secret):
        mock_account.return_value = self.account_number
        rds_client = mock_client.return_value
        expected_arn = f"arn:aws:rds:{self.region}:{self.account_number}:instance:{self.resource_id}"
        rds_client.get_instance_arn.return_value = expected_arn
        res_arn = RdsInstanceArn(self.region, self.account_id, self.resource_id)
        returned_arn = res_arn.generate_arn()
        self.assertEqual(expected_arn, returned_arn)
