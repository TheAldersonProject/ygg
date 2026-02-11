"""Dynamic models factory module is responsible for creating dynamic models based on schema definitions."""

import hashlib
from collections import defaultdict
from textwrap import dedent
from typing import Annotated, Any, Literal, Optional, Type, Union

import duckdb
from glom import glom
from pydantic import ConfigDict, Field, create_model

import ygg.config as constants
import ygg.utils.commons as file_utils
import ygg.utils.ygg_logs as log_utils
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
from ygg.helpers.shared_model_mixin import SharedModelMixin

logs = log_utils.get_logger()


class DynamicModelFactory:
    """Dynamic Models Factory."""

    def __init__(self, model: Model):
        """Initialize the Dynamic Models Factory."""

        if not model:
            raise ValueError("Model not provided.")

        self._model: Model = model

        logs.debug("Initializing Dynamic Models Factory.", model=self._model.value)

        self._odcs_schema_path: str = constants.ODCS_SCHEMA_FOLDER
        self._models_schema_path: str = constants.YGG_SCHEMAS_FOLDER
        self._models_config_file: str = constants.YGG_SCHEMA_CONFIG_FILE
        self._schema_config: YggConfig | None = None
        self._schema_version: str | None = None
        self._odcs_schema: dict | None = None

        self._model_settings: ModelSettings | None = None
        self._model_instance: Type[SharedModelMixin] | None = None
        self._model_read_instance: Type[SharedModelMixin] | None = None

        self._load_models_configuration()
        self._load_odcs_schema()
        self._load_model_settings()
        self._create_model_write_instance()

    @property
    def instance(self) -> Type[Union[YggBaseModel, SharedModelMixin]]:
        """Get the model instance."""

        return self._model_instance

    @property
    def read_instance(self) -> Type[Union[YggBaseModel, SharedModelMixin]]:
        """Get the model instance."""

        return self._model_read_instance

    @property
    def settings(self) -> ModelSettings:
        """Get the model settings."""

        return self._model_settings

    @staticmethod
    def _get_logical_data_type(data_type: str) -> dict:
        """Get the logical data type."""

        dtype: dict = get_data_type(data_type, "logical")
        return dtype

    @staticmethod
    def models() -> dict[str, Type["DynamicModelFactory"]]:
        """Get the models map."""

        return {
            Model.CONTRACT: DynamicModelFactory(model=Model.CONTRACT),
            Model.SERVERS: DynamicModelFactory(model=Model.SERVERS),
            Model.SCHEMA: DynamicModelFactory(model=Model.SCHEMA),
            Model.SCHEMA_PROPERTY: DynamicModelFactory(model=Model.SCHEMA_PROPERTY),
        }

    @staticmethod
    def cast_to_duck_lake_db_entity(model) -> PolyglotEntity:
        """Cast the model to a DuckLakeDbEntity."""

        list_of_columns: list[PolyglotEntityColumn] = []
        for property_ in model.properties:
            data_type = get_data_type(property_.type, "physical")
            column_data_type = PolyglotEntityColumnDataType(
                data_type_name=property_.type,
                duck_db_type=data_type["type"],
                duck_db_regex_pattern=data_type.get("pattern", None),
                duck_lake_type=data_type["type"],
            )

            c: PolyglotEntityColumn = PolyglotEntityColumn(
                name=property_.name,
                data_type=column_data_type,
                enum=property_.enum,
                comment=property_.description,
                nullable=property_.required,
                primary_key=property_.primary_key,
                unique_key=property_.unique,
                check_constraint=None,
                default_value=property_.default if property_.default and property_.default != ... else None,
                default_value_function=property_.physical_default_function,
            )
            list_of_columns.append(c)

        _duck_lake_db_entity: PolyglotEntity = PolyglotEntity(
            name=model.entity_name, columns=list_of_columns, schema_=model.entity_schema
        )

        return _duck_lake_db_entity

    def _get_schema_version(self) -> str:
        """Get the schema version."""

        version_file_path: str = f"{self._models_schema_path}/{self._schema_config.version_file}"
        version = file_utils.get_file_string_content(version_file_path)

        logs.debug("Models Schema Version Loaded.", version=version)

        return version

    def _load_models_configuration(self) -> None:
        """Loads the models configuration."""

        schema_config: dict = file_utils.get_yaml_content(self._models_config_file)
        if not schema_config:
            raise ValueError("Models Schema not found.")

        logs.debug("Models Schema Loaded.", models=schema_config)
        configs = YggConfig(**schema_config)

        self._schema_config = configs
        self._schema_version = self._get_schema_version()

    def _load_odcs_schema(self) -> None:
        """Loads the ODCS Schema."""

        odcs_schema_file_path: str = f"{self._odcs_schema_path}/{self._schema_config.odcs_schema_file}"
        schema_content = file_utils.get_json_file_content(odcs_schema_file_path)

        self._odcs_schema = schema_content

    def _load_model_settings(self) -> None:
        """Loads the models schema."""

        model = self._model.value
        logs.debug("Loading specified model.", model=model)

        logs.debug("Loading Models Schema.")

        model_config_file_path: str = f"{self._models_schema_path}/{model}.yaml"
        model_config_dict = file_utils.get_yaml_content(model_config_file_path)
        logs.debug("Model Schema Loaded.", model=model, config=model_config_dict)

        if self._schema_config.commons:
            properties_list: list = model_config_dict.get("properties", {})
            properties_list = properties_list + self._schema_config.commons
            model_config_dict["properties"] = properties_list

        model_settings = ModelSettings(**model_config_dict)
        logs.debug("Model Config Loaded", model=model_settings.name)
        logs.debug("Model Properties Loaded", model=model_settings.properties)

        self._model_settings = model_settings

    def _create_model_write_instance(self) -> None:
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
                logical_type_ = Literal[tuple(prop.enum)]  # type: ignore
            else:
                logical_type_ = DynamicModelFactory._get_logical_data_type(prop.type)["type"]

            if prop.required and not prop.default:
                prop.default = ...

            field_ = Field(
                default=prop.default,
                alias=prop.alias,
                description=prop.description,
                examples=prop.examples,
                pattern=prop.pattern,
            )

            fields_map_[prop.name] = Annotated[logical_type_ if prop.required else Optional[logical_type_], field_]
            read_fields_map_[prop.alias or prop.name] = Annotated[
                Optional[logical_type_], Field(default=None, alias=prop.name.upper())
            ]

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

    @staticmethod
    def upsert_data_contract_entity(
        model: ModelSettings,
        entity: Type[Union[YggBaseModel, SharedModelMixin]],
        ygg_db_url: str = ":memory:",
        on_conflict_ignore: bool = True,
        catalog_name: str | None = None,
        duckdb_instructions: list[str] | None = None,
        ducklake_instructions: list[str] | None = None,
    ) -> dict:
        """Insert data into the physical model."""

        entity_schema: str = model.entity_schema
        entity_name: str = model.entity_name
        values_map = entity.model_dump()

        affected_rows: int = 0
        hydrate_return: dict = {}

        empties_ = [k for k, v in values_map.items() if v in (None, "None", "")]
        drop_columns: list = [c.name for c in model.properties if c.skip_from_physical_model or c.name in empties_]
        for drop in drop_columns or []:
            if drop in values_map:
                del values_map[drop]

        signature_skip_columns = [c.name for c in model.properties if c.skip_from_signature]
        values_signature = "".join(
            list(sorted([str(v) for k, v in values_map.items() if v and k not in signature_skip_columns]))
        )

        record_hash = str(hashlib.md5(str(values_signature).encode()).hexdigest())
        values_map["record_hash"] = record_hash

        pk_columns = [c.name for c in model.properties if c.primary_key]
        for pk in pk_columns:
            hydrate_return[f"{entity_name}_{pk}"] = values_map.get(pk)

        duckdb_header: list[str] = [f for f in list(entity.model_fields.keys()) if f in list(values_map.keys())]
        params: list[str] = ", ".join(["?" for f in duckdb_header])
        duckdb_header_string: str = ", ".join(duckdb_header)

        values_list = list(values_map.values())
        values_list = [None if v == "None" else v for v in values_list]
        duckdb_statement: str = f"""
            INSERT INTO {entity_schema}.{entity_name} ({duckdb_header_string}) 
            VALUES ({params}) {" ON CONFLICT DO NOTHING" if on_conflict_ignore else ""}
        """
        duckdb_statement = dedent(duckdb_statement)

        ducklake_merge_constraints = "".join([f" and t.{pk} = s.{pk}" for pk in pk_columns])
        ducklake_merge_into: str = f"""
            MERGE INTO {catalog_name}.{entity_schema}.{entity_name} t 
            USING {entity_schema}.{entity_name} s 
            ON (1=1 {ducklake_merge_constraints}) 
            WHEN MATCHED THEN UPDATE 
            WHEN NOT MATCHED THEN INSERT
        """
        ducklake_merge_into = dedent(ducklake_merge_into)

        with duckdb.connect(ygg_db_url, read_only=False) as con:
            try:
                logs.debug("Executing SQL statement.")

                for instruction in duckdb_instructions:
                    logs.debug("Executing DuckDb instruction.", instruction=instruction)
                    con.execute(instruction)

                con.execute(duckdb_statement, values_list)
                logs.debug("SQL statement executed successfully.")

                if ducklake_instructions:
                    for instruction in ducklake_instructions:
                        logs.debug("Executing DuckLake instruction.", instruction=instruction)
                        con.execute(instruction)

                    con.execute(ducklake_merge_into)

                affected_rows += 1

            except Exception as e:
                logs.error(
                    f"Error executing SQL statement: {e}",
                    header_string=duckdb_header_string,
                    values=values_map,
                )
                raise e

        logs.debug("Data Inserted.", affected_rows=affected_rows)

        return hydrate_return
