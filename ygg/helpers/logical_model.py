from typing import Any, Literal, Type

from pydantic import BaseModel, ConfigDict, Field


class YggBaseModel(BaseModel):
    """Base data-models for Ygg data models."""

    model_config = ConfigDict(use_enum_values=True)


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
