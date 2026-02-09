"""Set of database operations and utilities for physical models."""

import hashlib
from typing import Any, Type, Union

import duckdb

from ygg.core.dynamic_odcs_models_factory import ModelSettings, YggBaseModel
from ygg.helpers.logical_data_models import SharedModelMixin
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DuckDbTools:
    """Tools for physical model operations."""

    def __init__(self, model: ModelSettings, ygg_db_url: str = ":memory:") -> None:
        logs.info("Initializing Physical Model Tools.")

        if not model:
            raise ValueError("Ygg Model Cannot be Empty.")

        self._model: ModelSettings = model
        self._db_url: str = ygg_db_url

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

    @staticmethod
    def execute_instructions(db_url: str, receipt: list[str] | str) -> None:
        """Execute a list of SQL statements against the database."""

        if not receipt:
            raise ValueError("Receipt cannot be empty.")

        if isinstance(receipt, str):
            receipt = [receipt]

        with duckdb.connect(db_url, read_only=False) as con:
            try:
                for statement in receipt:
                    logs.debug("Executing SQL statement.")
                    con.execute(statement)
                    logs.debug("SQL statement executed successfully.")

            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}")
                raise e

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
                logs.error(
                    f"Error executing SQL statement: {e}",
                    header_string=header_string,
                    values=values_map,
                )
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
