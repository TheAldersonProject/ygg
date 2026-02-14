"""Release Artifacts"""

from ygg.helpers.logical_data_models import PolyglotEntity, PolyglotEntityColumn, PolyglotEntityColumnDataType


class ArtifactsSetup:
    """Release Artifacts Setup"""

    def __init__(self, catalog_name: str | None = None, schema_name: str | None = None) -> None:
        """Initialize Release Artifacts"""

        self._catalog_name: str | None = catalog_name
        self._schema_name: str | None = schema_name
        self._release_entity_model: PolyglotEntity | None = None
        self._version_artifacts_entity_model: PolyglotEntity | None = None
        self._artifacts_entity_model: PolyglotEntity | None = None

        _data_type_mapping: dict[str, PolyglotEntityColumnDataType] = {
            "string": PolyglotEntityColumnDataType(
                data_type_name="string", duck_db_type="VARCHAR", duck_lake_type="VARCHAR", duck_db_regex_pattern=None
            ),
            "integer": PolyglotEntityColumnDataType(
                data_type_name="integer", duck_db_type="INTEGER", duck_lake_type="INTEGER", duck_db_regex_pattern=None
            ),
        }
        self.dtype_str: PolyglotEntityColumnDataType = _data_type_mapping["string"]
        self.dtype_int: PolyglotEntityColumnDataType = _data_type_mapping["integer"]

    @property
    def release_entity_model(self) -> PolyglotEntity | None:
        """Get the Release Entity Model"""

        return self._release_entity_model

    def define_release_entity_model(self) -> None:
        """Defines the Release Entity Model"""

        version = PolyglotEntityColumn(
            name="version", data_type=self.dtype_str, comment="Release version", primary_key=True
        )
        status = PolyglotEntityColumn(
            name="status",
            data_type=self.dtype_str,
            enum=["rc", "release", "beta", "alpha"],
            comment="Version status",
            primary_key=True,
        )
        semantical = PolyglotEntityColumn(
            name="semantical_version",
            data_type=self.dtype_str,
            comment="Semantical version",
            primary_key=False,
        )
        tag = PolyglotEntityColumn(
            name="tag",
            data_type=self.dtype_str,
            comment="Version tag",
            primary_key=False,
        )
        build = PolyglotEntityColumn(
            name="build",
            data_type=self.dtype_str,
            comment="Release build signature",
            primary_key=True,
            unique_key=True,
        )
        release_ets = PolyglotEntityColumn(
            name="release_ets",
            data_type=self.dtype_int,
            comment="Release Epoch Timestamp (UTC)",
            primary_key=False,
        )
        entity_columns: list[PolyglotEntityColumn] = [version, status, semantical, tag, build, release_ets]

        entity: PolyglotEntity = PolyglotEntity(
            name="versions",
            comment="Table to control the release pipeline",
            schema_=self._schema_name,
            columns=entity_columns,
        )

        self._release_entity_model = entity

    def define_release_artifacts_entity_model(self) -> None:
        """Defines the Release Artifacts Entity Model"""

        version = PolyglotEntityColumn(
            name="factory",
            data_type=self.dtype_str,
            enum=["blueprint", "base64_binary", "build-report", "report", "database_instructions"],
            comment="Artifact type factory",
            primary_key=False,
        )

        artifact = PolyglotEntityColumn(
            name="artifact",
            data_type=self.dtype_str,
            comment="Artifact content",
            primary_key=False,
        )

        entity_columns: list[PolyglotEntityColumn] = [version, artifact]

        entity: PolyglotEntity = PolyglotEntity(
            name="version_artifacts",
            comment="Table to control the release artifacts for the pipeline",
            schema_=self._schema_name,
            columns=entity_columns,
        )

        self._artifacts_entity_model = entity

    def define_artifacts_entity_model(self) -> None:
        """Defines the Artifacts Entity Model"""

        build = PolyglotEntityColumn(
            name="build",
            data_type=self.dtype_str,
            comment="Artifact build signature",
            primary_key=True,
        )

        artifact_name = PolyglotEntityColumn(
            name="name",
            data_type=self.dtype_str,
            comment="Artifact Name",
            primary_key=True,
        )

        artifact_extension = PolyglotEntityColumn(
            name="extension",
            data_type=self.dtype_str,
            comment="Artifact extension",
            primary_key=False,
            nullable=True,
        )

        artifact_signature = PolyglotEntityColumn(
            name="signature",
            data_type=self.dtype_str,
            comment="Artifact signature",
            primary_key=True,
        )

        content_factory = PolyglotEntityColumn(
            name="content_factory",
            data_type=self.dtype_str,
            enum=["json", "yaml", "base64_binary", "sql", "python", "markdown"],
            comment="Artifact type factory",
            primary_key=False,
        )

        direction = PolyglotEntityColumn(
            name="direction",
            data_type=self.dtype_str,
            enum=["input", "output"],
            comment="Artifact of input or output direction",
            primary_key=False,
        )

        artifact_factory = PolyglotEntityColumn(
            name="factory",
            data_type=self.dtype_str,
            enum=["blueprint", "base64_binary", "build-report", "report", "database_instructions"],
            comment="Artifact type factory",
            primary_key=False,
        )

        artifact = PolyglotEntityColumn(
            name="artifact",
            data_type=self.dtype_str,
            comment="Artifact content",
            primary_key=False,
        )

        entity_columns: list[PolyglotEntityColumn] = [
            build,
            artifact_name,
            artifact_signature,
            artifact_factory,
            artifact,
            content_factory,
            direction,
            artifact_extension,
        ]

        entity: PolyglotEntity = PolyglotEntity(
            name="artifacts",
            comment="Table to control the pipeline artifacts",
            schema_=self._schema_name,
            columns=entity_columns,
        )

        self._version_artifacts_entity_model = entity

    def create_entities(self) -> None:
        """Create the entities"""


if __name__ == "__main__":
    artifacts = ArtifactsSetup(catalog_name="ygg_catalog", schema_name="ygg_catalog")
    artifacts.define_release_entity_model()
    print(artifacts.release_entity_model)
