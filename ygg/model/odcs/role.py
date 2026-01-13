"""Implements the Role Data Model."""

import uuid
from typing import Optional, Union

from pydantic import UUID4, Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import CustomProperty


class Role(YggBaseModel):
    """Defines the Role Data Model."""

    id: Optional[Union[str, UUID4]] = Field(default=uuid.uuid4)
    role: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    access: Optional[str] = Field(default=None)
    first_level_approvers: Optional[str] = Field(default=None)
    second_level_approvers: Optional[str] = Field(default=None)
    custom_properties: Optional[list[CustomProperty]] = Field(default=None)
