"""Ingests online documents."""

import os
from datetime import datetime, timezone
from uuid import NAMESPACE_DNS, uuid5

import duckdb
from dotenv import load_dotenv
from pydantic import Field, model_validator

from ygg.core.data_contract_loader import YggBaseModel
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class WebScrapedContentDocument(YggBaseModel):
    """Ingests online documents."""

    id: str | None = Field(default=None)
    url: str = Field(...)

    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    markdown_content: str | None = Field(default=None)
    created_at: datetime | None = Field(default=None)

    @model_validator(mode="after")
    def validate_and_overwrite_deterministically(self):
        self.url = self.url.strip()
        unique_string = self.url.replace("://", "/").replace("//", "/").replace(".", "/").replace(":", "/")
        generated_id = uuid5(NAMESPACE_DNS, unique_string)

        self.tags = [t.lower().rstrip().lstrip() for t in self.tags]

        self.id = str(generated_id)
        self.created_at = datetime.now(tz=timezone.utc)

        return self

    @staticmethod
    def load_from_url(url: str):
        """Loads online documents from a URL."""

        if not url or not url.strip():
            logs.error("URL is empty", url=url)
            raise ValueError("Invalid URL")

        return WebScrapedContentDocument._acquire_from_url(url)

    @staticmethod
    def _acquire_from_url(url: str, force_reload: bool = False) -> "WebScrapedContentDocument":
        """Loads online documents from a URL."""

        load_dotenv()
        scraped_docs_db_path = os.getenv("SCRAPED_CONTENT_DATABASE_FOLDER", "")
        logs.debug(
            "Loading scraped docs database folder",
            scraped_docs_path=scraped_docs_db_path,
        )

        def get_url_as_markdown(url_: str) -> str:
            if not url_:
                logs.debug("URL is empty", url=url_)
                return url_

            from docling.document_converter import DocumentConverter

            converter = DocumentConverter()
            result = converter.convert(url)
            md_content = result.document.export_to_markdown()

            logs.debug("Content loaded and exported to Markdown.")

            return md_content

        def get_from_data_lake():
            try:
                with duckdb.connect(":memory:", read_only=False) as conn:
                    ddb_path = f"{scraped_docs_db_path}/*.parquet"
                    # ddb = conn.read_parquet(ddb_path)
                    data_ = duckdb.sql(f"select * from '{ddb_path}' where url = '{url}'")
                    data_ = data_.fetchdf()
                    data_ = data_.to_dict(orient="records")

                    if data_:
                        raw_ = (
                            WebScrapedContentDocument(**data_[0])
                            if isinstance(data_, list)
                            else WebScrapedContentDocument(**data_)
                        )
                        return raw_

            except Exception as exc:
                logs.error("Error during data retrieval step.", exception=exc)
                return None

        if not not force_reload:
            if data := get_from_data_lake():
                return data

        logs.debug("Scraping online documents...")

        md: str = get_url_as_markdown(url)

        def textract():
            from ygg.skadi.dspy_cli import DsPyCli

            cli = DsPyCli()

            logs.debug("Extracting values out of the online document.", url=url)

            class RawDocumentSignature(cli.dspy.Signature):
                """Contract Fundamentals Signature."""

                input: str = cli.dspy.InputField()
                output: WebScrapedContentDocument = cli.dspy.OutputField()

            module = cli.dspy.Predict(RawDocumentSignature)
            response_ = module(input=md)
            return response_

        response = textract()
        doc = WebScrapedContentDocument(**response.output.model_dump())
        headers = [k for k in list(doc.model_dump().keys())]
        place_holders = ",".join(["?" for _ in headers])
        values = list(doc.model_dump().values())
        headers = ",".join(headers)

        create_table_ddl = """
        create table if not exists scraped_content (
            id varchar,
            url varchar,
            title varchar,
            description varchar,
            summary varchar,
            tags varchar[],
            markdown_content varchar,
            created_at timestamptz
        )
        """

        stmt = f"insert into scraped_content ({headers}) values ({place_holders})"
        export_stmt = f"copy (select * from scraped_content where id = '{doc.id}') to '{scraped_docs_db_path}/{doc.id}.parquet' (FORMAT parquet, COMPRESSION zstd) "
        logs.debug("Inserting online documents into the documents database.")
        with duckdb.connect(":memory:", read_only=False) as conn:
            try:
                conn.execute(create_table_ddl)
                conn.execute(stmt, values)
                conn.execute(export_stmt)
            except Exception as e:
                logs.error("Error while inserting online documents", e=e)
                raise e

        raw_document = get_from_data_lake()
        logs.debug("Document loaded.", raw_document=raw_document.id)
        return raw_document


if __name__ == "__main__":
    # from ygg.utils.files_utils import get_yaml_content
    #
    # path = "/Users/thiagodias/Tad/projects/tyr/ygg-assets/manual-input/llm-prompts/sf-contract-from-url"
    # url_list = f"{path}/scrape.yaml"
    #
    # url_list_path = Path(url_list).resolve()
    # print(url_list_path)
    # if url_list_path.is_file():
    #     content: dict = get_yaml_content(url_list_path)
    #     if "urls" in content:
    #         for url in content.get("urls", []):
    #             RawDocument.acquire_from_url(url)
    r = WebScrapedContentDocument.load_from_url("https://docs.snowflake.com/en/user-guide/cost-understanding-compute")
    print(r)
