"""Set of database operations and utilities for physical models."""

import hashlib
from typing import Any, Type, Union

import duckdb

from ygg.core.dynamic_models_factory import ModelSettings, YggBaseModel
from ygg.helpers.physical_model import PhysicalModelHelper
from ygg.helpers.shared_model_mixin import SharedModelMixin
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class PhysicalModelTools:
    """Tools for physical model operations."""

    def __init__(self, model: ModelSettings, db_path: str = ":memory:") -> None:
        logs.info("Initializing Physical Model Tools.")

        if not model:
            raise ValueError("Ygg Model Cannot be Empty.")

        self._model: ModelSettings = model
        self._helper: PhysicalModelHelper = PhysicalModelHelper(model)

        self._db_url: str = db_path

    def _execute(self, statement: str, validation_query_console: str | None = None) -> bool:
        """Execute a SQL statement against the database."""

        with duckdb.connect(self._db_url, read_only=False) as con:
            try:
                logs.debug("Executing SQL statement.")
                con.execute(statement)
                logs.debug("SQL statement executed successfully.")

                if validation_query_console:
                    logs.debug("Executing validation query.")
                    try:
                        con.sql(validation_query_console).show()
                    except Exception as e:
                        logs.error(f"Error executing validation query: {e}")

                return True
            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}")
                raise e

    def create_schema(self) -> None:
        """Create the schema for the physical model."""

        logs.info("Creating Schema.", schema=self._model.entity_schema)
        schema_ddl: str = self._helper.get_create_schema_ddl()
        schema_name = self._model.entity_schema.upper()

        validation_query: str = "SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE UPPER(schema_name) = '{schema_name}';"
        validation_query = validation_query.format(schema_name=schema_name)
        self._execute(schema_ddl, validation_query_console=validation_query)

        logs.info("Schema Created.", schema=self._model.entity_schema)

    def create_table(self, recreate_existing: bool = False) -> bool:
        """Create the schema table for the physical model."""

        logs.info("Creating Table.", table=self._model.entity_name)
        schema_ddl: str = self._helper.get_create_table_ddl(recreate_existing=recreate_existing)
        validation_query: str = f"""
            DESC TABLE {self._model.entity_schema.upper()}.{self._model.entity_name.upper()};
        """
        self._execute(schema_ddl, validation_query_console=validation_query)
        table_comments: list[str] = self._helper.get_table_columns_comments()
        if table_comments:
            self._execute("\n".join(table_comments))
            logs.info("Table Comments Created.")

        logs.info("Table Created.")
        return True

    def insert_data(
        self,
        entity: Type[Union[YggBaseModel, SharedModelMixin]],
        on_conflict_ignore: bool = False,
    ) -> dict:
        """Insert data into the physical model."""

        entity_schema: str = self._model.entity_schema
        entity_name: str = self._model.entity_name

        affected_rows: int = 0
        hydrate_return: dict = {}

        values_map = entity.model_dump()

        empties_ = [k for k, v in values_map.items() if v in (None, "None", "")]
        drop_columns: list = [
            c.name for c in self._model.properties if c.skip_from_physical_model or c.name in empties_
        ]
        for drop in drop_columns or []:
            if drop in values_map:
                del values_map[drop]

        signature_skip_columns = [c.name for c in self._model.properties if c.skip_from_signature]
        values_signature = "".join(
            list(sorted([str(v) for k, v in values_map.items() if v and k not in signature_skip_columns]))
        )

        record_hash = str(hashlib.md5(str(values_signature).encode()).hexdigest())
        values_map["record_hash"] = record_hash

        pk_columns = [c.name for c in self._model.properties if c.primary_key]
        for pk in pk_columns:
            hydrate_return[f"{entity_name}_{pk}"] = values_map.get(pk)

        header: list[str] = [f for f in list(entity.model_fields.keys()) if f in list(values_map.keys())]
        params: list[str] = ", ".join(["?" for f in header])
        header_string: str = ", ".join(header)

        values_list = list(values_map.values())
        values_list = [None if v == "None" else v for v in values_list]
        statement: str = f"""INSERT INTO {entity_schema}.{entity_name} ({header_string}) VALUES ({params}) {" ON CONFLICT DO NOTHING" if on_conflict_ignore else ""}"""

        with duckdb.connect(self._db_url, read_only=False) as con:
            try:
                logs.debug("Executing SQL statement.")
                con.execute(statement, values_list)
                logs.debug("SQL statement executed successfully.")
                affected_rows += 1

            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}", header_string=header_string, values=values_map)
                raise e

        logs.debug("Data Inserted.", affected_rows=affected_rows)

        return hydrate_return

    @staticmethod
    def run_sql_statement(db_url: str, statement: str) -> list[dict]:
        """Run a SQL statement against the database."""

        content: Any = None
        with duckdb.connect(db_url, read_only=False) as con:
            try:
                logs.debug("Executing SQL statement.")
                content = con.sql(statement)
                logs.debug("SQL statement executed successfully.")

                content = content.to_df()
                content = content.to_dict("records")
            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}", error=str(e))
                raise e

        return content
