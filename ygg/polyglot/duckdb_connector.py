"""Set of tools to interact with DuckDb and DuckLake."""

from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import (
    PolyglotEntity,
)
from ygg.polyglot.quack_service import QuackService
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="DuckDbConnector")


class DuckDbConnector(QuackService):
    """DuckLake Db Tools"""

    def __init__(
        self,
        model: PolyglotEntity,
        catalog_name: str,
        recreate_existing_entity: bool = False,
    ) -> None:
        """Initialize DuckLake Db Tools"""

        if not model:
            logs.error("DuckLake Db Entity cannot be empty.")
            raise ValueError("DuckLake Db Entity cannot be empty.")

        if not catalog_name:
            logs.error("Catalog name cannot be empty.")
            raise ValueError("Catalog name cannot be empty.")

        super().__init__(model=model, catalog_name=catalog_name, recreate_existing_entity=recreate_existing_entity)

        logs.info(
            "Initializing Duck Lake & Db Tools module.",
            model=self._model.name,
            schema=self._entity_schema_name.lower(),
            recreate_existing=recreate_existing_entity,
            catalog_name=catalog_name,
        )

    @property
    def schema_ddl(self) -> str:
        """Get the DuckDb schema ddl."""
        return self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKDB)

    @property
    def entity_ddl(self) -> str:
        """Get the DuckDb entity ddl."""
        return self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKDB)
