""" custom exceptions for rds metadata api"""


# pylint:disable=R0801

class SecretNotFound(Exception):
    """Secret Not Found exception"""


class NonVPCxKeyExistsWithSameAlias(Exception):
    """Non VPCx Key Exists With Same Alias exception"""


class InvalidAccount(Exception):
    """Invalid account exception"""


class InvalidRegion(Exception):
    """Invalid region exception"""


class Unauthorized(Exception):
    """Unauthorized exception"""


class InvalidParameter(Exception):
    """Parameter not valid"""


class DatabaseNotAvailable(Exception):
    """Database Not Available exception"""


class DatabaseNotFound(Exception):
    """Database Not Found exception"""


class ClusterExists(Exception):
    """Cluster exists"""


class InstanceExists(Exception):
    """Instance exists"""


class SnsTopicNotFound(Exception):
    """Sns topic not found in account"""


class ResourceNotFound(Exception):
    """Resource Not Found exception"""
