"""ODCS fields for Ygg Implementation."""

import datetime
from typing import Annotated, Optional, Union

from pydantic import Field

from ygg.helpers.logical_data_models import YggBaseModel

StableId = Annotated[
    str,
    Field(pattern=r"^[A-Za-z0-9_-]+$"),
]


class AuthoritativeDefinition(YggBaseModel):
    """Authoritative Definition."""

    id: str = Field(alias="id")
    url: str = Field(description="URL to the authority.")
    type: str
    description: Optional[str]


class Description(YggBaseModel):
    """Authoritative Definition."""

    usage: str
    purpose: str
    limitations: str


class CustomProperty(YggBaseModel):
    """Custom Property"""

    id: StableId = Field(default=None)
    property: str
    value: Union[str, float, int, bool, list, dict]
    description: Optional[str]


Tags = Annotated[
    Optional[list[str]],
    Field(),
]


StructuredName = Annotated[
    Optional[str],
    Field(pattern=r"^[A-Za-z0-9_-]+$"),
]


CustomProperties = Annotated[
    Optional[list[CustomProperty]],
    Field(
        description="List of custom properties that are not part of the standard.",
    ),
]

SemanticalVersion = Annotated[
    Optional[str],
    Field(
        pattern=r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    ),
]


AuthoritativeDefinitions = Annotated[Optional[list[AuthoritativeDefinition]], Field()]

StructuredDescription = Annotated[Optional[Description], Field()]

DATA_TYPES: dict = {
    "Tags": {"logical": {"type": Tags}, "physical": {"type": "VARCHAR[]"}},
    "SemanticalVersion": {
        "logical": {
            "type": SemanticalVersion,
        },
        "physical": {
            "type": "VARCHAR",
            "pattern": r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
        },
    },
    "CustomProperties": {
        "logical": {"type": CustomProperties},
        "physical": {
            "type": "STRUCT(id VARCHAR, property VARCHAR, value VARCHAR, description VARCHAR)",
        },
    },
    "AuthoritativeDefinitions": {
        "logical": {
            "type": AuthoritativeDefinitions,
        },
        "physical": {
            "type": "STRUCT(id VARCHAR, url VARCHAR, type VARCHAR, description VARCHAR)[]"
        },
    },
    "StructuredDescription": {
        "logical": {
            "type": StructuredDescription,
        },
        "physical": {
            "type": "STRUCT(purpose VARCHAR, limitations VARCHAR, usage VARCHAR)"
        },
    },
    "StructuredName": {
        "logical": {
            "type": StructuredName,
        },
        "physical": {
            "pattern": r"^[a-zA-Z0-9_]+$",
            "type": "VARCHAR",
        },
    },
    "StableId": {
        "logical": {"type": StableId},
        "physical": {
            "pattern": r"^[a-zA-Z0-9_-]+$",
            "type": "VARCHAR",
        },
    },
    "string": {"logical": {"type": str}, "physical": {"type": "VARCHAR"}},
    "integer": {"logical": {"type": int}, "physical": {"type": "BIGINT"}},
    "boolean": {"logical": {"type": bool}, "physical": {"type": "BOOLEAN"}},
    "list_of_strings": {
        "logical": {"type": list[str]},
        "physical": {"type": "VARCHAR[]"},
    },
    "timestamp": {
        "logical": {
            "type": datetime.datetime,
        },
        "physical": {"type": "TIMESTAMPTZ"},
    },
}


def get_data_type(data_type: str, of_type: str) -> dict:
    """Get the data type."""

    return DATA_TYPES.get(data_type, {}).get(of_type, None)
