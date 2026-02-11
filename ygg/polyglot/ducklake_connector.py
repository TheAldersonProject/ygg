"""Set of tools to interact with DuckLake."""

from textwrap import dedent

from ygg.config import YggSetup
from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import (
    DuckLakeSetup,
    PolyglotEntity,
)
from ygg.polyglot.postgres_db_tools import PostgresConnector
from ygg.polyglot.quack_service import QuackService
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DuckLakeConnector(QuackService):
    """DuckLake Tools"""

    def __init__(
        self,
        model: PolyglotEntity,
        catalog_name: str,
        recreate_existing_entity: bool = False,
    ) -> None:
        """Initialize DuckLake Db Tools"""

        if not model:
            logs.error("DuckLake Db Entity cannot be empty.")
            raise ValueError("DuckLake Db Entity cannot be empty.")

        if not catalog_name:
            logs.error("Catalog name cannot be empty.")
            raise ValueError("Catalog name cannot be empty.")

        super().__init__(model=model, catalog_name=catalog_name, recreate_existing_entity=recreate_existing_entity)

        logs.info(
            "Initializing Duck Lake & Db Tools module.",
            model=self._model.name,
            schema=self._entity_schema_name.lower(),
            recreate_existing=recreate_existing_entity,
            catalog_name=catalog_name,
        )

        self._duck_lake_instructions_list: list[str] | None = None
        self._setup = YggSetup(create_ygg_folders=False, config_data=None)

    @property
    def schema_ddl(self) -> str:
        """Get the DuckLake schema ddl."""
        return self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)

    @property
    def entity_ddl(self) -> str:
        """Get the DuckLake entity ddl."""
        return self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)

    @property
    def quack_modules(self) -> list[str]:
        """Get the modules to install."""
        modules = ["postgres", "ducklake", "httpfs"]
        return modules

    @property
    def object_storage_secret(self) -> str:
        """Get the object storage secret."""
        storage_config = self._setup.ygg_s3_config
        object_storage_secret = f"""
            CREATE OR REPLACE SECRET OBJECT_STORAGE_SECRET (
            TYPE S3,
            KEY_ID '{storage_config.aws_access_key_id}',
            SECRET '{storage_config.aws_secret_access_key}',
            ENDPOINT '{storage_config.endpoint_url}',
            URL_STYLE 'path',
            USE_SSL false
            );
        """
        object_storage_secret = dedent(object_storage_secret)
        return object_storage_secret

    @property
    def attach_ducklake_catalog(self) -> str:
        """Attach the DuckLake catalog instruction."""

        general_config = self._setup.ygg_config
        catalog_database_config = self._setup.ygg_quack_config
        attach_ducklake_catalog: str = f"""
            ATTACH 'ducklake:postgres:dbname={self._catalog_name} 
            host={catalog_database_config.host} 
            user={catalog_database_config.user} 
            password={catalog_database_config.password} 
            port={catalog_database_config.port}' 
            AS {self._catalog_name}
            (DATA_PATH 's3://{general_config.repository}/{self._catalog_name}/', override_data_path true);
        """

        attach_ducklake_catalog = dedent(attach_ducklake_catalog)
        return attach_ducklake_catalog

    def create_duck_lake_catalog(self) -> None:
        """Create the DuckLake catalog."""

        pg_setup = PostgresConnector(polyglot_db_config=self._setup.ygg_quack_config)
        pg_setup.create_database(target_db_name=self._catalog_name)

    def ducklake_setup_instructions(self) -> DuckLakeSetup:
        """Get the DuckLake setup instructions."""

        install_modules: list[str] = " ".join(f"install {module};" for module in self.quack_modules)
        load_modules: list[str] = " ".join(f"load {module};" for module in self.quack_modules)

        setup = DuckLakeSetup(
            install_modules=install_modules,
            load_modules=load_modules,
            object_storage_secret=self.object_storage_secret,
            attach_ducklake_catalog=self.attach_ducklake_catalog,
        )

        return setup
