"""Ygg Models."""

from enum import Enum
from typing import Any, Literal, Self, Type

from pydantic import BaseModel, ConfigDict, Field

import ygg.utils.ygg_logs as log_utils

logs = log_utils.get_logger()


class YggBaseModel(BaseModel):
    """Dynamic Models Factory Base Model."""

    model_config = ConfigDict(use_enum_values=True)


class SharedModelMixin:
    """Shared Model Mixin."""

    def _model_hydrate(self, hydrate_data: dict) -> None:
        """Hydrate the model."""

        if not hydrate_data:
            return

        me = self
        dct = {k: v for k, v in hydrate_data.items() if k in me.model_fields}  #  type: ignore
        for k, v in dct.items():
            setattr(self, k, v)

    @classmethod
    def inflate(cls, data: dict, model_hydrate: dict | None = None) -> Self:
        """Inflate the model."""

        logs.debug("Inflating Model.", name=cls.__name__)

        model = cls(**data)
        if model_hydrate:
            model._model_hydrate(model_hydrate)

        return model


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


class Model(Enum):
    """Contract Models Enum."""

    CONTRACT = "contract"
    SCHEMA = "schema"
    SCHEMA_PROPERTY = "schema_property"
    SERVERS = "servers"


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

    id: str = Field(
        ..., description="Unique identifier for the target contract schema property"
    )
    record_hash: str = Field(
        ..., description="Hash of the target contract schema property record"
    )
    name: str = Field(..., description="Name of the target contract schema property")
    description: str = Field(
        ..., description="Description of the target contract schema property"
    )
    physical_type: str = Field(
        ..., description="Physical type of the target contract schema property"
    )
    is_key: bool = Field(
        ..., description="Whether the target contract schema property is a key"
    )
    is_unique: bool = Field(
        ..., description="Whether the target contract schema property is unique"
    )
    is_required: bool = Field(
        ..., description="Whether the target contract schema property is required"
    )


class TargetContractSchemaMap(YggBaseModel):
    """Map for the factory for creating target contract schemas."""

    id: str = Field(..., description="Unique identifier for the target contract schema")
    record_hash: str = Field(
        ..., description="Hash of the target contract schema record"
    )
    entity: str = Field(..., description="Entity name of the target contract schema")
    physical_type: str = Field(
        ..., description="Physical type of the target contract schema"
    )
    contract_id: str = Field(..., description="ID of the target contract")
    contract_record_hash: str = Field(
        ..., description="Hash of the target contract record"
    )
    create_infrastructure_ddl: str | None = Field(
        default=None, description="DDL to create the target contract schema"
    )
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
    schemas: list[TargetContractSchemaMap] = Field(
        ..., description="List of target contract schemas"
    )
