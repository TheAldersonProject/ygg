"""Dynamic models factory module is responsible for creating dynamic models based on schema definitions."""

from collections import defaultdict
from typing import Annotated, Any, Literal, Optional, Type

from glom import glom
from pydantic import ConfigDict, Field, create_model

import ygg.utils.ygg_logs as log_utils
from ygg.core.shared_model_mixin import SharedModelMixin
from ygg.helpers.data_types import get_data_type
from ygg.helpers.enums import Model
from ygg.helpers.logical_data_models import (
    ModelSettings,
    PolyglotEntity,
    PolyglotEntityColumn,
    PolyglotEntityColumnDataType,
    YggBaseModel,
    YggConfig,
)

logs = log_utils.get_logger(logger_name="DynamicModelFactory")


class DataContractLoader:
    """Dynamic Models Factory."""

    def __init__(
        self,
        model: Model,
        data_contract_schema_config: dict,
        odcs_schema_reference: dict,
        data_contract_schema: dict,
        catalog_name: str | None = None,
    ):
        """Initialize the Dynamic Models Factory."""

        if not model:
            raise ValueError("Model not provided.")

        self._model: Model = model
        logs.debug("Initializing Dynamic Models Factory.", model=self._model.value)

        data_contract_schema_config: YggConfig = YggConfig(**data_contract_schema_config)
        self._odcs_schema: dict = odcs_schema_reference
        self._catalog_name: str = catalog_name
        self._model_commons: dict | None = data_contract_schema_config.commons if data_contract_schema_config else None
        self._data_contract_schema: dict | None = data_contract_schema
        self._model_settings: ModelSettings | None = None
        self._model_instance: Type[SharedModelMixin] | None = None
        self._model_read_instance: Type[SharedModelMixin] | None = None

        self._load_model_settings()
        self._create_model_instance()

        self._polyglot_entity: PolyglotEntity = self.cast_dynamic_model_to_polyglot_entity()
        logs.debug("Polyglot Instance Created.", instance=self.polyglot_entity.name)

    @property
    def polyglot_entity(self) -> PolyglotEntity | None:
        """Get the polyglot entity."""
        return self._polyglot_entity

    def _load_model_settings(self) -> None:
        """Loads the models schema."""

        model = self._model.value
        logs.debug("Loading specified model.", model=model)

        logs.debug("Model Schema Loaded.")

        if self._model_commons:
            logs.debug("Model Commons Loaded.")
            properties_list: list = self._data_contract_schema.get("properties", {})
            properties_list = properties_list + self._model_commons
            self._data_contract_schema["properties"] = properties_list

        model_settings = ModelSettings(**self._data_contract_schema)
        logs.debug("Model Config Loaded", model=model_settings.name)
        logs.debug("Model Properties Loaded")

        self._model_settings = model_settings

    def _create_model_instance(self) -> None:
        """Get the model instance."""

        logs.info("Creating Model Instance.", model=self._model_settings.name)
        fields_map_: dict[str, Any] = defaultdict(dict)
        read_fields_map_: dict[str, Any] = defaultdict(dict)

        for prop in self._model_settings.properties:
            if prop.odcs_schema:
                odcs_: dict = glom(self._odcs_schema, prop.odcs_schema)
                prop.alias = prop.odcs_schema.split(".")[-1] if not prop.alias else prop.alias
                prop.type = odcs_.get("type", None) if not prop.type else prop.type
                prop.default = odcs_.get("default", None) if not prop.default else prop.default
                prop.enum = odcs_.get("enum", None) if not prop.enum else prop.enum
                prop.description = odcs_.get("description", None) if not prop.description else prop.description
                prop.examples = odcs_.get("examples", None) if not prop.examples else prop.examples

                odcs_: dict = glom(self._odcs_schema, prop.odcs_schema)
                prop.required = odcs_.get("required", None) if not prop.required else prop.required

            if prop.enum and isinstance(prop.enum, list):
                dtype = Literal[tuple(prop.enum)]  # type: ignore
            else:
                dtype: dict = get_data_type(prop.type, "logical")
                dtype = dtype["type"]

            if prop.required and not prop.default:
                prop.default = ...

            field_ = Field(
                default=prop.default,
                alias=prop.alias,
                description=prop.description,
                examples=prop.examples,
                pattern=prop.pattern,
            )

            fields_map_[prop.name] = Annotated[dtype if prop.required else Optional[dtype], field_]
            read_fields_map_[prop.name] = Annotated[Optional[dtype], Field(default=None, alias=prop.name)]

        instance = create_model(
            self._model_settings.name,
            __config__=ConfigDict(title=self._model_settings.description),
            __base__=(YggBaseModel, SharedModelMixin),
            **fields_map_,
        )

        read_instance = create_model(
            f"{self._model_settings.name}Read",
            __base__=(YggBaseModel, SharedModelMixin),
            **read_fields_map_,
        )

        self._model_instance = instance
        self._model_read_instance = read_instance

        logs.debug("Instance Created.", instance=instance.__name__)
        logs.debug("Read Instance Created.", instance=read_instance.__name__)

    def cast_dynamic_model_to_polyglot_entity(self) -> PolyglotEntity:
        """Cast the dynamic model to the polyglot entity."""

        columns: list[PolyglotEntityColumn] = []
        polyglot_entity: PolyglotEntity | None = None

        model = self._model_settings

        for prop in model.properties:
            data_type = get_data_type(prop.type, "physical")
            data_type = PolyglotEntityColumnDataType(
                data_type_name=prop.type,
                duck_db_type=data_type.get("type", None),
                regex_pattern=data_type.get("pattern", None),
                duck_lake_type=data_type.get("type", None),
            )

            entity_column = PolyglotEntityColumn(
                name=prop.name,
                alias=prop.alias,
                data_type=data_type,
                enum=prop.enum,
                comment=prop.description,
                nullable=prop.required,
                primary_key=prop.primary_key,
                unique_key=prop.unique,
                check_constraint=None,
                default_value=prop.default if prop.default and prop.default != ... else None,
                default_value_function=prop.physical_default_function,
                examples=prop.examples,
            )
            columns.append(entity_column)

            polyglot_entity = PolyglotEntity(
                name=model.entity_name,
                catalog=self._catalog_name or "ygg",
                columns=columns,
                schema_=model.entity_schema,
                comment=model.description,
                update_allowed=False,
                delete_allowed=False,
            )

        return polyglot_entity
