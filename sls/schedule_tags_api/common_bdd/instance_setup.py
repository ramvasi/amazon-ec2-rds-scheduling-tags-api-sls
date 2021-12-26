"""
    Instance setup and cleanup for BDD tests
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring
from sls.utils_bdd.db_setup import create_rds_resource, delete_rds_resource
from sls.utils_bdd.ec2_helper import create_ec2_instance, terminate_ec2_instance

DB_INSTANCE_DATA = {
    "mysql80-8151": {
        "DBInstanceIdentifier": "mysql80-8151",
        "EngineVersion": "8.0.25",
        "Engine": "mysql",
        "LicenseModel": "general-public-license",
        "DBInstanceClass": "db.t4g.micro",
        "BackupRetentionPeriod": 0,
        "AllocatedStorage": 5,
        "MasterUsername": "testuser8151",
        "MasterUserPassword": "adm1nPassw0rd8151"
    }
}

EC2_INSTANCE_DATA = {
    "image_id": "ami-02e136e904f3da870",
    "instance_type": "t2.nano",
    "max_count": 1,
    "min_count": 1,
    "tag_spec": [
        {
            "ResourceType": "instance",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "linux-8151"
                },
                {
                    "Key": "on-hours",
                    "Value": "testing_on"
                },
                {
                    "Key": "off-hours",
                    "Value": "testing_off"
                }
            ]
        }
    ]
}


def create_instances(context):
    """

        Args:
            context: bdd context

        Returns:

        """
    create_rds_resource(context, DB_INSTANCE_DATA)
    create_ec2_instance(context, EC2_INSTANCE_DATA)


def delete_instances(context):
    """

    Args:
        context: bdd context

    Returns:

    """
    terminate_ec2_instance(context)
    delete_rds_resource(context, DB_INSTANCE_DATA)
