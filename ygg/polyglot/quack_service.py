"""Set of shared tools to interact with DuckLake and DuckDb."""

from ygg.config import YggSetup
from ygg.helpers.enums import DuckLakeDbEntityType
from ygg.helpers.logical_data_models import (
    PolyglotEntity,
    PolyglotEntityColumn,
    PolyglotEntityColumnDataType,
)
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class QuackService:
    """Quack Service."""

    def __init__(
        self,
        model: PolyglotEntity,
        catalog_name: str,
        recreate_existing_entity: bool = False,
    ):
        self._model: PolyglotEntity = model
        self._catalog_name: str = catalog_name
        self._recreate_existing_entity: bool = recreate_existing_entity or False
        self._entity_schema_name: str = model.schema_

        self._setup = YggSetup(create_ygg_folders=False, config_data=None)
        self._instructions_list: list[str] | None = None

    @property
    def primary_keys(self) -> list[PolyglotEntityColumnDataType]:
        """Get the primary keys for the entity."""
        primary_keys = [c for c in self._model.columns if c.primary_key]
        return primary_keys

    def _get_entity_schema_spec(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the entity schema spec."""

        ducklake_catalog = ""
        if entity_type == DuckLakeDbEntityType.DUCKLAKE:
            ducklake_catalog: str = f"{self._catalog_name}."

        entity_schema_spec = f"CREATE SCHEMA IF NOT EXISTS {ducklake_catalog}{self._entity_schema_name};"

        logs.debug("Entity Schema Spec", spec=entity_schema_spec)
        return entity_schema_spec

    def _get_entity_spec(self, entity_type: DuckLakeDbEntityType) -> str:
        """Create or replace or if not exists entities in DuckLake"""

        header = self._get_create_entity_header(entity_type=entity_type)
        columns = self._get_entity_columns_definition(entity_type)

        stmt: str = f"{header} (\n{columns}\n);"
        return stmt

    def _get_create_entity_header(self, entity_type: DuckLakeDbEntityType) -> str:
        """Return the creation statement of the entity header."""

        create_or_replace: str = "CREATE OR REPLACE TABLE"
        create_if_not_exists: str = "CREATE TABLE IF NOT EXISTS"

        ducklake_catalog = ""
        if entity_type == DuckLakeDbEntityType.DUCKLAKE:
            ducklake_catalog: str = f"{self._catalog_name}."

        create_table_header: str = create_if_not_exists if not self._recreate_existing_entity else create_or_replace
        entity_header = (
            f"{create_table_header} {ducklake_catalog}{self._entity_schema_name.upper()}.{self._model.name.lower()}"
        )

        logs.debug("Entity Creation Header", header=entity_header)
        return entity_header

    @staticmethod
    def _get_db_column_ddl_definition(column: PolyglotEntityColumn, entity_type: DuckLakeDbEntityType) -> str:
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
