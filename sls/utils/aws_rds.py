"""
Module to make RDS calls
"""
# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position

import jmespath

from botocore.exceptions import ClientError, ParamValidationError
from sls.utils import get_boto3_client
from sls.utils.exceptions import DatabaseNotFound, ResourceNotFound


class RdsClient:
    """Class to make rds calls"""

    def __init__(self, aws_creds, rds_region, logger):
        """
        Setup for RDS Class
        @param aws_creds:
        """
        self.logger = logger
        self.rds_region = rds_region
        self.aws_creds = aws_creds
        self.credentials = self.aws_creds.get_creds()
        self.client = get_boto3_client("rds", self.rds_region, self.credentials)

    def get_metadata_by_instance_id(self, db_identifier, resp_filter):
        """
        Get the instance properties for the specified identifier

        Args:x
            db_identifier: DB Instance identifier
            resp_filter:

        Returns:
            Json: database properties

        Raises:
            DatabaseNotFound

        """
        try:

            response = self.client.describe_db_instances(
                DBInstanceIdentifier=db_identifier
            )
            return jmespath.search(resp_filter, response)
        except ParamValidationError as err:
            raise DatabaseNotFound(f"{db_identifier} not found. Details: {err}") from err
        except ClientError as boto_client_error:
            if boto_client_error.response["Error"]["Code"] in (
                    "DBInstanceNotFound",
                    "DBInstanceNotFoundFault",
                    "InvalidParameterValue"
            ):
                raise DatabaseNotFound(f"{db_identifier} not found") from boto_client_error
            else:
                raise boto_client_error

    def get_db_instance(self, db_identifier):
        instance_filter = "DBInstances[0]"
        return self.get_metadata_by_instance_id(db_identifier, instance_filter)

    def get_instance_arn(self, db_identifier):
        instance_filter = "DBInstances[0].DBInstanceArn"
        return self.get_metadata_by_instance_id(db_identifier, instance_filter)

    def get_cluster_arn(self, db_cluster_id):
        """
        Get the arn of a cluster

        Args:x
            db_cluster_id: Cluster identifier

        Returns:
            String: cluster arn

        Raises:
             ResourceNotFound

        """
        try:

            response = self.client.describe_db_clusters(
                DBClusterIdentifier=db_cluster_id
            )
            return response["DBClusters"][0]["DBClusterArn"]
        except ParamValidationError as err:
            raise ResourceNotFound(f"{db_cluster_id} not found. Details: {err}") from err
        except ClientError as boto_client_error:
            if boto_client_error.response["Error"]["Code"] in (
                    "DBClusterNotFound",
                    "DBClusterNotFoundFault",
                    "InvalidParameterValue"
            ):
                raise ResourceNotFound(f"{db_cluster_id} not found") from boto_client_error
            else:
                raise boto_client_error

