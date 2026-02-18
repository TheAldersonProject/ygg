"""Dynamic models factory module is responsible for creating dynamic models based on schema definitions."""

from typing import Self

from glom import glom
from midgard.logs import Logger
from polyglot.model.polyglot_config import PolyglotConfig
from polyglot.model.polyglot_entity import ColumnDataType as PolyglotEntityColumnDataType
from polyglot.model.polyglot_entity import Entity as PolyglotEntity
from polyglot.model.polyglot_entity import EntityColumn as PolyglotEntityColumn
from polyglot.polyglot import Polyglot

from ygg.data_models import ModelSettings

logs = Logger.get_logger(logger_name="DynamicModelFactory")


class DataContractLoader:
    """Dynamic Models Factory."""

    def __init__(self, config):
        """Initialize the Dynamic Models Factory."""

        from ygg.contract import YggConfig

        self._config: YggConfig = config
        logs.debug("Initializing Dynamic Models Factory.")

        self._data_contract: dict | None = None
        self._data_contract_list: list = self._config.data_contracts

        self._odcs_schema: dict = self._config.odcs_schema
        self._catalog_name: str = "ygg"
        self._model_commons: dict | None = self._config.additional_columns
        self._model_settings: ModelSettings | None = None

        # self._parse_model()

    @property
    def polyglot_entity(self) -> PolyglotEntity | None:
        """Get the polyglot entity."""
        return self._polyglot_entity

    def _persist(self) -> dict:
        """Set up the data contract model."""

        # self._load_model_settings()
        # self._parse_model()
        #
        # polyglot_entity: PolyglotEntity = self._cast_dynamic_model_to_polyglot_entity()
        # polyglot_config = PolyglotConfig(
        #     polyglot_entity=polyglot_entity,
        #     catalog_database_config=self._config.ygg_database,
        #     object_storage_config=self._config.ygg_object_storage,
        #     recreate_existing_entity=True,
        #     duckdb_modules=["httpfs", "postgres", "ducklake"],
        #     cache_folder="/home/thiago/projects/.ygg/local-dev/cache",
        # )
        #
        # if not isinstance(data, list):
        #     data = [data]
        #
        # for d in data:
        #     p = Polyglot(config=polyglot_config)
        #     p.create()
        #
        #     result = (
        #         Polyglot(config=polyglot_config)
        #         .driver.inflate(data=d, polyglot_entity=polyglot_entity, model_hydrate=model_hydrate)
        #         .write()
        #     )
        #     # model_hydrate = model_hydrate | result
        #     logs.info("Data Contract Model written.")
        #
        #     if contract_model.get("name", "").lower() == "schema":
        #         self._data_contract = self._config.schema_property_blueprint
        #         data_ = glom(d, self._data_contract.get("document_path"))
        #         for dt in data_:
        #             self._persist(model_hydrate, dt, self._config.schema_property_blueprint)
        #
        #         self._data_contract = contract_model

        model_hydrate: dict = {}
        for model_ in self._data_contract_list:
            self._data_contract = model_

            def save(dt_):
                self._load_model_settings()
                self._parse_model()

                polyglot_entity: PolyglotEntity = self._cast_dynamic_model_to_polyglot_entity()
                polyglot_config = PolyglotConfig(
                    polyglot_entity=polyglot_entity,
                    catalog_database_config=self._config.ygg_database,
                    object_storage_config=self._config.ygg_object_storage,
                    recreate_existing_entity=True,
                    duckdb_modules=["httpfs", "postgres", "ducklake"],
                    cache_folder="/home/thiago/projects/.ygg/local-dev/cache",
                )

                return (
                    Polyglot(config=polyglot_config)
                    .driver.inflate(data=dt_, polyglot_entity=polyglot_entity, model_hydrate=model_hydrate)
                    .write()
                )

            edge_models_list = ["schema_property", "servers"]

            def iterate_and_save(dt, contract_model):
                dt = glom(dt, model_.get("document_path"))
                if not isinstance(dt, list):
                    dt = [dt]
                for d in dt:
                    model_hydrate_ = save(d)
                    if contract_model not in edge_models_list:
                        model_hydrate.update(model_hydrate_)

                    if contract_model.get("name", "").lower() == "schema":
                        schema_property_ = self._config.schema_property_blueprint
                        self._data_contract = schema_property_
                        schema_properties_ = glom(d, schema_property_.get("document_path"))

                        if schema_properties_:
                            iterate_and_save(schema_properties_, schema_property_)

                        self._data_contract = model_

            iterate_and_save(self._config.contract, model_)

        return model_hydrate

    def create(self, polyglot_entity: PolyglotEntity) -> Self:
        """Create the data contract model."""

        polyglot_config = PolyglotConfig(
            polyglot_entity=polyglot_entity,
            catalog_database_config=self._config.ygg_database,
            object_storage_config=self._config.ygg_object_storage,
            recreate_existing_entity=True,
            duckdb_modules=["httpfs", "postgres", "ducklake"],
            cache_folder="/home/thiago/projects/.ygg/local-dev/cache",
        )

    def write(self) -> Self:
        """Set up the data contract."""

        # model_hydrate = {}
        # for contract_model in self._data_contract_list:
        #     self._data_contract = contract_model
        #
        #     data = glom(self._config.contract, self._data_contract.get("document_path"))
        #
        #     result = self._persist(model_hydrate, data, contract_model)
        #     model_hydrate = model_hydrate | result

        self._persist()

    def _load_model_settings(self) -> ModelSettings:
        """Loads the models schema."""

        logs.debug("Model Schema Loaded.")

        if self._model_commons:
            logs.debug("Model Commons Loaded.")
            properties_list: list = self._data_contract.get("properties", {})
            properties_list = properties_list + self._model_commons
            self._data_contract["properties"] = properties_list

        model_settings = ModelSettings(**self._data_contract)
        logs.debug("Model Config Loaded", model=model_settings.name)
        logs.debug("Model Properties Loaded")

        self._model_settings = model_settings

    def _parse_model(self) -> None:
        """Get the model instance."""

        logs.info("Parsing data contract.", model=self._model_settings.name)

        for prop in self._model_settings.properties:
            if prop.odcs_schema:
                odcs_: dict = glom(self._odcs_schema, prop.odcs_schema)
                prop.alias = prop.odcs_schema.split(".")[-1] if not prop.alias else prop.alias
                prop.type = odcs_.get("type", None) if not prop.type else prop.type
                prop.default = odcs_.get("default", None) if not prop.default else prop.default
                prop.enum = odcs_.get("enum", None) if not prop.enum else prop.enum
                prop.description = odcs_.get("description", None) if not prop.description else prop.description
                prop.examples = odcs_.get("examples", None) if not prop.examples else prop.examples
                prop.required = odcs_.get("required", None) if not prop.required else prop.required

    def _cast_dynamic_model_to_polyglot_entity(self) -> PolyglotEntity:
        """Cast the dynamic model to the polyglot entity."""

        columns: list[PolyglotEntityColumn] = []
        polyglot_entity: PolyglotEntity | None = None

        model = self._model_settings

        for prop in model.properties:
            data_type = PolyglotEntityColumnDataType(
                name=prop.type,
                logical=prop.type,
                specific_physical=None,
                regex_pattern=None,
            )

            entity_column = PolyglotEntityColumn(
                name=prop.name,
                alias=prop.alias,
                data_type=data_type,
                enum=prop.enum,
                comment=prop.description,
                nullable=not prop.required,
                primary_key=prop.primary_key,
                unique_key=prop.unique,
                check_constraint=None,
                default_value=prop.default if prop.default and prop.default != ... else None,
                default_value_function=prop.physical_default_function,
                examples=prop.examples,
            )
            columns.append(entity_column)

        return PolyglotEntity(
            name=model.entity_name,
            catalog=self._catalog_name,
            columns=columns,
            schema_=model.entity_schema,
            comment=model.description,
            update_allowed=False,
            delete_allowed=False,
        )
