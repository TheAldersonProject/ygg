"""Defines the Pricing Data Model."""

from typing import Optional, Union

from pydantic import Field

from ygg.core import YggBaseModel


class Pricing(YggBaseModel):
    """Defines the Pricing Data Model."""

    id: Optional[str] = Field(default=None)
    price_amount: Optional[Union[float, int]] = Field(default=None)
    price_currency: Optional[str] = Field(default=None)
    price_unit: Optional[str] = Field(default=None)
