"""Implements the Support Data Model."""

from typing import Optional

from pydantic import Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import CustomProperty


class Support(YggBaseModel):
    """Defines the Support Data Model."""

    id: Optional[str] = Field(default=None)
    channel: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    tool: Optional[str] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    invitation_url: Optional[str] = Field(default=None)
    custom_properties: Optional[list[CustomProperty]] = Field(default=None)
