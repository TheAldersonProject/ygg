"""Set of tools to interact with DuckDb and DuckLake."""

from enum import Enum
from typing import Any

from pydantic import Field

import ygg.helpers.data_types as data_types
from ygg.helpers.logical_data_models import YggBaseModel
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DuckLakeDbEntityType(Enum):
    """Entity Types"""

    DUCKDB = "duckdb"
    DUCKLAKE = "ducklake"


class DuckLakeDbEntityColumnDataType(YggBaseModel):
    """DuckLake Db Entity Column Data Type"""

    data_type_name: str = Field(..., description="Column data type")
    duck_db_type: str = Field(..., description="DuckDb data type")
    duck_db_regex_pattern: str | None = Field(default=None, description="DuckDb regex pattern")
    duck_lake_type: str = Field(..., description="DuckLake data type")


class DuckLakeDbEntityColumn(YggBaseModel):
    """DuckLake Db Entity Column"""

    name: str = Field(..., description="Column name")
    data_type: DuckLakeDbEntityColumnDataType = Field(..., description="Column data type")
    enum: list | None = Field(default=None)
    comment: str | None = Field(default=None, description="Column comment")
    nullable: bool | None = Field(default=False, description="Whether the column can be null")
    primary_key: bool | None = Field(default=False, description="Whether the column is a primary key")
    unique_key: bool | None = Field(default=False, description="Whether the column is a unique key")
    check_constraint: str | None = Field(default=None, description="Check constraint")
    default_value: str | Any | None = Field(default=None, description="Default value")
    default_value_function: str | None = Field(default=None, description="Database function for default value")


class DuckLakeDbEntity(YggBaseModel):
    """DuckLake Db Entity"""

    name: str = Field(..., description="Entity name")
    schema: str = Field(..., description="Entity schema name")
    comment: str | None = Field(default=None, description="Entity comment")
    columns: list[DuckLakeDbEntityColumn] | None = Field(default=None, description="Entity list of columns")


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

        self._duck_lake_receipts: list[str] | None = None
        self._duck_db_receipts: list[str] | None = None

        self._create_duck_db_entity()
        self._create_duck_lake_entity()

    @property
    def duck_lake_receipt(self) -> list[str]:
        """Get the DuckLake receipts."""
        if not self._duck_lake_receipts:
            raise ValueError("No DuckLake receipts found.")

        return self._duck_lake_receipts

    @property
    def duck_db_receipt(self) -> list[str]:
        """Get the DuckDb receipts."""
        if not self._duck_db_receipts:
            raise ValueError("No DuckDb receipts found.")

        return self._duck_db_receipts

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
        column_comment: str | None = column.comment

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

        return column_ddl_definition, column_comment

    @staticmethod
    def _get_duck_db_primary_key_ddl_definition(primary_key_list: list[str]) -> str:
        """Return the primary key ddl definition."""

        return f"PRIMARY KEY ({', '.join(primary_key_list)})"

    def _get_entity_columns_definition(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the entity definition."""

        columns: list[str] = []
        columns_comments: list[str] = []
        primary_key_columns: list[str] = []
        for column in self._model.columns:
            column_ddl_definition, column_comment = self._get_db_column_ddl_definition(column, entity_type)
            columns.append(column_ddl_definition)

            if column_comment:
                column_comment = (
                    f"COMMENT ON COLUMN {self._entity_schema_name}.{self._model.name}.{column.name.lower()}"
                    f" IS '{column_comment}';"
                )
                columns_comments.append(column_comment)

            if column.primary_key:
                primary_key_columns.append(column.name)

        if entity_type == DuckLakeDbEntityType.DUCKDB:
            primary_key_ddl_definition = self._get_duck_db_primary_key_ddl_definition(primary_key_columns)
            columns.append(primary_key_ddl_definition)

        columns_definition = ",\n".join(columns)
        columns_comments_definition = "\n".join(columns_comments)

        return columns_definition, columns_comments_definition, primary_key_columns

    def _get_entity_schema_spec(self) -> str:
        """Return the entity schema spec."""

        entity_schema_name = self._entity_schema_name
        entity_schema_spec = f"CREATE SCHEMA IF NOT EXISTS {entity_schema_name};"

        logs.debug("Entity Schema Spec", spec=entity_schema_spec)

        return entity_schema_spec

    def _get_create_entity_header(self) -> str:
        """Return the creation statement of the entity header."""

        create_or_replace: str = "CREATE OR REPLACE TABLE"
        create_if_not_exists: str = "CREATE TABLE IF NOT EXISTS"
        create_table_header: str = create_if_not_exists if not self._recreate_existing_database else create_or_replace
        entity_name = f"{create_table_header} {self._entity_schema_name.upper()}.{self._model.name.lower()}"

        return entity_name

    def _get_entity_spec(self, entity_type: DuckLakeDbEntityType) -> str:
        """Create entities in DuckLake"""

        if not self._duck_db_receipts:
            self._duck_db_receipts = []

        header = self._get_create_entity_header()
        columns, columns_comments, primary_key = self._get_entity_columns_definition(entity_type)

        stmt: str = f"{header} (\n{columns}\n);"
        return stmt, columns_comments

    def _create_duck_lake_entity(self) -> None:
        """Create entities in DuckDb"""

        if not self._duck_lake_receipts:
            self._duck_lake_receipts = []

        s3_secret = """
        CREATE OR REPLACE SECRET rustfs_secret (
            TYPE S3,
            KEY_ID 'tKpIEv0on3OBmGPhgjlT',
            SECRET 'tMvVHYPsXIKd7xSDRn3lj28G5pZNBaQbgAcfk4rw',
            ENDPOINT 'localhost:9000',
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
            "LOAD httpfs;",
            s3_secret,
            """
            ATTACH 'ducklake:postgres:dbname=ducklake_catalog host=localhost user=postgres password=postgres port=5432' 
              AS ygg_ducklake 
              (DATA_PATH 's3://repository/', override_data_path true);
            """,
            "use ygg_ducklake;",
        ]

        create_entity_stmt, columns_comments = self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKLAKE)
        self._duck_lake_receipts.extend(ducklake_instructions)
        self._duck_lake_receipts.append(self._get_entity_schema_spec())
        self._duck_lake_receipts.append(create_entity_stmt)

    def _create_duck_db_entity(self) -> None:
        """Create entities in DuckDb"""

        if not self._duck_lake_receipts:
            self._duck_lake_receipts = []

        create_entity_stmt, columns_comments = self._get_entity_spec(entity_type=DuckLakeDbEntityType.DUCKDB)
        self._duck_db_receipts.append(self._get_entity_schema_spec())
        self._duck_db_receipts.append(create_entity_stmt)
