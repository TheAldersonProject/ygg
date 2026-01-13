"""Implements the Team Data Model."""

from typing import Optional

from pydantic import Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import AuthoritativeDefinitionField, CustomProperty


class TeamMember(YggBaseModel):
    """Defines the Team Member Data Model."""

    id: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)
    dateIn: Optional[str] = Field(default=None)
    dateOut: Optional[str] = Field(default=None)
    replacedByUsername: Optional[str] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)
    custom_properties: Optional[list[CustomProperty]] = Field(default=None)
    authoritative_definitions: AuthoritativeDefinitionField = Field(default=None)


class Team(YggBaseModel):
    """Defines the Team Data Model."""

    id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    members: Optional[list[TeamMember]] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)
    customProperties: Optional[list[CustomProperty]] = Field(default=None)
    authoritative_definitions: AuthoritativeDefinitionField = Field(default=None)
