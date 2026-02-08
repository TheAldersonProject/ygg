"""Database Helper."""

import re
import textwrap
from typing import Any

from ygg.core.dynamic_odcs_models_factory import ModelSettings
from ygg.helpers.data_types import get_data_type
from ygg.utils.ygg_logs import get_logger

database_object_types: dict = dict(schema="schema", table="table")

DDB_CREATE_SCHEMA: str = "CREATE SCHEMA IF NOT EXISTS {object_schema_name};"
DDB_CREATE_SCHEMA_NAME: str = "{object_schema_name}."
DDB_CREATE_OR_REPLACE: str = """CREATE OR REPLACE {object_type} {create_schema_name}{object_name} """
DDB_CREATE_IF_NOT_EXISTS: str = """CREATE {object_type} IF NOT EXISTS {create_schema_name}{object_name} """

DDB_DDL_FIELD_TEMPLATE: str = (
    "{field_name} {field_type} {nullable} {field_pk_uc} {default_value} {field_check_constraint}"
)
DDB_DDL_FIELD_CHECK_CONSTRAINT_TEMPLATE: str = "CHECK ({field_check_constraint_expression})"
DDL_FIELD_CHECK_CONSTRAINT_REGEX_TEMPLATE: str = "regexp_matches({field_name}, '{regex}')"

logs = get_logger()


class OdcsPhysicalModel:
    """Tools for physical model operations."""

    def __init__(self, model: ModelSettings) -> None:
        """Initialize the Physical Model Tools."""

        logs.info("Initializing Physical Model Tools.")

        if not model:
            raise ValueError("Ygg Model Cannot be Empty.")

        self._model: ModelSettings = model
        logs.debug("Physical Model Tools Initialized.", model=self._model.name)

    def get_create_schema_ddl(self) -> str:
        """Create a schema statement."""
        ddl: str = DDB_CREATE_SCHEMA.format(object_schema_name=self._model.entity_schema).upper()
        logs.debug("Create schema statement generated.", schema=ddl)
        return ddl

    def get_table_columns_comments(self) -> list[str]:
        """Get table columns comments."""

        list_of_comments: list = []

        for p in self._model.properties:
            if p.description and p.description.strip():
                description: str = p.description.strip()
                column: str = f"{self._model.entity_schema}.{self._model.entity_name}.{p.name}"
                description = re.sub(r"[^a-zA-Z0-9 ]", "", description)
                comment: str = f"COMMENT ON COLUMN {column} IS '{description}';"
                list_of_comments.append(comment)

        return list_of_comments

    @staticmethod
    def get_physical_data_type(data_type: str) -> dict:
        """Get the physical data type."""

        dtype: dict = get_data_type(data_type, "physical")

        return dtype

    def _get_table_columns(self) -> list[str]:
        """Get table columns."""

        list_of_fields: list = []
        list_of_primary_keys: list = []

        def add_field(
            field_name_: str,
            field_type_: str,
            nullable_: str,
            is_pk_: bool = False,
            is_unique_: bool = False,
            field_check_constraint_: str = "",
            field_default_value_: Any = None,
            physical_default_function_: Any = None,
        ):
            if field_type_.upper() in ("TIMESTAMP", "TIMESTAMPTZ", "TIMESTAMP_LTZ", "BIGINT", "INTEGER"):
                if physical_default_function_:
                    field_default_value_ = f" DEFAULT {physical_default_function_}"
                elif field_default_value_:
                    field_default_value_ = f" DEFAULT {field_default_value_}"

            elif field_default_value_ is not None and not field_default_value_ == ...:
                if field_type_.upper() not in ("BOOL", "BOOLEAN"):
                    field_default_value_ = f" DEFAULT '{field_default_value_}'"

                elif field_type_.upper() in ("BOOL", "BOOLEAN"):
                    field_default_value_ = f" DEFAULT {1 if field_default_value_ else 0}"

                else:
                    field_default_value_ = f" DEFAULT {field_default_value_}"

            else:
                field_default_value_ = ""

            is_primary_key: str = ""
            is_unique_key: str = ""

            if is_pk_:
                list_of_primary_keys.append(field_name_)

            if is_unique_:
                is_unique_key = " UNIQUE "

            field_pk_uc = f"{is_primary_key}{is_unique_key}"

            field_ddl: str = DDB_DDL_FIELD_TEMPLATE.format(
                field_name=field_name_,
                field_type=field_type_,
                nullable=nullable_,
                field_pk_uc=field_pk_uc,
                default_value=field_default_value_,
                field_check_constraint=field_check_constraint_,
            )
            list_of_fields.append(field_ddl.strip())

        for p in self._model.properties:
            field_name: str = p.name.strip().upper().replace(" ", "_")
            nullable: str = "NOT NULL" if p.required else ""
            field_check_constraint: str = ""
            field_default_value: Any = p.default

            list_of_check_constraints: list = []

            if p.enum:
                field_type: str = f""" ENUM({", ".join(["'" + e + "'" for e in p.enum])}) """

            else:
                custom_field_type: dict = OdcsPhysicalModel.get_physical_data_type(p.type)
                pattern: str = custom_field_type.get("pattern", p.pattern)
                field_type: str = custom_field_type.get("type", p.type)

                if pattern:
                    field_check_constraint = DDL_FIELD_CHECK_CONSTRAINT_REGEX_TEMPLATE.format(
                        field_name=field_name,
                        regex=pattern,
                    )
                    list_of_check_constraints.append(field_check_constraint)

            if list_of_check_constraints:
                field_check_constraint_expression: str = " AND ".join(list_of_check_constraints)
                field_check_constraint: str = DDB_DDL_FIELD_CHECK_CONSTRAINT_TEMPLATE.format(
                    field_check_constraint_expression=field_check_constraint_expression
                )

            add_field(
                field_name_=field_name,
                field_type_=field_type,
                nullable_=nullable,
                is_pk_=p.primary_key,
                is_unique_=p.unique,
                field_check_constraint_=field_check_constraint,
                field_default_value_=field_default_value,
                physical_default_function_=p.physical_default_function,
            )

        if list_of_primary_keys:
            primary_keys: str = ", ".join(list_of_primary_keys)
            pk_constraint: str = f" PRIMARY KEY ({primary_keys})"
            list_of_fields.append(pk_constraint)

        return list_of_fields

    def get_create_table_ddl(self, recreate_existing: bool = False, with_create_schema: bool = False) -> str:
        """Create a table statement."""

        object_type: str = database_object_types.get(str(self._model.entity_type).lower(), None)
        if not object_type:
            logs.error("Invalid Entity Type.", entity_type=self._model.entity_type)
            raise ValueError(f"Invalid Entity Type: {self._model.entity_type}.")

        logs.debug("Creating table statement.", entity=self._model.entity_name)
        logs.debug("Recreate target object", recreate_existing=recreate_existing)
        logs.debug("With create schema", with_create_schema=with_create_schema)

        logs.debug("Generating table columns DDL block.")

        fields_ddl_block: str = ",\n".join(self._get_table_columns())
        ddl_create_table_statement_template: str = """
            {create_table_statement}   (
            {fields_ddl_block}
            ) ;
        """

        logs.debug("Parsing DDL.")

        ddl_create_table_statement_template = textwrap.dedent(ddl_create_table_statement_template)
        rendered_schema_name = DDB_CREATE_SCHEMA_NAME.format(object_schema_name=self._model.entity_schema)
        create_table_statement = DDB_CREATE_OR_REPLACE if recreate_existing else DDB_CREATE_IF_NOT_EXISTS
        values_map: dict = {
            "create_schema_name": rendered_schema_name,
            "object_type": object_type,
            "object_name": self._model.entity_name,
        }
        create_table_statement = create_table_statement.format(**values_map).upper()

        rendered_statement: str = ddl_create_table_statement_template.format(
            create_table_statement=create_table_statement, fields_ddl_block=fields_ddl_block
        )
        rendered_statement = rendered_statement.strip()

        logs.info("Table DDL generated.")
        logs.debug("Table DDL", table_ddl=rendered_statement)

        schema_ddl: str = self.get_create_schema_ddl() if with_create_schema else ""
        table_ddl: str = f"{schema_ddl}\n{rendered_statement}"

        logs.info("Generate table DDL process completed.")

        return table_ddl
