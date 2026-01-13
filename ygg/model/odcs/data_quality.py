"""Data Quality Data Model."""

from typing import Any, Optional, Union

from pydantic import Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import AuthoritativeDefinitionField, CustomProperty


class DataQuality(YggBaseModel):
    """Defines the Data Quality section Data Model."""

    id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    metric: Optional[str] = Field(default=None)
    rule: Optional[str] = Field(default=None, deprecated="This column has been deprecated. Use metric instead")
    arguments: Optional[dict[str, Any]] = Field(default=None)

    unit: Optional[str] = Field(default=None)
    query: Optional[str] = Field(default=None)
    engine: Optional[str] = Field(default=None)
    implementation: Optional[Union[str, dict[str, Any]]] = Field(default=None)
    dimension: Optional[str] = Field(default=None)
    method: Optional[str] = Field(default=None)
    severity: Optional[str] = Field(default=None)
    business_impact: Optional[str] = Field(default=None)
    custom_properties: Optional[list[CustomProperty]] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)
    authoritative_definitions: AuthoritativeDefinitionField = Field(default=None)
    scheduler: Optional[str] = Field(default=None)
    schedule: Optional[str] = Field(default=None)

    mustBe: Optional[Any] = Field(default=None)
    mustNotBe: Optional[Any] = Field(default=None)
    mustBeGreaterThan: Optional[Union[float, int]] = Field(default=None)
    mustBeGreaterOrEqualTo: Optional[Union[float, int]] = Field(default=None)
    mustBeLessThan: Optional[Union[float, int]] = Field(default=None)
    mustBeLessOrEqualTo: Optional[Union[float, int]] = Field(default=None)
    mustBeBetween: Optional[list[Union[float, int]]] = Field(default=None, max_length=2, min_length=2)
    mustNotBeBetween: Optional[list[Union[float, int]]] = Field(default=None, max_length=2, min_length=2)
