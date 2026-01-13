"""Implements the Service Level Agreement Data Model."""

from typing import Optional, Union

from pydantic import Field

from ygg.core import YggBaseModel


class ServiceLevelAgreementProperty(YggBaseModel):
    """Defines the Service Level Agreement Property Data Model."""

    id: Optional[str] = Field(default=None)
    property: Optional[str] = Field(default=None)
    value: Optional[Union[str, float, int, bool]] = Field(default=None)
    value_ext: Optional[Union[str, float, int, bool]] = Field(default=None)
    unit: Optional[str] = Field(default=None)
    element: Optional[str] = Field(default=None)
    driver: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    scheduler: Optional[str] = Field(default=None)
    schedule: Optional[str] = Field(default=None)
