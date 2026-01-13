"""General constants for the project."""

import datetime

from pydantic import UUID4

from ygg.core import config

_DOCS_FOLDER_ = config.DOCS_FOLDER
_YGG_DOC_EXTENSION_ = ".md"

DATA_TYPE_DEFINITIONS = {
    "string": {"logical_implementation": str, "physical_implementation": "VARCHAR"},
    "text": {"logical_implementation": str, "physical_implementation": "TEXT"},
    "integer": {"logical_implementation": int, "physical_implementation": "INTEGER"},
    "bigint": {"logical_implementation": int, "physical_implementation": "BIGINT"},
    "float": {"logical_implementation": float, "physical_implementation": "FLOAT"},
    "decimal": {"logical_implementation": float, "physical_implementation": "DECIMAL"},
    "boolean": {"logical_implementation": bool, "physical_implementation": "BOOLEAN"},
    "date": {"logical_implementation": datetime.date, "physical_implementation": "DATE"},
    "datetime": {"logical_implementation": datetime.datetime, "physical_implementation": "DATETIME"},
    "timestamp": {"logical_implementation": datetime.datetime, "physical_implementation": "TIMESTAMP"},
    "timestamp_ltz": {"logical_implementation": datetime.datetime, "physical_implementation": "TIMESTAMP_LTZ"},
    "timestamp_ntz": {"logical_implementation": datetime.datetime, "physical_implementation": "TIMESTAMP_NTZ"},
    "timestamp_ns": {"logical_implementation": datetime.datetime, "physical_implementation": "TIMESTAMP_NS"},
    "timestamp_s": {"logical_implementation": datetime.datetime, "physical_implementation": "TIMESTAMP_S"},
    "uuid": {"logical_implementation": str, "physical_implementation": "UUID"},
    "uuid4": {"logical_implementation": UUID4, "physical_implementation": "UUID"},
    "json": {"logical_implementation": dict, "physical_implementation": "JSON"},
    "array": {"logical_implementation": list, "physical_implementation": "ARRAY"},
}
