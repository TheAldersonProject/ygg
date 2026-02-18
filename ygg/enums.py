"""Ygg Enums"""

from enum import Enum


class Model(Enum):
    """Contract Models Enum."""

    CONTRACT = "contract"
    SCHEMA = "schema"
    SCHEMA_PROPERTY = "schema_property"
    SERVERS = "servers"
