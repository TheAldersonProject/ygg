"""Skadi Helper."""

from pathlib import Path
from typing import Literal

import duckdb
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from ygg.core.data_contract_loader import YggBaseModel

base_url = "https://docs.snowflake.com/en/sql-reference"

# account_usage_pages_list = [
#     "account-usage/warehouse_events_history",
#     "account-usage/warehouse_load_history",
#     "account-usage/warehouse_metering_history",
# ]

account_usage_pages_list = [
    "account-usage/query_history",
]

organization_usage_pages_list = []
# organization_usage_pages_list = [
#     "organization-usage/accounts",
#     "organization-usage/data_transfer_daily_history",
#     "organization-usage/data_transfer_history",
#     "organization-usage/database_storage_usage_history",
#     "organization-usage/metering_daily_history",
#     "organization-usage/rate_sheet_daily",
#     "organization-usage/stage_storage_usage_history",
#     "organization-usage/storage_daily_history",
#     "organization-usage/usage_in_currency_daily",
#     "organization-usage/warehouse_metering_history",
# ]

additional_authoritative_definitions = [
    "https://docs.snowflake.com/en/guides-overview-cost",
    "https://docs.snowflake.com/en/user-guide/cost-management-overview",
    "https://docs.snowflake.com/en/user-guide/cost-understanding-overall",
    "https://docs.snowflake.com/en/user-guide/cost-understanding-compute",
    "https://docs.snowflake.com/en/user-guide/cost-understanding-data-storage",
    "https://docs.snowflake.com/en/user-guide/cost-understanding-data-transfer",
    "https://docs.snowflake.com/en/user-guide/cost-access-control",
    "https://docs.snowflake.com/en/user-guide/cost-insights",
    "https://docs.snowflake.com/en/user-guide/cost-optimize-cloud-services",
    "https://docs.snowflake.com/en/user-guide/cost-anomalies-access-control",
]


class TableColumn(BaseModel):
    column: str = Field(description="Column name")
    data_type: str = Field(description="Data type")
    description: str = Field(description="Description")
    businessName: str = Field(description="Business friendly name")
    primaryKey: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column can be used as a primary key, multiple columns can be set true. Rely on nullables count on the summary to make the decision.",
    )
    uniqueKey: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column can be used as a unique key, if not sure, set false.",
    )
    dateOrTimestamp: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column is or not a date or timestamp, if not sure, set false.",
    )
    dateOrTimestampType: Literal["date", "timestamp", "timestamp_ntz", "timestamp_ltz"] | None = Field(
        default=None,
        description="Date or timestamp type if the column is a date or timestamp.",
    )
    dateOrTimestampPagination: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column is or not a date or timestamp to be used for start point for pagination.",
    )
    examples: list[str] | None = Field(default_factory=list, description="List of examples, maximum of 5.")


class Table(BaseModel):
    name: str = Field(description="Table name")
    schemaName: str = Field(description="Schema name")
    description: str = Field(description="Description")
    businessName: str = Field(description="Human friendly name")
    tags: list[str] = Field(description="List of relevant tags")
    # columns: list[TableColumn] = Field(description="List of columns")
    dataGranularityDescription: str = Field(
        description="Granular level of the data in the object",
        examples=["Aggregation by country"],
    )


class TableColumns(BaseModel):
    model: list[TableColumn] = Field(description="List of columns")


class SkadiContractBasic(YggBaseModel):
    """Skadi Helper."""

    tenant: str | None = Field(default=None, description="Tenant identifier.")
    domain: str | None = Field(default=None, description="Domain identifier.")
    tags: list[str] | None = Field(default_factory=list, description="List of tags.")


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
    from ygg.skadi.dspy_cli import DsPyCli

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

        identified_links: list[ContractFundamentalsLinks] = Field(
            default_factory=list, description="Identified links within the document."
        )

    class ContractFundamentalsSignature(cli._dspy.Signature):
        """Contract Fundamentals Signature."""

        input: str = cli._dspy.InputField()
        output: ContractFundamentals = cli._dspy.OutputField()

    module = cli._dspy.Predict(ContractFundamentalsSignature)
    response = module(input=md)

    return response.output if response else None


def get_url_as_markdown(url: str) -> str:
    from docling.document_converter import DocumentConverter

    if not url:
        return ""

    converter = DocumentConverter()
    result = converter.convert(url)

    return result.document.export_to_markdown()


def inflate_contract_fundamentals(data: dict) -> SkadiContractBody:
    return SkadiContractBody(**data)


def bulk_load():
    for page in organization_usage_pages_list + account_usage_pages_list:
        usage_type = page.split("/")[0].replace("-", "_")
        base_url_fmt = f"{base_url}/{page}"

        md = get_url_as_markdown(base_url_fmt)
        if md:
            with open(
                f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report/markdown-scrape/{usage_type}/{page.split('/')[1]}.md",
                "w",
            ) as f:
                f.write(md)

    # for page in additional_authoritative_definitions:
    #     md = get_url_as_markdown(page)
    #     if md:
    #         with open(
    #             f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report/markdown-scrape/authoritative/{page.split('/')[-1]}.md",
    #             "w",
    #         ) as f:
    #             f.write(md)


def build_samples():
    from pathlib import Path

    folders_ = ["organization_usage", "account_usage"]
    for fd in folders_:
        pt = f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/data/{fd}"
        folder_path = Path(pt)

        for file in folder_path.iterdir():
            if file.is_file() and file.suffix == ".parquet":
                if (
                    str(file)
                    != "/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/data/account_usage/query_history.parquet"
                ):
                    print(f"Skipping {file}", " ## ", file)
                    continue

                with duckdb.connect(":memory:") as con:
                    q = f"select * from '{file}'"
                    con.sql(q).to_table("sample")
                    s = con.sql("select * from sample limit 10")
                    s = s.to_df()
                    md_sample = s.to_markdown()

                    sm = con.sql("summarize sample")
                    sm = sm.to_df()
                    md_sample_summary = sm.to_markdown()

                    f_name = f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report/sample/{fd}/{file.stem}.md"
                    with open(f_name, "w") as f:
                        f.write(md_sample)

                    f_name = (
                        f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report/sample-summary/{fd}/{file.stem}.md"
                    )
                    with open(f_name, "w") as f:
                        f.write(md_sample_summary)


def summarize_reports():
    from ygg.skadi.dspy_cli import DsPyCli

    cli = DsPyCli()

    from pathlib import Path

    def get_all_files_recursive(directory):
        path = Path(directory)
        all_files = []

        for item in path.iterdir():
            if item.is_dir():
                all_files.extend(get_all_files_recursive(item))

            elif item.is_file() and item.suffix == ".md":
                all_files.append(item)

        return all_files

    files = get_all_files_recursive("/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report")
    for f in files:
        md = f.read_text()

        class ReportSummary(YggBaseModel):
            """Contract Fundamentals Links."""

            title: str = Field(default_factory=str, description="Define a title for the report.")
            summary: str = Field(
                default_factory=str,
                description="Summarize the report with all relevant information.",
            )
            tags: list[str] | None = Field(default=None, description="Relevant tags for the report.")

            table_name: str | None = Field(default=None, description="Table name if the report is about a table.")
            table_schema_name: str | None = Field(
                default=None,
                description="Table schema name if the report is about a table.",
            )

        class ContractFundamentalsSignature(cli.dspy.Signature):
            """Contract Fundamentals Signature."""

            input: str = cli.dspy.InputField()
            output: ReportSummary = cli.dspy.OutputField()

        module = cli.dspy.Predict(ContractFundamentalsSignature)
        response = module(input=md)

        new_file = str(f).split("/")
        new_file = new_file[len(new_file) - 3 :]
        new_file = "/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/report/json-extractions/" + "/".join(new_file)
        Path(new_file).parent.mkdir(parents=True, exist_ok=True)
        new_file = new_file.replace(".md", ".json")

        data = response.output.model_dump_json()
        with open(new_file, "w") as f:
            f.write(data)


def load_sf_big_tables():
    import os

    import snowflake.connector
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    load_dotenv()

    with open(os.getenv("SNOWFLAKE_PRIVATE_KEY_FILE"), "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # os.environ["PRIVATE_KEY_PASSPHRASE"].encode()
            backend=default_backend(),
        )

    # 2. Converter para formato DER binário
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Load credentials from env vars for security

    for day_count in range(1, 366):
        for time_hour in range(0, 24):
            query = "SELECT * FROM snowflake.account_usage.query_history where true and date_part('hour', start_time) = {time_hour} and start_time::date = current_date() -{day_count}"
            output_path = f"/Users/thiagodias/Tad/projects/tyr/ygg/data/sample/data/account_usage/query_history/data_{day_count}_{time_hour}.parquet"
            output_path = output_path.format(day_count=day_count, hour=time_hour)

            file_path = Path(output_path)
            if file_path.exists():
                continue

            connection_params = dict(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                private_key=pkb,
                private_key_passphrase=None,
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database="snowflake",
            )

            with snowflake.connector.connect(**connection_params) as conn:
                with conn.cursor() as cur:
                    exec_query = query.format(day_count=day_count, time_hour=time_hour)
                    cur.execute(exec_query)
                    df = cur.fetch_pandas_all()
                    df.to_parquet(output_path, compression="snappy", index=False)


if __name__ == "__main__":
    bulk_load()
    # build_samples()
    # summarize_reports()
    # load_sf_big_tables()
