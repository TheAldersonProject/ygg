"""Implements the Server Data Model."""

import uuid
from typing import Optional, Union

from pydantic import UUID4, Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import CustomProperty
from ygg.model.odcs.role import Role


class Server(YggBaseModel):
    """Defines the Server Data Model."""

    id: Optional[Union[str, UUID4]] = Field(default=uuid.uuid4)
    server: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    environment: Optional[str] = Field(default=None)
    roles: Optional[list[Role]] = Field(default=None)
    custom_properties: Optional[list[CustomProperty]] = Field(default=None)
    account: Optional[str] = Field(default=None)
    catalog: Optional[str] = Field(default=None)
    database: Optional[str] = Field(default=None)
    dataset: Optional[str] = Field(default=None)
    delimiter: Optional[str] = Field(default=None)
    endpoint_url: Optional[str] = Field(default=None)
    format: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    path: Optional[str] = Field(default=None)
    port: Optional[int] = Field(default=None)
    project: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    regionName: Optional[str] = Field(default=None)
    schema_: Optional[str] = Field(default=None, alias="schema")
    serviceName: Optional[str] = Field(default=None)
    stagingDir: Optional[str] = Field(default=None)
    stream: Optional[str] = Field(default=None)
    warehouse: Optional[str] = Field(default=None)
