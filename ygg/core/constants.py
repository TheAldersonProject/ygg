"""General constants for the project."""

import datetime
from uuid import UUID

from pydantic import UUID4

DATA_TYPE_DEFINITIONS = {
    "string": {"logical": str, "physical": "VARCHAR"},
    "text": {"logical": str, "physical": "TEXT"},
    "integer": {"logical": int, "physical": "INTEGER"},
    "bigint": {"logical": int, "physical": "BIGINT"},
    "float": {"logical": float, "physical": "FLOAT"},
    "decimal": {"logical": float, "physical": "DECIMAL"},
    "boolean": {"logical": bool, "physical": "BOOLEAN"},
    "date": {"logical": datetime.date, "physical": "DATE"},
    "datetime": {"logical": datetime.datetime, "physical": "DATETIME"},
    "timestamp": {"logical": datetime.datetime, "physical": "TIMESTAMP"},
    "timestamp_ltz": {"logical": datetime.datetime, "physical": "TIMESTAMP_LTZ"},
    "timestamp_ntz": {"logical": datetime.datetime, "physical": "TIMESTAMP_NTZ"},
    "timestamp_ns": {"logical": datetime.datetime, "physical": "TIMESTAMP_NS"},
    "timestamp_s": {"logical": datetime.datetime, "physical": "TIMESTAMP_S"},
    "uuid": {"logical": UUID, "physical": "UUID"},
    "uuid4": {"logical": UUID4, "physical": "UUID"},
    "json": {"logical": dict, "physical": "JSON"},
    "array": {"logical": list, "physical": "ARRAY"},
}
