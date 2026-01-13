"""Reference Data Model."""

from typing import Optional, Union

from pydantic import Field

from ygg.core import YggBaseModel
from ygg.model.odcs.odcs_commons import CustomProperty


class ReferenceBase(YggBaseModel):
    """Defines the References section Data Model."""

    type: Optional[str] = Field(default="foreignKey")
    to_: Optional[str] = Field(default=None)
    custom_properties: Optional[Union[list[CustomProperty], CustomProperty]] = Field(
        default=None
    )


class ReferenceObject(ReferenceBase):
    """Defines the Reference Object Data Model."""

    from_: str
