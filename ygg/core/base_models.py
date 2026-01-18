"""Ygg Base Model."""

from typing import Any, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

import ygg.core.enums as enums
import ygg.core.odcs_fields as odcs_fields
from ygg.core.odcs_fields import AuthoritativeDefinitionField


class YggBaseModel(BaseModel):
    """Base data-models for Ygg data models."""

    model_config = ConfigDict(use_enum_values=True)


class YggDataContractElementSchema(YggBaseModel):
    """A list of elements within the schema to be cataloged."""

    id_: odcs_fields.StableId = Field(default=None, alias="id")
    name: str = Field(min_length=5)
    physical_name: Optional[str] = Field(default=None, alias="physicalName")
    physical_type: Optional[Union[enums.YggEntityType, str]] = Field(default=None, alias="physicalType")
    description: Optional[str] = Field(default=None)
    business_name: Optional[str] = Field(default=None, alias="businessName")
    authoritative_definitions: AuthoritativeDefinitionField = Field(alias="authoritativeDefinitions")
    tags: odcs_fields.TagsField
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None)


class YggDataContractPropertiesSchema(YggDataContractElementSchema):
    """A list of elements within the schema to be cataloged."""

    primary_key: Optional[bool] = Field(default=False, alias="primaryKey")
    primary_key_position: Optional[int] = Field(default=None, alias="primaryKey")
    logical_type: Optional[enums.YggLogicalDataTypes] = Field(default=None, alias="logicalType")
    logical_type_options: Optional[dict] = Field(default=None, alias="logicalTypeOptions")
    required: Optional[bool] = Field(default=False)
    unique: Optional[bool] = Field(default=False)
    partitioned: Optional[bool] = Field(default=False)
    partition_key_position: Optional[int] = Field(default=None, alias="partitionKeyPosition")
    classification: Optional[str] = Field(default=None)
    encrypted_name: Optional[str] = Field(default=None, alias="encryptedName")
    transform_source_objects: Optional[list[str]] = Field(default=None, alias="transformSourceObjects")
    transform_logic: Optional[str] = Field(default=None, alias="transformLogic")
    transform_description: Optional[str] = Field(default=None, alias="transformDescription")
    examples: Optional[list[str]] = Field(default=None)
    critical_data_element: Optional[bool] = Field(default=False, alias="criticalDataElement")
    items: Optional[list[dict]] = Field(default=None)


class YggDataContractServiceLevelAgreement(YggBaseModel):
    """Service Level Agreement for Data Contract (SLA)."""

    id_: odcs_fields.StableId = Field(default=None, alias="id")
    property: enums.YggDataContractSlaProperty
    value: Union[str, float, int, bool]
    unit: Optional[str] = Field(default=None)
    element: list[str]
    driver: enums.YggDataContractSlaDriver
    description: Optional[str] = Field(default=None)


class YggDataContractServerSchema(YggBaseModel):
    """The servers element describes where the data protected by this data contract is physically located.

    That metadata helps to know where the data is so that a data consumer can discover the data
    and a platform engineer can automate access.
    """

    id_: odcs_fields.StableId = Field(default=None, alias="id")
    type_: enums.YggDataContractServerType = Field(alias="type")
    description: Optional[str] = Field(default=None)
    environment: enums.YggDataContractServerEnvironment
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None)
    server: odcs_fields.StableId = Field(default=None)
    database_name: odcs_fields.StableId = Field(alias="database")
    database_schema: odcs_fields.StableId = Field(alias="schema")


class YggDataContractSnowflakeServerSchema(YggDataContractServerSchema):
    """Snowflake Server Schema."""

    model_config = ConfigDict(use_enum_values=True)
    server_type: str = Field(alias="type", default=enums.YggDataContractServerType.SNOWFLAKE)

    host: Optional[AnyUrl] = Field(default=None)
    port: Optional[int] = Field(default=None)
    account: Optional[str] = Field(default=None)
    database: odcs_fields.StableId
    schema_: odcs_fields.StableId = Field(alias="schema")
    warehouse: Optional[str] = Field(default=None)


class YggDataContractDuckDBServerSchema(YggDataContractServerSchema):
    """DuckDB Server Schema."""

    model_config = ConfigDict(use_enum_values=True)
    server_type: str = Field(alias="type", default=enums.YggDataContractServerType.DUCKDB)

    database_name: odcs_fields.StableId = Field(alias="database")
    database_schema: odcs_fields.StableId = Field(alias="schema")


class YggDataContractSchema(YggDataContractElementSchema):
    """A list of elements within the schema to be cataloged."""

    data_granularity_description: Optional[str] = Field(default=None, alias="dataGranularityDescription")
    ygg_flow_type: Optional[enums.YggDataContractGeneralFlowType] = Field(default=None, alias="yggFlowType")
    sla_properties: Optional[list[YggDataContractServiceLevelAgreement]] = Field(default=None, alias="slaProperties")
    server: Optional[str] = Field(default=None)
    properties: list[YggDataContractPropertiesSchema]


class YggDataContract(YggBaseModel):
    """Data Contract."""

    api_version: Optional[Literal["v3.1.0"]] = Field(alias="apiVersion", default="v3.1.0")
    kind: Literal["DataContract"] = Field(default="DataContract")
    id_: odcs_fields.StableId = Field(default=None, alias="id")
    name: odcs_fields.StableId = Field(default=None, max_length=255)
    tenant: odcs_fields.StableId = Field(default=None, max_length=64)
    domain: odcs_fields.StableId = Field(default=None, max_length=64)
    version: Optional[odcs_fields.SemanticalVersionField] = Field(default="0.0.1")
    status: Optional[enums.YggDataContractStatus] = Field(default=enums.YggDataContractStatus.DRAFT)
    tags: odcs_fields.TagsField
    data_product: str = Field(alias="dataProduct", max_length=255)

    authoritative_definitions: AuthoritativeDefinitionField = Field(alias="authoritativeDefinitions")
    description: Any = Field(title="Description")

    schema_: list[YggDataContractSchema] = Field(alias="schema")
    servers: Optional[list[YggDataContractServerSchema]] = Field(default=None)
    sla_properties: Optional[YggDataContractServiceLevelAgreement] = Field(default=None, alias="slaProperties")
    ygg_flow_type: enums.YggDataContractGeneralFlowType = Field(alias="yggFlowType")


if __name__ == "__main__":
    from ygg.utils.yaml_utils import get_yaml_content

    yc = get_yaml_content("../../dev/file1.yaml")
    print(yc)
    i = YggDataContract(**yc)

    print(i.servers)
    # print(i)
