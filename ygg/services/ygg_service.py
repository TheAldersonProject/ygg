"""Ygg Service."""

from typing import Type, Union

from glom import glom

import ygg.utils.commons as file_utils
from ygg.config import YggGeneralConfiguration, YggSetup
from ygg.core.dynamic_odcs_models_factory import DynamicModelFactory
from ygg.core.dynamic_ygg_models_factory import YggFactory
from ygg.helpers.enums import DuckLakeDbEntityType, Model
from ygg.helpers.logical_data_models import YggBaseModel
from ygg.helpers.shared_model_mixin import SharedModelMixin
from ygg.polyglot.ducklake_connector import DuckLakeConnector
from ygg.polyglot.quack_tools import QuackConnector
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class YggService:
    """Ygg Service."""

    @staticmethod
    def setup(recreate_existing: bool = False):
        """Set up the Ygg service."""

        logs.info("Setting up Ygg Service.")

        models = DynamicModelFactory.models()
        models_list = list(models.values())
        config: YggGeneralConfiguration = YggSetup().ygg_config

        for model in models_list:
            logs.info("Setting up model", model=model.settings.name)  # type: ignore
            t = QuackConnector(
                model=DynamicModelFactory.cast_to_duck_lake_db_entity(model.settings),
                recreate_existing_entity=recreate_existing,
                catalog_name=config.lake_alias,
                connector_type=DuckLakeDbEntityType.DUCKLAKE,
            )
            t: DuckLakeConnector = t.connector  # type: ignore
            t.create_duck_lake_catalog()

            instructions: list[str] = list(t.ducklake_setup_instructions().model_dump().values())
            instructions.append(t.schema_ddl)
            instructions.append(t.entity_ddl)
            QuackConnector.execute_instructions(instructions=instructions)
            logs.info("Ygg Service setup complete for model.", model=model.settings.name)  # type: ignore

    @staticmethod
    def register_data_contract(contract_data: dict | str, insert_on_conflict_ignore: bool = True) -> None:
        """Register the data contract."""

        if not contract_data:
            logs.error("Contract data cannot be empty.")
            raise ValueError("Contract data cannot be empty.")

        if not isinstance(contract_data, dict):
            contract_data = file_utils.get_yaml_content(contract_data)
            if not isinstance(contract_data, dict):
                raise ValueError("Contract data is not a dictionary.")

        logs.debug("Contract Data Loaded.", data=contract_data)

        _contract: DynamicModelFactory = DynamicModelFactory(model=Model.CONTRACT)
        _servers: DynamicModelFactory = DynamicModelFactory(model=Model.SERVERS)
        _schema: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA)
        _schema_property: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA_PROPERTY)

        models_list = [_contract, _servers, _schema]
        edge_models_list = [_schema_property]
        model_hydrate: dict = {}

        for model in models_list:
            data = glom(contract_data, model.settings.document_path)
            if not data:
                continue

            elif not isinstance(data, list):
                data = [data]

            def save(dt_, model_):
                entity: Type[Union[YggBaseModel, SharedModelMixin]] = model_.instance
                entity = entity.inflate(data=dt_, model_hydrate=model_hydrate)

                dl = QuackConnector(
                    model=DynamicModelFactory.cast_to_duck_lake_db_entity(model_.settings),
                    recreate_existing_entity=False,
                    catalog_name="ygg_ducklake",
                    connector_type=DuckLakeDbEntityType.DUCKLAKE,
                )
                dl: DuckLakeConnector = dl.connector
                lake_instructions: list[str] = list(dl.ducklake_setup_instructions().model_dump().values())
                lake_instructions.append(dl.schema_ddl)
                lake_instructions.append(dl.entity_ddl)

                db = QuackConnector(
                    model=DynamicModelFactory.cast_to_duck_lake_db_entity(model_.settings),
                    recreate_existing_entity=False,
                    catalog_name="ygg_ducklake",
                    connector_type=DuckLakeDbEntityType.DUCKDB,
                )

                db: DuckLakeConnector = db.connector
                db_instructions: list[str] = [db.schema_ddl, db.entity_ddl]

                model_hydrate__ = DynamicModelFactory.upsert_data_contract_entity(
                    model=model_.settings,
                    entity=entity,
                    on_conflict_ignore=insert_on_conflict_ignore,
                    ducklake_instructions=lake_instructions,
                    duckdb_instructions=db_instructions,
                    catalog_name="ygg_ducklake",
                )

                if model_ is _contract:
                    _contract_id = entity.id  # type: ignore
                    _contract_version = entity.version  # type: ignore

                return model_hydrate__

            def iterate_and_save(dt, model_):
                for d in dt:
                    model_hydrate_ = save(d, model_)
                    if model not in edge_models_list:
                        model_hydrate.update(model_hydrate_)

                    if model_ is _schema:
                        schema_property_ = _schema_property
                        schema_properties_ = glom(d, schema_property_.settings.document_path)

                        if schema_properties_:
                            iterate_and_save(schema_properties_, schema_property_)

            iterate_and_save(data, model)

    @staticmethod
    def build_contract(contract_id: str | None = None, contract_version: str | None = None) -> None:
        """Build the contract by creating and populating the necessary models."""

        logs.info("Hello from the build contract method")
        factory = YggFactory(
            contract_id=contract_id,
            contract_version=contract_version,
            db_url="",
        )
        factory.build_contract()
