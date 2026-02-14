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
                logs.error("Error executing SQL statement.", error=str(e), statement=str(statement))
                raise e

    @staticmethod
    def create_entity(
        model: PolyglotEntity,
        catalog_name: str,
        recreate_existing_entity: bool = False,
    ) -> None:
        """Create the entity in the catalog."""

        instructions: list[str] = []
        db_connector: QuackConnector = QuackConnector(
            model=model,
            catalog_name=catalog_name,
            recreate_existing_entity=recreate_existing_entity,
            connector_type=DuckLakeDbEntityType.DUCKDB,
        )
        db_connector: DuckDbConnector = db_connector.connector
        instructions.append(db_connector.schema_ddl)
        instructions.append(db_connector.entity_ddl)

        dl_connector: QuackConnector = QuackConnector(
            model=model,
            catalog_name=catalog_name,
            recreate_existing_entity=recreate_existing_entity,
            connector_type=DuckLakeDbEntityType.DUCKLAKE,
        )
        dl_connector: DuckLakeConnector = dl_connector.connector
        dl_connector.create_duck_lake_catalog()
        for v in dl_connector.ducklake_setup_instructions().model_dump().values():
            instructions.append(v)
        instructions.append(dl_connector.schema_ddl)
        instructions.append(dl_connector.entity_ddl)

        QuackConnector.execute_instructions(instructions=instructions)
