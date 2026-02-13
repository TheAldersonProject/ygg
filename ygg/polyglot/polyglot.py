"""Database Polyglot Service."""

from typing import Any, Self

from ygg.config import YggSetup
from ygg.core.dynamic_odcs_models_factory import DynamicModelFactory
from ygg.helpers.data_types import get_data_type
from ygg.helpers.enums import PolyglotTargetType
from ygg.helpers.logical_data_models import (
    PolyglotEntity,
    PolyglotEntityColumn,
    PolyglotEntityColumnDataType,
)
from ygg.polyglot.quack_tools import QuackConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="Polyglot")


class Polyglot:
    """Database Polyglot Service."""

    def __init__(self, data_contract: dict[str, Any]):
        """Initialize the Database Polyglot Service."""

        if not data_contract:
            logs.error("Data contract cannot be empty.")
            raise ValueError("Data contract cannot be empty.")

        self._data_contract: dict[str, Any] = data_contract

        self._data_model: PolyglotEntity | None = None
        self._sink_type: PolyglotTargetType | None = None
        self._recreate_existing_entity: bool = False

        self._setup: YggSetup = YggSetup(create_ygg_folders=False, config_data=None)

    def data_model(self, value: PolyglotEntity) -> Self:
        """Set the data model."""
        if not value:
            logs.error("Data model cannot be empty.")
            raise ValueError("Data model cannot be empty.")

        logs.debug("Data Model Set.", data_model=value.name)
        self._data_model = value
        return self

    def sink_type(self, value: PolyglotTargetType) -> Self:
        """Set the sink type."""
        if not value:
            value = PolyglotTargetType.QUACK

        logs.debug("Sink Type Set.", sink_type=value.value)
        self._sink_type = value
        return self

    def recreate_existing_entity(self, value: bool) -> Self:
        """Set the property 'recreate existing entity' flag."""
        logs.debug("Recreate Existing Entity.", recreate_existing=value)
        self._recreate_existing_entity = value or False
        return self

    def build(self) -> Self:
        """Build the database polyglot service."""

    @staticmethod
    def _cast_dynamic_model_to_polyglot_entity(model) -> PolyglotEntity:
        """Cast the dynamic model to the polyglot entity."""

        columns: list[PolyglotEntityColumn] = []
        for prop in model.properties:
            data_type = get_data_type(prop.type, "physical")
            data_type = PolyglotEntityColumnDataType(
                data_type_name=prop.type,
                duck_db_type=data_type.get("type", None),
                duck_db_regex_pattern=data_type.get("pattern", None),
                duck_lake_type=data_type.get("type", None),
            )

            entity_column = PolyglotEntityColumn(
                name=prop.name,
                data_type=data_type,
                enum=prop.enum,
                comment=prop.description,
                nullable=prop.required,
                primary_key=prop.primary_key,
                unique_key=prop.unique,
                check_constraint=None,
                default_value=prop.default
                if prop.default and prop.default != ...
                else None,
                default_value_function=prop.physical_default_function,
            )
            columns.append(entity_column)

            polyglot_entity: PolyglotEntity = PolyglotEntity(
                name=model.entity_name,
                columns=columns,
                schema_=model.entity_schema,
            )

            return polyglot_entity

    @staticmethod
    def ygg_setup(
        recreate_existing: bool = False, config: dict[str, str | Any] | None = None
    ) -> None:
        """Build the Ygg DuckLake Setup."""

        models = DynamicModelFactory.models()
        _setup: YggSetup = YggSetup(create_ygg_folders=False, config_data=config)

        quack_list = []
        for model in models.values():
            quack = QuackConnector(
                model=Polyglot._cast_dynamic_model_to_polyglot_entity(model.settings),
                recreate_existing_entity=recreate_existing,
            )
            quack_list.append(quack)

        if quack_list:
            ...
