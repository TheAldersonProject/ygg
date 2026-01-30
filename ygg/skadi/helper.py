"""Skadi Helper."""

from typing import Literal

import duckdb
from pydantic import Field

from ygg.core.dynamic_models_factory import YggBaseModel
from ygg.skadi.dspy_cli import DsPyCli


class SkadiContractBasic(YggBaseModel):
    """Skadi Helper."""

    tenant: str | None = Field(default=None, description="Tenant identifier.")
    domain: str | None = Field(default=None, description="Domain identifier.")
    tags: list[str] | None = Field(default_factory=list, description="List of tags.")
    primaryKey: Literal[True, False] | None = Field(
        default=False, description="Whether the column can be used as a primary key, if not sure, set false."
    )
    uniqueKey: Literal[True, False] | None = Field(
        default=False, description="Whether the column can be used as a unique key, if not sure, set false."
    )
    dateOrTimestamp: Literal[True, False] | None = Field(
        default=False, description="Whether the column is or not a date or timestamp, if not sure, set false."
    )
    dateOrTimestampType: Literal["date", "timestamp", "timestamp_ntz", "timestamp_ltz"] | None = Field(
        default=None, description="Date or timestamp type if the column is a date or timestamp."
    )
    dateOrTimestampPagination: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column is or not a date or timestamp to be used for start point for pagination.",
    )


class SkadiContractBody(SkadiContractBasic):
    """Skadi Helper."""

    apiVersion: Literal["v3.1.0"] | None = Field(default="v3.1.0")
    kind: Literal["DataContract"] | None = Field(default="DataContract")
    id: str | None = Field(default=None)
    version: str | None = Field(default="0.0.1")
    name: str | None = Field(default=None)
    status: Literal["active", "draft", "deprecated"] | None = Field(default="draft")
    authoritativeDefinitions: list[dict] = Field(default_factory=dict)
    dataProduct: str | None = Field(default=None)
    description: dict | None = Field(default_factory=dict)


class SkadiContractSchema(YggBaseModel):
    """Skadi Contract Schema."""

    id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    schemaName: str | None = Field(default=None)
    description: str | None = Field(default=None)
    businessName: str | None = Field(default=None)
    tags: list[str] | None = Field(default_factory=list)
    physicalName: str | None = Field(default=None)
    physicalType: Literal["table", "view"] | None = Field(default="table")
    flowType: Literal["input", "output", "transform"] = Field(default="input")
    dataGranularityDescription: str | None = Field(default=None)


class SkadiContractSchemaColumns(YggBaseModel):
    columns: list[dict] = Field(default_factory=list)


def extract_fundamentals_info_from_sf_web_page(md: str):
    if not md:
        return None

    cli = DsPyCli()

    class ContractFundamentalsLinks(YggBaseModel):
        """Contract Fundamentals Links."""

        url: str | None = Field(default=None, description="Relevant identified links in the document.")
        type: str | None = Field(default=None, description="Type of the identified link.")
        description: str | None = Field(default=None, description="Description of the identified link.")

    class ContractFundamentals(YggBaseModel):
        """Contract Fundamentals."""

        document_description: str | None = Field(
            default=None,
            summary="Description / Summary of the analyzed document.",
        )
        type_of_document: str = Field(
            default="",
            description="Type of the analyzed document.",
            examples=["Canonical", "Jira Ticket", "Request for Comments"],
        )

        tags: list[str] | None = Field(default_factory=list, description="List of relevant tags.")

        purpose: str | None = Field(default=None, description="Purpose of the analyzed document.")
        limitations: str | None = Field(default=None, description="Limitations identified within the document.")
        usage: str | None = Field(default=None, description="Usage of the analyzed document.")

        identified_links: list[ContractFundamentalsLinks] = Field(default_factory=list, description="Identified links within the document.")

    class ContractFundamentalsSignature(cli.dspy.Signature):
        """Contract Fundamentals Signature."""

        input: str = cli.dspy.InputField()
        output: ContractFundamentals = cli.dspy.OutputField()

    module = cli.dspy.Predict(ContractFundamentalsSignature)
    response = module(input=md)

    return response.output if response else None


def extract_sf_web_page(md: str):
    if not md:
        return None

    cli = DsPyCli()
    data = cli.basic_predict(md)
    contract_schema = None
    md_sample = ""
    if data:
        data = data.model
        contract_schema = SkadiContractSchema(**data.model_dump())

        if contract_schema:
            with duckdb.connect(":memory:") as con:
                q = f"select * from '/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/data/organization_usage/{contract_schema.name.lower()}.parquet' using sample 20% "
                con.sql(q).to_table("sample")
                s = con.sql("select * from sample limit 25")
                s = s.to_df()
                md_sample = s.to_markdown()
                sm = con.sql("summarize sample")
                sm = sm.to_df()
                md_sample_summary = sm.to_markdown()

            contract_schema_cols = cli.columns_predict(md, md_sample_summary, md_sample)
            if contract_schema_cols:
                contract_schema_cols = contract_schema_cols.model
                contract_schema_cols = contract_schema_cols

    return data, contract_schema, md_sample, md_sample_summary, contract_schema_cols


def get_url_as_markdown(url: str) -> str:
    if not url:
        return ""

    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(url)

    return result.document.export_to_markdown()


def inflate_contract_fundamentals(data: dict) -> SkadiContractBody:
    return SkadiContractBody(**data)
