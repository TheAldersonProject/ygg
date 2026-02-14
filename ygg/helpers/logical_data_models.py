"""Ygg Models."""

from pathlib import Path
from typing import Any, Literal, Type

from pydantic import BaseModel, ConfigDict, Field


class YggBaseModel(BaseModel):
    """Dynamic Models Factory Base Model."""

    model_config = ConfigDict(use_enum_values=True)


class YggConfig(YggBaseModel):
    """Dynamic Models Factory Config."""

    version_file: str
    odcs_version: str
    odcs_schema_file: str
    models: list[str]
    commons: list[dict] | None = Field(default=None)


class ModelProperty(YggBaseModel):
    """Dynamic Models Factory Config."""

    name: str | None = Field(default=None)
    type: str | None = Field(default=None)
    pattern: str | None = Field(default=None)
    default: Any | None = Field(default=None)
    physical_default_function: str | None = Field(default=None)
    unique: bool | None = Field(default=False)
    description: str | None = Field(default=None)
    required: bool | None = Field(default=True)
    primary_key: bool | None = Field(default=False)
    alias: str | None = Field(default=None)
    enum: list | None = Field(default=None)
    odcs_schema: str | None = Field(default=None)
    skip_from_signature: bool = Field(default=False)
    skip_from_physical_model: bool = Field(default=False)
    examples: list[str] | None = Field(default=None)


class ModelSettings(YggBaseModel):
    """Model Settings Model."""

    name: str
    document_path: str
    type: str
    required: bool
    entity_name: str
    entity_type: str
    entity_schema: str
    description: str
    odcs_reference: str
    properties: list[ModelProperty]


class YggModelProperty(YggBaseModel):
    """Ygg model properties."""

    name: str
    type: str
    alias: str
    skip_from_signature: bool = Field(default=False)
    skip_from_physical_model: bool = Field(default=False)
    required: bool | None = Field(default=True)
    primary_key: bool | None = Field(default=False)
    primary_key_position: int | None = Field(default=None)
    unique: bool | None = Field(default=False)
    pattern: str | None = Field(default=None)
    odcs_schema: str | None = Field(default=None)
    enum: list[Any] | None = Field(default=None)
    properties: Any | None = Field(default=None)
    items: Any | None = Field(default=None)
    default: Any | None = Field(default=None)
    physical_default_function: Any | None = Field(default=None)
    description: str | None = Field(default=None)
    examples: list[Any] | None = Field(default=None)


class YggModelConfig(YggBaseModel):
    """Ygg model properties."""

    document_path: str | None = Field(default=None)
    type: str
    required: bool | None = Field(default=True)
    entity_name: str
    entity_type: Literal["table", "view"]
    entity_schema: str
    description: str
    odcs_reference: str


class YggModel(YggBaseModel):
    """Ygg model."""

    name: str
    version: str
    config: YggModelConfig
    properties: list[YggModelProperty]
    instance: Type[YggBaseModel] | None = Field(default=None)


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


class PolyglotDatabaseConfig(YggBaseModel):
    """Polyglot Database Config"""

    host: str | None = Field(default=None, description="Database host")
    db_name: str | None = Field(default=None, description="Database name")
    port: str | int | None = Field(default=None, description="Database port")
    user: str | None = Field(default=None, description="Database user")
    password: str | None = Field(default=None, description="Database password")
    path: str | Path | None = Field(default=None, description="Database path")
    auto_commit: bool | None = Field(default=True, description="Auto commit")


class PolyglotEntityColumnDataType(YggBaseModel):
    """Polyglot Db Entity Column Data Type"""

    data_type_name: str = Field(..., description="Column data type")
    duck_db_type: str = Field(..., description="DuckDb data type")
    duck_db_regex_pattern: str | None = Field(default=None, description="DuckDb regex pattern")
    duck_lake_type: str = Field(..., description="DuckLake data type")


class PolyglotEntityColumn(YggBaseModel):
    """Polyglot Db Entity Column"""

    name: str = Field(..., description="Column name")
    data_type: PolyglotEntityColumnDataType = Field(..., description="Column data type")
    enum: list | None = Field(default=None)
    comment: str | None = Field(default=None, description="Column comment")
    nullable: bool | None = Field(default=False, description="Whether the column can be null")
    primary_key: bool | None = Field(default=False, description="Whether the column is a primary key")
    unique_key: bool | None = Field(default=False, description="Whether the column is a unique key")
    check_constraint: str | None = Field(default=None, description="Check constraint")
    skip_from_update: bool | None = Field(default=False, description="Whether to skip the column from update")
    default_value: str | Any | None = Field(default=None, description="Default value")
    default_value_function: str | None = Field(default=None, description="Database function for default value")


class PolyglotEntity(YggBaseModel):
    """Polyglot Db Entity"""

    name: str = Field(..., description="Entity name")
    schema_: str = Field(..., description="Entity schema name")
    comment: str | None = Field(default=None, description="Entity comment")
    columns: list[PolyglotEntityColumn] | None = Field(default=None, description="Entity list of columns")


class DuckLakeSetup(YggBaseModel):
    """DuckLake Setup."""

    install_modules: list[str] | str = Field(default_factory=list, description="List of modules to install.")
    load_modules: list[str] | str = Field(default_factory=list, description="List of modules to load.")
    object_storage_secret: str = Field(default=str, description="Object storage secret.")
    catalog_secret: str = Field(default=str, description="Catalog secret.")
    lake_secret: str = Field(default=str, description="DuckLake secret.")
    attach_ducklake_catalog: str = Field(default=str, description="DuckLake catalog to attach.")
