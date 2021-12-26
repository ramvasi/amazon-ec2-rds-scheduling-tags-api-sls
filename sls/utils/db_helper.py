# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring

from sls.utils.exceptions import InvalidParameter


def get_rds_name_type(db_identifier):
    """
    Split the DB identifier and rds name and type [instance/cluster]

    Args:
        db_identifier:

    Returns:
        Tuple of rds_name & rds_type
    """
    index = db_identifier.find("-")
    if index != -1:
        rds_name = db_identifier[index + 1:]
        rds_type = db_identifier[:index]
    else:
        raise InvalidParameter("Invalid db name parameter format")
    if rds_type not in ["instance", "cluster"]:
        raise InvalidParameter("Invalid parameter. Only instance and cluster supported for db type")
    return rds_name.lower(), rds_type.lower()
