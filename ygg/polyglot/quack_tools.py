"""Set of tools to interact with DuckDb and DuckLake."""

import duckdb

from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import PolyglotEntity
from ygg.polyglot.duckdb_connector import DuckDbConnector
from ygg.polyglot.ducklake_connector import DuckLakeConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class QuackConnector:
    """DuckLake Db Tools"""

    def __init__(
        self,
        model: PolyglotEntity,
        catalog_name: str,
        recreate_existing_entity: bool = False,
        connector_type: DuckLakeDbEntityType = DuckLakeDbEntityType.DUCKLAKE,
    ) -> None:
        """Initialize DuckLake Db Tools"""

        if not model:
            logs.error("DuckLake Db Entity cannot be empty.")
            raise ValueError("DuckLake Db Entity cannot be empty.")

        if not catalog_name:
            logs.error("Catalog name cannot be empty.")
            raise ValueError("Catalog name cannot be empty.")

        self._model: PolyglotEntity = model
        self._entity_schema_name = model.schema_.upper()
        self._recreate_existing_database: bool = recreate_existing_entity or False
        self._catalog_name: str = catalog_name
        self._connector_type: DuckLakeDbEntityType = connector_type

        logs.info(
            "Initializing Duck Lake & Db Tools module.",
            model=self._model.name,
            schema=self._entity_schema_name.lower(),
            recreate_existing=recreate_existing_entity,
            catalog_name=catalog_name,
            connector_type=self._connector_type.value,
        )

        if connector_type == DuckLakeDbEntityType.DUCKLAKE:
            self._connector = DuckLakeConnector(
                model=model,
                catalog_name=catalog_name,
                recreate_existing_entity=recreate_existing_entity,
            )
        else:
            self._connector = DuckDbConnector(
                model=model,
                catalog_name=catalog_name,
                recreate_existing_entity=recreate_existing_entity,
            )

    @property
    def connector(self) -> DuckLakeConnector | DuckDbConnector:
        return self._connector

    @staticmethod
    def execute_instructions(instructions: list[str] | str) -> None:
        """Execute a list of SQL statements against the database."""

        if not instructions:
            raise ValueError("Instructions cannot be empty.")

        if isinstance(instructions, str):
            instructions = [instructions]

        with duckdb.connect(":memory:", read_only=False) as con:
            try:
                for statement in instructions:
                    logs.debug("Executing SQL statement.")
                    if isinstance(statement, list):
                        statement = " ".join(statement)
                    con.execute(statement)
                    logs.debug("SQL statement executed successfully.")

            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}")
                raise e
