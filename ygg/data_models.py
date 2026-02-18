"""Ygg Models."""

from typing import Any

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
