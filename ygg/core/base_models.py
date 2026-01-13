"""Ygg Base Model."""

from typing import Annotated, Any, Optional, Union

from pydantic import UUID4, AnyUrl, BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from ygg.core import helper
from ygg.core.enums import YggEntityType


class YggBaseModel(BaseModel):
    """Base data-models for Ygg data models."""

    model_config = ConfigDict(use_enum_values=True)


class AuthoritativeDefinition(YggBaseModel):
    """
    Represents an authoritative definition within the system, integrating unique identifiers,
    associated URLs, and other descriptive metadata. Designed to ensure data consistency
    and streamline the handling of URL and optional metadata.

    This model enforces proper validation of unique identifiers through field validators and
    enables flexible input handling through optional types and constructs.

    :ivar id: The unique identifier of the authoritative definition. If not provided,
              a UUID4 is generated automatically.
    :type id: Optional[Union[str, UUID4]]
    :ivar url: The URL associated with the authoritative definition.
    :type url: AnyUrl
    :ivar type: The type or category of the authoritative definition.
    :type type: Optional[str]
    :ivar description: A descriptive text providing additional information about the
                       authoritative definition.
    :type description: Optional[str]
    """

    id: Optional[Union[str, UUID4]]
    url: AnyUrl
    type: Optional[str]
    description: Optional[str]

    @field_validator("id", mode="before")
    @classmethod
    def enforce_id(cls, v: Any) -> UUID4:
        """Maps the logical data type."""
        if not v or not v.strip():
            return helper.generate_uuid4()

        return v


AuthoritativeDefinitionField = Annotated[
    Optional[list[AuthoritativeDefinition]],
    BeforeValidator(helper.enforce_authoritative_definition),
    Field(
        default=None,
        title="Authoritative Definitions",
        description="""List of links to sources that provide more details on the element;""",
    ),
]


class YggDataModelAttributes(YggBaseModel):
    """
    Represents the attributes of a Yggdrasil data model.

    This class provides a structured representation of metadata associated with a Yggdrasil
    data entity. It includes details such as the catalog name, schema name, entity name,
    entity type, description of the entity, and authoritative definitions.

    :ivar catalog: Catalog name.
    :type catalog: str
    :ivar schema_: Schema name.
    :type schema_: str
    :ivar entity: Entity name.
    :type entity: str
    :ivar entity_type: Type of the entity. Possible examples include
        `YggEntityType.TABLE` and `YggEntityType.VIEW`.
    :type entity_type: YggEntityType
    :ivar description: Entity description.
    :type description: str
    :ivar authoritative_definitions: Contains authoritative definitions pertaining to
        the entity.
    :type authoritative_definitions: AuthoritativeDefinitionField
    """

    catalog: str = Field(title="Catalog", description="Catalog name.")
    schema_: str = Field(alias="schema", title="Schema", description="Schema name.")
    entity: str = Field(title="Entity", description="Entity name.")
    entity_type: YggEntityType = Field(
        default=YggEntityType.TABLE,
        title="Entity",
        description="Entity name.",
        alias="entity-type",
        examples=[YggEntityType.TABLE, YggEntityType.VIEW],
    )
    description: str = Field(title="Description", description="Entity description.")
    authoritative_definitions: AuthoritativeDefinitionField = Field(default=None)


class _YggPhysicalPropertyConstraints(YggBaseModel):
    """
    Represents constraints and metadata for physical property definitions
    in the Ygg system.

    This class is designed to store and manage metadata related to
    physical properties, including whether a specific property serves
    as part of a Primary Key, and its position within the Primary Key
    if applicable. It primarily serves as a base model for handling
    these constraints consistently across the system.

    :ivar primary_key: Indicates whether the property is a Primary Key.
    :type primary_key: Optional[bool]
    :ivar primary_key_position: Specifies the position of the property
        within the Primary Key fields. None if the field is not part
        of a Primary Key.
    :type primary_key_position: Optional[int]
    """

    primary_key: Optional[bool] = Field(
        default=False, title="Primary Key", description="Whether the property is a Primary Key."
    )
    primary_key_position: Optional[int] = Field(
        default=None,
        title="Primary Key Position",
        description="Defines the position of the field within the Primary Key.",
    )


class _YggDataModelPropertyBase(YggBaseModel):
    """
    Represents a base model for Yggdrasil data model properties.

    This class is used to define the basic metadata and structure of a
    property within a Yggdrasil data model. It includes attributes such
    as the property's name, data type, description, and additional options
    such as whether the property is required or has a default value.

    :ivar name: The name of the property.
    :type name: str
    :ivar data_type: The data type of the property.
    :type data_type: str
    :ivar description: A brief description of the property's purpose or usage.
    :type description: str
    :ivar required: Specifies whether the property is required (True or False).
        Defaults to False if not specified.
    :type required: Optional[bool]
    :ivar default_value: The default value of the property if applicable.
        Defaults to None if not specified.
    :type default_value: Optional[str]
    """

    name: str
    data_type: str
    description: str
    required: Optional[bool] = Field(default=False)
    default_value: Optional[str] = Field(default=None)


class YggLogicalImplementation(_YggDataModelPropertyBase):
    """
    Represents the logical implementation layer for the Ygg data model property.

    This class is used to define and manage logical properties of the Ygg data
    model with attributes for customization and additional metadata. It supports
    aliasing, title designation, and optional coercion of numerical values to
    strings.

    :ivar name: The name of the property as used internally.
    :type name: str
    :ivar literal: Optional list of literal values associated with the property.
    :type literal: list[str], optional
    :ivar alias: An optional alias for the property name.
    :type alias: str, optional
    :ivar title: An optional title providing additional description of the property.
    :type title: str, optional
    :ivar coerce_numbers_to_str: Indicates whether numerical values should be
        coerced into string format. Defaults to False.
    :type coerce_numbers_to_str: bool, optional
    """

    name: str = Field(alias="property_name")
    literal: Optional[list[str]] = Field(default=None)
    alias: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    coerce_numbers_to_str: Optional[bool] = Field(default=False)


class YggPhysicalImplementation(_YggDataModelPropertyBase):
    """
    Represents the physical implementation of a Ygg data model property.

    This class is used to define the physical characteristics of a data model
    property within the Ygg system. It includes attributes such as the name,
    size, precision, and constraints of the property. The primary purpose of
    this class is to encapsulate metadata needed to accurately implement and
    model a property within the system's physical layer.

    :ivar name: The name of the column in the physical data model.
    :type name: str
    :ivar size: The size of the data model property. This is optional.
    :type size: Optional[int]
    :ivar precision: The level of precision for the property, if applicable.
    :type precision: Optional[int]
    :ivar constraints: Constraints or limitations associated with the property, if any.
    :type constraints: Optional[_YggPhysicalPropertyConstraints]
    """

    name: str = Field(alias="column_name")
    size: Optional[int] = Field(default=None)
    precision: Optional[int] = Field(default=None)
    constraints: Optional[_YggPhysicalPropertyConstraints] = Field(default=None)


class YggDataModelProperty(YggBaseModel):
    """
    Represents a data model property with logical and physical implementations and optional examples.

    This class encapsulates the details of a data model property, including its logical
    implementation, physical implementation, and examples for reference. It allows users to
    define and retrieve metadata associated with a specific data model property.

    :ivar logical_implementation: Logical implementation associated with the data
        model property that defines its abstract behavior or logic.
    :type logical_implementation: Optional[YggLogicalImplementation]

    :ivar physical_implementation: Physical implementation associated with the data
        model property that defines its concrete realization or structure.
    :type physical_implementation: Optional[YggPhysicalImplementation]

    :ivar examples: List of example values or entries associated with the data model
        property, providing reference or guidance for its usage.
    :type examples: Optional[list[str]]
    """

    logical_implementation: Optional[YggLogicalImplementation] = Field(default=None)
    physical_implementation: Optional[YggPhysicalImplementation] = Field(default=None)
    examples: Optional[list[str]] = Field(default=None)
