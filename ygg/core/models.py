"""Ygg Base Model."""

from datetime import datetime
from typing import ClassVar, Literal, Optional

from pydantic import Field

import ygg.core.commons as commons
import ygg.core.odcs_fields as odcs_fields
import ygg.core.sla as sla
from ygg.core.contract_schema import YggDataContractSchema
from ygg.core.odcs_fields import AuthoritativeDefinitionField
from ygg.core.server import YggDataContractServer


class YggDataContractFundamentals(commons.YggBaseModel):
    """Fundamentals of the Data Contract."""

    TABLE_NAME: ClassVar[str] = "contract"
    ODCS_NODE: ClassVar[str] = "properties"

    api_version: Optional[Literal["v3.1.0"]] = Field(alias="apiVersion", default="v3.1.0")
    kind: Literal["DataContract"] = Field(default="DataContract")
    id: odcs_fields.StableId = Field(default=None, alias="id")
    contract_name: odcs_fields.StableId = Field(default=None, max_length=255, alias="name")
    tenant: odcs_fields.StableId = Field(default=None, max_length=64)
    contract_domain: odcs_fields.StableId = Field(default=None, max_length=64, alias="domain")
    contract_version: Optional[odcs_fields.SemanticalVersionField] = Field(default="0.0.1", alias="version")
    status: Optional[commons.YggDataContractStatus] = Field(default=commons.YggDataContractStatus.DRAFT)
    tags: odcs_fields.TagsField
    data_product: str = Field(alias="dataProduct", max_length=255)

    authoritative_definitions: AuthoritativeDefinitionField = Field(alias="authoritativeDefinitions")
    description: dict = Field(title="Description")
    ygg_flow_type: commons.YggDataContractGeneralFlowType = Field(alias="yggFlowType", description="General flow type.")
    version_ts: Optional[datetime] = Field(default=None, alias="versionTs")


class YggDataContract(commons.YggBaseModel):
    """Data Contract."""

    SCHEMA_NAME: ClassVar[str] = "data_contracts"

    fundamentals: YggDataContractFundamentals
    contract_schema: list[YggDataContractSchema] = Field(alias="schema")
    servers: Optional[list[YggDataContractServer]] = Field(default=None)
    sla_properties: Optional[sla.YggDataContractSla] = Field(default=None, alias="slaProperties")


if __name__ == "__main__":
    from ygg.utils.yaml_utils import get_yaml_content

    yc = get_yaml_content(
        "/home/thiago/projects/ygg/assets/data-models/examples/snowflake/organization_usage/usage_in_currency_daily.yaml"
    )

    i = YggDataContract(**yc)
    print(i)
    pm = i.fundamentals.model_dump(mode="json", exclude_none=False)
