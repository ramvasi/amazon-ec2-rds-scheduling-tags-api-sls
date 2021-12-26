"""
    DB setup and cleanup for BDD tests
"""
import threading

from time import perf_counter
from sls.utils_bdd.rds_helper import create_rds_instance, delete_rds_instance, create_rds_cluster, delete_rds_cluster


def create_rds_resource(context, instance_data):
    """

      Args:
          context: bdd context
          instance_data: Json with properties of instance and cluster to create

      """
    start = perf_counter()
    threads = []
    append_to_create_thread(context, instance_data,  threads)

    for thread in threads:
        thread.join()
    context.logger.info(
        f"Time taken to create RDS resources is {(perf_counter() - start) / 60} minutes"
    )


def append_to_create_thread(context, resources, threads):
    """
    Args:
          resources: Json with properties of instance to create
          context: bdd context
          threads: list of thread
    """
    for res in resources:
        resources[res]['VpcSecurityGroupIds'] = context.sg_name
        resources[res]['DBSubnetGroupName'] = context.subnet_name

        thrd = threading.Thread(
            target=get_create_target(resources[res]),
            args=(
                context,
                context.rds_client,
                res,
                resources[res],
            ),
        )
        thrd.start()
        threads.append(thrd)


def is_engine_aurora(instance):
    engine = instance['Engine']
    return 'aurora' in engine


def get_create_target(instance):
    if is_engine_aurora(instance):
        return create_rds_cluster
    else:
        return create_rds_instance


def delete_rds_resource(context, instance_data):
    """

    Args:
        context: bdd context
        instance_data: Json with properties of instance to create
        cluster_data: Json if creating aurora cluster

    """
    start = perf_counter()
    threads = []
    append_to_delete_thread(context, instance_data, threads)
    for thread in threads:
        thread.join()
    context.logger.info(
        f"Time taken to delete RDS resources is {(perf_counter() - start) / 60} minutes"
    )


def append_to_delete_thread(context, resources,  threads):
    for res in resources:
        thrd = threading.Thread(
            target=get_delete_target(resources[res]),
            args=(
                context,
                context.rds_client,
                res,
            ),
        )
        thrd.start()
        threads.append(thrd)


def get_delete_target(instance):
    if is_engine_aurora(instance):
        return delete_rds_cluster
    else:
        return delete_rds_instance
