"""Dynamic models factory module is responsible for creating dynamic models based on schema definitions."""

from collections import defaultdict
from enum import Enum
from typing import Annotated, Any, Literal, Optional, Type, Union

from glom import glom
from pydantic import BaseModel, ConfigDict, Field, create_model

import ygg.config as constants
import ygg.utils.files_utils as file_utils
import ygg.utils.ygg_logs as log_utils
from ygg.helpers.data_types import get_data_type
from ygg.helpers.shared_model_mixin import SharedModelMixin

logs = log_utils.get_logger()


class YggBaseModel(BaseModel):
    """Dynamic Models Factory Base Model."""

    model_config = ConfigDict(use_enum_values=True)


class _YggConfig(YggBaseModel):
    """Dynamic Models Factory Config."""

    version_file: str
    odcs_version: str
    odcs_schema_file: str
    models: list[str]
    commons: list[dict] | None = Field(default=None)


class ModelProperty(YggBaseModel):
    """Dynamic Models Factory Config."""

    name: str | None = Field(default=None)
    type: str | None = Field(default=None)
    pattern: str | None = Field(default=None)
    default: Any | None = Field(default=None)
    physical_default_function: str | None = Field(default=None)
    unique: bool | None = Field(default=False)
    description: str | None = Field(default=None)
    required: bool | None = Field(default=True)
    primary_key: bool | None = Field(default=False)
    alias: str | None = Field(default=None)
    enum: list | None = Field(default=None)
    odcs_schema: str | None = Field(default=None)
    skip_from_signature: bool = Field(default=False)
    skip_from_physical_model: bool = Field(default=False)
    examples: list[str] | None = Field(default=None)


class ModelSettings(YggBaseModel):
    """Model Settings Model."""

    name: str
    document_path: str
    type: str
    required: bool
    entity_name: str
    entity_type: str
    entity_schema: str
    description: str
    odcs_reference: str
    properties: list[ModelProperty]


class Model(Enum):
    """Contract Models Enum."""

    CONTRACT = "contract"
    SCHEMA = "schema"
    SCHEMA_PROPERTY = "schema_property"
    SERVERS = "servers"


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
        self._schema_config: _YggConfig | None = None
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
        configs = _YggConfig(**schema_config)

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

    def get_create_table_ddl(self, recreate_existing: bool = False) -> None:
        """Create a table statement."""
        from ygg.services.physical_model_tools import PhysicalModelTools

        tools = PhysicalModelTools(self._model_settings)
        tools.create_schema()
        tools.create_table(recreate_existing=recreate_existing)
