"""Ygg Factory Module

This module provides a factory class for creating Ygg objects based on configuration data.
"""

from pathlib import Path
from typing import Any, Type

import duckdb
from numpy import ndarray

from ygg.config import YggGeneralConfiguration, YggSetup
from ygg.core.dynamic_odcs_models_factory import DynamicModelFactory
from ygg.helpers.data_types import get_data_type
from ygg.helpers.enums import DuckLakeDbEntityType, Model
from ygg.helpers.logical_data_models import (
    ModelSettings,
    PolyglotEntity,
    PolyglotEntityColumn,
    PolyglotEntityColumnDataType,
    YggBaseModel,
)
from ygg.polyglot.ducklake_connector import DuckLakeConnector
from ygg.polyglot.helper import Helper
from ygg.polyglot.quack_tools import QuackConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="YggFactory")


class YggFactory:
    """Factory for creating Ygg objects."""

    def __init__(self, contract_id: str, contract_version: str):
        """Initialize the Ygg Factory."""

        logs.debug(f"Initializing Ygg Factory for contract: {contract_id} version: {contract_version}")

        if not contract_id or not contract_version:
            logs.error("Contract ID and version cannot be empty.")
            raise ValueError("Contract ID and version cannot be empty.")

        self._contract_id = contract_id
        self._contract_version = contract_version
        self._db_url = ":memory:"

        self._contract: Type[YggBaseModel] | None = None
        self._servers: dict[str, Type[YggBaseModel]] = {}
        self._schemas: dict[str, list[Type[YggBaseModel]]] = {}
        self._schema_properties: dict[str, list[Type[YggBaseModel]]] = {}

        self._config: YggGeneralConfiguration = YggSetup().ygg_config

        logs.debug("Ygg Factory Initialized.")
        self._load_contract()
        self._load_contract_servers()
        self._load_contract_schemas()

    def _load(self, settings: ModelSettings, query: str) -> list[dict]:
        """Loads data from DuckLake."""

        result = self.run_lake_statement(statement=query, settings=settings)
        return result

    def _load_contract(self) -> None:
        """Load the contract."""

        _contract = DynamicModelFactory(model=Model.CONTRACT)
        settings = _contract.settings
        statement = f"""
            select  * 
            from    {self._config.lake_alias}.{settings.entity_schema}.{settings.entity_name} 
            where   id = '{self._contract_id}' 
            and     version = '{self._contract_version}';
        """

        result = self._load(query=statement, settings=settings)
        self._contract = _contract.read_instance(**result[0])

        logs.debug("Contract Loaded.", contract=self._contract)

    def _load_contract_servers(self) -> None:
        """Load the contract servers."""

        _contract_servers = DynamicModelFactory(model=Model.SERVERS)
        settings = _contract_servers.settings

        statement = f"""
            select  * 
            from    {self._config.lake_alias}.{settings.entity_schema}.{settings.entity_name}
            where   contract_id = '{self._contract.id}' 
            and     contract_record_hash = '{self._contract.record_hash}';
        """

        result = self._load(query=statement, settings=settings)
        servers: dict = {}
        if result:
            for r in result:
                server = _contract_servers.read_instance(**r)
                servers[server.id] = server

        self._servers = servers or {}
        logs.debug("Servers Loaded.", contract=self._servers)

    def _load_contract_schema_properties(self, schema_id: str, schema_record_hash: str) -> None:
        """Load the contract schema properties."""

        _schema_properties = DynamicModelFactory(model=Model.SCHEMA_PROPERTY)
        settings = _schema_properties.settings
        statement = f"""
            select  * 
            from    {self._config.lake_alias}.{settings.entity_schema}.{settings.entity_name}
            where   contract_schema_id = '{schema_id}' 
            and     contract_schema_record_hash = '{schema_record_hash}';
        """

        result = self._load(query=statement, settings=settings)
        properties: list = []
        if result:
            for r in result:
                _schema_property = _schema_properties.read_instance(**r)
                properties.append(_schema_property.model_dump())

        logs.debug("Schema Properties Loaded.", schema_id=schema_id)
        self._schema_properties[schema_id] = properties

    def _load_contract_schemas(self) -> None:
        """Load the contract schema."""

        _schema = DynamicModelFactory(model=Model.SCHEMA)
        settings = _schema.settings
        statement = f"""
            select  * 
            from    {self._config.lake_alias}.{settings.entity_schema}.{settings.entity_name}
            where   contract_id = '{self._contract.id}' 
            and     contract_record_hash = '{self._contract.record_hash}';
        """

        result = self._load(query=statement, settings=settings)
        schemas: dict = {}
        if result:
            for r in result:
                properties = self._load_contract_schema_properties(
                    schema_id=r["id"], schema_record_hash=r["record_hash"]
                )
                r["properties"] = properties
                schema = _schema.read_instance(**r)
                schemas[schema.id] = schema

        self._schemas = schemas or {}
        logs.debug("Schemas Loaded.", schemas=self._schemas)

    @staticmethod
    def _get_sink_folder_path(sink_path: str | Path) -> Path:
        """Get the sink path."""

        path_ = sink_path / "contracts"
        return path_

    def run_lake_statement(self, statement: str, settings: ModelSettings) -> list[dict]:
        """Run a SQL statement against the database."""

        content: Any = None
        dl = QuackConnector(
            model=Helper.cast_to_polyglot_entity(settings),
            recreate_existing_entity=False,
            catalog_name=self._config.lake_alias,
            connector_type=DuckLakeDbEntityType.DUCKLAKE,
        )
        dl: DuckLakeConnector = dl.connector
        lake_instructions: list[str] = list(dl.ducklake_setup_instructions().model_dump().values())
        lake_instructions.append(dl.schema_ddl)
        lake_instructions.append(dl.entity_ddl)

        def lower_json_keys(obj):
            if isinstance(obj, dict):
                return {k.lower(): lower_json_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list) or isinstance(obj, ndarray):
                return [lower_json_keys(i) for i in obj]
            else:
                return obj

        with duckdb.connect(":memory:", read_only=False) as con:
            try:
                for instruction in lake_instructions:
                    logs.debug("Executing instruction.", instruction=instruction)
                    con.execute(instruction)

                logs.debug("Executing SQL statement.", statement=statement)
                content = con.sql(statement)

                content = content.to_df()
                content = content.rename(columns=str.lower)

                object_cols = content.select_dtypes(include=["object"]).columns
                for o in object_cols:
                    content[o] = content[o].apply(lower_json_keys)
                content = content.to_dict("records")
            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}", error=str(e))
                raise e

        return content

    def register_contract_physical_model(self) -> None:
        """Register the contract physical model."""

        catalog_name: str = self._contract.tenant  # type: ignore
        schema_name: str = self._contract.domain  # type: ignore
        if self._schemas and isinstance(self._schemas, dict):
            for k, sc in self._schemas.items():
                columns: list[PolyglotEntityColumn] = []
                for c in self._schema_properties.get(sc.id, []):
                    dt: dict = get_data_type(c["logical_type"], "physical")
                    pcd = PolyglotEntityColumnDataType(
                        data_type_name=c["logical_type"],
                        duck_db_type=c["physical_type"] or dt.get("type", None) if dt else c["logical_type"],
                        duck_db_regex_pattern=dt.get("pattern", None) if dt else None,
                        duck_lake_type=c["physical_type"] or dt.get("type", c["logical_type"]),
                    )
                    pc = PolyglotEntityColumn(
                        name=c["physical_name"],
                        data_type=pcd,
                        enum=None,
                        comment=c["description"],
                        nullable=c["is_required"] or False,
                        primary_key=c["primary_key"] or False,
                        unique_key=c["is_unique"] or False,
                        check_constraint="",
                        default_value=None,
                        default_value_function=None,
                    )
                    columns.append(pc)

                entity: PolyglotEntity = PolyglotEntity(
                    name=sc.physical_name,
                    schema_=schema_name,
                    comment=sc.description,
                    columns=columns,
                )
                dl = QuackConnector(
                    model=entity,
                    recreate_existing_entity=True,
                    catalog_name=catalog_name,
                    connector_type=DuckLakeDbEntityType.DUCKLAKE,
                )
                dl: DuckLakeConnector = dl.connector
                dl.create_duck_lake_catalog()
                lake_instructions: list[str] = list(dl.ducklake_setup_instructions().model_dump().values())
                lake_instructions.append(dl.schema_ddl)
                lake_instructions.append(dl.entity_ddl)
                QuackConnector.execute_instructions(instructions=lake_instructions)

                for i in lake_instructions:
                    print(i)
