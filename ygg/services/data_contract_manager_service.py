"""Contract Management Service."""

from pathlib import Path
from typing import Type, Union

from glom import glom

import ygg.utils.commons as file_utils
from ygg.config import YggSetup
from ygg.core.dynamic_odcs_models_factory import (
    DynamicModelFactory,
    Model,
    YggBaseModel,
)
from ygg.core.dynamic_ygg_models_factory import YggFactory
from ygg.helpers.logical_data_models import SharedModelMixin
from ygg.helpers.odcs_duckdb_tools import DuckDbTools
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DataContractManagerService:
    """
    Service for managing contracts and related data.
    """

    def __init__(
        self,
        insert_on_conflict_ignore: bool = True,
        recreate_existing: bool = False,
        enforce_create_schema_if_not_exists: bool = False,
        contract_data: dict | str | None = None,
    ):
        """Initialize the Contract Management Service."""

        self._ygg_setup: YggSetup = YggSetup(create_ygg_folders=True)

        self._sink_path: Path = self._ygg_setup.sink_config.location
        self._ygg_db_url: Path = self._ygg_setup.database_config.database_url
        self._contract_data: dict | str | None = contract_data

        self._contract: DynamicModelFactory = DynamicModelFactory(model=Model.CONTRACT)
        self._servers: DynamicModelFactory = DynamicModelFactory(model=Model.SERVERS)
        self._schema: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA)
        self._schema_property: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA_PROPERTY)

        self._contract_id: str | None = None
        self._contract_version: str | None = None

        self._recreate_existing: bool = recreate_existing
        self._insert_on_conflict_ignore: bool = insert_on_conflict_ignore
        self._enforce_create_schema_if_not_exists: bool = enforce_create_schema_if_not_exists

    def _get_contract_data(self) -> None:
        """Get the contract data."""

        logs.debug("File path", path=self._contract_data)

        if isinstance(self._contract_data, dict):
            data = self._contract_data

        else:
            data = file_utils.get_yaml_content(self._contract_data)
            if not isinstance(data, dict):
                raise ValueError("Contract data is not a dictionary.")

        logs.debug("Contract Data Loaded.", data=data)
        self._contract_data = data

    def _database_persist_data_contract(self) -> None:
        """Save the contract data to the database."""

        if self._contract_data is None:
            raise ValueError("Contract data is not set. Please set the contract data before saving.")

        models_list = [self._contract, self._servers, self._schema]
        edge_models_list = [self._schema_property]
        model_hydrate: dict = {}

        self._create_ygg_db_if_not_exists()

        for model in models_list:
            data = glom(self._contract_data, model.settings.document_path)

            if not data:
                continue

            elif not isinstance(data, list):
                data = [data]

            def save(dt_, model_):
                tools_ = DuckDbTools(model=model_.settings, ygg_db_url=self._ygg_db_url)
                entity: Type[Union[YggBaseModel, SharedModelMixin]] = model_.instance
                entity = entity.inflate(data=dt_, model_hydrate=model_hydrate)

                model_hydrate__ = tools_.insert_data(
                    entity=entity,
                    on_conflict_ignore=self._insert_on_conflict_ignore,
                )

                if model_ is self._contract:
                    self._contract_id = entity.id  # type: ignore
                    self._contract_version = entity.version  # type: ignore

                return model_hydrate__

            def iterate_and_save(dt, model_):
                for d in dt:
                    model_hydrate_ = save(d, model_)
                    if model not in edge_models_list:
                        model_hydrate.update(model_hydrate_)

                    if model_ is self._schema:
                        schema_property_ = self._schema_property
                        schema_properties_ = glom(d, schema_property_.settings.document_path)

                        if schema_properties_:
                            iterate_and_save(schema_properties_, schema_property_)

            iterate_and_save(data, model)

    def _create_ygg_db_if_not_exists(self) -> None:
        """Create the contract if it does not exist."""

        models_list = [
            self._contract,
            self._servers,
            self._schema,
            self._schema_property,
        ]
        for model in models_list:
            tools = DuckDbTools(model=model.settings, ygg_db_url=self._ygg_db_url)
            tools.create_table(
                recreate_existing=self._recreate_existing,
                enforce_create_schema_if_not_exists=self._enforce_create_schema_if_not_exists,
            )

    def build_contract(self) -> None:
        """Build the contract by creating and populating the necessary models."""

        self._get_contract_data()
        self._database_persist_data_contract()
        factory = YggFactory(
            contract_id=self._contract_id,
            contract_version=self._contract_version,
            db_url=self._ygg_db_url,
        )
        factory.build_contract(sink_path=self._sink_path)
