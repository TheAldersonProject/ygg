"""Contract Management Service."""

from pathlib import Path
from typing import Type, Union

from glom import glom

import ygg.utils.files_utils as file_utils
from ygg import config
from ygg.core.dynamic_models_factory import DynamicModelFactory, Model, YggBaseModel
from ygg.core.ygg_factory import YggFactory
from ygg.helpers.shared_model_mixin import SharedModelMixin
from ygg.services.physical_model_tools import PhysicalModelTools
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class ContractManagerService:
    """
    Service for managing contracts and related data.
    """

    def __init__(
        self, recreate_existing: bool = False, contract_data: dict | str | None = None, db_url: str | None = None
    ):
        """Initialize the Contract Management Service."""

        self._contract: DynamicModelFactory = DynamicModelFactory(model=Model.CONTRACT)
        self._servers: DynamicModelFactory = DynamicModelFactory(model=Model.SERVERS)
        self._schema: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA)
        self._schema_property: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA_PROPERTY)

        self._contract_data: dict | str | None = contract_data

        self._db_url: str | Path = db_url or config.DATABASE_FOLDER / "db.duckdb"

        self._contract_id: str | None = None
        self._contract_version: str | None = None

        self._get_contract_data()
        self._create_if_not_exists(recreate_existing=recreate_existing)

    def _get_contract_data(self) -> dict:
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

    def build_contract(self) -> None:
        """Build the contract by creating and populating the necessary models."""

        self._database_persist()
        factory = YggFactory(
            contract_id=self._contract_id,
            contract_version=self._contract_version,
            db_url=self._db_url,
        )
        factory.build_ygg_contract()

    def _database_persist(self) -> None:
        """Save the contract data to the database."""

        if self._contract_data is None:
            raise ValueError("Contract data is not set. Please set the contract data before saving.")

        models_list = [self._contract, self._servers, self._schema]
        edge_models_list = [self._schema_property]
        model_hydrate: dict = {}

        for model in models_list:
            data = glom(self._contract_data, model.settings.document_path)

            if not data:
                continue

            elif not isinstance(data, list):
                data = [data]

            def save(dt_, model_):
                tools_ = PhysicalModelTools(model=model_.settings, db_path=self._db_url)
                entity: Type[Union[YggBaseModel, SharedModelMixin]] = model_.instance
                entity = entity.inflate(data=dt_, model_hydrate=model_hydrate)

                model_hydrate__ = tools_.insert_data(
                    entity=entity,
                    on_conflict_ignore=False,
                )

                if model_ is self._contract:
                    self._contract_id = entity.id  # type: ignore
                    self._contract_version = entity.version  # type: ignore

                return model_hydrate__

            def iterate_save(dt, model_):
                for d in dt:
                    model_hydrate_ = save(d, model_)
                    if model not in edge_models_list:
                        model_hydrate.update(model_hydrate_)

                    if model_ is self._schema:
                        schema_property_ = self._schema_property
                        schema_properties_ = glom(d, schema_property_.settings.document_path)

                        if schema_properties_:
                            iterate_save(schema_properties_, schema_property_)

            iterate_save(data, model)

    def _create_if_not_exists(self, recreate_existing: bool = False) -> None:
        """Create the contract if it does not exist."""

        models_list = [self._contract, self._servers, self._schema, self._schema_property]
        for model in models_list:
            tools = PhysicalModelTools(model=model.settings, db_path=self._db_url)
            tools.create_schema()
            tools.create_table(recreate_existing=recreate_existing)


if __name__ == "__main__":
    c = file_utils.get_yaml_content("/data/contracts/snowflake/organization_usage/input.yaml")

    m = ContractManagerService(recreate_existing=True, contract_data=c)
    m.build_contract()
