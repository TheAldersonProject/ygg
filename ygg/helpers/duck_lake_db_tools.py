"""Set of tools to interact with DuckDb and DuckLake."""

from pydantic import Field

import ygg.helpers.data_types as data_types
from ygg.config import YggSetup
from ygg.helpers.logical_data_models import (
    DuckLakeDbEntity,
    DuckLakeDbEntityColumn,
    DuckLakeDbEntityColumnDataType,
    DuckLakeDbEntityType,
    YggBaseModel,
)
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DuckLakeSetup(YggBaseModel):
    """DuckLake Setup."""

    install_modules: list[str] = Field(default_factory=list, description="List of modules to install.")
    load_modules: list[str] = Field(default_factory=list, description="List of modules to load.")
    object_storage_secret: str = Field(default=str, description="Object storage secret.")
    attach_ducklake_catalog: str = Field(default=str, description="DuckLake catalog to attach.")


class DuckLakeDbTools:
    """DuckLake Db Tools"""

    def __init__(self, model: DuckLakeDbEntity, recreate_existing_entity: bool = False) -> None:
        """Initialize DuckLake Db Tools"""

        if not model:
            logs.error("DuckLake Db Entity cannot be empty.")
            raise ValueError("DuckLake Db Entity cannot be empty.")

        self._model: DuckLakeDbEntity = model
        self._entity_schema_name = model.schema.upper()
        self._recreate_existing_database: bool = recreate_existing_entity or False

        logs.info(
            "Initializing Duck Lake & Db Tools module.",
            model=self._model.name,
            schema=self._entity_schema_name.lower(),
            recreate_existing=recreate_existing_entity,
        )

        self._duck_lake_instructions_list: list[str] | None = None
        self._duck_db_instructions_list: list[str] | None = None

        self._setup = YggSetup(create_ygg_folders=False, config_data=None)
        self._duck_lake_catalog: str = self._setup.ygg_config.lake_alias  # type: ignore

        self._primary_keys: list[DuckLakeDbEntityColumnDataType] | None = None

        self._create_duck_db_entity()
        self._create_duck_lake_entity()

    @property
    def duck_lake_instructions(self) -> list[str]:
        """Get the DuckLake receipts."""
        if not self._duck_lake_instructions_list:
            raise ValueError("No DuckLake receipts found.")

        return self._duck_lake_instructions_list

    @property
    def duck_db_instructions(self) -> list[str]:
        """Get the DuckDb receipts."""
        if not self._duck_db_instructions_list:
            raise ValueError("No DuckDb receipts found.")
        return self._duck_db_instructions_list

    @property
    def ducklake_schema_ddl(self) -> str:
        """Get the DuckLake schema ddl."""
        return self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)

    @property
    def duckdb_schema_ddl(self) -> str:
        """Get the DuckDb schema ddl."""
        return self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKDB)

    @property
    def duckdb_entity_ddl(self) -> str:
        """Get the DuckDb entity ddl."""
        return self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKDB)

    @property
    def ducklake_entity_ddl(self) -> str:
        """Get the DuckLake entity ddl."""
        return self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)

    @property
    def primary_keys(self) -> list[DuckLakeDbEntityColumnDataType]:
        """Get the primary keys for the entity."""
        primary_keys = [c for c in self._model.columns if c.primary_key]
        return primary_keys

    @property
    def ducklake_setup_instructions(self) -> DuckLakeSetup:
        """Get the DuckLake setup instructions."""

        general_config = self._setup.ygg_config
        object_storage_config = self._setup.ygg_s3_config
        catalog_database_config = self._setup.ygg_catalog_database_config

        object_storage_secret = f"""
            CREATE OR REPLACE SECRET OBJECT_STORAGE_SECRET (
                TYPE S3,
                KEY_ID '{object_storage_config.aws_secret_access_key}',
                SECRET '{object_storage_config.aws_secret_access_key}',
                ENDPOINT '{object_storage_config.endpoint_url}',
                URL_STYLE 'path',
                USE_SSL false
            );
        """
        install_modules: list[str] = ["install ducklake;", "install postgres;", "install httpfs;"]
        load_modules: list[str] = ["load ducklake;", "load postgres;", "load httpfs;"]
        attach_ducklake_catalog: str = f"""
            ATTACH 'ducklake:postgres:dbname={catalog_database_config.database} 
                host={catalog_database_config.host} 
                user={catalog_database_config.user} 
                password={catalog_database_config.password} 
                port={catalog_database_config.port}' 
                AS {self._duck_lake_catalog}
                (DATA_PATH 's3://{general_config.repository}/', override_data_path true);
        """
        setup = DuckLakeSetup(
            install_modules=install_modules,
            load_modules=load_modules,
            object_storage_secret=object_storage_secret,
            attach_ducklake_catalog=attach_ducklake_catalog,
        )

        return setup

    @staticmethod
    def _get_data_type(data_type_name: str) -> DuckLakeDbEntityColumnDataType:
        """Get the data type based on the entity type."""

        data_type = data_types.get_data_type(data_type=data_type_name, of_type="physical")
        if not data_type:
            raise ValueError(f"Data type {data_type_name} not found.")

        physical_data_type = data_type.get("type", None)
        column_data_type = DuckLakeDbEntityColumnDataType(
            data_type_name=data_type_name,
            duck_db_type=physical_data_type,
            duck_db_regex_pattern=data_type.get("pattern", None),
            duck_lake_type=data_type.get("duck_lake_type", physical_data_type),
        )

        return column_data_type

    @staticmethod
    def _get_db_column_ddl_definition(column: DuckLakeDbEntityColumn, entity_type: DuckLakeDbEntityType) -> str:
        """Return the column ddl definition."""

        duck_lake_column_spec: str = "{name} {type}"
        duck_db_column_spec: str = duck_lake_column_spec + "{default_value}{nullable}{check_constraint}"
        column_ddl_definition: str = ""

        reserved_names_translation = {"date": "date_", "timestamp": "timestamp_"}
        column_name = reserved_names_translation.get(column.name, column.name)

        if entity_type == DuckLakeDbEntityType.DUCKLAKE:
            column_ddl_definition = duck_lake_column_spec.format(
                name=column_name.lower(),
                type=column.data_type.duck_lake_type.upper(),
            )

        elif entity_type == DuckLakeDbEntityType.DUCKDB:
            default_value: str = ""
            nullable: str = "" if not column.nullable else " NOT NULL"

            if column.enum:
                data_type: str = f""" ENUM({", ".join(["'" + enum_ + "'" for enum_ in column.enum])}) """
                check_constraint: str | None = None
            else:
                data_type: str = column.data_type.duck_lake_type.upper()
                check_constraint: str | None = None

                if column.data_type.duck_db_regex_pattern:
                    column_check_constraint = (
                        f"regexp_matches({column_name.lower()}, '{column.data_type.duck_db_regex_pattern}')"
                    )
                    check_constraint = f" CHECK ({column_check_constraint})"

            if column.default_value or column.default_value_function:
                if data_type.upper() in (
                    "TIMESTAMP",
                    "TIMESTAMPTZ",
                    "TIMESTAMP_LTZ",
                    "BIGINT",
                    "INTEGER",
                ):
                    if column.default_value_function:
                        default_value = f" DEFAULT {column.default_value_function}"
                    else:
                        default_value = f" DEFAULT {column.default_value}"

                elif data_type.upper() not in ("BOOL", "BOOLEAN"):
                    default_value = f" DEFAULT '{column.default_value}'"

                elif data_type.upper() in ("BOOL", "BOOLEAN"):
                    default_value = f" DEFAULT {1 if column.default_value else 0}"

                elif default_value == ...:
                    default_value = ""

                else:
                    default_value = f" DEFAULT {column.default_value}"

            column_ddl_definition = duck_db_column_spec.format(
                default_value=default_value or "",
                name=column_name.lower(),
                type=data_type,
                nullable=nullable or "",
                check_constraint=check_constraint or "",
            )

            logs.debug("Column DDL Definition", ddl=column_ddl_definition)

        return column_ddl_definition

    def _get_entity_columns_definition(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the entity definition."""

        columns: list[str] = []
        primary_key_columns: list[str] = []
        for column in self._model.columns:
            column_ddl_definition = self._get_db_column_ddl_definition(column, entity_type)
            columns.append(column_ddl_definition)

            if column.primary_key:
                primary_key_columns.append(column.name)

        if entity_type == DuckLakeDbEntityType.DUCKDB:
            primary_key_ddl_definition = f"PRIMARY KEY ({', '.join(primary_key_columns)})"
            columns.append(primary_key_ddl_definition)

        columns_definition = "  ,\n".join(columns)
        return columns_definition

    def _get_entity_schema_spec(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the entity schema spec."""

        ducklake_catalog = ""
        if entity_type == DuckLakeDbEntityType.DUCKLAKE:
            ducklake_catalog: str = f"{self._duck_lake_catalog}."

        entity_schema_name = self._entity_schema_name
        entity_schema_spec = f"CREATE SCHEMA IF NOT EXISTS {ducklake_catalog}{entity_schema_name};"

        logs.debug("Entity Schema Spec", spec=entity_schema_spec)
        return entity_schema_spec

    def _get_create_entity_header(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the creation statement of the entity header."""

        create_or_replace: str = "CREATE OR REPLACE TABLE"
        create_if_not_exists: str = "CREATE TABLE IF NOT EXISTS"

        ducklake_catalog = ""
        if entity_type == DuckLakeDbEntityType.DUCKLAKE:
            ducklake_catalog: str = f"{self._duck_lake_catalog}."

        create_table_header: str = create_if_not_exists if not self._recreate_existing_database else create_or_replace
        entity_header = (
            f"{create_table_header} {ducklake_catalog}{self._entity_schema_name.upper()}.{self._model.name.lower()}"
        )

        logs.debug("Entity Creation Header", header=entity_header)
        return entity_header

    def _get_entity_spec(self, entity_type: DuckLakeDbEntityType) -> str:
        """Create entities in DuckLake"""

        if not self._duck_db_instructions_list:
            self._duck_db_instructions_list = []

        header = self._get_create_entity_header(entity_type=entity_type)
        columns = self._get_entity_columns_definition(entity_type)

        stmt: str = f"{header} (\n{columns}\n);"
        return stmt

    def _create_duck_lake_entity(self) -> None:
        """Create entities in DuckDb"""

        if not self._duck_lake_instructions_list:
            self._duck_lake_instructions_list = []

        general_config = self._setup.ygg_config
        object_storage_config = self._setup.ygg_s3_config
        catalog_database_config = self._setup.ygg_catalog_database_config

        s3_secret = f"""
        CREATE OR REPLACE SECRET OBJECT_STORAGE_SECRET (
            TYPE S3,
            KEY_ID '{object_storage_config.aws_secret_access_key}',
            SECRET '{object_storage_config.aws_secret_access_key}',
            ENDPOINT '{object_storage_config.endpoint_url}',
            URL_STYLE 'path',
            USE_SSL false
        );
        """

        ducklake_instructions: list[str] = [
            "install ducklake;",
            "install postgres;",
            "install httpfs;",
            "load ducklake;",
            "load postgres;",
            "load httpfs;",
            s3_secret,
            f"""
            ATTACH 'ducklake:postgres:dbname={catalog_database_config.database} 
                host={catalog_database_config.host} 
                user={catalog_database_config.user} 
                password={catalog_database_config.password} 
                port={catalog_database_config.port}' 
                AS {self._duck_lake_catalog}
                (DATA_PATH 's3://{general_config.repository}/', override_data_path true);
            """,
        ]

        create_entity_stmt = self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)
        create_schema_stmt = self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)
        self._duck_lake_instructions_list.extend(ducklake_instructions)
        self._duck_lake_instructions_list.append(create_schema_stmt)
        self._duck_lake_instructions_list.append(create_entity_stmt)

    def _create_duck_db_entity(self) -> None:
        """Create entities in DuckDb"""

        if not self._duck_lake_instructions_list:
            self._duck_lake_instructions_list = []

        create_entity_stmt = self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKDB)
        self._duck_db_instructions_list.append(self._get_entity_schema_spec(entity_type=DuckLakeDbEntityType.DUCKDB))
        self._duck_db_instructions_list.append(create_entity_stmt)
