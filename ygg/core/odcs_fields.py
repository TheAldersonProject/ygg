"""ODCS fields for Ygg Implementation."""

from typing import Annotated, Optional, Union

from pydantic import AnyUrl, BaseModel, Field

TagsField = Annotated[
    Optional[list[str]],
    Field(
        default=None,
        description="A list of tags that may be assigned to the elements (object or property); the tags keyword may appear at any level. Tags may be used to better categorize an element.",
        examples=["finance", "sales", "marketing", "sensitive"],
    ),
]

StableId = Annotated[
    Optional[str],
    Field(
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Stable technical identifier for references. Must be unique within its containing array. Cannot contain special characters ('-', '_' allowed).",
    ),
]


class CustomProperty(BaseModel):
    """Custom Property"""

    id_: StableId = Field(default=None, alias="id")
    property: str
    value: Union[str, float, int, bool, list, dict]
    description: Optional[str]


CustomPropertiesField = Annotated[
    Optional[list[CustomProperty]],
    Field(
        alias="customProperties",
        description="List of custom properties that are not part of the standard.",
    ),
]


ShorthandReferenceField = Annotated[
    Optional[str],
    Field(
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*\\.[A-Za-z_][A-Za-z0-9_]*$",
        description="Shorthand notation using name fields (table_name.column_name)",
    ),
]

SemanticalVersionField = Annotated[
    Optional[str],
    Field(
        pattern=r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
        description="Shorthand notation using name fields (table_name.column_name)",
    ),
]

FullyQualifiedReferenceField = Annotated[
    Optional[str],
    Field(
        default=None,
        pattern=r"^(?:(?:https?:\\/\\/)?[A-Za-z0-9._\\-\\/]+\\.yaml#)?\\/?[A-Za-z_][A-Za-z0-9_]*\\/[A-Za-z0-9_-]+(?:\\/[A-Za-z_][A-Za-z0-9_]*\\/[A-Za-z0-9_-]+)*$",
        description="Fully qualified reference to a schema element.",
    ),
]


class AuthoritativeDefinition(BaseModel):
    """Authoritative Definition."""

    id_: str = Field(alias="id")
    url: AnyUrl = Field(description="URL to the authority.")
    type: str = Field(
        description="Type or category of the authority.",
        examples=["businessDefinition", "transformationImplementation", "videoTutorial", "tutorial", "implementation"],
    )
    description: Optional[str] = Field(description="Description of the authoritative definition for humans.")


AuthoritativeDefinitionField = Annotated[
    Optional[list[AuthoritativeDefinition]],
    Field(default=None),
]
