"""ODCS Common Data Structures."""

import uuid
from enum import Enum
from typing import Annotated, Any, Optional, Union

from pydantic import UUID4, BeforeValidator, Field

from ygg.core import YggBaseModel
from ygg.core.model_parser import AuthoritativeDefinition


class ApiVersion(Enum):
    """Defines the ApiVersion Data Model."""

    V_3_1_0 = "v3.1.0"


class LogicalDataTypes(Enum):
    """Defines the Custom Property Data Types."""

    STRING = "string"
    INTEGER = "integer"
    BIGINT = "bigint"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    DECIMAL = "decimal"
    URI = "uri"
    UUID = "uuid"
    FLOAT = "float"
    JSON = "json"


class PhysicalTypeSchemaObject(Enum):
    """Defines the Physical Type Schema Data Model."""

    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    TOPIC = "topic"


class CustomProperty(YggBaseModel):
    """Defines the CustomProperty object Data Model."""

    id: Optional[Union[str, UUID4]] = Field(
        default=uuid.uuid4,
    )
    key: str
    # data_type: LogicalDataTypes = Field(default=LogicalDataTypes.STRING)
    value: Any
    description: Optional[str]


def _enforce_custom_property(v: Any) -> Union[list[AuthoritativeDefinition], None]:
    """Enforces the custom property to be a list of CustomProperty objects."""

    if not v:
        return []

    elif isinstance(v, CustomProperty):
        return [v]

    elif isinstance(v, dict):
        return [CustomProperty(**v)]

    return v


CustomPropertyField = Annotated[
    Optional[list[CustomProperty]],
    BeforeValidator(_enforce_custom_property),
    Field(default=None),
]


class ObjectDescription(YggBaseModel):
    """Defines the Description object Data Model."""

    purpose: str = Field(
        title="Purpose", description="Intended purpose for the provided data."
    )
    limitations: str = Field(
        title="limitations",
        description="Technical, compliance, and legal limitations for data use.",
    )
    usage: str = Field(title="Usage", description="Recommended usage of the data.")
    authoritative_definitions: Optional[
        Union[list[AuthoritativeDefinition], AuthoritativeDefinition]
    ] = Field(
        title="Authoritative Definitions",
        default=None,
        alias="authoritativeDefinitions",
    )
    custom_properties: Optional[Union[list[CustomProperty], CustomProperty]] = Field(
        title="Custom Properties", default=None, alias="customProperties"
    )
