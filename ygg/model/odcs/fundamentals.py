"""Open Data Contract Fundamentals Section Data Model."""

import uuid
from typing import Literal, Optional, Union

from pydantic import UUID4, Field

from ygg.core import YggBaseModel

from .odcs_commons import ApiVersion, AuthoritativeDefinitionField, ObjectDescription


class Fundamentals(YggBaseModel):
    """This section contains general information about the contract.

    Fundamentals were also called demographics in early versions of ODCS.
    """

    api_version: ApiVersion = Field(
        default=ApiVersion.V_3_1_0,
        coerce_numbers_to_str=True,
        alias="apiVersion",
        title="Standard version",
        description="Version of the standard used to build data contract. Default value is v3.1.0.",
    )
    kind: Literal["DataContract"] = Field(
        default="DataContract",
        const=True,
        frozen=True,
        title="Kind",
        description="The kind of file this is. Valid value is DataContract.",
    )
    id: Union[str, UUID4] = Field(
        default=uuid.uuid4,
        title="ID",
        description="A unique identifier used to reduce the risk of dataset name collisions, such as a UUID.",
    )
    name: Optional[str] = Field(
        default=None, description="Name of the data contract.", title="Name"
    )
    version: str = Field(
        title="Version", description="Current version of the data contract."
    )
    status: str = Field(
        title="Status",
        description="Current status of the data contract.",
        examples=["proposed", "draft", "active", "deprecated", "retired"],
    )
    tenant: Optional[str] = Field(
        default=None,
        title="Tenant",
        description="Indicates the property the data is primarily associated with. Value is case insensitive.",
    )
    tags: list[str] = Field(
        default=[],
        title="Tags",
        description="A list of tags that may be assigned to the elements (object or property); the tags keyword may appear at any level. Tags may be used to better categorize an element.",
        example=["finance", "sales", "marketing", "sensitive"],
    )
    domain: Optional[str] = Field(
        default=None, title="Domain", description="Name of the logical data domain."
    )

    data_product: Optional[str] = Field(
        title="Data Product", description="Name of the product.", alias="dataProduct"
    )
    authoritative_definitions: AuthoritativeDefinitionField = Field(
        default=None,
        alias="authoritativeDefinitions",
        title="Authoritative Definitions",
        description="List of links to sources that provide more details on the data contract.",
    )
    description: Optional[ObjectDescription] = Field(
        default=None,
        title="Description",
        description="Object containing the descriptions.",
    )
