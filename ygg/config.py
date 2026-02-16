"""Project configuration."""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ygg.utils.commons import replace_placeholders_with_env_values
from ygg.utils.custom_decorators import singleton


class YggBaseConfig(BaseModel):
    """Base configuration model for Ygg."""

    model_config = ConfigDict(use_enum_values=True)


class DuckLakeMetadataRepository(Enum):
    """DuckLake Metadata Repository"""

    POSTGRES = "postgres"


class DuckLakeRepository(Enum):
    """DuckLake Repository"""

    S3 = "s3"


class YggS3Config(YggBaseConfig):
    """S3 Config"""

    endpoint_url: str = Field(..., description="S3 endpoint url")
    aws_access_key_id: str = Field(..., description="AWS access key id")
    aws_secret_access_key: str = Field(..., description="AWS secret access key")
    region_name: str = Field(..., description="AWS region name")
    use_ssl: bool | None = Field(default=True, description="Indicates whether to use SSL.")


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
        self._database_config: YggDatabaseConfig = self._ygg_database_config()

    @staticmethod
    def _create_folder(folder: Path) -> None:
        """Create the folders."""

        folder.mkdir(parents=True, exist_ok=True)

    @property
    def ygg_quack_config(self) -> YggQuackDatabaseConfig:
        """Get the Ygg Quack Config."""

        return YggQuackDatabaseConfig(**self._config.get("ygg-quack-database-config", {}))

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

    @staticmethod
    def _get_config(config_data: dict) -> dict[str, str | Any]:
        """Get the configuration."""

        if not config_data:
            raise ValueError("Config data not found. Please check the config.yaml file.")

        config = config_data
        config = replace_placeholders_with_env_values(config)

        return config
