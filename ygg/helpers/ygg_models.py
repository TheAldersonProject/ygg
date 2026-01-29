"""Ygg Models."""

from pydantic import Field

from ygg.core.dynamic_models_factory import YggBaseModel


class TargetContractSchemaPropertyMap(YggBaseModel):
    """Map for the factory for creating target contract schema properties."""

    id: str = Field(..., description="Unique identifier for the target contract schema property")
    record_hash: str = Field(..., description="Hash of the target contract schema property record")
    name: str = Field(..., description="Name of the target contract schema property")
    description: str = Field(..., description="Description of the target contract schema property")
    physical_type: str = Field(..., description="Physical type of the target contract schema property")
    is_key: bool = Field(..., description="Whether the target contract schema property is a key")
    is_unique: bool = Field(..., description="Whether the target contract schema property is unique")
    is_required: bool = Field(..., description="Whether the target contract schema property is required")


class TargetContractSchemaMap(YggBaseModel):
    """Map for the factory for creating target contract schemas."""

    id: str = Field(..., description="Unique identifier for the target contract schema")
    record_hash: str = Field(..., description="Hash of the target contract schema record")
    entity: str = Field(..., description="Entity name of the target contract schema")
    physical_type: str = Field(..., description="Physical type of the target contract schema")
    contract_id: str = Field(..., description="ID of the target contract")
    contract_record_hash: str = Field(..., description="Hash of the target contract record")
    create_infrastructure_ddl: str | None = Field(default=None, description="DDL to create the target contract schema")
    properties: list[TargetContractSchemaPropertyMap] = Field(
        ..., description="List of target contract schema properties"
    )


class TargetContractMap(YggBaseModel):
    """Map for the factory for creating target contracts."""

    id: str = Field(..., description="Unique identifier for the target contract")
    record_hash: str = Field(..., description="Hash of the target contract record")
    version: str = Field(..., description="Version of the target contract")
    catalog: str = Field(..., description="URL to the target contract catalog")
    catalog_schema: str = Field(..., description="Schema of the target contract")
    schemas: list[TargetContractSchemaMap] = Field(..., description="List of target contract schemas")
