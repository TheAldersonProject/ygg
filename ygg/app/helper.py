"""GUI App Helper."""

import ygg.utils.commons as cm
from ygg.config import (
    ODCS_SCHEMA_FOLDER,
    YGG_SCHEMAS_FOLDER,
    YggQuackDatabaseConfig,
    YggRepositoryConfiguration,
    YggS3Config,
    YggSetup,
)


class AppHelper:
    """App Helper."""

    @staticmethod
    def ygg_config() -> YggRepositoryConfiguration:
        """Get the Lake config."""

        return YggSetup().ygg_config

    @staticmethod
    def ygg_quack_config() -> YggQuackDatabaseConfig:
        """Get the Quack config."""

        return YggSetup().ygg_quack_config

    @staticmethod
    def ygg_s3_config() -> YggS3Config:
        """Get the S3 config."""

        return YggSetup().ygg_s3_config

    @staticmethod
    def ygg_version() -> str:
        """Get the Ygg version."""

        version_file = YGG_SCHEMAS_FOLDER / "VERSION.txt"
        version = cm.get_file_string_content(version_file)

        return version

    @staticmethod
    def blueprint_odcs() -> str:
        """Get the Ygg Schema Config."""

        ygg_ = ODCS_SCHEMA_FOLDER / "odcs-json-schema-v3.1.0.json"
        content = cm.get_file_string_content(ygg_)
        return content

    @staticmethod
    def blueprint_config() -> str:
        """Get the Ygg Schema Config."""

        ygg_ = YGG_SCHEMAS_FOLDER / "config.yaml"
        content = cm.get_file_string_content(ygg_)

        return content

    @staticmethod
    def contract_blueprint() -> str:
        """Get the Ygg Schema Contract."""

        ygg_ = YGG_SCHEMAS_FOLDER / "contract.yaml"
        content = cm.get_file_string_content(ygg_)

        return content

    @staticmethod
    def servers_blueprint() -> str:
        """Get the Ygg Schema Servers."""

        ygg_ = YGG_SCHEMAS_FOLDER / "servers.yaml"
        content = cm.get_file_string_content(ygg_)

        return content

    @staticmethod
    def schema_blueprint() -> str:
        """Get the Ygg Schema Servers."""

        ygg_ = YGG_SCHEMAS_FOLDER / "schema.yaml"
        content = cm.get_file_string_content(ygg_)

        return content

    @staticmethod
    def schema_property_blueprint() -> str:
        """Get the Ygg Schema Servers."""

        ygg_ = YGG_SCHEMAS_FOLDER / "schema_property.yaml"
        content = cm.get_file_string_content(ygg_)

        return content
