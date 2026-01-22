"""ODCS fields for Ygg Implementation."""

from typing import Annotated, Optional, Union

from pydantic import BaseModel, Field

Tags = Annotated[
    Optional[list[str]],
    Field(default=None),
]

StableId = Annotated[
    str,
    Field(pattern=r"^[A-Za-z0-9_-]+$"),
]

StructuredName = Annotated[
    str,
    Field(pattern=r"^[A-Za-z0-9_-]+$"),
]


class CustomProperty(BaseModel):
    """Custom Property"""

    id: StableId = Field(default=None)
    property: str
    value: Union[str, float, int, bool, list, dict]
    description: Optional[str]


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


class AuthoritativeDefinition(BaseModel):
    """Authoritative Definition."""

    id: str = Field(alias="id")
    url: str = Field(description="URL to the authority.")
    type: str
    description: Optional[str]


class Description(BaseModel):
    """Authoritative Definition."""

    usage: str
    purpose: str
    limitations: str


AuthoritativeDefinitions = Annotated[Optional[list[AuthoritativeDefinition]], Field(default=None)]

StructuredDescription = Annotated[Optional[Description], Field(default=None)]
