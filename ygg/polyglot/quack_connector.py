"""Set of tools to interact with DuckDb and DuckLake."""

import duckdb

from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import PolyglotEntity
from ygg.polyglot.duckdb_connector import DuckDbConnector
from ygg.polyglot.ducklake_connector import DuckLakeConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="QuackConnector")


class QuackConnector:
    """DuckLake Db Tools"""

    def __init__(
        self,
        entity: PolyglotEntity,
        recreate_existing_entity: bool = False,
        connector_type: DuckLakeDbEntityType = DuckLakeDbEntityType.DUCKLAKE,
    ) -> None:
        """Initialize DuckLake Db Tools"""

        if not entity:
            logs.error("DuckLake Db Entity cannot be empty.")
            raise ValueError("DuckLake Db Entity cannot be empty.")

        self._model: PolyglotEntity = entity
        self._entity_schema_name = entity.schema_
        self._recreate_existing_database: bool = recreate_existing_entity or False
        self._connector_type: DuckLakeDbEntityType = connector_type

        logs.info(
            "Initializing Duck Lake & Db Tools module.",
            model=self._model.name,
            schema=self._entity_schema_name.lower(),
            recreate_existing=recreate_existing_entity,
            catalog_name=self._model.catalog,
            connector_type=self._connector_type.value,
        )

        if connector_type == DuckLakeDbEntityType.DUCKLAKE:
            self._connector = DuckLakeConnector(
                model=entity,
                catalog_name=self._model.catalog,
                recreate_existing_entity=recreate_existing_entity,
            )
        else:
            self._connector = DuckDbConnector(
                model=entity,
                catalog_name=self._model.catalog,
                recreate_existing_entity=recreate_existing_entity,
            )

    @property
    def connector(self) -> DuckLakeConnector | DuckDbConnector:
        return self._connector

    @staticmethod
    def execute_instructions(instructions: list[str] | str, duckdb_file: str | None = ":memory:") -> None:
        """Execute a list of SQL statements against the database."""

        if not instructions:
            raise ValueError("Instructions cannot be empty.")

        if isinstance(instructions, str):
            instructions = [instructions]

        with duckdb.connect(duckdb_file, read_only=False) as con:
            try:
                for statement in instructions:
                    logs.debug("Executing SQL statement.")
                    if isinstance(statement, dict):
                        con.execute(statement["statement"], statement["values"])
                        short_statement = (
                            str(statement["statement"]).replace("\n", " ").replace("\t", " ").strip().lower()[:30]
                        )
                        logs.debug("SQL statement executed successfully.", statement=short_statement)
                        continue
                    elif isinstance(statement, list):
                        statement = " ".join(statement)

                    con.execute(statement)
                    short_statement = str(statement).replace("\n", " ").replace("\t", " ").strip().lower()[:30]
                    logs.debug("SQL statement executed successfully.", statement=short_statement)

            except Exception as e:
                logs.error("Error executing SQL statement.", error=str(e), statement=str(statement))
                raise e
