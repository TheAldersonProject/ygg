"""Contract Management Service."""

from typing import Type, Union

from glom import glom

import ygg.utils.files_utils as file_utils
from ygg.core.dynamic_models_factory import DynamicModelFactory, Model, YggBaseModel
from ygg.helpers.shared_model_mixin import SharedModelMixin
from ygg.services.physical_model_tools import PhysicalModelTools


class ContractManagementService:
    """
    Service for managing contracts and related data.
    """

    def __init__(self, recreate_existing: bool = False, contract_data: dict | None = None):
        """Initialize the Contract Management Service."""

        self._contract: DynamicModelFactory = DynamicModelFactory(model=Model.CONTRACT)
        self._servers: DynamicModelFactory = DynamicModelFactory(model=Model.SERVERS)
        self._schema: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA)
        self._schema_property: DynamicModelFactory = DynamicModelFactory(model=Model.SCHEMA_PROPERTY)

        self._contract_data: dict | None = contract_data
        self._create_if_not_exists(recreate_existing=recreate_existing)

    def database_persist(self) -> None:
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
                tools_ = PhysicalModelTools(model=model_.settings)
                entity: Type[Union[YggBaseModel, SharedModelMixin]] = model_.instance
                entity = entity.inflate(data=dt_, model_hydrate=model_hydrate)

                model_hydrate__ = tools_.insert_data(
                    entity=entity,
                    on_conflict_ignore=True,
                )

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
            tools = PhysicalModelTools(model=model.settings)
            tools.create_schema()
            tools.create_table(recreate_existing=recreate_existing)


if __name__ == "__main__":
    c = file_utils.get_yaml_content(
        "/Users/thiagodias/Tad/projects/tyr/ygg/dev/assets/data-models/examples/snowflake/organization_usage/usage_in_currency_daily.yaml"
    )

    m = ContractManagementService(recreate_existing=False, contract_data=c)
    m.database_persist()
