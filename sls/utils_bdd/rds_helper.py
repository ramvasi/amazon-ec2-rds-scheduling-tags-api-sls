"""
    RDS utilities functions for bdd
"""
# pylint: disable=wrong-import-position,no-value-for-parameter
import time
import mysql.connector

from botocore.exceptions import ClientError
from mysql.connector import errorcode
from sls.retry.api import retry
from sls.utils.exceptions import ClusterExists, DatabaseNotAvailable, InstanceExists
from sls.utils.aws_rds import RdsClient


def is_db_present(context, rds_client, db_instance_name):
    try:
        db_exists = \
            rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_name)['DBInstances'][
                0][
                'DBInstanceStatus']
        context.logger.info(
            f"DB instance %s already exists with status %s" % (db_instance_name, db_exists))
        return True
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBInstanceNotFound":
            context.logger.info(f"DB instance %s does not exist" % db_instance_name)
            return False
        else:
            raise boto_client_error


def create_rds_instance(context, rds_client, db_instance_name, db_info):
    if not is_db_present(context, rds_client, db_instance_name):
        try:
            res = rds_client.create_db_instance(**db_info)
            if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                context.logger.info(f"Successfully initiated create DB instance %s" % db_instance_name)
                context.logger.info(f"waiting for db instance %s to be available" % db_instance_name)
                wait_for_instance(rds_client, db_instance_name)
                return True
            else:
                context.logger.info(f"Couldn't create DB instance %s" % db_instance_name)
                return False
        except Exception as error:
            context.logger.error(error)
            return False
    return True


def wait_for_instance(rds_client, db_instance_name):
    rds_waiter = rds_client.get_waiter('db_instance_available')
    rds_waiter.wait(
        DBInstanceIdentifier=db_instance_name
    )


def create_rds_cluster(context, rds_client, db_cluster_name, db_info):
    try:
        db_exists = \
            rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_name)['DBClusters'][0][
                'Status']
        context.logger.info(
            f"DB cluster %s already exists with status %s" % (db_cluster_name, db_exists))
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBClusterNotFoundFault":
            context.logger.info(f"DB cluster %s does not exist" % db_cluster_name)
            res_c = rds_client.create_db_cluster(
                VpcSecurityGroupIds=db_info['sg_name'],
                DBSubnetGroupName=db_info['subnet_name'],
                BackupRetentionPeriod=1,
                DBClusterIdentifier=db_cluster_name,
                Engine=db_info['engine'],
                EngineVersion=db_info['version'],
                MasterUsername=db_info['master_user'],
                MasterUserPassword=db_info['master_pwd'],
                EngineMode=db_info['mode']
            )

            if res_c['ResponseMetadata']['HTTPStatusCode'] == 200:
                context.logger.info(
                    f"Successfully initiated create DB cluster %s" % db_cluster_name)
            else:
                context.logger.info(f"Couldn't create DB cluster %s" % db_cluster_name)

            context.logger.info(f"waiting for db cluster %s to be available" % db_cluster_name)
            check_cluster_available(db_cluster_name, context)
        else:
            raise boto_client_error

    if db_info['mode'] == 'serverless':
        return True
    try:
        db_details = rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_name)
        if len(db_details['DBClusters'][0]['DBClusterMembers']) > 0:
            context.logger.info(f"DB cluster instance already exists for %s" % db_cluster_name)
            return True
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBClusterNotFoundFault":
            context.logger.info(f"DB cluster %s does not exist" % db_cluster_name)
            return False
    db_instance_name = db_cluster_name + '-instance'
    res_i = rds_client.create_db_instance(
        DBInstanceIdentifier=db_instance_name,
        DBInstanceClass="db.r4.large",
        Engine=db_info['engine'],
        DBClusterIdentifier=db_cluster_name,
        PubliclyAccessible=False
    )
    if res_i['ResponseMetadata']['HTTPStatusCode'] == 200:
        context.logger.info(
            f"Successfully initiated create DB cluster-instance %s" % db_instance_name)
    else:
        context.logger.info(f"Couldn't create DB cluster-instance %s" % db_instance_name)

    context.logger.info(f"waiting for db cluster-instance %s to be available" % db_instance_name)
    check_instance_available(db_instance_name, context)


def delete_rds_cluster(context, rds_client, db_cluster_name):
    try:
        db_details = rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_name)
        for i in db_details['DBClusters'][0]['DBClusterMembers']:
            delete_rds_instance(context, rds_client, i['DBInstanceIdentifier'])
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBClusterNotFoundFault":
            context.logger.info(f"DB cluster %s does not exist" % db_cluster_name)
            return True

    res = rds_client.delete_db_cluster(
        DBClusterIdentifier=db_cluster_name,
        SkipFinalSnapshot=True)
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        context.logger.info(f"Successfully initiated delete DB cluster %s" % db_cluster_name)
    else:
        context.logger.info(f"Couldn't delete DB cluster %s" % db_cluster_name)

    context.logger.info(f"waiting for db cluster %s to be deleted" % db_cluster_name)
    check_cluster_removed(db_cluster_name, context)


def delete_rds_instance(context, rds_client, db_instance_name):
    try:
        db_status = \
            rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_name)['DBInstances'][
                0][
                'DBInstanceStatus']
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBInstanceNotFound":
            context.logger.info(f"DB instance %s is already deleted" % db_instance_name)
            return True

    try:
        res = rds_client.delete_db_instance(
            DBInstanceIdentifier=db_instance_name,
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=True)
    except ClientError as boto_client_error:
        if 'NoDeleteAutomatedBackups' in boto_client_error.response["Error"]["Message"]:
            res = rds_client.delete_db_instance(
                DBInstanceIdentifier=db_instance_name,
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=False)
        else:
            raise boto_client_error
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        context.logger.info(f"Successfully initiated delete DB instance %s" % db_instance_name)
    else:
        context.logger.info(f"Couldn't delete DB instance %s" % db_instance_name)

    context.logger.info(f"waiting for db instance %s to be deleted" % db_instance_name)
    check_instance_removed(db_instance_name, context)


def get_db_connection(context, rds_client, db_conn_info):
    """
    Function to test DB connection

    Args:
        context:
        pwd:
        db_name:

    Returns:

    """
    try:
        context.logger.info(f"checking connection for %s" % db_conn_info['db_name'])
        conn_config = {"user": db_conn_info['user_name'], "password": db_conn_info['user_pwd'],
                       "host": db_conn_info['endpoint'], "port": db_conn_info['port']}
        cnx = mysql.connector.connect(**conn_config)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            context.logger.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            context.logger.error("Database does not exist")
        else:
            context.logger.error(err)
        raise err


@retry(DatabaseNotAvailable, delay=30, tries=30)
def check_instance_available(db_instance_name, context):
    """
    Retry loop to ensure instance is available
    Args:
        db_instance_name:
        context:
        rds_client:

    Returns:

    """
    rds_client = RdsClient(
        context.db_creds, context.db_region, context.logger
    ).client
    db_status = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_name)[
        "DBInstances"
    ][0]["DBInstanceStatus"]
    if db_status == "available":
        context.logger.info(f"DB instance %s is ready" % db_instance_name)
    else:
        raise DatabaseNotAvailable(f"DB instance %s is not ready" % db_instance_name)


@retry(DatabaseNotAvailable, delay=30, tries=30)
def check_cluster_available(db_cluster_name, context):
    """
    Retry loop to ensure cluster is available
    Args:
        db_cluster_name:
        context:
        rds_client:

    Returns:

    """
    rds_client = RdsClient(
        context.db_creds, context.db_region, context.logger
    ).client
    db_status = rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_name)[
        "DBClusters"
    ][0]["Status"]
    if db_status == "available":
        context.logger.info(f"DB cluster %s is ready" % db_cluster_name)
    else:
        raise DatabaseNotAvailable(f"DB cluster %s is not ready" % db_cluster_name)


@retry(ClusterExists, delay=30, tries=25)
def check_cluster_removed(db_cluster_name, context):
    """
    Retry loop to ensure cluster is deleted
    Args:
        db_cluster_name:
        context:

    Returns:

    """
    try:
        rds_client = RdsClient(
            context.db_creds, context.db_region, context.logger
        ).client
        db_status = rds_client.describe_db_clusters(
            DBClusterIdentifier=db_cluster_name
        )["DBClusters"][0]["Status"]
        raise ClusterExists(f"DB cluster %s is not deleted" % db_cluster_name)
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBClusterNotFoundFault":
            context.logger.info(f"DB cluster %s is deleted" % db_cluster_name)
        else:
            raise boto_client_error


@retry(InstanceExists, delay=30, tries=25)
def check_instance_removed(db_instance_name, context):
    """
    Retry loop to ensure instance is deleted
    Args:
        db_instance_name:
        context:

    Returns:

    """
    try:
        rds_client = RdsClient(
            context.instance_creds, context.instance_region, context.logger
        ).client
        rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_name
        )["DBInstances"][0]["DBInstanceStatus"]
        raise InstanceExists(f"DB instance %s is not deleted" % db_instance_name)
    except ClientError as boto_client_error:
        if boto_client_error.response["Error"]["Code"] in "DBInstanceNotFound":
            context.logger.info(f"DB instance %s is deleted" % db_instance_name)
        else:
            raise boto_client_error
