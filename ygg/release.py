"""Set of tools to release Ygg."""

import hashlib
import time
import uuid
from enum import Enum
from typing import Any, Self

from midgard.file_utils import JsonFileTools
from midgard.logs import Logger
from midgard.shared_model_mixin import SharedModelMixin
from pydantic import Field

from ygg.data_models import YggBaseModel
from ygg.enums import Model

logs = Logger.get_logger(logger_name="YggRelease")


class VersionStatus(Enum):
    """Release Type."""

    RELEASE_CANDIDATE = "rc"
    RELEASE = "release"
    BETA = "beta"
    ALPHA = "alpha"


class ReleaseItem(YggBaseModel):
    """Release Item."""

    name: str = Field(..., description="Blueprint name")
    signature: str = Field(..., description="Blueprint sha256 signature")
    content: str = Field(..., description="Blueprint content as a string")
    release_signature: str = Field(..., description="Release UUID5-NAMESPACE_DNS signature")


class ReleaseDocument(YggBaseModel, SharedModelMixin):
    """Release Document."""

    version: str = Field(..., description="Contract version")
    version_status: VersionStatus = Field(..., description="Contract version status")
    semantical_version: str = Field(..., description="Contract semantical version with status")
    blueprint_config: str = Field(..., description="Blueprint config as a string")
    odcs_blueprint_schema: str = Field(..., description="ODCS blueprint schema as a string")
    blueprint_content: list[ReleaseItem] = Field(..., description="Blueprint content as a list of ReleaseItem")
    tag: str = Field(..., description="Release tag")
    signature: str = Field(..., description="Release UUID5-NAMESPACE_DNS signature")
    build_ets: int = Field(..., description="Release build epoch timestamp (UTC)")


YGG_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "ygg-blueprints-release")


class Release:
    """Ygg Release."""

    def __init__(self, release: ReleaseDocument | None = None):
        """Initialize the Ygg Release."""

        self._version: str | None = None
        self._version_status: VersionStatus | None = None
        self._blueprint_config: dict | None = None
        self._odcs_blueprint_schema: dict | None = None

        self._blueprint_content: list[ReleaseItem] | None = None
        self._release: ReleaseDocument | None = release

    def set_version(self, version: str) -> Self:
        """Add a version."""

        if not version:
            logs.error("Version cannot be empty.")
            raise ValueError("Version cannot be empty.")

        self._version = version
        logs.debug("Version added", version=version)
        return self

    def set_status(self, version_status: VersionStatus) -> Self:
        """Add a version status."""

        if not version_status or not isinstance(version_status, VersionStatus):
            logs.error("Version Type cannot be empty.")
            raise ValueError("Version Type cannot be empty.")

        self._version_status = version_status
        logs.debug("Version status added.", version_type=version_status.value)
        return self

    def set_blueprints_config(self, blueprint_config: dict) -> Self:
        """Add the blueprints' config."""

        if not blueprint_config:
            logs.error("Blueprint config cannot be empty.")
            raise ValueError("Blueprint config cannot be empty.")

        if not isinstance(blueprint_config, dict):
            logs.error("Blueprint config must be a dictionary.")
            raise TypeError("Blueprint config must be a dictionary.")

        if not blueprint_config.get("models"):
            logs.error("Blueprint config must contain 'models' key.")
            raise KeyError("Blueprint config must contain 'models' key.")

        if not isinstance(blueprint_config["models"], list):
            logs.error("Blueprint config 'models' must be a list.")
            raise TypeError("Blueprint config 'models' must be a list.")

        models: str = ", ".join(blueprint_config["models"])
        models = f"[{models}]"

        self._blueprint_config = blueprint_config
        logs.debug("Blueprint config added.", models=models)
        return self

    def set_odcs_blueprint_schema(self, blueprint_odcs_schema: str) -> Self:
        """Add the blueprints' config."""

        if not blueprint_odcs_schema:
            logs.error("ODCS Blueprint schema cannot be empty.")
            raise ValueError("ODCS Blueprint schema cannot be empty.")

        self._blueprint_config = blueprint_odcs_schema
        logs.debug("Blueprint ODCS schema added.")
        return self

    def add_blueprint(self, blueprint_name: Model, content: dict[str, Any]) -> Self:
        """Add a blueprint."""

        if not content:
            logs.error("Blueprint content cannot be empty.")
            raise ValueError("Blueprint content cannot be empty.")

        if not blueprint_name or not isinstance(blueprint_name, Model):
            logs.error("Blueprint name cannot be empty.")
            raise ValueError("Blueprint name cannot be empty.")

        if not self._blueprint_config:
            logs.error("Blueprint config must be informed.")
            raise ValueError("Blueprint config must be informed.")

        content_signature = JsonFileTools.json_to_sha256(data=content)
        content: ReleaseItem = ReleaseItem(
            name=blueprint_name.value, content=JsonFileTools.json_to_base64(content), signature=content_signature
        )
        if not self._blueprint_content:
            self._blueprint_content = []

        self._blueprint_content.append(content)

        logs.debug("Blueprint added to release.", blueprint_name=blueprint_name.value, signature=f"{content_signature}")
        return self

    @property
    def semantical_version(self) -> str:
        """Get the semantical version."""

        release_version_status = (
            f".{self._version_status.value}" if self._version_status != VersionStatus.RELEASE else ""
        )
        return f"{self._version}{release_version_status}"

    @property
    def tag(self) -> str:
        """Get the release tag."""

        return f"ygg.{self.semantical_version}"

    def _store_release(self) -> None:
        """Store the release."""

    def build(self) -> Self:
        """Build the release object."""

        blueprint_config_base64 = JsonFileTools.json_to_base64(self._blueprint_config)
        blueprint_config_base64_hash = hashlib.md5(blueprint_config_base64.encode()).hexdigest()
        blueprint_config_base64_hash = str(blueprint_config_base64_hash)

        odcs_schema_base_64 = JsonFileTools.json_to_base64(self._odcs_blueprint_schema)
        odcs_schema_base_64_hash = hashlib.md5(odcs_schema_base_64.encode()).hexdigest()
        odcs_schema_base_64_hash = str(odcs_schema_base_64_hash)

        sorted_contents = sorted(self._blueprint_content, key=lambda x: x.name)
        content_map = [p.signature for p in sorted_contents]
        content = "||".join(content_map)

        release_signature = f"{content}||{self._version}||{blueprint_config_base64_hash}||{odcs_schema_base_64_hash}"
        release_signature = str(uuid.uuid5(YGG_NAMESPACE, release_signature))

        build_ets: int = time.time_ns()

        release: ReleaseDocument = ReleaseDocument(
            version=self._version,
            version_status=self._version_status,
            blueprint_config=blueprint_config_base64,
            odcs_blueprint_schema=odcs_schema_base_64,
            blueprint_content=self._blueprint_content,
            semantical_version=self.semantical_version,
            tag=self.tag,
            release_signature=release_signature,
            build_ets=build_ets,
        )

        self._release = release
        logs.debug(
            "Release built.",
            version=self._version,
            tag=self.tag,
            release_signature=release_signature,
            build_ets=build_ets,
        )

        return self

    @staticmethod
    def setup(catalog_name: str, release_entities_spec: list[dict[str, Any]]) -> None:
        """Create if not exists the tables in the catalog database."""

        logs.info("Setting up Release.")

        for e in release_entities_spec:
            # model = PolyglotEntity(**e)
            # create_entity(model=model, catalog_name=catalog_name, recreate_existing_entity=False)

            # logs.info("Setting completed for model.", model=model.name, schema=model.schema_, catalog=catalog_name)
            ...


if __name__ == "__main__":
    # import ygg.config as yc

    release_spec = JsonFileTools.yaml_to_json("/home/thiago/projects/.ygg/local-dev/contract.yaml")
    # Release.setup(catalog_name="ygg", release_entities_spec=release_spec)

    print(release_spec)

    # odcs_schema = cm.get_file_string_content(yc.ODCS_SCHEMA_FILE)
    # ygg_config = cm.get_yaml_content(yc.YGG_SCHEMA_CONFIG_FILE)

    # r = (
    #     Release()
    #     .set_version("0.1.0")
    #     .set_status(VersionStatus.ALPHA)
    #     .set_odcs_blueprint_schema(odcs_schema)
    #     .set_blueprints_config(ygg_config)
    #     .add_blueprint(Model.CONTRACT, cm.get_yaml_content(yc.YGG_SCHEMAS_FOLDER / "contract.yaml"))
    #     .add_blueprint(Model.SERVERS, cm.get_yaml_content(yc.YGG_SCHEMAS_FOLDER / "servers.yaml"))
    #     .add_blueprint(Model.SCHEMA, cm.get_yaml_content(yc.YGG_SCHEMAS_FOLDER / "schema.yaml"))
    #     .add_blueprint(Model.SCHEMA_PROPERTY, cm.get_yaml_content(yc.YGG_SCHEMAS_FOLDER / "schema_property.yaml"))
    #     .build()
    # )

    # logs.info("Semantical Version", semantical_version=r.semantical_version)
    # logs.info("Tag", tag=r.tag)
