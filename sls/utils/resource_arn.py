"""
Generate arn for different resources types
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring
from abc import ABC, abstractmethod
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_rds import RdsClient
from sls.utils.aws_ec2 import Ec2Client
from sls.utils.aws_account import get_aws_account_number
from sls.utils.logger import Logger

lgr = Logger()


class ResourceArn(ABC):
    """
    Base class to generate ARN for resources
    """

    def __init__(self, region, account_id, resource_id, logger=None):
        self.region = region
        self.account_id = account_id
        self.resource_id = resource_id
        self.logger = logger or lgr
        self.aws_creds = AwsCreds(account_id, logger)
        self.aws_account_number = get_aws_account_number(account_id)
        self.base_arn = f"arn:aws:{{service}}:{self.region}:{self.aws_account_number}:{{arn_suffix}}"
        self.arn_suffix = resource_id
        self.service = "undefined"

    @abstractmethod
    def generate_arn(self):
        pass

    def format_arn(self):
        generated_arn = self.base_arn.format(service=self.service, arn_suffix=self.arn_suffix)
        self.logger.info(f"Returned ARN for {self.service}"
                         f" with suffix {self.arn_suffix}:{generated_arn}")
        return generated_arn


class Ec2InstanceArn(ResourceArn):
    """
        Class that generates ARN for Ec2 instances
    """

    def __init__(self, region, account_id, resource_id, logger=None):
        logger = logger or lgr
        super().__init__(region, account_id, resource_id, logger)
        self.client = Ec2Client(self.aws_creds, region, logger)

    def generate_arn(self):
        if self.client.instance_exists(self.resource_id):
            self.service = "ec2"
            self.arn_suffix = f"instance/{self.resource_id}"
            return self.format_arn()


class RdsClusterArn(ResourceArn):
    """
        Class that generates ARN for Rds cluster
    """

    def __init__(self, region, account_id, resource_id, logger=None):
        logger = logger or lgr
        super().__init__(region, account_id, resource_id, logger)
        self.client = RdsClient(self.aws_creds, region, logger)

    def generate_arn(self):
        returned_arn = self.client.get_cluster_arn(self.resource_id)
        self.logger.info(f"Returned ARN for RDS Cluster:{returned_arn}")
        return returned_arn


class RdsInstanceArn(ResourceArn):
    """
        Class that generates ARN for Rds instances
    """

    def __init__(self, region, account_id, resource_id, logger=None):
        logger = logger or lgr
        super().__init__(region, account_id, resource_id, logger)
        self.client = RdsClient(self.aws_creds, region, logger)

    def generate_arn(self):
        returned_arn = self.client.get_instance_arn(self.resource_id)
        self.logger.info(f"Returned ARN for RDS Instance:{returned_arn}")
        return returned_arn
