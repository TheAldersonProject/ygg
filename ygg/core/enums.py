"""Collection of enums for Ygg."""

from enum import Enum


class YggEntityType(Enum):
    """Defines the Ygg Entity Types."""

    TABLE = "table"
    VIEW = "view"


class YggDataContractStatus(Enum):
    """Defines the Ygg Data Contract Status."""

    ACTIVE = "active"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class YggLogicalDataTypes(Enum):
    """Defines the Custom Property Data Types."""

    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    TIMESTAMP_LTZ = "timestamp_ltz"
    TIMESTAMP_NTZ = "timestamp_ntz"
    UUID = "uuid"
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"
    FLOAT = "float"


class YggDataContractServerType(Enum):
    """Defines the Data Contract Server Types."""

    LOCAL = "local"
    SNOWFLAKE = "snowflake"
    DUCKDB = "duckdb"


class YggDataContractSlaProperty(Enum):
    """Defines the Data Contract Server SLA Properties."""

    AVAILABILITY = "availability"
    LATENCY = "latency"
    RETENTION = "retention"
    THROUGHPUT = "throughput"


class YggDataContractSlaDriver(Enum):
    """Defines the Data Contract Server SLA Drivers."""

    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    ANALYTICS = "analytics"


class YggDataContractGeneralFlowType(Enum):
    """Defines the Flow Type of the Data Contract."""

    INPUT = "input"
    OUTPUT = "output"
    TRANSFORM = "transform"


class YggDataContractServerEnvironment(Enum):
    """Defines the Data Contract Server Environment Types."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    QA = "qa"
    LOCAL = "local"
    GENERAL = "general"
