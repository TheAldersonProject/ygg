"""Ygg Service"""

from midgard.logs import Logger
from polyglot.model.database_config import DatabaseConfig
from polyglot.model.object_storage_config import S3Config
from pydantic import Field

from ygg.data_contract_loader import DataContractLoader
from ygg.data_models import YggBaseModel


class Config(YggBaseModel):
    """Service Config"""

    ygg_database: DatabaseConfig
    ygg_object_storage: S3Config

    contract: dict | None = Field(default=None)
    contract_blueprint: dict
    servers_blueprint: dict
    schema_blueprint: dict
    schema_property_blueprint: dict

    additional_columns: list | None = Field(default=None)
    odcs_schema: dict


class YggConfig(Config):
    """Ygg Service Config"""

    data_contracts: list[dict] = Field(default_factory=list)


class Contract:
    """Ygg Service"""

    def __init__(self, config: YggConfig):
        """Initialize the Ygg Service."""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.config = config

        contracts_list = [
            self.config.contract_blueprint,
            self.config.servers_blueprint,
            self.config.schema_blueprint,
        ]
        ygg_config_data = config.model_dump()
        ygg_config_data = ygg_config_data | {"data_contracts": contracts_list}
        self._ygg_config = YggConfig(**ygg_config_data)

        self.logs.debug("Ygg Config Loaded", config=self._ygg_config)

    @property
    def ygg_config(self) -> YggConfig:
        """Get the Ygg Config."""
        return self._ygg_config

    @property
    def data_contract_loader(self) -> DataContractLoader:
        """Get the Data Contract Loader."""

        return DataContractLoader(self._ygg_config)
