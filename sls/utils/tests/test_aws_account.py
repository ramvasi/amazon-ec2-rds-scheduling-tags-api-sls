import unittest

from unittest.mock import patch
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils.aws_account import get_aws_account_number
from sls.utils.exceptions import InvalidAccount


def get_gpl_return_value(item=None, token=None):
    return {
        "data":
            {
                "GetAccountByProjectId":
                    {
                        "items": item,
                        "nextToken": token
                    }

            }
    }


class TestAwsAccount(unittest.TestCase):
    def setUp(self):
        self.secret = "{\n \"url\":\"test_url\",\n \"key\":\"test_key\"\n}\n"
        self.aws_number = "test_aws_number"

    @patch("sls.utils.aws_account.execute_gql")
    @patch("sls.utils.aws_account.retrieve_secret")
    def test_get_aws_account_number(self, mock_secret, mock_gql):
        mock_secret.return_value = self.secret
        valid_item = [
            {
                "aws_number": self.aws_number
            }
        ]
        mock_gql.return_value = get_gpl_return_value(valid_item)

        returned_account = get_aws_account_number("test")
        self.assertEqual(returned_account, self.aws_number)

    @patch("sls.utils.aws_account.execute_gql")
    @patch("sls.utils.aws_account.retrieve_secret")
    def test_item_not_present_exception(self, mock_secret, mock_gql):
        mock_secret.return_value = self.secret
        mock_gql.return_value = get_gpl_return_value()

        self.assertRaises(InvalidAccount, get_aws_account_number, "test")
