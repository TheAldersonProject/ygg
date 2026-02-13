"""Project configuration."""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ygg.utils.commons import get_yaml_content, replace_placeholders_with_env_values
from ygg.utils.custom_decorators import singleton

CURRENT_FILE_PATH = Path(__file__).resolve()
SRC_FOLDER = CURRENT_FILE_PATH.parent
PROJECT_ROOT = SRC_FOLDER.parent

# DATA FOLDERS
DATA_FOLDER = PROJECT_ROOT / "data"
CONTRACTS_FOLDER = DATA_FOLDER / "contracts"
DATABASE_FOLDER = DATA_FOLDER / "database"
SAMPLE_FOLDER = DATA_FOLDER / "sample"
TESTS_FOLDER = DATA_FOLDER / "tests"
YGG_MAPS_FOLDER = DATA_FOLDER / "ygg-maps"
YGG_DBS_FOLDER = DATA_FOLDER / "ygg-databases"

DOCS_FOLDER = PROJECT_ROOT / "docs"
DEV_FOLDER = PROJECT_ROOT / "dev"

ASSETS_FOLDER = SRC_FOLDER / "assets"
ODCS_SCHEMA_FOLDER = ASSETS_FOLDER / "odcs_schemas"
YGG_SCHEMAS_FOLDER = ASSETS_FOLDER / "ygg_schemas"

YGG_SCHEMA_CONFIG_FILE = YGG_SCHEMAS_FOLDER / "config.yaml"
YGG_CONFIG_FILE = PROJECT_ROOT / "config.yaml"


class YggBaseConfig(BaseModel):
    """Base configuration model for Ygg."""

    model_config = ConfigDict(use_enum_values=True)


class DuckLakeMetadataRepository(Enum):
    """DuckLake Metadata Repository"""

    POSTGRES = "postgres"


class DuckLakeRepository(Enum):
    """DuckLake Repository"""

    S3 = "s3"


class YggRepositoryConfiguration(YggBaseConfig):
    """Ygg Repository"""

    repository: str = Field(..., description="Repository name")
    ducklake_repository_data_location: str | Path = Field(..., description="Repository location")
    ducklake_metadata_repository: DuckLakeMetadataRepository = Field(
        ...,
        description="Metadata repository technology, must be of type YggMetadataRepository",
    )
    ducklake_repository: DuckLakeRepository = Field(
        ...,
        description="Repository technology, must be of type YggRepository",
    )


class YggS3Config(YggBaseConfig):
    """S3 Config"""

    endpoint_url: str = Field(..., description="S3 endpoint url")
    aws_access_key_id: str = Field(..., description="AWS access key id")
    aws_secret_access_key: str = Field(..., description="AWS secret access key")
    region_name: str = Field(..., description="AWS region name")
    use_ssl: bool | None = Field(default=True, description="Indicates whether to use SSL.")


class YggSinkConfig(YggBaseConfig):
    location: Path = Field(..., description="Path sink the implementation")


class YggGeneralConfiguration(YggBaseConfig):
    environment: str = Field(..., description="Environment name.", examples=["dev", "prod"])
    repository: str = Field(..., description="Repository name.")
    lake_alias: str = Field(..., description="DuckLake alias.")
    local_cache: str = Field(..., description="Local cache path.")


class YggQuackDatabaseConfig(YggBaseConfig):
    """Quack Database Config."""

    host: str | None = Field(default=None, description="Database host")
    db_name: str | None = Field(default=None, description="Database name")
    port: int | str | None = Field(default=None, description="Database port")
    user: str | None = Field(default=None, description="Database user")
    password: str | None = Field(default=None, description="Database password")


class YggDatabaseConfig(YggBaseConfig):
    database: str = Field(..., description="Database name")
    database_extension: str = Field(..., description="Database extension, e.g. .db or .duckdb")
    database_location: Path = Field(..., description="Path to the database")
    data_location: Path = Field(..., description="Path to store the data")

    @model_validator(mode="after")
    def validate_and_overwrite_deterministically(self):
        """Validate and overwrite deterministically."""
        self.database = self.database.strip().lower()
        self.database_extension = self.database_extension.strip().lower()

        return self

    @property
    def database_url(self) -> Path:
        """Get the database URL."""

        database_name = f"{self.database}.{self.database_extension}" if self.database_extension else self.database
        return self.database_location / database_name


class YggCatalogDatabaseConfig(YggBaseConfig):
    host: str = Field(..., description="Database host name")
    port: str = Field(..., description="Database host name")
    database: str = Field(..., description="Database catalog name")
    user: str = Field(..., description="Database user name")
    password: str = Field(..., description="Database user password")


@singleton
class YggSetup:
    """Ygg Setup."""

    def __init__(
        self,
        create_ygg_folders: bool = True,
        config_data: dict[str, str | Any] | None = None,
    ):
        """Initialize the Ygg Setup."""

        self._config = self._get_config(config_data)
        self._create_ygg_folders = create_ygg_folders

        self._sink_config: YggSinkConfig = self._ygg_sink_config()
        self._database_config: YggDatabaseConfig = self._ygg_database_config()

    @staticmethod
    def _create_folder(folder: Path) -> None:
        """Create the folders."""

        folder.mkdir(parents=True, exist_ok=True)

    @property
    def database_config(self) -> YggDatabaseConfig:
        """Get the Database Config."""

        return self._database_config

    @property
    def sink_config(self) -> YggSinkConfig:
        """Get the Sink Config."""

        return self._sink_config

    @property
    def ygg_repository_config(self) -> YggRepositoryConfiguration:
        """Get the Ygg Repository Config."""

        return YggRepositoryConfiguration(**self._config.get("ygg-repository-config", {}))

    @property
    def ygg_quack_config(self) -> YggQuackDatabaseConfig:
        """Get the Ygg Quack Config."""

        return YggQuackDatabaseConfig(**self._config.get("ygg-quack-database-config", {}))

    @property
    def ygg_config(self) -> YggRepositoryConfiguration:
        """Get the Ygg General Config."""

        return YggGeneralConfiguration(**self._config.get("ygg-config", {}))

    @property
    def ygg_s3_config(self) -> YggS3Config:
        """Get the Ygg Repository Config."""

        return YggS3Config(**self._config.get("ygg-s3-config", {}))

    def _ygg_database_config(self) -> YggDatabaseConfig:
        """Get the Ygg Database Config."""
        ygg_database_config = self._config.get("ygg-database-config", {})

        if not ygg_database_config:
            raise ValueError("Ygg Database Config not found. Please check the config.yaml file.")

        db_config = YggDatabaseConfig(**ygg_database_config)
        if self._create_ygg_folders:
            self._create_folder(db_config.database_location)

        return db_config

    @property
    def ygg_catalog_database_config(self) -> YggCatalogDatabaseConfig:
        """Get the Ygg Catalog Database Config."""

        ygg_database_config = self._config.get("ygg-metadata-catalog-database-config", {})
        if not ygg_database_config:
            raise ValueError("Ygg Catalog Database Config not found. Please check the config.yaml file.")

        db_config = YggCatalogDatabaseConfig(**ygg_database_config)
        return db_config

    def _ygg_sink_config(self) -> YggSinkConfig:
        """Get the Ygg Sink Config."""

        ygg_sink_config = self._config.get("ygg-sink-config", {})

        if not ygg_sink_config:
            raise ValueError("Ygg Sink Config not found. Please check the config.yaml file.")

        sink_config = YggSinkConfig(**ygg_sink_config)
        if self._create_ygg_folders:
            self._create_folder(sink_config.location)

        return sink_config

    @staticmethod
    def _get_config(config_data: dict) -> dict[str, str | Any]:
        """Get the configuration."""

        if not config_data:
            config_data = get_yaml_content(YGG_CONFIG_FILE)

        config = config_data
        config = replace_placeholders_with_env_values(config)

        return config
