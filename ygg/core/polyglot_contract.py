"""Core services to handle data contracts"""

from typing import Any, Self, Type, Union

from ygg.core.shared_model_mixin import SharedModelMixin
from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import PolyglotEntity, YggBaseModel
from ygg.polyglot.polyglot import Polyglot
from ygg.polyglot.quack_connector import QuackConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="DataContract")


class PolyglotContract:
    """Polyglot Contract"""

    def __init__(self, entity: PolyglotEntity | Polyglot):
        """Initialize Data Contract Setup"""

        if not entity:
            logs.error("Polyglot Entity must be provided and must be of types Polyglot or PolyglotEntity.")
            raise ValueError("Polyglot Entity must be provided and must be of types Polyglot or PolyglotEntity.")

        instance = None
        if isinstance(entity, YggBaseModel):
            instance = entity
            entity = entity.polyglot_entity
        else:
            entity = entity.instance.polyglot_entity

        self._entity: Union[Polyglot, PolyglotEntity] = entity
        self._instance: Union[Polyglot, PolyglotEntity] = instance

        self._second_layer_db_connector: QuackConnector | None = None

        self.__first_layer_instructions: list[str] = []
        self.__second_layer_instructions: list[str] = []

        self._load_instructions()

    def _load_instructions(self, recreate_existing_entity: bool | None = False) -> Self:
        """Build the data contract."""

        if not self._entity:
            logs.error("A Polyglot Entity must be provided.")
            raise ValueError("A Polyglot Entity must be provided.")

        logs.debug(
            "Creating Data Contract Tables",
            entity_schema=self._entity.schema_,
            entity=self._entity.name,
        )

        if not self.__first_layer_instructions or not self.__second_layer_instructions:
            _first_layer_db_connector = QuackConnector(
                entity=self._entity,
                connector_type=DuckLakeDbEntityType.DUCKDB,
                recreate_existing_entity=recreate_existing_entity,
            )
            _first_layer_db_connector = _first_layer_db_connector.connector

            _second_layer_db_connector = QuackConnector(
                entity=self._entity,
                connector_type=DuckLakeDbEntityType.DUCKLAKE,
                recreate_existing_entity=recreate_existing_entity,
            )
            _second_layer_db_connector = _second_layer_db_connector.connector
            self._second_layer_db_connector = _second_layer_db_connector

            self.__first_layer_instructions.append(_first_layer_db_connector.schema_ddl)
            self.__first_layer_instructions.append(_first_layer_db_connector.entity_ddl)
            self.__second_layer_instructions = list(
                _second_layer_db_connector.ducklake_setup_instructions().model_dump().values()
            )

        logs.info("Table create statement successfully added to the instructions list.")

        return self

    def setup(self) -> Self:
        """Execute the instructions."""

        logs.info("Executing Instructions")
        instructions = self.__first_layer_instructions + self.__second_layer_instructions
        instructions.append(self._second_layer_db_connector.schema_ddl)
        instructions.append(self._second_layer_db_connector.entity_ddl)

        QuackConnector.execute_instructions(instructions=instructions)

        logs.info("Instructions Executed Successfully.")
        return self

    def write_contract(self, upsert: bool = True) -> dict[str, Any]:
        """Write the data document."""

        instructions = self.__first_layer_instructions + self.__second_layer_instructions

        statement_map: Type[YggBaseModel, SharedModelMixin] = self._instance.statement_map
        first_layer_statement: str = statement_map.get("first_layer_db_write_statement", "")
        first_layer_values: str = statement_map.get("first_layer_db_write_values", [])

        second_layer_statement: str = statement_map.get("second_layer_db_insert_statement", "")
        if upsert:
            second_layer_statement: str = statement_map.get("second_layer_db_merge_statement", "")

        instructions.append({"statement": first_layer_statement, "values": first_layer_values})
        instructions.append(second_layer_statement)
        QuackConnector.execute_instructions(instructions=instructions)

        return statement_map.get("hydrate_return", {})
