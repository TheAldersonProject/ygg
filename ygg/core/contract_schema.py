"""Data Contract Schema and Schema Property Implementation."""

from typing import Any, ClassVar, Optional, Self, Union

from pydantic import Field

import ygg.core.commons as commons
import ygg.core.odcs_fields as odcs_fields
from ygg.core.odcs_fields import AuthoritativeDefinitionField


class YggDataContractSchemaProperty(commons.YggBaseModel):
    """A list of elements within the schema to be cataloged."""

    TABLE_NAME: ClassVar[str] = "contract_schema_property"

    id: odcs_fields.StableId = Field(default=None, alias="id")
    physical_name: Optional[str] = Field(default=None, alias="physicalName")
    physical_type: Optional[Union[commons.YggEntityType, str]] = Field(default=None, alias="physicalType")
    description: Optional[str] = Field(default=None)
    business_name: Optional[str] = Field(default=None, alias="businessName")
    authoritative_definitions: AuthoritativeDefinitionField = Field(alias="authoritativeDefinitions")
    # PLACEHOLDER for quality
    tags: odcs_fields.TagsField
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None, alias="customProperties")

    property_name: str = Field(min_length=5, alias="name")
    primary_key: Optional[bool] = Field(default=False, alias="primaryKey")
    primary_key_position: Optional[int] = Field(default=None, alias="primaryKey")
    logical_type: Optional[commons.YggLogicalDataTypes] = Field(default=None, alias="logicalType")
    # PLACEHOLDER for logical type options
    is_required: Optional[bool] = Field(default=False, alias="required")
    is_unique: Optional[bool] = Field(default=False, alias="unique")
    is_partitioned: Optional[bool] = Field(default=False, alias="partitioned")
    partition_key_position: Optional[int] = Field(default=None, alias="partitionKeyPosition")
    classification: Optional[str] = Field(default=None)
    encrypted_name: Optional[str] = Field(default=None, alias="encryptedName")
    # PLACEHOLDER for transform source objects
    # PLACEHOLDER for transform logic
    # PLACEHOLDER for transform description
    examples: Optional[list[str]] = Field(default=None)
    critical_data_element: Optional[bool] = Field(default=False, alias="criticalDataElement")
    # PLACEHOLDER for items


class YggDataContractSchema(commons.YggBaseModel):
    """A list of elements within the schema to be cataloged."""

    id: odcs_fields.StableId = Field(default=None, alias="id")
    physical_name: Optional[str] = Field(default=None, alias="physicalName")
    physical_type: Optional[Union[commons.YggEntityType, str]] = Field(default=None, alias="physicalType")
    description: Optional[str] = Field(default=None)
    business_name: Optional[str] = Field(default=None, alias="businessName")
    authoritative_definitions: AuthoritativeDefinitionField = Field(alias="authoritativeDefinitions")
    tags: odcs_fields.TagsField
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None, alias="customProperties")

    schema_name: str = Field(min_length=5, alias="name")
    data_granularity_description: Optional[str] = Field(default=None, alias="dataGranularityDescription")
    ygg_flow_type: Optional[commons.YggDataContractGeneralFlowType] = Field(default=None, alias="yggFlowType")
    # not in the standard: sla_properties: Optional[list[sla.YggDataContractSchemaSla]] = Field(default=None, alias="slaProperties")
    server_name: Optional[str] = Field(default=None, alias="server")
    properties: list[YggDataContractSchemaProperty]

    contract_id: odcs_fields.StableId = Field(default=None)
    contract_version: odcs_fields.SemanticalVersionField = Field(default=None)

    TABLE_NAME: ClassVar[str] = "contract_schema"
    IGNORE_ON_INSERT: ClassVar[list[str]] = ["properties"]

    def model_hydrate(self, contract_id: odcs_fields.StableId, contract_version: odcs_fields.SemanticalVersionField):
        """Hydrate the model with the contract_id and contract_version."""

        if not self.contract_id or not self.contract_version:
            raise ValueError("Contract ID and version cannot be empty.")

        self.contract_id = contract_id
        self.contract_version = contract_version

    def get_upsert_dml(
        self, contract_id: odcs_fields.StableId, contract_version: odcs_fields.SemanticalVersionField
    ) -> Union[str, Any]:
        """Generates the insert DML for the schema."""

        self.model_hydrate(contract_id=contract_id, contract_version=contract_version)

        me: Self = [k for k in self.model_fields if k not in self.IGNORE_ON_INSERT]
        upsert_dml: str = (
            f"""insert into {self.TABLE_NAME} ({", ".join(me.keys())}) values ({", ".join(["?"] * len(me))})"""
        )

        insert_values: list[Any] = [getattr(self, k) for k in me]

        return upsert_dml, insert_values
