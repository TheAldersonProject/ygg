"""Service Level Agreement Implementation"""

from typing import ClassVar, Optional, Union

from pydantic import Field

import ygg.core.commons as commons
import ygg.core.odcs_fields as odcs_fields


class YggDataContractServiceLevelAgreement(commons.YggBaseModel):
    """Service Level Agreement for Data Contract (SLA)."""

    id: odcs_fields.StableId = Field(default=None, alias="id")
    property: commons.YggDataContractSlaProperty
    property_value: Union[str, float, int, bool] = Field(alias="value")
    property_unit: Optional[str] = Field(default=None, alias="unit")
    element: list[str]
    driver: commons.YggDataContractSlaDriver
    description: str

    contract_id: odcs_fields.StableId = Field(default=None)
    contract_version: odcs_fields.StableId = Field(default=None)


class YggDataContractSla(YggDataContractServiceLevelAgreement):
    """Service Level Agreement for Data Contract (SLA)."""

    TABLE_NAME: ClassVar[str] = "contract_sla"


class YggDataContractSchemaSla(YggDataContractServiceLevelAgreement):
    """Service Level Agreement for Data Contract (SLA)."""

    TABLE_NAME: ClassVar[str] = "contract_schema_sla"
