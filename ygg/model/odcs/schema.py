"""Open Data Contract Schema Section Data Model."""

from typing import Optional, Self, Union

from pydantic import UUID4, Field

from ygg.core import YggBaseModel

from .data_quality import DataQuality
from .odcs_commons import (
    AuthoritativeDefinitionField,
    CustomProperty,
    LogicalDataTypes,
    PhysicalTypeSchemaObject,
)
from .reference import ReferenceBase, ReferenceObject


class Element(YggBaseModel):
    """This section describes the schema of the data contract.

    It is the support for data quality, which is detailed in the next section.
    Schema supports both a business representation of your data and a physical implementation.
    """

    id: Optional[Union[str, UUID4]] = Field(
        default=None,
        title="ID",
        description="""A unique identifier for the element used to create stable, refactor-safe references.
        Recommended for elements that will be referenced. See References for more details.
        """,
    )
    name: str = Field(title="Name", description="Name of the element.")
    physical_name: Optional[str] = Field(
        default=None, title="Physical Name", description="Physical name."
    )
    physical_type: Optional[Union[str, PhysicalTypeSchemaObject, LogicalDataTypes]] = (
        Field(
            default=None,
            title="Physical Type",
            description="""The physical element data type in the data source.
        For objects: table, view, topic, file. For properties: VARCHAR(2), DOUBLE, INT, etc""",
        )
    )
    description: Optional[str] = Field(
        default=None, title="Description", description="Description of the element."
    )
    business_name: Optional[str] = Field(
        default=None,
        title="Business Name",
        description="The business name of the element.",
    )
    authoritative_definitions: AuthoritativeDefinitionField = Field(default=None)

    quality: Optional[list[DataQuality]] = Field(
        default=None, title="Quality", description="List of data quality attributes."
    )

    tags: Optional[list[str]] = Field(
        default=None,
        title="Tags",
        description="""A list of tags that may be assigned to the elements (object or property);
        the tags keyword may appear at any level. Tags may be used to better categorize an element.
        """,
        examples=["finance", "sales", "marketing", "sensitive"],
    )
    custom_properties: Optional[Union[list[CustomProperty], CustomProperty]] = Field(
        default=None,
        title="Custom Properties",
        description="Custom properties that are not part of the standard.",
    )


class SchemaProperty(Element):
    """Defines the Schema Property Data Model."""

    primary_key: Optional[bool] = Field(default=False)
    primary_key_position: Optional[int] = Field(default=None, ge=1)
    logical_type: Optional[str] = Field(default=None)
    logical_type_options: Optional[dict] = Field(default=None)  # TODO: implement.
    required: Optional[bool] = Field(default=False)
    unique: Optional[bool] = Field(default=False)
    partitioned: Optional[bool] = Field(default=False)
    partition_key_position: Optional[int] = Field(default=None, ge=1)
    classification: Optional[str] = Field(default=None)
    encrypted_name: Optional[str] = Field(default=None)
    transform_source_objects: Optional[list[str]] = Field(default=None)
    transform_logic: Optional[str] = Field(default=None)
    transform_description: Optional[str] = Field(default=None)
    examples: Optional[list[str]] = Field(default=None)
    critical_data_element: Optional[bool] = Field(default=False)
    items: Optional[list[Self]] = Field(default=None)
    relationship: Optional[list[ReferenceBase]] = Field(default=None)


class SchemaObject(Element):
    """Defines the Schema Object Data Model."""

    data_granularity_description: Optional[str] = Field(default=None)
    properties: Optional[list[SchemaProperty]] = Field(default=None)
    relationship: Optional[list[ReferenceObject]] = Field(default=None)
