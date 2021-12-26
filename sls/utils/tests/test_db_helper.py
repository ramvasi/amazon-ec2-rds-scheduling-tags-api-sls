import unittest


from sls.utils.db_helper import get_rds_name_type


class TestDbHelper(unittest.TestCase):

    def test_get_rds_name_type(self):
        db_identifier = "instance-test_id"
        returned_db_id, returned_db_type = get_rds_name_type(db_identifier)
        self.assertEqual(returned_db_type, "instance")
        self.assertEqual(returned_db_id, "test_id")

    def test_exception(self):
        db_identifier = "invalid"
        self.assertRaises(Exception, get_rds_name_type, db_identifier)
