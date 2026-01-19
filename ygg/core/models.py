"""Ygg Base Model."""

from datetime import datetime
from typing import ClassVar, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

import ygg.core.constants as cons
import ygg.core.enums as enums
import ygg.core.odcs_fields as odcs_fields
from ygg.core.odcs_fields import AuthoritativeDefinitionField


class YggBaseModel(BaseModel):
    """Base data-models for Ygg data models."""

    model_config = ConfigDict(use_enum_values=True)
    record_create_ts: Optional[datetime] = Field(default=None, frozen=True)
    record_update_ts: Optional[datetime] = Field(default=None, frozen=True)

    @classmethod
    def get_ddl(cls) -> str:
        return cons.get_entity_ddl_from_class_name(cls.__name__)


class YggDataContractSchemaProperty(YggBaseModel):
    """A list of elements within the schema to be cataloged."""

    TABLE_NAME: ClassVar[str] = "contract_schema_property"

    id: odcs_fields.StableId = Field(default=None, alias="id")
    physical_name: Optional[str] = Field(default=None, alias="physicalName")
    physical_type: Optional[Union[enums.YggEntityType, str]] = Field(
        default=None, alias="physicalType"
    )
    description: Optional[str] = Field(default=None)
    business_name: Optional[str] = Field(default=None, alias="businessName")
    authoritative_definitions: AuthoritativeDefinitionField = Field(
        alias="authoritativeDefinitions"
    )
    tags: odcs_fields.TagsField
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None)

    property_name: str = Field(min_length=5, alias="name")
    primary_key: Optional[bool] = Field(default=False, alias="primaryKey")
    primary_key_position: Optional[int] = Field(default=None, alias="primaryKey")
    logical_type: Optional[enums.YggLogicalDataTypes] = Field(
        default=None, alias="logicalType"
    )
    is_required: Optional[bool] = Field(default=False, alias="required")
    is_unique: Optional[bool] = Field(default=False, alias="unique")
    is_partitioned: Optional[bool] = Field(default=False, alias="partitioned")
    partition_key_position: Optional[int] = Field(
        default=None, alias="partitionKeyPosition"
    )
    classification: Optional[str] = Field(default=None)
    encrypted_name: Optional[str] = Field(default=None, alias="encryptedName")
    critical_data_element: Optional[bool] = Field(
        default=False, alias="criticalDataElement"
    )
    examples: Optional[list[str]] = Field(default=None)


class YggDataContractServiceLevelAgreement(YggBaseModel):
    """Service Level Agreement for Data Contract (SLA)."""

    id: odcs_fields.StableId = Field(default=None, alias="id")
    property: enums.YggDataContractSlaProperty
    property_value: Union[str, float, int, bool] = Field(alias="value")
    unit: Optional[str] = Field(default=None)
    element: list[str]
    driver: enums.YggDataContractSlaDriver
    description: Optional[str] = Field(default=None)


class YggDataContractServiceLevelAgreementContract(
    YggDataContractServiceLevelAgreement
):
    """Service Level Agreement for Data Contract (SLA)."""

    TABLE_NAME: ClassVar[str] = "contract_sla"


class YggDataContractServiceLevelAgreementSchema(YggDataContractServiceLevelAgreement):
    """Service Level Agreement for Data Contract (SLA)."""

    TABLE_NAME: ClassVar[str] = "contract_schema_sla"


class YggDataContractServer(YggBaseModel):
    """Data Contract Server."""

    TABLE_NAME: ClassVar[str] = "contract_server"
    ODCS_NODE: ClassVar[str] = "$defs.Server"

    id: odcs_fields.StableId = Field(default=None, alias="id")
    server: odcs_fields.StableId = Field(default=None)
    server_type: enums.YggDataContractServerType = Field(alias="type")
    description: Optional[str] = Field(default=None)
    environment: enums.YggDataContractServerEnvironment
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None)
    database_name: odcs_fields.StableId = Field(
        alias="database", description="Name of the database."
    )
    database_schema: odcs_fields.StableId = Field(
        alias="schema", description="Name of the schema in the database."
    )


class YggDataContractSchema(YggBaseModel):
    """A list of elements within the schema to be cataloged."""

    TABLE_NAME: ClassVar[str] = "contract_schema"

    id: odcs_fields.StableId = Field(default=None, alias="id")
    physical_name: Optional[str] = Field(default=None, alias="physicalName")
    physical_type: Optional[Union[enums.YggEntityType, str]] = Field(
        default=None, alias="physicalType"
    )
    description: Optional[str] = Field(default=None)
    business_name: Optional[str] = Field(default=None, alias="businessName")
    authoritative_definitions: AuthoritativeDefinitionField = Field(
        alias="authoritativeDefinitions"
    )
    tags: odcs_fields.TagsField
    custom_properties: odcs_fields.CustomPropertiesField = Field(default=None)

    schema_name: str = Field(min_length=5, alias="name")
    data_granularity_description: Optional[str] = Field(
        default=None, alias="dataGranularityDescription"
    )
    ygg_flow_type: Optional[enums.YggDataContractGeneralFlowType] = Field(
        default=None, alias="yggFlowType"
    )
    sla_properties: Optional[list[YggDataContractServiceLevelAgreementSchema]] = Field(
        default=None, alias="slaProperties"
    )
    server_name: Optional[str] = Field(default=None, alias="server")
    properties: list[YggDataContractSchemaProperty]


class YggDataContractFundamentals(YggBaseModel):
    """Fundamentals of the Data Contract."""

    TABLE_NAME: ClassVar[str] = "contract"
    ODCS_NODE: ClassVar[str] = "properties"

    api_version: Optional[Literal["v3.1.0"]] = Field(
        alias="apiVersion", default="v3.1.0"
    )
    kind: Literal["DataContract"] = Field(default="DataContract")
    id: odcs_fields.StableId = Field(default=None, alias="id")
    contract_name: odcs_fields.StableId = Field(
        default=None, max_length=255, alias="name"
    )
    tenant: odcs_fields.StableId = Field(default=None, max_length=64)
    contract_domain: odcs_fields.StableId = Field(
        default=None, max_length=64, alias="domain"
    )
    contract_version: Optional[odcs_fields.SemanticalVersionField] = Field(
        default="0.0.1", alias="version"
    )
    status: Optional[enums.YggDataContractStatus] = Field(
        default=enums.YggDataContractStatus.DRAFT
    )
    tags: odcs_fields.TagsField
    data_product: str = Field(alias="dataProduct", max_length=255)

    authoritative_definitions: AuthoritativeDefinitionField = Field(
        alias="authoritativeDefinitions"
    )
    description: dict = Field(title="Description")
    ygg_flow_type: enums.YggDataContractGeneralFlowType = Field(
        alias="yggFlowType", description="General flow type."
    )
    version_ts: Optional[datetime] = Field(default=None, alias="versionTs")


class YggDataContract(YggBaseModel):
    """Data Contract."""

    SCHEMA_NAME: ClassVar[str] = "data_contracts"

    fundamentals: YggDataContractFundamentals
    contract_schema: list[YggDataContractSchema] = Field(alias="schema")
    servers: Optional[list[YggDataContractServer]] = Field(default=None)
    sla_properties: Optional[YggDataContractServiceLevelAgreementContract] = Field(
        default=None, alias="slaProperties"
    )


if __name__ == "__main__":
    from ygg.utils.yaml_utils import get_yaml_content

    yc = get_yaml_content("../../dev/file1.yaml")
    # print(yc)
    i = YggDataContract(**yc)
    pm = i.fundamentals.model_dump(mode="json", exclude_none=False)
    #
    # import duckdb as ddb
    #
    # with ddb.connect(database="ygg_x.duckdb", read_only=False) as ddb:
    #     ddb.execute("create schema if not exists data_contracts;")
    #     ddb.execute(YggDataContract.get_ddl())
    #     cols = ",".join(pm.keys())
    #     params = ", ".join(["?"] * len(pm))
    #     insert_statement: str = f"""
    #         insert into data_contracts.contract (
    #             {cols}
    #         ) values ({params})
    #     """
    #     ddb.execute(insert_statement, list(pm.values()))

    # from sqlmodel import create_engine, Session, select
    #
    # engine = create_engine("duckdb:///:memory:")
    # # SQLModel.metadata.create_all(engine)
    #
    # with Session(engine) as session:
    #     # We can instantiate the dynamic class just like a normal one
    #     cust = CustomerDB(id=1, name="Mimir Corp", email="info@mimir.com", internal_score=99.9)
    #     session.add(cust)
    #     session.commit()
    #
    #     # Query it back
    #     statement = select(CustomerDB).where(CustomerDB.name == "Mimir Corp")
    #     result = session.exec(statement).first()
    #     print(f"Retrieved: {result.name} - {result.email}")
