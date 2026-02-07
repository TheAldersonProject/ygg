"""Project configuration."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from ygg.utils import files_utils
from ygg.utils.custom_decorators import singleton
from ygg.utils.files_utils import replace_placeholders_with_env_values

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


class YggSinkConfig(BaseModel):
    location: Path = Field(..., description="Path sink the implementation")


class YggDatabaseConfig(BaseModel):
    database: str = Field(..., description="Database name")
    database_extension: str = Field(..., description="Database extension, e.g. .db or .duckdb")
    environment: Literal["dev", "prod"] = Field(..., description="Environment name")
    database_location: Path = Field(..., description="Path to the database")
    data_location: Path = Field(..., description="Path to store the data")

    @model_validator(mode="after")
    def validate_and_overwrite_deterministically(self):
        """Validate and overwrite deterministically."""
        self.environment = self.environment.strip().lower()
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

    def __init__(self, create_ygg_folders: bool = True):
        """Initialize the Ygg Setup."""

        self._create_ygg_folders = create_ygg_folders
        self._config = self._get_config()

        self._sink_config = self._ygg_sink_config()
        self._database_config = self._ygg_database_config()

        self._ygg_sink_config: YggDatabaseConfig | None = None

    @staticmethod
    def _create_folder(folder: Path) -> None:
        """Create the folders."""
        folder.mkdir(parents=True, exist_ok=True)

    @property
    def database_config(self) -> YggDatabaseConfig:
        return self._database_config

    @property
    def sink_config(self) -> YggSinkConfig:
        return self._sink_config

    def _ygg_database_config(self) -> YggDatabaseConfig:
        """Get the Ygg Database Config."""
        ygg_database_config = self._config.get("ygg-database-config", {})

        if not ygg_database_config:
            raise ValueError("Ygg Database Config not found. Please check the config.yaml file.")

        db_config = YggDatabaseConfig(**ygg_database_config)
        if self._create_ygg_folders:
            self._create_folder(db_config.database_location)

        return db_config

    def _ygg_sink_config(self) -> YggSinkConfig:
        ygg_sink_config = self._config.get("ygg-sink-config", {})

        if not ygg_sink_config:
            raise ValueError("Ygg Sink Config not found. Please check the config.yaml file.")

        sink_config = YggSinkConfig(**ygg_sink_config)
        if self._create_ygg_folders:
            self._create_folder(sink_config.location)

        return sink_config

    @staticmethod
    def _get_config() -> dict[str, str | Any]:
        """Get the configuration."""
        with open("config.yaml", "r") as f:
            config = files_utils.get_yaml_content(f.name)

        config = replace_placeholders_with_env_values(config)
        return config


if __name__ == "__main__":
    s = YggSetup()
    print(s.database_config)
    print(s.database_config.database_url)
    print(s.sink_config)
    print(s.sink_config.location)
